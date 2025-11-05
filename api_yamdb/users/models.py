"""Содержание основной модели пользователя."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from api.constants import MODELS_CONSTANTS, ROLE_ADMIN, ROLE_MODERATOR, ROLES
from api.utils import get_role_length
from .validators import username_validator


class User(AbstractUser):
    """Задание расширенной модели пользователя."""

    email = models.EmailField(blank=False, null=False, unique=True)
    username = models.CharField(
        _('username'),
        max_length=MODELS_CONSTANTS['username'],
        unique=True,
        help_text=_(
            'Обязательное поле, длинной до 150 символов. '
            'Буквы, числа или спец-сиволы @/./+/-/_ .'
        ),
        validators=[username_validator,],
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
        max_length=get_role_length(ROLES),
        choices=ROLES,
        default='user',
    )

    class Meta:
        """Meta класс модели User."""

        ordering = ('role',)
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
        return (self.is_superuser and self.is_staff) or self.role == ROLE_ADMIN

    @property
    def is_moderator(self):
        """Определение роли модератора в проекте."""
        return self.role == ROLE_MODERATOR
