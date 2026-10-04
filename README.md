# ResumeBuilder: Production-Ready Modular Resume Engine

ResumeBuilder is a production-grade, modular Flask web application engineered to separate a student or developer's **Master Profile** (immutable baseline credentials) from **Prospective Roles** (tailored job-specific resumes).

It supports three print-optimized, ATS-compliant formats (**Modern**, **Minimalist**, and **Executive**), compiled server-side into vector PDFs via **WeasyPrint** and monetized through **Stripe** checkout and download credit authorization.

---

## 1. System Architecture

```
[ Browser / Client ]
        │  (HTTPS / Form Submissions / Fetch)
        ▼
[ Render Web Service: Gunicorn WSGI ]
        │
 ┌──────┴────────────────────────────────────────────────┐
 │ Flask Application Context                             │
 │                                                       │
 │  ├── Routing & Blueprints                             │
 │  │    ├── auth_bp      (Session / Registration)       │
 │  │    ├── profile_bp   (Master Academic Profile)      │
 │  │    ├── roles_bp     (Prospective Job Roles)        │
 │  │    ├── resume_bp    (Editor Workspace & Sections)  │
 │  │    ├── export_bp    (Jinja ➔ WeasyPrint ➔ PDF)     │
 │  │    └── billing_bp   (Stripe Webhooks & Credits)    │
 │  │                                                    │
 │  ├── Template Engine: Jinja2                          │
 │  │    ├── Modern (Asymmetric 2-Column with Accent)    │
 │  │    ├── Minimalist (Monochrome Inter Hierarchy)     │
 │  │    └── Executive (ATS Classic Serif Layout)        │
 │  │                                                    │
 │  └── Security & Sanitization                          │
 │       ├── Flask-WTF (CSRF protection on all POSTs)    │
 │       └── Bleach (HTML/XSS input sanitizer)           │
 └──────┬────────────────────────────────────────────────┘
        │
        ├── [ Render Managed PostgreSQL Database ]
        │
        └── [ External Payment Gateway: Stripe ]
```

---

## 2. Relational Database Schema

* **users**: Authentication, active status, download credit balance (`download_credits`), and Pro Lifetime entitlement (`has_paid_access`).
* **master_profiles**: Contact tokens and baseline identity (Full name, email, phone, location, LinkedIn, GitHub, portfolio).
* **job_role_resumes**: Tailored prospective job positions (`target_role_title`, `target_industry`, `summary`, `selected_style`).
* **experiences**: Role-specific work experience and accomplishments with newline bullet points.
* **projects**: Role-specific featured technical projects and outcomes.
* **educations**: Academic degree records associated with either Master Profile or tailored roles.
* **skills**: Categorized competency groups (e.g. Languages, Cloud, Frameworks).
* **payments**: Transaction history from Stripe checkout sessions.

---

## 3. Directory Layout

```
ResumeBuilder/
├── app/
│   ├── __init__.py                # App factory pattern: create_app()
│   ├── config.py                  # Dev, Test, Prod configuration classes
│   ├── extensions.py              # db, migrate, login_manager, csrf instances
│   ├── forms.py                   # WTForms validation definitions
│   ├── models/
│   │   ├── __init__.py            # Model re-exports & user_loader
│   │   ├── user.py                # User & Payment models
│   │   ├── profile.py             # MasterProfile model
│   │   └── resume.py              # JobRoleResume, Experience, Project, Skill, Education
│   ├── routes/
│   │   ├── __init__.py            # Blueprint registry
│   │   ├── auth.py                # /login, /register, /logout
│   │   ├── profile.py             # /profile (Master academic profile)
│   │   ├── roles.py               # /roles (CRUD prospective job roles)
│   │   ├── dashboard.py           # / (Dashboard overview)
│   │   ├── resume.py              # /resume/<id>/editor & full section CRUD
│   │   ├── export.py              # /export/<role_id>/pdf/<style> & live preview
│   │   └── billing.py             # /billing/paywall, /billing/checkout, /billing/webhook
│   ├── templates/
│   │   ├── base.html              # Layout shell with Tailwind and navigation
│   │   ├── auth/                  # login.html, register.html
│   │   ├── dashboard/             # index.html, edit_profile.html, edit_role.html
│   │   ├── resume/                # editor.html, entry_form.html
│   │   ├── resumes/               # _print_base.html, modern.html, minimalist.html, executive.html
│   │   └── billing/               # paywall.html, pricing.html, success.html
│   ├── static/
│   │   ├── css/
│   │   │   ├── app.css            # Custom application styles
│   │   │   └── resume_print.css   # @page rules & print media styling
│   │   └── js/
│   │       ├── dynamic_fields.js  # Interactive dynamic form controls
│   │       └── preview.js         # Real-time split-screen iframe handler
│   └── utils/
│       └── sanitizer.py           # Bleach input sanitization
├── Dockerfile                     # Bullseye container with WeasyPrint Cairo/Pango runtime
├── render.yaml                    # Infrastructure as Code blueprint for Render
├── requirements.txt               # Pinned Python package dependencies
├── wsgi.py                        # Gunicorn execution entrypoint
└── README.md
```

---

## 4. Local Development Setup

### 1. Clone & create virtual environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables (`.env`)
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-dev-secret-key
DATABASE_URL=sqlite:///dev.db

# Optional Stripe credentials (for payment testing):
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 4. Run the development server
```bash
python wsgi.py
```
Visit `http://localhost:5000` in your browser.

> **Tip:** If testing locally without Stripe API keys, the paywall includes a **Developer Testing Bypass** button to grant instant test credits or lifetime access.

---

## 5. Running with Docker

WeasyPrint requires native system libraries (`libpango`, `libharfbuzz`, `shared-mime-info`) which are pre-configured inside the `Dockerfile`:

```bash
# Build container image
docker build -t resumebuilder .

# Run container
docker run -p 10000:10000 -e SECRET_KEY="docker-secret" resumebuilder
```
Navigate to `http://localhost:10000`.

---

## 6. Deploying to Render

This repository includes a ready-to-deploy `render.yaml` specification:

1. Push your code to a GitHub or GitLab repository.
2. In the Render Dashboard, click **New +** ➔ **Blueprint**.
3. Select your repository.
4. Render will automatically configure:
   - **resumebuilder-db**: Managed PostgreSQL 15 database instance.
   - **resume-builder-app**: Web Service built from `./Dockerfile` with Gunicorn WSGI.
5. Provide your live `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` in the Render environment variables dashboard.
