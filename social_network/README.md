# Social Network User Management API

REST API для регистрации и аутентификации пользователей в системе социальной сети.

## Архитектура

Система состоит из двух сервисов:

1. **API Gateway** (порт 8000) - проксирует запросы к сервису пользователей
2. **User Service** (порт 8001) - обрабатывает пользователей и аутентификацию
3. **PostgreSQL** (порт 5434) - база данных для хранения пользователей

## Функционал

### Регистрация и аутентификация
- ✅ Регистрация нового пользователя (логин, пароль, email)
- ✅ Аутентификация по логину/email и паролю
- ✅ JWT токены для авторизации
- ✅ Хеширование паролей с bcrypt

### Управление профилем
- ✅ Получение данных профиля
- ✅ Обновление профиля (имя, фамилия, дата рождения, телефон)
- ✅ Логин и пароль нельзя изменить
- ✅ Автоматическое отслеживание дат создания и обновления

### Валидация
- ✅ Валидация всех входных данных
- ✅ Проверка уникальности username и email
- ✅ Валидация формата email
- ✅ Ограничения на длину полей

## Быстрый старт

### 1. Запуск через Docker Compose

```bash
# Клонируйте репозиторий и перейдите в директорию
cd social_network

# Запустите все сервисы
docker-compose up --build

# Сервисы будут доступны по адресам:
# API Gateway: http://localhost:8000
# User Service: http://localhost:8001
# PostgreSQL: localhost:5434
```

### 2. Проверка работы

```bash
# Проверка здоровья API Gateway
curl http://localhost:8000/health

# Проверка здоровья User Service
curl http://localhost:8001/health

# Регистрация пользователя
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword123",
    "email": "test@example.com"
  }'

# Аутентификация
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword123"
  }'
```

## API Endpoints

### API Gateway (http://localhost:8000)

| Метод | Endpoint | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/register` | Регистрация пользователя | Нет |
| POST | `/login` | Аутентификация | Нет |
| GET | `/profile` | Получение профиля | Да |
| PUT | `/profile` | Обновление профиля | Да |
| GET | `/users` | Список пользователей | Нет |
| GET | `/health` | Проверка здоровья | Нет |

### User Service (http://localhost:8001)

| Метод | Endpoint | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/api/v1/register` | Регистрация пользователя | Нет |
| POST | `/api/v1/login` | Аутентификация | Нет |
| GET | `/api/v1/profile` | Получение профиля | Да |
| PUT | `/api/v1/profile` | Обновление профиля | Да |
| GET | `/api/v1/users` | Список пользователей | Нет |
| GET | `/api/v1/health` | Проверка здоровья | Нет |

## Тестирование

### 1. Автоматические тесты

```bash
# Тесты User Service
cd social_network/user_service
pip install -r tests/requirements.txt
pytest tests/

# Тесты API Gateway
cd social_network/api_gateway
pip install -r tests/requirements.txt
pytest tests/
```

### 2. Ручное тестирование

Используйте файл `test_requests.http` для тестирования API через HTTP клиент (например, VS Code REST Client).

### 3. OpenAPI документация

- API Gateway: http://localhost:8000/docs
- User Service: http://localhost:8001/docs

## Структура проекта

```
social_network/
├── api_gateway/                 # API Gateway сервис
│   ├── app/
│   │   ├── main.py             # Основное приложение
│   │   ├── auth.py             # JWT аутентификация
│   │   └── schemas.py          # Pydantic схемы
│   ├── tests/                  # Тесты
│   ├── Dockerfile
│   └── requirements.txt
├── user_service/               # User Service
│   ├── app/
│   │   ├── main.py             # Основное приложение
│   │   ├── handlers.py         # Обработчики запросов
│   │   ├── models.py           # SQLAlchemy модели
│   │   ├── schemas.py          # Pydantic схемы
│   │   └── auth.py             # Аутентификация и хеширование
│   ├── tests/                  # Тесты
│   ├── Dockerfile
│   └── requirements.txt
├── api_specification.yaml      # OpenAPI спецификация
├── test_requests.http          # Тестовые запросы
├── docker-compose.yaml         # Docker Compose конфигурация
└── README.md
```

## Переменные окружения

### API Gateway
- `USER_SERVICE_URL` - URL сервиса пользователей (по умолчанию: http://user_service:8001)
- `SECRET_KEY` - Секретный ключ для JWT (по умолчанию: your-secret-key-here-change-in-production)

### User Service
- `DATABASE_URL` - URL базы данных PostgreSQL
- `SECRET_KEY` - Секретный ключ для JWT

## База данных

### Модель User

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| username | String(50) | Уникальное имя пользователя |
| email | String(100) | Уникальный email |
| password_hash | String(255) | Хеш пароля |
| first_name | String(50) | Имя |
| last_name | String(50) | Фамилия |
| birth_date | Date | Дата рождения |
| phone | String(20) | Номер телефона |
| created_at | DateTime | Дата создания |
| updated_at | DateTime | Дата обновления |

## Безопасность

- Пароли хешируются с помощью bcrypt
- JWT токены для авторизации
- Валидация всех входных данных
- CORS настроен для разработки

## Мониторинг

- Health check endpoints для всех сервисов
- Логирование через FastAPI
- Health checks в Docker Compose

## Разработка

### Локальная разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск User Service
cd social_network/user_service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Запуск API Gateway
cd social_network/api_gateway
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Добавление новых функций

1. Обновите модели в `user_service/app/models.py`
2. Добавьте схемы в `user_service/app/schemas.py`
3. Реализуйте обработчики в `user_service/app/handlers.py`
4. Добавьте проксирование в `api_gateway/app/main.py`
5. Обновите OpenAPI спецификацию
6. Напишите тесты
7. Обновите документацию
