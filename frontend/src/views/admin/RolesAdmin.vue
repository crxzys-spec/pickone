<template>
  <div class="page">
    <div class="toolbar">
      <div class="actions">
        <el-button type="primary" @click="openCreate">
          {{ t("roles.new") }}
        </el-button>
        <el-button @click="refresh">{{ t("common.refresh") }}</el-button>
      </div>
      <el-input
        v-model="keyword"
        :placeholder="t('roles.searchPlaceholder')"
        clearable
        class="search"
      />
    </div>

    <el-table
      :data="roles"
      v-loading="loading"
      border
      stripe
      class="table"
      @sort-change="handleSortChange"
    >
      <el-table-column
        :label="t('roles.columns.id')"
        prop="id"
        width="80"
        sortable="custom"
      />
      <el-table-column
        :label="t('roles.columns.name')"
        prop="name"
        min-width="160"
        sortable="custom"
      />
      <el-table-column
        :label="t('roles.columns.description')"
        prop="description"
        min-width="220"
        sortable="custom"
      />
      <el-table-column :label="t('roles.columns.permissions')" min-width="260">
        <template #default="{ row }">
          <el-tag
            v-for="permission in row.permissions"
            :key="permission.id"
            class="tag"
          >
            {{ permission.scope }}
          </el-tag>
          <span v-if="!row.permissions?.length" class="muted">-</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('roles.columns.actions')" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">
            {{ t("common.edit") }}
          </el-button>
          <el-button link @click="openAssignPermissions(row)">
            {{ t("roles.actions.permissions") }}
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

  <el-dialog v-model="roleDialogVisible" :title="dialogTitle" width="520px">
    <el-form :model="form" label-width="120px">
      <el-form-item :label="t('roles.form.name')" required>
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item :label="t('roles.form.description')">
        <el-input v-model="form.description" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="roleDialogVisible = false">
        {{ t("common.cancel") }}
      </el-button>
      <el-button type="primary" @click="submitRole">
        {{ t("common.save") }}
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="permissionDialogVisible"
    :title="t('roles.dialog.assignPermissions')"
    width="520px"
  >
    <el-form label-width="120px">
      <el-form-item :label="t('roles.form.permissions')">
        <el-select
          v-model="permissionForm.permission_ids"
          multiple
          filterable
          style="width: 100%;"
        >
          <el-option
            v-for="permission in permissions"
            :key="permission.id"
            :label="permission.scope"
            :value="permission.id"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="permissionDialogVisible = false">
        {{ t("common.cancel") }}
      </el-button>
      <el-button type="primary" @click="submitPermissions">
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
  assignRolePermissions,
  createRole,
  deleteRole,
  listRoles,
  listRolesAll,
  updateRole,
} from "../../services/roles";
import { listPermissionsAll } from "../../services/permissions";
import type { Permission, Role } from "../../types/rbac";

interface RoleForm {
  name: string;
  description: string;
}

const roles = ref<Role[]>([]);
const permissions = ref<Permission[]>([]);
const loading = ref(false);
const keyword = ref("");
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const sortBy = ref<string | undefined>();
const sortOrder = ref<"asc" | "desc" | undefined>();
const { t } = useI18n();

const roleDialogVisible = ref(false);
const permissionDialogVisible = ref(false);
const isEditing = ref(false);
const editingId = ref<number | null>(null);
const permissionTargetId = ref<number | null>(null);

const form = reactive<RoleForm>({
  name: "",
  description: "",
});

const permissionForm = reactive({
  permission_ids: [] as number[],
});

const dialogTitle = computed(() =>
  isEditing.value ? t("roles.dialog.edit") : t("roles.dialog.new"),
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
  form.description = "";
}

async function refresh() {
  loading.value = true;
  try {
    const result = await listRoles({
      page: page.value,
      page_size: pageSize.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      keyword: keyword.value.trim() || undefined,
    });
    roles.value = result.items;
    total.value = result.total;
  } finally {
    loading.value = false;
  }
}

async function refreshPermissions() {
  permissions.value = await listPermissionsAll();
}

function openCreate() {
  resetForm();
  isEditing.value = false;
  editingId.value = null;
  roleDialogVisible.value = true;
}

function openEdit(role: Role) {
  isEditing.value = true;
  editingId.value = role.id;
  form.name = role.name;
  form.description = role.description ?? "";
  roleDialogVisible.value = true;
}

async function submitRole() {
  try {
    if (isEditing.value && editingId.value) {
      await updateRole(editingId.value, {
        name: form.name,
        description: form.description,
      });
      ElMessage.success(t("roles.messages.updated"));
    } else {
      await createRole({
        name: form.name,
        description: form.description,
      });
      ElMessage.success(t("roles.messages.created"));
    }
    roleDialogVisible.value = false;
    await refresh();
  } catch (error) {
    ElMessage.error(t("roles.messages.opFailed"));
  }
}

function openAssignPermissions(role: Role) {
  permissionTargetId.value = role.id;
  permissionForm.permission_ids = role.permissions?.map((perm) => perm.id) ?? [];
  permissionDialogVisible.value = true;
}

async function submitPermissions() {
  if (!permissionTargetId.value) {
    return;
  }
  try {
    await assignRolePermissions(permissionTargetId.value, {
      permission_ids: permissionForm.permission_ids,
    });
    ElMessage.success(t("roles.messages.permissionsUpdated"));
    permissionDialogVisible.value = false;
    await refresh();
  } catch (error) {
    ElMessage.error(t("roles.messages.opFailed"));
  }
}

async function confirmDelete(role: Role) {
  try {
    await ElMessageBox.confirm(
      t("roles.messages.deleteConfirm", { name: role.name }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  await deleteRole(role.id);
  ElMessage.success(t("roles.messages.deleted"));
  await refresh();
}

onMounted(async () => {
  await Promise.all([refresh(), refreshPermissions()]);
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

.tag {
  margin-right: 6px;
  margin-bottom: 4px;
}

.muted {
  color: #9aa3b2;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
