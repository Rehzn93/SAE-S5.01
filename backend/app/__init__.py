from flask import Flask 
from flask_cors import CORS 

def create_app() :
    app = Flask(__name__, static_url_path='/static')

    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user_sae:password_sae@localhost:5432/vehicules_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    
    # Route de test basique pour vérifier que le serveur répond
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {"status": "success", "message": "Backend Flask opérationnel !"}, 200

    return app