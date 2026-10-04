from app.routes.auth import auth_bp
from app.routes.profile import profile_bp
from app.routes.roles import roles_bp
from app.routes.dashboard import dashboard_bp
from app.routes.resume import resume_bp
from app.routes.export import export_bp
from app.routes.billing import billing_bp

__all__ = [
    "auth_bp",
    "profile_bp",
    "roles_bp",
    "dashboard_bp",
    "resume_bp",
    "export_bp",
    "billing_bp",
]
