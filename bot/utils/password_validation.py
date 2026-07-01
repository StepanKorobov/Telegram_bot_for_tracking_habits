import re

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

    if result:
        return True

    return False
