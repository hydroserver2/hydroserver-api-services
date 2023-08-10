import '@/assets/css/global.scss'

import { createApp } from 'vue'
import store from './store'
import App from './App.vue'
import router from './router/router'
import vuetify from '@/plugins/vuetify'
import interceptor from '@/plugins/axios.config'

// ==== Font Awesome Icons setuo =====

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

/* add icons to the library */
import { faOrcid } from '@fortawesome/free-brands-svg-icons'
library.add(faOrcid)

// ===================================

const app = createApp(App)

app.use(router)
app.use(interceptor)
store.use(({ store }) => {
  store.$http = app.config.globalProperties.$http
})
app.use(store)
app.use(vuetify)
app.component('font-awesome-icon', FontAwesomeIcon).mount('#app')

export default app
