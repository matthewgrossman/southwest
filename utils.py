import time
from functools import wraps
from typing import Any
from typing import Callable
from typing import cast
from typing import List
from typing import Type
from typing import TypeVar


F = TypeVar('F', bound=Callable[..., Any])


def retry(e: List[Type[Exception]], count: int = 10, delay_s: int = 5) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def decorated(*args, **kwargs):
            for i in range(count):
                try:
                    return func(*args, **kwargs)
                except tuple(e):
                    time.sleep(delay_s)
                    print(f'retrying, attempt {i}')
            return func(*args, **kwargs)
        return cast(F, decorated)
    return decorator
