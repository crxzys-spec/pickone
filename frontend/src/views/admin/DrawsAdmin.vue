<template>
  <div class="page">
    <div class="toolbar">
      <div class="actions">
        <el-button type="primary" @click="openCreate">
          {{ t("draws.new") }}
        </el-button>
        <el-button @click="refresh">{{ t("common.refresh") }}</el-button>
      </div>
      <el-input
        v-model="keyword"
        :placeholder="t('draws.searchPlaceholder')"
        clearable
        class="search"
      />
    </div>

    <el-table
      :data="draws"
      v-loading="loading"
      border
      stripe
      class="table"
      @sort-change="handleSortChange"
    >
      <el-table-column
        :label="t('draws.columns.id')"
        prop="id"
        width="80"
        sortable="custom"
      />
      <el-table-column
        :label="t('draws.columns.category')"
        prop="category"
        min-width="140"
        sortable="custom"
      />
      <el-table-column
        :label="t('draws.columns.subcategory')"
        prop="subcategory"
        min-width="140"
        sortable="custom"
      />
      <el-table-column
        :label="t('draws.columns.count')"
        prop="expert_count"
        width="90"
        sortable="custom"
      />
      <el-table-column
        :label="t('draws.columns.backup')"
        prop="backup_count"
        width="90"
        sortable="custom"
      />
      <el-table-column :label="t('draws.columns.method')" width="120" prop="draw_method" sortable="custom">
        <template #default="{ row }">
          {{ methodLabel(row.draw_method) }}
        </template>
      </el-table-column>
      <el-table-column
        :label="t('draws.columns.reviewTime')"
        prop="review_time"
        min-width="170"
        sortable="custom"
      />
      <el-table-column
        :label="t('draws.columns.location')"
        prop="review_location"
        min-width="160"
        sortable="custom"
      />
      <el-table-column :label="t('draws.columns.status')" width="120" prop="status" sortable="custom">
        <template #default="{ row }">
          {{ statusLabel(row.status) }}
        </template>
      </el-table-column>
      <el-table-column :label="t('draws.columns.rule')" prop="rule_id" width="90" sortable="custom" />
      <el-table-column :label="t('draws.columns.actions')" width="280" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">
            {{ t("common.edit") }}
          </el-button>
          <el-button link @click="openResults(row)">
            {{ t("common.results") }}
          </el-button>
          <el-button
            link
            type="success"
            :disabled="row.status === 'completed'"
            @click="confirmExecute(row)"
          >
            {{ t("common.execute") }}
          </el-button>
          <el-button link type="danger" @click="confirmDelete(row)">
            {{ t("common.delete") }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handlePageSizeChange"
      />
    </div>
  </div>

  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="620px">
    <el-form :model="form" label-width="120px">
      <el-form-item :label="t('draws.form.expertCount')">
        <el-input-number v-model="form.expert_count" :min="1" />
      </el-form-item>
      <el-form-item :label="t('draws.form.backupCount')">
        <el-input-number v-model="form.backup_count" :min="0" />
      </el-form-item>
      <el-form-item :label="t('draws.form.drawMethod')">
        <el-select v-model="form.draw_method" style="width: 100%;">
          <el-option :label="t('draws.method.random')" value="random" />
          <el-option :label="t('draws.method.lottery')" value="lottery" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('draws.form.reviewTime')">
        <el-date-picker
          v-model="form.review_time"
          type="datetime"
          value-format="YYYY-MM-DDTHH:mm:ss"
          style="width: 100%;"
        />
      </el-form-item>
      <el-form-item :label="t('draws.form.reviewLocation')">
        <el-input v-model="form.review_location" />
      </el-form-item>
      <el-form-item :label="t('draws.form.rule')">
        <el-select v-model="form.rule_id" clearable style="width: 100%;">
          <el-option
            v-for="rule in rules"
            :key="rule.id"
            :label="rule.name"
            :value="rule.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item v-if="isEditing" :label="t('draws.form.status')">
        <el-select v-model="form.status" style="width: 100%;">
          <el-option :label="t('draws.status.pending')" value="pending" />
          <el-option :label="t('draws.status.scheduled')" value="scheduled" />
          <el-option :label="t('draws.status.completed')" value="completed" />
          <el-option :label="t('draws.status.cancelled')" value="cancelled" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">
        {{ t("common.cancel") }}
      </el-button>
      <el-button type="primary" @click="submitForm">
        {{ t("common.save") }}
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="resultsVisible"
    :title="t('draws.results.title')"
    width="760px"
  >
    <div class="results-toolbar">
      <el-input
        v-model="resultsKeyword"
        :placeholder="t('experts.searchPlaceholder')"
        clearable
        class="search"
      />
    </div>
    <el-table :data="results" border stripe @sort-change="handleResultsSortChange">
      <el-table-column :label="t('draws.results.columns.order')" prop="ordinal" width="80" sortable="custom" />
      <el-table-column :label="t('draws.results.columns.backup')" width="100" prop="is_backup" sortable="custom">
        <template #default="{ row }">
          <el-tag :type="row.is_backup ? 'warning' : 'success'">
            {{ row.is_backup ? t("common.yes") : t("common.no") }}
          </el-tag>
          <el-tag v-if="row.is_replacement" type="success" class="tag">
            {{ t("draws.results.badges.promoted") }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('draws.results.columns.name')" min-width="140">
        <template #default="{ row }">
          {{ row.expert?.name || "-" }}
        </template>
      </el-table-column>
      <el-table-column :label="t('draws.results.columns.company')" min-width="160">
        <template #default="{ row }">
          {{ row.expert?.company || "-" }}
        </template>
      </el-table-column>
      <el-table-column :label="t('draws.results.columns.category')" min-width="120">
        <template #default="{ row }">
          {{ row.expert?.category || "-" }}
        </template>
      </el-table-column>
      <el-table-column :label="t('draws.results.columns.phone')" min-width="140">
        <template #default="{ row }">
          {{ row.expert?.phone || "-" }}
        </template>
      </el-table-column>
      <el-table-column :label="t('draws.results.columns.email')" min-width="160">
        <template #default="{ row }">
          {{ row.expert?.email || "-" }}
        </template>
      </el-table-column>
      <el-table-column :label="t('draws.results.columns.actions')" width="140">
        <template #default="{ row }">
          <el-button
            v-if="!row.is_backup"
            link
            type="warning"
            :disabled="!hasBackup"
            @click="confirmReplace(row)"
          >
            {{ t("draws.actions.replace") }}
          </el-button>
          <span v-else class="muted">-</span>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager results-pager">
      <el-pagination
        v-model:current-page="resultsPage"
        v-model:page-size="resultsPageSize"
        :total="resultsTotal"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handleResultsPageChange"
        @size-change="handleResultsPageSizeChange"
      />
    </div>
    <template #footer>
      <el-button @click="resultsVisible = false">
        {{ t("common.cancel") }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import axios from "axios";
import { computed, onMounted, reactive, ref, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useI18n } from "vue-i18n";

import {
  createDraw,
  deleteDraw,
  executeDraw,
  listDrawResults,
  listDraws,
  replaceDrawResult,
  updateDraw,
} from "../../services/draws";
import { listRulesAll } from "../../services/rules";
import type {
  DrawApplication,
  DrawResultOut,
  Rule,
} from "../../types/domain";

interface DrawForm {
  expert_count: number;
  backup_count: number;
  draw_method: string;
  review_time: string;
  review_location: string;
  rule_id: number | null;
  status: string;
}

const draws = ref<DrawApplication[]>([]);
const rules = ref<Rule[]>([]);
const loading = ref(false);
const keyword = ref("");
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const sortBy = ref<string | undefined>();
const sortOrder = ref<"asc" | "desc" | undefined>();
const { t } = useI18n();

const dialogVisible = ref(false);
const isEditing = ref(false);
const editingId = ref<number | null>(null);
const resultsVisible = ref(false);
const results = ref<DrawResultOut[]>([]);
const resultsKeyword = ref("");
const resultsPage = ref(1);
const resultsPageSize = ref(10);
const resultsTotal = ref(0);
const resultsSortBy = ref<string | undefined>();
const resultsSortOrder = ref<"asc" | "desc" | undefined>();
const hasBackup = ref(false);
const activeDrawId = ref<number | null>(null);

const form = reactive<DrawForm>({
  expert_count: 1,
  backup_count: 0,
  draw_method: "random",
  review_time: "",
  review_location: "",
  rule_id: null,
  status: "pending",
});

const dialogTitle = computed(() =>
  isEditing.value ? t("draws.dialog.edit") : t("draws.dialog.new"),
);

let keywordTimer: number | undefined;
let resultsKeywordTimer: number | undefined;

watch(keyword, () => {
  if (keywordTimer) {
    window.clearTimeout(keywordTimer);
  }
  keywordTimer = window.setTimeout(() => {
    page.value = 1;
    refresh();
  }, 300);
});

watch(resultsKeyword, () => {
  if (resultsKeywordTimer) {
    window.clearTimeout(resultsKeywordTimer);
  }
  resultsKeywordTimer = window.setTimeout(() => {
    resultsPage.value = 1;
    refreshResults();
  }, 300);
});

function resetForm() {
  form.expert_count = 1;
  form.backup_count = 0;
  form.draw_method = "random";
  form.review_time = "";
  form.review_location = "";
  form.rule_id = null;
  form.status = "pending";
}

function methodLabel(value: string) {
  if (value === "lottery") {
    return t("draws.method.lottery");
  }
  if (value === "random") {
    return t("draws.method.random");
  }
  return value;
}

function statusLabel(value: string) {
  if (value === "scheduled") {
    return t("draws.status.scheduled");
  }
  if (value === "completed") {
    return t("draws.status.completed");
  }
  if (value === "cancelled") {
    return t("draws.status.cancelled");
  }
  if (value === "pending") {
    return t("draws.status.pending");
  }
  return value;
}

const ERROR_MESSAGE_MAP: Record<string, string> = {
  "Not enough qualified experts": "draws.messages.notEnoughExperts",
};

function resolveErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) {
      const mappedKey = ERROR_MESSAGE_MAP[detail];
      if (mappedKey) {
        return t(mappedKey);
      }
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: string };
      if (typeof first?.msg === "string" && first.msg.trim()) {
        return first.msg;
      }
    }
  }
  return fallback;
}

