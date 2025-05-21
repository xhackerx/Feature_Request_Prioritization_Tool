from pymongo import MongoClient
from datetime import datetime
import json

class MongoManager:
    def __init__(self, app=None):
        self.client = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize MongoDB connection"""
        mongo_uri = app.config.get('MONGODB_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(mongo_uri)
        self.db = self.client['feature_requests']
        
        # Create indexes
        self.db.analysis_results.create_index('feature_id')
        self.db.user_feedback.create_index('feature_id')
        self.db.feature_history.create_index([('feature_id', 1), ('timestamp', -1)])

    def store_analysis_results(self, feature_id, analysis_data):
        """Store ML analysis results"""
        analysis_data['feature_id'] = feature_id
        analysis_data['timestamp'] = datetime.utcnow()
        
        return self.db.analysis_results.insert_one(analysis_data)

    def get_analysis_history(self, feature_id):
        """Get analysis history for a feature"""
        return list(self.db.analysis_results.find(
            {'feature_id': feature_id},
            {'_id': 0}
        ).sort('timestamp', -1))

    def store_user_feedback(self, feature_id, feedback_data):
        """Store user feedback"""
        feedback_data['feature_id'] = feature_id
        feedback_data['timestamp'] = datetime.utcnow()
        
        return self.db.user_feedback.insert_one(feedback_data)

    def get_user_feedback(self, feature_id):
        """Get all user feedback for a feature"""
        return list(self.db.user_feedback.find(
            {'feature_id': feature_id},
            {'_id': 0}
        ).sort('timestamp', -1))

    def track_feature_changes(self, feature_id, changes, user_id=None):
        """Track feature changes history"""
        history_entry = {
            'feature_id': feature_id,
            'changes': changes,
            'user_id': user_id,
            'timestamp': datetime.utcnow()
        }
        
        return self.db.feature_history.insert_one(history_entry)

    def get_feature_history(self, feature_id):
        """Get complete history of feature changes"""
        return list(self.db.feature_history.find(
            {'feature_id': feature_id},
            {'_id': 0}
        ).sort('timestamp', -1))

    def store_ml_metrics(self, feature_id, metrics_data):
        """Store ML model metrics"""
        metrics_data['feature_id'] = feature_id
        metrics_data['timestamp'] = datetime.utcnow()
        
        return self.db.ml_metrics.insert_one(metrics_data)

    def aggregate_feature_metrics(self, feature_id):
        """Aggregate metrics for a feature"""
        pipeline = [
            {'$match': {'feature_id': feature_id}},
            {'$group': {
                '_id': '$feature_id',
                'avg_priority_score': {'$avg': '$priority_score'},
                'avg_impact_score': {'$avg': '$impact_score'},
                'total_feedback_count': {'$sum': 1}
            }}
        ]
        return list(self.db.ml_metrics.aggregate(pipeline))