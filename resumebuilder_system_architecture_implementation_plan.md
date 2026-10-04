# ResumeBuilder: Production-Ready Architectural Specification

## 1. System Architecture & Tech Stack Overview

ResumeBuilder is designed as a modular, monolithic Flask application deployed to **Render** using a containerized environment to handle server-side PDF compilation reliably.

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
 │  │    ├── role_bp      (Prospective Job Roles)        │
 │  │    ├── export_bp    (Jinja ➔ WeasyPrint ➔ PDF)     │
 │  │    └── billing_bp   (Stripe / Razorpay Webhooks)   │
 │  │                                                    │
 │  ├── Template Engine: Jinja2                          │
 │  │    ├── Modern Template (2-Column CSS Grid)         │
 │  │    ├── Minimalist Template (Clean Monochrome)      │
 │  │    └── Executive Template (ATS Traditional Serif)  │
 │  │                                                    │
 │  └── Security & Sanitization                          │
 │       ├── Flask-WTF (CSRF tokens on every POST)       │
 │       └── Bleach (HTML input sanitizer)               │
 └──────┬────────────────────────────────────────────────┘
        │
        ├── [ Render Managed PostgreSQL Database ]
        │     (Multi-tenant user profiles, roles, and payment records)
        │
        └── [ External Payment Gateway (Stripe/Razorpay) ]
              (Webhooks for download credit authorization)

```

## 2. Relational Database Schema Design

The schema separates a student's **Master Profile** (immutable baseline credentials) from **Prospective Roles** (tailored job-specific resumes).

```
┌────────────────────────────────┐
│             users              │
├────────────────────────────────┤
│ id (PK, UUID/Int)              │
│ email (VARCHAR, Unique, Index) │
│ password_hash (VARCHAR)        │
│ is_active (BOOLEAN)            │
│ download_credits (INT, Def: 0) │
│ created_at (TIMESTAMP)         │
└───────────────┬────────────────┘
                │ 1
                │
                ├───────────────────────────────────────────┐
                │ 1                                         │ 1
                ▼                                           ▼
┌────────────────────────────────┐          ┌──────────────────────────────────┐
│         master_profiles        │          │         job_role_resumes         │
├────────────────────────────────┤          ├──────────────────────────────────┤
│ id (PK)                        │          │ id (PK)                          │
│ user_id (FK -> users.id)       │          │ user_id (FK -> users.id)         │
│ full_name (VARCHAR)            │          │ role_title (VARCHAR)             │
│ phone (VARCHAR)                │          │ target_industry (VARCHAR)        │
│ location (VARCHAR)             │          │ custom_summary (TEXT)            │
│ linkedin_url (VARCHAR)         │          │ selected_style (VARCHAR)         │
│ github_url (VARCHAR)           │          │ is_archived (BOOLEAN)            │
│ portfolio_url (VARCHAR)        │          │ created_at (TIMESTAMP)           │
└───────────────┬────────────────┘          └────────────────┬─────────────────┘
                │ 1                                          │ 1
                │                                            │
                ▼ N                                          ├────────────────────────────┐
┌────────────────────────────────┐                           │ 1                          │ 1
│          educations            │                           ▼ N                          ▼ N
├────────────────────────────────┤          ┌───────────────────────────┐ ┌───────────────┐
│ id (PK)                        │          │        experiences        │ │   projects    │
│ profile_id (FK)                │          ├───────────────────────────┤ ├───────────────┤
│ institution (VARCHAR)          │          │ id (PK)                   │ │ id (PK)       │
│ degree (VARCHAR)               │          │ role_id (FK)              │ │ role_id (FK)  │
│ field_of_study (VARCHAR)       │          │ company (VARCHAR)         │ │ name (VARCHAR)│
│ graduation_date (DATE)         │          │ job_title (VARCHAR)       │ │ tech_stack    │
│ gpa_or_grade (VARCHAR)         │          │ start_date (DATE)         │ │ bullet_points │
└────────────────────────────────┘          │ end_date (DATE, Nullable) │ │ live_url      │
                                            │ is_current (BOOLEAN)      │ └───────────────┘
                                            │ bullet_points (JSON/TEXT) │
                                            └───────────────────────────┘

```

## 3. Project Directory Structure

```
resumebuilder/
├── app/
│   ├── __init__.py                # App factory pattern: create_app()
│   ├── config.py                  # Dev, Test, Prod configuration classes
│   ├── extensions.py              # db, migrate, login_manager, csrf instantiation
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User and Payment transaction models
│   │   ├── profile.py             # MasterProfile and Education models
│   │   └── resume.py              # JobRoleResume, Experience, Project, Skill models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                # /login, /register, /logout
│   │   ├── profile.py             # /profile (Master academic profile)
│   │   ├── roles.py               # /roles (CRUD prospective job roles)
│   │   ├── export.py              # /export/<role_id>/pdf/<style>
│   │   └── billing.py             # /billing/checkout, /billing/webhook
│   ├── templates/
│   │   ├── base.html              # Core application layout
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── dashboard/
│   │   │   ├── index.html         # Overview of roles & profile status
│   │   │   ├── edit_profile.html  # Master profile editor
│   │   │   └── edit_role.html     # Role-specific tailoring form
│   │   ├── resumes/               # Dedicated Print-Optimized Layouts
│   │   │   ├── _print_base.html   # Common PDF headers & page rules
│   │   │   ├── modern.html        # Two-column dynamic design
│   │   │   ├── minimalist.html    # Clean typographic monochrome
│   │   │   └── executive.html     # Formal ATS-compliant layout
│   │   └── billing/
│   │       ├── paywall.html       # Upgrade / Buy credits prompt
│   │       └── success.html
│   └── static/
│       ├── css/
│       │   ├── app.css            # Standard UI styling
│       │   └── resume_print.css   # Print specific styles: @page, breaks
│       └── js/
│           ├── dynamic_fields.js  # Add/remove experience & project rows
│           └── preview.js         # Real-time iframe preview handler
├── migrations/                    # Flask-Migrate database migrations
├── Dockerfile                     # Custom runtime containing WeasyPrint dependencies
├── render.yaml                    # Infrastructure definition for Render
├── requirements.txt               # Pinned Python package dependencies
├── wsgi.py                        # Gunicorn execution entrypoint
└── README.md

