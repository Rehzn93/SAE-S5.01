import { createRouter, createWebHistory } from 'vue-router'
import AccueilView from '../views/AccueilView.vue'
import VoitureView from '../views/VoitureView.vue'
import RechercheView from '../views/RechercheView.vue'
import ResultatsView from '../views/ResultatsView.vue'

const routes = [
  { path: '/', component: AccueilView },
  { path: '/voiture', component: VoitureView },
  { path: '/criteres', component: RechercheView },
  { path: '/resultats', component: ResultatsView },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
