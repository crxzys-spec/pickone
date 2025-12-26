<template>
  <div class="page">
    <div class="toolbar">
      <div class="actions">
        <el-button type="primary" @click="openCreate">
          {{ t("organizations.new") }}
        </el-button>
        <el-button @click="refresh">{{ t("common.refresh") }}</el-button>
      </div>
      <el-input
        v-model="keyword"
        :placeholder="t('organizations.searchPlaceholder')"
        clearable
        class="search"
      />
    </div>

    <el-table
      :data="organizations"
      v-loading="loading"
      border
      stripe
      class="table"
      @sort-change="handleSortChange"
    >
      <el-table-column
        :label="t('organizations.columns.id')"
        prop="id"
        width="80"
        sortable="custom"
      />
      <el-table-column
        :label="t('organizations.columns.name')"
        prop="name"
        min-width="180"
        sortable="custom"
      />
      <el-table-column
        :label="t('organizations.columns.code')"
        prop="code"
        min-width="160"
        sortable="custom"
      />
      <el-table-column
        :label="t('organizations.columns.sort')"
        prop="sort_order"
        width="120"
        sortable="custom"
      />
      <el-table-column
        :label="t('organizations.columns.active')"
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
      <el-table-column :label="t('organizations.columns.actions')" width="200" fixed="right">
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
      <el-form-item :label="t('organizations.form.name')">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item :label="t('organizations.form.code')">
        <el-input v-model="form.code" />
      </el-form-item>
      <el-form-item :label="t('organizations.form.sort')">
        <el-input-number v-model="form.sort_order" :min="0" />
      </el-form-item>
      <el-form-item :label="t('organizations.form.active')">
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
  createOrganization,
  deleteOrganization,
  listOrganizations,
  updateOrganization,
} from "../../services/organizations";
import type { Organization } from "../../types/domain";

interface OrganizationForm {
  name: string;
  code: string;
  sort_order: number;
  is_active: boolean;
}

const organizations = ref<Organization[]>([]);
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

const form = reactive<OrganizationForm>({
  name: "",
  code: "",
  sort_order: 0,
  is_active: true,
});

const dialogTitle = computed(() =>
  isEditing.value ? t("organizations.dialog.edit") : t("organizations.dialog.new"),
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
    const result = await listOrganizations({
      page: page.value,
      page_size: pageSize.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      keyword: keyword.value.trim() || undefined,
    });
    organizations.value = result.items;
    total.value = result.total;
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

function openEdit(organization: Organization) {
  isEditing.value = true;
  editingId.value = organization.id;
  form.name = organization.name;
  form.code = organization.code ?? "";
  form.sort_order = organization.sort_order;
  form.is_active = organization.is_active;
  dialogVisible.value = true;
}

async function submitForm() {
  try {
    if (isEditing.value && editingId.value) {
      await updateOrganization(editingId.value, {
        name: form.name,
        code: form.code || null,
        sort_order: form.sort_order,
        is_active: form.is_active,
      });
      ElMessage.success(t("organizations.messages.updated"));
    } else {
      await createOrganization({
        name: form.name,
        code: form.code || null,
        sort_order: form.sort_order,
        is_active: form.is_active,
      });
      ElMessage.success(t("organizations.messages.created"));
    }
    dialogVisible.value = false;
    await refresh();
  } catch (error) {
    ElMessage.error(t("organizations.messages.opFailed"));
  }
}

async function confirmDelete(organization: Organization) {
  try {
    await ElMessageBox.confirm(
      t("organizations.messages.deleteConfirm", { name: organization.name }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  await deleteOrganization(organization.id);
  ElMessage.success(t("organizations.messages.deleted"));
  await refresh();
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
