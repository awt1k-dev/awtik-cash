import asyncio
from app.db.database import SessionLocal
from app.crud.users import get_user_by_id

async def make_admin(user_id: int):
    async with SessionLocal() as db:
        user = await get_user_by_id(db, user_id)
        
        if not user:
            print(f"Ошибка: Пользователь с ID {user_id} не найден.")
            return

        user.role = 'admin'
    
        await db.commit() 
        await db.refresh(user)
        
        print(f"Успех: Пользователь {user.username} теперь админ.")

if __name__ == "__main__":
    asyncio.run(make_admin(4))