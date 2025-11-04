"""Валидаторы для модели Users."""
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from api.constants import UNACCEPTABLE_USERNAMES


class MainUsernameValidator(validators.RegexValidator):
    """Валидация username на допустимые символы.

    Имя username должно содержать только буквы числа или
    специальные символы @/./+/-/_ .
    """

    regex = r'^[\w.@+-]+\Z'
    message = _(
        'Имя username должно содержать только буквы '
        'числа или специальные символы @/./+/-/_ .'
    )
    flags = 0


def unacceptable_name(value):
    """Валидация username на допустимые имена пользователей."""
    if value in UNACCEPTABLE_USERNAMES:
        raise ValidationError(f'{value} - недопустимое имя пользователя.')
