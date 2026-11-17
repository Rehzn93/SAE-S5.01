# Frontend (Vue.js, HTML, CSS, Bootstrap)

## Lancer

```bash
cd frontend
npm install
npm run dev
```

Puis ouvrir http://localhost:5173

Le front appelle directement le backend Flask sur `http://localhost:8000` (CORS est activé dans `backend/app/__init__.py`).

## Routes utilisées

- `GET /api/vehicules` : catalogue des véhicules (sert à remplir la liste des marques)
- `POST /api/recommandations` : envoie les filtres, reçoit `{ methode, temps_ms, nb_candidats, resultats }`

Les appels sont dans `src/services/api.js`, la lecture du JSON dans `src/services/normaliser.js`.

## Docker

```bash
docker build -t sae-frontend .
docker run -p 5173:5173 sae-frontend
```
