"""
nettoyage du jeu de données ADEME Car Labelling -> app/static/data/vehicules.csv

à lancer depuis backend/ :  python scripts/nettoyage_donnees.py
on peut aussi préciser les fichiers : python scripts/nettoyage_donnees.py entree.csv sortie.csv

étapes :
	1. lecture du CSV brut (séparateur ;, décimales avec virgule)
	2. suppression des lignes strictement identiques
	3. sélection des colonnes utiles et renommage en snake_case
	4. réparation des accents mal encodés (CoupÃ© -> Coupé)
	5. harmonisation des textes et des catégories (marques, énergie, carrosserie...)
	6. conversion des unités (kW -> ch, Wh/km -> kWh/100 km)
	7. complétion des valeurs manquantes quand elles ont un sens (CO2 d'une électrique = 0)
	8. correction des incohérences (min > max)
	9. rejet des lignes inutilisables ou hors cible -> rejets.csv avec la raison
	10. regroupement des finitions : même voiture, prix différents
	11. écriture du CSV propre + bilan
"""
import os, re, sys
import pandas as pd

DOSSIER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app', 'static', 'data')
FICHIER_BRUT = os.path.join(DOSSIER, 'ademe_brut.csv')
FICHIER_PROPRE = os.path.join(DOSSIER, 'vehicules.csv')
FICHIER_REJETS = os.path.join(DOSSIER, 'rejets.csv')

# regrouper les finitions d'une même voiture en une seule ligne (prix médian)
# sans ça, le top 10 d'une recommandation peut contenir 10 fois la même voiture
REGROUPER_FINITIONS = True

# au-delà de ce prix, le véhicule est écarté (supercars hors cible).
# sinon une Ferrari à 1,5 M€ écrase la normalisation min-max du prix : toutes les autres
# voitures auraient une note de prix presque identique. None = on garde tout
PRIX_MAX = None

# colonne ADEME -> colonne de notre base
# toutes les autres colonnes (essais HC/NOx, CO2 par vitesse, groupe...) sont abandonnées
COLONNES = {
	"Marque": "marque",
	"Libellé modèle": "libelle_modele",
	"Description Commerciale": "description_commerciale",
	"Gamme": "gamme",
	"Carrosserie": "carrosserie",
	"Energie": "energie",
	"Cylindrée": "cylindree",
	"Puissance maximale": "puissance_max_kw",
	"Puissance nominale électrique": "puissance_elec_kw",
	"Puissance fiscale": "puissance_fiscale",
	"Type de boite": "type_boite",
	"Nombre rapports": "nb_rapports",
	"Poids à vide": "poids_a_vide",
	"Masse OM Min": "masse_ordre_marche",
	"Autonomie elec Min": "autonomie_elec_min",
	"Autonomie elec Max": "autonomie_elec_max",
	"Autonomie elec urbain Max": "autonomie_elec_urbain",
	"Conso elec Min": "conso_elec_min",
	"Conso elec Max": "conso_elec_max",
	"Conso vitesse mixte Min": "conso_mixte_min",
	"Conso vitesse mixte Max": "conso_mixte_max",
	# consommation par type de trajet (cycle WLTP), utile pour la question « type de trajet »
	"Conso basse vitesse Max": "conso_ville",
	"Conso moyenne vitesse Max": "conso_periurbain",
	"Conso haute vitesse Max": "conso_route",
	"Conso T-haute vitesse Max": "conso_autoroute",
	"CO2 vitesse mixte Min": "co2_mixte_min",
	"CO2 vitesse mixte Max": "co2_mixte_max",
	"Prix véhicule": "prix",
	"Bonus-Malus": "statut_ecologique",
	"Barème Bonus-Malus": "bareme_bonus_malus",
}

# noms de marques tronqués ou écrits différemment dans le fichier ADEME
MARQUES = {
	"B.M.W.": "BMW",
	"M.G.": "MG",
	"LAMBORGHIN": "LAMBORGHINI",
	"ROLLS ROYC": "ROLLS-ROYCE",
	"ALFA ROMEO": "ALFA-ROMEO",
	"LAND ROVER": "LAND-ROVER",
}

