from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.templating import templates, flash
from app.schemas import UserEditSchema
from fastapi.responses import RedirectResponse
from app.crud.admin import get_all_users
from app.crud.admin import edit_user as edit_user_db
from app.crud.admin import delete_user as delete_user_db
from app.core.security import check_auth

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get('/')
async def admin(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await check_auth(request, db)
    match user_id:
        case "Unauthorized": 
            return RedirectResponse(url="/", status_code=303)
        case "No access": 
            flash(request, "You do not have access", "error")
            return RedirectResponse(url="/profile", status_code=303)
        case _:
            pass
    
    users = await get_all_users(db)
    return templates.TemplateResponse(request, "admin.html", {
        "users": users
    })

@router.post("/edit/{user_id_for_edit}", name="admin_edit_user")
async def edit_user(user_id_for_edit: int, user_data: UserEditSchema, request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await check_auth(request, db)
    match user_id:
        case "Unauthorized": 
            return {"ok": False, "message": "Unauthorized"}
        case "No access": 
            return {"ok": False, "message": "You do not have access"}
        case _:
            pass
    
    result = await edit_user_db(db, user_id_for_edit, user_data)
    if result:
        return {"ok": True, "message": "User successfully edited"}
    else:
        return {"ok": False, "message": "Something went wrong"}


@router.post("/delete/{user_id_for_delete}", name='admin_delete_user')
async def delete_user(user_id_for_delete: int, request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await check_auth(request, db)
    match user_id:
        case "Unauthorized": 
            return {"ok": False, "message": "Unauthorized"}
        case "No access": 
            return {"ok": False, "message": "You do not have access"}
        case _:
            pass
    
    result = await delete_user_db(db, user_id_for_delete)
    if result:
        return {"ok": True, "message": "User successfully deleted"}
    else:
        return {"ok": False, "message": "Something went wrong"}