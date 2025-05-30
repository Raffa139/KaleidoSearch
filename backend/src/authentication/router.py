from typing import Annotated
from datetime import datetime, timezone, timedelta
import jwt
from pydantic import ValidationError
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from backend.src.app.dependencies import SessionDep, SummarizeGraphDep
from backend.src.authentication.models import TokenData, BearerToken, GoogleLogin
from backend.src.products.service import ProductService
from backend.src.shops.service import ShopService
from backend.src.users.service import UserService
from backend.src.users.models import User, UserIn
from backend.src.environment import google_client_id

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["authentication"],
                   responses={498: {"description": "Token expired"}})

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def create_product_service(session: SessionDep, summarize_graph: SummarizeGraphDep):
    shop_service = ShopService(session)
    return ProductService(session, shop_service, summarize_graph)


ProductServiceDep = Annotated[ProductService, Depends(create_product_service)]


def create_user_service(session: SessionDep, product_service: ProductServiceDep):
    return UserService(session, product_service)


UserServiceDep = Annotated[UserService, Depends(create_user_service)]


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], user_service: UserServiceDep):
    exception_details = "Could not validate credentials"
    exception_headers = {"WWW-Authenticate": "Bearer"}

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenData(user_id=payload.get("sub"))

        if user := user_service.find_user_by_id(token_data.user_id):
            return user

        raise HTTPException(status_code=401, detail=exception_details, headers=exception_headers)
    except ExpiredSignatureError:
        raise HTTPException(status_code=498, detail=exception_details, headers=exception_headers)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(status_code=401, detail=exception_details, headers=exception_headers)


CurrentUserDep = Annotated[User, Depends(get_current_user)]


# TODO: Make constants configurable
# TODO: Secure relevant routes
# TODO: Secure uid based routes with admin permission only (or not have them)
# TODO: Create "/me" versions of e.g. /threads route


def create_access_token(data: dict):
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/token")
def admin_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> BearerToken:
    password = form_data.password

    if password != "admin":
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    access_token = create_access_token({"sub": "2"})
    return BearerToken(access_token=access_token)


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
            user = user_service.create_user(UserIn(sub_id=sub_id))

        access_token = create_access_token({"sub": str(user.id)})
        return BearerToken(access_token=access_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid ID token")
