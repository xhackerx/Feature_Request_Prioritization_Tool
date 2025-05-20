from app import create_app, db
from app.models import FeatureRequest

def create_sample_data():
    app = create_app()
    with app.app_context():
        # Clear existing data
        FeatureRequest.query.delete()
        
        # Sample feature requests
        features = [
            {
                'title': 'Dark Mode Support',
                'description': 'Add dark mode theme support for better night viewing',
                'user_impact': 8,
                'effort_required': 4,
                'strategic_alignment': 7
            },
            {
                'title': 'Export to CSV',
                'description': 'Allow users to export feature lists to CSV format',
                'user_impact': 6,
                'effort_required': 3,
                'strategic_alignment': 5
            },
            {
                'title': 'Mobile App',
                'description': 'Create mobile app version for on-the-go access',
                'user_impact': 9,
                'effort_required': 8,
                'strategic_alignment': 9
            }
        ]
        
        for feature_data in features:
            feature = FeatureRequest(**feature_data)
            feature.calculate_priority_score()
            db.session.add(feature)
        
        db.session.commit()

if __name__ == '__main__':
    create_sample_data()