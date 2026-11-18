FROM python:3.12-slim

WORKDIR /app

# affiche les print() tout de suite dans les logs Docker
ENV PYTHONUNBUFFERED=1

# les dépendances d'abord : Docker garde cette étape en cache tant que requirements.txt ne change pas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# remplit la base (s'il n'y a encore aucun véhicule) puis lance l'API
CMD ["sh", "-c", "python prepa_db.py && python main.py"]
