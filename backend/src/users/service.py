from datetime import datetime, timezone
from sqlmodel import Session, select, text
from sqlmodel.sql.expression import Select, SelectOfScalar
from backend.src.products.service import ProductService
from backend.src.users.models import User, UserIn, Thread, Bookmark


class UserService:
    def __init__(self, session: Session, product_service: ProductService):
        self._session = session
        self._product_service = product_service

    def find_all_users(self) -> list[User]:
        return self._query(select(User)).all()

    def find_user_by_id(self, id: int) -> User | None:
        return self._session.get(User, id)

    def find_user_by_sub_id(self, sub_id: str) -> User | None:
        return self._query(select(User).where(User.sub_id == sub_id)).first()

    def find_thread_by_id(self, id: int) -> Thread | None:
        return self._session.get(Thread, id)

    def find_bookmark_by_id(self, id: int) -> Bookmark | None:
        return self._session.get(Bookmark, id)

    def find_bookmark_by_user_product_id(self, user_id: int, product_id: int) -> Bookmark | None:
        return self._query(
            select(
                Bookmark
            ).where(Bookmark.product_id == product_id).where(Bookmark.user_id == user_id)
        ).first()

    def find_user_threads(self, user_id: int) -> list[Thread]:
        return self._query(
            select(Thread).where(Thread.user_id == user_id).order_by(Thread.updated_at.desc())
        ).all()

    def find_user_bookmarks(self, user_id: int) -> list[Bookmark]:
        return self._query(
            select(Bookmark).where(Bookmark.user_id == user_id).order_by(Bookmark.created_at.desc())
        ).all()

    def create_user(self, user_in: UserIn) -> User:
        user = User.model_validate(user_in)
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user

    def create_thread(self, user_id: int) -> Thread:
        thread = Thread(user_id=user_id)
        self._session.add(thread)
        self._session.commit()
        self._session.refresh(thread)
        return thread

    def create_bookmark(self, user_id: int, product_id: int) -> Bookmark:
        if not self._product_service.find_by_id(product_id):
            raise ValueError(f"Product {product_id} not found")

        if self.find_bookmark_by_user_product_id(user_id, product_id):
            raise ValueError(f"Bookmark already exists")

        bookmark = Bookmark(user_id=user_id, product_id=product_id)
        self._session.add(bookmark)
        self._session.commit()
        self._session.refresh(bookmark)
        return bookmark

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

    def delete_bookmark(self, bookmark_id: int):
        if bookmark := self.find_bookmark_by_id(bookmark_id):
            self._session.delete(bookmark)
            self._session.commit()
            return

        raise ValueError(f"Bookmark {bookmark_id} not found")

    def has_user_access_to_thread(self, user_id: int, thread_id: int) -> bool:
        thread = self.find_thread_by_id(thread_id)
        return thread and thread.user_id == user_id

    def has_user_access_to_bookmark(self, user_id: int, bookmark_id: int) -> bool:
        bookmark = self.find_bookmark_by_id(bookmark_id)
        return bookmark and bookmark.user_id == user_id

    def _query(self, query: Select | SelectOfScalar):
        return self._session.exec(query)
