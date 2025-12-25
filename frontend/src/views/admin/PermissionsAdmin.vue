<template>
  <div class="page">
    <div class="toolbar">
      <div class="actions">
        <el-button type="primary" @click="openCreate">
          {{ t("permissions.new") }}
        </el-button>
        <el-button @click="refresh">{{ t("common.refresh") }}</el-button>
      </div>
      <el-input
        v-model="keyword"
        :placeholder="t('permissions.searchPlaceholder')"
        clearable
        class="search"
      />
    </div>

    <el-table
      :data="filteredPermissions"
      v-loading="loading"
      border
      stripe
      class="table"
    >
      <el-table-column :label="t('permissions.columns.id')" prop="id" width="80" />
      <el-table-column
        :label="t('permissions.columns.name')"
        prop="name"
        min-width="180"
      />
      <el-table-column
        :label="t('permissions.columns.scope')"
        prop="scope"
        min-width="200"
      />
      <el-table-column
        :label="t('permissions.columns.description')"
        prop="description"
        min-width="220"
      />
      <el-table-column :label="t('permissions.columns.actions')" width="200" fixed="right">
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

  <el-dialog
    v-model="permissionDialogVisible"
    :title="dialogTitle"
    width="520px"
  >
    <el-form :model="form" label-width="120px">
      <el-form-item :label="t('permissions.form.name')">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item :label="t('permissions.form.scope')">
        <el-input v-model="form.scope" />
      </el-form-item>
      <el-form-item :label="t('permissions.form.description')">
        <el-input v-model="form.description" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="permissionDialogVisible = false">
        {{ t("common.cancel") }}
      </el-button>
      <el-button type="primary" @click="submitPermission">
        {{ t("common.save") }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useI18n } from "vue-i18n";

import {
  createPermission,
  deletePermission,
  listPermissions,
  updatePermission,
} from "../../services/permissions";
import type { Permission } from "../../types/rbac";

interface PermissionForm {
  name: string;
  scope: string;
  description: string;
}

const permissions = ref<Permission[]>([]);
const loading = ref(false);
const keyword = ref("");
const { t } = useI18n();

const permissionDialogVisible = ref(false);
const isEditing = ref(false);
const editingId = ref<number | null>(null);

const form = reactive<PermissionForm>({
  name: "",
  scope: "",
  description: "",
});

const dialogTitle = computed(() =>
  isEditing.value ? t("permissions.dialog.edit") : t("permissions.dialog.new"),
);

const filteredPermissions = computed(() => {
  const key = keyword.value.trim().toLowerCase();
  if (!key) {
    return permissions.value;
  }
  return permissions.value.filter((permission) =>
    permission.scope.toLowerCase().includes(key),
  );
});

function resetForm() {
  form.name = "";
  form.scope = "";
  form.description = "";
}

async function refresh() {
  loading.value = true;
  try {
    permissions.value = await listPermissions();
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  resetForm();
  isEditing.value = false;
  editingId.value = null;
  permissionDialogVisible.value = true;
}

function openEdit(permission: Permission) {
  isEditing.value = true;
  editingId.value = permission.id;
  form.name = permission.name;
  form.scope = permission.scope;
  form.description = permission.description ?? "";
  permissionDialogVisible.value = true;
}

async function submitPermission() {
  try {
    if (isEditing.value && editingId.value) {
      await updatePermission(editingId.value, {
        name: form.name,
        scope: form.scope,
        description: form.description,
      });
      ElMessage.success(t("permissions.messages.updated"));
    } else {
      await createPermission({
        name: form.name,
        scope: form.scope,
        description: form.description,
      });
      ElMessage.success(t("permissions.messages.created"));
    }
    permissionDialogVisible.value = false;
    await refresh();
  } catch (error) {
    ElMessage.error(t("permissions.messages.opFailed"));
  }
}

async function confirmDelete(permission: Permission) {
  try {
    await ElMessageBox.confirm(
      t("permissions.messages.deleteConfirm", { scope: permission.scope }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  await deletePermission(permission.id);
  ElMessage.success(t("permissions.messages.deleted"));
  await refresh();
}

onMounted(refresh);
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
