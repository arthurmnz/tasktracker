from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db_dep
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import LoginRequest, Token
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository

router = APIRouter()


@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db_dep)):
    existing = await UserRepository.get_by_email(db, user_in.email)

    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')
    
    user = await AuthService.register(db, user_in)
    return user

@router.post('/login', response_model=Token)
async def login(login_in: LoginRequest, db: AsyncSession = Depends(get_db_dep)):
    token = await AuthService.authenticate(db, login_in.email, login_in.password)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    return token
