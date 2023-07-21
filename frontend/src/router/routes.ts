import { RouteRecordRaw } from 'vue-router'

import Home from '@/components/Home.vue'
import Sites from '@/components/Site/Sites.vue'
import Signup from '@/components/account/Signup.vue'
import Login from '@/components/account/Login.vue'
import SingleSite from '@/components/Site/SingleSite.vue'
import Browse from '@/components/Browse.vue'
import DatastreamForm from '@/components/Datastream/DatastreamForm.vue'
import DataSourceForm from '@/components/DataSource/DataSourceForm.vue'
import DataSourceDashboard from '@/components/DataSource/DataSourceDashboard.vue'
import DataSourceDetail from '@/components/DataSource/DataSourceDetail.vue'
import DataLoaderDashboard from '@/components/DataSource/DataLoaderDashboard.vue'
import Profile from '@/components/account/Profile.vue'
import Metadata from '@/components/Datastream/Metadata.vue'
import PasswordResetRequest from '@/components/account/PasswordRecovery/PasswordResetRequest.vue'
import { useAuthStore } from '@/store/authentication'
import { useThingStore } from '@/store/things'
import { RouteLocationNormalized } from 'vue-router'
import PageNotFound from '@/components/base/PageNotFound.vue'

function requireAuth(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: (to?: string | object) => void
) {
  const authStore = useAuthStore()
  if (!authStore.isLoggedIn) next({ name: 'Login' })
  else next()
}

async function requireThingOwnership(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: (to?: string | object) => void
) {
  const authStore = useAuthStore()
  const thingStore = useThingStore()
  if (!authStore.isLoggedIn) {
    next({ name: 'Login' })
    return
  }

  if (typeof to.params.id !== 'string') {
    next({ name: 'PageNotFound' })
    return
  }

  await thingStore.fetchThingById(to.params.id)
  const thing = thingStore.things[to.params.id]
  if (thing && (thing.is_primary_owner || thing.owns_thing)) next()
  else next({ name: 'PageNotFound' })
}

export const routes: RouteRecordRaw[] = [
  { path: '/', name: 'Home', component: Home },
  {
    path: '/browse',
    name: 'Browse',
    component: Browse,
    meta: { hideFooter: true, isFullScreen: true },
  },
  {
    path: '/sites',
    name: 'Sites',
    component: Sites,
    beforeEnter: requireAuth,
  },
  { path: '/sites/:id', name: 'SingleSite', component: SingleSite },
  {
    path: '/sites/:id/datastreams/form/:datastreamId?',
    name: 'DatastreamForm',
    component: DatastreamForm,
    beforeEnter: requireThingOwnership,
  },
  {
    path: '/data-sources',
    name: 'DataSources',
    component: DataSourceDashboard,
  },
  {
    path: '/data-sources/:id',
    name: 'DataSource',
    component: DataSourceDetail
  },
  {
    path: '/data-loaders',
    name: 'DataLoaders',
    component: DataLoaderDashboard
  },
  {
    path: '/sites/:id/datastreams/:datastreamId/datasource',
    name: 'DataSourceForm',
    component: DataSourceForm,
    beforeEnter: requireThingOwnership,
  },
  { path: '/signup', name: 'Signup', component: Signup },
  { path: '/login', name: 'Login', component: Login },
  {
    path: '/password_reset',
    name: 'PasswordResetRequest',
    component: PasswordResetRequest,
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    beforeEnter: requireAuth,
  },
  {
    path: '/metadata',
    name: 'Metadata',
    component: Metadata,
    beforeEnter: requireAuth,
  },
  {
    path: '/:catchAll(.*)*',
    name: 'PageNotFound',
    component: PageNotFound,
  },
]
