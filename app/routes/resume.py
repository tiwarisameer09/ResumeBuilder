from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import JobRoleResume, Experience, Education, Project, Skill
from app.forms import JobRoleResumeForm, ExperienceForm, EducationForm, ProjectForm, SkillForm
from app.utils.sanitizer import sanitize_text

resume_bp = Blueprint("resume", __name__, url_prefix="/resume")

def get_user_resume_or_404(resume_id):
    resume = JobRoleResume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)
    return resume

@resume_bp.route("/<int:resume_id>/editor")
@login_required
def editor(resume_id):
    resume = get_user_resume_or_404(resume_id)
    return render_template("resume/editor.html", resume=resume)

@resume_bp.route("/<int:resume_id>/edit-meta", methods=["GET", "POST"])
@login_required
def edit_meta(resume_id):
    resume = get_user_resume_or_404(resume_id)
    form = JobRoleResumeForm(obj=resume)
    if form.validate_on_submit():
        resume.target_role_title = sanitize_text(form.target_role_title.data)
        resume.target_industry = sanitize_text(form.target_industry.data)
        resume.summary = sanitize_text(form.summary.data)
        resume.selected_style = form.selected_style.data
        db.session.commit()
        flash("Role details and style updated.", "success")
        return redirect(url_for("resume.editor", resume_id=resume.id))
    return render_template("dashboard/edit_role.html", form=form, title=f"Edit {resume.target_role_title}")

@resume_bp.route("/<int:resume_id>/update-style", methods=["POST"])
@login_required
def update_style(resume_id):
    resume = get_user_resume_or_404(resume_id)
    style = request.form.get("style") or (request.json and request.json.get("style"))
    if style in ["modern", "minimalist", "executive"]:
        resume.selected_style = style
        db.session.commit()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({"status": "success", "style": style})
        flash(f"Switched layout style to {style.capitalize()}.", "success")
    return redirect(url_for("resume.editor", resume_id=resume.id))

# --- Experience Endpoints ---
@resume_bp.route("/<int:resume_id>/experience/add", methods=["GET", "POST"])
@login_required
def add_experience(resume_id):
    resume = get_user_resume_or_404(resume_id)
    form = ExperienceForm()
    if form.validate_on_submit():
        exp = Experience(
            resume_id=resume.id,
            job_title=sanitize_text(form.job_title.data),
            company=sanitize_text(form.company.data),
            location=sanitize_text(form.location.data),
            start_date=sanitize_text(form.start_date.data),
            end_date="Present" if form.is_current.data else sanitize_text(form.end_date.data),
            is_current=form.is_current.data,
            bullet_points=sanitize_text(form.bullet_points.data)
        )
        db.session.add(exp)
        db.session.commit()
        flash("Experience entry added.", "success")
        return redirect(url_for("resume.editor", resume_id=resume.id))
    return render_template("resume/entry_form.html", form=form, title="Add Experience")

