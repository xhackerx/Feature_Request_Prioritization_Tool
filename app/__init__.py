from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import Config
from .models import db
from .cache import init_redis
from .models.mongo_manager import MongoManager

socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='threading',
    logger=True,
    engineio_logger=True
)
mongo = MongoManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Add Redis configuration
    app.config['REDIS_URL'] = 'redis://localhost:6379/0'
    
    # Initialize all extensions
    db.init_app(app)
    socketio.init_app(app)
    mongo.init_app(app)
    init_redis(app)
    
    from .routes import main
    app.register_blueprint(main)
    
    # Import and register Socket.IO event handlers
    from . import events
    
    with app.app_context():
        db.create_all()
    
    return app