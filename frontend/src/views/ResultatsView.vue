<script setup>
import ResultCard from '../components/ResultCard.vue'
import { etat } from '../etat.js'
</script>

<template>
  <div v-if="etat.approches.length === 0" class="text-center py-5">
    <p class="text-muted">Aucune recherche pour l'instant.</p>
    <RouterLink to="/" class="btn btn-vert">Faire une recherche</RouterLink>
  </div>

  <div v-else>
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
      <h1 class="h3 fw-bold mb-0">Nos propositions</h1>
      <RouterLink to="/criteres" class="btn btn-outline-secondary btn-sm">← Modifier mes filtres</RouterLink>
    </div>

    <div class="row g-4">
      <div v-for="approche in etat.approches" :key="approche.nom" class="col-lg">
        <h2 class="h5 mb-0">{{ approche.nom }}</h2>
        <p class="small text-muted">
          calculé en {{ approche.temps }} ms · {{ approche.nbEvalues }} voitures évaluées · complexité {{ approche.complexite }}
        </p>

        <p v-if="approche.resultats.length === 0" class="text-muted">
          Aucune voiture ne correspond à ces filtres.
        </p>
        <ResultCard v-for="r in approche.resultats" :key="r.vehicule.id" :resultat="r" />
      </div>
    </div>
  </div>
</template>
