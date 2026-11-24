from app.models.user import User


def display_name(user: User) -> str:
    """Имя для отображения: 'Иван Петров' или полный email, если имя не задано."""
    full = f"{user.first_name or ''} {user.last_name or ''}".strip()
    return full or user.email
