<template>
  <div class="page">
    <div class="toolbar">
      <div class="actions">
        <el-button type="primary" @click="openCreate">
          {{ t("rules.new") }}
        </el-button>
        <el-button @click="refresh">{{ t("common.refresh") }}</el-button>
      </div>
      <el-input
        v-model="keyword"
        :placeholder="t('rules.searchPlaceholder')"
        clearable
        class="search"
      />
    </div>

    <el-table
      :data="rules"
      v-loading="loading"
      border
      stripe
      class="table"
      @sort-change="handleSortChange"
    >
      <el-table-column
        :label="t('rules.columns.id')"
        prop="id"
        width="80"
        sortable="custom"
      />
      <el-table-column
        :label="t('rules.columns.name')"
        prop="name"
        min-width="160"
        sortable="custom"
      />
      <el-table-column
        :label="t('rules.columns.category')"
        prop="category"
        min-width="140"
        sortable="custom"
      />
      <el-table-column
        :label="t('rules.columns.specialty')"
        prop="specialty"
        min-width="160"
        sortable="custom"
      />
      <el-table-column
        :label="t('rules.columns.title')"
        prop="title_required"
        min-width="140"
        sortable="custom"
      />
      <el-table-column
        :label="t('rules.columns.region')"
        prop="region_required"
        min-width="120"
        sortable="custom"
      />
      <el-table-column :label="t('rules.columns.method')" width="120" prop="draw_method" sortable="custom">
        <template #default="{ row }">
          {{ methodLabel(row.draw_method) }}
        </template>
      </el-table-column>
      <el-table-column :label="t('rules.columns.active')" width="100" prop="is_active" sortable="custom">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? t("common.yes") : t("common.no") }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('rules.columns.actions')" width="220" fixed="right">
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
      <el-form-item :label="t('rules.form.name')" required>
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item :label="t('rules.form.specialty')">
        <el-tree-select
          v-model="form.specialty_ids"
          :data="specialtyTreeOptions"
          :props="specialtyTreeProps"
          multiple
          filterable
          clearable
          check-strictly
          collapse-tags
          collapse-tags-tooltip
          style="width: 100%;"
        />
      </el-form-item>
      <el-form-item :label="t('rules.form.titleRequired')">
        <el-tree-select
          v-model="form.title_required_ids"
          :data="titleTreeOptions"
          :props="titleTreeProps"
          multiple
          filterable
          clearable
          check-strictly
          collapse-tags
          collapse-tags-tooltip
          style="width: 100%;"
        />
      </el-form-item>
      <el-form-item :label="t('rules.form.regionRequired')">
        <el-select
          v-model="form.region_required_ids"
          multiple
          filterable
          clearable
          collapse-tags
          collapse-tags-tooltip
          style="width: 100%;"
        >
          <el-option
            v-for="region in regions"
            :key="region.id"
            :label="region.name"
            :value="region.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('rules.form.drawMethod')">
        <el-select v-model="form.draw_method" style="width: 100%;">
          <el-option :label="t('rules.method.random')" value="random" />
          <el-option :label="t('rules.method.lottery')" value="lottery" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('rules.form.active')">
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
  createRule,
  deleteRule,
  listRules,
  updateRule,
} from "../../services/rules";
import { listCategoryTree } from "../../services/categories";
import { listRegionsAll } from "../../services/regions";
import { listTitleTree } from "../../services/titles";
import type { Category, Region, Rule, Title } from "../../types/domain";

interface RuleForm {
  name: string;
  specialty_ids: number[];
  title_required_ids: number[];
  region_required_ids: number[];
  draw_method: string;
  is_active: boolean;
}

const rules = ref<Rule[]>([]);
const specialtyTree = ref<Category[]>([]);
const regions = ref<Region[]>([]);
const titleTree = ref<Title[]>([]);
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

const form = reactive<RuleForm>({
  name: "",
  specialty_ids: [],
  title_required_ids: [],
  region_required_ids: [],
  draw_method: "random",
  is_active: true,
});

const dialogTitle = computed(() =>
  isEditing.value ? t("rules.dialog.edit") : t("rules.dialog.new"),
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
  form.specialty_ids = [];
  form.title_required_ids = [];
  form.region_required_ids = [];
  form.draw_method = "random";
  form.is_active = true;
}

async function refresh() {
  loading.value = true;
  try {
    const result = await listRules({
      page: page.value,
      page_size: pageSize.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      keyword: keyword.value.trim() || undefined,
    });
    rules.value = result.items;
    total.value = result.total;
  } finally {
    loading.value = false;
  }
}

async function refreshCategories() {
  specialtyTree.value = await listCategoryTree();
}

async function refreshTitles() {
  titleTree.value = await listTitleTree();
}

