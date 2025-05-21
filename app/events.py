from flask_socketio import emit
from . import socketio
from .models import FeatureRequest, db

@socketio.on('connect')
def handle_connect():
    """Handle client connection using cached data"""
    emit('features_update', {
        'features': FeatureRequest.get_all_features()
    })

@socketio.on('request_update')
def handle_update_request():
    """Handle client request for feature updates using cached data"""
    emit('features_update', {
        'features': FeatureRequest.get_all_features()
    }, broadcast=True)