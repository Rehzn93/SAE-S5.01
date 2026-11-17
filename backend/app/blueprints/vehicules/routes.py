from flask import Blueprint, jsonify, request
from app.services import VehiculeService

vehicule_bp = Blueprint("vehicules", __name__, url_prefix="/api/vehicules")


@vehicule_bp.route("", methods=["GET"])
def get_vehicules():
    """
    Récupère la liste des véhicules (tous ou filtrés)
    ---
    tags:
      - Véhicules
    parameters:
      - name: marque
        in: query
        type: string
        required: false
        description: Marque du véhicule en majuscules (ex. RENAULT, PEUGEOT, TESLA)
      - name: famille_energie
        in: query
        type: string
        enum: [thermique, hybride, electrique, hybride_rechargeable]
        required: false
        description: Famille de motorisation
      - name: carrosserie
        in: query
        type: string
        enum: [SUV, berline, break, minibus, ludospace, coupe, cabriolet, monospace]
        required: false
        description: Type de carrosserie
      - name: type_boite
        in: query
        type: string
        enum: [automatique, manuelle]
        required: false
        description: Type de boîte de vitesses
      - name: gamme
        in: query
        type: string
        enum: [economique, inferieure, moyenne_inferieure, moyenne_superieure, superieure, luxe]
        required: false
        description: Gamme du véhicule
      - name: prix_max
        in: query
        type: integer
        required: false
        description: Prix médian maximum en euros
      - name: puissance_min
        in: query
        type: integer
        required: false
        description: Puissance minimale en chevaux (ch)
    responses:
      200:
        description: Liste des véhicules correspondants et nombre total de résultats
    """
    service = VehiculeService()

    filters = {
        "marque": request.args.get("marque"),
        "famille_energie": request.args.get("famille_energie"),
        "carrosserie": request.args.get("carrosserie"),
        "type_boite": request.args.get("type_boite"),
        "gamme": request.args.get("gamme"),
        "prix_max": request.args.get("prix_max", type=int),
        "puissance_min": request.args.get("puissance_min", type=int),
    }

    if any(val is not None and val != "" for val in filters.values()):
        vehicules = service.searchVehicules(filters)
    else:
        vehicules = service.getAllVehicules()

    return jsonify({
        "count": len(vehicules),
        "vehicules": vehicules
    }), 200


@vehicule_bp.route("/<int:vehicule_id>", methods=["GET"])
def get_vehicule_by_id(vehicule_id: int):
    """
    Récupère le détail complet d'un véhicule par son ID
    ---
    tags:
      - Véhicules
    parameters:
      - name: vehicule_id
        in: path
        type: integer
        required: true
        default: 481
        description: Identifiant unique du véhicule (ex. 481 pour Peugeot e-208)
    responses:
      200:
        description: Objet véhicule complet au format JSON regroupé
      404:
        description: Véhicule introuvable
    """
    service = VehiculeService()
    vehicule = service.getVehiculeById(vehicule_id)

    if vehicule is None:
        return jsonify({"error": f"Véhicule avec l'id {vehicule_id} introuvable."}), 404

    return jsonify(vehicule), 200