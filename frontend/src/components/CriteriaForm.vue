<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { getMarques } from '../services/api.js'
import { ENERGIES, CARROSSERIES, TRAJETS } from '../outils/format.js'

const emit = defineEmits(['rechercher'])

const BUDGET_MAX = 150000 // curseur au max = pas de limite

const form = reactive({
  budget_max: 40000,
  puissance_min_ch: 0,
  energies: [],
  carrosseries: [],
  boite: '',
  trajet: 'mixte',
  conso_max: null,
  conso_elec_max: null,
  autonomie_min_km: null,
  marques: [],
  priorite_ecologie: false,
  nb_resultats: 5,
})

const marques = ref([])

onMounted(async () => {
  try {
    marques.value = await getMarques()
  } catch (e) {
    marques.value = []
  }
})

// questions affichées selon la motorisation (aucune cochée = toutes)
const afficherConsoCarburant = computed(() => {
  if (form.energies.length === 0) return true
  return form.energies.some((e) => e !== 'electrique')
})

const afficherConsoElec = computed(() => {
  return form.energies.length === 0 || form.energies.includes('electrique')
})

const afficherAutonomie = computed(() => {
  return form.energies.includes('electrique') || form.energies.includes('hybride_rechargeable')
})

// on envoie seulement les filtres remplis et affichés
function envoyer() {
  const criteres = { nb_resultats: form.nb_resultats, trajet: form.trajet }

  if (form.budget_max < BUDGET_MAX) criteres.budget_max = form.budget_max
  if (form.puissance_min_ch > 0) criteres.puissance_min_ch = form.puissance_min_ch
  if (form.energies.length > 0) criteres.energies = form.energies
  if (form.carrosseries.length > 0) criteres.carrosseries = form.carrosseries
  if (form.boite) criteres.boite = form.boite
  if (afficherConsoCarburant.value && form.conso_max) criteres.conso_max = form.conso_max
  if (afficherConsoElec.value && form.conso_elec_max) criteres.conso_elec_max = form.conso_elec_max
  if (afficherAutonomie.value && form.autonomie_min_km) criteres.autonomie_min_km = form.autonomie_min_km
  if (form.marques.length > 0) criteres.marques = form.marques
  if (form.priorite_ecologie) criteres.priorite_ecologie = true

  emit('rechercher', criteres)
}
</script>

<template>
  <form class="row g-4" @submit.prevent="envoyer">
    <div class="col-md-6">
      <label class="form-label fw-semibold" for="budget">Quel est ton budget maximum ?</label>
      <input id="budget" v-model.number="form.budget_max" type="range" class="form-range" min="10000" :max="BUDGET_MAX" step="2500" />
      <div class="text-vert fw-semibold">
        <span v-if="form.budget_max >= BUDGET_MAX">Sans limite</span>
        <span v-else>{{ form.budget_max.toLocaleString('fr-FR') }} €</span>
      </div>
    </div>

    <div class="col-md-6">
      <label class="form-label fw-semibold" for="puissance">Quelle puissance minimale recherches-tu ?</label>
      <input id="puissance" v-model.number="form.puissance_min_ch" type="range" class="form-range" min="0" max="400" step="10" />
      <div class="text-vert fw-semibold">
        <span v-if="form.puissance_min_ch === 0">Peu importe</span>
        <span v-else>{{ form.puissance_min_ch }} ch minimum</span>
      </div>
    </div>

    <div class="col-12">
      <label class="form-label fw-semibold">Quelle motorisation préfères-tu ?</label>
      <div class="pastilles">
        <template v-for="e in ENERGIES" :key="e.valeur">
          <input :id="'energie-' + e.valeur" v-model="form.energies" type="checkbox" class="btn-check" :value="e.valeur" />
          <label class="btn btn-sm btn-outline-secondary" :for="'energie-' + e.valeur">{{ e.libelle }}</label>
        </template>
      </div>
      <div class="form-text">Aucune sélection = toutes les motorisations.</div>
    </div>

    <div class="col-12">
      <label class="form-label fw-semibold">Quel type de voiture recherches-tu ?</label>
      <div class="pastilles">
        <template v-for="c in CARROSSERIES" :key="c.valeur">
          <input :id="'carrosserie-' + c.valeur" v-model="form.carrosseries" type="checkbox" class="btn-check" :value="c.valeur" />
          <label class="btn btn-sm btn-outline-secondary" :for="'carrosserie-' + c.valeur">{{ c.libelle }}</label>
        </template>
      </div>
    </div>

    <div class="col-md-6">
      <label class="form-label fw-semibold" for="boite">Préfères-tu une boîte manuelle ou automatique ?</label>
      <select id="boite" v-model="form.boite" class="form-select">
        <option value="">Peu importe</option>
        <option value="manuelle">Manuelle</option>
        <option value="automatique">Automatique</option>
      </select>
    </div>

    <div v-if="afficherConsoCarburant" class="col-md-6">
      <label class="form-label fw-semibold" for="trajet">Quel est ton type de trajet principal ?</label>
      <select id="trajet" v-model="form.trajet" class="form-select">
        <option v-for="t in TRAJETS" :key="t.valeur" :value="t.valeur">{{ t.libelle }}</option>
      </select>
    </div>

    <div v-if="afficherConsoCarburant" class="col-md-4">
      <label class="form-label fw-semibold" for="conso">Consommation maximale</label>
      <div class="input-group">
        <input id="conso" v-model.number="form.conso_max" type="number" class="form-control" min="0" step="0.5" placeholder="Peu importe" />
        <span class="input-group-text">L/100 km</span>
      </div>
    </div>

    <div v-if="afficherConsoElec" class="col-md-4">
      <label class="form-label fw-semibold" for="conso-elec">Consommation électrique maximale</label>
      <div class="input-group">
        <input id="conso-elec" v-model.number="form.conso_elec_max" type="number" class="form-control" min="0" step="0.5" placeholder="Peu importe" />
        <span class="input-group-text">kWh/100 km</span>
      </div>
    </div>

    <div v-if="afficherAutonomie" class="col-md-4">
      <label class="form-label fw-semibold" for="autonomie">Autonomie électrique minimale</label>
      <div class="input-group">
        <input id="autonomie" v-model.number="form.autonomie_min_km" type="number" class="form-control" min="0" step="10" placeholder="Peu importe" />
        <span class="input-group-text">km</span>
      </div>
    </div>

    <div class="col-12">
      <label class="form-label fw-semibold">As-tu une ou plusieurs marques préférées ?</label>
      <div class="pastilles">
        <template v-for="m in marques" :key="m">
          <input :id="'marque-' + m" v-model="form.marques" type="checkbox" class="btn-check" :value="m" />
          <label class="btn btn-sm btn-outline-secondary" :for="'marque-' + m">{{ m }}</label>
        </template>
      </div>
    </div>

    <div class="col-md-6">
      <div class="form-check form-switch">
        <input id="ecologie" v-model="form.priorite_ecologie" class="form-check-input" type="checkbox" />
        <label class="form-check-label fw-semibold" for="ecologie">L'impact environnemental est important pour moi</label>
      </div>
    </div>

    <div class="col-md-6">
      <label class="form-label fw-semibold" for="nb">Nombre de propositions</label>
      <select id="nb" v-model.number="form.nb_resultats" class="form-select" style="max-width: 120px">
        <option :value="5">5</option>
        <option :value="10">10</option>
        <option :value="20">20</option>
      </select>
    </div>

    <div class="col-12">
      <button type="submit" class="btn btn-vert px-4">Trouver ma voiture</button>
    </div>
  </form>
</template>
