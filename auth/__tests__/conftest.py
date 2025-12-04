# auth/tests/conftest.py
import os
import pytest
from fastapi.testclient import TestClient
from psycopg2.pool import SimpleConnectionPool

# Переключаем приложение на использование тестовой БД ПЕРЕД импортом
os.environ['DB_NAME'] = os.getenv('DB_NAME', 'auth_test')
os.environ['DB_USER'] = os.getenv('DB_USER', 'testuser')
os.environ['DB_PASSWORD'] = os.getenv('DB_PASSWORD', 'testsecret')
os.environ['DB_HOST'] = os.getenv('DB_HOST', 'postgres-auth-test')

from auth.main import app
from auth.http import get_repository
from auth.repository import PostgresAuthRepository


# --- Фикстура для пула соединений с ТЕСТОВОЙ базой ---
@pytest.fixture(scope="session")
def db_pool():
    dsn = f"dbname={os.environ['DB_NAME']} user={os.environ['DB_USER']} password={os.environ['DB_PASSWORD']} host={os.environ['DB_HOST']}"
    pool = SimpleConnectionPool(minconn=1, maxconn=1, dsn=dsn)
    yield pool
    pool.closeall()


# --- Фикстура для ОДНОГО соединения на тест ---
@pytest.fixture
def db_connection(db_pool):
    connection = db_pool.getconn()
    yield connection
    # Очищаем таблицы после каждого теста для изоляции
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE;")
    connection.commit()
    db_pool.putconn(connection)


# --- Фикстура, которая подменяет зависимость и возвращает тестовый репозиторий ---
@pytest.fixture
def test_repo(db_connection):
    return PostgresAuthRepository(db_connection)


# --- Фикстура для тестового клиента API ---
@pytest.fixture
def test_app(test_repo):
    # Вот магия: мы подменяем зависимость `get_repository` нашей тестовой фикстурой
    app.dependency_overrides[get_repository] = lambda: test_repo
    
    with TestClient(app) as client:
        yield client
    
    # Очищаем подмену после теста
    app.dependency_overrides.clear()


# --- Пример фикстуры с данными ---
@pytest.fixture
def created_user(test_app):
    """Фикстура, которая создает пользователя через API и возвращает его данные."""
    user_data = {"username": "testuser", "password": "testpassword"}
    response = test_app.post("/auth/users", json=user_data)
    assert response.status_code == 201
    return response.json()
