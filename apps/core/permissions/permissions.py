
from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.users.models import Role


class IsOwner(BasePermission):
    """Перевіряє, чи є користувач власником об'єкта."""

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Суперадмін та менеджер мають доступ до всіх об'єктів
        if user.is_superuser:
            return True
        if user.role and user.role.name == Role.RoleName.MANAGER:
            return True

        # Перевірка: шукаємо поле owner або user на об'єкті
        return getattr(
            obj,
            'owner',
            getattr(obj, 'user', None)
        ) == user


class IsImageOwner(BasePermission):
    """Перевіряє, чи є користувач власником оголошення, до якого належить фото."""

    def has_object_permission(self, request, view, obj):
        return obj.listing.owner == request.user


class HasPermissionCodename(BasePermission):
    """
    Перевіряє, чи має користувач необхідний дозвіл (permission codename).
    Дозвіл береться з атрибута required_permission у в'юшці.
    """

    def has_permission(self, request, view):
        user = request.user

        # Анонімні або неактивні користувачі не мають прав
        if not user.is_authenticated or not user.is_active:
            return False

        # Суперадмін має всі права
        if user.is_superuser:
            return True

        # Отримуємо код дозволу з в'юшки
        required_permission = getattr(view, 'required_permission', None)
        if not required_permission:
            return False

        # Перевіряємо наявність дозволу у ролі користувача
        if user.role_id is None:
            return False

        return user.role.permissions.filter(
            codename=required_permission
        ).exists()


class HasPermissionCodenameOrReadOnly(BasePermission):
    """
    Дозволяє читання всім, а зміни - тільки користувачам з відповідним дозволом.
    Використовується для ендпоїнтів з публічним читанням.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return HasPermissionCodename().has_permission(request, view)