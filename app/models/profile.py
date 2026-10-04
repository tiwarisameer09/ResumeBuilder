from datetime import datetime
from app.extensions import db

class MasterProfile(db.Model):
    __tablename__ = "master_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)
    github_url = db.Column(db.String(255), nullable=True)
    portfolio_url = db.Column(db.String(255), nullable=True)

    educations = db.relationship("Education", backref="master_profile", cascade="all, delete-orphan", foreign_keys="Education.profile_id")

# Alias for backwards compatibility
BaseProfile = MasterProfile
