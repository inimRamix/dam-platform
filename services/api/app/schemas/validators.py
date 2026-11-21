from typing import Annotated

from pydantic import AfterValidator


def validate_password(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Пароль должен содержать минимум 8 символов")
    if len(value.encode("utf-8")) > 72:
        raise ValueError(
            "Пароль слишком длинный: максимум 72 байта "
            "(≈72 символа латиницы или ≈36 символов кириллицы)"
        )
    return value


Password = Annotated[str, AfterValidator(validate_password)]
