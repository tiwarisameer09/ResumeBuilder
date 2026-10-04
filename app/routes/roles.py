from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import JobRoleResume
from app.forms import JobRoleResumeForm
from app.utils.sanitizer import sanitize_text

roles_bp = Blueprint("roles", __name__, url_prefix="/roles")

@roles_bp.route("/")
@login_required
def index():
    resumes = JobRoleResume.query.filter_by(user_id=current_user.id, is_archived=False).all()
    return render_template("dashboard/index.html", resumes=resumes, profile=current_user.profile)

@roles_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_role():
    form = JobRoleResumeForm()
    if form.validate_on_submit():
        resume = JobRoleResume(
            user_id=current_user.id,
            target_role_title=sanitize_text(form.target_role_title.data),
            target_industry=sanitize_text(form.target_industry.data),
            summary=sanitize_text(form.summary.data),
            selected_style=form.selected_style.data
        )
        db.session.add(resume)
        db.session.commit()
        flash(f"Created workspace for role: {resume.target_role_title}", "success")
        return redirect(url_for("resume.editor", resume_id=resume.id))

    return render_template("dashboard/edit_role.html", form=form, title="Create Prospective Role")

@roles_bp.route("/<int:role_id>/edit", methods=["GET", "POST"])
@login_required
def edit_role(role_id):
    resume = JobRoleResume.query.get_or_404(role_id)
    if resume.user_id != current_user.id:
        abort(403)

    form = JobRoleResumeForm(obj=resume)
    if form.validate_on_submit():
        resume.target_role_title = sanitize_text(form.target_role_title.data)
        resume.target_industry = sanitize_text(form.target_industry.data)
        resume.summary = sanitize_text(form.summary.data)
        resume.selected_style = form.selected_style.data
        db.session.commit()
        flash("Role updated successfully.", "success")
        return redirect(url_for("resume.editor", resume_id=resume.id))

    return render_template("dashboard/edit_role.html", form=form, title=f"Edit {resume.target_role_title}")

@roles_bp.route("/<int:role_id>/delete", methods=["POST"])
@login_required
def delete_role(role_id):
    resume = JobRoleResume.query.get_or_404(role_id)
    if resume.user_id != current_user.id:
        abort(403)

    role_title = resume.target_role_title
    db.session.delete(resume)
    db.session.commit()
    flash(f"Deleted prospective role: {role_title}", "info")
    return redirect(url_for("dashboard.index"))
