from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine

sqlite_file = "database.db"
sqlite_url = f"sqlite:///{sqlite_file}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def db_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(db_session)]
