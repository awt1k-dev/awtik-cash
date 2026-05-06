import pytest
from pydantic import ValidationError
from app.schemas import UserRegisterSchema, UserLoginSchema, UserEditSchema, TransactionSchema

################################
#
#         REGISTER
#
################################
def test_user_register_schema_success():
    data = {
        "username": "tester",
        "email": "test@test.com",
        "password": "Password123",
        "password_confirm": "Password123"
    }
    
    user = UserRegisterSchema(**data)
    
    assert user.username == "tester"
    assert user.email == "test@test.com"

# Wrong datas
register_wrong_test_data = [
    # Passwords
    ("tester", "tester@gmail.com", "password123", "password123", "must include one letter in upper case"),
    ("tester", "tester@gmail.com", "Password123", "Wrongpassword", "Passwords must match"),
    ("tester", "tester@gmail.com", "Short1", "Short1", "String should have at least 8 characters"),
    # username
    ("t", "tester@gmail.com", "Correct123", "Correct123", "String should have at least 3 characters"),
    ("a" * 17, "tester@gmail.com", "Correct123", "Correct123", "String should have at most 16 characters"),
    ("123.", "tester@gmail.com", "Correct123", "Correct123", 'username cant include "."'),
    # Email
    ("tester", "testergmail.com", "Correct123", "Correct123", "value is not a valid email address")
]

@pytest.mark.parametrize("username, email, password, password_confirm, expected_error", register_wrong_test_data)
def test_user_register_schema_errors(username, email, password, password_confirm, expected_error):
    data = {
        "username": username,
        "email": email,
        "password": password,
        "password_confirm": password_confirm
    }
    
    with pytest.raises(ValidationError) as exc_info:
        UserRegisterSchema(**data)
        
    assert expected_error in str(exc_info.value)

################################
#
#         LOGIN
#
################################
login_success_test_data = [
    ("tester", "Correct123"),
    ("tester@gmail.com", "Correct123")
]

@pytest.mark.parametrize("login, password", login_success_test_data)
def test_user_login_schema_success(login, password):
    data = {
        "login": login,
        "password": password,
    }
    
    user = UserLoginSchema(**data)
    
    assert user.login == login
    assert user.password == password

login_wrong_test_data = [
    # Password
    ("tester", "short", "String should have at least 8 characters"),
    # Login
    ("t", "Correct123", "String should have at least 3 characters"),
    ("a" * 17, "Correct123", "String should have at most 16 characters"),
    ("testergmail.com", "Correct123", 'username cant include "."')


]

@pytest.mark.parametrize("login, password, expected_error", login_wrong_test_data)
def test_user_login_schema_errors(login, password, expected_error):
    data = {
        "login": login,
        "password": password,
    }
    
    with pytest.raises(ValidationError) as exc_info:
        UserLoginSchema(**data)
        
    assert expected_error in str(exc_info.value)

################################
#
#         User Edit
#
################################
user_edit_success_test_data = [
    ("tester", "tester@gmail.com", "admin")
]
@pytest.mark.parametrize("username, email, role", user_edit_success_test_data)
def test_user_edit_schema_success(username, email, role):
    data = {
        "username": username,
        "email": email,
        "role": role
    }

    user = UserEditSchema(**data)
    
    assert user.username == username
    assert user.role == role

user_edit_wrong_data = [
    # Username
    ("tester"*10, "tester@gmail.com", "admin", "String should have at most 16 characters"),   
    ("te", "tester@gmail.com", "admin", "String should have at least 3 characters"),
    ("test.er", "tester@gmail.com", "admin", 'username cant include "."'),
    # Role
    ("tester", "tester@gmail.com", "vugabuga", "Input should be 'user', 'moderator' or 'admin'"),
    # Email
    ("tester", "testergmail.com", "admin", "An email address must have an @-sign"), 

]
@pytest.mark.parametrize("username, email, role, expected_error", user_edit_wrong_data)
def test_user_edit_schema_errors(username, email, role, expected_error):
    data = {
        "username": username,
        "email": email,
        "role": role,
    }

    with pytest.raises(ValidationError) as exc_info:
        UserEditSchema(**data)
    
    assert expected_error in str(exc_info.value)

################################
#
#         Transaction
#
################################
def test_transaction_schema_success():
    data = {
        "type": "income",
        "category": "Salary",
        "amount": 10000,
        "desc": "April's salary"
    }

    transaction = TransactionSchema(**data)

    assert transaction.type == "income"
    assert transaction.amount == 10000

transaction_wrong_test_data = [
    # Type
    ("wrongtype", "Salary", 10000, "Description", "Input should be 'income' or 'expense'"),
    # Category
    ("income", "Category"*10, 10000, "Description", "String should have at most 30 characters"),
    ("income", "", 10000, "Description", "String should have at least 1 character"),
    # Amount
    ("income", "Salary", -1000, "Description", "Input should be greater than 0"),
    # Description
    ("income", "Salary", 10000, "Description"*10, "String should have at most 100 characters"),

]
@pytest.mark.parametrize("type, category, amount, desc, expected_error", transaction_wrong_test_data)
def test_transaction_schema_wrong(type, category, amount, desc, expected_error):
    data = {
        "type": type,
        "category": category,
        "amount": amount,
        "desc": desc
    }

    with pytest.raises(ValidationError) as exc_info:
        TransactionSchema(**data)
    
    assert expected_error in str(exc_info.value)