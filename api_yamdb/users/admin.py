from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Расширенная модель пользователя для администрирования."""

    search_fields = ('email', 'first_name', 'last_name')
    list_display = ('username', 'email', 'role', 'bio', 'date_joined')
    list_editable = ('role', 'bio')
    empty_value_display = '-пусто-'
