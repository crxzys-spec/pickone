<template>
  <div class="page">
    <div class="toolbar">
      <div class="actions">
        <el-button type="primary" @click="openCreate">
          {{ t("experts.new") }}
        </el-button>
        <el-upload
          :show-file-list="false"
          :http-request="handleImport"
          accept=".xlsx"
        >
          <el-button :loading="importing">{{ t("common.import") }}</el-button>
        </el-upload>
        <el-button :loading="exporting" @click="handleExport">
          {{ t("common.export") }}
        </el-button>
        <el-button @click="refresh">{{ t("common.refresh") }}</el-button>
      </div>
      <el-input
        v-model="keyword"
        :placeholder="t('experts.searchPlaceholder')"
        clearable
        class="search"
      />
    </div>

    <el-table
      :data="filteredExperts"
      v-loading="loading"
      border
      stripe
      class="table"
    >
      <el-table-column :label="t('experts.columns.id')" prop="id" width="80" />
      <el-table-column
        :label="t('experts.columns.name')"
        prop="name"
        min-width="140"
      />
      <el-table-column :label="t('experts.columns.gender')" width="90">
        <template #default="{ row }">
          {{ genderLabel(row.gender) }}
        </template>
      </el-table-column>
      <el-table-column
        :label="t('experts.columns.company')"
        prop="company"
        min-width="180"
      />
      <el-table-column
        :label="t('experts.columns.category')"
        prop="category"
        min-width="120"
      />
      <el-table-column
        :label="t('experts.columns.subcategory')"
        prop="subcategory"
        min-width="120"
      />
      <el-table-column
        :label="t('experts.columns.title')"
        prop="title"
        min-width="120"
      />
      <el-table-column
        :label="t('experts.columns.phone')"
        prop="phone"
        min-width="140"
      />
      <el-table-column :label="t('experts.columns.active')" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? t("common.yes") : t("common.no") }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('experts.columns.actions')" width="220" fixed="right">
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

  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="620px">
    <el-form :model="form" label-width="120px">
      <el-form-item :label="t('experts.form.name')">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item :label="t('experts.form.gender')">
        <el-select v-model="form.gender" clearable style="width: 100%;">
          <el-option :label="t('experts.gender.male')" value="男" />
          <el-option :label="t('experts.gender.female')" value="女" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('experts.form.phone')">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item :label="t('experts.form.email')">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-form-item :label="t('experts.form.company')">
        <el-select
          v-model="form.organization_id"
          clearable
          filterable
          style="width: 100%;"
          @change="handleOrganizationChange"
        >
          <el-option
            v-for="organization in organizations"
            :key="organization.id"
            :label="organization.name"
            :value="organization.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('experts.form.title')">
        <el-select
          v-model="form.title_id"
          clearable
          filterable
          style="width: 100%;"
          @change="handleTitleChange"
        >
          <el-option
            v-for="title in titles"
            :key="title.id"
            :label="title.name"
            :value="title.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('experts.form.category')">
        <el-select
          v-model="form.category_id"
          clearable
          filterable
          style="width: 100%;"
          @change="handleCategoryChange"
        >
          <el-option
            v-for="category in categoryTree"
            :key="category.id"
            :label="category.name"
            :value="category.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('experts.form.subcategory')">
        <el-select
          v-model="form.subcategory_id"
          clearable
          filterable
          style="width: 100%;"
          :disabled="!form.category_id"
        >
          <el-option
            v-for="subcategory in subcategoryOptions"
            :key="subcategory.id"
            :label="subcategory.name"
            :value="subcategory.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('experts.form.avoidUnits')">
        <el-input v-model="form.avoid_units" />
      </el-form-item>
      <el-form-item :label="t('experts.form.avoidPersons')">
        <el-input v-model="form.avoid_persons" />
      </el-form-item>
      <el-form-item :label="t('experts.form.active')">
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
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox, type UploadRequestOptions } from "element-plus";
import { useI18n } from "vue-i18n";

