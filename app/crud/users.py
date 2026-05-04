from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.models import User
from passlib.context import CryptContext
from app.schemas import UserRegisterSchema, UserLoginSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_username_or_email(db: AsyncSession, username: str | None = None, email: str | None = None) -> User | None:
    query = select(User).where((User.username == username) | (User.email == email))
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_data: UserRegisterSchema) -> User | bool:
    try:
        hashed_password = pwd_context.hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except:
        return False

async def check_login(db: AsyncSession, user_data: UserLoginSchema) -> int | None:
    """
    If succesfully - returning `user_id`
    """
    user = await get_user_by_username_or_email(db, user_data.login, user_data.login)
    if not user:
        return None
    if pwd_context.verify(user_data.password, user.password_hash):
        return user.id
    return None

async def get_user_with_transactions(db: AsyncSession, user_id: int) -> User | None:
    query = (
        select(User)
        .options(selectinload(User.transactions))
        .where(User.id == user_id)
    )
    
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    query = (
        select(User)
        .where(User.id == user_id)
    )
    user = await db.execute(query)
    return user.scalar_one_or_none()