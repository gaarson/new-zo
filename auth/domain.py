from abc import ABC, abstractmethod

class User:
    def __init__(self, id: int, username: str, password_hash: str = None):
        self.id = id
        self.username = username
        self.password_hash = password_hash

class UserAlreadyExistsError(Exception):
    pass

class UserRepository(ABC):
    @abstractmethod
    def find_by_username(self, username: str) -> User | None: ...
    def create_new_user(self, userdata: User) -> User | None: ...
