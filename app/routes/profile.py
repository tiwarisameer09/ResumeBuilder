from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import MasterProfile, Education
from app.forms import BaseProfileForm, EducationForm
from app.utils.sanitizer import sanitize_text

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

@profile_bp.route("/")
@login_required
def view_profile():
    profile = current_user.profile
    if not profile:
        return redirect(url_for("profile.edit_profile"))
    return render_template("dashboard/edit_profile.html", profile=profile, form=BaseProfileForm(obj=profile))

@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    profile = current_user.profile
    if not profile:
        profile = MasterProfile(user_id=current_user.id, full_name="Your Name", email=current_user.email)
        db.session.add(profile)
        db.session.commit()

    form = BaseProfileForm(obj=profile)
    if form.validate_on_submit():
        profile.full_name = sanitize_text(form.full_name.data)
        profile.email = sanitize_text(form.email.data)
        profile.phone = sanitize_text(form.phone.data)
        profile.location = sanitize_text(form.location.data)
        profile.linkedin_url = sanitize_text(form.linkedin_url.data)
        profile.github_url = sanitize_text(form.github_url.data)
        profile.portfolio_url = sanitize_text(form.portfolio_url.data)
        db.session.commit()
        flash("Master Profile updated successfully.", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("dashboard/edit_profile.html", form=form, profile=profile)

@profile_bp.route("/education/add", methods=["GET", "POST"])
@login_required
def add_master_education():
    profile = current_user.profile
    if not profile:
        flash("Please complete your profile first.", "info")
        return redirect(url_for("profile.edit_profile"))

    form = EducationForm()
    if form.validate_on_submit():
        edu = Education(
            profile_id=profile.id,
            institution=sanitize_text(form.institution.data),
            degree=sanitize_text(form.degree.data),
            field_of_study=sanitize_text(form.field_of_study.data),
            graduation_year=sanitize_text(form.graduation_year.data),
            gpa=sanitize_text(form.gpa.data),
        )
        db.session.add(edu)
        db.session.commit()
        flash("Education added to Master Profile.", "success")
        return redirect(url_for("profile.edit_profile"))

    return render_template("resume/entry_form.html", form=form, title="Add Master Profile Education")
