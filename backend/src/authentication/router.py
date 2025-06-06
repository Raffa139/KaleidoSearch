from typing import Annotated
from datetime import datetime, timezone, timedelta
import jwt
from pydantic import ValidationError
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from backend.src.app.dependencies import UserServiceDep
from backend.src.authentication.models import TokenData, BearerToken, GoogleLogin
from backend.src.users.models import User, UserIn
from backend.src.environment import google_client_id, secret_key, access_token_expire_minutes, \
    algorithm

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], user_service: UserServiceDep):
    exception_details = "Could not validate credentials"
    exception_headers = {"WWW-Authenticate": "Bearer"}

    try:
        payload = jwt.decode(token, secret_key(), algorithms=[algorithm()])
        token_data = TokenData(user_id=payload.get("sub"))

        if user := user_service.find_user_by_id(token_data.user_id):
            return user

        raise HTTPException(status_code=401, detail=exception_details, headers=exception_headers)
    except ExpiredSignatureError:
        raise HTTPException(status_code=498, detail=exception_details, headers=exception_headers)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(status_code=401, detail=exception_details, headers=exception_headers)


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def create_access_token(data: dict):
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_expire_minutes())
    payload.update({"exp": expire})
    return jwt.encode(payload, secret_key(), algorithm=algorithm())


@router.post("/token/google")
def login_with_google(google_login: GoogleLogin, user_service: UserServiceDep) -> BearerToken:
    try:
        id_info = id_token.verify_oauth2_token(
            google_login.id_token,
            requests.Request(),
            google_client_id()
        )

        sub_id = id_info["sub"]
        user = user_service.find_user_by_sub_id(sub_id)

        if not user:
            username = id_info.get("given_name")
            picture_url = id_info.get("picture")
            user = user_service.create_user(
                UserIn(sub_id=sub_id, username=username, picture_url=picture_url)
            )

        access_token = create_access_token({"sub": str(user.id)})
        return BearerToken(access_token=access_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid ID token")


@router.get("/token/verify")
def verify_token(token: Annotated[str, Depends(oauth2_scheme)]) -> bool:
    try:
        jwt.decode(token, secret_key(), algorithms=[algorithm()])
        return True
    except InvalidTokenError:
        return False
