from django.contrib import admin
from .models import Role, BusinessElement, AccessRoleRule, UserRole


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Админка для ролей"""
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)


@admin.register(BusinessElement)
class BusinessElementAdmin(admin.ModelAdmin):
    """Админка для бизнес-элементов"""
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)


@admin.register(AccessRoleRule)
class AccessRoleRuleAdmin(admin.ModelAdmin):
    """Админка для правил доступа"""
    list_display = (
        'role', 'element',
        'read_permission', 'read_all_permission',
        'create_permission',
        'update_permission', 'update_all_permission',
        'delete_permission', 'delete_all_permission',
        'created_at'
    )
    list_filter = ('role', 'element', 'created_at')
    search_fields = ('role__name', 'element__name')
    raw_id_fields = ('role', 'element')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Админка для ролей пользователей"""
    list_display = ('user', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__email', 'user__username', 'role__name')
    raw_id_fields = ('user', 'role')
