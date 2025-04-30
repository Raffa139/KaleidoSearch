from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine
from src.environment import datasource_url

engine = create_engine(datasource_url())


def db_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(db_session)]
