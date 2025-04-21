from app import create_app
from extensions import db

app = create_app()

with app.app_context():
    db.create_all()
    print(" look at you go you did something simple")