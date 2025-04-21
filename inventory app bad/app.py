from flask import Flask, render_template, request, session, redirect, url_for
from extensions import db

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your-secret-key-here'  # Change this for production
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mock_inventory.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    from routes import inventory_bp
    app.register_blueprint(inventory_bp)
    
    # Add default route
    @app.route('/')
    def index():
        return redirect(url_for('inventory.login'))
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)