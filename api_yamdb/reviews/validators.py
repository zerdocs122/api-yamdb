import datetime as dt

from django.core.exceptions import ValidationError


def validate_year(value):
    """Валидация года выпуска произведения."""
    if value > dt.datetime.now().year:
        raise ValidationError(
            'Год выпуска не может быть больше текущего.'
        )
    return value
