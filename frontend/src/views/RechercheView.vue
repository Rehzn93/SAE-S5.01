<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import CriteriaForm from '../components/CriteriaForm.vue'
import { getRecommandations } from '../services/api.js'
import { etat } from '../etat.js'

const router = useRouter()
const erreur = ref('')

async function rechercher(criteres) {
  erreur.value = ''
  try {
    etat.approches = await getRecommandations(criteres)
    router.push('/resultats')
  } catch (e) {
    erreur.value = e.message
  }
}
</script>

<template>
  <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
    <h1 class="h3 fw-bold mb-0">Je décris mes besoins</h1>
    <RouterLink to="/" class="btn btn-outline-secondary btn-sm">← Changer de type de recherche</RouterLink>
  </div>

  <div v-if="erreur" class="alert alert-danger">{{ erreur }}</div>

  <div class="card shadow-sm">
    <div class="card-body p-4">
      <CriteriaForm @rechercher="rechercher" />
    </div>
  </div>
</template>
