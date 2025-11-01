from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from api.constants import UNACCEPTABLE_USERNAMES as bad_usernames


class MainUsernameValidator(validators.RegexValidator):
    regex = r'^[\w.@+-]+\Z'
    message = _(
        'Имя username должно содержать только буквы '
        'числа или специальные символы @/./+/-/_ .'
        )
    flags = 0


def unacceptable_name(value):
    if value in bad_usernames:
        raise ValidationError(f'{value} - недопустимое имя пользователя.')
