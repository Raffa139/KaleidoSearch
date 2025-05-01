from sqlmodel import Session, select
from sqlmodel.sql.expression import Select, SelectOfScalar
from src.users.models import User, UserIn


class UserService:
    def __init__(self, session: Session):
        self._session = session

    def find_all(self) -> list[User]:
        return self._query(select(User)).all()

    def find_by_id(self, id: int) -> User | None:
        return self._session.get(User, id)

    def create(self, user_in: UserIn) -> User:
        user = User.model_validate(user_in)
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user

    def _query(self, query: Select | SelectOfScalar):
        return self._session.exec(query)
