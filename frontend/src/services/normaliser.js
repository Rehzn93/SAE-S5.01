// transforme la réponse de POST /api/recommandations pour l'affichage

const METHODES = {
  score_pondere: { nom: 'Score pondéré (heuristique)', complexite: 'O(n log n)' },
}

function aplatirVehicule(v) {
  const elec = v.performances_electriques || {}
  return {
    id: v.id,
    marque: v.identification.marque,
    modele: v.identification.libelle_modele,
    description: v.identification.description_commerciale,
    carrosserie: v.identification.carrosserie,
    energie: v.motorisation.energie,
    puissance: v.motorisation.puissance_ch,
    boite: v.motorisation.type_boite,
    prix: v.prix_fiscalite.prix,
    statut: v.prix_fiscalite.statut_ecologique,
    conso: v.conso_emissions.conso_mixte_max,
    consoElec: elec.conso_elec_max,
    co2: v.conso_emissions.co2_mixte_max,
    autonomie: elec.autonomie_elec_max,
  }
}

// une liste d'approches : une seule pour l'instant, la 2e (KNN) viendra s'ajouter
export function normaliserReponse(json) {
  const methode = METHODES[json.methode] || { nom: json.methode, complexite: '?' }
  return [
    {
      nom: methode.nom,
      complexite: methode.complexite,
      temps: json.temps_ms,
      nbEvalues: json.nb_candidats,
      resultats: json.resultats.map((r) => ({
        score: r.score,
        details: r.details,
        vehicule: aplatirVehicule(r.vehicule),
      })),
    },
  ]
}
