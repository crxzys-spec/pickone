<template>
  <el-container class="layout">
    <el-aside :width="asideWidth" class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="logo">
        <div class="gov-brand" :class="{ collapsed: isCollapsed }">
          <img :src="logoUrl" alt="Logo" class="logo-image" />
          <div v-if="!isCollapsed" class="logo-text">
            <div class="logo-name">{{ t("admin.logo") }}</div>
            <div class="logo-subtitle">{{ t("admin.subtitle") }}</div>
          </div>
        </div>
      </div>
      <el-menu
        :default-active="activePath"
        router
        :collapse="isCollapsed"
        class="menu"
      >
        <el-menu-item v-if="canDraws" index="/admin/draws">
          <svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="12" r="7" fill="none" stroke="currentColor" stroke-width="1.6" />
            <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.6" />
            <path d="M12 3v3M12 18v3M3 12h3M18 12h3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
          </svg>
          <span class="menu-label">{{ t("admin.menu.draws") }}</span>
        </el-menu-item>
        <el-menu-item v-if="canRules" index="/admin/rules">
          <svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M7 4h7l4 4v12H7z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" />
            <path d="M14 4v4h4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" />
            <path d="M10 14h6M10 18h6M10 10h2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
          </svg>
          <span class="menu-label">{{ t("admin.menu.rules") }}</span>
        </el-menu-item>
        <el-sub-menu v-if="showResources" index="resources">
          <template #title>
            <svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true">
              <rect x="4" y="5" width="16" height="6" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.6" />
              <rect x="4" y="13" width="16" height="6" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.6" />
            </svg>
            <span class="menu-label">{{ t("admin.menu.resources") }}</span>
          </template>
          <el-menu-item v-if="canExperts" index="/admin/experts">
            <svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="12" cy="8" r="3.5" fill="none" stroke="currentColor" stroke-width="1.6" />
              <path d="M5 20c1.6-3.5 11.4-3.5 14 0" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            </svg>
            <span class="menu-label">{{ t("admin.menu.experts") }}</span>
          </el-menu-item>
          <el-menu-item v-if="canCategories" index="/admin/categories">
            <svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true">
              <rect x="4" y="4" width="7" height="7" rx="1.2" fill="none" stroke="currentColor" stroke-width="1.6" />
              <rect x="13" y="4" width="7" height="7" rx="1.2" fill="none" stroke="currentColor" stroke-width="1.6" />
              <rect x="4" y="13" width="7" height="7" rx="1.2" fill="none" stroke="currentColor" stroke-width="1.6" />
              <rect x="13" y="13" width="7" height="7" rx="1.2" fill="none" stroke="currentColor" stroke-width="1.6" />
            </svg>
            <span class="menu-label">{{ t("admin.menu.categories") }}</span>
          </el-menu-item>
          <el-menu-item v-if="canOrganizations" index="/admin/organizations">
            <svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true">
              <rect x="4" y="3" width="16" height="18" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.6" />
              <path d="M8 7h2M8 11h2M8 15h2M14 7h2M14 11h2M14 15h2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
              <path d="M10 21v-4h4v4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" />
            </svg>
            <span class="menu-label">{{ t("admin.menu.organizations") }}</span>
          </el-menu-item>
          <el-menu-item v-if="canRegions" index="/admin/regions">
            <svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="12" cy="10" r="4" fill="none" stroke="currentColor" stroke-width="1.6" />
              <path d="M12 3v3M12 17v4M5 10h3M16 10h3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            </svg>
            <span class="menu-label">{{ t("admin.menu.regions") }}</span>
          </el-menu-item>
          <el-menu-item v-if="canTitles" index="/admin/titles">
            <svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="12" cy="8" r="4" fill="none" stroke="currentColor" stroke-width="1.6" />
              <path d="M9 12l-2 8 5-3 5 3-2-8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" />
            </svg>
            <span class="menu-label">{{ t("admin.menu.titles") }}</span>
          </el-menu-item>
        </el-sub-menu>
        <el-sub-menu v-if="showSystem" index="system">
          <template #title>
            <svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M4 7h16M4 12h16M4 17h16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
              <circle cx="9" cy="7" r="1.6" fill="currentColor" />
              <circle cx="15" cy="12" r="1.6" fill="currentColor" />
              <circle cx="11" cy="17" r="1.6" fill="currentColor" />
            </svg>
            <span class="menu-label">{{ t("admin.menu.system") }}</span>
          </template>
          <el-menu-item v-if="canUsers" index="/admin/users">
            <svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="10" cy="8" r="3.2" fill="none" stroke="currentColor" stroke-width="1.6" />
              <path d="M3.8 20c1.4-3 8.8-3 10.2 0" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
              <circle cx="17.2" cy="9.5" r="2.4" fill="none" stroke="currentColor" stroke-width="1.6" />
              <path d="M15.2 20c0.6-1.3 2.9-2 4.8-2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            </svg>
            <span class="menu-label">{{ t("admin.menu.users") }}</span>
          </el-menu-item>
          <el-menu-item v-if="canRoles" index="/admin/roles">
            <svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 3l8 3v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" />
              <path d="M9 12l2 2 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <span class="menu-label">{{ t("admin.menu.roles") }}</span>
          </el-menu-item>
          <el-menu-item v-if="canPermissions" index="/admin/permissions">
            <svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="8" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.6" />
              <path d="M11 12h9l2 2-2 2-2-2H11" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" />
            </svg>
            <span class="menu-label">{{ t("admin.menu.permissions") }}</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
      <div class="sidebar-footer">
        <el-button
          class="collapse-icon-btn"
          circle
          size="small"
          :title="collapseTitle"
          :aria-label="collapseTitle"
          @click="toggleSidebar"
        >
          <svg v-if="isCollapsed" class="collapse-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <svg v-else class="collapse-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M15 6l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </el-button>
      </div>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="title">{{ headerTitle }}</div>
        <div class="header-actions">
          <el-select v-model="currentLocale" size="small" class="locale">
            <el-option :label="t('locale.zh')" value="zh" />
            <el-option :label="t('locale.en')" value="en" />
          </el-select>
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-dropdown">
              <span class="user-name">{{ displayName }}</span>
              <svg class="user-caret" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M7 9l5 5 5-5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  {{ t("common.profile") }}
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  {{ t("common.logout") }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="content">
        <router-view />
      </el-main>
    </el-container>

    <el-dialog
      v-model="profileVisible"
      :title="t('profile.title')"
      width="760px"
      destroy-on-close
    >
      <ProfilePanel />
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";

import ProfilePanel from "../../components/ProfilePanel.vue";
import { getMe } from "../../services/users";
import { useUserStore } from "../../stores/user";
import logoUrl from "../../assets/imgs/logo.png";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const { t, locale } = useI18n();
const activePath = computed(() => route.path);
const profileVisible = ref(false);
const isCollapsed = ref(localStorage.getItem("sidebar_collapsed") === "1");
const userName = ref("");
const asideWidth = computed(() => (isCollapsed.value ? "72px" : "220px"));
const collapseTitle = computed(() =>
  isCollapsed.value ? t("common.expand") : t("common.collapse"),
);
const displayName = computed(() => userName.value || t("common.user"));
const headerTitle = computed(() => {
  const metaTitle = route.meta?.title;
  if (typeof metaTitle === "string" && metaTitle) {
    return t(metaTitle);
  }
  return t("admin.title");
});
const updateDocumentTitle = () => {
  const title = t("admin.title");
  const subtitle = t("admin.subtitle");
  document.title = subtitle ? `${title} - ${subtitle}` : title;
};

const hasScope = (scope: string) =>
  userStore.scopes.includes("*") || userStore.scopes.includes(scope);

const canDraws = computed(
  () => hasScope("draw:read") || hasScope("draw:apply") || hasScope("draw:execute"),
);
const canExperts = computed(
  () => hasScope("expert:read") || hasScope("expert:write"),
);
const canRules = computed(
  () => hasScope("rule:read") || hasScope("rule:write"),
);
const canCategories = computed(
  () =>
    hasScope("category:read") || hasScope("category:write"),
);
const canOrganizations = computed(
  () => hasScope("organization:read") || hasScope("organization:write"),
);
const canRegions = computed(() => hasScope("region:read") || hasScope("region:write"));
const canTitles = computed(() => hasScope("title:read") || hasScope("title:write"));
const canUsers = computed(
  () => hasScope("user:read") || hasScope("user:write"),
);
const canRoles = computed(() => hasScope("role:write"));
const canPermissions = computed(() => hasScope("role:write"));

const showResources = computed(
  () =>
    canExperts.value ||
    canCategories.value ||
    canOrganizations.value ||
    canRegions.value ||
    canTitles.value,
);
const showSystem = computed(
  () => canUsers.value || canRoles.value || canPermissions.value,
);
const currentLocale = computed({
  get: () => locale.value,
  set: (value) => {
    locale.value = value;
    localStorage.setItem("locale", value);
  },
});

function logout() {
  userStore.clear();
  router.push("/login");
}

function goProfile() {
  profileVisible.value = true;
}

function handleUserCommand(command: string | number | object) {
  if (command === "profile") {
    goProfile();
    return;
  }
  if (command === "logout") {
    logout();
  }
}

function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value;
  localStorage.setItem("sidebar_collapsed", isCollapsed.value ? "1" : "0");
}

