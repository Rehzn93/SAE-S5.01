from typing import Dict, Any, List, Optional
from flask import current_app
from app.models.VehiculeDAO import VehiculeORM as VehiculeDAO


class VehiculeService:
    """Service métier gérant la logique des véhicules et le formatage JSON."""

    def __init__(self, db_uri: Optional[str] = None):
        if db_uri is None:
            try:
                db_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI")
            except RuntimeError:
                pass
        self.vdao = VehiculeDAO(db_uri=db_uri)

    def getAllVehicules(self) -> List[Dict[str, Any]]:
        """Retourne tous les véhicules au format JSON regroupé attendu par le Front."""
        vehicules = self.vdao.findAll()
        return [v.to_dict() for v in vehicules]

    def getVehiculeById(self, vehicule_id: int) -> Optional[Dict[str, Any]]:
        """Retourne un véhicule spécifique au format JSON regroupé, ou None s'il n'existe pas."""
        vehicule = self.vdao.findById(vehicule_id)
        return vehicule.to_dict() if vehicule else None

    def getVehiculesByIds(self, vehicule_ids: List[int]) -> List[Dict[str, Any]]:
        """Utile pour l'équipe Algo/KNN : transforme une liste d'IDs recommandés en JSON complet."""
        vehicules = self.vdao.findByIds(vehicule_ids)
        # Préserve l'ordre de pertinence renvoyé par l'algorithme
        vehicules_map = {v.id: v.to_dict() for v in vehicules}
        return [vehicules_map[vid] for vid in vehicule_ids if vid in vehicules_map]

    def searchVehicules(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filtre les véhicules selon les critères envoyés en query params par le Front."""
        vehicules = self.vdao.findFiltered(
            marque=filters.get("marque"),
            famille_energie=filters.get("famille_energie"),
            carrosserie=filters.get("carrosserie"),
            type_boite=filters.get("type_boite"),
            gamme=filters.get("gamme"),
            prix_max=filters.get("prix_max"),
            puissance_min=filters.get("puissance_min"),
        )
        return [v.to_dict() for v in vehicules]

    def getAllVehiculesFlat(self) -> List[Dict[str, Any]]:
        """Retourne les données à plat (37 colonnes) pour les calculs Pandas de l'équipe Data."""
        vehicules = self.vdao.findAll()
        return [v.to_flat_dict() for v in vehicules]