from app.core.config import settings


def _build_activation_url(prefix: str, token: str) -> str:
    path = f"{settings.api.prefix}{settings.api.v1.prefix}{prefix}/activate"
    return f"{settings.app_base_url}{path}?token={token}"


def build_admin_activation_url(token: str) -> str:
    return _build_activation_url(settings.api.v1.admin, token)


def build_user_activation_url(token: str) -> str:
    return _build_activation_url(settings.api.v1.users, token)
