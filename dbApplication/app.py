from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from Routes.loan_routes import register_routes
from Models.dbModel import db
from Routes.image_routes import image_routes 
from Routes.text_routes import text_routes
from Routes.movies_routes import movies_bp


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./testdb.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, suppresses warnings

    db.init_app(app)  # Bind SQLAlchemy to the app

    register_routes(app, db)
    app.register_blueprint(image_routes, url_prefix='/images')
    app.register_blueprint(text_routes, url_prefix='/text')
    app.register_blueprint(movies_bp, url_prefix='/movies')
    

    migrate = Migrate(app, db)  # Initialize Flask-Migrate

    return app
