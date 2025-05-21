from flask_socketio import emit
from . import socketio
from .models import FeatureRequest, db

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    features = FeatureRequest.query.order_by(FeatureRequest.priority_score.desc()).all()
    emit('features_update', {
        'features': [
            {
                'id': f.id,
                'title': f.title,
                'priority_score': f.priority_score,
                'user_impact': f.user_impact,
                'effort_required': f.effort_required,
                'strategic_alignment': f.strategic_alignment
            } for f in features
        ]
    })

@socketio.on('request_update')
def handle_update_request():
    """Handle client request for feature updates"""
    features = FeatureRequest.query.order_by(FeatureRequest.priority_score.desc()).all()
    emit('features_update', {
        'features': [
            {
                'id': f.id,
                'title': f.title,
                'priority_score': f.priority_score,
                'user_impact': f.user_impact,
                'effort_required': f.effort_required,
                'strategic_alignment': f.strategic_alignment
            } for f in features
        ]
    }, broadcast=True)