from . import db
from datetime import datetime

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey('feature_request.id'), nullable=False)
    user_id = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'feature_id': self.feature_id,
            'user_id': self.user_id,
            'comment': self.comment,
            'rating': self.rating,
            'created_date': self.created_date.isoformat()
        }