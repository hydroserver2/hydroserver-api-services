import { RouteRecordRaw } from 'vue-router'

import Home from '@/components/Home.vue'
import Sites from '@/components/Site/Sites.vue'
import Signup from '@/components/account/Signup.vue'
import Login from '@/components/account/Login.vue'
import SingleSite from '@/components/Site/SingleSite.vue'
import Browse from '@/components/Browse.vue'
import SiteDatastreams from '@/components/Datastream/Datastreams.vue'
import DatastreamForm from '@/components/Datastream/DatastreamForm.vue'
import Profile from '@/components/account/Profile.vue'
import Metadata from '@/components/Datastream/Metadata.vue'

export const routes: RouteRecordRaw[] = [
  { path: '/', name: 'Home', component: Home },
  { path: '/browse', name: 'Browse', component: Browse },
  { path: '/sites', name: 'Sites', component: Sites },
  { path: '/sites/:id', name: 'SingleSite', component: SingleSite },
  {
    path: '/sites/:id/datastreams',
    name: 'SiteDatastreams',
    component: SiteDatastreams,
  },
  {
    path: '/sites/:id/datastreams/form/:datastreamId?',
    name: 'DatastreamForm',
    component: DatastreamForm,
  },
  { path: '/signup', name: 'Signup', component: Signup },
  { path: '/login', name: 'Login', component: Login },
  { path: '/profile', name: 'Profile', component: Profile },
  { path: '/metadata', name: 'Metadata', component: Metadata },
  {
    path: '/:catchAll(.*)',
    redirect: '/',
    // TODO: implement NotFound component
    // name: "NotFound",
    //   component: PageNotFound,
    //   meta: {
    //     requiresAuth: false
    //   }
    // }
  },
]
