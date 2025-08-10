# auth.py (улучшенная версия)
import bcrypt
from .domain import User, UserRepository

def get_user_by_username(username: str, user_repo: UserRepository) -> User | None:
    user = user_repo.find_by_username(username)
    return user

def register_new_user(
    username: str,
    password: str,
    user_repo: UserRepository
) -> User:
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user_data = User(id=None, username=username, password_hash=password_hash)

    created_user = user_repo.create_new_user(new_user_data)
    
    if created_user is None:
        raise ValueError("User already exists")

    return created_user
