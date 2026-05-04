from pydantic import BaseModel, Field, EmailStr
from typing import Annotated, Literal
from fastapi import Form
from pydantic import model_validator

class UserRegisterSchema(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=16)]
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]
    password_confirm: Annotated[str, Field(min_length=8)]

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        password_confirm: str = Form(...)
    ):
        return cls(
            username=username,
            email=email,
            password=password,
            password_confirm=password_confirm
        )

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserRegisterSchema':
        if self.password != self.password_confirm:
            raise ValueError("Passwords must match!")
        
        if self.password.lower() == self.password:
            raise ValueError("Password must include one letter in upper case!")
        
        return self

class UserLoginSchema(BaseModel):
    login: Annotated[str, Field(min_length=3, max_length=16)] | EmailStr
    password: Annotated[str, Field(min_length=8)]

    @classmethod
    def as_form(
        cls,
        login: str = Form(...),
        password: str = Form(...)
    ):
        return cls(
            login=login,
            password=password,
        )

class TransactionSchema(BaseModel):
    type: str
    category: str
    amount: int
    desc: Annotated[str, Field(max_length=100)] | None

class UserEditSchema(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=16)]
    email: EmailStr
    role: Literal["user", "moderator", "admin"]