from . import db
from datetime import datetime

class FeatureRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_impact = db.Column(db.Integer, nullable=False)
    effort_required = db.Column(db.Integer, nullable=False)
    strategic_alignment = db.Column(db.Integer, nullable=False)
    priority_score = db.Column(db.Float, default=0.0)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, title, description, user_impact, effort_required, strategic_alignment):
        self.title = title
        self.description = description
        self.user_impact = user_impact
        self.effort_required = effort_required
        self.strategic_alignment = strategic_alignment
        self.calculate_priority_score()
    
    def calculate_priority_score(self):
        """Calculate priority score based on impact, effort, and alignment"""
        self.priority_score = (
            (self.user_impact * 0.4) +
            (self.strategic_alignment * 0.4) +
            ((10 - self.effort_required) * 0.2)
        )
        return self.priority_score
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'user_impact': self.user_impact,
            'effort_required': self.effort_required,
            'strategic_alignment': self.strategic_alignment,
            'priority_score': self.priority_score,
            'created_date': self.created_date.isoformat()
        }