async function refreshRegions() {
  regions.value = await listRegionsAll();
}

type TreeSource = {
  id: number;
  name: string;
  code?: string | null;
  children?: TreeSource[];
};

type TreeOption = {
  id: number;
  label: string;
  is_leaf: boolean;
  children?: TreeOption[];
};

function buildTreeOptions(nodes: TreeSource[]): TreeOption[] {
  return (nodes ?? []).map((node) => {
    const children = buildTreeOptions(node.children ?? []);
    return {
      id: node.id,
      label: node.code ? `${node.code} ${node.name}` : node.name,
      is_leaf: children.length == 0,
      children: children.length > 0 ? children : undefined,
    };
  });
}

function flattenTree<T extends TreeSource>(nodes: T[]): T[] {
  const result: T[] = [];
  nodes.forEach((node) => {
    result.push(node);
    if (node.children && node.children.length > 0) {
      result.push(...flattenTree(node.children as T[]));
    }
  });
  return result;
}

const specialtyTreeOptions = computed<TreeOption[]>(() =>
  buildTreeOptions(specialtyTree.value),
);

const titleTreeOptions = computed<TreeOption[]>(() =>
  buildTreeOptions(titleTree.value),
);

const specialtyFlat = computed(() => flattenTree(specialtyTree.value));
const titleFlat = computed(() => flattenTree(titleTree.value));

const specialtyTreeProps = {
  value: "id",
  label: "label",
  children: "children",
};

const titleTreeProps = specialtyTreeProps;

function splitTerms(value: string | null | undefined): string[] {
  if (!value) {
    return [];
  }
  return value
    .split(/[;,|\n、，；]/)
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
}

function resolveIdsFromNames(
  value: string | null | undefined,
  options: Array<{ id: number; name: string }>,
) {
  const names = splitTerms(value);
  if (!names.length) {
    return [];
  }
  const ids: number[] = [];
  const seen = new Set<number>();
  for (const name of names) {
    const id = options.find((item) => item.name === name)?.id;
    if (id != null && !seen.has(id)) {
      ids.push(id);
      seen.add(id);
    }
  }
  return ids;
}

function resolveSpecialtyIds(rule: Rule): number[] {
  if (rule.specialty_ids?.length) {
    return [...rule.specialty_ids];
  }
  if (rule.specialty_id) {
    return [rule.specialty_id];
  }
  return resolveIdsFromNames(rule.specialty, specialtyFlat.value);
}

function methodLabel(value: string) {
  if (value === "lottery") {
    return t("rules.method.lottery");
  }
  if (value === "random") {
    return t("rules.method.random");
  }
  return value;
}

function openCreate() {
  resetForm();
  isEditing.value = false;
  editingId.value = null;
  dialogVisible.value = true;
}

function openEdit(rule: Rule) {
  isEditing.value = true;
  editingId.value = rule.id;
  form.name = rule.name;
  form.specialty_ids = resolveSpecialtyIds(rule);
  form.title_required_ids = rule.title_required_ids?.length
    ? [...rule.title_required_ids]
    : resolveIdsFromNames(rule.title_required, titleFlat.value);
  form.region_required_ids = rule.region_required_ids?.length
    ? [...rule.region_required_ids]
    : resolveIdsFromNames(rule.region_required, regions.value);
  form.draw_method = rule.draw_method;
  form.is_active = rule.is_active;
  dialogVisible.value = true;
}

async function submitForm() {
  try {
    if (isEditing.value && editingId.value) {
      await updateRule(editingId.value, {
        name: form.name,
        specialty_ids: form.specialty_ids,
        title_required_ids: form.title_required_ids,
        region_required_ids: form.region_required_ids,
        draw_method: form.draw_method,
        is_active: form.is_active,
      });
      ElMessage.success(t("rules.messages.updated"));
    } else {
      await createRule({
        name: form.name,
        specialty_ids: form.specialty_ids,
        title_required_ids: form.title_required_ids,
        region_required_ids: form.region_required_ids,
        draw_method: form.draw_method,
        is_active: form.is_active,
      });
      ElMessage.success(t("rules.messages.created"));
    }
    dialogVisible.value = false;
    await refresh();
  } catch (error) {
    ElMessage.error(t("rules.messages.opFailed"));
  }
}

async function confirmDelete(rule: Rule) {
  try {
    await ElMessageBox.confirm(
      t("rules.messages.deleteConfirm", { name: rule.name }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  await deleteRule(rule.id);
  ElMessage.success(t("rules.messages.deleted"));
  await refresh();
}

onMounted(async () => {
  await Promise.all([
    refresh(),
    refreshCategories(),
    refreshRegions(),
    refreshTitles(),
  ]);
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
