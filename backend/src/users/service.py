from datetime import datetime, timezone
from sqlmodel import Session, select, text
from sqlmodel.sql.expression import Select, SelectOfScalar
from backend.src.users.models import User, UserIn, Thread


class UserService:
    def __init__(self, session: Session):
        self._session = session

    def find_all_users(self) -> list[User]:
        return self._query(select(User)).all()

    def find_user_by_id(self, id: int) -> User | None:
        return self._session.get(User, id)

    def find_thread_by_id(self, id: int) -> Thread | None:
        return self._session.get(Thread, id)

    def create_user(self, user_in: UserIn) -> User:
        user = User.model_validate(user_in)
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user

    def find_user_threads(self, user_id: int) -> list[Thread]:
        return self._query(select(Thread).where(Thread.user_id == user_id)).all()

    def create_thread(self, user_id: int) -> Thread:
        thread = Thread(user_id=user_id)
        self._session.add(thread)
        self._session.commit()
        self._session.refresh(thread)
        return thread

    def update_thread(self, thread_id: int) -> Thread:
        if thread := self.find_thread_by_id(thread_id):
            thread.updated_at = datetime.now(timezone.utc)
            self._session.add(thread)
            self._session.commit()
            self._session.refresh(thread)
            return thread

        raise ValueError(f"Thread {thread_id} not found")

    def delete_thread(self, thread_id: int):
        if thread := self.find_thread_by_id(thread_id):
            for del_sql in [
                text("DELETE FROM checkpoints WHERE thread_id = ':tid'"),
                text("DELETE FROM checkpoint_writes WHERE thread_id = ':tid'"),
                text("DELETE FROM checkpoint_blobs WHERE thread_id = ':tid'")
            ]:
                self._session.exec(del_sql, params={"tid": thread_id})

            self._session.delete(thread)
            self._session.commit()
            return

        raise ValueError(f"Thread {thread_id} not found")

    def has_user_access_to_thread(self, user_id: int, thread_id: int) -> bool:
        thread = self.find_thread_by_id(thread_id)
        return thread and thread.user_id == user_id

    def _query(self, query: Select | SelectOfScalar):
        return self._session.exec(query)
