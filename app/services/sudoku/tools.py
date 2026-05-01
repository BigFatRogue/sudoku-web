from typing import Callable, Any
from functools import wraps
import time

def timer(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        res = func(*args, **kwargs)
        print(time.time() - start, 'сек')
        return res
    return wrapper