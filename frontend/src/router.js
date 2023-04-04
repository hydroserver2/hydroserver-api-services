import { createRouter, createWebHistory } from 'vue-router';
import Home from './views/Home.vue';
import Sites from './views/Sites.vue';
import Signup from "./components/Signup.vue";
import Login from "./components/Login.vue";
import Site from "./views/Site.vue";
import Browse from "./views/Browse.vue";

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/browse', name: 'Browse', component: Browse},
  { path: '/sites', name: 'Sites', component: Sites },
  { path: '/sites/:id', name: 'Site', component: Site },
  { path: '/signup', name: 'Signup', component: Signup },
  { path: '/login', name: 'Login', component: Login },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;