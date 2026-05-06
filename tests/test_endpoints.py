import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

################################
#
#         Auth
#
################################

################################
# Register
@pytest.mark.asyncio
async def test_register_success(client):
    form_data = {
        "username": "tester",
        "email": "tester@gmail.com",
        "password": "Correct123",
        "password_confirm": "Correct123"
    }
    response = await client.post("/register", data=form_data)

    assert response.status_code in (302, 303)
    assert "/profile" in response.headers["location"]

@pytest.mark.asyncio
async def test_register_post_wrong(client):
    form_data = {
        "username": "tester",
        "email": "test@test.com",
        "password": "Password123",
        "password_confirm": "Wrong123"
    }
    response = await client.post("/register", data=form_data)
        
    assert response.status_code != 500

@pytest.mark.asyncio
async def test_register_user_exists(client_with_user_in_db):
    form_data = {
        "username": "tester",
        "email": "tester@test.com",
        "password": "Correct123",
        "password_confirm": "Correct123"
    }

    response = await client_with_user_in_db.post("/register", data=form_data)

    assert response.status_code == 200
    assert "User with this credentials already exists" in response.text
    
################################
# Login
@pytest.mark.asyncio
async def test_login_wrong_data(client):
    form_data = {
        "login": "testerwrong"*10,
        "password": "Correct123"
    }
    response = await client.post("/login", data=form_data)
    assert "Invalid credentials" in response.text

@pytest.mark.asyncio
async def test_login_wrong_password(client_with_user_in_db: AsyncClient):
    form_data = {
        "login": "tester",
        "password": "InCorrect123",
    }
    response = await client_with_user_in_db.post("/login", data=form_data)

    assert "Invalid credentials" in response.text

################################
# Profile
@pytest.mark.asyncio
async def test_profile_unauthorized(client):
    response = await client.get("/profile", follow_redirects=False)
        
    assert response.status_code in (302, 303)
    assert "/login" in response.headers["location"]

@pytest.mark.asyncio
async def test_profile_accepts_user(auth_client):
    response = await auth_client.get("/profile")
    
    assert response.status_code == 200
    
    assert "tester@test.com" in response.text

@pytest.mark.asyncio
async def test_logout_anonymous(client):
    response = await client.get("/logout")

    assert response.status_code in (302, 303)
    assert "/" in response.headers["location"]

################################
#
#         Pages
#
################################
@pytest.mark.asyncio
async def test_home_page(client):
    response = await client.get("/")
        
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

################################
#
#         Transactions
#
################################

################################
# Create
@pytest.mark.asyncio
async def test_create_transaction_success(auth_client: AsyncClient):
    json = {
        "type": "income",
        "category": "Salary",
        "amount": 1000,
        "desc": None
    }
    response = await auth_client.post("/transactions/create", json=json)

    assert response.json()["ok"]

@pytest.mark.asyncio
async def test_create_transaction_wrong(auth_client: AsyncClient):
    json = {
        "type": "wrong_type",
        "category": "Salary",
        "amount": 1000,
        "desc": None
    }
    response = await auth_client.post("/transactions/create", json=json)

    assert "Input should be \'income\' or \'expense\'" in response.text

@pytest.mark.asyncio
async def test_create_transaction_anonymous(client):
    json = {
        "type": "income",
        "category": "Salary",
        "amount": 1000,
        "desc": None
    }
    response = await client.post("/transactions/create", json=json)

    assert "Unauthorized" in response.text

################################
# Delete
@pytest.mark.asyncio
async def test_delete_transaction_success(auth_client: AsyncClient):
    json = {
        "type": "income",
        "category": "Salary",
        "amount": 1000,
        "desc": None
    }
    response = await auth_client.post("/transactions/create", json=json)

    assert response.json()["ok"]
    t_id = response.json()["transaction"]["id"]
    assert (await auth_client.post(f"/transactions/delete/{t_id}")).json()["ok"]

@pytest.mark.asyncio
async def test_delete_invalid_transaction(auth_client: AsyncClient):
    assert (await auth_client.post("/transactions/delete/2")).json()["ok"] == False
    
@pytest.mark.asyncio
async def test_delete_transaction_anonymous(client: AsyncClient):
    assert (await client.post("/transactions/delete/2")).json()["ok"] == False
    
################################
#
#         Admin
#
################################

################################
# Main
@pytest.mark.asyncio
async def test_admin_anonymous(client):
    response = await client.get("/admin")
    assert response.status_code in (302, 303)

@pytest.mark.asyncio
async def test_admin_not_access(auth_client: AsyncClient):
    response = await auth_client.get("/admin")
    assert response.status_code in (302, 303)
    assert "/profile" in response.headers["location"]

@pytest.mark.asyncio
async def test_admin_success(admin_client: AsyncClient):
    response = await admin_client.get("/admin")
    assert response.status_code == 200
    assert "tester" in response.text

################################
# Edit
@pytest.mark.asyncio
async def test_admin_edit_anonymous(client_with_user_in_db: AsyncClient):
    json = {
        "username": "new_tester",
        "email": "new_tester@gmail.com",
        "role": "admin"
    }
    response = await client_with_user_in_db.post("/admin/edit/1", json=json)

    assert response.json()["ok"] == False
    assert response.json()["message"] == "Unauthorized"

@pytest.mark.asyncio
async def test_admin_edit_not_access(auth_client: AsyncClient):
    json = {
        "username": "new_tester",
        "email": "new_tester@gmail.com",
        "role": "admin"
    }
    response = await auth_client.post("/admin/edit/1", json=json)

    assert response.json()["ok"] == False
    assert response.json()["message"] == "You do not have access"


@pytest.mark.asyncio
async def test_admin_edit_wrong_data(admin_client: AsyncClient):
    json = {
        "username": "new_tester_wrong"*10,
        "email": "new_tester@gmail.com",
        "role": "admin"
    }
    response = await admin_client.post("/admin/edit/1", json=json)

    assert response.status_code != 500
    assert "String should have at most 16 characters" in response.text


@pytest.mark.asyncio
async def test_admin_edit_success(admin_client: AsyncClient):
    json = {
        "username": "new_tester",
        "email": "new_tester@gmail.com",
        "role": "admin"
    }
    response = await admin_client.post("/admin/edit/1", json=json)

    assert response.json()["ok"]
    assert response.json()["message"] == "User successfully edited"

################################
# Delete
@pytest.mark.asyncio
async def test_admin_delete_anonymous(client: AsyncClient):
    response = await client.post("/admin/delete/1")

    assert response.json()["ok"] == False
    assert response.json()["message"] == "Unauthorized"

@pytest.mark.asyncio
async def test_admin_delete_not_access(auth_client: AsyncClient):
    response = await auth_client.post("/admin/delete/1")

    assert response.json()["ok"] == False
    assert response.json()["message"] == "You do not have access"

@pytest.mark.asyncio
async def test_admin_delete_wrong_id(admin_client: AsyncClient):
    response = await admin_client.post("/admin/delete/10")

    assert response.json()["ok"] == False
    assert response.json()["message"] == "Something went wrong"

@pytest.mark.asyncio
async def test_admin_delete_success(admin_client: AsyncClient):
    response = await admin_client.post("/admin/delete/1")

    assert response.json()["ok"]
    assert response.json()["message"] == "User successfully deleted"