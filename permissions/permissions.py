from rest_framework import permissions

from .models import AccessRoleRule, BusinessElement, UserRole


class HasPermission(permissions.BasePermission):
    """
    Кастомный permission класс для проверки прав доступа пользователя
    к бизнес-элементам на основе ролей.
    """

    def has_permission(self, request, view):
        """Проверка прав доступа для действия."""
        if not request.user or not request.user.is_authenticated:
            return False

        # Получаем бизнес-элемент из view
        element_name = getattr(view, 'business_element', None)
        if not element_name:
            return True  # Если элемент не указан, разрешаем доступ

        # Получаем действие (read, create, update, delete)
        action = getattr(view, 'action', None)
        if not action:
            # Определяем действие по HTTP методу
            if request.method in permissions.SAFE_METHODS:
                action = 'read'
            elif request.method == 'POST':
                action = 'create'
            elif request.method in ['PUT', 'PATCH']:
                action = 'update'
            elif request.method == 'DELETE':
                action = 'delete'

        # Проверяем права доступа
        return self._check_permission(
            request.user,
            element_name,
            action,
            request
        )

    def has_object_permission(self, request, view, obj):
        """Проверка прав доступа к конкретному объекту."""
        if not request.user or not request.user.is_authenticated:
            return False

        element_name = getattr(view, 'business_element', None)
        if not element_name:
            return True

        action = getattr(view, 'action', None)
        if not action:
            if request.method in permissions.SAFE_METHODS:
                action = 'read'
            elif request.method in ['PUT', 'PATCH']:
                action = 'update'
            elif request.method == 'DELETE':
                action = 'delete'

        # Проверяем права доступа с учетом владельца объекта
        return self._check_permission(
            request.user,
            element_name,
            action,
            request,
            obj=obj
        )

    def _check_permission(self, user, element_name, action, request, obj=None):
        """Внутренний метод для проверки прав доступа."""
        try:
            element = BusinessElement.objects.get(name=element_name)
        except BusinessElement.DoesNotExist:
            return False

        # Получаем роли пользователя
        user_roles = UserRole.objects.filter(
            user=user
        ).select_related('role')
        if not user_roles.exists():
            return False

        # Проверяем права для каждой роли
        for user_role in user_roles:
            access_rule = AccessRoleRule.objects.filter(
                role=user_role.role,
                element=element
            ).first()

            if not access_rule:
                continue

            # Проверяем права в зависимости от действия
            if action == 'read':
                if access_rule.read_all_permission:
                    return True
                if access_rule.read_permission and obj:
                    # Проверяем владельца
                    if self._is_owner(user, obj):
                        return True

            elif action == 'create':
                if access_rule.create_permission:
                    return True

            elif action == 'update':
                if access_rule.update_all_permission:
                    return True
                if access_rule.update_permission and obj:
                    if self._is_owner(user, obj):
                        return True

            elif action == 'delete':
                if access_rule.delete_all_permission:
                    return True
                if access_rule.delete_permission and obj:
                    if self._is_owner(user, obj):
                        return True

        return False

    def _is_owner(self, user, obj):
        """Проверка, является ли пользователь владельцем объекта."""
        # Проверяем наличие поля owner или user
        if hasattr(obj, 'owner'):
            return obj.owner == user
        if hasattr(obj, 'user'):
            return obj.user == user
        if hasattr(obj, 'user_id'):
            return obj.user_id == user.id
        # Если объект - это сам пользователь
        if isinstance(obj, type(user)) and obj.id == user.id:
            return True
        return False

