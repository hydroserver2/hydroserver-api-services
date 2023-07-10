import { useAuthStore } from '@/store/authentication'
import { useThingStore } from '@/store/things'
import { RouteRecordRaw, RouteLocationNormalized } from 'vue-router'

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
  { path: '/', name: 'Home', component: () => import('@/components/Home.vue') },
  {
    path: '/browse',
    name: 'Browse',
    component: () => import('@/components/Browse.vue'),
    meta: { hideFooter: true, isFullScreen: true },
  },
  {
    path: '/sites',
    name: 'Sites',
    component: () => import('@/components/Site/Sites.vue'),
    beforeEnter: requireAuth,
  },
  {
    path: '/sites/:id',
    name: 'SingleSite',
    component: () => import('@/components/Site/SingleSite.vue'),
  },
  {
    path: '/sites/:id/datastreams/form/:datastreamId?',
    name: 'DatastreamForm',
    component: () => import('@/components/Datastream/DatastreamForm.vue'),
    beforeEnter: requireThingOwnership,
  },
  {
    path: '/data-sources',
    name: 'DataSources',
    component: () => import('@/components/DataSource/DataSourceDashboard.vue'),
  },
  {
    path: '/sites/:id/datastreams/:datastreamId/datasource',
    name: 'DataSourceForm',
    component: () => import('@/components/DataSource/DataSourceForm.vue'),
    beforeEnter: requireThingOwnership,
  },
  {
    path: '/signup',
    name: 'Signup',
    component: () => import('@/components/account/Signup.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/components/account/Login.vue'),
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/components/account/Profile.vue'),
    beforeEnter: requireAuth,
  },
  {
    path: '/metadata',
    name: 'Metadata',
    component: () => import('@/components/Datastream/Metadata.vue'),
    beforeEnter: requireAuth,
  },
  {
    path: '/:catchAll(.*)*',
    name: 'PageNotFound',
    component: () => import('@/components/base/PageNotFound.vue'),
  },
]
