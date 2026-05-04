from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.templating import templates, flash
from app.schemas import UserLoginSchema, UserRegisterSchema
from fastapi.responses import HTMLResponse, RedirectResponse
from app.crud.users import *
from app.crud.transactions import *

router = APIRouter(prefix="", tags=["Auth"])

@router.get("/logout", name="logout")
async def profile_exit(request: Request):
    if "user_id" in request.session:
        request.session.clear()
    return RedirectResponse(url='/', status_code=303)

@router.get("/login", name="login")
async def login(request: Request) -> HTMLResponse:
    if "user_id" in request.session:
        return RedirectResponse(url='/profile', status_code=303)
    return templates.TemplateResponse(request, "login.html")

@router.post("/login", name="login")
async def post_login(
        request: Request,
        db: AsyncSession = Depends(get_db),
        form_data: UserLoginSchema = Depends(UserLoginSchema.as_form)
    ):
    if "user_id" in request.session:
        return RedirectResponse(url='/profile', status_code=303)

    user_id = await check_login(db, form_data)
    if not user_id:
        flash(request, "Invalid credentials", "error")
        return templates.TemplateResponse(request, "login.html")
    else:
        flash(request, "Welcome to your profile!", "success")
        request.session["user_id"] = user_id
        return RedirectResponse(url='/profile', status_code=303)

@router.get("/register", name="register")
async def register(request: Request) -> HTMLResponse:
    if "user_id" in request.session:
        return RedirectResponse(url='/profile', status_code=303)
    return templates.TemplateResponse(request, "register.html")

@router.post("/register", name="register")
async def post_register(
        request: Request, 
        db: AsyncSession = Depends(get_db), 
        form_data: UserRegisterSchema = Depends(UserRegisterSchema.as_form)
    ):
    existing_user = await get_user_by_username_or_email(db, form_data.username, form_data.email)

    if not existing_user:
        user = await create_user(db, form_data)
        if user:
            flash(request, "Success registration! Go to ur profile!", "success")
            request.session["user_id"] = user.id
            return RedirectResponse(url='/profile', status_code=303)
        else:
            flash(request, "Something wrong with db", "error")
            return templates.TemplateResponse(request, "register.html", context={
                "username": form_data.username,
                "email": form_data.email
            })
    else:
        flash(request, "User with this credentials already exists", "error")
        return templates.TemplateResponse(request, "register.html", context={
                "username": form_data.username,
                "email": form_data.email
            })