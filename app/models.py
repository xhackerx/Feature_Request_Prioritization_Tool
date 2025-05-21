from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from . import socketio
from .ml.priority_predictor import PriorityPredictor
from .ml.feature_clusterer import FeatureClusterer
from .ml.impact_predictor import ImpactPredictor
from .ml.sentiment_analyzer import SentimentAnalyzer
from .ml.effort_estimator import EffortEstimator
from .cache import cache_key, set_cache, get_cache, invalidate_cache
from .search.elastic_manager import ElasticManager
from .models.mongo_manager import MongoManager

db = SQLAlchemy()
predictor = PriorityPredictor()
clusterer = FeatureClusterer()
impact_predictor = ImpactPredictor()
sentiment_analyzer = SentimentAnalyzer()
effort_estimator = EffortEstimator()
elastic = ElasticManager()

mongo = MongoManager()

class FeatureRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_impact = db.Column(db.Integer, nullable=False)  # Scale 1-10
    effort_required = db.Column(db.Integer, nullable=False)  # Scale 1-10
    strategic_alignment = db.Column(db.Integer, nullable=False)  # Scale 1-10
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    priority_score = db.Column(db.Float)
    user_base_size = db.Column(db.Integer, default=0)
    active_users_percent = db.Column(db.Float, default=0)
    market_demand = db.Column(db.Integer, default=0)
    competitor_presence = db.Column(db.Integer, default=0)
    user_feedback_score = db.Column(db.Float, default=0)
    predicted_impact = db.Column(db.Float)
    impact_confidence = db.Column(db.Float)
    complexity_score = db.Column(db.Integer, default=5)
    dependencies_count = db.Column(db.Integer, default=0)
    required_skills = db.Column(db.Integer, default=5)
    testing_requirements = db.Column(db.Integer, default=5)
    integration_complexity = db.Column(db.Integer, default=5)
    documentation_needs = db.Column(db.Integer, default=3)
    security_requirements = db.Column(db.Integer, default=3)
    performance_impact = db.Column(db.Integer, default=3)
    estimated_hours = db.Column(db.Float)
    effort_confidence = db.Column(db.Float)
    
    def estimate_effort(self):
        """Estimate implementation effort for this feature"""
        feature_data = {
            'complexity_score': self.complexity_score,
            'dependencies_count': self.dependencies_count,
            'required_skills': self.required_skills,
            'testing_requirements': self.testing_requirements,
            'integration_complexity': self.integration_complexity,
            'documentation_needs': self.documentation_needs,
            'security_requirements': self.security_requirements,
            'performance_impact': self.performance_impact
        }
        
        estimation = effort_estimator.predict_effort(feature_data)
        
        self.estimated_hours = estimation['estimated_hours']
        self.effort_confidence = estimation['confidence_score']
        
        return estimation
    
    def predict_user_impact(self):
        """Predict the user impact of this feature"""
        feature_data = {
            'user_base_size': self.user_base_size,
            'active_users_percent': self.active_users_percent,
            'feature_complexity': self.effort_required,
            'market_demand': self.market_demand,
            'competitor_presence': self.competitor_presence,
            'user_feedback_score': self.user_feedback_score,
            'strategic_alignment': self.strategic_alignment
        }
        
        prediction = impact_predictor.predict_impact(feature_data)
        
        self.predicted_impact = prediction['predicted_impact']
        self.impact_confidence = prediction['confidence_score']
        
        return prediction
    
    def calculate_priority_score(self):
        # First predict user impact
        impact_prediction = self.predict_user_impact()
        
        # Update user_impact based on prediction if confidence is high
        if impact_prediction['confidence_score'] > 70:
            self.user_impact = round(impact_prediction['predicted_impact'])
        
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
        
        # Invalidate cache after score update
        invalidate_cache('features:*')
        
        # Emit update event after priority score calculation
        socketio.emit('features_update', {
            'features': self.get_all_features()
        }, broadcast=True)
        
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
    sentiment = db.Column(db.String(20))
    sentiment_confidence = db.Column(db.Float)
    aspect_sentiments = db.Column(db.JSON)
    key_phrases = db.Column(db.JSON)
    
    def analyze_sentiment(self):
        """Analyze the sentiment of the feedback"""
        analysis = sentiment_analyzer.analyze_feedback(self.content)
        
        self.sentiment = analysis['overall_sentiment']
        self.sentiment_confidence = analysis['confidence']
        self.aspect_sentiments = analysis['aspects']
        self.key_phrases = analysis['key_phrases']
        
        return analysis
    
    @classmethod
    def get_sentiment_summary(cls):
        """Get summary of sentiment analysis for all feedback"""
        feedbacks = cls.query.all()
        
        summary = {
            'total_count': len(feedbacks),
            'sentiment_distribution': defaultdict(int),
            'aspect_summary': defaultdict(lambda: {
                'positive': 0,
                'negative': 0,
                'total': 0
            }),
            'top_phrases': defaultdict(int)
        }
        
        for feedback in feedbacks:
            summary['sentiment_distribution'][feedback.sentiment] += 1
            
            for aspect, data in feedback.aspect_sentiments.items():
                summary['aspect_summary'][aspect][data['sentiment'].lower()] += 1
                summary['aspect_summary'][aspect]['total'] += 1
            
            for phrase in feedback.key_phrases:
                summary['top_phrases'][phrase['phrase']] += 1
        
        return summary
    
    @classmethod
    def get_all_features(cls):
        """Get all features with caching"""
        cache_k = cache_key('features', 'all')
        features = get_cache(cache_k)
        
        if features is None:
            features = [
                {
                    'id': f.id,
                    'title': f.title,
                    'priority_score': f.priority_score,
                    'user_impact': f.user_impact,
                    'effort_required': f.effort_required,
                    'strategic_alignment': f.strategic_alignment
                } for f in cls.query.order_by(cls.priority_score.desc()).all()
            ]
            set_cache(cache_k, features)
        
        return features
    
    def save(self):
        """Save feature and invalidate cache"""
        db.session.add(self)
        db.session.commit()
        invalidate_cache('features:*')
        return self
    
    def save(self):
        """Save the feature and index it in Elasticsearch"""
        db.session.add(self)
        db.session.commit()
        elastic.index_feature(self)
        return self
    
    def delete(self):
        """Delete the feature and remove from Elasticsearch"""
        elastic.delete_feature(self.id)
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def search(cls, query, filters=None, sort_by=None):
        """Search features using Elasticsearch"""
        results = elastic.search_features(query, filters, sort_by)
        return [cls.query.get(hit['_id']) for hit in results]
    
    def save(self):
        """Save feature and track changes"""
        is_new = self.id is None
        
        if not is_new:
            old_data = FeatureRequest.query.get(self.id).to_dict()
        
        db.session.add(self)
        db.session.commit()
        
        if not is_new:
            # Track changes
            new_data = self.to_dict()
            changes = {
                k: {'old': old_data.get(k), 'new': v}
                for k, v in new_data.items()
                if old_data.get(k) != v
            }
            if changes:
                mongo.track_feature_changes(self.id, changes)
        
        return self
    
    def store_analysis(self, analysis_data):
        """Store analysis results in MongoDB"""
        return mongo.store_analysis_results(self.id, analysis_data)
    
    def get_analysis_history(self):
        """Get feature analysis history"""
        return mongo.get_analysis_history(self.id)
    
    def add_user_feedback(self, feedback_data):
        """Add user feedback"""
        return mongo.store_user_feedback(self.id, feedback_data)
    
    def get_user_feedback(self):
        """Get all user feedback"""
        return mongo.get_user_feedback(self.id)
    
    def get_change_history(self):
        """Get feature change history"""
        return mongo.get_feature_history(self.id)
    
    def store_ml_metrics(self, metrics):
        """Store ML metrics"""
        return mongo.store_ml_metrics(self.id, metrics)
    
    def get_aggregated_metrics(self):
        """Get aggregated metrics"""
        return mongo.aggregate_feature_metrics(self.id)