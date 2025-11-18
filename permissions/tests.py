from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import AccessRoleRule, BusinessElement, Role, UserRole

User = get_user_model()


class RoleModelTest(TestCase):
    """Тесты для модели Role."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.role_data = {
            'name': 'Test Role',
            'description': 'Test Description'
        }

    def test_create_role(self):
        """Тест создания роли."""
        role = Role.objects.create(**self.role_data)
        self.assertEqual(role.name, 'Test Role')
        self.assertEqual(role.description, 'Test Description')
        self.assertIsNotNone(role.created_at)

    def test_role_str(self):
        """Тест строкового представления роли."""
        role = Role.objects.create(**self.role_data)
        self.assertEqual(str(role), 'Test Role')

    def test_role_unique_name(self):
        """Тест уникальности имени роли."""
        Role.objects.create(**self.role_data)
        with self.assertRaises(Exception):
            Role.objects.create(**self.role_data)


class BusinessElementModelTest(TestCase):
    """Тесты для модели BusinessElement."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.element_data = {
            'name': 'test_element',
            'description': 'Test Element Description'
        }

    def test_create_business_element(self):
        """Тест создания бизнес-элемента."""
        element = BusinessElement.objects.create(**self.element_data)
        self.assertEqual(element.name, 'test_element')
        self.assertIsNotNone(element.created_at)

    def test_business_element_str(self):
        """Тест строкового представления бизнес-элемента."""
        element = BusinessElement.objects.create(**self.element_data)
        self.assertEqual(str(element), 'test_element')


class AccessRoleRuleModelTest(TestCase):
    """Тесты для модели AccessRoleRule."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.role = Role.objects.create(name='Test Role')
        self.element = BusinessElement.objects.create(name='test_element')

    def test_create_access_rule(self):
        """Тест создания правила доступа."""
        rule = AccessRoleRule.objects.create(
            role=self.role,
            element=self.element,
            read_permission=True,
            create_permission=True
        )
        self.assertEqual(rule.role, self.role)
        self.assertEqual(rule.element, self.element)
        self.assertTrue(rule.read_permission)
        self.assertTrue(rule.create_permission)
        self.assertFalse(rule.read_all_permission)

    def test_access_rule_str(self):
        """Тест строкового представления правила доступа."""
        rule = AccessRoleRule.objects.create(
            role=self.role,
            element=self.element
        )
        expected = f"{self.role.name} -> {self.element.name}"
        self.assertEqual(str(rule), expected)

    def test_access_rule_unique_together(self):
        """Тест уникальности комбинации роли и элемента."""
        AccessRoleRule.objects.create(
            role=self.role,
            element=self.element
        )
        with self.assertRaises(Exception):
            AccessRoleRule.objects.create(
                role=self.role,
                element=self.element
            )


class UserRoleModelTest(TestCase):
    """Тесты для модели UserRole."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        self.role = Role.objects.create(name='Test Role')

    def test_create_user_role(self):
        """Тест создания связи пользователя с ролью."""
        user_role = UserRole.objects.create(
            user=self.user,
            role=self.role
        )
        self.assertEqual(user_role.user, self.user)
        self.assertEqual(user_role.role, self.role)
        self.assertIsNotNone(user_role.created_at)

    def test_user_role_str(self):
        """Тест строкового представления связи."""
        user_role = UserRole.objects.create(
            user=self.user,
            role=self.role
        )
        expected = f"{self.user.email} - {self.role.name}"
        self.assertEqual(str(user_role), expected)

    def test_user_role_unique_together(self):
        """Тест уникальности комбинации пользователя и роли."""
        UserRole.objects.create(user=self.user, role=self.role)
        with self.assertRaises(Exception):
            UserRole.objects.create(user=self.user, role=self.role)


