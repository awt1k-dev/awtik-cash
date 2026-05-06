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
    
    @model_validator(mode='after')
    def check_dot(self) -> 'UserRegisterSchema':
        if "." in self.username and not "@" in self.username:
            raise ValueError('username cant include "."')
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
    
    @model_validator(mode='after')
    def check_dot(self) -> 'UserLoginSchema':
        if "." in self.login and not "@" in self.login:
            raise ValueError('username cant include "."')
        return self

class TransactionSchema(BaseModel):
    type: Literal["income", "expense"]
    category: Annotated[str, Field(max_length=30, min_length=1)]
    amount: Annotated[int, Field(gt=0)]
    desc: Annotated[str, Field(max_length=100)] | None

class UserEditSchema(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=16)]
    email: EmailStr
    role: Literal["user", "moderator", "admin"]

    @model_validator(mode='after')
    def check_dot(self) -> 'UserEditSchema':
        if "." in self.username and not "@" in self.username:
            raise ValueError('username cant include "."')
        return self