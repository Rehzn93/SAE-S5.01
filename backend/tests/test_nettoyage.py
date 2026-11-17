"""
tests du script de nettoyage : python -m pytest tests/test_nettoyage.py -v  (depuis backend/)

- tests unitaires : chaque fonction est testée sur quelques lignes écrites à la main
- test complet : lance le nettoyage sur le vrai fichier ADEME (ignoré si le fichier est absent)
"""
import io, math, os
import pandas as pd
import pytest
from scripts import nettoyage_donnees as nd


@pytest.fixture(autouse=True)
def viderJournaux():
	""" le script garde les rejets et le bilan dans des listes globales : on les vide avant chaque test """
	nd.rejets.clear()
	nd.bilan.clear()


def ligne(**valeurs):
	""" une ligne au format du fichier ADEME après renommage, avec des valeurs par défaut réalistes """
	base = {
		"marque": "RENAULT", "libelle_modele": "CLIO", "description_commerciale": "CLIO (91ch)",
		"gamme": "INFERIEURE", "carrosserie": "BERLINE", "energie": "ESSENCE", "cylindree": 999,
		"puissance_max_kw": 67.0, "puissance_elec_kw": None, "puissance_fiscale": 5,
		"type_boite": "MECANIQUE", "nb_rapports": 5, "poids_a_vide": 1100, "masse_ordre_marche": 1180,
		"autonomie_elec_min": None, "autonomie_elec_max": None, "autonomie_elec_urbain": None,
		"conso_elec_min": None, "conso_elec_max": None, "conso_mixte_min": 5.2, "conso_mixte_max": 5.6,
		"conso_ville": 6.5, "conso_periurbain": 5.0, "conso_route": 4.6, "conso_autoroute": 6.0,
		"co2_mixte_min": 118.0, "co2_mixte_max": 126.0, "prix": 21000,
		"statut_ecologique": "Neutre 0", "bareme_bonus_malus": None,
	}
	base.update(valeurs)
	return base


def preparer(*lignes):
	""" applique les étapes du script jusqu'à la correction des incohérences (comme dans nettoyer()) """
	# on passe par un CSV en mémoire pour avoir les mêmes types qu'à la lecture du vrai fichier
	# (cases vides = NaN dans une colonne de nombres, et pas None dans une colonne de texte)
	csv = pd.DataFrame(list(lignes)).to_csv(sep=';', index=False)
	df = pd.read_csv(io.StringIO(csv), sep=';')
	df = nd.nettoyerTextes(df)
	df = nd.harmoniserCategories(df)
	df = nd.convertirUnites(df)
	df = nd.completerValeurs(df)
	return nd.corrigerIncoherences(df)


def electrique(**valeurs):
	return ligne(**{
		"description_commerciale": "ZOE (51Kw)", "libelle_modele": "ZOE", "energie": "ELECTRIC",
		"puissance_max_kw": None, "puissance_elec_kw": 51.0, "type_boite": "VARIATION ELECTRIQUE",
		"conso_mixte_min": None, "conso_mixte_max": None, "conso_ville": None, "conso_periurbain": None,
		"conso_route": None, "conso_autoroute": None, "co2_mixte_min": None, "co2_mixte_max": None,
		"conso_elec_min": 175.0, "conso_elec_max": 190.0, "autonomie_elec_min": 380.0,
		"autonomie_elec_max": 340.0, "autonomie_elec_urbain": 450.0, "prix": 33000,
		"statut_ecologique": "Bonus 6000", **valeurs})


# --- textes ---

def test_reparer_encodage():
	assert nd.reparerEncodage("M4 Competition CoupÃ©") == "M4 Competition Coupé"
	assert nd.reparerEncodage("SystÃ¨me hybride") == "Système hybride"


def test_texte_correct_inchange():
	assert nd.reparerEncodage("Clio Évolution") == "Clio Évolution"
	assert nd.reparerEncodage(None) is None


def test_marques_et_espaces():
	df = preparer(ligne(marque="B.M.W.", description_commerciale="  118i   Sport "))
	assert df.loc[0, "marque"] == "BMW"
	assert df.loc[0, "description_commerciale"] == "118i Sport"


# --- catégories ---

def test_categories_traduites():
	df = preparer(ligne(energie="ELEC+ESSENC HR", carrosserie="TS TERRAINS/CHEMINS", gamme="LUXE"))
	assert df.loc[0, "energie"] == "hybride_rechargeable_essence"
	assert df.loc[0, "famille_energie"] == "hybride_rechargeable"
	assert df.loc[0, "carrosserie"] == "suv"
	assert df.loc[0, "gamme"] == "luxe"
	assert df.loc[0, "gamme_niveau"] == 6
	assert df.loc[0, "type_boite"] == "manuelle"


# --- unités ---

def test_puissance_en_chevaux():
	df = preparer(ligne(puissance_max_kw=100.0))
	assert df.loc[0, "puissance_ch"] == 136
	assert "puissance_max_kw" not in df.columns


