from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Проверка прав доступа для администратора."""

    def has_permission(self, request, view):
        """Проверка GET метода и аутентифицированного пользователя."""
        return (
            request.user.is_authenticated
            and (request.user.role == 'admin' or request.user.is_superuser)
        )
