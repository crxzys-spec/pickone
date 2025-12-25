<template>
  <div class="page">
    <el-card class="card gov-panel gov-animate">
      <div class="header">
        <div class="gov-brand">
          <div class="gov-emblem"></div>
          <div>
            <h2 class="title">{{ t("login.title") }}</h2>
            <p class="subtitle">{{ t("login.subtitle") }}</p>
          </div>
        </div>
      </div>

      <el-form :model="form" @submit.prevent="onSubmit" label-width="90px">
        <el-form-item :label="t('login.username')">
          <el-input v-model="form.username" autocomplete="username" />
        </el-form-item>
        <el-form-item :label="t('login.password')">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            autocomplete="current-password"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            class="submit"
            @click="onSubmit"
          >
            {{ t("login.signIn") }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";

import { login } from "../services/auth";
import { useUserStore } from "../stores/user";

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const form = reactive({
  username: "",
  password: "",
});
const loading = ref(false);

async function onSubmit() {
  if (!form.username || !form.password) {
    ElMessage.warning(t("login.missing"));
    return;
  }
  loading.value = true;
  try {
    const result = await login(form.username, form.password);
    userStore.setAuth(result.access_token, result.scopes ?? []);
    const redirect = (route.query.redirect as string) || "/admin/draws";
    await router.push(redirect);
  } catch (error) {
    ElMessage.error(t("login.failed"));
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 20px;
}

.card {
  width: min(520px, 94vw);
  padding: 20px 18px 24px;
  background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
  border: 1px solid var(--gov-border);
  box-shadow: var(--gov-shadow);
}

.header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
  position: relative;
  padding-bottom: 12px;
  border-bottom: 1px solid #e1e7f0;
}

.title {
  margin: 0 0 6px;
  font-size: 22px;
  font-family: var(--gov-font-serif);
}

.subtitle {
  margin: 0 0 18px;
  color: var(--gov-muted);
}

.submit {
  width: 140px;
  height: 36px;
}
</style>
