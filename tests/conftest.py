import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker
from dbmodels.base import Base

@pytest.fixture(scope='function')
def engine() -> Engine:
    # Use an in-memory SQLite database for testing
    return create_engine('sqlite:///:memory:')

@pytest.fixture(scope='function')
def tables(engine):
    # Create all tables in the database for the test session
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(scope='function')
def session(engine, tables):
    """Returns a SQLAlchemy session, and after the test tears down everything properly."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()