async function refresh() {
  loading.value = true;
  try {
    const result = await listDraws({
      page: page.value,
      page_size: pageSize.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      keyword: keyword.value.trim() || undefined,
    });
    draws.value = result.items;
    total.value = result.total;
  } finally {
    loading.value = false;
  }
}

async function refreshRules() {
  rules.value = await listRulesAll();
}

async function refreshResults() {
  if (!activeDrawId.value) {
    return;
  }
  const result = await listDrawResults(activeDrawId.value, {
    page: resultsPage.value,
    page_size: resultsPageSize.value,
    sort_by: resultsSortBy.value,
    sort_order: resultsSortOrder.value,
    keyword: resultsKeyword.value.trim() || undefined,
  });
  results.value = result.items;
  resultsTotal.value = result.total;
  hasBackup.value = result.items.some((item) => item.is_backup);
  if (!hasBackup.value && result.total > result.items.length) {
    const backupCheck = await listDrawResults(activeDrawId.value, {
      page: 1,
      page_size: 1,
      sort_by: "is_backup",
      sort_order: "desc",
    });
    hasBackup.value = backupCheck.items.some((item) => item.is_backup);
  }
}

function openCreate() {
  resetForm();
  isEditing.value = false;
  editingId.value = null;
  dialogVisible.value = true;
}

