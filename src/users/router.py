from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from src.app.dependencies import SessionDep
from src.users.models import UserOut, UserIn
from src.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def user_service(session: SessionDep):
    return UserService(session)


ServiceDep = Annotated[UserService, Depends(user_service)]


@router.get("/", response_model=list[UserOut])
def get_users(service: ServiceDep):
    return service.find_all_users()


@router.post("/", response_model=UserOut, status_code=201)
def create_user(user_in: UserIn, service: ServiceDep):
    return service.create_user(user_in)


@router.get("/{id}", response_model=UserOut)
def get_user_by_id(id: int, service: ServiceDep):
    user = service.find_user_by_id(id)
    if not user:
        raise HTTPException(status_code=404)
    return user
