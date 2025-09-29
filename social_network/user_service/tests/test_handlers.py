import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base, get_db, User
from app.auth import get_password_hash

# Создаем тестовую базу данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Создаем таблицы для тестов
Base.metadata.create_all(bind=engine)

client = TestClient(app)

class TestUserRegistration:
    """Тесты для регистрации пользователей"""
    
    def setup_method(self):
        """Очистка базы данных перед каждым тестом"""
        db = TestingSessionLocal()
        db.query(User).delete()
        db.commit()
        db.close()
    
    def test_register_user_success(self):
        """Тест успешной регистрации пользователя"""
        user_data = {
            "username": "testuser",
            "password": "testpassword123",
            "email": "test@example.com"
        }
        
        response = client.post("/api/v1/register", json=user_data)
        
        assert response.status_code == 201
        assert response.json()["message"] == "User registered successfully"
    
    def test_register_user_duplicate_username(self):
        """Тест регистрации с дублирующимся username"""
        user_data = {
            "username": "testuser",
            "password": "testpassword123",
            "email": "test@example.com"
        }
        
        # Первая регистрация
        response1 = client.post("/api/v1/register", json=user_data)
        assert response1.status_code == 201
        
        # Вторая регистрация с тем же username
        user_data["email"] = "test2@example.com"
        response2 = client.post("/api/v1/register", json=user_data)
        
        assert response2.status_code == 400
        assert "Username already exists" in response2.json()["detail"]
    
    def test_register_user_duplicate_email(self):
        """Тест регистрации с дублирующимся email"""
        user_data = {
            "username": "testuser",
            "password": "testpassword123",
            "email": "test@example.com"
        }
        
        # Первая регистрация
        response1 = client.post("/api/v1/register", json=user_data)
        assert response1.status_code == 201
        
        # Вторая регистрация с тем же email
        user_data["username"] = "testuser2"
        response2 = client.post("/api/v1/register", json=user_data)
        
        assert response2.status_code == 400
        assert "Email already exists" in response2.json()["detail"]
    
    def test_register_user_invalid_data(self):
        """Тест регистрации с невалидными данными"""
        # Слишком короткий username
        user_data = {
            "username": "ab",  # Меньше 3 символов
            "password": "testpassword123",
            "email": "test@example.com"
        }
        
        response = client.post("/api/v1/register", json=user_data)
        assert response.status_code == 422  # Validation error
        
        # Слишком короткий пароль
        user_data = {
            "username": "testuser",
            "password": "123",  # Меньше 8 символов
            "email": "test@example.com"
        }
        
        response = client.post("/api/v1/register", json=user_data)
        assert response.status_code == 422  # Validation error
        
        # Невалидный email
        user_data = {
            "username": "testuser",
            "password": "testpassword123",
            "email": "invalid-email"
        }
        
        response = client.post("/api/v1/register", json=user_data)
        assert response.status_code == 422  # Validation error

class TestUserLogin:
    """Тесты для аутентификации пользователей"""
    
    def setup_method(self):
        """Создание тестового пользователя перед каждым тестом"""
        db = TestingSessionLocal()
        db.query(User).delete()
        
        # Создаем тестового пользователя
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash=get_password_hash("testpassword123")
        )
        db.add(test_user)
        db.commit()
        db.close()
    
    def test_login_success(self):
        """Тест успешной аутентификации"""
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"
        assert data["user"]["email"] == "test@example.com"
    
    def test_login_with_email(self):
        """Тест аутентификации по email"""
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == "testuser"
    
    def test_login_wrong_password(self):
        """Тест аутентификации с неправильным паролем"""
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self):
        """Тест аутентификации несуществующего пользователя"""
        login_data = {
            "username": "nonexistent",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

class TestUserProfile:
    """Тесты для работы с профилем пользователя"""
    
    def setup_method(self):
        """Создание тестового пользователя и токена"""
        db = TestingSessionLocal()
        db.query(User).delete()
        
        # Создаем тестового пользователя
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash=get_password_hash("testpassword123"),
            first_name="Test",
            last_name="User"
        )
        db.add(test_user)
        db.commit()
        db.close()
        
        # Получаем токен для тестов
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/login", json=login_data)
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_profile_success(self):
        """Тест получения профиля"""
        response = client.get("/api/v1/profile", headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
    
    def test_get_profile_unauthorized(self):
        """Тест получения профиля без авторизации"""
        response = client.get("/api/v1/profile")
        
        assert response.status_code == 403  # No authorization header
    
    def test_update_profile_success(self):
        """Тест обновления профиля"""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "+1234567890"
        }
        
        response = client.put("/api/v1/profile", json=update_data, headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["phone"] == "+1234567890"
    
    def test_update_profile_partial(self):
        """Тест частичного обновления профиля"""
        update_data = {
            "phone": "+9876543210"
        }
        
        response = client.put("/api/v1/profile", json=update_data, headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Test"  # Не изменилось
        assert data["last_name"] == "User"   # Не изменилось
        assert data["phone"] == "+9876543210"  # Изменилось