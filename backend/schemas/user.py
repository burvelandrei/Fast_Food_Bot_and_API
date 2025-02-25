from pydantic import BaseModel, EmailStr
from typing import List


class UserOut(BaseModel):
    id: int
    tg_id: str | None
    email: EmailStr | None

    class Config:
        from_attributes = True


class UserCreateTg(BaseModel):
    email: EmailStr
    tg_id: str


class UserCreateWeb(BaseModel):
    email: EmailStr
    password: str