import os
from typing import List, Optional
from sqlalchemy.orm import sessionmaker
from app.models.Vehicule import Vehicule
from app.models.base import get_engine


class VehiculeORM:
    """DAO SQLAlchemy pour la table vehicules, calqué sur l'architecture du cours."""

    def __init__(self, db_uri: Optional[str] = None):
        if db_uri is not None:
            self.db_uri = db_uri
        else:
            self.db_uri = os.getenv(
                "DATABASE_URL",
                "postgresql://user_sae:password_sae@localhost:5432/vehicules_db"
            )

        self.engine = get_engine(self.db_uri)
        self.SessionFactory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def connect(self):
        return self.SessionFactory()

    def findAll(self) -> List[Vehicule]:
        session = self.connect()
        try:
            return (
                session.query(Vehicule)
                .order_by(Vehicule.marque, Vehicule.libelle_modele)
                .all()
            )
        finally:
            session.close()

    def findById(self, vehicule_id: int) -> Optional[Vehicule]:
        session = self.connect()
        try:
            return session.query(Vehicule).filter(Vehicule.id == vehicule_id).first()
        finally:
            session.close()

    def findByIds(self, vehicule_ids: List[int]) -> List[Vehicule]:
        if not vehicule_ids:
            return []
        session = self.connect()
        try:
            return session.query(Vehicule).filter(Vehicule.id.in_(vehicule_ids)).all()
        finally:
            session.close()

    def findFiltered(
        self,
        marque: Optional[str] = None,
        famille_energie: Optional[str] = None,
        carrosserie: Optional[str] = None,
        type_boite: Optional[str] = None,
        gamme: Optional[str] = None,
        prix_max: Optional[int] = None,
        puissance_min: Optional[int] = None,
    ) -> List[Vehicule]:
        session = self.connect()
        try:
            query = session.query(Vehicule)

            if marque:
                query = query.filter(Vehicule.marque == marque.upper())
            if famille_energie:
                query = query.filter(Vehicule.famille_energie == famille_energie)
            if carrosserie:
                query = query.filter(Vehicule.carrosserie == carrosserie)
            if type_boite:
                query = query.filter(Vehicule.type_boite == type_boite)
            if gamme:
                query = query.filter(Vehicule.gamme == gamme)
            if prix_max is not None:
                query = query.filter(Vehicule.prix <= prix_max)
            if puissance_min is not None:
                query = query.filter(Vehicule.puissance_ch >= puissance_min)

            return query.order_by(Vehicule.marque, Vehicule.libelle_modele).all()
        finally:
            session.close()