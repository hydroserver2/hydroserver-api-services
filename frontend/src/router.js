// src/router.js
import { createRouter, createWebHistory } from 'vue-router';
import Home from './views/Home.vue';
import Sites from './views/Sites.vue';
import Signup from "./views/Signup.vue";

const routes = [
  { path: '/', component: Home },
  { path: '/sites', component: Sites },
  { path: '/signup', component: Signup },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
