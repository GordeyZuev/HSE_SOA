import httpx
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .schemas import (
    RegisterRequest, LoginRequest, ProfileUpdateRequest, 
    TokenResponse, UserResponse, MessageResponse
)
import os

app = FastAPI(
    title="API Gateway",
    description="API Gateway для проксирования запросов к сервису пользователей",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8001")
security = HTTPBearer()

async def proxy_request(method: str, endpoint: str, data: dict = None, headers: dict = None):
    """Проксирование запроса к сервису пользователей"""
    url = f"{USER_SERVICE_URL}/api/v1{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = await client.put(url, json=data, headers=headers)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            return response.json(), response.status_code
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

@app.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Регистрация нового пользователя"""
    import httpx
    try:
        data, status_code = await proxy_request("POST", "/register", request.model_dump(mode='json'), None)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    
    if status_code != 201:
        raise HTTPException(status_code=status_code, detail=data.get("detail", "Registration failed"))
    
    return MessageResponse(message=data["message"])

@app.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Аутентификация пользователя"""
    import httpx
    try:
        data, status_code = await proxy_request("POST", "/login", request.model_dump(mode='json'), None)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=data.get("detail", "Login failed"))
    
    return TokenResponse(**data)

@app.get("/profile", response_model=UserResponse)
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Получение профиля текущего пользователя"""
    import httpx
    headers = {"Authorization": f"Bearer {credentials.credentials}"}
    try:
        data, status_code = await proxy_request("GET", "/profile", None, headers)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=data.get("detail", "Failed to get profile"))
    
    return UserResponse(**data)

@app.put("/profile", response_model=UserResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Обновление профиля пользователя"""
    import httpx
    headers = {"Authorization": f"Bearer {credentials.credentials}"}
    payload = request.model_dump(mode='json', exclude_unset=True, exclude_none=True)
    try:
        data, status_code = await proxy_request("PUT", "/profile", payload, headers)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=data.get("detail", "Failed to update profile"))
    
    return UserResponse(**data)

@app.get("/users", response_model=list[UserResponse])
async def get_users():
    """Получение списка всех пользователей (для тестирования)"""
    import httpx
    try:
        data, status_code = await proxy_request("GET", "/users", None, None)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=data.get("detail", "Failed to get users"))
    
    return [UserResponse(**user) for user in data]

@app.get("/")
async def root():
    return {"message": "API Gateway", "version": "1.0.0"}