import {
  createExpert,
  deleteExpert,
  exportExperts,
  importExperts,
  listExperts,
  updateExpert,
} from "../../services/experts";
import { listCategoryTree } from "../../services/categories";
import { listOrganizations } from "../../services/organizations";
import { listTitles } from "../../services/titles";
import type {
  CategoryTree,
  Expert,
  Organization,
  Subcategory,
  Title,
} from "../../types/domain";

interface ExpertForm {
  name: string;
  gender: string;
  phone: string;
  email: string;
  company: string;
  organization_id: number | null;
  title: string;
  title_id: number | null;
  category_id: number | null;
  subcategory_id: number | null;
  avoid_units: string;
  avoid_persons: string;
  is_active: boolean;
}

const experts = ref<Expert[]>([]);
const categoryTree = ref<CategoryTree[]>([]);
const organizations = ref<Organization[]>([]);
const titles = ref<Title[]>([]);
const loading = ref(false);
const importing = ref(false);
const exporting = ref(false);
const keyword = ref("");
const { t } = useI18n();

const dialogVisible = ref(false);
const isEditing = ref(false);
const editingId = ref<number | null>(null);

const form = reactive<ExpertForm>({
  name: "",
  gender: "",
  phone: "",
  email: "",
  company: "",
  organization_id: null,
  title: "",
  title_id: null,
  category_id: null,
  subcategory_id: null,
  avoid_units: "",
  avoid_persons: "",
  is_active: true,
});

const dialogTitle = computed(() =>
  isEditing.value ? t("experts.dialog.edit") : t("experts.dialog.new"),
);

const filteredExperts = computed(() => {
  const key = keyword.value.trim().toLowerCase();
  if (!key) {
    return experts.value;
  }
  return experts.value.filter((expert) => {
    const company = expert.company ?? "";
    const phone = expert.phone ?? "";
    return (
      expert.name.toLowerCase().includes(key) ||
      company.toLowerCase().includes(key) ||
      phone.toLowerCase().includes(key)
    );
  });
});

function resetForm() {
  form.name = "";
  form.gender = "";
  form.phone = "";
  form.email = "";
  form.company = "";
  form.organization_id = null;
  form.title = "";
  form.title_id = null;
  form.category_id = null;
  form.subcategory_id = null;
  form.avoid_units = "";
  form.avoid_persons = "";
  form.is_active = true;
}

function genderLabel(value?: string | null) {
  if (!value) {
    return "-";
  }
  if (value === "男") {
    return t("experts.gender.male");
  }
  if (value === "女") {
    return t("experts.gender.female");
  }
  return value;
}

async function refresh() {
  loading.value = true;
  try {
    experts.value = await listExperts();
  } finally {
    loading.value = false;
  }
}

async function refreshCategories() {
  categoryTree.value = await listCategoryTree();
}

async function refreshOrganizations() {
  organizations.value = await listOrganizations();
}

async function refreshTitles() {
  titles.value = await listTitles();
}

const subcategoryOptions = computed<Subcategory[]>(() => {
  if (!form.category_id) {
    return [];
  }
  return (
    categoryTree.value.find((category) => category.id === form.category_id)
      ?.subcategories ?? []
  );
});

function handleCategoryChange() {
  form.subcategory_id = null;
}

function handleOrganizationChange() {
  const organization = organizations.value.find(
    (item) => item.id === form.organization_id,
  );
  form.company = organization?.name ?? "";
}

function handleTitleChange() {
  const selected = titles.value.find((item) => item.id === form.title_id);
  form.title = selected?.name ?? "";
}

function resolveCategoryId(expert: Expert): number | null {
  if (expert.category_id) {
    return expert.category_id;
  }
  if (!expert.category) {
    return null;
  }
  return (
    categoryTree.value.find((category) => category.name === expert.category)
      ?.id ?? null
  );
}

