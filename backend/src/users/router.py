from fastapi import APIRouter, HTTPException
from backend.src.app.dependencies import UserServiceDep
from backend.src.authentication.router import CurrentUserDep
from backend.src.users.models import UserOut, UserIn
from backend.src.users.threads_router import router as threads_router
from backend.src.users.bookmarks_router import router as bookmarks_router

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserOut])
def get_users(user_service: UserServiceDep):
    return user_service.find_all_users()


@router.post("/", response_model=UserOut, status_code=201)
def create_user(user_in: UserIn, user_service: UserServiceDep):
    return user_service.create_user(user_in)


@router.get("/me", response_model=UserOut)
def get_user(user: CurrentUserDep, user_service: UserServiceDep):
    if user := user_service.find_user_by_id(user.id):
        return user

    raise HTTPException(status_code=404)


router.include_router(threads_router)
router.include_router(bookmarks_router)