@resume_bp.route("/<int:resume_id>/experience/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit_experience(resume_id, entry_id):
    resume = get_user_resume_or_404(resume_id)
    exp = Experience.query.filter_by(id=entry_id, resume_id=resume.id).first_or_404()
    form = ExperienceForm(obj=exp)
    if form.validate_on_submit():
        exp.job_title = sanitize_text(form.job_title.data)
        exp.company = sanitize_text(form.company.data)
        exp.location = sanitize_text(form.location.data)
        exp.start_date = sanitize_text(form.start_date.data)
        exp.is_current = form.is_current.data
        exp.end_date = "Present" if form.is_current.data else sanitize_text(form.end_date.data)
        exp.bullet_points = sanitize_text(form.bullet_points.data)
        db.session.commit()
        flash("Experience updated.", "success")
        return redirect(url_for("resume.editor", resume_id=resume.id))
    return render_template("resume/entry_form.html", form=form, title="Edit Experience")

@resume_bp.route("/<int:resume_id>/experience/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_experience(resume_id, entry_id):
    resume = get_user_resume_or_404(resume_id)
    exp = Experience.query.filter_by(id=entry_id, resume_id=resume.id).first_or_404()
    db.session.delete(exp)
    db.session.commit()
    flash("Experience removed.", "info")
    return redirect(url_for("resume.editor", resume_id=resume.id))

# --- Education Endpoints ---
@resume_bp.route("/<int:resume_id>/education/add", methods=["GET", "POST"])
@login_required
def add_education(resume_id):
    resume = get_user_resume_or_404(resume_id)
    form = EducationForm()
    if form.validate_on_submit():
        edu = Education(
            resume_id=resume.id,
            institution=sanitize_text(form.institution.data),
            degree=sanitize_text(form.degree.data),
            field_of_study=sanitize_text(form.field_of_study.data),
            graduation_year=sanitize_text(form.graduation_year.data),
            gpa=sanitize_text(form.gpa.data)
        )
        db.session.add(edu)
        db.session.commit()
        flash("Education added.", "success")
        return redirect(url_for("resume.editor", resume_id=resume.id))
    return render_template("resume/entry_form.html", form=form, title="Add Education")

@resume_bp.route("/<int:resume_id>/education/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit_education(resume_id, entry_id):
    resume = get_user_resume_or_404(resume_id)
    edu = Education.query.filter_by(id=entry_id, resume_id=resume.id).first_or_404()
    form = EducationForm(obj=edu)
    if form.validate_on_submit():
        edu.institution = sanitize_text(form.institution.data)
        edu.degree = sanitize_text(form.degree.data)
        edu.field_of_study = sanitize_text(form.field_of_study.data)
        edu.graduation_year = sanitize_text(form.graduation_year.data)
        edu.gpa = sanitize_text(form.gpa.data)
        db.session.commit()
        flash("Education updated.", "success")
        return redirect(url_for("resume.editor", resume_id=resume.id))
    return render_template("resume/entry_form.html", form=form, title="Edit Education")

@resume_bp.route("/<int:resume_id>/education/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_education(resume_id, entry_id):
    resume = get_user_resume_or_404(resume_id)
    edu = Education.query.filter_by(id=entry_id, resume_id=resume.id).first_or_404()
    db.session.delete(edu)
    db.session.commit()
    flash("Education removed.", "info")
    return redirect(url_for("resume.editor", resume_id=resume.id))

# --- Project Endpoints ---
@resume_bp.route("/<int:resume_id>/project/add", methods=["GET", "POST"])
@login_required
def add_project(resume_id):
    resume = get_user_resume_or_404(resume_id)
    form = ProjectForm()
    if form.validate_on_submit():
        proj = Project(
            resume_id=resume.id,
            name=sanitize_text(form.name.data),
            technologies=sanitize_text(form.technologies.data),
            link=sanitize_text(form.link.data),
            bullet_points=sanitize_text(form.bullet_points.data)
        )
        db.session.add(proj)
        db.session.commit()
        flash("Project added.", "success")
        return redirect(url_for("resume.editor", resume_id=resume.id))
    return render_template("resume/entry_form.html", form=form, title="Add Project")

@resume_bp.route("/<int:resume_id>/project/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(resume_id, entry_id):
    resume = get_user_resume_or_404(resume_id)
    proj = Project.query.filter_by(id=entry_id, resume_id=resume.id).first_or_404()
    form = ProjectForm(obj=proj)
    if form.validate_on_submit():
        proj.name = sanitize_text(form.name.data)
        proj.technologies = sanitize_text(form.technologies.data)
        proj.link = sanitize_text(form.link.data)
        proj.bullet_points = sanitize_text(form.bullet_points.data)
        db.session.commit()
        flash("Project updated.", "success")
        return redirect(url_for("resume.editor", resume_id=resume.id))
    return render_template("resume/entry_form.html", form=form, title="Edit Project")

@resume_bp.route("/<int:resume_id>/project/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_project(resume_id, entry_id):
    resume = get_user_resume_or_404(resume_id)
    proj = Project.query.filter_by(id=entry_id, resume_id=resume.id).first_or_404()
    db.session.delete(proj)
    db.session.commit()
    flash("Project removed.", "info")
    return redirect(url_for("resume.editor", resume_id=resume.id))

# --- Skill Endpoints ---
@resume_bp.route("/<int:resume_id>/skill/add", methods=["GET", "POST"])
@login_required
def add_skill(resume_id):
    resume = get_user_resume_or_404(resume_id)
    form = SkillForm()
    if form.validate_on_submit():
        skill = Skill(
            resume_id=resume.id,
            category=sanitize_text(form.category.data),
            items=sanitize_text(form.items.data)
        )
        db.session.add(skill)
        db.session.commit()
        flash("Skill group added.", "success")
        return redirect(url_for("resume.editor", resume_id=resume.id))
    return render_template("resume/entry_form.html", form=form, title="Add Skill Category")

@resume_bp.route("/<int:resume_id>/skill/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit_skill(resume_id, entry_id):
    resume = get_user_resume_or_404(resume_id)
    skill = Skill.query.filter_by(id=entry_id, resume_id=resume.id).first_or_404()
    form = SkillForm(obj=skill)
    if form.validate_on_submit():
        skill.category = sanitize_text(form.category.data)
        skill.items = sanitize_text(form.items.data)
        db.session.commit()
        flash("Skill updated.", "success")
        return redirect(url_for("resume.editor", resume_id=resume.id))
    return render_template("resume/entry_form.html", form=form, title="Edit Skill Category")

@resume_bp.route("/<int:resume_id>/skill/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_skill(resume_id, entry_id):
    resume = get_user_resume_or_404(resume_id)
    skill = Skill.query.filter_by(id=entry_id, resume_id=resume.id).first_or_404()
    db.session.delete(skill)
    db.session.commit()
    flash("Skill removed.", "info")
    return redirect(url_for("resume.editor", resume_id=resume.id))