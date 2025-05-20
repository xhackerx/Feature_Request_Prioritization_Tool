from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from .ml.priority_predictor import PriorityPredictor
from .ml.feature_clusterer import FeatureClusterer

db = SQLAlchemy()
predictor = PriorityPredictor()
clusterer = FeatureClusterer()

class FeatureRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_impact = db.Column(db.Integer, nullable=False)  # Scale 1-10
    effort_required = db.Column(db.Integer, nullable=False)  # Scale 1-10
    strategic_alignment = db.Column(db.Integer, nullable=False)  # Scale 1-10
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    priority_score = db.Column(db.Float)

    def calculate_priority_score(self):
        # Get ML prediction
        prediction = predictor.predict_priority(self)
        
        # Combine ML prediction with rule-based score
        rule_based_score = self._calculate_rule_based_score()
        
        # Weight between ML and rule-based (adjustable)
        ml_weight = 0.7
        rule_weight = 0.3
        
        self.priority_score = (
            prediction['predicted_score'] * ml_weight +
            rule_based_score * rule_weight
        )
        
        return self.priority_score
    
    def _calculate_rule_based_score(self):
        # Original scoring logic
        impact_weight = 0.4
        effort_weight = 0.3
        strategic_weight = 0.3
        
        effort_score = (11 - self.effort_required)
        
        return (
            (self.user_impact * impact_weight) +
            (effort_score * effort_weight) +
            (self.strategic_alignment * strategic_weight)
        ) * 10
    
    @classmethod
    def find_similar_requests(cls, description):
        """Find similar feature requests"""
        existing_features = cls.query.all()
        return clusterer.find_similar_features(description, existing_features)
    
    @classmethod
    def get_feature_clusters(cls):
        """Get clustered feature requests"""
        features = cls.query.all()
        return clusterer.cluster_features(features)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)