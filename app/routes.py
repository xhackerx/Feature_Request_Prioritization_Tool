from flask import Blueprint, render_template, jsonify, request
from .models import db, FeatureRequest
from . import socketio
from datetime import datetime  # Add this import

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/features', methods=['GET'])
def get_features():
    features = FeatureRequest.query.all()
    return jsonify([feature.to_dict() for feature in features])

@main.route('/api/features', methods=['POST'])
def create_feature():
    data = request.json
    feature = FeatureRequest(
        title=data['title'],
        description=data['description'],
        user_impact=int(data['user_impact']),
        effort_required=int(data['effort_required']),
        strategic_alignment=int(data['strategic_alignment'])
    )
    db.session.add(feature)
    db.session.commit()
    return jsonify(feature.to_dict())

@main.route('/api/features/<int:feature_id>/vote', methods=['POST'])
def vote_feature(feature_id):
    feature = FeatureRequest.query.get_or_404(feature_id)
    vote_type = request.json.get('vote')
    
    # Update vote count in MongoDB
    from .models.mongo_manager import mongo
    vote_data = {
        'feature_id': feature_id,
        'vote_type': vote_type,
        'timestamp': datetime.utcnow()
    }
    mongo.db.votes.insert_one(vote_data)
    
    # Get total votes
    up_votes = mongo.db.votes.count_documents({'feature_id': feature_id, 'vote_type': 'up'})
    down_votes = mongo.db.votes.count_documents({'feature_id': feature_id, 'vote_type': 'down'})
    
    return jsonify({'votes': up_votes - down_votes})

@main.route('/api/features/<int:feature_id>', methods=['DELETE'])
def delete_feature(feature_id):
    feature = FeatureRequest.query.get_or_404(feature_id)
    feature.delete()
    socketio.emit('feature_deleted', {'feature_id': feature_id}, to='/')
    return jsonify({'success': True})