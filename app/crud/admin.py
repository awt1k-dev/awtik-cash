from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import User, Transaction
from app.crud.users import get_user_by_id
from app.schemas import UserEditSchema

async def is_admin(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    
    if user.role == 'admin':
        return True
    else:
        return False

async def get_all_users(db: AsyncSession) -> tuple:
    query = (
        select(
            User, 
            func.count(Transaction.id).label("tx_count")
        )
        .outerjoin(Transaction)
        .group_by(User.id)
    )
    result = await db.execute(query)
    return result.all()

async def get_user_by_id_with_tx(db: AsyncSession, user_id: int) -> User | None:
    query = (
        select(
            User, 
            func.count(Transaction.id).label("tx_count")
        )
        .outerjoin(Transaction)
        .group_by(User.id)
        .where(User.id == user_id)
    )
    result = await db.execute(query)
    return result.one_or_none()

async def edit_user(db: AsyncSession, user_id: int, user_data: UserEditSchema) -> bool:
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    user.email = user_data.email
    user.username = user_data.username
    user.role = user_data.role

    await db.commit()
    await db.refresh(user)
    return True

async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    
    await db.delete(user)
    await db.commit()
    return True