from pydantic import BaseModel, Field, EmailStr
from enum import StrEnum


class UserType(StrEnum):
    guest: str = 'guest'
    user: str = 'user'


class UserScheme(BaseModel):
    user_id: int
    username: str | None = Field(default=None, description='Имя пользвателя (левая часть от @ в mail)')
    type_user: str = UserType.guest


class UserAuthScheme(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserRegestartionScheme(UserAuthScheme):
    password_repet: str = Field(..., min_length=8)


