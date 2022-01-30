from datetime import timezone
from enum import unique
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(150))
    date_event = db.Column(db.String(15))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    role = db.Column(db.String(150))
    visit = db.relationship('Visit')