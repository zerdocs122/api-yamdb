"""Настройка админ-панели для модели пользователя."""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Расширенная модель пользователя для администрирования."""

    search_fields = ('email', 'first_name', 'last_name')
    list_display = (
        'username', 'email', 'role', 'number_of_reviews',
        'number_of_comments', 'bio', 'date_joined'
    )
    list_editable = ('role', 'bio')
    empty_value_display = '-пусто-'

    @admin.display(description='Отзывов оставлено')
    def number_of_reviews(self, obj):
        """Подсчет оставленных отзывов пользователем."""
        return obj.review.count()

    @admin.display(description='Комментариев оставлено')
    def number_of_comments(self, obj):
        """Подсчет оставленных комментариев пользователем."""
        return obj.comment.count()
