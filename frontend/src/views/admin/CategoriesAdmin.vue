<template>
  <div class="page">
    <div class="toolbar">
      <div class="actions">
        <el-button type="primary" @click="openCreateCategory">
          {{ t("categories.new") }}
        </el-button>
        <el-button @click="refresh">{{ t("common.refresh") }}</el-button>
      </div>
      <el-input
        v-model="keyword"
        :placeholder="t('categories.searchPlaceholder')"
        clearable
        class="search"
      />
    </div>

    <el-table
      :data="categories"
      v-loading="loading"
      border
      stripe
      class="table"
      @sort-change="handleSortChange"
    >
      <el-table-column
        :label="t('categories.columns.id')"
        prop="id"
        width="80"
        sortable="custom"
      />
      <el-table-column
        :label="t('categories.columns.name')"
        prop="name"
        min-width="160"
        sortable="custom"
      />
      <el-table-column
        :label="t('categories.columns.code')"
        prop="code"
        min-width="140"
        sortable="custom"
      />
      <el-table-column
        :label="t('categories.columns.sort')"
        prop="sort_order"
        width="100"
        sortable="custom"
      />
      <el-table-column
        :label="t('categories.columns.active')"
        width="100"
        prop="is_active"
        sortable="custom"
      >
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? t("common.yes") : t("common.no") }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        :label="t('categories.columns.actions')"
        width="260"
        fixed="right"
      >
        <template #default="{ row }">
          <el-button link type="primary" @click="openEditCategory(row)">
            {{ t("common.edit") }}
          </el-button>
          <el-button link @click="openSubcategories(row)">
            {{ t("categories.actions.subcategories") }}
          </el-button>
          <el-button link type="danger" @click="confirmDeleteCategory(row)">
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

  <el-dialog v-model="categoryDialogVisible" :title="categoryDialogTitle" width="520px">
    <el-form :model="categoryForm" label-width="120px">
      <el-form-item :label="t('categories.form.name')">
        <el-input v-model="categoryForm.name" />
      </el-form-item>
      <el-form-item :label="t('categories.form.code')">
        <el-input v-model="categoryForm.code" />
      </el-form-item>
      <el-form-item :label="t('categories.form.sort')">
        <el-input-number v-model="categoryForm.sort_order" :min="0" />
      </el-form-item>
      <el-form-item :label="t('categories.form.active')">
        <el-switch v-model="categoryForm.is_active" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="categoryDialogVisible = false">
        {{ t("common.cancel") }}
      </el-button>
      <el-button type="primary" @click="submitCategory">
        {{ t("common.save") }}
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="subcategoryDialogVisible"
    :title="subcategoryDialogTitle"
    width="640px"
  >
    <div class="subtoolbar">
      <div class="actions">
        <el-button type="primary" @click="openCreateSubcategory">
          {{ t("categories.subcategories.new") }}
        </el-button>
        <el-button @click="refreshSubcategories">
          {{ t("common.refresh") }}
        </el-button>
      </div>
      <el-input
        v-model="subKeyword"
        :placeholder="t('categories.searchPlaceholder')"
        clearable
        class="search"
      />
    </div>
    <el-table
      :data="subcategories"
      v-loading="subcategoryLoading"
      border
      stripe
      @sort-change="handleSubSortChange"
    >
      <el-table-column
        :label="t('categories.subcategories.columns.id')"
        prop="id"
        width="80"
        sortable="custom"
      />
      <el-table-column
        :label="t('categories.subcategories.columns.name')"
        prop="name"
        min-width="160"
        sortable="custom"
      />
      <el-table-column
        :label="t('categories.subcategories.columns.code')"
        prop="code"
        min-width="140"
        sortable="custom"
      />
      <el-table-column
        :label="t('categories.subcategories.columns.sort')"
        prop="sort_order"
        width="100"
        sortable="custom"
      />
      <el-table-column
        :label="t('categories.subcategories.columns.active')"
        width="100"
        prop="is_active"
        sortable="custom"
      >
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? t("common.yes") : t("common.no") }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        :label="t('categories.subcategories.columns.actions')"
        width="200"
        fixed="right"
      >
        <template #default="{ row }">
          <el-button link type="primary" @click="openEditSubcategory(row)">
            {{ t("common.edit") }}
          </el-button>
          <el-button link type="danger" @click="confirmDeleteSubcategory(row)">
            {{ t("common.delete") }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager subpager">
      <el-pagination
        v-model:current-page="subPage"
        v-model:page-size="subPageSize"
        :total="subTotal"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handleSubPageChange"
        @size-change="handleSubPageSizeChange"
      />
    </div>
    <template #footer>
      <el-button @click="subcategoryDialogVisible = false">
        {{ t("common.cancel") }}
      </el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="subcategoryFormVisible" :title="subcategoryFormTitle" width="520px">
    <el-form :model="subcategoryForm" label-width="120px">
      <el-form-item :label="t('categories.subcategories.form.name')">
        <el-input v-model="subcategoryForm.name" />
      </el-form-item>
      <el-form-item :label="t('categories.subcategories.form.code')">
        <el-input v-model="subcategoryForm.code" />
      </el-form-item>
      <el-form-item :label="t('categories.subcategories.form.sort')">
        <el-input-number v-model="subcategoryForm.sort_order" :min="0" />
      </el-form-item>
      <el-form-item :label="t('categories.subcategories.form.active')">
        <el-switch v-model="subcategoryForm.is_active" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="subcategoryFormVisible = false">
        {{ t("common.cancel") }}
      </el-button>
      <el-button type="primary" @click="submitSubcategory">
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
  createCategory,
  createSubcategory,
  deleteCategory,
  deleteSubcategory,
  listCategories,
  listSubcategories,
  updateCategory,
  updateSubcategory,
} from "../../services/categories";
import type { Category, Subcategory } from "../../types/domain";

