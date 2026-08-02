import { createRouter, createWebHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('../pages/HomePage.vue') },
    { path: '/projects/new/purpose', component: () => import('../pages/PurposePage.vue') },
    { path: '/projects/new/copy', component: () => import('../pages/CopyPage.vue') },
    { path: '/projects/new/assets', component: () => import('../pages/AssetsPage.vue') },
    { path: '/projects/new/style', component: () => import('../pages/StylePage.vue') },
    { path: '/projects/:id/generate', component: () => import('../pages/GeneratePage.vue') },
    { path: '/projects/:id/result/:versionId', component: () => import('../pages/ResultPage.vue') },
    { path: '/projects/:id/annotate/:versionId', component: () => import('../pages/AnnotatePage.vue') },
    { path: '/projects/:id/compare/:beforeId/:afterId', component: () => import('../pages/ComparePage.vue') },
    { path: '/projects/:id/reframe/:versionId', component: () => import('../pages/ReframePage.vue') },
    { path: '/projects/:id/history', component: () => import('../pages/HistoryPage.vue') },
  ],
})
