from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import JobRoleResume, MasterProfile
from app.forms import BaseProfileForm, JobRoleResumeForm

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    resumes = JobRoleResume.query.filter_by(user_id=current_user.id, is_archived=False).all()
    return render_template("dashboard/index.html", resumes=resumes, profile=current_user.profile)

# Compatibility aliases
@dashboard_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    return redirect(url_for("profile.edit_profile"))

@dashboard_bp.route("/role/new", methods=["GET", "POST"])
@login_required
def create_role():
    return redirect(url_for("roles.create_role"))