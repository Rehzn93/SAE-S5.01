import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from main import app
from app.models.base import Base, get_engine
from app.models.Vehicule import Vehicule


def init_db():
    # Récupération directe de la config et du dossier static depuis l'app Flask
    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    csv_path = os.path.join(app.static_folder, "data", "vehicules.csv")

    engine = get_engine(db_uri)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. Création de la table 'vehicules' si elle n'existe pas
        print("Création des tables SQLAlchemy...")
        Base.metadata.create_all(engine)

        # 2. Vérifier si la base est déjà remplie pour éviter les doublons
        existing_count = session.query(Vehicule).count()
        if existing_count > 0:
            print(f"La table contient déjà {existing_count} véhicules. Aucune insertion nécessaire.")
            return

        # 3. Lecture du CSV nettoyé
        print(f"Lecture du fichier {csv_path}...")
        df = pd.read_csv(csv_path, sep=";")

        # Forcer le type object pour que None ne soit pas reconverti en float NaN par Pandas
        df = df.astype(object).where(pd.notnull(df), None)

        vehicules = []
        for row in df.to_dict(orient="records"):
            # Conversion propre en entier si la valeur n'est pas None
            if row.get("puissance_elec_ch") is not None:
                row["puissance_elec_ch"] = int(float(row["puissance_elec_ch"]))

            if row.get("puissance_estimee") is not None:
                row["puissance_estimee"] = bool(row["puissance_estimee"])

            vehicules.append(Vehicule(**row))

        # 4. Insertion en masse dans PostgreSQL
        session.bulk_save_objects(vehicules)
        session.commit()
        print(f"✅ Import terminé : {len(vehicules)} véhicules insérés dans PostgreSQL.")

    except Exception as e:
        session.rollback()
        print(f"❌ Erreur lors de l'initialisation de la base : {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    init_db()