interface CategoryForm {
  name: string;
  code: string;
  sort_order: number;
  is_active: boolean;
}

interface SubcategoryForm {
  name: string;
  code: string;
  sort_order: number;
  is_active: boolean;
}

const categories = ref<Category[]>([]);
const loading = ref(false);
const keyword = ref("");
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const sortBy = ref<string | undefined>();
const sortOrder = ref<"asc" | "desc" | undefined>();
const { t } = useI18n();

const categoryDialogVisible = ref(false);
const isEditingCategory = ref(false);
const editingCategoryId = ref<number | null>(null);

const categoryForm = reactive<CategoryForm>({
  name: "",
  code: "",
  sort_order: 0,
  is_active: true,
});

const subcategoryDialogVisible = ref(false);
const subcategoryLoading = ref(false);
const selectedCategory = ref<Category | null>(null);
const subcategories = ref<Subcategory[]>([]);
const subKeyword = ref("");
const subPage = ref(1);
const subPageSize = ref(10);
const subTotal = ref(0);
const subSortBy = ref<string | undefined>();
const subSortOrder = ref<"asc" | "desc" | undefined>();

const subcategoryFormVisible = ref(false);
const isEditingSubcategory = ref(false);
const editingSubcategoryId = ref<number | null>(null);
const subcategoryForm = reactive<SubcategoryForm>({
  name: "",
  code: "",
  sort_order: 0,
  is_active: true,
});

const categoryDialogTitle = computed(() =>
  isEditingCategory.value
    ? t("categories.dialog.edit")
    : t("categories.dialog.new"),
);

const subcategoryDialogTitle = computed(() => {
  if (!selectedCategory.value) {
    return t("categories.subcategories.title");
  }
  return t("categories.subcategories.titleWithName", {
    name: selectedCategory.value.name,
  });
});

const subcategoryFormTitle = computed(() =>
  isEditingSubcategory.value
    ? t("categories.subcategories.dialog.edit")
    : t("categories.subcategories.dialog.new"),
);

let keywordTimer: number | undefined;
let subKeywordTimer: number | undefined;

watch(keyword, () => {
  if (keywordTimer) {
    window.clearTimeout(keywordTimer);
  }
  keywordTimer = window.setTimeout(() => {
    page.value = 1;
    refresh();
  }, 300);
});

watch(subKeyword, () => {
  if (subKeywordTimer) {
    window.clearTimeout(subKeywordTimer);
  }
  subKeywordTimer = window.setTimeout(() => {
    subPage.value = 1;
    refreshSubcategories();
  }, 300);
});

function resetCategoryForm() {
  categoryForm.name = "";
  categoryForm.code = "";
  categoryForm.sort_order = 0;
  categoryForm.is_active = true;
}

function resetSubcategoryForm() {
  subcategoryForm.name = "";
  subcategoryForm.code = "";
  subcategoryForm.sort_order = 0;
  subcategoryForm.is_active = true;
}

async function refresh() {
  loading.value = true;
  try {
    const result = await listCategories({
      page: page.value,
      page_size: pageSize.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      keyword: keyword.value.trim() || undefined,
    });
    categories.value = result.items;
    total.value = result.total;
  } finally {
    loading.value = false;
  }
}

async function refreshSubcategories() {
  if (!selectedCategory.value) {
    return;
  }
  subcategoryLoading.value = true;
  try {
    const result = await listSubcategories(selectedCategory.value.id, {
      page: subPage.value,
      page_size: subPageSize.value,
      sort_by: subSortBy.value,
      sort_order: subSortOrder.value,
      keyword: subKeyword.value.trim() || undefined,
    });
    subcategories.value = result.items;
    subTotal.value = result.total;
  } finally {
    subcategoryLoading.value = false;
  }
}

