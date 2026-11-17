import { createRouter, createWebHistory } from 'vue-router'
import AccueilView from '../views/AccueilView.vue'
import VoitureView from '../views/VoitureView.vue'

const routes = [
  { path: '/', component: AccueilView },
  { path: '/voiture', component: VoitureView },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
