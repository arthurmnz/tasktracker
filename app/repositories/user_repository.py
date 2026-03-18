from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from typing import Optional


class UserRepository:
    @staticmethod
    async def create(session: AsyncSession, name: str, email: str, password_hash: str) -> User:
        user = User(name=name, email=email, password_hash=password_hash)
        session.add(user)
        await session.flush()
        return user

    @staticmethod
    async def get_by_email(session: AsyncSession, email: str) -> Optional[User]:
        q = select(User).where(User.email == email)
        res = await session.execute(q)
        return res.scalars().first()

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id) -> Optional[User]:
        q = select(User).where(User.id == user_id)
        res = await session.execute(q)
        return res.scalars().first()