async function loadUserName() {
  try {
    const me = await getMe();
    userName.value = me.username;
  } catch {
    userName.value = "";
  }
}

onMounted(loadUserName);
watch(() => locale.value, updateDocumentTitle, { immediate: true });
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: var(--gov-surface);
}

.sidebar {
  background: linear-gradient(180deg, #143a63 0%, #102a47 100%);
  border-right: 1px solid #0f2743;
  color: #e8eff7;
  display: flex;
  flex-direction: column;
  --el-menu-bg-color: transparent;
  --el-menu-text-color: #e8eff7;
  --el-menu-hover-bg-color: rgba(255, 255, 255, 0.08);
  --el-menu-active-color: var(--gov-gold-500);
  --el-menu-active-bg-color: rgba(255, 255, 255, 0.12);
}

.logo {
  padding: 16px 14px 12px;
  color: #f8fbff;
}

.gov-brand {
  align-items: flex-start;
}

.gov-brand.collapsed {
  justify-content: center;
}

.logo-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 150px;
}

.logo-name {
  font-weight: 700;
  letter-spacing: 0.4px;
  font-size: 15px;
  line-height: 1.25;
  word-break: break-word;
  font-family: var(--gov-font-serif);
  color: #f8fbff;
}

.logo-subtitle {
  font-size: 12px;
  color: rgba(232, 239, 247, 0.72);
  letter-spacing: 0.3px;
  line-height: 1.2;
  word-break: break-word;
}

