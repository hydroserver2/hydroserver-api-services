import { createApp } from 'vue'
import { store } from './store'
import App from './App.vue'
import router from './router/router'
import vuetify from '@/plugins/vuetify'

const app = createApp(App)
app.use(router)
app.use(store)
app.use(vuetify)
app.mount('#app')
