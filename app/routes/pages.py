from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.templating import templates, flash
from fastapi.responses import HTMLResponse, RedirectResponse
from app.crud.users import get_user_with_transactions

router = APIRouter(prefix="", tags=["Pages"])

@router.get('/', name="home")
@router.get('/home', name="home")
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "home.html")

@router.get("/profile", name="profile")
async def profile(
    request: Request,
    db: AsyncSession = Depends(get_db)
    ) -> HTMLResponse:
    if not "user_id" in request.session:
        flash(request, "Please log in to access your profile", "error")
        return RedirectResponse(url="/login", status_code=303)
    
    user_id = request.session.get("user_id")
    user = await get_user_with_transactions(db, user_id)

    if not user:
        request.session.clear()
        return RedirectResponse(url='/login', status_code=303)
    
    context = {
        "request": request,
        "user": user,
        "transactions": user.transactions,
        "transactions_count": len(user.transactions)
    }
    
    return templates.TemplateResponse(request, "profile.html", context)
