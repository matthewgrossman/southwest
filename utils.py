import time
from functools import wraps
from typing import Any
from typing import Callable
from typing import cast
from typing import Type
from typing import TypeVar


F = TypeVar('F', bound=Callable[..., Any])


def retry(e: Type[Exception], count: int = 5, delay_s: int = 5) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def decorated(*args, **kwargs):
            for i in range(count):
                try:
                    return func(*args, **kwargs)
                except e:
                    print(f"retry {i}")
                    time.sleep(delay_s)
            return func(*args, **kwargs)
        return cast(F, decorated)
    return decorator
