from flask import Flask
from extensions import db

def create_app():
    app = Flask(__name__)

    app.secret_key = 'ohsosuperdupersecretkey777'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mock_inventory.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from routes import inventory_bp
    app.register_blueprint(inventory_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
