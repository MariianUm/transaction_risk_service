# app/services/auth.py
import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.databases.users import user_crud
from app.schemas.users import UserCreate
from app.models.users import UserModel
from app.core.security import verify_password, get_username_from_session_cookie

logger = logging.getLogger(__name__)

async def register_new_user(db: AsyncSession, user_in: UserCreate) -> UserModel:
    logger.info(f"Попытка зарегистрировать нового пользователя: {user_in.username}")
    try:
        db_user = await user_crud.get_user_by_username(db, username=user_in.username)
        if db_user:
            logger.warning(f"Имя пользователя уже зарегистрировано: {user_in.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя пользователя уже зарегистрировано"
            )
        new_user = await user_crud.add(db=db, user_in=user_in)
        logger.info(f"Пользователь {user_in.username} успешно зарегистрирован")
        return new_user
    except Exception as e:
        logger.error(f"Ошибка регистрации: {str(e)}")
        raise

async def authenticate_user(db: AsyncSession, username: str, password: str) -> UserModel | None:
    logger.info(f"Попытка аутентификации пользователя: {username}")
    try:
        user = await user_crud.get_user_by_username(db, username=username)
        if not user:
            logger.warning(f"Пользователь не найден: {username}")
            return None
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Некорректный пароль: {username}")
            return None
        logger.info(f"Успешная аутентификация: {username}")
        return user
    except Exception as e:
        logger.error(f"Ошибка аутентификации: {str(e)}")
        return None

async def get_current_user(request, db: AsyncSession):
    logger.debug("Проверка текущего пользователя")
    try:
        session_id = request.cookies.get("auth_session")
        if not session_id:
            logger.warning("No session cookie found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не аутентифицирован (нет сессионной cookie)",
                headers={"WWW-Authenticate": "Cookie"},
            )

        username = get_username_from_session_cookie(session_id)
        if username is None:
            logger.warning("Invalid or expired session cookie")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительная или истекшая сессия",
                headers={"WWW-Authenticate": "Cookie"},
            )

        user = await user_crud.get_user_by_username(db, username=username)
        if user is None:
            logger.warning(f"User not found for session: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь для сессии не найден",
                headers={"WWW-Authenticate": "Cookie"},
            )
        logger.debug(f"Current user: {username}")
        return user
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise