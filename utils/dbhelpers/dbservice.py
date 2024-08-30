from sqlalchemy.orm import Session
from contextlib import contextmanager

class DatabaseService:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session: Session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_or_create(self, model, session: Session = None, **kwargs):
        """Generic method to get or create a model instance."""
        if not session:
            with self.session_scope() as session:
                instance = session.query(model).filter_by(**kwargs).first()
                if instance:
                    return instance
                else:
                    instance = model(**kwargs)
                    session.add(instance)
                    return instance
        else:
            instance = session.query(model).filter_by(**kwargs).first()
            if instance:
                return instance
            else:
                instance = model(**kwargs)
                session.add(instance)
                return instance

    def get(self, model, **kwargs):
        """Generic method to get a model instance."""
        with self.session_scope() as session:
            instance = session.query(model).filter_by(**kwargs).first()
            return instance

    def create(self, model, **kwargs):
        """Generic method to create a model instance."""
        with self.session_scope() as session:
            instance = model(**kwargs)
            session.add(instance)
            return instance