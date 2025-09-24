# StreamEvents
Projecte de 2n de Desenvolupament d'aplicacions Web (DAW). Consisteix en una aplicació Django per gestionar esdeveniments i usuaris.
## ✨ Objectius
- Practicar un projecte de Django modular.
- Treballar amb un usuari personalitzat.
- Organitzar templates, estàtics i media correctament.
- Introduir fitxers d'entorn (.env) i bones pràctiques Git.
- Preparar el terreny per a futures funcionalitats (API, auth avançada, etc.).

## 🧱 Stack Principal
- Python
- Django
- MongoDB
- HTML / CSS / JS

## 📂 Estructura Simplificada
streamevents/
    manage.py
    config/
    users/
    templates/
    static/
    media/
    fixtures/
    seeds/
    .env
    .env.example
    README.md
    requirements.txt

## ✅ Requisits previs
- Python instal·lat
- pip i virtualenv
- MongoDB instal·lat

## 🚀 Instal·lació ràpida
git clone <REPO_URL>
cd streamevents
python -m venv venv
venv\Scripts\activate # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
python manage.py migrate
python manage.py runserver

Obre: http://127.0.0.1:8000/

## 🔐 Variables d'entorn (env.example)
SECRET_KEY=your_secret_key_here
DEBUG=0
ALLOWED_HOSTS=allowed_hosts_here
MONGO_URL=mongodb://url_mongo
DB_NAME=your_database_name

## 👤 Superusuari
python manage.py createsuperuser

Panell admin: /admin/

## 🗃️ Migrar a MongoDB (opcional futur)
## 🛠️ Comandes útils
python manage.py makemigrations
python manage.py migrate
python manage.py shell
python manage.py collectstatic   # (en producció)

## 💾 Fixtures (exemple)
## 🌱 Seeds (exemple d'script)
