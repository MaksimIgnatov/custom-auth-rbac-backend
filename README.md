# Custom Auth RBAC Backend

Система аутентификации и авторизации с ролевой моделью доступа (RBAC) на основе Django REST Framework.

## Описание

Проект представляет собой REST API для управления пользователями и ролями с гибкой системой прав доступа. Система поддерживает:

- Кастомную модель пользователя с email в качестве логина
- JWT аутентификацию
- Ролевую модель доступа (RBAC)
- Гибкую систему прав доступа к бизнес-элементам
- Хеширование паролей с помощью bcrypt

## Технологии

- **Python 3.12**
- **Django 5.2.8**
- **Django REST Framework 3.16.1**
- **PostgreSQL 15** (для production)
- **SQLite** (для разработки)
- **Docker & Docker Compose**

## Структура проекта

```
.
├── accounts/          # Приложение для управления пользователями
│   ├── models.py      # Модель User
│   ├── views.py       # API endpoints для аутентификации
│   ├── serializers.py # Сериализаторы
│   └── tests.py       # Тесты
├── permissions/       # Приложение для управления ролями и правами
│   ├── models.py      # Модели Role, BusinessElement, AccessRoleRule, UserRole
│   ├── views.py       # API endpoints для управления ролями
│   ├── permissions.py # Кастомный класс проверки прав доступа
│   └── tests.py       # Тесты
├── backend/           # Основные настройки проекта
│   ├── settings.py    # Конфигурация Django
│   └── urls.py        # Главный URL router
├── docker-compose.yml # Конфигурация Docker Compose
├── Dockerfile         # Образ Docker для приложения
└── requirements.txt  # Зависимости Python
```

## Установка и запуск

### Вариант 1: Локальная установка

#### 1. Клонирование репозитория

```bash
git clone https://github.com/MaksimIgnatov/custom-auth-rbac-backend.git
cd custom-auth-rbac-backend
```

#### 2. Создание виртуального окружения

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

#### 4. Настройка базы данных

Для разработки используется SQLite (по умолчанию). Если нужно использовать PostgreSQL, раскомментируйте соответствующие настройки в `backend/settings.py` или установите переменные окружения.

#### 5. Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Создание суперпользователя

```bash
python manage.py createsuperuser
```

#### 7. Запуск сервера разработки

```bash
python manage.py runserver
```

API будет доступен по адресу: `http://127.0.0.1:8000/`

### Вариант 2: Запуск через Docker

#### 1. Клонирование репозитория

```bash
git clone https://github.com/MaksimIgnatov/custom-auth-rbac-backend.git
cd custom-auth-rbac-backend
```

#### 2. Запуск контейнеров

```bash
docker-compose up --build
```

Это команда:
- Соберет Docker образ
- Запустит PostgreSQL базу данных
- Применит миграции Django
- Запустит веб-сервер

#### 3. Создание суперпользователя

В другом терминале:

```bash
docker-compose exec web python manage.py createsuperuser
```

#### 4. Доступ к приложению

API будет доступен по адресу: `http://localhost:8000/`

#### 5. Остановка контейнеров

```bash
docker-compose down
```

Для удаления данных базы данных:

```bash
docker-compose down -v
```

## API Endpoints

### Аутентификация

- `POST /api/auth/register/` - Регистрация нового пользователя
- `POST /api/auth/login/` - Вход в систему
- `POST /api/auth/logout/` - Выход из системы
- `GET /api/auth/profile/` - Получение профиля текущего пользователя
- `POST /api/token/refresh/` - Обновление JWT токена

### Управление ролями и правами

- `GET /api/permissions/roles/` - Список ролей
- `POST /api/permissions/roles/` - Создание роли
- `GET /api/permissions/business-elements/` - Список бизнес-элементов
- `POST /api/permissions/business-elements/` - Создание бизнес-элемента
- `GET /api/permissions/access-rules/` - Список правил доступа
- `POST /api/permissions/access-rules/` - Создание правила доступа
- `GET /api/permissions/user-roles/` - Список ролей пользователей
- `POST /api/permissions/user-roles/assign/` - Назначение роли пользователю
- `DELETE /api/permissions/user-roles/remove/` - Удаление роли у пользователя

## Примеры использования API

### Регистрация пользователя

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user",
    "first_name": "Иван",
    "last_name": "Иванов",
    "password": "password123",
    "password_confirm": "password123"
  }'
```

### Вход в систему

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Ответ содержит JWT токены:
```json
{
  "user": {...},
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Использование токена для доступа к API

```bash
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Создание роли

```bash
curl -X POST http://127.0.0.1:8000/api/permissions/roles/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Менеджер",
    "description": "Роль менеджера"
  }'
```

## Тестирование

### Запуск тестов

```bash
python manage.py test
```

### Проверка покрытия кода

```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

Текущее покрытие кода: **более 88%**

## Настройка прав доступа

### 1. Создание бизнес-элементов

Бизнес-элементы определяют сущности системы, к которым применяются права доступа:

```bash
POST /api/permissions/business-elements/
{
  "name": "users",
  "description": "Пользователи системы"
}
```

### 2. Создание правил доступа

Правила доступа связывают роли с бизнес-элементами и определяют права:

```bash
POST /api/permissions/access-rules/
{
  "role": 1,
  "element": 1,
  "read_permission": true,
  "read_all_permission": false,
  "create_permission": true,
  "update_permission": true,
  "update_all_permission": false,
  "delete_permission": false,
  "delete_all_permission": false
}
```

### 3. Назначение роли пользователю

```bash
POST /api/permissions/user-roles/assign/
{
  "user_id": 1,
  "role_id": 1
}
```

## Переменные окружения

Для настройки через переменные окружения:

- `SECRET_KEY` - Секретный ключ Django
- `DEBUG` - Режим отладки (True/False)
- `ALLOWED_HOSTS` - Разрешенные хосты (через запятую)
- `DATABASE_URL` - URL базы данных (для использования PostgreSQL)
- `POSTGRES_DB` - Имя базы данных PostgreSQL
- `POSTGRES_USER` - Пользователь PostgreSQL
- `POSTGRES_PASSWORD` - Пароль PostgreSQL
- `POSTGRES_HOST` - Хост PostgreSQL
- `POSTGRES_PORT` - Порт PostgreSQL

## Админ-панель Django

Доступ к админ-панели: `http://127.0.0.1:8000/admin/`

Используйте учетные данные суперпользователя, созданного через `createsuperuser`.

## Разработка

### Структура кода

Код соответствует стандартам PEP8. Для проверки:

```bash
pip install flake8
flake8 .
```

### Миграции

При изменении моделей:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Лицензия

MIT License

## Автор

Maksim Ignatov

## Контакты

GitHub: [MaksimIgnatov](https://github.com/MaksimIgnatov)

