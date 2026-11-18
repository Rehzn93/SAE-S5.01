"""
Méthode de recommandation n°1 : filtrage + score pondéré (heuristique)

principe :
	1. FILTRER : on retire les véhicules qui ne respectent pas un critère obligatoire
	   (budget, motorisation, boîte, carrosserie, conso max, autonomie min, puissance min)
	2. NOTER : chaque véhicule restant reçoit des sous-scores entre 0 et 1
	   (prix, puissance, consommation, CO2, marque préférée)

l'utilisateur n'a pas de voiture en tête : il répond seulement au questionnaire.
(la recherche à partir d'une voiture de départ sera la méthode n°2, KNN)
	3. COMBINER : score final = somme pondérée des sous-scores / somme des poids -> entre 0 et 1
	4. TRIER : on garde les N meilleurs

complexité (n = nombre de véhicules, k = nombre de critères, constant ici) :
	- filtrage      : O(n)        (un passage par critère)
	- normalisation : O(n log n)  (calcul des percentiles = tri)
	- scores        : O(n)
	- tri final     : O(n log n)  -> total O(n log n)
"""
import os, time
import numpy as np
import pandas as pd

FICHIER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'static', 'data', 'vehicules.csv')

# choix de motorisation du formulaire : valeurs de la colonne "energie" du CSV nettoyé
MOTORISATIONS = {
	"essence": ["essence", "superethanol", "gpl"],
	"diesel": ["diesel"],
	"hybride": ["hybride_essence", "hybride_diesel"],
	"hybride_rechargeable": ["hybride_rechargeable_essence", "hybride_rechargeable_diesel"],
	"electrique": ["electrique"],
}

# type de trajet : colonne de consommation correspondante (cycle WLTP)
TRAJETS = {
	"ville": "conso_ville",
	"periurbain": "conso_periurbain",
	"route": "conso_route",
	"autoroute": "conso_autoroute",
	"mixte": "conso_mixte_max",
}

# poids de chaque sous-score dans la note finale
POIDS = {
	"prix": 3,
	"consommation": 2,
	"puissance": 1,
	"co2": 1,             # passe à 3 si l'utilisateur dit que l'écologie compte
	"marque": 1,          # utilisé seulement si des marques préférées sont données
}


def chargerVehicules(chemin=FICHIER):
	return pd.read_csv(chemin, sep=';', encoding='utf-8')


def normaliser(serie, inverse=False):
	"""
	ramène une colonne entre 0 et 1.
	on utilise les percentiles 5 et 95 au lieu du min et du max : sinon une seule valeur extrême
	(une Ferrari à 1,5 M€) écrase toutes les autres notes vers 0.
	inverse=True quand « plus petit = mieux » (prix, conso, CO2).
	les cases vides donnent une note neutre de 0,5.
	"""
	bas, haut = serie.quantile(0.05), serie.quantile(0.95)

	if pd.isna(bas) or haut == bas: # toutes les valeurs sont identiques (ou absentes) : le critère ne départage personne
		return pd.Series(0.5, index=serie.index)
	
	note = ((serie - bas) / (haut - bas)).clip(0, 1)
	
	if inverse:
		note = 1 - note
	return note.fillna(0.5)


def filtrer(df, c):
	"""étape 1 : on ne garde que les véhicules qui respectent les critères obligatoires"""
	if c.get("budget_max"):
		df = df[df["prix"] <= c["budget_max"]]

	if c.get("energies"):
		valeurs = [v for choix in c["energies"] for v in MOTORISATIONS.get(choix, [])]
		df = df[df["energie"].isin(valeurs)]

	if c.get("boite"):
		df = df[df["type_boite"] == c["boite"]]

	if c.get("carrosseries"):
		df = df[df["carrosserie"].isin(c["carrosseries"])]

	if c.get("puissance_min_ch"):
		df = df[df["puissance_ch"] >= c["puissance_min_ch"]]

	# conso max en L/100 km : ne concerne que les véhicules qui consomment du carburant.
	# une électrique (conso vide) n'est pas éliminée par ce critère
	if c.get("conso_max"):
		df = df[df["conso_mixte_max"].isna() | (df["conso_mixte_max"] <= c["conso_max"])]

	# conso max en kWh/100 km : ne concerne que les électriques
	if c.get("conso_elec_max"):
		df = df[df["conso_elec_max"].isna() | (df["conso_elec_max"] <= c["conso_elec_max"])]

	# autonomie min : ne concerne que les électriques et hybrides rechargeables.
	# on compare à autonomie_elec_min pour être sûr que toutes les versions la respectent
	if c.get("autonomie_min_km"):
		electrifie = df["famille_energie"].isin(["electrique", "hybride_rechargeable"])
		df = df[~electrifie | (df["autonomie_elec_min"] >= c["autonomie_min_km"])]

	return df

