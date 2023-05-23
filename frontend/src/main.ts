import '@/assets/css/global.scss'

import { createApp } from 'vue'
import store from './store'
import App from './App.vue'
import router from './router/router'
import vuetify from '@/plugins/vuetify'
import interceptor from '@/plugins/axios.config'

const app = createApp(App)

app.use(router)
app.use(interceptor)
store.use(({ store }) => {
  store.$http = app.config.globalProperties.$http
})
app.use(store)
app.use(vuetify)
app.mount('#app')

export default app
