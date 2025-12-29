import { createRouter, createWebHistory } from "vue-router";

const HomeView = () => import("../views/Home.vue");
const LoginView = () => import("../views/Login.vue");
const AdminLayout = () => import("../views/admin/AdminLayout.vue");
const DrawsAdmin = () => import("../views/admin/DrawsAdmin.vue");
const ExpertsAdmin = () => import("../views/admin/ExpertsAdmin.vue");
const OrganizationsAdmin = () => import("../views/admin/OrganizationsAdmin.vue");
const PermissionsAdmin = () => import("../views/admin/PermissionsAdmin.vue");
const RegionsAdmin = () => import("../views/admin/RegionsAdmin.vue");
const RolesAdmin = () => import("../views/admin/RolesAdmin.vue");
const UsersAdmin = () => import("../views/admin/UsersAdmin.vue");
const RulesAdmin = () => import("../views/admin/RulesAdmin.vue");
const CategoriesAdmin = () => import("../views/admin/CategoriesAdmin.vue");
const TitlesAdmin = () => import("../views/admin/TitlesAdmin.vue");

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
        path: "regions",
        name: "admin-regions",
        component: RegionsAdmin,
        meta: { title: "admin.menu.regions" },
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
