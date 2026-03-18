from datetime import timedelta
from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    @staticmethod
    async def register(session: AsyncSession, user_in: UserCreate):
        password_hash = get_password_hash(user_in.password)
        user = await UserRepository.create(session, name=user_in.name, email=user_in.email, password_hash=password_hash)
        return user

    @staticmethod
    async def authenticate(session: AsyncSession, email: str, password: str):
        user = await UserRepository.get_by_email(session, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        access_token = create_access_token(str(user.id))
        return {"access_token": access_token, "token_type": "bearer"}
