from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login_manager, csrf

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Import models so they are registered with SQLAlchemy
    from app import models

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.roles import roles_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.resume import resume_bp
    from app.routes.export import export_bp
    from app.routes.billing import billing_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(billing_bp)

    from flask_wtf.csrf import CSRFError
    from flask import redirect, url_for, flash, request
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        flash("Your session has expired. Please try again.", "warning")
        return redirect(request.referrer or url_for("dashboard.index"))

    return app