from typing import Literal

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class BearerToken(Token):
    token_type: Literal["bearer"] = "bearer"


class TokenData(BaseModel):
    user_id: int


class GoogleLogin(BaseModel):
    id_token: str
