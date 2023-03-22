import { createRouter, createWebHistory } from 'vue-router';
import Home from './views/Home.vue';
import Sites from './views/Sites.vue';
import Signup from "./views/Signup.vue";
import Login from "./views/Login.vue";
import store from "./store.js";

const routes = [
  { path: '/',  name: 'Home', component: Home },
  { path: '/sites', name: 'Sites', component: Sites },
  { path: '/signup', component: Signup },
  { path: '/login', component: Login },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  await store.dispatch('loadTokens');
  next();
});

export default router;