function resolveSubcategoryId(
  categoryId: number | null,
  expert: Expert,
): number | null {
  if (expert.subcategory_id) {
    return expert.subcategory_id;
  }
  if (!categoryId || !expert.subcategory) {
    return null;
  }
  const category = categoryTree.value.find((item) => item.id === categoryId);
  return category?.subcategories.find((sub) => sub.name === expert.subcategory)?.id ?? null;
}

function resolveOrganizationId(expert: Expert): number | null {
  if (expert.organization_id) {
    return expert.organization_id;
  }
  if (!expert.company) {
    return null;
  }
  return organizations.value.find((item) => item.name === expert.company)?.id ?? null;
}

function resolveTitleId(expert: Expert): number | null {
  if (expert.title_id) {
    return expert.title_id;
  }
  if (!expert.title) {
    return null;
  }
  return titles.value.find((item) => item.name === expert.title)?.id ?? null;
}

function openCreate() {
  resetForm();
  isEditing.value = false;
  editingId.value = null;
  dialogVisible.value = true;
}

function openEdit(expert: Expert) {
  isEditing.value = true;
  editingId.value = expert.id;
  form.name = expert.name;
  form.gender = expert.gender ?? "";
  form.phone = expert.phone ?? "";
  form.email = expert.email ?? "";
  form.organization_id = resolveOrganizationId(expert);
  form.title_id = resolveTitleId(expert);
  form.company = expert.company ?? "";
  form.title = expert.title ?? "";
  form.category_id = resolveCategoryId(expert);
  form.subcategory_id = resolveSubcategoryId(form.category_id, expert);
  form.avoid_units = expert.avoid_units ?? "";
  form.avoid_persons = expert.avoid_persons ?? "";
  form.is_active = expert.is_active;
  dialogVisible.value = true;
}

async function submitForm() {
  try {
    if (isEditing.value && editingId.value) {
      await updateExpert(editingId.value, {
        name: form.name,
        gender: form.gender,
        phone: form.phone,
        email: form.email,
        company: form.company,
        organization_id: form.organization_id,
        title: form.title,
        title_id: form.title_id,
        category_id: form.category_id,
        subcategory_id: form.subcategory_id,
        avoid_units: form.avoid_units,
        avoid_persons: form.avoid_persons,
        is_active: form.is_active,
      });
      ElMessage.success(t("experts.messages.updated"));
    } else {
      await createExpert({
        name: form.name,
        gender: form.gender,
        phone: form.phone,
        email: form.email,
        company: form.company,
        organization_id: form.organization_id,
        title: form.title,
        title_id: form.title_id,
        category_id: form.category_id,
        subcategory_id: form.subcategory_id,
        avoid_units: form.avoid_units,
        avoid_persons: form.avoid_persons,
        is_active: form.is_active,
      });
      ElMessage.success(t("experts.messages.created"));
    }
    dialogVisible.value = false;
    await refresh();
  } catch (error) {
    ElMessage.error(t("experts.messages.opFailed"));
  }
}

async function confirmDelete(expert: Expert) {
  try {
    await ElMessageBox.confirm(
      t("experts.messages.deleteConfirm", { name: expert.name }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  await deleteExpert(expert.id);
  ElMessage.success(t("experts.messages.deleted"));
  await refresh();
}

async function handleImport(options: UploadRequestOptions) {
  importing.value = true;
  try {
    const result = await importExperts(options.file as File);
    ElMessage.success(
      t("experts.messages.importSuccess", {
        created: result.created,
        skipped: result.skipped,
      }),
    );
    await refresh();
    options.onSuccess?.(result);
  } catch (error) {
    ElMessage.error(t("experts.messages.importFailed"));
    options.onError?.(error as Error);
  } finally {
    importing.value = false;
  }
}

async function handleExport() {
  exporting.value = true;
  try {
    const blob = await exportExperts();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "experts_export.xlsx";
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    ElMessage.error(t("experts.messages.exportFailed"));
  } finally {
    exporting.value = false;
  }
}

onMounted(async () => {
  await Promise.all([
    refresh(),
    refreshCategories(),
    refreshOrganizations(),
    refreshTitles(),
  ]);
});
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
