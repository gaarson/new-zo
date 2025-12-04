import os

from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from .domain import User, UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not SECRET_KEY:
    raise EnvironmentError("JWT_SECRET_KEY не установлен в переменных окружения")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет обычный пароль против хэша."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Создает хэш пароля."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Создает JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    # 'iat' (issued at) - время выпуска
    to_encode.update({"iat": datetime.now(timezone.utc)})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_username(username: str, user_repo: UserRepository) -> User | None:
    user = user_repo.find_by_username(username)
    return user

def register_new_user(
    username: str,
    password: str,
    user_repo: UserRepository
) -> User:
    password_hash = get_password_hash(password) 

    new_user_data = User(id=None, username=username, password_hash=password_hash)
    created_user = user_repo.create_new_user(new_user_data)

    if created_user is None:
        raise Exception("Ошибка создания пользователя")

    return created_user

def authenticate_user(
    username: str, 
    password: str, 
    user_repo: UserRepository
) -> User | None:
    """
    Проверяет учетные данные пользователя.
    Возвращает User, если аутентификация прошла, иначе None.
    """
    user = get_user_by_username(username, user_repo)

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
