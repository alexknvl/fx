from typing import TypeVar, Callable, Any
T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')

from functools import partial, update_wrapper, wraps
from inspect import getargspec
from operator import add, attrgetter, itemgetter

identity = lambda value: value

def const(value: T) -> Callable[[], T]:
    def f(*args: List[Any]) -> T:
        return value
    return f


def flip(f: Callable[[U, V], T]) -> Callable[[V, U], T]:
    """Return function that will apply arguments in reverse order"""

    flipper = getattr(f, "__flipback__", None)
    if flipper is not None:
        return flipper

    def _flipper(a: V, b: U) -> T:
        return f(b, a)

    setattr(_flipper, "__flipback__", f)
    return _flipper


def curried(func):
    """A decorator that makes the function curried
    Usage example:
    >>> @curried
    ... def sum5(a, b, c, d, e):
    ...     return a + b + c + d + e
    ...
    >>> sum5(1)(2)(3)(4)(5)
    15
    >>> sum5(1, 2, 3)(4, 5)
    15
    """
    @wraps(func)
    def _curried(*args, **kwargs):
        f = func
        count = 0
        while isinstance(f, partial):
            if f.args:
                count += len(f.args)
            f = f.func

        spec = getargspec(f)

        if count == len(spec.args) - len(args):
            return func(*args, **kwargs)

        para_func = partial(func, *args, **kwargs)
        update_wrapper(para_func, f)
        return curried(para_func)

    return _curried
