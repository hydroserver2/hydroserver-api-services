import { createRouter, createWebHistory } from 'vue-router';
import Home from './views/Home.vue';
import Sites from './views/Sites.vue';
import Signup from "./views/Signup.vue";
import Login from "./views/Login.vue";

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

export default router;
