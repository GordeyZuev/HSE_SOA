import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAPIGateway:
    """Тесты для API Gateway"""
    
    @patch('app.main.proxy_request')
    def test_register_success(self, mock_proxy):
        """Тест успешной регистрации через API Gateway"""
        # Настраиваем мок
        mock_proxy.return_value = ({"message": "User registered successfully"}, 201)
        
        user_data = {
            "username": "testuser",
            "password": "testpassword123",
            "email": "test@example.com"
        }
        
        response = client.post("/register", json=user_data)
        
        assert response.status_code == 201
        assert response.json()["message"] == "User registered successfully"
        mock_proxy.assert_called_once_with("POST", "/register", user_data, None)
    
    @patch('app.main.proxy_request')
    def test_register_failure(self, mock_proxy):
        """Тест неудачной регистрации через API Gateway"""
        # Настраиваем мок для ошибки
        mock_proxy.return_value = ({"detail": "Username already exists"}, 400)
        
        user_data = {
            "username": "testuser",
            "password": "testpassword123",
            "email": "test@example.com"
        }
        
        response = client.post("/register", json=user_data)
        
        assert response.status_code == 400
        assert "Username already exists" in response.json()["detail"]
    
    @patch('app.main.proxy_request')
    def test_login_success(self, mock_proxy):
        """Тест успешной аутентификации через API Gateway"""
        # Настраиваем мок
        mock_response = {
            "access_token": "test_token",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "first_name": None,
                "last_name": None,
                "birth_date": None,
                "phone": None,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }
        mock_proxy.return_value = (mock_response, 200)
        
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = client.post("/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test_token"
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"
        mock_proxy.assert_called_once_with("POST", "/login", login_data, None)
    
    @patch('app.main.proxy_request')
    def test_get_profile_success(self, mock_proxy):
        """Тест успешного получения профиля через API Gateway"""
        # Настраиваем мок
        mock_response = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "birth_date": None,
            "phone": None,
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z"
        }
        mock_proxy.return_value = (mock_response, 200)
        
        headers = {"Authorization": "Bearer test_token"}
        response = client.get("/profile", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["first_name"] == "Test"
        mock_proxy.assert_called_once_with("GET", "/profile", None, headers)
    
    @patch('app.main.proxy_request')
    def test_update_profile_success(self, mock_proxy):
        """Тест успешного обновления профиля через API Gateway"""
        # Настраиваем мок
        mock_response = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Updated",
            "last_name": "Name",
            "birth_date": None,
            "phone": "+1234567890",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:30:00Z"
        }
        mock_proxy.return_value = (mock_response, 200)
        
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "+1234567890"
        }
        
        headers = {"Authorization": "Bearer test_token"}
        response = client.put("/profile", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["phone"] == "+1234567890"
        mock_proxy.assert_called_once_with("PUT", "/profile", update_data, headers)
    
    @patch('app.main.proxy_request')
    def test_get_users_success(self, mock_proxy):
        """Тест успешного получения списка пользователей через API Gateway"""
        # Настраиваем мок
        mock_response = [
            {
                "id": 1,
                "username": "testuser1",
                "email": "test1@example.com",
                "first_name": "Test",
                "last_name": "User1",
                "birth_date": None,
                "phone": None,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            },
            {
                "id": 2,
                "username": "testuser2",
                "email": "test2@example.com",
                "first_name": "Test",
                "last_name": "User2",
                "birth_date": None,
                "phone": None,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        ]
        mock_proxy.return_value = (mock_response, 200)
        
        response = client.get("/users")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["username"] == "testuser1"
        assert data[1]["username"] == "testuser2"
        mock_proxy.assert_called_once_with("GET", "/users", None, None)
    
    def test_root_endpoint(self):
        """Тест корневого эндпоинта"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "API Gateway"
        assert data["version"] == "1.0.0"
    
    @patch('app.main.proxy_request')
    def test_service_unavailable(self, mock_proxy):
        """Тест обработки недоступности сервиса"""
        # Настраиваем мок для ошибки соединения
        import httpx
        mock_proxy.side_effect = httpx.RequestError("Connection failed")
        
        user_data = {
            "username": "testuser",
            "password": "testpassword123",
            "email": "test@example.com"
        }
        
        response = client.post("/register", json=user_data)
        
        assert response.status_code == 503
        assert "Service unavailable" in response.json()["detail"]
