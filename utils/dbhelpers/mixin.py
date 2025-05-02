import typing as T
from sqlalchemy.inspection import inspect

class SerializerMixin:
    def to_dict(self) -> dict[T.Any]:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}