function openEdit(draw: DrawApplication) {
  isEditing.value = true;
  editingId.value = draw.id;
  form.expert_count = draw.expert_count;
  form.backup_count = draw.backup_count ?? 0;
  form.draw_method = draw.draw_method;
  form.review_time = draw.review_time ?? "";
  form.review_location = draw.review_location ?? "";
  form.rule_id = draw.rule_id ?? null;
  form.status = draw.status;
  dialogVisible.value = true;
}

async function submitForm() {
  if (!form.rule_id) {
    ElMessage.error(t("draws.messages.ruleRequired"));
    return;
  }
  try {
    if (isEditing.value && editingId.value) {
      await updateDraw(editingId.value, {
        expert_count: form.expert_count,
        backup_count: form.backup_count,
        draw_method: form.draw_method,
        review_time: form.review_time || null,
        review_location: form.review_location,
        rule_id: form.rule_id,
        status: form.status,
      });
      ElMessage.success(t("draws.messages.updated"));
    } else {
      await createDraw({
        expert_count: form.expert_count,
        backup_count: form.backup_count,
        draw_method: form.draw_method,
        review_time: form.review_time || null,
        review_location: form.review_location,
        rule_id: form.rule_id,
      });
      ElMessage.success(t("draws.messages.created"));
    }
    dialogVisible.value = false;
    await refresh();
  } catch (error) {
    ElMessage.error(t("draws.messages.opFailed"));
  }
}

