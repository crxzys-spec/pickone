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
      :data="filteredRules"
      v-loading="loading"
      border
      stripe
      class="table"
    >
      <el-table-column :label="t('rules.columns.id')" prop="id" width="80" />
      <el-table-column
        :label="t('rules.columns.name')"
        prop="name"
        min-width="160"
      />
      <el-table-column
        :label="t('rules.columns.category')"
        prop="category"
        min-width="140"
      />
      <el-table-column
        :label="t('rules.columns.subcategory')"
        prop="subcategory"
        min-width="140"
      />
      <el-table-column
        :label="t('rules.columns.title')"
        prop="title_required"
        min-width="140"
      />
      <el-table-column :label="t('rules.columns.method')" width="120">
        <template #default="{ row }">
          {{ methodLabel(row.draw_method) }}
        </template>
      </el-table-column>
      <el-table-column :label="t('rules.columns.avoid')" width="100">
        <template #default="{ row }">
          <el-tag :type="row.avoid_enabled ? 'success' : 'info'">
            {{ row.avoid_enabled ? t("common.yes") : t("common.no") }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('rules.columns.active')" width="100">
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
  </div>

  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px">
    <el-form :model="form" label-width="120px">
      <el-form-item :label="t('rules.form.name')">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item :label="t('rules.form.category')">
        <el-select v-model="form.category_id" clearable style="width: 100%;">
          <el-option
            v-for="category in categories"
            :key="category.id"
            :label="category.name"
            :value="category.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('rules.form.subcategory')">
        <el-select
          v-model="form.subcategory_id"
          clearable
          style="width: 100%;"
          :disabled="!form.category_id"
        >
          <el-option
            v-for="subcategory in availableSubcategories"
            :key="subcategory.id"
            :label="subcategory.name"
            :value="subcategory.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('rules.form.titleRequired')">
        <el-select v-model="form.title_required" clearable style="width: 100%;">
          <el-option
            v-for="title in titles"
            :key="title.id"
            :label="title.name"
            :value="title.name"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('rules.form.drawMethod')">
        <el-select v-model="form.draw_method" style="width: 100%;">
          <el-option :label="t('rules.method.random')" value="random" />
          <el-option :label="t('rules.method.lottery')" value="lottery" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('rules.form.avoidEnabled')">
        <el-switch v-model="form.avoid_enabled" />
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
import { listTitles } from "../../services/titles";
import type { CategoryTree, Rule, Subcategory, Title } from "../../types/domain";

interface RuleForm {
  name: string;
  category_id: number | null;
  subcategory_id: number | null;
  title_required: string | null;
  draw_method: string;
  avoid_enabled: boolean;
  is_active: boolean;
}

const rules = ref<Rule[]>([]);
const categories = ref<CategoryTree[]>([]);
const titles = ref<Title[]>([]);
const loading = ref(false);
const keyword = ref("");
const { t } = useI18n();

const dialogVisible = ref(false);
const isEditing = ref(false);
const editingId = ref<number | null>(null);

const form = reactive<RuleForm>({
  name: "",
  category_id: null,
  subcategory_id: null,
  title_required: null,
  draw_method: "random",
  avoid_enabled: true,
  is_active: true,
});

const dialogTitle = computed(() =>
  isEditing.value ? t("rules.dialog.edit") : t("rules.dialog.new"),
);

const filteredRules = computed(() => {
  const key = keyword.value.trim().toLowerCase();
  if (!key) {
    return rules.value;
  }
  return rules.value.filter((rule) => rule.name.toLowerCase().includes(key));
});

function resetForm() {
  form.name = "";
  form.category_id = null;
  form.subcategory_id = null;
  form.title_required = null;
  form.draw_method = "random";
  form.avoid_enabled = true;
  form.is_active = true;
}

async function refresh() {
  loading.value = true;
  try {
    rules.value = await listRules();
  } finally {
    loading.value = false;
  }
}

async function refreshCategories() {
  categories.value = await listCategoryTree();
}

async function refreshTitles() {
  titles.value = await listTitles();
}

function resolveCategoryId(rule: Rule): number | null {
  if (rule.category_id) {
    return rule.category_id;
  }
  return categories.value.find((category) => category.name === rule.category)?.id ?? null;
}

function resolveSubcategoryId(
  rule: Rule,
  categoryId: number | null,
): number | null {
  if (rule.subcategory_id) {
    return rule.subcategory_id;
  }
  if (!rule.subcategory || !categoryId) {
    return null;
  }
  const category = categories.value.find((item) => item.id === categoryId);
  return (
    category?.subcategories.find((sub) => sub.name === rule.subcategory)?.id ?? null
  );
}

const availableSubcategories = computed<Subcategory[]>(() => {
  if (!form.category_id) {
    return [];
  }
  return (
    categories.value.find((category) => category.id === form.category_id)
      ?.subcategories ?? []
  );
});

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
  const categoryId = resolveCategoryId(rule);
  form.category_id = categoryId;
  form.subcategory_id = resolveSubcategoryId(rule, categoryId);
  form.title_required = rule.title_required ?? null;
  form.draw_method = rule.draw_method;
  form.avoid_enabled = rule.avoid_enabled;
  form.is_active = rule.is_active;
  dialogVisible.value = true;
}

async function submitForm() {
  try {
    if (isEditing.value && editingId.value) {
      await updateRule(editingId.value, {
        name: form.name,
        category_id: form.category_id,
        subcategory_id: form.subcategory_id,
        title_required: form.title_required,
        draw_method: form.draw_method,
        avoid_enabled: form.avoid_enabled,
        is_active: form.is_active,
      });
      ElMessage.success(t("rules.messages.updated"));
    } else {
      await createRule({
        name: form.name,
        category_id: form.category_id,
        subcategory_id: form.subcategory_id,
        title_required: form.title_required,
        draw_method: form.draw_method,
        avoid_enabled: form.avoid_enabled,
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
  await Promise.all([refresh(), refreshCategories(), refreshTitles()]);
});

watch(
  () => form.category_id,
  (value, previous) => {
    if (value !== previous) {
      form.subcategory_id = null;
    }
  },
);
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
</style>
