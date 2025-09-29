from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .handlers import router

app = FastAPI(
    title="User Service",
    description="Сервис для управления пользователями, регистрации и аутентификации",
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

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "User Service API", "version": "1.0.0"}