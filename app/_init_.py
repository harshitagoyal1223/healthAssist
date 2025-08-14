from flask import Flask
from flask_cors import CORS
from model import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
    app.config['SECRET_KEY'] = 'secret'

    CORS(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app