```

## 4. Resume Design Specifications

Each design targets an exact standard A4/US-Letter page format with strict pagination constraints using CSS Paged Media standards.

```
/* static/css/resume_print.css */
@page {
    size: A4;
    margin: 12mm 14mm 12mm 14mm;
}

@media print {
    body {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    
    .section-block {
        break-inside: avoid;
        page-break-inside: avoid;
    }
}

```

### Style 1: Modern

* **Layout**: Asymmetric 2-column layout (30% sidebar, 70% main body).

* **Palette**: Dark slate gray (`#1E293B`) headers, primary teal or royal navy accent (`#0F766E`), white background.

* **Sections**: Sidebar holds contact details, skills list, education, and languages. Main body showcases target professional summary, experience bullets, and featured technical projects.

### Style 2: Minimalist

* **Layout**: Single column, high vertical whitespace, strict typographic hierarchy.

* **Palette**: Monochrome (`#111827` primary text, `#4B5563` subtext, `#E5E7EB` thin dividers).

* **Typography**: Geometric sans-serif font stack (Inter, Helvetica Neue, sans-serif).

* **Sections**: Top centered name and inline contact tokens, separated by horizontal rules, prioritizing projects and core achievements.

### Style 3: Executive (ATS Classic)

* **Layout**: Traditional single column, left-aligned, standard corporate hierarchy.

* **Palette**: Deep charcoal (`#000000` or `#1A1A1A`) with zero decorative background graphics to ensure optimal ATS parsing.

* **Typography**: Classic serif font stack (Merriweather, Georgia, Times New Roman).

* **Sections**: Contact header $\rightarrow$ Professional Summary $\rightarrow$ Chronological Experience $\rightarrow$ Education $\rightarrow$ Certifications.

## 5. Paywall & Monetization Logic

To enable the transition from free access to a paid export model:

1. **Free Tier**: Students can build their profiles, add infinite prospective roles, and view web-based live previews (served via `<iframe src="/resume/preview/<role_id>">`).

2. **Paid Action (PDF Download)**:

   * When triggering `GET /export/<role_id>/pdf/<style>`, the route checks:
     

     $$
     \text{can\_download} = (\text{user.is\_premium}) \lor (\text{user.download\_credits} > 0)
     $$

   * If `False`, the app redirects to the paywall with a session parameter preserving their target role and style choice.

3. **Webhook Verification**:

   * Upon successful checkout from Stripe or Razorpay, the webhook endpoint executes an idempotent update:

     * Increments `download_credits` or sets `is_premium = True`.

   * User is redirected directly to the download trigger.

## 6. Deployment & Render Configuration

### Dockerfile (with WeasyPrint Native Dependencies)

WeasyPrint relies on system-level graphics libraries (`cairo`, `pango`, `gdk-pixbuf`) that are not present in standard bare-metal Python buildpacks.

```
FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install native dependencies for WeasyPrint and compile tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libjpeg-dev \
    libopenjp2-7-dev \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render exposes the port via the PORT environment variable (default 10000)
EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "2", "--threads", "4", "--timeout", "120", "wsgi:app"]

```

### Infrastructure as Code: `render.yaml`

```
services:
  - type: web
    name: resume-builder-app
    env: docker
    plan: starter
    region: oregon
    dockerContext: .
    dockerfilePath: ./Dockerfile
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: resumebuilder-db
          property: connectionString
      - key: STRIPE_SECRET_KEY
        sync: false
      - key: STRIPE_WEBHOOK_SECRET
        sync: false

databases:
  - name: resumebuilder-db
    plan: starter
    region: oregon
    postgresMajorVersion: 15

```

## 7. Phased Implementation Roadmap for Antigravity

| Phase | Milestone Focus | Deliverables | 
| ----- | ----- | ----- | 
| **Phase 1** | Project Setup & Core Models | `create_app()`, DB schema with SQLAlchemy, Alembic migrations, registration/login system. | 
| **Phase 2** | Profile & Roles Engine | Base Profile editor, Prospective Role dashboard, CRUD forms for tailored experiences and skills. | 
| **Phase 3** | Print Templates & PDF Generation | Implementation of Modern, Minimalist, and Executive HTML/CSS layouts; WeasyPrint export endpoint. | 
| **Phase 4** | Paywall & Monetization Gate | Credits logic, Stripe/Razorpay integration, checkout modal, and webhook validation. | 
| **Phase 5** | Containerization & Render Launch | Finalize `Dockerfile`, configure `render.yaml`, set up PostgreSQL instance, and test production deployments. | 