def scoreConsommation(df, trajet):
    """
    Calcule une note de consommation entre 0 et 1.
	Les électriques et les autres véhicules sont normalisés séparément 
	car leurs consommations utilisent des unités différentes.
	Moins un véhicule consomme, meilleure est sa note.
    """
    colonne = TRAJETS.get(trajet, "conso_mixte_max")

    scores = pd.Series(0.5, index=df.index)

    thermique = df["famille_energie"] != "electrique"
    electrique = df["famille_energie"] == "electrique"

    scores[thermique] = normaliser(
        df[colonne][thermique], inverse=True
    )

    scores[electrique] = normaliser(
        df["conso_elec_max"][electrique], inverse=True
    )

    return scores


def noter(df, c):
	"""étape 2 : calcul des sous-scores, chacun entre 0 et 1"""
	scores = pd.DataFrame(index=df.index)
	poids = dict(POIDS)

	scores["prix"] = normaliser(df["prix"], inverse=True)
	scores["consommation"] = scoreConsommation(df, c.get("trajet"))
	scores["puissance"] = normaliser(df["puissance_ch"])
	scores["co2"] = normaliser(df["co2_mixte_max"], inverse=True)
	if c.get("priorite_ecologie"):
		poids["co2"] = 3

	if c.get("marques"):
		scores["marque"] = df["marque"].isin(c["marques"]).astype(float)
	else:
		del poids["marque"]

	# étape 3 : moyenne pondérée -> toujours entre 0 et 1
	total = sum(poids.values())
	scores["score"] = sum(scores[nom] * p for nom, p in poids.items()) / total
	return scores, poids


def versJson(ligne):
	"""une ligne du DataFrame -> le JSON imbriqué attendu par le front"""
	def val(colonne):
		v = ligne[colonne]
		if pd.isna(v):
			return None
		return v.item() if isinstance(v, np.generic) else v

	return {
		"id": val("id"),
		"identification": {k: val(k) for k in ["marque", "libelle_modele", "description_commerciale", "gamme", "carrosserie"]},
		"motorisation": {k: val(k) for k in ["energie", "famille_energie", "cylindree", "puissance_ch", "puissance_elec_ch",
											 "puissance_fiscale", "type_boite", "nb_rapports"]},
		"poids": {k: val(k) for k in ["poids_a_vide", "masse_ordre_marche"]},
		"performances_electriques": {k: val(k) for k in ["autonomie_elec_min", "autonomie_elec_max", "autonomie_elec_urbain",
														 "conso_elec_min", "conso_elec_max"]},
		"conso_emissions": {k: val(k) for k in ["conso_mixte_min", "conso_mixte_max", "conso_ville", "conso_route",
												"co2_mixte_min", "co2_mixte_max"]},
		"prix_fiscalite": {k: val(k) for k in ["prix", "prix_min", "prix_max", "statut_ecologique", "bareme_bonus_malus"]},
	}


def recommander(df, criteres):
	"""
	point d'entrée appelé par la route POST /api/recommandations.
	retourne les N meilleurs véhicules avec leur score, le détail des sous-scores
	(pour expliquer « pourquoi cette voiture » dans le dashboard) et le temps de calcul.
	"""
	debut = time.perf_counter()

	candidats = filtrer(df, criteres)

	resultats = []
	if not candidats.empty:
		scores, poids = noter(candidats, criteres)
		# étape 4 : tri décroissant puis on garde les N premiers.
		# certaines voitures existent en plusieurs versions quasi identiques (ex : 3 Twingo
		# électriques au poids différent) : on n'en garde qu'une pour varier les propositions
		classement = scores.sort_values("score", ascending=False)
		cles = candidats.loc[classement.index, ["marque", "description_commerciale", "energie"]]
		classement = classement[~cles.duplicated().values]
		meilleurs = classement.head(criteres.get("nb_resultats", 5))
		for index, ligne in meilleurs.iterrows():
			resultats.append({
				"score": round(float(ligne["score"]), 3),
				"details": {nom: round(float(ligne[nom]), 3) for nom in poids},
				"vehicule": versJson(candidats.loc[index]),
			})

	return {
		"methode": "score_pondere",
		"temps_ms": round((time.perf_counter() - debut) * 1000, 2),
		"nb_candidats": len(candidats),
		"resultats": resultats,
	}

