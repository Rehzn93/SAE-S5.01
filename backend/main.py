import os
from app import create_app

app = create_app()

if __name__ == '__main__' :
    # dans Docker, FLASK_HOST=0.0.0.0 pour que l'API soit joignable depuis l'extérieur du conteneur
    app.run(host=os.environ.get("FLASK_HOST", "localhost"), port=8000, debug=True)
