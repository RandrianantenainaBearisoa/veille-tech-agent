# connexion to the DB
import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVICE = os.getenv("DB_SERVICE")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = (
    f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVICE}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


@contextmanager
def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables(re_create: bool = False):
    if re_create:
        SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