# énergie ADEME -> (énergie détaillée, famille utilisée pour les filtres)
# HNR = hybride non rechargeable, HR = hybride rechargeable
ENERGIES = {
	"ESSENCE": ("essence", "thermique"),
	"GAZOLE": ("diesel", "thermique"),
	"SUPERETHANOL": ("superethanol", "thermique"),
	"ESS+G.P.L.": ("gpl", "thermique"),
	"ESS+ELEC HNR": ("hybride_essence", "hybride"),
	"GAZ+ELEC HNR": ("hybride_diesel", "hybride"),
	"ELEC+ESSENC HR": ("hybride_rechargeable_essence", "hybride_rechargeable"),
	"ELEC+GAZOLE HR": ("hybride_rechargeable_diesel", "hybride_rechargeable"),
	"ELECTRIC": ("electrique", "electrique"),
}

CARROSSERIES = {
	"BERLINE": "berline",
	"BREAK": "break",
	"COUPE": "coupe",
	"CABRIOLET": "cabriolet",
	"TS TERRAINS/CHEMINS": "suv",
	"COMBISPACE": "ludospace",
	"MINIBUS": "minibus",
	"MONOSPACE": "monospace",
	"MONOSPACE COMPACT": "monospace",
	"MINISPACE": "monospace",
}

# gamme -> (code, niveau de 1 à 6) : le niveau permet de calculer une distance en KNN
GAMMES = {
	"ECONOMIQUE": ("economique", 1),
	"INFERIEURE": ("inferieure", 2),
	"MOYENNE INFERIEURE": ("moyenne_inferieure", 3),
	"MOYENNE SUPERIEURE": ("moyenne_superieure", 4),
	"SUPERIEURE": ("superieure", 5),
	"LUXE": ("luxe", 6),
}

BOITES = {
	"MECANIQUE": "manuelle",
	"AUTOMATIQUE": "automatique",
	"VARIATION CONTINUE": "automatique",
	"VARIATION ELECTRIQUE": "automatique",
}

# colonnes qui vont par paire min / max
PAIRES_MIN_MAX = [
	("autonomie_elec_min", "autonomie_elec_max"),
	("conso_elec_min", "conso_elec_max"),
	("conso_mixte_min", "conso_mixte_max"),
	("co2_mixte_min", "co2_mixte_max"),
]

# 1 kW = 1,36 ch (cheval-vapeur DIN, celui des fiches techniques)
# à ne pas confondre avec les CV fiscaux de la carte grise (colonne puissance_fiscale)
KW_VERS_CH = 1.36

# ce qui définit "la même voiture" : deux lignes avec ces valeurs identiques sont des finitions
# (options, jantes, équipements) d'une seule voiture
CLES_VOITURE = ["marque", "libelle_modele", "description_commerciale", "energie", "famille_energie",
				"carrosserie", "gamme", "gamme_niveau", "type_boite", "puissance_ch", "puissance_estimee",
				"poids_a_vide"]

# colonnes sans lesquelles un véhicule ne peut pas être recommandé
INDISPENSABLES = ["marque", "libelle_modele", "energie", "carrosserie", "gamme", "type_boite",
				  "prix", "puissance_ch", "co2_mixte_max", "poids_a_vide"]

# ordre des colonnes dans le CSV final (même découpage que le JSON envoyé au front)
COLONNES_FINALES = [
	"id",
	"marque", "libelle_modele", "description_commerciale", "gamme", "gamme_niveau", "carrosserie",
	"energie", "famille_energie", "cylindree", "puissance_ch", "puissance_elec_ch", "puissance_estimee",
	"puissance_fiscale", "type_boite", "nb_rapports",
	"poids_a_vide", "masse_ordre_marche",
	"autonomie_elec_min", "autonomie_elec_max", "autonomie_elec_urbain", "conso_elec_min", "conso_elec_max",
	"conso_mixte_min", "conso_mixte_max", "conso_ville", "conso_periurbain", "conso_route", "conso_autoroute",
	"co2_mixte_min", "co2_mixte_max",
	"prix", "prix_min", "prix_max", "nb_finitions", "statut_ecologique", "bareme_bonus_malus",
]

