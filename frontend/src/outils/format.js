// les valeurs correspondent à celles attendues par score_pondere.py
export const ENERGIES = [
  { valeur: 'essence', libelle: 'Essence' },
  { valeur: 'diesel', libelle: 'Diesel' },
  { valeur: 'hybride', libelle: 'Hybride' },
  { valeur: 'hybride_rechargeable', libelle: 'Hybride rechargeable' },
  { valeur: 'electrique', libelle: 'Électrique' },
]

export const CARROSSERIES = [
  { valeur: 'berline', libelle: 'Berline' },
  { valeur: 'suv', libelle: 'SUV' },
  { valeur: 'break', libelle: 'Break' },
  { valeur: 'monospace', libelle: 'Monospace' },
  { valeur: 'ludospace', libelle: 'Ludospace' },
  { valeur: 'coupe', libelle: 'Coupé' },
  { valeur: 'cabriolet', libelle: 'Cabriolet' },
  { valeur: 'minibus', libelle: 'Minibus' },
]

export const TRAJETS = [
  { valeur: 'mixte', libelle: 'Mixte' },
  { valeur: 'ville', libelle: 'Ville' },
  { valeur: 'periurbain', libelle: 'Périurbain' },
  { valeur: 'route', libelle: 'Route' },
  { valeur: 'autoroute', libelle: 'Autoroute' },
]

// noms des sous-scores ("details")
export const SOUS_SCORES = {
  prix: 'Prix',
  consommation: 'Consommation',
  puissance: 'Puissance',
  co2: 'CO₂',
  marque: 'Marque préférée',
}

export function formatPrix(prix) {
  if (prix == null) return '–'
  return prix.toLocaleString('fr-FR') + ' €'
}

export function formatNombre(valeur, unite) {
  if (valeur == null) return '–'
  return valeur.toLocaleString('fr-FR', { maximumFractionDigits: 1 }) + ' ' + unite
}

// "hybride_essence" -> "Hybride essence"
export function majuscule(texte) {
  if (!texte) return '–'
  texte = texte.replaceAll('_', ' ').toLowerCase()
  return texte.charAt(0).toUpperCase() + texte.slice(1)
}
