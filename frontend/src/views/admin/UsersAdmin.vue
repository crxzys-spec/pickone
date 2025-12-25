<template>
  <div class="page">
    <div class="toolbar">
      <div class="actions">
        <el-button type="primary" @click="openCreate">
          {{ t("users.new") }}
        </el-button>
        <el-button @click="refresh">{{ t("common.refresh") }}</el-button>
      </div>
      <el-input
        v-model="keyword"
        :placeholder="t('users.searchPlaceholder')"
        clearable
        class="search"
      />
    </div>

    <el-table
      :data="filteredUsers"
      v-loading="loading"
      border
      stripe
      class="table"
    >
      <el-table-column :label="t('users.columns.id')" prop="id" width="80" />
      <el-table-column
        :label="t('users.columns.username')"
        prop="username"
        min-width="160"
      />
      <el-table-column
        :label="t('users.columns.name')"
        prop="full_name"
        min-width="160"
      />
      <el-table-column
        :label="t('users.columns.email')"
        prop="email"
        min-width="200"
      />
      <el-table-column :label="t('users.columns.active')" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? t("common.yes") : t("common.no") }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('users.columns.superuser')" width="120">
        <template #default="{ row }">
          <el-tag :type="row.is_superuser ? 'warning' : 'info'">
            {{ row.is_superuser ? t("common.yes") : t("common.no") }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('users.columns.roles')" min-width="200">
        <template #default="{ row }">
          <el-tag
            v-for="role in row.roles"
            :key="role.id"
            class="tag"
          >
            {{ role.name }}
          </el-tag>
          <span v-if="!row.roles?.length" class="muted">-</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('users.columns.actions')" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">
            {{ t("common.edit") }}
          </el-button>
          <el-button link @click="openAssignRoles(row)">
            {{ t("users.actions.roles") }}
          </el-button>
          <el-button link type="danger" @click="confirmDelete(row)">
            {{ t("common.delete") }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>

  <el-dialog v-model="userDialogVisible" :title="dialogTitle" width="520px">
    <el-form :model="form" label-width="120px">
      <el-form-item :label="t('users.form.username')">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item :label="t('users.form.fullName')">
        <el-input v-model="form.full_name" />
      </el-form-item>
      <el-form-item :label="t('users.form.email')">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-form-item :label="t('users.form.password')">
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>
      <el-form-item :label="t('users.form.active')">
        <el-switch v-model="form.is_active" />
      </el-form-item>
      <el-form-item :label="t('users.form.superuser')">
        <el-switch v-model="form.is_superuser" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="userDialogVisible = false">
        {{ t("common.cancel") }}
      </el-button>
      <el-button type="primary" @click="submitUser">
        {{ t("common.save") }}
      </el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="roleDialogVisible"
    :title="t('users.dialog.assignRoles')"
    width="520px"
  >
    <el-form label-width="120px">
      <el-form-item :label="t('users.form.roles')">
        <el-select
          v-model="roleForm.role_ids"
          multiple
          filterable
          style="width: 100%;"
        >
          <el-option
            v-for="role in roles"
            :key="role.id"
            :label="role.name"
            :value="role.id"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="roleDialogVisible = false">
        {{ t("common.cancel") }}
      </el-button>
      <el-button type="primary" @click="submitRoles">
        {{ t("common.save") }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useI18n } from "vue-i18n";

import { listRoles } from "../../services/roles";
import {
  assignUserRoles,
  createUser,
  deleteUser,
  listUsers,
  updateUser,
} from "../../services/users";
import type { Role, User } from "../../types/rbac";

interface UserForm {
  username: string;
  full_name: string;
  email: string;
  password: string;
  is_active: boolean;
  is_superuser: boolean;
}

const users = ref<User[]>([]);
const roles = ref<Role[]>([]);
const loading = ref(false);
const keyword = ref("");
const { t } = useI18n();

const userDialogVisible = ref(false);
const roleDialogVisible = ref(false);
const isEditing = ref(false);
const editingId = ref<number | null>(null);
const roleTargetId = ref<number | null>(null);

const form = reactive<UserForm>({
  username: "",
  full_name: "",
  email: "",
  password: "",
  is_active: true,
  is_superuser: false,
});

const roleForm = reactive({
  role_ids: [] as number[],
});

const dialogTitle = computed(() =>
  isEditing.value ? t("users.dialog.edit") : t("users.dialog.new"),
);

const filteredUsers = computed(() => {
  const key = keyword.value.trim().toLowerCase();
  if (!key) {
    return users.value;
  }
  return users.value.filter((user) => {
    const fullName = user.full_name ?? "";
    const email = user.email ?? "";
    return (
      user.username.toLowerCase().includes(key) ||
      fullName.toLowerCase().includes(key) ||
      email.toLowerCase().includes(key)
    );
  });
});

function resetForm() {
  form.username = "";
  form.full_name = "";
  form.email = "";
  form.password = "";
  form.is_active = true;
  form.is_superuser = false;
}

async function refresh() {
  loading.value = true;
  try {
    users.value = await listUsers();
  } finally {
    loading.value = false;
  }
}

async function refreshRoles() {
  roles.value = await listRoles();
}

function openCreate() {
  resetForm();
  isEditing.value = false;
  editingId.value = null;
  userDialogVisible.value = true;
}

function openEdit(user: User) {
  isEditing.value = true;
  editingId.value = user.id;
  form.username = user.username;
  form.full_name = user.full_name ?? "";
  form.email = user.email ?? "";
  form.password = "";
  form.is_active = user.is_active;
  form.is_superuser = user.is_superuser;
  userDialogVisible.value = true;
}

async function submitUser() {
  try {
    if (isEditing.value && editingId.value) {
      await updateUser(editingId.value, {
        username: form.username,
        full_name: form.full_name,
        email: form.email,
        password: form.password || undefined,
        is_active: form.is_active,
        is_superuser: form.is_superuser,
      });
      ElMessage.success(t("users.messages.updated"));
    } else {
      await createUser({
        username: form.username,
        full_name: form.full_name,
        email: form.email,
        password: form.password,
        is_active: form.is_active,
        is_superuser: form.is_superuser,
      });
      ElMessage.success(t("users.messages.created"));
    }
    userDialogVisible.value = false;
    await refresh();
  } catch (error) {
    ElMessage.error(t("users.messages.opFailed"));
  }
}

function openAssignRoles(user: User) {
  roleTargetId.value = user.id;
  roleForm.role_ids = user.roles?.map((role) => role.id) ?? [];
  roleDialogVisible.value = true;
}

async function submitRoles() {
  if (!roleTargetId.value) {
    return;
  }
  try {
    await assignUserRoles(roleTargetId.value, { role_ids: roleForm.role_ids });
    ElMessage.success(t("users.messages.rolesUpdated"));
    roleDialogVisible.value = false;
    await refresh();
  } catch (error) {
    ElMessage.error(t("users.messages.opFailed"));
  }
}

async function confirmDelete(user: User) {
  try {
    await ElMessageBox.confirm(
      t("users.messages.deleteConfirm", { name: user.username }),
      t("common.confirm"),
      { type: "warning" },
    );
  } catch {
    return;
  }
  await deleteUser(user.id);
  ElMessage.success(t("users.messages.deleted"));
  await refresh();
}

onMounted(async () => {
  await Promise.all([refresh(), refreshRoles()]);
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

.tag {
  margin-right: 6px;
}

.muted {
  color: #9aa3b2;
}
</style>
