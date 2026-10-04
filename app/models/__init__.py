from app.extensions import login_manager
from app.models.user import User, Payment
from app.models.profile import MasterProfile, BaseProfile
from app.models.resume import JobRoleResume, Experience, Education, Project, Skill

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

__all__ = [
    "User",
    "Payment",
    "MasterProfile",
    "BaseProfile",
    "JobRoleResume",
    "Experience",
    "Education",
    "Project",
    "Skill",
]
