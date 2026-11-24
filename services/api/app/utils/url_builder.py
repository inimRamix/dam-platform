from app.core.config import settings


def build_admin_activation_url(token: str) -> str:
    return f"{settings.app_base_url}/admin/activate?token={token}"


def build_user_activation_url(token: str) -> str:
    return f"{settings.app_base_url}/users/activate?token={token}"
