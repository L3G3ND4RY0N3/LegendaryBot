from sqlalchemy.inspection import inspect


def get_valid_attributes(model):
    """Automatically determine valid attribute names for sorting based on the model's columns."""
    mapper = inspect(model)
    valid_attributes = set(str(column.key) for column in mapper.columns)
    return valid_attributes