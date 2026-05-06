import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.users import create_user, check_login, get_user_by_id, get_user_by_username_or_email, get_user_with_transactions
from app.crud.transactions import create_transaction_db, delete_transaction_db
from app.crud.admin import is_admin, get_all_users, get_user_by_id_with_tx, edit_user, delete_user
from app.schemas import UserRegisterSchema, UserLoginSchema, TransactionSchema, UserEditSchema
from app.db.models import User, Transaction

################################
#
#         Users
#
################################

################################
# Get users
@pytest.mark.asyncio
async def test_get_user_by_username_or_email_success(db_session):
    new_user = User(
        username="tester",
        email="tester@gmail.com",
        password_hash="hashed_password"
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    user = await get_user_by_username_or_email(db_session, "tester", "tester@gmail.com")
    assert user is not None
    assert user.balance == 0
    assert user.username == "tester"

@pytest.mark.asyncio
async def test_get_user_by_username_or_email_failed(db_session):
    user = await get_user_by_username_or_email(db_session, "tester", "tester@gmail.com")
    assert not user

@pytest.mark.asyncio
async def test_get_user_with_transactions_success(db_session):
    new_user = User(
        username="tester",
        email="tester@gmail.com",
        password_hash="hashed_password"
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    user_id = new_user.id

    new_transaction = Transaction(
        user_id=user_id,
        amount=1000,
        type="income",
        category="Salary",
        desc=None
    )
    db_session.add(new_transaction)
    await db_session.commit()
    await db_session.refresh(new_transaction)

    user_with_transactions = await get_user_with_transactions(db_session, user_id)
    assert user_with_transactions.username == "tester"
    assert len(user_with_transactions.transactions) == 1
    assert user_with_transactions.transactions[0].type == "income"
    assert user_with_transactions.transactions[0].amount == 1000

@pytest.mark.asyncio
async def test_get_user_with_transactions_wrong_user_id(db_session):
    new_user = User(
        username="tester",
        email="tester@gmail.com",
        password_hash="hashed_password"
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    user_id = new_user.id

    new_transaction = Transaction(
        user_id=user_id,
        amount=1000,
        type="income",
        category="Salary",
        desc=None
    )
    db_session.add(new_transaction)
    await db_session.commit()
    await db_session.refresh(new_transaction)

    user_with_transactions = await get_user_with_transactions(db_session, 10)
    assert user_with_transactions is None

@pytest.mark.asyncio
async def test_get_user_by_id_success(db_session):
    new_user = User(
        username="tester",
        email="tester@gmail.com",
        password_hash="hashed_password"
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    user = await get_user_by_id(db_session, new_user.id)
    assert user is not None
    assert user.balance == 0
    assert user.username == "tester"

@pytest.mark.asyncio
async def test_get_user_by_id_wrong_id(db_session):
    user = await get_user_by_id(db_session, 10)
    assert user is None

@pytest.mark.asyncio
async def test_crud_create_user_success(db_session: AsyncSession):
    user_data = UserRegisterSchema(
        username="tester",
        email="tester@gmail.com",
        password="Correct123",
        password_confirm="Correct123"
    )

    new_user = await create_user(db_session, user_data)

    assert new_user.id is not None
    assert new_user.username == "tester"
    
    assert new_user.password_hash != "Correct123"

    db_user = await get_user_by_id(db_session, new_user.id)
    assert db_user.email == "tester@gmail.com"

@pytest.mark.asyncio
async def test_crud_create_user_exist(db_session: AsyncSession):
    exist_user = User(
        username="tester",
        email="tester@gmail.com",
        password_hash="hashed_password"
    )
    db_session.add(exist_user)
    await db_session.commit()
    await db_session.refresh(exist_user)

    user_data = UserRegisterSchema(
        username="tester",
        email="tester_new_email@gmail.com",
        password="Correct123",
        password_confirm="Correct123"
    )

    new_user = await create_user(db_session, user_data)
    assert not new_user

@pytest.mark.asyncio
async def test_crud_check_login_success(db_session):
    user_data = UserRegisterSchema(
        username="tester",
        email="tester@gmail.com",
        password="Correct123",
        password_confirm="Correct123"
    )

    new_user = await create_user(db_session, user_data)
    assert new_user is not None

    login_data = UserLoginSchema(
        login="tester",
        password="Correct123"
    )

    user_id = await check_login(db_session, login_data)
    assert user_id is not None

@pytest.mark.asyncio
async def test_crud_check_login_wrong(db_session):
    user_data = UserRegisterSchema(
        username="tester",
        email="tester@gmail.com",
        password="Correct123",
        password_confirm="Correct123"
    )

    new_user = await create_user(db_session, user_data)
    assert new_user is not None

    login_data = UserLoginSchema(
        login="tester",
        password="WrongPasswrod"
    )

    user_id = await check_login(db_session, login_data)
    assert user_id is None

################################
#
#         Trasnsactions
#
################################
@pytest.mark.asyncio
async def test_create_transaction_success(db_session):
    user_data = UserRegisterSchema(
        username="tester",
        email="tester@gmail.com",
        password="Correct123",
        password_confirm="Correct123"
    )

    new_user = await create_user(db_session, user_data)
    assert new_user is not None

    data = TransactionSchema(
        type="income",
        category="Salary",
        amount=1000,
        desc=None
    )

    transaction = await create_transaction_db(db_session, new_user.id, data)
    assert transaction is not None
    assert transaction.id == 1
    assert transaction.type == "income"

    user = await get_user_by_id(db_session, 1)
    assert user.balance == 1000

@pytest.mark.asyncio
async def test_create_transaction_wrong_id(db_session):
    user_data = UserRegisterSchema(
        username="tester",
        email="tester@gmail.com",
        password="Correct123",
        password_confirm="Correct123"
    )

    new_user = await create_user(db_session, user_data)
    assert new_user is not None

    data = TransactionSchema(
        type="income",
        category="Salary",
        amount=1000,
        desc=None
    )

    transaction = await create_transaction_db(db_session, 10, data)
    assert not transaction

@pytest.mark.asyncio
async def test_delete_transaction_success(db_session):
    user_data = UserRegisterSchema(
        username="tester",
        email="tester@gmail.com",
        password="Correct123",
        password_confirm="Correct123"
    )

    new_user = await create_user(db_session, user_data)
    assert new_user is not None

    user_id = new_user.id

    exist_transaction = Transaction(
        user_id=user_id,
        amount=1000,
        type="income",
        category="Salary",
        desc=None
    )
    db_session.add(exist_transaction)
    await db_session.commit()
    await db_session.refresh(exist_transaction)

    delete_result = await delete_transaction_db(db_session, user_id, exist_transaction.id)
    assert delete_result

    user = await get_user_by_id(db_session, user_id)
    assert user.balance == -1000

@pytest.mark.asyncio
async def test_delete_transaction_wrong_id(db_session):
    user_data = UserRegisterSchema(
        username="tester",
        email="tester@gmail.com",
        password="Correct123",
        password_confirm="Correct123"
    )

    new_user = await create_user(db_session, user_data)
    assert new_user is not None

    user_id = new_user.id

    exist_transaction = Transaction(
        user_id=user_id,
        amount=1000,
        type="income",
        category="Salary",
        desc=None
    )
    db_session.add(exist_transaction)
    await db_session.commit()
    await db_session.refresh(exist_transaction)

    delete_result = await delete_transaction_db(db_session, 10, exist_transaction.id)
    assert delete_result == False

################################
#
#         Admin
#
################################
@pytest.mark.asyncio
async def test_is_admin_success(db_session):
    user_data = UserRegisterSchema(
        username="tester",
        email="tester@gmail.com",
        password="Correct123",
        password_confirm="Correct123"
    )

    new_user = await create_user(db_session, user_data)
    assert new_user is not None

    new_user.role = "admin"
    await db_session.commit()
    await db_session.refresh(new_user)

    check_result = await is_admin(db_session, new_user.id)
    assert check_result

@pytest.mark.asyncio
async def test_is_admin_not_admin(db_session):
    user_data = UserRegisterSchema(
        username="tester",
        email="tester@gmail.com",
        password="Correct123",
        password_confirm="Correct123"
    )

    new_user = await create_user(db_session, user_data)
    assert new_user is not None

    check_result = await is_admin(db_session, new_user.id)
    assert check_result == False

@pytest.mark.asyncio
async def test_is_admin_not_user(db_session):
    check_result = await is_admin(db_session, 1)
    assert check_result == False

@pytest.mark.asyncio
async def test_get_all_users_success(db_session):
    user_data = UserRegisterSchema(
        username="tester",
        email="tester@gmail.com",
        password="Correct123",
        password_confirm="Correct123"
    )

    new_user = await create_user(db_session, user_data)
    assert new_user is not None

    users = await get_all_users(db_session)
    assert len(users) == 1
    assert users[0][0].balance == 0

@pytest.mark.asyncio
async def test_get_all_users_empty(db_session):
    users = await get_all_users(db_session)
    assert len(users) == 0

@pytest.mark.asyncio
async def test_get_user_by_id_with_tx_success(db_session):
    user_data = UserRegisterSchema(
        username="tester",
        email="tester@gmail.com",
        password="Correct123",
        password_confirm="Correct123"
    )

    new_user = await create_user(db_session, user_data)
    assert new_user is not None

    user_id = new_user.id

    exist_transaction = Transaction(
        user_id=user_id,
        amount=1000,
        type="income",
        category="Salary",
        desc=None
    )
    db_session.add(exist_transaction)
    await db_session.commit()
    await db_session.refresh(exist_transaction)

    user = await get_user_by_id_with_tx(db_session, user_id)
    assert user is not None
    assert user[1] == 1
    assert user[0].username == "tester"

@pytest.mark.asyncio
async def test_get_user_by_id_with_tx_wrong_id(db_session):
    user = await get_user_by_id_with_tx(db_session, 1)
    assert user is None

@pytest.mark.asyncio
async def test_edit_user_success(db_session):
    user_data = UserRegisterSchema(
        username="tester",
        email="tester@gmail.com",
        password="Correct123",
        password_confirm="Correct123"
    )

    new_user = await create_user(db_session, user_data)
    assert new_user is not None

    user_id = new_user.id

    user_edit_data = UserEditSchema(
        username="new_tester",
        email="new_tester@gmail.com",
        role="admin"
    )

    edit_result = await edit_user(db_session, user_id, user_edit_data)
    assert edit_result

@pytest.mark.asyncio
async def test_edit_user_wrong_id(db_session):
    user_edit_data = UserEditSchema(
        username="new_tester",
        email="new_tester@gmail.com",
        role="admin"
    )

    edit_result = await edit_user(db_session, 1, user_edit_data)
    assert edit_result == False

@pytest.mark.asyncio
async def test_delete_user_success(db_session):
    user_data = UserRegisterSchema(
        username="tester",
        email="tester@gmail.com",
        password="Correct123",
        password_confirm="Correct123"
    )

    new_user = await create_user(db_session, user_data)
    assert new_user is not None

    user_id = new_user.id

    delete_result = await delete_user(db_session, user_id)
    assert delete_result

@pytest.mark.asyncio
async def test_delete_user_wrong_id(db_session):
    delete_result = await delete_user(db_session, 1)
    assert delete_result == False