import psycopg2.errors

from .domain import User, UserRepository, UserAlreadyExistsError

class PostgresAuthRepository(UserRepository):
    def __init__(self, connection):
        self._connection = connection

    def find_by_username(self, username: str) -> User | None:
        conn = self._connection
        with conn.cursor() as cur:
            cur.execute("SELECT id, username, password_hash, roles FROM users WHERE username = %s", (username,))
            row = cur.fetchone()
            if not row:
                return None
            return User(id=row[0], username=row[1], password_hash=row[2], roles=row[3])

    def create_new_user(self, userdata: User) -> User:
        conn = self._connection
        with conn.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO users (username, password_hash) 
                    VALUES (%s, %s)
                    RETURNING id, username, roles
                """, (userdata.username, userdata.password_hash))
                row = cur.fetchone()

                if row is None:
                    raise Exception("Cannot create new user")

                new_user = User(id=row[0], username=row[1], roles=row[2])

                conn.commit()

                return new_user
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                raise UserAlreadyExistsError(f"User with username '{userdata.username}' already exists")
