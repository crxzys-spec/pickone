<template>
  <div class="page">
    <div class="toolbar">
      <div class="actions">
        <el-button type="primary" @click="openCreate">
          {{ t("titles.new") }}
        </el-button>
        <el-button
          type="danger"
          :loading="deleting"
          :disabled="selectedIds.length === 0"
          @click="handleBatchDelete"
        >
          {{ t("titles.actions.batchDelete") }}
        </el-button>
        <el-button @click="refresh">{{ t("common.refresh") }}</el-button>
      </div>
      <el-input
        v-model="keyword"
        :placeholder="t('titles.searchPlaceholder')"
        clearable
        class="search"
      />
    </div>

    <el-table
      ref="tableRef"
      :data="titles"
      v-loading="loading"
      border
      stripe
      class="table"
      @sort-change="handleSortChange"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="48" />
      <el-table-column
        :label="t('titles.columns.id')"
        prop="id"
        width="80"
        sortable="custom"
      />
      <el-table-column
        :label="t('titles.columns.name')"
        prop="name"
        min-width="180"
        sortable="custom"
      />
      <el-table-column
        :label="t('titles.columns.code')"
        prop="code"
        min-width="160"
        sortable="custom"
      />
      <el-table-column
        :label="t('titles.columns.sort')"
        prop="sort_order"
        width="120"
        sortable="custom"
      />
      <el-table-column
        :label="t('titles.columns.active')"
        width="120"
        prop="is_active"
        sortable="custom"
      >
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? t("common.yes") : t("common.no") }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('titles.columns.actions')" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">
            {{ t("common.edit") }}
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

  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px">
    <el-form :model="form" label-width="120px">
      <el-form-item :label="t('titles.form.name')" required>
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item :label="t('titles.form.code')">
        <el-input v-model="form.code" />
      </el-form-item>
      <el-form-item :label="t('titles.form.sort')">
        <el-input-number v-model="form.sort_order" :min="0" />
      </el-form-item>
      <el-form-item :label="t('titles.form.active')">
        <el-switch v-model="form.is_active" />
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
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useI18n } from "vue-i18n";

import {
  createTitle,
  deleteTitle,
  deleteTitles,
  listTitles,
  updateTitle,
} from "../../services/titles";
import type { Title } from "../../types/domain";

interface TitleForm {
  name: string;
  code: string;
  sort_order: number;
  is_active: boolean;
}

const titles = ref<Title[]>([]);
const tableRef = ref();
const loading = ref(false);
const deleting = ref(false);
const selectedIds = ref<number[]>([]);
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

const form = reactive<TitleForm>({
  name: "",
  code: "",
  sort_order: 0,
  is_active: true,
});

const dialogTitle = computed(() =>
  isEditing.value ? t("titles.dialog.edit") : t("titles.dialog.new"),
);

let keywordTimer: number | undefined;

watch(keyword, () => {
  if (keywordTimer) {
    window.clearTimeout(keywordTimer);
  }
  keywordTimer = window.setTimeout(() => {
    page.value = 1;
    refresh();
  }, 300);
});

function resetForm() {
  form.name = "";
  form.code = "";
  form.sort_order = 0;
  form.is_active = true;
}

async function refresh() {
  loading.value = true;
  try {
    const result = await listTitles({
      page: page.value,
      page_size: pageSize.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      keyword: keyword.value.trim() || undefined,
    });
    titles.value = result.items;
    total.value = result.total;
    tableRef.value?.clearSelection();
    selectedIds.value = [];
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  resetForm();
  isEditing.value = false;
  editingId.value = null;
  dialogVisible.value = true;
}

function openEdit(title: Title) {
  isEditing.value = true;
  editingId.value = title.id;
  form.name = title.name;
  form.code = title.code ?? "";
  form.sort_order = title.sort_order;
  form.is_active = title.is_active;
  dialogVisible.value = true;
}

async function submitForm() {
  try {
    if (isEditing.value && editingId.value) {
      await updateTitle(editingId.value, {
        name: form.name,
        code: form.code || null,
        sort_order: form.sort_order,
        is_active: form.is_active,
      });
      ElMessage.success(t("titles.messages.updated"));
    } else {
      await createTitle({
        name: form.name,
        code: form.code || null,
        sort_order: form.sort_order,
        is_active: form.is_active,
      });
      ElMessage.success(t("titles.messages.created"));
    }
    dialogVisible.value = false;
    await refresh();
  } catch (error) {
    ElMessage.error(t("titles.messages.opFailed"));
  }
}

async function confirmDelete(title: Title) {
  try {
    await ElMessageBox.confirm(
      t("titles.messages.deleteConfirm", { name: title.name }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  await deleteTitle(title.id);
  ElMessage.success(t("titles.messages.deleted"));
  await refresh();
}

function handleSelectionChange(rows: Title[]) {
  selectedIds.value = rows.map((item) => item.id);
}

async function handleBatchDelete() {
  if (selectedIds.value.length === 0) {
    return;
  }
  try {
    await ElMessageBox.confirm(
      t("titles.messages.batchDeleteConfirm", { count: selectedIds.value.length }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  deleting.value = true;
  try {
    const result = await deleteTitles(selectedIds.value);
    ElMessage.success(
      t("titles.messages.batchDeleteSuccess", {
        deleted: result.deleted,
        skipped: result.skipped,
      }),
    );
    await refresh();
  } catch (error) {
    ElMessage.error(t("titles.messages.batchDeleteFailed"));
  } finally {
    deleting.value = false;
  }
}

onMounted(refresh);

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

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
