import asyncio
from app.db.database import SessionLocal # Импортируем фабрику сессий
from app.crud.users import get_user_by_id

async def make_admin(user_id: int):
    # Создаем асинхронную сессию вручную[cite: 3]
    async with SessionLocal() as db:
        user = await get_user_by_id(db, user_id)
        
        if not user:
            print(f"Ошибка: Пользователь с ID {user_id} не найден.")
            return

        user.role = 'admin' # Меняем роль в объекте
        
        # Обязательно await для асинхронных методов алхимии
        await db.commit() 
        await db.refresh(user)
        
        print(f"Успех: Пользователь {user.username} теперь админ.")

if __name__ == "__main__":
    asyncio.run(make_admin(4))