COLONNES_ENTIERES = ["cylindree", "puissance_ch", "puissance_elec_ch", "puissance_fiscale", "nb_rapports",
					 "poids_a_vide", "masse_ordre_marche", "prix", "prix_min", "prix_max", "nb_finitions",
					 "gamme_niveau", "bareme_bonus_malus"]

# journal des étapes pour le bilan : [(étape, nombre de lignes après l'étape)]
bilan = []
# lignes écartées, chacune avec la raison du rejet
rejets = []


def noter(etape, df):
	bilan.append((etape, len(df)))
	return df


def rejeter(df, masque, raison):
	"""met de côté les lignes où masque est vrai (avec la raison) et retourne les autres"""
	if masque.any():
		lignes = df[masque].copy()
		lignes.insert(0, "raison", raison)
		rejets.append(lignes)
	return df[~masque]


def lireBrut(chemin):
	# utf-8-sig retire le caractère invisible (BOM) au début du fichier
	return pd.read_csv(chemin, sep=';', encoding='utf-8-sig', decimal=',')


def garderColonnes(df):
	manquantes = [c for c in COLONNES if c not in df.columns]
	if manquantes:
		raise SystemExit(f"colonnes absentes du fichier brut : {manquantes}")
	return df[list(COLONNES.keys())].rename(columns=COLONNES)


def reparerEncodage(texte):
	"""
	certains textes ont été enregistrés en UTF-8 puis relus en Latin-1 : "é" devient "Ã©".
	on refait l'opération à l'envers. Si ça échoue, on garde le texte tel quel.
	"""
	if type(texte) is not str or "Ã" not in texte:
		return texte
	try:
		return texte.encode('latin-1').decode('utf-8')
	except (UnicodeEncodeError, UnicodeDecodeError):
		return texte


def nettoyerTextes(df):
	for colonne in ["marque", "libelle_modele", "description_commerciale"]:
		df[colonne] = df[colonne].map(reparerEncodage)
		# espaces en trop au début, à la fin, ou en double au milieu
		df[colonne] = df[colonne].str.strip().str.replace(r"\s+", " ", regex=True)

	df["marque"] = df["marque"].replace(MARQUES)
	df["libelle_modele"] = df["libelle_modele"].str.upper()
	return df


def harmoniserCategories(df):
	df["famille_energie"] = df["energie"].map(lambda e: ENERGIES.get(e, (None, None))[1])
	df["energie"] = df["energie"].map(lambda e: ENERGIES.get(e, (None, None))[0])
	df["carrosserie"] = df["carrosserie"].map(CARROSSERIES)
	df["gamme_niveau"] = df["gamme"].map(lambda g: GAMMES.get(g, (None, None))[1])
	df["gamme"] = df["gamme"].map(lambda g: GAMMES.get(g, (None, None))[0])
	df["type_boite"] = df["type_boite"].map(BOITES)
	return df


def convertirUnites(df):
	# puissance : kW (ADEME) -> ch
	df["puissance_ch"] = (df["puissance_max_kw"] * KW_VERS_CH).round()
	df["puissance_elec_ch"] = (df["puissance_elec_kw"] * KW_VERS_CH).round()
	# consommation électrique : Wh/km (ADEME) -> kWh/100 km, l'unité affichée partout en France
	for colonne in ["conso_elec_min", "conso_elec_max"]:
		df[colonne] = (df[colonne] / 10).round(1)
	return df.drop(columns=["puissance_max_kw", "puissance_elec_kw"])


def puissanceDepuisDescription(description):
	"""
	lit la puissance en ch dans la description : "e-Soul (204ch)" -> 204.
	les valeurs en kW de la description ("(57Kw)") sont des puissances nominales, on les ignore.
	"""
	resultat = re.search(r"\((\d+)\s*ch\)", str(description), re.IGNORECASE)
	if resultat is None:
		return None
	return int(resultat.group(1))


