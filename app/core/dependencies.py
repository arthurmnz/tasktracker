from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.db.database import get_db
from app.repositories.user_repository import UserRepository
from app.core.security import decode_access_token
from sqlalchemy.ext.asyncio import AsyncSession

http_bearer = HTTPBearer()

async def get_db_dep():
    async for s in get_db():
        yield s


async def get_current_user(credential: str = Depends(http_bearer), db: AsyncSession = Depends(get_db_dep)):
    
    
    try:
        token = credential.credentials 
        payload = decode_access_token(token)
        user_id = payload.get('sub')
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    user = await UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
