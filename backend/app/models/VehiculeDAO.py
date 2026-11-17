from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.Vehicule import Vehicule


class VehiculeDAO:
    """Data Access Object pour interroger la table des véhicules."""

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Vehicule]:
        """Retourne tous les véhicules triés par marque et modèle."""
        return (
            self.session.query(Vehicule)
            .order_by(Vehicule.marque, Vehicule.libelle_modele)
            .all()
        )

    def get_by_id(self, vehicule_id: int) -> Optional[Vehicule]:
        """Retourne un véhicule par son identifiant unique."""
        return self.session.query(Vehicule).filter(Vehicule.id == vehicule_id).first()

    def get_by_ids(self, vehicule_ids: List[int]) -> List[Vehicule]:
        """Retourne une liste de véhicules à partir d'une liste d'identifiants."""
        if not vehicule_ids:
            return []
        return self.session.query(Vehicule).filter(Vehicule.id.in_(vehicule_ids)).all()