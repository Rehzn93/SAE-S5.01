import { normaliserReponse } from './normaliser.js'

// adresse du backend Flask (backend/main.py)
const API = 'http://localhost:8000/api'

// liste des marques sans doublons, à partir du catalogue des véhicules
export async function getMarques() {
  const reponse = await fetch(API + '/vehicules')
  if (!reponse.ok) {
    throw new Error('Impossible de charger les marques')
  }
  const json = await reponse.json()
  const marques = json.vehicules.map((v) => v.identification.marque)
  return [...new Set(marques)].sort()
}

export async function getRecommandations(criteres) {
  const reponse = await fetch(API + '/recommandations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(criteres),
  })
  if (!reponse.ok) {
    throw new Error('Le serveur a répondu ' + reponse.status)
  }
  const json = await reponse.json()
  return normaliserReponse(json)
}
