import functools

class CountFuncCalls:
    def __init__(self, max_count=1):
        self.max_count = max_count
        self.call_count = {}

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if func.__name__ not in self.call_count:
                self.call_count[func.__name__] = 0

            self.call_count[func.__name__] += 1

            if self.call_count[func.__name__] > self.max_count:
                print(f"Function '{func.__name__}' called more than {self.max_count} times!")
                return
            return func(*args, **kwargs)
        
        wrapper.get_call_count = lambda: self.call_count.get(func.__name__, 0)
        return wrapper


def repeat_func(num: int):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(num):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator_repeat