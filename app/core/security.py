from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.admin import is_admin

async def check_auth(request: Request, db: AsyncSession) -> str | int:
    if not "user_id" in request.session:
        return "Unauthorized"
    
    user_id = request.session.get("user_id")
    if not await is_admin(db, user_id):
        return "No access"
    
    return user_id