from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class RegisterForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create Account")

class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")

class BaseProfileForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Contact Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[Optional(), Length(max=20)])
    location = StringField("City, Country", validators=[Optional(), Length(max=100)])
    linkedin_url = StringField("LinkedIn Profile URL", validators=[Optional()])
    github_url = StringField("GitHub Profile URL", validators=[Optional()])
    portfolio_url = StringField("Portfolio URL", validators=[Optional()])
    submit = SubmitField("Save Profile")

# Alias
MasterProfileForm = BaseProfileForm

class JobRoleResumeForm(FlaskForm):
    target_role_title = StringField("Target Job Role (e.g. Backend Engineer)", validators=[DataRequired()])
    target_industry = StringField("Target Industry (e.g. FinTech, Healthcare, E-Commerce)", validators=[Optional()])
    summary = TextAreaField("Professional Summary (Tailored for this role)", validators=[Optional()])
    selected_style = SelectField("Template Style", choices=[
        ("modern", "Modern (Two Column with Accent Sidebar)"),
        ("minimalist", "Minimalist (Clean Single Column)"),
        ("executive", "Executive (Classic Formal Serif)")
    ], default="modern")
    submit = SubmitField("Save Role")

class ExperienceForm(FlaskForm):
    job_title = StringField("Job Title", validators=[DataRequired()])
    company = StringField("Company", validators=[DataRequired()])
    location = StringField("Location", validators=[Optional()])
    start_date = StringField("Start Date (e.g., Jun 2024)", validators=[DataRequired()])
    end_date = StringField("End Date (leave blank if current)", validators=[Optional()])
    is_current = BooleanField("Currently working here", default=False)
    bullet_points = TextAreaField("Accomplishments (1 bullet point per line)", validators=[DataRequired()])
    submit = SubmitField("Save Experience")

class EducationForm(FlaskForm):
    institution = StringField("Institution / University", validators=[DataRequired()])
    degree = StringField("Degree", validators=[DataRequired()])
    field_of_study = StringField("Major / Field of Study", validators=[Optional()])
    graduation_year = StringField("Graduation Year / Date", validators=[DataRequired()])
    gpa = StringField("GPA / Percentage / Grade", validators=[Optional()])
    submit = SubmitField("Save Education")

class ProjectForm(FlaskForm):
    name = StringField("Project Name", validators=[DataRequired()])
    technologies = StringField("Tech Stack Used", validators=[Optional()])
    link = StringField("Live Link / GitHub", validators=[Optional()])
    bullet_points = TextAreaField("Key Outcomes (1 bullet point per line)", validators=[DataRequired()])
    submit = SubmitField("Save Project")

class SkillForm(FlaskForm):
    category = StringField("Category (e.g., Languages, Frameworks, Cloud, Tools)", validators=[DataRequired()])
    items = StringField("Skills (Comma separated, e.g. Python, Docker, PostgreSQL)", validators=[DataRequired()])
    submit = SubmitField("Save Skills")