def test_conso_electrique_en_kwh_100km():
	df = preparer(electrique())
	assert df.loc[0, "conso_elec_min"] == 17.5
	assert df.loc[0, "conso_elec_max"] == 19.0


def test_puissance_lue_dans_la_description():
	assert nd.puissanceDepuisDescription("e-Soul (204ch)") == 204
	assert nd.puissanceDepuisDescription("ZOE (51Kw)") is None


# --- valeurs manquantes ---

def test_electrique_complete():
	df = preparer(electrique())
	assert df.loc[0, "co2_mixte_max"] == 0
	# pas de "(...ch)" dans la description : puissance nominale (51 kW = 69 ch) signalée comme estimée
	assert df.loc[0, "puissance_ch"] == 69
	assert df.loc[0, "puissance_estimee"] == True
	# la conso en L/100 km reste vide : 0 serait une fausse donnée
	assert math.isnan(df.loc[0, "conso_mixte_max"])


def test_thermique_sans_moteur_electrique():
	df = preparer(ligne())
	assert df.loc[0, "puissance_elec_ch"] == 0
	assert math.isnan(df.loc[0, "autonomie_elec_max"])


def test_min_ou_max_recopie():
	df = preparer(ligne(conso_mixte_min=None, conso_mixte_max=5.6))
	assert df.loc[0, "conso_mixte_min"] == 5.6


def test_bareme_bonus_malus():
	df = preparer(electrique(), ligne(statut_ecologique="Neutre 0"))
	assert df.loc[0, "bareme_bonus_malus"] == -6000
	assert df.loc[0, "statut_ecologique"] == "bonus"
	assert df.loc[1, "bareme_bonus_malus"] == 0
	assert df.loc[1, "statut_ecologique"] == "neutre"


def test_min_max_remis_dans_l_ordre():
	df = preparer(electrique(autonomie_elec_min=380.0, autonomie_elec_max=340.0))
	assert df.loc[0, "autonomie_elec_min"] == 340
	assert df.loc[0, "autonomie_elec_max"] == 380


# --- rejets ---

def test_rejet_prix_trop_eleve():
	df = preparer(ligne(), ligne(prix=nd.PRIX_MAX + 1))
	gardees = nd.rejeterLignes(df)
	assert len(gardees) == 1
	assert len(nd.rejets) == 1
	assert "prix supérieur" in nd.rejets[0].iloc[0]["raison"]


def test_rejet_donnee_indispensable_manquante():
	df = preparer(ligne(prix=None))
	gardees = nd.rejeterLignes(df)
	assert len(gardees) == 0
	assert nd.rejets[0].iloc[0]["raison"] == "prix manquant"


def test_electrique_pas_rejetee_pour_cases_sans_objet():
	df = preparer(electrique())
	assert len(nd.rejeterLignes(df)) == 1


# --- regroupement des finitions ---

def test_finitions_regroupees():
	df = preparer(ligne(prix=20000), ligne(prix=22000), ligne(prix=24000, co2_mixte_max=130.0))
	resultat = nd.regrouperFinitions(df)
	assert len(resultat) == 1
	assert resultat.loc[0, "prix"] == 22000
	assert resultat.loc[0, "prix_min"] == 20000
	assert resultat.loc[0, "prix_max"] == 24000
	assert resultat.loc[0, "nb_finitions"] == 3
	# on garde tout l'intervalle de CO2
	assert resultat.loc[0, "co2_mixte_max"] == 130


def test_versions_differentes_non_regroupees():
	df = preparer(ligne(), ligne(energie="GAZOLE"), ligne(type_boite="AUTOMATIQUE"))
	assert len(nd.regrouperFinitions(df)) == 3


# --- test complet sur le vrai fichier ADEME ---

@pytest.mark.skipif(not os.path.exists(nd.FICHIER_BRUT), reason="ademe_brut.csv absent de app/static/data/")
def test_nettoyage_complet(tmp_path):
	sortie = tmp_path / "vehicules.csv"
	nd.nettoyer(nd.FICHIER_BRUT, str(sortie))
	df = pd.read_csv(sortie, sep=';')

	assert list(df.columns) == nd.COLONNES_FINALES
	assert len(df) > 500
	assert df["id"].is_unique
	# aucune case vide dans les colonnes indispensables
	assert df[nd.INDISPENSABLES].notna().all().all()
	assert df["prix"].max() <= nd.PRIX_MAX
	# plus aucun accent mal encodé
	assert not df["description_commerciale"].str.contains("Ã").any()
	# règles métier
	assert (df.loc[df["famille_energie"] == "electrique", "co2_mixte_max"] == 0).all()
	assert (df["conso_mixte_min"].dropna() <= df["conso_mixte_max"].dropna()).all()
	assert set(df["type_boite"]) <= {"manuelle", "automatique"}
	assert (tmp_path / "rejets.csv").exists()