def completerValeurs(df):
	electrique = df["famille_energie"] == "electrique"

	# 0 seulement quand c'est la vraie valeur physique :
	# une électrique n'émet pas de CO2 à l'échappement, une thermique n'a pas de moteur électrique
	df.loc[electrique, ["co2_mixte_min", "co2_mixte_max"]] = 0
	df.loc[df["famille_energie"] == "thermique", "puissance_elec_ch"] = 0
	# les autres cases vides (autonomie d'une thermique, conso en L/100 km d'une électrique...)
	# veulent dire « sans objet » : 0 serait faux et fausserait les calculs, elles restent vides (NULL)

	# l'ADEME ne donne pas la puissance maximale des électriques, seulement la puissance nominale
	# (bien plus faible). On lit d'abord la description, sinon on prend la nominale et on le signale
	# avec puissance_estimee (ex : BMW iX M60 = 190 ch nominal pour environ 620 ch réels)
	df["puissance_estimee"] = False
	sansPuissance = electrique & df["puissance_ch"].isna()
	df.loc[sansPuissance, "puissance_ch"] = df.loc[sansPuissance, "description_commerciale"].map(puissanceDepuisDescription)
	sansPuissance = electrique & df["puissance_ch"].isna()
	df.loc[sansPuissance, "puissance_ch"] = df.loc[sansPuissance, "puissance_elec_ch"]
	df.loc[sansPuissance, "puissance_estimee"] = True

	# si une seule valeur de la paire min / max est connue, on la recopie dans l'autre
	for colMin, colMax in PAIRES_MIN_MAX:
		df[colMin] = df[colMin].fillna(df[colMax])
		df[colMax] = df[colMax].fillna(df[colMin])

	# barème : bonus = montant négatif, neutre = 0. On le déduit du libellé quand il manque
	statut = df["statut_ecologique"].str.strip()
	montantBonus = -pd.to_numeric(statut.str.extract(r"Bonus (\d+)")[0], errors='coerce')
	df["bareme_bonus_malus"] = df["bareme_bonus_malus"].fillna(montantBonus)
	neutre = statut.str.startswith("Neutre")
	df.loc[neutre, "bareme_bonus_malus"] = df.loc[neutre, "bareme_bonus_malus"].fillna(0)
	df["statut_ecologique"] = statut.str.split(" ").str[0].str.lower().replace({"autres": "autre"})
	return df


def corrigerIncoherences(df):
	# les colonnes min / max de l'ADEME correspondent à la version la plus légère / la plus lourde,
	# donc parfois "min" > "max" (ex : autonomie). On les remet dans l'ordre pour avoir un intervalle
	for colMin, colMax in PAIRES_MIN_MAX:
		inverse = df[colMin] > df[colMax]
		df.loc[inverse, [colMin, colMax]] = df.loc[inverse, [colMax, colMin]].values
	return df


def rejeterLignes(df):
	"""
	on écarte une ligne seulement si une information indispensable manque, si une valeur est
	impossible, ou si le véhicule est hors cible (prix). Chaque rejet est enregistré avec sa raison.
	Les cases vides des colonnes "électriques" pour une voiture thermique (et inversement)
	ne sont PAS des erreurs : elles veulent dire "sans objet" et restent vides (NULL en base).
	"""
	for colonne in INDISPENSABLES:
		df = rejeter(df, df[colonne].isna(), f"{colonne} manquant")

	df = rejeter(df, df["prix"] <= 0, "prix négatif ou nul")
	df = rejeter(df, df["poids_a_vide"] < 500, "poids à vide impossible (< 500 kg)")
	df = rejeter(df, df["puissance_ch"] <= 0, "puissance négative ou nulle")
	if PRIX_MAX is not None:
		df = rejeter(df, df["prix"] > PRIX_MAX, f"prix supérieur à {PRIX_MAX} € (hors cible)")
	return df


