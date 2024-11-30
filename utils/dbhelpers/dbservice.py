from typing import Type, TypeVar
from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from contextlib import contextmanager

_T = TypeVar('T')

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

    def get_or_create(self, model: Type[_T], session: Session, **kwargs) -> _T:
        """Generic method to get or create a model instance."""
        # Get the mapper to inspect the model's attributes and constraints
        mapper = inspect(model)
        
        # Identify unique columns in the model (those with unique=True or primary_key)
        unique_columns = []
        for column in mapper.columns:
            if column.unique or column.primary_key:
                unique_columns.append(column.name)
        
        for constraint in model.__table__.constraints:
            if isinstance(constraint, UniqueConstraint):
                for column in constraint.columns:
                    if column.name not in unique_columns:
                        unique_columns.append(column.name)
        
        # Try to query using unique fields in kwargs, in order
        instance = None

        unique_filters = {key: val for key, val in kwargs.items() if key in unique_columns}
        instance = session.query(model).filter_by(**unique_filters).first()
        
        if instance:
            # If an instance is found, update its fields (if necessary)
            has_changes = False
            for field, value in kwargs.items():
                old_val = getattr(instance, field)
                if  old_val != value:
                    setattr(instance, field, value)
                    has_changes = True
            if has_changes:
                session.add(instance)  # Update the instance if fields have changed
            return instance
        else:
            # If no instance is found, create a new one
            try:
                instance = model(**kwargs)
                session.add(instance)
                return instance
            except IntegrityError:
                session.rollback()
                # If an IntegrityError occurs, a duplicate unique key might have been inserted
                # Retry fetching the instance based on unique fields
                instance = session.query(model).filter_by(**unique_filters).first()
                if instance:
                    return instance
