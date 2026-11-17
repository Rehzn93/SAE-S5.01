import os
from flask import Flask 
from flask_cors import CORS 
from flasgger import Swagger

def create_app() :
    app = Flask(__name__, static_url_path='/static')

    CORS(app)

    # en local : la base Docker est sur localhost ; dans Docker, DATABASE_URL pointe vers le service "db"
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'postgresql://user_sae:password_sae@localhost:5432/vehicules_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SWAGGER'] = {
        'title': 'API Véhicules ADEME - SAE S5.01',
        'uiversion': 3,
        'description': 'Documentation interactive de l’API Backend (748 véhicules)'
    }

    Swagger(app)

    from app.blueprints import vehicule_bp, recommandation_bp
    app.register_blueprint(vehicule_bp)
    app.register_blueprint(recommandation_bp)
    
    
    # Route de test basique pour vérifier que le serveur répond
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """
        Vérifie l'état du serveur Backend
        ---
        tags:
          - Système
        responses:
          200:
            description: Le serveur Flask est opérationnel
        """
        return {"status": "success", "message": "Backend Flask opérationnel !"}, 200

    return app