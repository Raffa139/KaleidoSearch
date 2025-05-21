from pydantic import HttpUrl
from sqlmodel import SQLModel, Field
from backend.src.common.http_url_type import HttpUrlType


class UserBase(SQLModel):
    sub_id: str = Field(unique=True)
    username: str | None = None
    picture_url: HttpUrl | None = Field(default=None, sa_type=HttpUrlType)


class UserIn(UserBase):
    pass


class UserOut(UserBase):
    id: int


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class Thread(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
