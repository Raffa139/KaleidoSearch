from datetime import datetime, timezone
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


class ThreadBase(SQLModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Thread(ThreadBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")


class ThreadOut(ThreadBase):
    thread_id: int
