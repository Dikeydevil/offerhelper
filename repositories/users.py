from typing import Optional, Sequence

from .base import BaseRepository
from models.users import User
from services.auth import AuthService


auth_service = AuthService()


class UsersRepository(BaseRepository):
    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def create(self, email: str, password: str) -> User:
        user = User(
            email=email,
            hashed_password=auth_service.hash_password(password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(email)
        if not user:
            return None
        if not auth_service.verify_password(password, user.hashed_password):
            return None
        return user

    def list_users(
            self,
            skip: int = 0,
            limit: int = 50,
    ) -> Sequence[User]:
        return (
            self.db.query(User)
            .order_by(User.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def set_random_password(self, user: User) -> str:
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits
        plain = "".join(secrets.choice(alphabet) for _ in range(12))

        user.hashed_password = auth_service.hash_password(plain)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return plain
