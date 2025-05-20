from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np
import joblib
from datetime import datetime

class EffortEstimator:
    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_columns = [
            'complexity_score',
            'dependencies_count',
            'required_skills',
            'testing_requirements',
            'integration_complexity',
            'documentation_needs',
            'security_requirements',
            'performance_impact'
        ]
    
    def prepare_features(self, feature_request):
        """Convert feature request into ML features"""
        features = np.array([
            feature_request.get('complexity_score', 5),
            feature_request.get('dependencies_count', 0),
            feature_request.get('required_skills', 5),
            feature_request.get('testing_requirements', 5),
            feature_request.get('integration_complexity', 5),
            feature_request.get('documentation_needs', 3),
            feature_request.get('security_requirements', 3),
            feature_request.get('performance_impact', 3)
        ]).reshape(1, -1)
        
        return self.scaler.transform(features)
    
    def train(self, feature_data_list, effort_hours):
        """Train the model with historical feature data"""
        X = []
        for data in feature_data_list:
            features = self.prepare_features(data)
            X.append(features[0])
        
        X = np.array(X)
        y = np.array(effort_hours)
        
        self.model.fit(X, y)
    
    def predict_effort(self, feature_request):
        """Predict implementation effort for a feature"""
        features = self.prepare_features(feature_request)
        prediction = self.model.predict(features)[0]
        
        # Get feature importances
        importances = dict(zip(
            self.feature_columns,
            self.model.feature_importances_
        ))
        
        # Calculate confidence and risk factors
        confidence = self._calculate_confidence(features)
        risk_factors = self._analyze_risk_factors(feature_request)
        
        return {
            'estimated_hours': round(prediction, 2),
            'confidence_score': confidence,
            'feature_importances': importances,
            'risk_factors': risk_factors,
            'team_composition': self._suggest_team_composition(feature_request),
            'timeline_breakdown': self._generate_timeline_breakdown(prediction)
        }
    
    def _calculate_confidence(self, features):
        """Calculate confidence score for the prediction"""
        tree_predictions = [tree.predict(features) for tree in self.model.estimators_]
        confidence = 1 - np.std(tree_predictions) / np.mean(tree_predictions)
        return min(max(confidence * 100, 0), 100)
    
    def _analyze_risk_factors(self, feature_request):
        """Analyze potential risk factors"""
        risks = []
        
        if feature_request.get('complexity_score', 0) > 7:
            risks.append({
                'type': 'high_complexity',
                'severity': 'high',
                'description': 'Complex implementation may lead to delays'
            })
            
        if feature_request.get('dependencies_count', 0) > 5:
            risks.append({
                'type': 'dependencies',
                'severity': 'medium',
                'description': 'Multiple dependencies increase integration risks'
            })
            
        if feature_request.get('security_requirements', 0) > 7:
            risks.append({
                'type': 'security',
                'severity': 'high',
                'description': 'High security requirements need careful implementation'
            })
            
        return risks
    
    def _suggest_team_composition(self, feature_request):
        """Suggest optimal team composition"""
        team = {
            'developers': self._calculate_developer_count(feature_request),
            'required_skills': self._identify_required_skills(feature_request),
            'recommended_roles': []
        }
        
        # Add recommended roles based on requirements
        if feature_request.get('security_requirements', 0) > 5:
            team['recommended_roles'].append('Security Engineer')
            
        if feature_request.get('integration_complexity', 0) > 5:
            team['recommended_roles'].append('Integration Specialist')
            
        if feature_request.get('testing_requirements', 0) > 5:
            team['recommended_roles'].append('QA Engineer')
            
        return team
    
    def _calculate_developer_count(self, feature_request):
        """Calculate recommended number of developers"""
        complexity = feature_request.get('complexity_score', 5)
        dependencies = feature_request.get('dependencies_count', 0)
        
        base_count = max(1, complexity // 3)
        additional = dependencies // 4
        
        return min(base_count + additional, 5)  # Cap at 5 developers
    
    def _identify_required_skills(self, feature_request):
        """Identify required technical skills"""
        skills = []
        
        if feature_request.get('integration_complexity', 0) > 5:
            skills.append('API Integration')
            
        if feature_request.get('security_requirements', 0) > 5:
            skills.append('Security Protocols')
            
        if feature_request.get('performance_impact', 0) > 5:
            skills.append('Performance Optimization')
            
        return skills
    
    def _generate_timeline_breakdown(self, total_hours):
        """Generate timeline breakdown for the implementation"""
        phases = {
            'planning': 0.1,
            'development': 0.5,
            'testing': 0.2,
            'documentation': 0.1,
            'deployment': 0.1
        }
        
        return {
            phase: round(total_hours * percentage, 2)
            for phase, percentage in phases.items()
        }
    
    def save_model(self, path='effort_model.joblib'):
        """Save the trained model"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'timestamp': datetime.now()
        }
        joblib.dump(model_data, path)
    
    def load_model(self, path='effort_model.joblib'):
        """Load a trained model"""
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']