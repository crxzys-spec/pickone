<template>
  <div class="page">
    <el-card class="card gov-panel gov-animate">
      <div class="header">
        <div class="login-brand">
          <div class="gov-emblem"></div>
          <div class="brand-text">
            <h2 class="title">{{ t("login.title") }}</h2>
            <p class="subtitle">{{ t("login.subtitle") }}</p>
          </div>
        </div>
      </div>

      <el-form :model="form" @submit.prevent="onSubmit" label-width="90px">
        <el-form-item :label="t('login.username')" required>
          <el-input v-model="form.username" autocomplete="username" />
        </el-form-item>
        <el-form-item :label="t('login.password')" required>
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
import { onMounted, reactive, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";

import { login } from "../services/auth";
import { useUserStore } from "../stores/user";

const { t, locale } = useI18n();
const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const form = reactive({
  username: "",
  password: "",
});
const loading = ref(false);
const updateDocumentTitle = () => {
  const title = t("login.title");
  const subtitle = t("login.subtitle");
  document.title = subtitle ? `${title} - ${subtitle}` : title;
};

onMounted(updateDocumentTitle);
watch(() => locale.value, updateDocumentTitle);

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
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
  position: relative;
  padding-bottom: 12px;
  border-bottom: 1px solid #e1e7f0;
}

.login-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 420px;
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title {
  margin: 0;
  font-size: 20px;
  font-family: var(--gov-font-serif);
  line-height: 1.25;
  word-break: break-word;
}

.subtitle {
  margin: 0;
  color: var(--gov-muted);
  font-size: 13px;
  line-height: 1.2;
  word-break: break-word;
}

.login-brand :deep(.gov-emblem) {
  width: 36px;
  height: 36px;
}

.submit {
  width: 140px;
  height: 36px;
}
</style>
