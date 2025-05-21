from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import Config
from .models import db
from .cache import init_redis
from .models.mongo_manager import MongoManager

socketio = SocketIO()

from .models.mongo_manager import MongoManager

mongo = MongoManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    socketio.init_app(app)
    mongo.init_app(app)
    
    # Add Redis configuration
    app.config['REDIS_URL'] = 'redis://localhost:6379/0'
    
    db.init_app(app)
    socketio.init_app(app)
    init_redis(app)
    
    from .routes import main
    app.register_blueprint(main)
    
    with app.app_context():
        db.create_all()
    
    return app