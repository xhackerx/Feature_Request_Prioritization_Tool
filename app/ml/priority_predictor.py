from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np
import joblib
from datetime import datetime

class PriorityPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_columns = [
            'user_impact',
            'effort_required',
            'strategic_alignment',
            'reach',
            'confidence',
            'implementation_cost',
            'expected_revenue',
            'maintenance_cost'
        ]
    
    def prepare_features(self, feature_request):
        """Convert feature request into ML features"""
        features = np.array([
            feature_request.user_impact,
            feature_request.effort_required,
            feature_request.strategic_alignment,
            feature_request.reach if hasattr(feature_request, 'reach') else 0,
            feature_request.confidence if hasattr(feature_request, 'confidence') else 50,
            feature_request.implementation_cost if hasattr(feature_request, 'implementation_cost') else 0,
            feature_request.expected_revenue if hasattr(feature_request, 'expected_revenue') else 0,
            feature_request.maintenance_cost if hasattr(feature_request, 'maintenance_cost') else 0
        ]).reshape(1, -1)
        
        return self.scaler.transform(features)
    
    def train(self, feature_requests):
        """Train the model with historical feature requests"""
        X = []
        y = []
        
        for request in feature_requests:
            features = self.prepare_features(request)
            X.append(features[0])
            y.append(request.priority_score)
        
        X = np.array(X)
        y = np.array(y)
        
        self.model.fit(X, y)
        
    def predict_priority(self, feature_request):
        """Predict priority score for a new feature request"""
        features = self.prepare_features(feature_request)
        prediction = self.model.predict(features)[0]
        
        # Get feature importances
        importances = dict(zip(
            self.feature_columns,
            self.model.feature_importances_
        ))
        
        return {
            'predicted_score': prediction,
            'feature_importances': importances,
            'confidence_score': self.calculate_confidence(features)
        }
    
    def calculate_confidence(self, features):
        """Calculate confidence score for the prediction"""
        # Use the model's internal metrics to estimate confidence
        tree_predictions = [tree.predict(features) for tree in self.model.estimators_]
        confidence = 1 - np.std(tree_predictions) / np.mean(tree_predictions)
        return min(max(confidence * 100, 0), 100)
    
    def save_model(self, path='model.joblib'):
        """Save the trained model"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'timestamp': datetime.now()
        }
        joblib.dump(model_data, path)
    
    def load_model(self, path='model.joblib'):
        """Load a trained model"""
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']