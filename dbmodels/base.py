from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///tables/testbase.db')

engine = create_engine(DATABASE_URL, echo=True)

Base: DeclarativeBase = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """Gets the db session from SessionLocal bound to the engine. Finally closes the connection to the database.

    Yields:
        sessionmaker: A session for the database connection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Initiates the database, creating all nonexisting tables
    """
    Base.metadata.create_all(engine)