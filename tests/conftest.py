import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.db.database import Base, get_db
from app.db import models
from app.crud.users import get_user_by_id

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine_test = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_client(client):
    reg_resp = await client.post("/register", data={
        "username": "tester",
        "email": "tester@test.com",
        "password": "Correct123",
        "password_confirm": "Correct123"
    })
    
    assert reg_resp.status_code == 303, f"Ошибка регистрации! Ответ сервера: {reg_resp.text}"

    login_resp = await client.post("/login", data={
        "login": "tester@test.com",
        "password": "Correct123"
    })
    
    assert login_resp.status_code == 303, f"Ошибка логина! Ответ сервера: {login_resp.text}"
    
    yield client

@pytest.fixture
async def client_with_user_in_db(client):
    reg_resp = await client.post("/register", data={
        "username": "tester",
        "email": "tester@test.com",
        "password": "Correct123",
        "password_confirm": "Correct123"
    })
    assert reg_resp.status_code == 303, f"Ошибка регистрации! Ответ сервера: {reg_resp.text}"

    assert (await client.get("/logout")).status_code in (302, 303)

    yield client

@pytest.fixture
async def admin_client(auth_client):
    async with TestingSessionLocal() as db:
        user = await get_user_by_id(db, 1)

        assert user.username == "tester"

        user.role = "admin"

        await db.commit()
        await db.refresh(user)

        yield auth_client