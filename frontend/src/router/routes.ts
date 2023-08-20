import { RouteRecordRaw } from 'vue-router'
import Home from '@/components/Home.vue'
import { useAuthStore } from '@/store/authentication'
import { useThingStore } from '@/store/things'
import { RouteLocationNormalized } from 'vue-router'

function requireAuth(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: (to?: string | object) => void
) {
  const authStore = useAuthStore()
  if (!authStore.isLoggedIn) next({ name: 'Login' })
  else next()
}

function requireVerifiedAuth(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: (to?: string | object) => void
) {
  const authStore = useAuthStore()
  if (!authStore.isLoggedIn) next({ name: 'Login' })
  else if (!authStore.isVerified) next({ name: 'VerifyEmail'})
  else next()
}

function requireUnverifiedAuth(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: (to?: string | object) => void
) {
  const authStore = useAuthStore()
  if (!authStore.isLoggedIn) next({ name: 'Login' })
  else if (authStore.isVerified) next({ name: 'Sites'})
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

  if (!authStore.isVerified) {
    next({ name: 'VerifyEmail'})
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
    component: () => import('@/components/Browse.vue'),
    meta: { hideFooter: true, isFullScreen: true },
  },
  {
    path: '/sites',
    name: 'Sites',
    component: () => import('@/components/Site/Sites.vue'),
    beforeEnter: requireVerifiedAuth,
  },
  {
    path: '/sites/:id',
    name: 'SingleSite',
    component: () => import('@/components/Site/SingleSite.vue'),
  },
  {
    path: '/visualization/:id/:datastreamId',
    name: 'SiteVisualization',
    component: () => import('@/components/SiteVisualization.vue'),
  },
  {
    path: '/sites/:id/datastreams/form/:datastreamId?',
    name: 'DatastreamForm',
    component: () => import('@/components/Datastream/DatastreamForm.vue'),
    beforeEnter: requireThingOwnership,
  },
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('@/components/Contact.vue'),
  },
  {
    path: '/data-sources',
    name: 'DataSources',
    component: () => import('@/components/DataSource/DataSourceDashboard.vue'),
    beforeEnter: requireVerifiedAuth,
  },
  {
    path: '/data-sources/:id',
    name: 'DataSource',
    component: () => import('@/components/DataSource/DataSourceDetail.vue'),
  },
  {
    path: '/data-loaders',
    name: 'DataLoaders',
    component: () => import('@/components/DataSource/DataLoaderDashboard.vue'),
    beforeEnter: requireVerifiedAuth,
  },
  {
    path: '/hydroloader/download',
    name: 'HydroLoader',
    component: () => import('@/components/DataSource/HydroLoaderDownload.vue'),
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
    path: '/password_reset',
    name: 'PasswordResetRequest',
    component: () =>
      import('@/components/account/PasswordRecovery/PasswordResetRequest.vue'),
  },
  {
    path: '/password_reset/:uid/:token',
    name: 'PasswordReset',
    component: () =>
      import('@/components/account/PasswordRecovery/PasswordReset.vue'),
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/components/account/Profile.vue'),
    beforeEnter: requireAuth,
  },
  {
    path: '/verify-email',
    name: 'VerifyEmail',
    component: () => import('@/components/account/VerifyEmail.vue'),
    beforeEnter: requireUnverifiedAuth,
  },
  {
    path: '/activate/:uid/:token',
    name: 'ActivateAccount',
    component: () => import('@/components/account/ActivateAccount.vue'),
  },
  {
    path: '/metadata',
    name: 'Metadata',
    component: () => import('@/components/Datastream/Metadata.vue'),
    beforeEnter: requireVerifiedAuth,
  },
  {
    path: '/:catchAll(.*)*',
    name: 'PageNotFound',
    component: () => import('@/components/base/PageNotFound.vue'),
  },
]
