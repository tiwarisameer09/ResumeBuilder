from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    download_credits = db.Column(db.Integer, default=0)
    has_paid_access = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship("MasterProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    resumes = db.relationship("JobRoleResume", backref="user", cascade="all, delete-orphan")
    payments = db.relationship("Payment", backref="user", cascade="all, delete-orphan")

    @property
    def is_premium(self):
        return self.has_paid_access

    @is_premium.setter
    def is_premium(self, value):
        self.has_paid_access = bool(value)

    def can_download_pdf(self):
        return self.has_paid_access or (self.download_credits > 0)

    def consume_credit(self):
        """Consume a credit if not premium. Returns True if allowed, False otherwise."""
        if self.has_paid_access:
            return True
        if self.download_credits > 0:
            self.download_credits -= 1
            return True
        return False

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    stripe_session_id = db.Column(db.String(255), nullable=True)
    amount = db.Column(db.Integer, default=0)
    currency = db.Column(db.String(10), default="usd")
    status = db.Column(db.String(50), default="completed")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
