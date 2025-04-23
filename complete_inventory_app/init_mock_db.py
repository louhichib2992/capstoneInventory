import os
from app import create_app


# Conditional import of database
if os.getenv('FLASK_ENV') == 'pos':
    from src.utils.db_utils import db
else:
    from extensions import db

app = create_app()

with app.app_context():
    db.create_all()
    print(" look at you go you did something simple")
