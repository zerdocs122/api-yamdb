"""Валидаторы для модели Users."""
import re

from django.core.exceptions import ValidationError

from api.constants import REGEXP_PATTERN, UNACCEPTABLE_USERNAMES


def username_validator(value):
    """Валидация username на допустимые символы и имена.

    Имя username должно содержать только буквы числа или
    специальные символы @/./+/-/_ .
    """
    if not re.match(REGEXP_PATTERN, value):
        raise ValidationError(
            'Имя username должно содержать только буквы '
            'числа или специальные символы @/./+/-/_ .'
        )
    if value in UNACCEPTABLE_USERNAMES:
        raise ValidationError(f'{value} - недопустимое имя пользователя.')