async function confirmDelete(draw: DrawApplication) {
  try {
    await ElMessageBox.confirm(
      t("draws.messages.deleteConfirm", { id: draw.id }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  await deleteDraw(draw.id);
  ElMessage.success(t("draws.messages.deleted"));
  await refresh();
}

async function confirmExecute(draw: DrawApplication) {
  try {
    await ElMessageBox.confirm(
      t("draws.messages.executeConfirm", { id: draw.id }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  try {
    await executeDraw(draw.id);
    resultsVisible.value = true;
    activeDrawId.value = draw.id;
    resultsPage.value = 1;
    resultsSortBy.value = undefined;
    resultsSortOrder.value = undefined;
    await refreshResults();
    await refresh();
  } catch (error) {
    ElMessage.error(resolveErrorMessage(error, t("draws.messages.executeFailed")));
  }
}

async function openResults(draw: DrawApplication) {
  try {
    activeDrawId.value = draw.id;
    resultsPage.value = 1;
    resultsSortBy.value = undefined;
    resultsSortOrder.value = undefined;
    await refreshResults();
    resultsVisible.value = true;
  } catch (error) {
    ElMessage.error(t("draws.messages.resultsFailed"));
  }
}

async function confirmReplace(result: DrawResultOut) {
  if (!activeDrawId.value) {
    return;
  }
  try {
    await ElMessageBox.confirm(
      t("draws.messages.replaceConfirm", {
        name: result.expert?.name ?? result.expert_id,
      }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }

  try {
    await replaceDrawResult(activeDrawId.value, result.id);
    await refreshResults();
    ElMessage.success(t("draws.messages.replaceSuccess"));
  } catch (error) {
    ElMessage.error(t("draws.messages.replaceFailed"));
  }
}

onMounted(async () => {
  await Promise.all([refresh(), refreshRules()]);
});

function handleSortChange({
  prop,
  order,
}: {
  prop?: string;
  order?: "ascending" | "descending" | null;
}) {
  if (!prop || !order) {
    sortBy.value = undefined;
    sortOrder.value = undefined;
  } else {
    sortBy.value = prop;
    sortOrder.value = order === "ascending" ? "asc" : "desc";
  }
  page.value = 1;
  refresh();
}

function handlePageChange(value: number) {
  page.value = value;
  refresh();
}

function handlePageSizeChange(value: number) {
  pageSize.value = value;
  page.value = 1;
  refresh();
}

function handleResultsSortChange({
  prop,
  order,
}: {
  prop?: string;
  order?: "ascending" | "descending" | null;
}) {
  if (!prop || !order) {
    resultsSortBy.value = undefined;
    resultsSortOrder.value = undefined;
  } else {
    resultsSortBy.value = prop;
    resultsSortOrder.value = order === "ascending" ? "asc" : "desc";
  }
  resultsPage.value = 1;
  refreshResults();
}

function handleResultsPageChange(value: number) {
  resultsPage.value = value;
  refreshResults();
}

function handleResultsPageSizeChange(value: number) {
  resultsPageSize.value = value;
  resultsPage.value = 1;
  refreshResults();
}
</script>

<style scoped>
.page {
  position: relative;
  background: var(--gov-card);
  padding: 20px;
  border-radius: 6px;
  border: 1px solid var(--gov-border);
  box-shadow: var(--gov-shadow);
  overflow: hidden;
  animation: gov-rise 360ms ease-out;
}

.page::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  height: 4px;
  width: 100%;
  background: linear-gradient(
    90deg,
    var(--gov-blue-700),
    var(--gov-blue-500),
    var(--gov-blue-700)
  );
}


.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 12px;
}

.actions {
  display: flex;
  gap: 8px;
}

.search {
  max-width: 260px;
}

.table {
  width: 100%;
}

.tag {
  margin-left: 6px;
}

.muted {
  color: #9aa3b2;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.results-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}

.results-pager {
  margin-top: 12px;
}
</style>
