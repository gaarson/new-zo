import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import SecretStr, BaseModel

from .repository import PostgresAuthRepository
from .auth import get_user_by_username, register_new_user
from .domain import UserRepository, User, UserAlreadyExistsError

logger = logging.getLogger(__name__);

class UserResponse(BaseModel):
    id: int
    username: str

class UserCreate(BaseModel):
    username: str
    password: str

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

def get_repository(request: Request) -> UserRepository:
    """
    Эта зависимость-генератор делает всё в одном месте:
    1. Берёт соединение из пула, хранящегося в app.state.
    2. Создаёт экземпляр репозитория.
    3. Передаёт (yield) его в эндпоинт.
    4. Гарантированно возвращает соединение в пул после отработки эндпоинта.
    """
    pool = request.app.state.pool
    connection = None
    try:
        connection = pool.getconn()
        repo = PostgresAuthRepository(connection)
        yield repo
    finally:
        if connection:
            pool.putconn(connection)

@router.post("/users", response_model=UserResponse, status_code=201)
def create_user_endpoint(
    user_data: UserCreate,
    user_repo: UserRepository = Depends(get_repository)
):
    try:
        new_user_domain = register_new_user(
            username=user_data.username,
            password=user_data.password,
            user_repo=user_repo
        )

        logger.info(f"User '{user_data.username}' created successfully with ID {new_user_domain.id}")

        return UserResponse(id=new_user_domain.id, username=new_user_domain.username)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e)) # 409 Conflict

@router.get("/users/{username}", response_model=UserResponse)
def get_user_endpoint(
    username: str,
    user_repo: UserRepository = Depends(get_repository)
):
    user_domain = get_user_by_username(username=username, user_repo=user_repo)
    if user_domain:
        return UserResponse(id=user_domain.id, username=user_domain.username)
    
    raise HTTPException(status_code=404, detail="User not found")

