from datetime import datetime
from app.extensions import db

class JobRoleResume(db.Model):
    __tablename__ = "job_role_resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    target_role_title = db.Column(db.String(120), nullable=False)
    target_industry = db.Column(db.String(120), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    selected_style = db.Column(db.String(20), default="modern")  # modern, minimalist, executive
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    experiences = db.relationship("Experience", backref="resume", cascade="all, delete-orphan", order_by="desc(Experience.start_date)")
    educations = db.relationship("Education", backref="resume", cascade="all, delete-orphan", foreign_keys="Education.resume_id")
    projects = db.relationship("Project", backref="resume", cascade="all, delete-orphan")
    skills = db.relationship("Skill", backref="resume", cascade="all, delete-orphan")

    @property
    def role_title(self):
        return self.target_role_title

    @role_title.setter
    def role_title(self, val):
        self.target_role_title = val

    @property
    def custom_summary(self):
        return self.summary

    @custom_summary.setter
    def custom_summary(self, val):
        self.summary = val


class Experience(db.Model):
    __tablename__ = "experiences"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("job_role_resumes.id"), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=True)
    is_current = db.Column(db.Boolean, default=False)
    bullet_points = db.Column(db.Text, nullable=False)

    @property
    def role_id(self):
        return self.resume_id


class Education(db.Model):
    __tablename__ = "educations"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("master_profiles.id"), nullable=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("job_role_resumes.id"), nullable=True)
    institution = db.Column(db.String(120), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    field_of_study = db.Column(db.String(100), nullable=True)
    graduation_year = db.Column(db.String(20), nullable=False)
    gpa = db.Column(db.String(20), nullable=True)

    @property
    def graduation_date(self):
        return self.graduation_year

    @property
    def gpa_or_grade(self):
        return self.gpa


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("job_role_resumes.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    technologies = db.Column(db.String(150), nullable=True)
    link = db.Column(db.String(255), nullable=True)
    bullet_points = db.Column(db.Text, nullable=False)

    @property
    def tech_stack(self):
        return self.technologies

    @property
    def live_url(self):
        return self.link


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("job_role_resumes.id"), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., Languages, Frameworks, Tools
    items = db.Column(db.Text, nullable=False)  # e.g., "Python, Go, JavaScript"
