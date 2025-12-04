from abc import ABC, abstractmethod
from typing import List

class User:
    def __init__(
        self, 
        id: int, 
        username: str, 
        password_hash: str = None,
        roles: List[str] = None
    ):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.roles = roles if roles is not None else ['user']

class UserAlreadyExistsError(Exception):
    pass

class UserRepository(ABC):
    @abstractmethod
    def find_by_username(self, username: str) -> User | None: ...
    def create_new_user(self, userdata: User) -> User | None: ...