def regrouperFinitions(df):
	"""
	plusieurs lignes décrivent la même voiture avec des prix ou des émissions légèrement différents
	(finitions, taille des jantes...). On garde une seule ligne par voiture :
	  - prix médian + prix min / max + nombre de finitions
	  - pour les paires min / max : le plus petit min et le plus grand max (on garde tout l'intervalle)
	  - pour les autres nombres : la médiane
	"""
	regles = {
		"prix": "median",
		"statut_ecologique": lambda s: s.mode().iloc[0],  # statut le plus fréquent
		"bareme_bonus_malus": "median",
	}
	for colMin, colMax in PAIRES_MIN_MAX:
		regles[colMin] = "min"
		regles[colMax] = "max"
	for colonne in df.columns:
		if colonne not in CLES_VOITURE and colonne not in regles:
			regles[colonne] = "median"

	# dropna=False : sinon pandas ignore les groupes qui ont une case vide
	groupes = df.groupby(CLES_VOITURE, dropna=False, sort=False)
	resultat = groupes.agg(regles)
	resultat["prix_min"] = groupes["prix"].min()
	resultat["prix_max"] = groupes["prix"].max()
	resultat["nb_finitions"] = groupes["prix"].size()
	return resultat.reset_index()


def finaliser(df):
	if "prix_min" not in df.columns:
		df["prix_min"] = df["prix"]
		df["prix_max"] = df["prix"]
		df["nb_finitions"] = 1

	df = df.sort_values(["marque", "libelle_modele", "prix"]).reset_index(drop=True)
	df["id"] = df.index + 1

	# Int64 accepte les cases vides (sinon pandas écrit 1998.0 au lieu de 1998)
	for colonne in COLONNES_ENTIERES:
		df[colonne] = df[colonne].round().astype("Int64")
	return df[COLONNES_FINALES]


def ecrireRejets(chemin):
	if not rejets:
		# fichier avec seulement l'en-tête : on voit qu'il n'y a eu aucun rejet
		pd.DataFrame(columns=["raison"]).to_csv(chemin, sep=';', index=False)
		return pd.DataFrame(columns=["raison"])
	tout = pd.concat(rejets, ignore_index=True)
	tout.to_csv(chemin, sep=';', index=False, encoding='utf-8')
	return tout


def afficherBilan(df, dfRejets):
	print("\n=== Bilan du nettoyage ===")
	precedent = None
	for etape, nb in bilan:
		ecart = "" if precedent is None else f"  ({nb - precedent:+d})"
		print(f"{etape:<40} {nb:>6} lignes{ecart}")
		precedent = nb

	print(f"\nlignes rejetées : {len(dfRejets)}")
	for raison, nb in dfRejets["raison"].value_counts().items():
		print(f"  {raison:<45} {nb:>5}")

	print(f"\n{len(df)} véhicules, {len(df.columns)} colonnes")
	print("répartition par famille d'énergie :", df["famille_energie"].value_counts().to_dict())
	print("cases vides (« sans objet » pour une partie des véhicules) :")
	vides = df.isna().sum()
	for colonne, nb in vides[vides > 0].items():
		print(f"  {colonne:<25} {nb:>5}")


def nettoyer(cheminEntree, cheminSortie):
	df = noter("lecture du fichier brut", lireBrut(cheminEntree))
	df = noter("suppression des lignes identiques", df.drop_duplicates())
	df = garderColonnes(df)
	df = nettoyerTextes(df)
	df = harmoniserCategories(df)
	df = convertirUnites(df)
	df = completerValeurs(df)
	df = corrigerIncoherences(df)
	df = noter("rejet des lignes inutilisables", rejeterLignes(df))
	if REGROUPER_FINITIONS:
		df = noter("regroupement des finitions", regrouperFinitions(df))
	df = finaliser(df)

	df.to_csv(cheminSortie, sep=';', index=False, encoding='utf-8')
	cheminRejets = os.path.join(os.path.dirname(os.path.abspath(cheminSortie)), 'rejets.csv')
	dfRejets = ecrireRejets(cheminRejets)

	afficherBilan(df, dfRejets)
	print(f"\nfichier écrit : {os.path.normpath(cheminSortie)}")
	print(f"rejets écrits : {os.path.normpath(cheminRejets)}")
	return df


if __name__ == '__main__':
	entree = sys.argv[1] if len(sys.argv) > 1 else FICHIER_BRUT
	sortie = sys.argv[2] if len(sys.argv) > 2 else FICHIER_PROPRE
	nettoyer(entree, sortie)
