from flask import Blueprint, jsonify, request
from app.models import Feature, User, Plugin
from app.extensions import db

api = Blueprint('api', __name__)

@api.route('/api/v1/features', methods=['GET'])
def get_features():
    """Get all features with optional filtering"""
    features = Feature.query.all()
    return jsonify([feature.to_dict() for feature in features])

@api.route('/api/v1/features/<int:id>', methods=['GET'])
def get_feature(id):
    """Get a specific feature by ID"""
    feature = Feature.query.get_or_404(id)
    return jsonify(feature.to_dict())

@api.route('/api/v1/features', methods=['POST'])
def create_feature():
    """Create a new feature"""
    data = request.get_json()
    feature = Feature(**data)
    db.session.add(feature)
    db.session.commit()
    return jsonify(feature.to_dict()), 201

@api.route('/api/v1/webhooks', methods=['POST'])
def register_webhook():
    """Register a new webhook endpoint"""
    data = request.get_json()
    webhook = Webhook(
        url=data['url'],
        events=data['events'],
        secret=data.get('secret')
    )
    db.session.add(webhook)
    db.session.commit()
    return jsonify(webhook.to_dict()), 201

@api.route('/api/v1/plugins', methods=['GET'])
def get_plugins():
    """Get all available plugins"""
    plugins = Plugin.query.all()
    return jsonify([plugin.to_dict() for plugin in plugins])