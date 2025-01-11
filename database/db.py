from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# this will makesure that always the command is run it will use the database in the below path

DB_PARENT_PATH = Path("~/.toshu").expanduser()
DB_PARENT_PATH.mkdir(exist_ok=True)

DB_PATH = DB_PARENT_PATH.resolve() / "todo.db"

from .models import Base

engine = create_engine(f"sqlite:///{DB_PATH}")

SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
