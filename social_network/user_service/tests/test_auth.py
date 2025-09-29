import pytest
from datetime import datetime, timedelta
from app.auth import (
    verify_password, get_password_hash, create_access_token, 
    verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
)

class TestPasswordHashing:
    """Тесты для хеширования паролей"""
    
    def test_password_hashing(self):
        """Тест хеширования пароля"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert verify_password(password, hashed)
    
    def test_password_verification_correct(self):
        """Тест проверки правильного пароля"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_password_verification_incorrect(self):
        """Тест проверки неправильного пароля"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

class TestJWTToken:
    """Тесты для JWT токенов"""
    
    def test_create_access_token(self):
        """Тест создания JWT токена"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_expiry(self):
        """Тест создания JWT токена с кастомным временем истечения"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token_valid(self):
        """Тест проверки валидного токена"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        username = verify_token(token)
        assert username == "testuser"
    
    def test_verify_token_invalid(self):
        """Тест проверки невалидного токена"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):  # HTTPException
            verify_token(invalid_token)
    
    def test_verify_token_expired(self):
        """Тест проверки истекшего токена"""
        data = {"sub": "testuser"}
        # Создаем токен с истекшим временем
        expired_time = datetime.utcnow() - timedelta(minutes=1)
        data["exp"] = expired_time
        
        # Создаем токен вручную с истекшим временем
        from jose import jwt
        import os
        SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
        ALGORITHM = "HS256"
        
        expired_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        
        with pytest.raises(Exception):  # HTTPException
            verify_token(expired_token)
