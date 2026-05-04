from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.exceptions import *
from app.routes import auth, pages, transactions, admin
from app.core.config import settings

import uvicorn

# App initialization
app = FastAPI(
    title="Awtik Cash"
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.mount('/static', StaticFiles(directory="app/static"), name="static")

setup_exception_handlers(app)

app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(transactions.router)
app.include_router(admin.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=settings.DEBUG)