function openCreateCategory() {
  resetCategoryForm();
  isEditingCategory.value = false;
  editingCategoryId.value = null;
  categoryDialogVisible.value = true;
}

function openEditCategory(category: Category) {
  isEditingCategory.value = true;
  editingCategoryId.value = category.id;
  categoryForm.name = category.name;
  categoryForm.code = category.code ?? "";
  categoryForm.sort_order = category.sort_order;
  categoryForm.is_active = category.is_active;
  categoryDialogVisible.value = true;
}

async function submitCategory() {
  try {
    if (isEditingCategory.value && editingCategoryId.value) {
      await updateCategory(editingCategoryId.value, {
        name: categoryForm.name,
        code: categoryForm.code || null,
        sort_order: categoryForm.sort_order,
        is_active: categoryForm.is_active,
      });
      ElMessage.success(t("categories.messages.updated"));
    } else {
      await createCategory({
        name: categoryForm.name,
        code: categoryForm.code || null,
        sort_order: categoryForm.sort_order,
        is_active: categoryForm.is_active,
      });
      ElMessage.success(t("categories.messages.created"));
    }
    categoryDialogVisible.value = false;
    await refresh();
  } catch (error) {
    ElMessage.error(t("categories.messages.opFailed"));
  }
}

async function confirmDeleteCategory(category: Category) {
  try {
    await ElMessageBox.confirm(
      t("categories.messages.deleteConfirm", { name: category.name }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  try {
    await deleteCategory(category.id);
    ElMessage.success(t("categories.messages.deleted"));
    await refresh();
  } catch (error) {
    ElMessage.error(t("categories.messages.deleteFailed"));
  }
}

function openSubcategories(category: Category) {
  selectedCategory.value = category;
  subPage.value = 1;
  subSortBy.value = undefined;
  subSortOrder.value = undefined;
  subcategoryDialogVisible.value = true;
  refreshSubcategories();
}

function openCreateSubcategory() {
  resetSubcategoryForm();
  isEditingSubcategory.value = false;
  editingSubcategoryId.value = null;
  subcategoryFormVisible.value = true;
}

function openEditSubcategory(subcategory: Subcategory) {
  isEditingSubcategory.value = true;
  editingSubcategoryId.value = subcategory.id;
  subcategoryForm.name = subcategory.name;
  subcategoryForm.code = subcategory.code ?? "";
  subcategoryForm.sort_order = subcategory.sort_order;
  subcategoryForm.is_active = subcategory.is_active;
  subcategoryFormVisible.value = true;
}

async function submitSubcategory() {
  if (!selectedCategory.value) {
    return;
  }
  try {
    if (isEditingSubcategory.value && editingSubcategoryId.value) {
      await updateSubcategory(editingSubcategoryId.value, {
        name: subcategoryForm.name,
        code: subcategoryForm.code || null,
        sort_order: subcategoryForm.sort_order,
        is_active: subcategoryForm.is_active,
      });
      ElMessage.success(t("categories.subcategories.messages.updated"));
    } else {
      await createSubcategory(selectedCategory.value.id, {
        name: subcategoryForm.name,
        code: subcategoryForm.code || null,
        sort_order: subcategoryForm.sort_order,
        is_active: subcategoryForm.is_active,
      });
      ElMessage.success(t("categories.subcategories.messages.created"));
    }
    subcategoryFormVisible.value = false;
    await refreshSubcategories();
  } catch (error) {
    ElMessage.error(t("categories.subcategories.messages.opFailed"));
  }
}

async function confirmDeleteSubcategory(subcategory: Subcategory) {
  try {
    await ElMessageBox.confirm(
      t("categories.subcategories.messages.deleteConfirm", {
        name: subcategory.name,
      }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  try {
    await deleteSubcategory(subcategory.id);
    ElMessage.success(t("categories.subcategories.messages.deleted"));
    await refreshSubcategories();
  } catch (error) {
    ElMessage.error(t("categories.subcategories.messages.deleteFailed"));
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

function handleSubSortChange({
  prop,
  order,
}: {
  prop?: string;
  order?: "ascending" | "descending" | null;
}) {
  if (!prop || !order) {
    subSortBy.value = undefined;
    subSortOrder.value = undefined;
  } else {
    subSortBy.value = prop;
    subSortOrder.value = order === "ascending" ? "asc" : "desc";
  }
  subPage.value = 1;
  refreshSubcategories();
}

function handleSubPageChange(value: number) {
  subPage.value = value;
  refreshSubcategories();
}

function handleSubPageSizeChange(value: number) {
  subPageSize.value = value;
  subPage.value = 1;
  refreshSubcategories();
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

.subtoolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
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

.subpager {
  margin-top: 12px;
}
</style>
