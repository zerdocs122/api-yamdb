"""Настройка админ-панели для модели пользователя."""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Расширенная модель пользователя для администрирования."""

    search_fields = ('email', 'first_name', 'last_name')
    list_display = ('username', 'email', 'role', 'bio', 'date_joined')
    list_editable = ('role', 'bio')
    empty_value_display = '-пусто-'
