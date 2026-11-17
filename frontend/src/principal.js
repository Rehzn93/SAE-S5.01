import { createApp } from 'vue'
import 'bootstrap/dist/css/bootstrap.min.css'
import './ressources/style.css'
import App from './Application.vue'
import router from './router'

createApp(App).use(router).mount('#app')
