import os
from flask import Blueprint, render_template, make_response, abort, current_app, redirect, url_for, session, request, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import JobRoleResume

export_bp = Blueprint("export", __name__, url_prefix="/export")

def split_lines_helper(s):
    if not s:
        return []
    return [line.strip() for line in s.split("\n") if line.strip()]

@export_bp.route("/preview/<int:resume_id>/<style>")
@login_required
def preview_html(resume_id, style):
    resume = JobRoleResume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)
    
    if style not in ["modern", "minimalist", "executive"]:
        abort(404)

    return render_template(
        f"resumes/{style}.html",
        resume=resume,
        profile=current_user.profile,
        split_lines=split_lines_helper,
        is_preview=True
    )

@export_bp.route("/<int:resume_id>/pdf/<style>")
@export_bp.route("/download/<int:resume_id>/<style>")
@login_required
def download_pdf(resume_id, style):
    resume = JobRoleResume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)

    if style not in ["modern", "minimalist", "executive"]:
        abort(404)

    # Monetization Paywall Check as per Specification Section 5:
    # can_download = (user.is_premium) or (user.download_credits > 0)
    if not current_user.can_download_pdf():
        session["target_resume_id"] = resume.id
        session["target_style"] = style
        flash("PDF export requires Pro Lifetime access or download credits.", "info")
        return redirect(url_for("billing.paywall", resume_id=resume.id, style=style))

    # Render template with profile & resume data
    rendered_html = render_template(
        f"resumes/{style}.html",
        resume=resume,
        profile=current_user.profile,
        split_lines=split_lines_helper,
        is_preview=False
    )

    clean_role = "".join(c for c in resume.target_role_title if c.isalnum() or c in ("-", "_")).rstrip()
    user_name = (current_user.profile.full_name if current_user.profile and current_user.profile.full_name else "Resume").replace(" ", "_")
    filename = f"{user_name}_{clean_role}_{style}.pdf"

    # Attempt PDF generation via WeasyPrint
    try:
        from weasyprint import HTML
        pdf = HTML(string=rendered_html).write_pdf()

        # Deduct credit if user is not lifetime premium
        current_user.consume_credit()
        db.session.commit()

        response = make_response(pdf)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        # Fallback for local environments without WeasyPrint GTK/Cairo native libraries
        current_app.logger.warning(f"WeasyPrint PDF generation fallback triggered: {e}")
        # Still consume credit if intended
        current_user.consume_credit()
        db.session.commit()

        # Return a printable HTML version with auto-print script
        printable_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{filename}</title>
            <script>
                window.onload = function() {{
                    window.print();
                }};
            </script>
        </head>
        <body style="margin: 0; padding: 0;">
            {rendered_html}
        </body>
        </html>
        """
        response = make_response(printable_html)
        response.headers["Content-Type"] = "text/html"
        return response