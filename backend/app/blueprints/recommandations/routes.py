import pandas as pd
from flask import Blueprint, jsonify, request
from app.services import VehiculeService
from app.services.recommandations.score_pondere import recommander

recommandation_bp = Blueprint("recommandations", __name__, url_prefix="/api/recommandations")


@recommandation_bp.route("", methods=["POST"])
def post_recommandations():
    """
    Recommande les meilleurs véhicules selon les critères du questionnaire utilisateur
    ---
    tags:
      - Recommandations
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            budget_max:
              type: integer
              example: 35000
            energies:
              type: array
              items:
                type: string
                enum: [essence, diesel, hybride, hybride_rechargeable, electrique]
              example: ["hybride", "electrique"]
            boite:
              type: string
              enum: [automatique, manuelle]
              example: "automatique"
            carrosseries:
              type: array
              items:
                type: string
                enum: [SUV, berline, break, minibus, ludospace, coupe, cabriolet, monospace]
              example: ["berline", "SUV"]
            puissance_min_ch:
              type: integer
              example: 100
            conso_max:
              type: number
              example: 6.5
            conso_elec_max:
              type: number
              example: 20.0
            autonomie_min_km:
              type: integer
              example: 300
            trajet:
              type: string
              enum: [ville, periurbain, route, autoroute, mixte]
              example: "mixte"
            priorite_ecologie:
              type: boolean
              example: true
            marques:
              type: array
              items:
                type: string
              example: ["PEUGEOT", "RENAULT"]
            nb_resultats:
              type: integer
              example: 5
    responses:
      200:
        description: Liste des meilleurs véhicules scorés avec le détail des notes
    """
    criteres = request.get_json(silent=True) or {}

    # 1. Récupération des 748 véhicules depuis PostgreSQL sous forme de DataFrame
    service = VehiculeService()
    df = pd.DataFrame(service.getAllVehiculesFlat())

    # 2. Appel direct de l'algorithme de score pondéré sans le modifier
    resultat = recommander(df, criteres)

    return jsonify(resultat), 200