from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .feature import FeatureRequest
from .feedback import Feedback