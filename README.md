# SAE S5.01 — Les Panthères Véloces

Application web de recommandation de véhicules (données ADEME Car Labelling) :
API Flask + PostgreSQL, interface Vue.js.

## Dépôt GitHub

[https://github.com/Rehzn93/SAE-S5.01](https://github.com/Rehzn93/SAE-S5.01)

## Équipe

| Membre | GitHub | Rôle |
|---|---|---|
| Rehan MOHAMMAD | [@Rehzn93](https://github.com/Rehzn93) | Backend / Data / Algorithmes / Docker |
| Clarence EDOH-DAGNON | [@Clarinos](https://github.com/Clarinos) | Backend / Base de données / Docker |
| Zoubida BENHABIB | [@zbd6](https://github.com/zbd6) | Backend / Data / Algorithmes |
| Mohammed BEQQAL AZIRAR | [@Meyruem](https://github.com/Meyruem) | Frontend |
| Adem BEN MAAMAR | [@Ademb29](https://github.com/Ademb29) | Frontend |


## Lancer le projet avec Docker (recommandé)

Prérequis : Docker Desktop ouvert.

```bash
docker compose up --build
```

La première fois, la construction prend quelques minutes. Ensuite :

| Service | Adresse |
|---|---|
| Site (Vue.js) | http://localhost:5173 |
| API (Flask) | http://localhost:8000/api/health |
| Documentation de l'API (Swagger) | http://localhost:8000/apidocs |
| Base PostgreSQL | localhost:5432 (user_sae / password_sae / vehicules_db) |

Au démarrage, l'API remplit la base avec `backend/app/static/data/vehicules.csv` si elle est vide.

Commandes utiles :

```bash
docker compose up --build -d   # en arrière-plan
docker compose logs -f back    # voir les logs de l'API
docker compose down            # tout arrêter
docker compose down -v         # tout arrêter ET vider la base (réimport au prochain lancement)
```

Après une modification du code, relancer `docker compose up --build`.

Si un port est déjà pris (`port is already allocated`), un autre programme utilise 5173, 8000 ou 5432 :
`docker ps` et `lsof -nP -iTCP:8000 -sTCP:LISTEN` permettent de le trouver.

## Lancer sans Docker (pour développer)

Prérequis : Python 3.11 ou plus récent, Node 18 ou plus récent.

```bash
docker compose up -d db          # seulement la base

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python prepa_db.py
python main.py                   # http://localhost:8000

cd ../frontend                   # dans un autre terminal
npm install
npm run dev                      # http://localhost:5173
```

## Tests

```bash
cd backend
pip install pytest
python -m pytest tests -v
```
