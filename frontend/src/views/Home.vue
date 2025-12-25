<template>
  <div class="page">
    <div class="hero gov-panel gov-animate">
      <div class="intro">
        <h1 class="title">{{ t("home.title") }}</h1>
        <p class="subtitle">{{ t("home.subtitle") }}</p>
        <div class="actions">
          <el-button type="primary" @click="goLogin">
            {{ t("home.login") }}
          </el-button>
          <el-button @click="goAdmin">{{ t("home.admin") }}</el-button>
        </div>
      </div>
      <div class="seal" aria-hidden="true">
        <div class="seal-ring"></div>
        <div class="seal-lines"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";

const router = useRouter();
const { t } = useI18n();

function goLogin() {
  router.push("/login");
}

function goAdmin() {
  router.push("/admin/draws");
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

.hero {
  width: min(880px, 94vw);
  padding: 36px 40px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 220px;
  gap: 32px;
  align-items: center;
}

.intro {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.title {
  margin: 0;
  font-size: clamp(26px, 3.2vw, 34px);
  font-family: var(--gov-font-serif);
}

.subtitle {
  margin: 0;
  color: var(--gov-muted);
  line-height: 1.6;
}

.actions {
  margin-top: 8px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.seal {
  position: relative;
  width: 200px;
  height: 200px;
  margin-left: auto;
}

.seal-ring {
  position: absolute;
  inset: 8px;
  border-radius: 50%;
  border: 2px dashed #c9b06c;
  box-shadow: inset 0 0 0 6px rgba(63, 134, 192, 0.08);
}

.seal-lines {
  position: absolute;
  inset: 32px;
  border-radius: 50%;
  background: repeating-linear-gradient(
    45deg,
    rgba(31, 79, 130, 0.08),
    rgba(31, 79, 130, 0.08) 6px,
    transparent 6px,
    transparent 12px
  );
}

@media (max-width: 860px) {
  .hero {
    grid-template-columns: 1fr;
    padding: 28px 24px;
  }

  .seal {
    margin: 0 auto;
    width: 160px;
    height: 160px;
  }
}
</style>