class RoleViewSetTest(TestCase):
    """Тесты для RoleViewSet."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            password='admin123'
        )
        self.role = Role.objects.create(name='Admin Role')
        self.element = BusinessElement.objects.create(name='roles')
        # Создаем правило доступа для чтения всех
        AccessRoleRule.objects.create(
            role=self.role,
            element=self.element,
            read_all_permission=True,
            create_permission=True,
            update_all_permission=True,
            delete_all_permission=True
        )
        UserRole.objects.create(user=self.user, role=self.role)

    def test_list_roles_authenticated(self):
        """Тест получения списка ролей."""
        self.client.force_authenticate(user=self.user)
        url = reverse('permissions:role-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_role_authenticated(self):
        """Тест создания роли."""
        self.client.force_authenticate(user=self.user)
        url = reverse('permissions:role-list')
        data = {
            'name': 'New Role',
            'description': 'New Role Description'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Role')

    def test_update_role_authenticated(self):
        """Тест обновления роли."""
        self.client.force_authenticate(user=self.user)
        url = reverse('permissions:role-detail', args=[self.role.id])
        data = {'name': 'Updated Role', 'description': 'Updated'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Role')

    def test_delete_role_authenticated(self):
        """Тест удаления роли."""
        self.client.force_authenticate(user=self.user)
        url = reverse('permissions:role-detail', args=[self.role.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class BusinessElementViewSetTest(TestCase):
    """Тесты для BusinessElementViewSet."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            password='admin123'
        )
        self.role = Role.objects.create(name='Admin Role')
        self.element = BusinessElement.objects.create(
            name='business_elements'
        )
        AccessRoleRule.objects.create(
            role=self.role,
            element=self.element,
            read_all_permission=True,
            create_permission=True,
            update_all_permission=True,
            delete_all_permission=True
        )
        UserRole.objects.create(user=self.user, role=self.role)

    def test_list_business_elements(self):
        """Тест получения списка бизнес-элементов."""
        self.client.force_authenticate(user=self.user)
        url = reverse('permissions:business-element-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_business_element(self):
        """Тест создания бизнес-элемента."""
        self.client.force_authenticate(user=self.user)
        url = reverse('permissions:business-element-list')
        data = {
            'name': 'new_element',
            'description': 'New Element'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AccessRoleRuleViewSetTest(TestCase):
    """Тесты для AccessRoleRuleViewSet."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            password='admin123'
        )
        self.role = Role.objects.create(name='Admin Role')
        self.element = BusinessElement.objects.create(name='access_rules')
        AccessRoleRule.objects.create(
            role=self.role,
            element=self.element,
            read_all_permission=True,
            create_permission=True,
            update_all_permission=True,
            delete_all_permission=True
        )
        UserRole.objects.create(user=self.user, role=self.role)

    def test_list_access_rules(self):
        """Тест получения списка правил доступа."""
        self.client.force_authenticate(user=self.user)
        url = reverse('permissions:access-rule-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_access_rule(self):
        """Тест создания правила доступа."""
        self.client.force_authenticate(user=self.user)
        url = reverse('permissions:access-rule-list')
        new_role = Role.objects.create(name='New Role')
        new_element = BusinessElement.objects.create(name='new_element')
        data = {
            'role': new_role.id,
            'element': new_element.id,
            'read_permission': True,
            'create_permission': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UserRoleViewSetTest(TestCase):
    """Тесты для UserRoleViewSet."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            password='admin123'
        )
        self.role = Role.objects.create(name='Admin Role')
        self.element = BusinessElement.objects.create(name='user_roles')
        AccessRoleRule.objects.create(
            role=self.role,
            element=self.element,
            read_all_permission=True,
            create_permission=True,
            update_all_permission=True,
            delete_all_permission=True
        )
        UserRole.objects.create(user=self.user, role=self.role)

    def test_list_user_roles(self):
        """Тест получения списка ролей пользователей."""
        self.client.force_authenticate(user=self.user)
        url = reverse('permissions:user-role-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assign_role(self):
        """Тест назначения роли пользователю."""
        self.client.force_authenticate(user=self.user)
        url = reverse('permissions:user-role-assign')
        new_user = User.objects.create_user(
            email='newuser@example.com',
            username='newuser',
            first_name='New',
            last_name='User',
            password='newpass123'
        )
        new_role = Role.objects.create(name='New Role')
        data = {
            'user_id': new_user.id,
            'role_id': new_role.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)

    def test_assign_role_duplicate(self):
        """Тест назначения уже существующей роли."""
        self.client.force_authenticate(user=self.user)
        url = reverse('permissions:user-role-assign')
        new_user = User.objects.create_user(
            email='newuser@example.com',
            username='newuser',
            first_name='New',
            last_name='User',
            password='newpass123'
        )
        data = {
            'user_id': new_user.id,
            'role_id': self.role.id
        }
        # Первое назначение
        self.client.post(url, data)
        # Второе назначение (должно вернуть 200)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_remove_role(self):
        """Тест удаления роли у пользователя."""
        self.client.force_authenticate(user=self.user)
        new_user = User.objects.create_user(
            email='newuser@example.com',
            username='newuser',
            first_name='New',
            last_name='User',
            password='newpass123'
        )
        UserRole.objects.create(user=new_user, role=self.role)
        url = reverse('permissions:user-role-remove')
        data = {
            'user_id': new_user.id,
            'role_id': self.role.id
        }
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_remove_role_nonexistent(self):
        """Тест удаления несуществующей роли."""
        self.client.force_authenticate(user=self.user)
        url = reverse('permissions:user-role-remove')
        data = {
            'user_id': 999,
            'role_id': 999
        }
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class HasPermissionTest(TestCase):
    """Тесты для кастомного permission класса."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.user = User.objects.create_user(
            email='user@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        self.role = Role.objects.create(name='Test Role')
        self.element = BusinessElement.objects.create(name='roles')
        UserRole.objects.create(user=self.user, role=self.role)

    def test_permission_without_rule(self):
        """Тест доступа без правила."""
        from .permissions import HasPermission
        permission = HasPermission()
        # Без правила доступа должно быть False
        self.assertFalse(
            permission._check_permission(
                self.user,
                'roles',
                'read',
                None
            )
        )

    def test_permission_read_all(self):
        """Тест доступа на чтение всех."""
        from .permissions import HasPermission
        AccessRoleRule.objects.create(
            role=self.role,
            element=self.element,
            read_all_permission=True
        )
        permission = HasPermission()
        self.assertTrue(
            permission._check_permission(
                self.user,
                'roles',
                'read',
                None
            )
        )

    def test_permission_read_own(self):
        """Тест доступа на чтение своих."""
        from .permissions import HasPermission
        AccessRoleRule.objects.create(
            role=self.role,
            element=self.element,
            read_permission=True
        )
        permission = HasPermission()
        # Создаем объект-пользователя для проверки владельца
        self.assertTrue(
            permission._check_permission(
                self.user,
                'roles',
                'read',
                None,
                obj=self.user
            )
        )

    def test_permission_create(self):
        """Тест доступа на создание."""
        from .permissions import HasPermission
        AccessRoleRule.objects.create(
            role=self.role,
            element=self.element,
            create_permission=True
        )
        permission = HasPermission()
        self.assertTrue(
            permission._check_permission(
                self.user,
                'roles',
                'create',
                None
            )
        )

    def test_permission_update_all(self):
        """Тест доступа на обновление всех."""
        from .permissions import HasPermission
        AccessRoleRule.objects.create(
            role=self.role,
            element=self.element,
            update_all_permission=True
        )
        permission = HasPermission()
        self.assertTrue(
            permission._check_permission(
                self.user,
                'roles',
                'update',
                None
            )
        )

    def test_permission_delete_all(self):
        """Тест доступа на удаление всех."""
        from .permissions import HasPermission
        AccessRoleRule.objects.create(
            role=self.role,
            element=self.element,
            delete_all_permission=True
        )
        permission = HasPermission()
        self.assertTrue(
            permission._check_permission(
                self.user,
                'roles',
                'delete',
                None
            )
        )

    def test_is_owner_check(self):
        """Тест проверки владельца объекта."""
        from .permissions import HasPermission
        permission = HasPermission()
        # Тест с объектом, имеющим поле user
        class TestObj:
            def __init__(self, user):
                self.user = user
        obj = TestObj(self.user)
        self.assertTrue(permission._is_owner(self.user, obj))

    def test_is_owner_check_false(self):
        """Тест проверки владельца - не владелец."""
        from .permissions import HasPermission
        other_user = User.objects.create_user(
            email='other@example.com',
            username='other',
            first_name='Other',
            last_name='User',
            password='otherpass123'
        )
        permission = HasPermission()
        class TestObj:
            def __init__(self, user):
                self.user = user
        obj = TestObj(other_user)
        self.assertFalse(permission._is_owner(self.user, obj))
