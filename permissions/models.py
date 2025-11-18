from django.db import models

from accounts.models import User


class Role(models.Model):
    """Роли пользователей (админ, менеджер, пользователь, гость)."""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название роли'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        db_table = 'roles'
        ordering = ['name']

    def __str__(self):
        return self.name


class BusinessElement(models.Model):
    """Бизнес-элементы системы."""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название элемента'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Бизнес-элемент'
        verbose_name_plural = 'Бизнес-элементы'
        db_table = 'business_elements'
        ordering = ['name']

    def __str__(self):
        return self.name


class AccessRoleRule(models.Model):
    """Правила доступа ролей к бизнес-элементам."""
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='access_rules',
        verbose_name='Роль'
    )
    element = models.ForeignKey(
        BusinessElement,
        on_delete=models.CASCADE,
        related_name='access_rules',
        verbose_name='Бизнес-элемент'
    )

    # Права доступа
    read_permission = models.BooleanField(
        default=False,
        verbose_name='Чтение (свои)'
    )
    read_all_permission = models.BooleanField(
        default=False,
        verbose_name='Чтение (все)'
    )
    create_permission = models.BooleanField(
        default=False,
        verbose_name='Создание'
    )
    update_permission = models.BooleanField(
        default=False,
        verbose_name='Обновление (свои)'
    )
    update_all_permission = models.BooleanField(
        default=False,
        verbose_name='Обновление (все)'
    )
    delete_permission = models.BooleanField(
        default=False,
        verbose_name='Удаление (свои)'
    )
    delete_all_permission = models.BooleanField(
        default=False,
        verbose_name='Удаление (все)'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Правило доступа'
        verbose_name_plural = 'Правила доступа'
        db_table = 'access_roles_rules'
        unique_together = [['role', 'element']]
        ordering = ['role', 'element']

    def __str__(self):
        return f"{self.role.name} -> {self.element.name}"


class UserRole(models.Model):
    """Связь пользователей с ролями."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name='Пользователь'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name='Роль'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        db_table = 'user_roles'
        unique_together = [['user', 'role']]
        ordering = ['user', 'role']

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"
