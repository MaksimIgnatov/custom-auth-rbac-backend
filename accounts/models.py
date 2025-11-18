import bcrypt
from django.contrib.auth.hashers import (
    check_password as django_check_password,
    make_password,
)
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя."""
    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'users'

    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"

    def set_password(self, raw_password):
        """Хеширование пароля с помощью bcrypt."""
        if raw_password:
            # Используем bcrypt для хеширования
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(raw_password.encode('utf-8'), salt)
            # Сохраняем с префиксом для идентификации
            self.password = f'bcrypt${hashed.decode("utf-8")}'
        else:
            self.password = make_password(None)

    def check_password(self, raw_password):
        """Проверка пароля с поддержкой bcrypt и стандартного Django."""
        if not raw_password:
            return False

        # Проверяем, используется ли bcrypt
        if self.password.startswith('bcrypt$'):
            try:
                hashed = self.password.replace('bcrypt$', '')
                return bcrypt.checkpw(
                    raw_password.encode('utf-8'),
                    hashed.encode('utf-8')
                )
            except (ValueError, AttributeError):
                return False
        else:
            # Используем стандартный метод Django
            return django_check_password(raw_password, self.password)
