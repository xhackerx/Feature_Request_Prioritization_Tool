from flask import Blueprint, jsonify, request
from app.models import Feature, User, Plugin
from app.extensions import db
from ..cache import cache_key, set_cache, get_cache, invalidate_cache

api = Blueprint('api', __name__)

@api.route('/api/v1/features', methods=['GET'])
def get_features():
    """Get all features with caching"""
    return jsonify(FeatureRequest.get_all_features())

@api.route('/api/v1/features/<int:id>', methods=['GET'])
def get_feature(id):
    """Get a specific feature by ID with caching"""
    cache_k = cache_key('feature', id)
    feature_data = get_cache(cache_k)
    
    if feature_data is None:
        feature = Feature.query.get_or_404(id)
        feature_data = feature.to_dict()
        set_cache(cache_k, feature_data)
    
    return jsonify(feature_data)

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