from flask_socketio import emit
from . import socketio
from .models import FeatureRequest

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    features = FeatureRequest.query.all()
    emit('features_update', {'features': [feature.to_dict() for feature in features]})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_update')
def handle_update_request():
    features = FeatureRequest.query.all()
    emit('features_update', {'features': [feature.to_dict() for feature in features]}, broadcast=True)

@socketio.on('feature_deleted')
def handle_feature_delete(data):
    emit('feature_deleted', {'feature_id': data['feature_id']}, broadcast=True)