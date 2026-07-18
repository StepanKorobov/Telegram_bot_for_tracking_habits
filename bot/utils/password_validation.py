import logging
import re

logger = logging.getLogger(__name__)
# Более корректный пароль (минимум 8 символов, хотя бы одна заглавная, хотя бы одна строчная, хотя бы одна цифра, хотя бы один спецсимвол, без пробелов)
# pattern = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[#@#$%^&*])[^\s]{8,}$")

# Пароль из букв английского алфавита и цифр в любом количестве, без пробелов
pattern = re.compile(r"[a-zA-Z0-9]+")


def password_validator(password: str) -> bool:
    """
    Валидация пароля.

    Args:
        password: Пароль пользователя.

    Returns:
        True в случае прохождения валидации, False при невалидном пароле.
    """

    result: re.Match | None = pattern.fullmatch(password)

    is_valid = result is not None

    if is_valid:
        logger.debug(
            "password_validator: password is valid (pattern=%s)", pattern.pattern
        )
    else:
        logger.debug(
            "password_validator: password is invalid (pattern=%s, length=%s, has_space=%s)",
            pattern.pattern,
            len(password),
            any(ch.isspace() for ch in password),
        )

    return is_valid
