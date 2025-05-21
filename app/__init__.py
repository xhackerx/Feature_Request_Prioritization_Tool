from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import Config
from .models import db

socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    socketio.init_app(app)
    
    from .routes import main
    app.register_blueprint(main)
    
    with app.app_context():
        db.create_all()
    
    return app