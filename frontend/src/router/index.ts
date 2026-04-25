import { createRouter, createWebHistory } from "vue-router";

import { lockAdminLocale, unlockAdminLocale } from "@/utils/localeAdmin";

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) return savedPosition;
    if (to.hash) {
      return { el: to.hash, behavior: "smooth", top: 96 };
    }
    return { top: 0 };
  },
  routes: [
    { path: "/", name: "home", component: () => import("@/views/HomePage.vue") },
    { path: "/me", name: "profile", component: () => import("@/views/ProfilePage.vue") },
    {
      path: "/explore/:packId",
      name: "pack-explore",
      component: () => import("@/views/PackStylesPage.vue"),
    },
    {
      path: "/generate/:styleId",
      name: "style-generate",
      component: () => import("@/views/StyleGeneratePage.vue"),
    },
    {
      path: "/choose-style",
      name: "choose-style",
      component: () => import("@/views/StyleSelectPage.vue"),
    },
    {
      path: "/quick",
      name: "quick",
      component: () => import("@/views/QuickSelectPage.vue"),
    },
    {
      path: "/loading/:taskId",
      name: "loading",
      component: () => import("@/views/LoadingPage.vue"),
      props: true,
    },
    {
      path: "/result/:taskId",
      name: "result",
      component: () => import("@/views/ResultPage.vue"),
      props: true,
    },
    {
      path: "/terms",
      name: "terms",
      component: () => import("@/views/TermsPage.vue"),
    },
    {
      path: "/privacy",
      name: "privacy",
      component: () => import("@/views/PrivacyPage.vue"),
    },
    {
      path: "/refund",
      name: "refund",
      component: () => import("@/views/RefundPage.vue"),
    },
    {
      path: "/packs",
      name: "packs",
      component: () => import("@/views/PacksPage.vue"),
    },
    {
      path: "/tools",
      name: "tools",
      component: () => import("@/views/ToolsPage.vue"),
    },
    {
      path: "/pricing",
      name: "pricing",
      component: () => import("@/views/PricingPage.vue"),
    },
    {
      path: "/admin",
      name: "admin",
      component: () => import("@/views/admin/AdminLayout.vue"),
      children: [
        {
          path: "",
          name: "admin-dash",
          component: () => import("@/views/admin/AdminDashboard.vue"),
        },
        {
          path: "users",
          name: "admin-users",
          component: () => import("@/views/admin/AdminUsersPage.vue"),
        },
        {
          path: "orders",
          name: "admin-orders",
          component: () => import("@/views/admin/AdminOrdersPage.vue"),
        },
        {
          path: "affiliates",
          name: "admin-affiliates",
          component: () => import("@/views/admin/AdminAffiliatesPage.vue"),
        },
        {
          path: "config",
          name: "admin-config",
          component: () => import("@/views/admin/AdminConfigPage.vue"),
        },
        {
          path: "logs",
          name: "admin-logs",
          component: () => import("@/views/admin/AdminLogsPage.vue"),
        },
      ],
    },
  ],
});

/** 管理后台仅中文：进入 /admin 强制 zh-CN，离开时恢复用户语言 */
router.beforeEach((to, from) => {
  const toAdmin = to.path.startsWith("/admin");
  const fromAdmin = from.path.startsWith("/admin");
  if (toAdmin && !fromAdmin) {
    lockAdminLocale();
  } else if (!toAdmin && fromAdmin) {
    unlockAdminLocale();
  }
});

export default router;
