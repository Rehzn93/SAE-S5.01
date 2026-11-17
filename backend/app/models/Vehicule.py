from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Float, Boolean
from app.models.base import Base, BaseModelMixin


class Vehicule(Base, BaseModelMixin):
    """Modèle SQLAlchemy représentant une version de véhicule (37 champs ADEME nettoyés)."""
    __tablename__ = 'vehicules'

    # --- 1. Racine ---
    id = Column(Integer, primary_key=True, autoincrement=True)

    # --- 2. Identification ---
    marque = Column(String(100), nullable=False, index=True)
    libelle_modele = Column(String(150), nullable=False, index=True)
    description_commerciale = Column(String(255), nullable=False)
    gamme = Column(String(50), nullable=False)
    gamme_niveau = Column(Integer, nullable=False)
    carrosserie = Column(String(50), nullable=False, index=True)

    # --- 3. Motorisation ---
    energie = Column(String(50), nullable=False)
    famille_energie = Column(String(50), nullable=False, index=True)
    cylindree = Column(Integer, nullable=False)  # 0 pour une électrique
    puissance_ch = Column(Integer, nullable=False)
    puissance_elec_ch = Column(Integer, nullable=True)  # null pour 60 hybrides non renseignés
    puissance_estimee = Column(Boolean, nullable=False, default=False)
    puissance_fiscale = Column(Integer, nullable=False)
    type_boite = Column(String(50), nullable=False)
    nb_rapports = Column(Integer, nullable=False)

    # --- 4. Poids ---
    poids_a_vide = Column(Integer, nullable=False)
    masse_ordre_marche = Column(Integer, nullable=False)

    # --- 5. Performances électriques (null pour thermiques et hybrides simples) ---
    autonomie_elec_min = Column(Float, nullable=True)
    autonomie_elec_max = Column(Float, nullable=True)
    autonomie_elec_urbain = Column(Float, nullable=True)
    conso_elec_min = Column(Float, nullable=True)
    conso_elec_max = Column(Float, nullable=True)

    # --- 6. Consommation et émissions ---
    conso_mixte_min = Column(Float, nullable=True)      # null pour électriques
    conso_mixte_max = Column(Float, nullable=True)      # null pour électriques
    conso_ville = Column(Float, nullable=True)          # null pour électriques et hybrides rechargeables
    conso_periurbain = Column(Float, nullable=True)     # null pour électriques et hybrides rechargeables
    conso_route = Column(Float, nullable=True)          # null pour électriques et hybrides rechargeables
    conso_autoroute = Column(Float, nullable=True)      # null pour électriques et hybrides rechargeables
    co2_mixte_min = Column(Float, nullable=False)       # 0.0 pour électriques
    co2_mixte_max = Column(Float, nullable=False)       # 0.0 pour électriques

    # --- 7. Prix et fiscalité ---
    prix = Column(Integer, nullable=False)
    prix_min = Column(Integer, nullable=False)
    prix_max = Column(Integer, nullable=False)
    nb_finitions = Column(Integer, nullable=False)
    statut_ecologique = Column(String(50), nullable=False)
    bareme_bonus_malus = Column(Integer, nullable=False)

    def __init__(
        self,
        marque: str = None,
        libelle_modele: str = None,
        description_commerciale: str = None,
        gamme: str = None,
        gamme_niveau: int = None,
        carrosserie: str = None,
        energie: str = None,
        famille_energie: str = None,
        cylindree: int = 0,
        puissance_ch: int = None,
        puissance_elec_ch: Optional[int] = None,
        puissance_estimee: bool = False,
        puissance_fiscale: int = None,
        type_boite: str = None,
        nb_rapports: int = None,
        poids_a_vide: int = None,
        masse_ordre_marche: int = None,
        autonomie_elec_min: Optional[float] = None,
        autonomie_elec_max: Optional[float] = None,
        autonomie_elec_urbain: Optional[float] = None,
        conso_elec_min: Optional[float] = None,
        conso_elec_max: Optional[float] = None,
        conso_mixte_min: Optional[float] = None,
        conso_mixte_max: Optional[float] = None,
        conso_ville: Optional[float] = None,
        conso_periurbain: Optional[float] = None,
        conso_route: Optional[float] = None,
        conso_autoroute: Optional[float] = None,
        co2_mixte_min: float = 0.0,
        co2_mixte_max: float = 0.0,
        prix: int = None,
        prix_min: int = None,
        prix_max: int = None,
        nb_finitions: int = 1,
        statut_ecologique: str = None,
        bareme_bonus_malus: int = 0,
        id: Optional[int] = None
    ):
        if id is not None:
            self.id = id
        self.marque = marque
        self.libelle_modele = libelle_modele
        self.description_commerciale = description_commerciale
        self.gamme = gamme
        self.gamme_niveau = gamme_niveau
        self.carrosserie = carrosserie
        self.energie = energie
        self.famille_energie = famille_energie
        self.cylindree = cylindree
        self.puissance_ch = puissance_ch
        self.puissance_elec_ch = puissance_elec_ch
        self.puissance_estimee = puissance_estimee
        self.puissance_fiscale = puissance_fiscale
        self.type_boite = type_boite
        self.nb_rapports = nb_rapports
        self.poids_a_vide = poids_a_vide
        self.masse_ordre_marche = masse_ordre_marche
        self.autonomie_elec_min = autonomie_elec_min
        self.autonomie_elec_max = autonomie_elec_max
        self.autonomie_elec_urbain = autonomie_elec_urbain
        self.conso_elec_min = conso_elec_min
        self.conso_elec_max = conso_elec_max
        self.conso_mixte_min = conso_mixte_min
        self.conso_mixte_max = conso_mixte_max
        self.conso_ville = conso_ville
        self.conso_periurbain = conso_periurbain
        self.conso_route = conso_route
        self.conso_autoroute = conso_autoroute
        self.co2_mixte_min = co2_mixte_min
        self.co2_mixte_max = co2_mixte_max
        self.prix = prix
        self.prix_min = prix_min
        self.prix_max = prix_max
        self.nb_finitions = nb_finitions
        self.statut_ecologique = statut_ecologique
        self.bareme_bonus_malus = bareme_bonus_malus

    def to_flat_dict(self) -> Dict[str, Any]:
        """Retourne le dictionnaire à plat via BaseModelMixin (utile pour Pandas / algos)."""
        return super().to_dict()

    def to_dict(self) -> Dict[str, Any]:
        """Retourne le dictionnaire regroupé exactement comme attendu par le Front."""
        has_elec_perf = any(
            val is not None for val in (
                self.autonomie_elec_min,
                self.autonomie_elec_max,
                self.autonomie_elec_urbain,
                self.conso_elec_min,
                self.conso_elec_max,
            )
        )

        performances_electriques = None
        if has_elec_perf:
            performances_electriques = {
                "autonomie_elec_min": self.autonomie_elec_min,
                "autonomie_elec_max": self.autonomie_elec_max,
                "autonomie_elec_urbain": self.autonomie_elec_urbain,
                "conso_elec_min": self.conso_elec_min,
                "conso_elec_max": self.conso_elec_max,
            }

        return {
            "id": self.id,
            "identification": {
                "marque": self.marque,
                "libelle_modele": self.libelle_modele,
                "description_commerciale": self.description_commerciale,
                "gamme": self.gamme,
                "gamme_niveau": self.gamme_niveau,
                "carrosserie": self.carrosserie,
            },
            "motorisation": {
                "energie": self.energie,
                "famille_energie": self.famille_energie,
                "cylindree": self.cylindree,
                "puissance_ch": self.puissance_ch,
                "puissance_elec_ch": self.puissance_elec_ch,
                "puissance_estimee": self.puissance_estimee,
                "puissance_fiscale": self.puissance_fiscale,
                "type_boite": self.type_boite,
                "nb_rapports": self.nb_rapports,
            },
            "poids": {
                "poids_a_vide": self.poids_a_vide,
                "masse_ordre_marche": self.masse_ordre_marche,
            },
            "performances_electriques": performances_electriques,
            "conso_emissions": {
                "conso_mixte_min": self.conso_mixte_min,
                "conso_mixte_max": self.conso_mixte_max,
                "conso_ville": self.conso_ville,
                "conso_periurbain": self.conso_periurbain,
                "conso_route": self.conso_route,
                "conso_autoroute": self.conso_autoroute,
                "co2_mixte_min": self.co2_mixte_min,
                "co2_mixte_max": self.co2_mixte_max,
            },
            "prix_fiscalite": {
                "prix": self.prix,
                "prix_min": self.prix_min,
                "prix_max": self.prix_max,
                "nb_finitions": self.nb_finitions,
                "statut_ecologique": self.statut_ecologique,
                "bareme_bonus_malus": self.bareme_bonus_malus,
            },
        }