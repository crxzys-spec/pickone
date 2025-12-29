<template>
  <div class="panel" v-loading="loading">
    <p class="subtitle">{{ t("profile.subtitle") }}</p>
    <el-descriptions v-if="user" :column="1" border>
      <el-descriptions-item :label="t('profile.labels.username')">
        {{ user.username }}
      </el-descriptions-item>
      <el-descriptions-item :label="t('profile.labels.fullName')">
        {{ user.full_name || "-" }}
      </el-descriptions-item>
      <el-descriptions-item :label="t('profile.labels.email')">
        {{ user.email || "-" }}
      </el-descriptions-item>
      <el-descriptions-item :label="t('profile.labels.active')">
        {{ user.is_active ? t("common.yes") : t("common.no") }}
      </el-descriptions-item>
      <el-descriptions-item :label="t('profile.labels.superuser')">
        {{ user.is_superuser ? t("common.yes") : t("common.no") }}
      </el-descriptions-item>
      <el-descriptions-item :label="t('profile.labels.roles')">
        <el-tag v-for="role in user.roles" :key="role.id" class="tag">
          {{ role.name }}
        </el-tag>
        <span v-if="!user.roles.length" class="muted">-</span>
      </el-descriptions-item>
    </el-descriptions>

    <el-divider />

    <div class="form-grid">
      <div>
        <h3 class="section-title">{{ t("profile.sections.info") }}</h3>
        <el-form :model="profileForm" label-width="100px" class="form">
          <el-form-item :label="t('profile.labels.username')">
            <el-input v-model="profileForm.username" disabled />
          </el-form-item>
          <el-form-item :label="t('profile.labels.fullName')">
            <el-input v-model="profileForm.full_name" />
          </el-form-item>
          <el-form-item :label="t('profile.labels.email')">
            <el-input v-model="profileForm.email" />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :loading="savingProfile"
              @click="saveProfile"
            >
              {{ t("common.save") }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      <div>
        <h3 class="section-title">{{ t("profile.sections.password") }}</h3>
        <el-form :model="passwordForm" label-width="110px" class="form">
          <el-form-item :label="t('profile.password.current')" required>
            <el-input
              v-model="passwordForm.current_password"
              type="password"
              show-password
            />
          </el-form-item>
          <el-form-item :label="t('profile.password.new')" required>
            <el-input
              v-model="passwordForm.new_password"
              type="password"
              show-password
            />
          </el-form-item>
          <el-form-item :label="t('profile.password.confirm')" required>
            <el-input
              v-model="passwordForm.confirm_password"
              type="password"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :loading="savingPassword"
              @click="submitPassword"
            >
              {{ t("profile.actions.changePassword") }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { useI18n } from "vue-i18n";

import { changePassword, getMe, updateMe } from "../services/users";
import type { User } from "../types/rbac";

const { t } = useI18n();

const user = ref<User | null>(null);
const loading = ref(false);
const savingProfile = ref(false);
const savingPassword = ref(false);

const profileForm = ref({
  username: "",
  full_name: "",
  email: "",
});

const passwordForm = ref({
  current_password: "",
  new_password: "",
  confirm_password: "",
});

async function fetchMe() {
  loading.value = true;
  try {
    const data = await getMe();
    user.value = data;
    profileForm.value = {
      username: data.username,
      full_name: data.full_name ?? "",
      email: data.email ?? "",
    };
  } catch (error) {
    ElMessage.error(t("profile.loadFailed"));
  } finally {
    loading.value = false;
  }
}

async function saveProfile() {
  savingProfile.value = true;
  try {
    const updated = await updateMe({
      full_name: profileForm.value.full_name || null,
      email: profileForm.value.email || null,
    });
    user.value = updated;
    profileForm.value = {
      username: updated.username,
      full_name: updated.full_name ?? "",
      email: updated.email ?? "",
    };
    ElMessage.success(t("profile.messages.updated"));
  } catch (error) {
    ElMessage.error(t("profile.messages.updateFailed"));
  } finally {
    savingProfile.value = false;
  }
}

async function submitPassword() {
  if (!passwordForm.value.current_password || !passwordForm.value.new_password) {
    ElMessage.warning(t("profile.messages.passwordRequired"));
    return;
  }
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    ElMessage.warning(t("profile.messages.passwordMismatch"));
    return;
  }
  savingPassword.value = true;
  try {
    await changePassword({
      current_password: passwordForm.value.current_password,
      new_password: passwordForm.value.new_password,
    });
    passwordForm.value = {
      current_password: "",
      new_password: "",
      confirm_password: "",
    };
    ElMessage.success(t("profile.messages.passwordUpdated"));
  } catch (error) {
    ElMessage.error(t("profile.messages.passwordFailed"));
  } finally {
    savingPassword.value = false;
  }
}

onMounted(fetchMe);
</script>

<style scoped>
.panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.subtitle {
  margin: 0;
  color: var(--gov-muted);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.form {
  margin-top: 12px;
}

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f3f63;
  font-family: var(--gov-font-serif);
}

.tag {
  margin-right: 6px;
  margin-bottom: 4px;
}

.muted {
  color: #9aa3b2;
}
</style>