.menu {
  border-right: none;
  padding-top: 4px;
  flex: 1;
}

.menu :deep(.el-menu-item),
.menu :deep(.el-sub-menu__title) {
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 10px;
}

.menu :deep(.el-sub-menu__icon-arrow) {
  margin-left: auto;
}

.menu-icon {
  width: 18px;
  height: 18px;
  color: rgba(255, 255, 255, 0.88);
  flex: 0 0 auto;
}

.sidebar.collapsed .logo {
  display: flex;
  justify-content: center;
  padding: 14px 0 10px;
}

.sidebar.collapsed .menu {
  padding-left: 0;
  padding-right: 0;
}

.sidebar.collapsed .menu :deep(.el-menu-item),
.sidebar.collapsed .menu :deep(.el-sub-menu__title) {
  justify-content: center;
  padding: 0 !important;
}

.sidebar.collapsed .menu-label {
  display: none;
}

.sidebar.collapsed .menu :deep(.el-sub-menu__icon-arrow) {
  display: none;
}

.sidebar-footer {
  display: flex;
  justify-content: center;
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.collapse-icon-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #e8eff7;
}

.collapse-icon-btn:hover {
  background: rgba(255, 255, 255, 0.14);
  border-color: rgba(255, 255, 255, 0.28);
}

.collapse-icon {
  width: 18px;
  height: 18px;
}

.logo-image {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 6px;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(90deg, #ffffff 0%, #f3f6fb 60%, #ffffff 100%);
  border-bottom: 1px solid var(--gov-border);
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

.title {
  font-weight: 600;
  font-family: var(--gov-font-serif);
  color: #15365a;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.locale {
  min-width: 110px;
}

.user-dropdown {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid transparent;
  color: #15365a;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.user-dropdown:hover {
  background: #eef3f8;
  border-color: #d6dde8;
}

.user-name {
  font-weight: 600;
}

.user-caret {
  width: 16px;
  height: 16px;
  color: #6b7a90;
}

.content {
  padding: 24px;
}
</style>
