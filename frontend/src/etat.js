import { reactive } from 'vue'

// partagé entre la page des filtres et la page des résultats
export const etat = reactive({
  approches: [],
})
