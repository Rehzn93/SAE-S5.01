<script setup>
import { formatPrix, formatNombre, majuscule, SOUS_SCORES } from '../outils/format.js'

const props = defineProps({
  resultat: Object,
})

const v = props.resultat.vehicule
const pourcentage = Math.round(props.resultat.score * 100)

function consommation() {
  if (v.conso != null) return formatNombre(v.conso, 'L/100 km')
  return formatNombre(v.consoElec, 'kWh/100 km')
}

function couleurStatut() {
  if (v.statut === 'bonus') return 'text-bg-success'
  if (v.statut === 'malus') return 'text-bg-danger'
  return 'text-bg-secondary'
}
</script>

<template>
  <div class="card shadow-sm mb-3">
    <div class="card-body">
      <div class="d-flex justify-content-between gap-2">
        <div>
          <strong>{{ v.marque }} {{ v.modele }}</strong>
          <div class="text-muted small">{{ v.description }}</div>
        </div>
        <div class="fs-5 fw-bold text-nowrap">{{ formatPrix(v.prix) }}</div>
      </div>

      <div class="my-2">
        <span class="badge text-bg-light border me-1">{{ majuscule(v.energie) }}</span>
        <span class="badge text-bg-light border me-1">{{ majuscule(v.carrosserie) }}</span>
        <span class="badge text-bg-light border me-1">{{ majuscule(v.boite) }}</span>
        <span v-if="v.statut" class="badge" :class="couleurStatut()">{{ majuscule(v.statut) }}</span>
      </div>

      <div class="row small text-center mb-2">
        <div class="col-6 col-md-3"><div class="text-muted">Puissance</div>{{ formatNombre(v.puissance, 'ch') }}</div>
        <div class="col-6 col-md-3"><div class="text-muted">Consommation</div>{{ consommation() }}</div>
        <div class="col-6 col-md-3"><div class="text-muted">CO₂</div>{{ formatNombre(v.co2, 'g/km') }}</div>
        <div class="col-6 col-md-3"><div class="text-muted">Autonomie élec.</div>{{ formatNombre(v.autonomie, 'km') }}</div>
      </div>

      <div class="d-flex justify-content-between small">
        <span>Correspondance avec tes critères</span><strong>{{ pourcentage }} %</strong>
      </div>
      <div class="barre"><div :style="{ width: pourcentage + '%' }"></div></div>

      <details v-if="resultat.details" class="mt-2 small">
        <summary class="text-vert">Pourquoi cette voiture ?</summary>
        <div v-for="(note, nom) in resultat.details" :key="nom" class="d-flex align-items-center gap-2 mt-1">
          <span style="width: 120px">{{ SOUS_SCORES[nom] }}</span>
          <div class="barre flex-grow-1"><div :style="{ width: note * 100 + '%' }"></div></div>
          <span style="width: 40px" class="text-end">{{ Math.round(note * 100) }}</span>
        </div>
      </details>
    </div>
  </div>
</template>
