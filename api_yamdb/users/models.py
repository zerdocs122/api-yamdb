from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Расширенная модель пользователя."""

    ROLE_CHOICES = [
        ('user', 'Аутентифицированный пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]
    email = models.EmailField(blank=False, null=False, unique=True)
    password = models.CharField(
        verbose_name='Пароль',
        max_length=128,
        blank=True,
    )
    confirmation_code = models.CharField(max_length=50, blank=True)
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=32,
        choices=ROLE_CHOICES,
        default='user',
    )

    constraints = [
        models.UniqueConstraint(
            fields=['email', 'username'],
            name='Поля email и username должны быть уникальными.'
        )
    ]
