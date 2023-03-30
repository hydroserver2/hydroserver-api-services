import { createRouter, createWebHistory } from 'vue-router';
import Home from './views/Home.vue';
import Sites from './views/Sites.vue';
import Signup from "./views/Signup.vue";
import Login from "./views/Login.vue";
import Site from "./views/Site.vue";

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/sites', name: 'Sites', component: Sites },
  { path: '/signup', name: 'Signup', component: Signup },
  { path: '/login', name: 'Login', component: Login },
  { path: '/site/:id', name: 'Site', component: Site },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;