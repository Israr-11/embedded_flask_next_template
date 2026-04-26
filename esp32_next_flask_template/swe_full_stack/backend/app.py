from flask import Flask
from configuration.config import Config
from routes.user_routes import user_bp
from models.user_model import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(user_bp)
    
    @app.route('/')
    def home():
        return {"message": "Flask + PostgreSQL is working!"}
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Uncomment to create tables on startup
    # with app.app_context():
    #     db.create_all()
    
    app.run(debug=True)
