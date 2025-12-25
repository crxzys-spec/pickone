import { createRouter, createWebHistory } from "vue-router";

import HomeView from "../views/Home.vue";
import LoginView from "../views/Login.vue";
import AdminLayout from "../views/admin/AdminLayout.vue";
import DrawsAdmin from "../views/admin/DrawsAdmin.vue";
import ExpertsAdmin from "../views/admin/ExpertsAdmin.vue";
import OrganizationsAdmin from "../views/admin/OrganizationsAdmin.vue";
import PermissionsAdmin from "../views/admin/PermissionsAdmin.vue";
import RolesAdmin from "../views/admin/RolesAdmin.vue";
import UsersAdmin from "../views/admin/UsersAdmin.vue";
import RulesAdmin from "../views/admin/RulesAdmin.vue";
import CategoriesAdmin from "../views/admin/CategoriesAdmin.vue";
import TitlesAdmin from "../views/admin/TitlesAdmin.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
  },
  {
    path: "/me",
    redirect: "/admin/draws",
    meta: { requiresAuth: true },
  },
  {
    path: "/admin",
    component: AdminLayout,
    redirect: "/admin/draws",
    meta: { requiresAuth: true },
    children: [
      {
        path: "users",
        name: "admin-users",
        component: UsersAdmin,
        meta: { title: "admin.menu.users" },
      },
      {
        path: "roles",
        name: "admin-roles",
        component: RolesAdmin,
        meta: { title: "admin.menu.roles" },
      },
      {
        path: "permissions",
        name: "admin-permissions",
        component: PermissionsAdmin,
        meta: { title: "admin.menu.permissions" },
      },
      {
        path: "experts",
        name: "admin-experts",
        component: ExpertsAdmin,
        meta: { title: "admin.menu.experts" },
      },
      {
        path: "organizations",
        name: "admin-organizations",
        component: OrganizationsAdmin,
        meta: { title: "admin.menu.organizations" },
      },
      {
        path: "titles",
        name: "admin-titles",
        component: TitlesAdmin,
        meta: { title: "admin.menu.titles" },
      },
      {
        path: "categories",
        name: "admin-categories",
        component: CategoriesAdmin,
        meta: { title: "admin.menu.categories" },
      },
      {
        path: "rules",
        name: "admin-rules",
        component: RulesAdmin,
        meta: { title: "admin.menu.rules" },
      },
      {
        path: "draws",
        name: "admin-draws",
        component: DrawsAdmin,
        meta: { title: "admin.menu.draws" },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      return {
        path: "/login",
        query: { redirect: to.fullPath },
      };
    }
  }
  return true;
});

export default router;
