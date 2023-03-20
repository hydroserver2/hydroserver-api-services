// src/router.js
import { createRouter, createWebHistory } from 'vue-router';
import Home from './components/Home.vue';
import Sites from './components/Sites.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/sites', component: Sites },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
