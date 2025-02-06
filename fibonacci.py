from functools import lru_cache
from icecream import ic

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

ic(fibonacci(200))  # Blazing fast after caching!