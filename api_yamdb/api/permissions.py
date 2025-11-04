from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Проверка прав доступа для администратора."""

    def has_permission(self, request, view):
        """Проверка GET метода и аутентифицированного пользователя."""
        if request.user.is_authenticated:
            return request.user.is_admin


class IsAdminOrReadOnly(IsAdmin):
    """Проверка прав доступа для администратора или только чтение."""

    def has_permission(self, request, view):
        """Условия на доступ к списку объектов."""
        return (
            request.method in permissions.SAFE_METHODS
            or super().has_permission(request, view)
        )


class IsAuthorOrModeratorsOrReadOnly(permissions.BasePermission):
    """GET-доступ для всех или для автора и модераторов."""

    def has_permission(self, request, view):
        """Условия на доступ к списку объектов."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Условия на доступ к отдельному объекту."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and obj.author == request.user
            or (request.user.is_admin or request.user.is_moderator)
        )
