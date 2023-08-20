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
import HydroLoaderDownload from '@/components/DataSource/HydroLoaderDownload.vue'
import Profile from '@/components/account/Profile.vue'
import VerifyEmail from '@/components/account/VerifyEmail.vue'
import ActivateAccount from '@/components/account/ActivateAccount.vue'
import Metadata from '@/components/Datastream/Metadata.vue'
import PasswordResetRequest from '@/components/account/PasswordRecovery/PasswordResetRequest.vue'
import PasswordReset from '@/components/account/PasswordRecovery/PasswordReset.vue'
import { useAuthStore } from '@/store/authentication'
import { useThingStore } from '@/store/things'
import { RouteLocationNormalized } from 'vue-router'
import PageNotFound from '@/components/base/PageNotFound.vue'
import SiteVisualization from '@/components/SiteVisualization.vue'
import Contact from '@/components/Contact.vue'

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
    component: Browse,
    meta: { hideFooter: true, isFullScreen: true },
  },
  {
    path: '/sites',
    name: 'Sites',
    component: Sites,
    beforeEnter: requireVerifiedAuth,
  },
  { path: '/sites/:id', name: 'SingleSite', component: SingleSite },
  {
    path: '/visualization/:id/:datastreamId',
    name: 'SiteVisualization',
    component: SiteVisualization,
  },
  {
    path: '/sites/:id/datastreams/form/:datastreamId?',
    name: 'DatastreamForm',
    component: DatastreamForm,
    beforeEnter: requireThingOwnership,
  },
  {
    path: '/contact',
    name: 'Contact',
    component: Contact,
  },
  {
    path: '/data-sources',
    name: 'DataSources',
    component: DataSourceDashboard,
    beforeEnter: requireVerifiedAuth,
  },
  {
    path: '/data-sources/:id',
    name: 'DataSource',
    component: DataSourceDetail,
  },
  {
    path: '/data-loaders',
    name: 'DataLoaders',
    component: DataLoaderDashboard,
    beforeEnter: requireVerifiedAuth,
  },
  {
    path: '/hydroloader/download',
    name: 'HydroLoader',
    component: HydroLoaderDownload,
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
    path: '/password_reset/:uid/:token',
    name: 'PasswordReset',
    component: PasswordReset,
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    beforeEnter: requireAuth,
  },
  {
    path: '/verify-email',
    name: 'VerifyEmail',
    component: VerifyEmail,
    beforeEnter: requireUnverifiedAuth,
  },
  {
    path: '/activate/:uid/:token',
    name: 'ActivateAccount',
    component: ActivateAccount
  },
  {
    path: '/metadata',
    name: 'Metadata',
    component: Metadata,
    beforeEnter: requireVerifiedAuth,
  },
  {
    path: '/:catchAll(.*)*',
    name: 'PageNotFound',
    component: PageNotFound,
  },
]
