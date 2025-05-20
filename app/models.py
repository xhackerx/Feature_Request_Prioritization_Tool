from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
        # Priority scoring algorithm
        impact_weight = 0.4
        effort_weight = 0.3
        strategic_weight = 0.3
        
        # Effort is inverse (lower effort = higher score)
        effort_score = (11 - self.effort_required)
        
        self.priority_score = (
            (self.user_impact * impact_weight) +
            (effort_score * effort_weight) +
            (self.strategic_alignment * strategic_weight)
        ) * 10

        return self.priority_score

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)