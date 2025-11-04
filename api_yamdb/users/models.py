"""Содержание основной модели пользователя."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from api.constants import MODELS_CONSTANTS, ROLES
from .validators import unacceptable_name
from .validators import MainUsernameValidator


class User(AbstractUser):
    """Задание расширенной модели пользователя."""

    ROLE_CHOICES = ROLES
    email = models.EmailField(blank=False, null=False, unique=True)
    username_validator = MainUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=MODELS_CONSTANTS['username'],
        unique=True,
        help_text=_(
            'Обязательное поле, длинной до 150 символов. '
            'Буквы, числа или спец-сиволы @/./+/-/_ .'
        ),
        validators=[username_validator, unacceptable_name],
        error_messages={
            "unique": _('Такое имя пользователся уже существует.'),
        },
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=MODELS_CONSTANTS['password'],
        blank=True,
    )
    confirmation_code = models.CharField(max_length=50, blank=True)
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=MODELS_CONSTANTS['role'],
        choices=ROLE_CHOICES,
        default='user',
    )

    class Meta:
        """Meta класс модели User."""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'username'],
                name='Поля email и username должны быть уникальными.'
            )
        ]

    @property
    def is_admin(self):
        """Определение роли администратора в проекте."""
        return (self.is_superuser and self.is_staff) or self.role == 'admin'

    @property
    def is_moderator(self):
        """Определение роли модератора в проекте."""
        return self.role == 'moderator'
