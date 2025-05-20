from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
import numpy as np
import joblib
from datetime import datetime

class ImpactPredictor:
    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_columns = [
            'user_base_size',
            'active_users_percent',
            'feature_complexity',
            'market_demand',
            'competitor_presence',
            'user_feedback_score',
            'strategic_alignment'
        ]
    
    def prepare_features(self, feature_data):
        """Convert feature request data into ML features"""
        features = np.array([
            feature_data.get('user_base_size', 0),
            feature_data.get('active_users_percent', 0),
            feature_data.get('feature_complexity', 5),
            feature_data.get('market_demand', 0),
            feature_data.get('competitor_presence', 0),
            feature_data.get('user_feedback_score', 0),
            feature_data.get('strategic_alignment', 5)
        ]).reshape(1, -1)
        
        return self.scaler.transform(features)
    
    def train(self, feature_data_list, impact_scores):
        """Train the model with historical feature data"""
        X = []
        for data in feature_data_list:
            features = self.prepare_features(data)
            X.append(features[0])
        
        X = np.array(X)
        y = np.array(impact_scores)
        
        self.model.fit(X, y)
    
    def predict_impact(self, feature_data):
        """Predict user impact for a new feature"""
        features = self.prepare_features(feature_data)
        prediction = self.model.predict(features)[0]
        
        # Get feature importances
        importances = dict(zip(
            self.feature_columns,
            self.model.feature_importances_
        ))
        
        # Calculate confidence score
        confidence = self._calculate_confidence(features)
        
        return {
            'predicted_impact': prediction,
            'feature_importances': importances,
            'confidence_score': confidence,
            'supporting_metrics': self._get_supporting_metrics(feature_data)
        }
    
    def _calculate_confidence(self, features):
        """Calculate confidence score for the prediction"""
        tree_predictions = [tree.predict(features) for tree in self.model.estimators_]
        confidence = 1 - np.std(tree_predictions) / np.mean(tree_predictions)
        return min(max(confidence * 100, 0), 100)
    
    def _get_supporting_metrics(self, feature_data):
        """Calculate additional supporting metrics"""
        return {
            'market_potential': self._calculate_market_potential(feature_data),
            'user_satisfaction_impact': self._calculate_satisfaction_impact(feature_data),
            'competitive_advantage': self._calculate_competitive_advantage(feature_data)
        }
    
    def _calculate_market_potential(self, feature_data):
        """Calculate market potential score"""
        user_base = feature_data.get('user_base_size', 0)
        market_demand = feature_data.get('market_demand', 0)
        return (user_base * market_demand) / 100
    
    def _calculate_satisfaction_impact(self, feature_data):
        """Calculate user satisfaction impact score"""
        feedback_score = feature_data.get('user_feedback_score', 0)
        active_users = feature_data.get('active_users_percent', 0)
        return (feedback_score * active_users) / 100
    
    def _calculate_competitive_advantage(self, feature_data):
        """Calculate competitive advantage score"""
        competitor_presence = feature_data.get('competitor_presence', 0)
        strategic_alignment = feature_data.get('strategic_alignment', 0)
        return ((10 - competitor_presence) * strategic_alignment) / 10
    
    def save_model(self, path='impact_model.joblib'):
        """Save the trained model"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'timestamp': datetime.now()
        }
        joblib.dump(model_data, path)
    
    def load_model(self, path='impact_model.joblib'):
        """Load a trained model"""
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']