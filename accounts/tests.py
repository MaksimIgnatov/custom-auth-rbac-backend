from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from permissions.models import BusinessElement, Role, UserRole

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты для модели User."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }

    def test_create_user(self):
        """Тест создания пользователя."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_str(self):
        """Тест строкового представления пользователя."""
        user = User.objects.create_user(**self.user_data)
        expected = f"{user.email} ({user.get_full_name()})"
        self.assertEqual(str(user), expected)

    def test_set_password_bcrypt(self):
        """Тест хеширования пароля с помощью bcrypt."""
        user = User(**self.user_data)
        user.set_password('testpass123')
        user.save()
        self.assertTrue(user.password.startswith('bcrypt$'))
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.check_password('wrongpass'))

    def test_check_password_django(self):
        """Тест проверки пароля с Django хешированием."""
        from django.contrib.auth.hashers import make_password
        user = User(**self.user_data)
        # Используем стандартный метод Django для установки пароля
        user.password = make_password('djangopass123')
        user.save()
        # Проверяем, что пароль не начинается с bcrypt$
        self.assertFalse(user.password.startswith('bcrypt$'))
        self.assertTrue(user.check_password('djangopass123'))


class UserRegistrationTest(TestCase):
    """Тесты для регистрации пользователя."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.register_url = reverse('accounts:register')
        self.valid_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }

    def test_register_user_success(self):
        """Тест успешной регистрации пользователя."""
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertEqual(
            response.data['user']['email'],
            'newuser@example.com'
        )

    def test_register_user_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями."""
        data = self.valid_data.copy()
        data['password_confirm'] = 'differentpass'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_user_duplicate_email(self):
        """Тест регистрации с дублирующимся email."""
        User.objects.create_user(**{
            'email': 'newuser@example.com',
            'username': 'existing',
            'first_name': 'Existing',
            'last_name': 'User',
            'password': 'pass123'
        })
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_missing_fields(self):
        """Тест регистрации с отсутствующими полями."""
        data = {'email': 'test@example.com'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTest(TestCase):
    """Тесты для входа пользователя."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.login_url = reverse('accounts:login')
        self.user = User.objects.create_user(
            email='login@example.com',
            username='loginuser',
            first_name='Login',
            last_name='User',
            password='loginpass123'
        )

    def test_login_success(self):
        """Тест успешного входа."""
        data = {
            'email': 'login@example.com',
            'password': 'loginpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])

    def test_login_wrong_password(self):
        """Тест входа с неверным паролем."""
        data = {
            'email': 'login@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_login_nonexistent_user(self):
        """Тест входа несуществующего пользователя."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'pass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_login_inactive_user(self):
        """Тест входа неактивного пользователя."""
        self.user.is_active = False
        self.user.save()
        data = {
            'email': 'login@example.com',
            'password': 'loginpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class UserLogoutTest(TestCase):
    """Тесты для выхода пользователя."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.logout_url = reverse('accounts:logout')
        self.user = User.objects.create_user(
            email='logout@example.com',
            username='logoutuser',
            first_name='Logout',
            last_name='User',
            password='logoutpass123'
        )

    def test_logout_authenticated(self):
        """Тест выхода аутентифицированного пользователя."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_logout_unauthenticated(self):
        """Тест выхода неаутентифицированного пользователя."""
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTest(TestCase):
    """Тесты для профиля пользователя."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.profile_url = reverse('accounts:profile')
        self.user = User.objects.create_user(
            email='profile@example.com',
            username='profileuser',
            first_name='Profile',
            last_name='User',
            password='profilepass123'
        )

    def test_get_profile_authenticated(self):
        """Тест получения профиля аутентифицированного пользователя."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profile@example.com')
        self.assertEqual(response.data['username'], 'profileuser')

    def test_get_profile_with_roles(self):
        """Тест получения профиля с ролями."""
        role = Role.objects.create(name='Test Role')
        BusinessElement.objects.create(name='roles')
        UserRole.objects.create(user=self.user, role=role)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('roles', response.data)
        self.assertIn('Test Role', response.data['roles'])

    def test_get_profile_unauthenticated(self):
        """Тест получения профиля неаутентифицированного пользователя."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
