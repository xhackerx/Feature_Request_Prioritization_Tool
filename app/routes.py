from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from .models import db, FeatureRequest, Feedback

main = Blueprint('main', __name__)

@main.route('/')
def index():
    features = FeatureRequest.query.order_by(FeatureRequest.priority_score.desc()).all()
    return render_template('dashboard.html', features=features)

@main.route('/feature/new', methods=['GET', 'POST'])
def new_feature():
    if request.method == 'POST':
        feature = FeatureRequest(
            title=request.form['title'],
            description=request.form['description'],
            user_impact=int(request.form['user_impact']),
            effort_required=int(request.form['effort_required']),
            strategic_alignment=int(request.form['strategic_alignment'])
        )
        feature.calculate_priority_score()
        
        db.session.add(feature)
        db.session.commit()
        return redirect(url_for('main.index'))
    
    return render_template('feature_form.html')

@main.route('/feedback', methods=['POST'])
def submit_feedback():
    feedback = Feedback(content=request.form['feedback'])
    db.session.add(feedback)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/api/features')
def api_features():
    features = FeatureRequest.query.all()
    return jsonify([{
        'id': f.id,
        'title': f.title,
        'priority_score': f.priority_score,
        'description': f.description,
        'user_impact': f.user_impact,
        'effort_required': f.effort_required,
        'strategic_alignment': f.strategic_alignment
    } for f in features])