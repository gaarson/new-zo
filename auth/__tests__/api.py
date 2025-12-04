# auth/tests/test_api.py
import os # <-- Добавить
from jose import jwt # <-- Добавить

from fastapi.testclient import TestClient

ALGORITHM = os.getenv("ALGORITHM", "HS256")

def test_create_user_success(test_app: TestClient):
    """
    Тест успешного создания пользователя.
    `test_app` - это фикстура из conftest.py.
    """
    response = test_app.post(
        "/auth/users",
        json={"username": "newuser", "password": "strongpassword"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data

def test_create_user_conflict(created_user: dict, test_app: TestClient):
    """
    Тест на конфликт при создании пользователя с существующим именем.
    Фикстура `created_user` уже создала пользователя 'testuser'.
    """
    response = test_app.post(
        "/auth/users",
        json={"username": "testuser", "password": "anotherpassword"}
    )
    
    assert response.status_code == 409 # Conflict

def test_get_user_success(created_user: dict, test_app: TestClient):
    """
    Тест успешного получения пользователя, который уже существует.
    """
    username = created_user["username"]
    response = test_app.get(f"/auth/users/{username}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == username
    assert data["id"] == created_user["id"]

def test_get_user_not_found(test_app: TestClient):
    """
    Тест получения несуществующего пользователя.
    """
    response = test_app.get("/auth/users/nonexistentuser")
    
    assert response.status_code == 404


def test_login_success_and_token_content(created_user: dict, test_app: TestClient):
    """
    Тест успешного входа.
    Проверяет статус 200, наличие токена и его содержимое (payload).
    Фикстура `created_user` создает 'testuser' с паролем 'testpassword'.
    """
    
    # ВАЖНО: OAuth2PasswordRequestForm ожидает "form data",
    # а НЕ JSON. Поэтому используем `data=`, а не `json=`.
    response = test_app.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    
    # 1. Проверяем успешный ответ
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # 2. (Продвинутая проверка) Декодируем токен и проверяем его payload
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    assert SECRET_KEY is not None, "JWT_SECRET_KEY не найден в окружении"
    
    token = data["access_token"]
    
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )
    
    # 'sub' (subject) должен содержать ID пользователя в виде строки
    assert payload["sub"] == str(created_user["id"])
    assert payload["roles"] == ["user"]
    # (Опционально) Проверяем 'exp' (срок годности), если нужно


def test_login_wrong_password(created_user: dict, test_app: TestClient):
    """
    Тест входа с неверным паролем.
    """
    response = test_app.post(
        "/auth/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_wrong_username(test_app: TestClient):
    """
    Тест входа с несуществующим пользователем.
    """
    response = test_app.post(
        "/auth/token",
        data={"username": "nonexistentuser", "password": "testpassword"}
    )
    
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_missing_field(test_app: TestClient):
    """
    Тест входа с отсутствующим полем (например, без пароля).
    FastAPI должен вернуть 422 Unprocessable Entity.
    """
    response = test_app.post(
        "/auth/token",
        data={"username": "testuser"} # 'password' отсутствует
    )
    
    assert response.status_code == 422 # Ошибка валидации


def test_login_wrong_content_type(test_app: TestClient):
    """
    Тест входа с неправильным Content-Type (JSON вместо form-data).
    FastAPI должен вернуть 422, так как не сможет распарсить OAuth2PasswordRequestForm.
    """
    response = test_app.post(
        "/auth/token",
        # Используем `json=` вместо `data=`, что некорректно для этого эндпоинта
        json={"username": "testuser", "password": "testpassword"} 
    )
    
    assert response.status_code == 422
