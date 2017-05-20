#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from typing import Iterable, Optional, TypeVar, List, \
                   Callable, Iterator, Tuple, Dict, \
                   Any, Set, Union
T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')

import builtins    as _builtins
import itertools   as _itertools
import functools   as _functools
import random      as _random
import collections as _collections

import fx.semigroups as _semigroups

from fx.op import identity, itemgetter, attrgetter


__all__ = [
    'min', 'max',
    'map', 'starmap'
    'zip', 'zip_with', 'zip_longest',
    'spliton', 'spliton2',
    'filter', 'filterfalse',
    'range', 'reversed', 'reduce', 'tee',
    'islice', 'chain', 'product',
    'interleave', 'interleave_longest',
    'flatten',
    'iterate', 'repeat', 'repeatfunc',
    'cycle', 'pad',
    'take', 'drop', 'peek',
    'takewhile', 'dropwhile',
    'takelast', 'droplast', 'peekwhile'
    'nth', 'head', 'tail',
    'find',
    'count', 'countwhile', 'counter',
    'uniq',
    'pairwise', 'sliding', 'grouped',
    'groupby', 'rungroupby',
    'filter_by_min_freq',
    'indices',
    'sample', 'hash_sample', 'reservoir_sample',
    'throttle', 'threaded_throttle',
    'merge_many',
    'shuffle'
    'windowdiffs', 'windows'
    'remap']


_SENTINEL = object()


iter = _builtins.iter


def destructive(lst: List[T]) -> Iterator[T]:
    if not isinstance(lst, list):
        raise ValueError('Destructive iterator requires a mutable list.')

    for i, v in enumerate(lst):
        lst[i] = None
        yield v


map = _builtins.map
"""
map(function, sequence[, sequence, ...]) -> iterable

Make an iterator that computes the function using arguments from each
of the iterables. If function is set to None, then map() returns
the arguments as a tuple.
"""


starmap = _itertools.starmap
"""
Make an iterator that computes the function using arguments obtained
from the iterable. Used instead of map() when argument parameters are
already grouped in tuples from a single iterable (the data has been
"pre-zipped").
"""


zip = _builtins.zip
"""
Make an iterator that aggregates elements from each of the iterables.
Used for lock-step iteration over several iterables at a time.
"""


zip_longest = _itertools.zip_longest
"""
Make an iterator that aggregates elements from each of the iterables.
If the iterables are of uneven length, missing values are filled-in with
fillvalue. Iteration continues until the longest iterable is exhausted.
"""


def zip_with(f: Callable[..., T], *coll: List[Iterable[U]]) -> Iterator[T]:
    return starmap(f, zip(*coll))


filter = _builtins.filter
"""
Construct an iterator from those elements of iterable for which function
returns true. iterable may be either a sequence, a container which supports
iteration, or an iterator. If function is None, the identity function is
assumed, that is, all elements of iterable that are false are removed.

>>> list(filter(lambda x: x > 0, [1, 2, -1, 3]))
[1, 2, 3]
"""


filternot = _itertools.filterfalse

reduce = _functools.reduce
range = _builtins.range


reversed = _builtins.reversed
"""
Return a reverse iterator. seq must be an object which has a __reversed__()
method or supports the sequence protocol (the __len__() method and the
__getitem__() method with integer arguments starting at 0).
"""

def spliton(iterable: Iterable[T],
            key: Callable[[T], Optional[U]],
            default_key: Optional[U]=None
            ) -> Iterator[Tuple[U, List[T]]]:
    """
    Splits iterator whenever key value is not None.

    >>> list(spliton([1, 2, 3, 4, 5], key=lambda i: None if i%2 == 0 else i))
    [(1, [1, 2]), (3, [3, 4]), (5, [5])]
    """
    current_key = default_key
    elements = [] # type: List[T]

    for value in iterable:
        new_key = key(value)

        if new_key is not None:
            if len(elements) > 0:
                yield (current_key, elements)
                elements = []
            elements.append(value)
            current_key = new_key
        else:
            elements.append(value)

    if len(elements) > 0:
        yield (current_key, elements)


def spliton2(iterable: Iterable[T],
             key: Callable[[T, T], Optional[U]],
             default_key: Optional[U]=None,
             filler: T=None
             ) -> Iterator[Tuple[U, List[T]]]:
    current_key = default_key
    last_value = filler
    elements = [] # type: List[T]

    for value in iterable:
        new_key = key(last_value, value)

        if new_key is not None:
            if len(elements) > 0:
                yield (current_key, elements)
                elements = []
            elements.append(value)
            current_key = new_key
        else:
            elements.append(value)

        last_value = value

    if len(elements) > 0:
        yield (current_key, elements)


tee = _itertools.tee
"""
Return n independent iterators from a single iterable.
"""

islice = _itertools.islice



chain = _itertools.chain
"""
Make an iterator that returns elements from the first iterable until it is
exhausted, then proceeds to the next iterable, until all of the iterables
are exhausted. Used for treating consecutive sequences as a single sequence.

>>> list(chain([1, 2], [3], [4]))
[1, 2, 3, 4]
>>> list(chain([1], repeat(2, 3), [3]))
[1, 2, 2, 2, 3]
"""


def interleave(*iterables: List[Iterable[T]]) -> Iterator[T]:
    """
    Return a new iterable yielding from each iterable in turn,
    until the shortest is exhausted.

    >>> list(interleave([1, 2, 3], [4, 5], [6, 7, 8]))
    [1, 4, 6, 2, 5, 7]

    Note that this is the same as ``chain(*zip(*iterables))``.
    For a version that doesn't terminate after the shortest iterable is
    exhausted, see ``interleave_longest()``.
    """
    return chain.from_iterable(zip(*iterables))


def interleave_longest(*iterables: List[Iterable[T]]) -> Iterator[T]:
    """
    Return a new iterable yielding from each iterable in turn,
    skipping any that are exhausted.

    >>> list(interleave_longest([1, 2, 3], [4, 5], [6, 7, 8]))
    [1, 4, 6, 2, 5, 7, 3, 8]

    Note that this is an alternate implementation of ``roundrobin()`` from the
    itertools documentation.
    """
    i = chain.from_iterable(zip_longest(*iterables, fillvalue=_SENTINEL))
    return filter(lambda x: x is not _SENTINEL, i)


def flatten(iterable: Iterable[Iterable[T]]) -> Iterable[T]:
    """
    Flatten one level of nesting.

    >>> list(flatten([[1], [2, 3]]))
    [1, 2, 3]
    """
    return chain.from_iterable(iterable)


def iterate(f: Callable[[T], T], x: T, times: Optional[int]=None) -> Iterator[T]:
    """
    Return an iterator yielding x, f(x), f(f(x)) etc.

    >>> list(iterate(lambda x: x + 1, 1, 5))
    [1, 2, 3, 4, 5]
    >>> list(take(5, iterate(lambda x: x + 1, 1)))
    [1, 2, 3, 4, 5]
    """
    r = repeat(None) if times is None else range(times)
    for _ in r:
        yield x
        x = f(x)


repeat = _itertools.repeat


def repeatfunc(func: Callable[..., T], times: Optional[int]=None, *args: List[Any]) -> Iterator[T]:
    """
    Repeat calls to func with specified arguments.

    Example:  repeatfunc(random.random)
    """
    if times is None:
        return starmap(func, repeat(args))
    return starmap(func, repeat(args, times))


def cycle(iterable: Iterable[T], times: Optional[int]=None) -> Iterator[T]:
    """Cycle through the sequence elements multiple times."""
    if times is None:
        return _itertools.cycle(iterable)
    return chain.from_iterable(repeat(tuple(iterable), times))


def pad(iterable: Iterable[T], value: T=None) -> Iterator[T]:
    """
    Make an iterator that returns elements from the iterable until it is
    exhausted, then proceeds to yield a specified value indefinitely.
    """
    return chain(iterable, repeat(value))


product = _itertools.product


def take(limit: int, base: Iterable[T]) -> Iterator[T]:
    """
    >>> list(take(2, [1, 2, 3, 4]))
    [1, 2]
    >>> list(take(2, [1]))
    [1]
    """
    assert limit >= 0
    return islice(base, limit)


def drop(limit: int, base: Iterable[T]) -> Iterator[T]:
    """
    >>> list(drop(2, [1, 2, 3, 4]))
    [3, 4]
    >>> list(drop(2, [1]))
    []
    """
    assert limit >= 0
    return islice(base, limit, None)


def peek(limit: int, base: Iterable[T]) -> Tuple[List[T], Iterator[T]]:
    """
    Peeks at most 'limit' elements from an iterator, returning
    the original iterator intact.

    >>> peek(2, [1, 2, 3, 4])[0]
    [1, 2]
    >>> list(peek(2, [1, 2, 3, 4])[1])
    [1, 2, 3, 4]
    >>> peek(2, [1])[0]
    [1]
    >>> list(peek(2, [1])[1])
    [1]
    """
    assert limit >= 0
    base = iter(base)

    if limit == 0:
        return [], base

    elements = []
    try:
        for i in range(limit):
            elements.append(next(base))
    except:
        return elements[:], iter(elements)
    else:
        return elements[:], chain(iter(elements), base)


def takelast(limit: int, base: Iterable[T]) -> Iterator[T]:
    """Return iterator to produce last n items from origin.

    >>> list(takelast(2, [1, 2, 3, 4]))
    [3, 4]
    >>> list(takelast(2, [1]))
    [1]
    """
    return iter(_collections.deque(base, maxlen=limit))


def droplast(limit: int, base: Iterable[T]) -> Iterator[T]:
    """Return iterator to produce items from origin except last n

    >>> list(droplast(2, [1, 2, 3, 4]))
    [1, 2]
    >>> list(droplast(2, [1]))
    []
    """
    t1, t2 = tee(base)
    return map(itemgetter(0), zip(t1, islice(t2, limit, None)))

takewhile = _itertools.takewhile
"""
>>> list(takewhile(lambda x: x <= 2, [1, 2, 3, 4, 2]))
[1, 2]
>>> list(takewhile(lambda x: x <= 2, [1]))
[1]
"""

dropwhile = _itertools.dropwhile
"""
>>> list(dropwhile(lambda x: x <= 2, [1, 2, 3, 4, 2]))
[3, 4, 2]
>>> list(dropwhile(lambda x: x <= 2, [1]))
[]
"""

def peekwhile(predicate: Callable[[T], bool], base: Iterable[T]
              ) -> Tuple[List[T], Iterator[T]]:
    """
    Peeks elements from an iterator until predicate fails, returning
    the original iterator intact.

    >>> peekwhile(lambda x: x <= 2, [1, 2, 3, 4])[0]
    [1, 2]
    >>> list(peekwhile(lambda x: x <= 2, [1, 2, 3, 4])[1])
    [1, 2, 3, 4]
    >>> peekwhile(lambda x: x <= 2, [1])[0]
    [1]
    >>> list(peekwhile(lambda x: x <= 2, [1])[1])
    [1]
    """
    predicate = identity if predicate is None else predicate
    base = iter(base)

    elements = []

    for value in base:
        if predicate(value):
            elements.append(value)
        else:
            return elements[:], chain(iter(elements), [value], base)
    return elements[:], iter(elements)


def nth(iterable: Iterable[T], n: int, default: Optional[T]=None) -> Optional[T]:
    """Returns the nth item or a default value
    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    return next(islice(iterable, n, None), default)


def head(iterable: Iterable[T], default: Optional[T]=None) -> Optional[T]:
    return nth(iterable, 0, default)


def tail(iterable: Iterable[T])-> Iterable[T]:
    return drop(1, iterable)


def find(predicate: Callable[[T], bool],
         iterable: Iterable[T],
         default: T=None
         ) -> Optional[T]:
    return next(dropwhile(lambda x: not predicate(x), iterable), default)


def count(predicate: Optional[Callable[[T], bool]], iterable: Iterable[T]) -> int:
    """Count how many times the predicate is true."""
    if predicate is None:
        return sum(1 for x in iterable)
    else:
        return sum(1 for x in iterable if predicate(x))


def countwhile(predicate: Callable[[T], bool], iterable: Iterable[T]) -> int:
    return count(None, takewhile(predicate, iterable))


def counter(iterable: Iterable[T],
            key: Callable[[T], U]=identity
            ) -> Dict[U, int]:
    return _collections.Counter(key(x) for x in iterable)


def uniq(iterable: Iterable[T],
         key: Callable[[T], U]=identity,
         first: bool=True
         ) -> Iterator[Tuple[int, T]]:
    """
    Similar to unix uniq command, selects unique elements from an iterator.

    >>> list(uniq([1, 1, 2, 2, 2, 3]))
    [(2, 1), (3, 2), (1, 3)]

    >>> list(uniq('aaabbc'))
    [(3, 'a'), (2, 'b'), (1, 'c')]

    >>> list(uniq('AaabBc', key=lambda c: c.lower()))
    [(3, 'A'), (2, 'b'), (1, 'c')]

    >>> list(uniq('AaabBc', key=lambda c: c.lower(), first=False))
    [(3, 'a'), (2, 'B'), (1, 'c')]
    """

    sentinel   = _SENTINEL # type: Any

    cnt        = 0
    last_key   = sentinel  # type: U
    last_value = sentinel  # type: T

    for v in iterable:
        k = key(v)

        if k == last_key:
            cnt += 1
            if not first:
                last_value = v
        else:
            if last_value is not sentinel:
                yield (cnt, last_value)

            cnt        = 1
            last_key   = k
            last_value = v

    if last_value is not sentinel:
        yield (cnt, last_value)


def distinct(iterable: Iterable[T],
             key: Callable[[T], U]=identity
             ) -> Iterator[T]:
    """
    Similar to unix uniq command, selects unique elements from an iterator.

    >>> list(distinct([1, 1, 2, 1, 2, 2, 1, 2, 3]))
    [1, 2, 3]

    >>> list(distinct('aaababcab'))
    ['a', 'b', 'c']

    >>> list(distinct('AaabaABcb', key=lambda c: c.lower()))
    ['A', 'b', 'c']
    """

    seen = set() # type: Set[U]
    for v in iterable:
        k = key(v)
        if k in seen:
            continue
        seen.add(k)
        yield v


def pairwise(iterable: Iterable[T]) -> Iterator[Tuple[T, T]]:
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def sliding(iterable: Iterable[T], length: int, step: int=1
            ) -> Iterator[List[T]]:
    """Groups elements in fixed size blocks by passing a "sliding window"
    over them (as opposed to partitioning them, as is done in grouped.)
    "Sliding window" step is 1 by default.
    >>> list(sliding([1, 2, 3], 2))
    [[1, 2], [2, 3]]
    >>> list(sliding([1], 2))
    [[1]]
    >>> list(sliding([], 2))
    []
    >>> list(sliding([1, 2, 3], 2, 2))
    [[1, 2], [3]]
    """
    assert length > 0
    assert step > 0
    assert step <= length

    result = []
    yielded = True

    for v in iterable:
        result.append(v)
        if len(result) == length:
            yield result[:]
            del result[:step]
            yielded = True
        else:
            yielded = False

    if not yielded:
        yield result[:]


def grouped(n: int, iterable: Iterable[T], fillvalue: T=None
            ) -> Iterator[Tuple[T, ...]]:
    """Collect data into fixed-length chunks or blocks, so
    grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


rungroupby = _itertools.groupby


def groupby(iterable: Iterable[T],
            key: Optional[Callable[[T], Any]]=None,
            keys: Optional[Callable[[T], Tuple[Any, ...]]]=None,
            mapfunc: Callable[[T], U]=identity,
            semigroup: Union[str, _semigroups.AlgebraK[U, V]]='list'
            ) -> Dict[Any, Any]:
    """
    ... # doctest: +NORMALIZE_WHITESPACE
    >>> d = groupby(['abc', 'acd', 'dsa', 'dw', 'd', 'k'],
    ...             key=lambda w: w[0]).items()
    >>> sorted(d)
    [('a', ['abc', 'acd']), ('d', ['dsa', 'dw', 'd']), ('k', ['k'])]
    """

    if keys is None:
        if key is not None:
            keyfunc = lambda t: (key(t),)
        else:
            keyfunc = lambda t: (t,)
    else:
        keyfunc = keys

    if isinstance(semigroup, str):
        sgk = _semigroups.get_named(semigroup)
        # type: _semigroups.AlgebraK[U, V]
    else:
        sgk = semigroup

    result = {} # type: Dict[Any, Any]
    def resolve(d: Dict[Any, Any], k: Tuple[Any, ...]
                ) -> Tuple[Dict[Any, V], Any]:
        for i in range(len(k) - 1):
            d = d.setdefault(k[i], {})
        return d, k[-1]

    for v in iterable:
        d, k = resolve(result, keyfunc(v))
        if k in d:
            d[k] = sgk.iappend(d[k], mapfunc(v))
        else:
            d[k] = sgk.unit(mapfunc(v))
    return result


max = _builtins.max
min = _builtins.min


def filter_by_min_freq(iterable: Iterable[T],
                       n: int,
                       key: Callable[[T], U]=identity
                       ) -> Set[T]:
    result      = set() # type: Set[T]
    result_keys = set() # type: Set[U]
    candidates  = {}    # type: Dict[U, int]

    for v in iterable:
        k = key(v)

        if k in result_keys:
            continue

        cnt = candidates.setdefault(k, 0)
        cnt = cnt + 1

        if cnt >= n:
            del candidates[k]
            result.add(v)
            result_keys.add(k)
        else:
            candidates[k] = cnt

    return result


def indices(iterable: Iterable[T]) -> Dict[T, int]:
    result = {} # type: Dict[T, int]
    for i, v in enumerate(iterable):
        result.setdefault(v, i)
    return result


def sample(rate: int, iterable: Iterable[T]) -> Iterator[T]:
    n = 0
    for v in iterable:
        if n % rate == 0:
            yield v
        n += 1


def hash_sample(rate: int, iterable: Iterable[T],
                hash: Callable[[T], int]=hash
                ) -> Iterator[T]:
    return (v for v in iterable if hash(v) % rate == 0)


def reservoir_sample(limit: int,
                     iterable: Iterable[T],
                     rng: Any=None) -> List[T]:
    sample = []

    if rng is None:
        rand = _random.random
        # python's randint is inclusive
        randint = lambda x: _random.randint(0, x)
    else:
        rand = rng.rand
        # numpy's randint is exclusive on the higher bound
        randint = lambda x: rng.randint(0, x + 1)

    for i, v in enumerate(iterable):
        if i < limit:
            sample.append(v)
        elif i >= limit and rand() < limit / float(i+1):
            replace = randint(len(sample) - 1)
            sample[replace] = v
    return sample


def throttle(iterable: Iterable[T],
             key: Callable[[T], float]=identity,
             delay: float=0
             ) -> Iterator[T]:
    last = None
    for v in iterable:
        k = key(v)
        if last is None or last + delay <= k:
            last = k
            yield v


def threaded_throttle(iterable: Iterable[T],
                      keys: Callable[[T], Tuple[U, float]],
                      delay: float=0
                      ) -> Iterator[T]:
    last = {} # type: Dict[U, float]
    for v in iterable:
        thread, key = keys(v)

        if thread not in last or last[thread] + delay <= key:
            last[thread] = key
            yield v


def merge_many(key: Callable[[T], U], *args: List[Iterable[T]]) -> Iterator[T]:
    """Merge multiple sorted inputs into a single sorted output.

    Equivalent to:  sorted(itertools.chain(*iterables))

    >>> list(merge_many(identity, [1,3,5,7], [0,2,4,8], [5,10,15,20], [], [25]))
    [0, 1, 2, 3, 4, 5, 5, 7, 8, 10, 15, 20, 25]

    """
    import heapq as _heapq

    heappop, siftup, _StopIteration = \
        _heapq.heappop, _heapq._siftup, StopIteration

    its = [] # type: List[List[Any]]
    h   = [] # type: List[List[Any]]
    h_append = h.append
    for it in map(iter, args):
        try:
            v = next(it)
            k = key(v)
            n = len(its)
            its.append([v, it])
            h_append([k, n])
        except _StopIteration:
            pass
    _heapq.heapify(h)

    while 1:
        try:
            while 1:
                # raises IndexError when h is empty
                k, n = h[0]
                v, it = its[n]
                yield v
                # raises StopIteration when exhausted
                v = next(it)
                its[n][0] = v
                h[0][0] = key(v)
                # restore heap condition
                siftup(h, 0)
        except _StopIteration:
            # remove empty iterator
            heappop(h)
        except IndexError:
            return


def shuffle(iterable: Iterable[T], rng: Any=None) -> List[T]:
    if rng is None:
        rng = _random
    result = list(iterable)
    rng.shuffle(result)
    return result


def windowdiffs(sorted_iterable: Iterable[T],
                key_func: Callable[[T], float],
                window_size: float,
                window_step: float=None,
                window_start: float=None
                ) -> Iterator[Tuple[float, float, int, List[T]]]:
    """
    >>> list(windowdiffs([0, 1, 1, 2, 2, 2.4, 2.9, 3.5,
    ...                   4, 4.1, 4.2, 4.3, 5], lambda k: k, 2, 1))
    ... # doctest: +NORMALIZE_WHITESPACE
    [(0, 2, 0, [0, 1, 1]),
     (1, 3, 1, [2, 2, 2.4, 2.9]),
     (2, 4, 2, [3.5]),
     (3, 5, 4, [4, 4.1, 4.2, 4.3]),
     (4, 6, 1, [5])]
    """
    values = iter(sorted_iterable)

    old_keys   = [] # type: List[float]
    new_keys   = [] # type: List[float]
    new_values = [] # type: List[T]

    # If window_step is not specified, assume that
    # the step is equal to the size.
    if window_step is None:
        window_step = window_size

    # If window_start is not specified, assume that
    # we start with the first item.
    if window_start is None:
        new_values.append(next(values))
        window_start = key_func(new_values[0])
        new_keys.append(window_start)

    for value in values:
        key = key_func(value)

        if key < window_start + window_size:
            new_keys.append(key)
            new_values.append(value)
            continue

        while key >= window_start + window_size:
            new_window_start = window_start + window_step

            remove = countwhile(lambda k: k < window_start, old_keys)
            del old_keys[:remove]
            old_keys.extend(new_keys)

            yield (window_start, window_start + window_size,
                   remove, new_values)

            new_keys = []
            new_values = []
            window_start = new_window_start

        new_keys.append(key)
        new_values.append(value)

    remove = countwhile(lambda k: k < window_start, old_keys)
    yield (window_start, window_start + window_size,
           remove, new_values)


def windows(sorted_iterable: Iterable[T],
            key_func: Callable[[T], float],
            window_size: float,
            window_step: float=None,
            window_start: float=None
            ) -> Iterator[Tuple[float, float, List[T]]]:
    """
    >>> list(windows([0, 1, 1, 2, 2, 2.4, 2.9, 3.5,
    ...               4, 4.1, 4.2, 4.3, 5], lambda k: k, 2, 1))
    ... # doctest: +NORMALIZE_WHITESPACE
    [(0, 2, [0, 1, 1]),
     (1, 3, [1, 1, 2, 2, 2.4, 2.9]),
     (2, 4, [2, 2, 2.4, 2.9, 3.5]),
     (3, 5, [3.5, 4, 4.1, 4.2, 4.3]),
     (4, 6, [4, 4.1, 4.2, 4.3, 5])]
    """
    diffs = windowdiffs(sorted_iterable, key_func,
                        window_size, window_step, window_start)

    items = [] # type: List[T]
    for t0, t1, remove, add in diffs:
        del items[:remove]
        items += add
        yield (t0, t1, items[:])


def remap(iterable: Iterable[T], predicate: Callable[[int, T], bool]
          ) -> Tuple[List[T], List[int]]:
    """
    >>> remap([3, 2, 3], lambda i, x: x > 0)
    ([3, 2, 3], [0, 1, 2])
    >>> remap([3, 2, 3], lambda i, x: x < 0)
    ([], [-1, -1, -1])
    >>> remap([3, 2, 3], lambda i, x: x > 2)
    ([3, 3], [0, -1, 1])
    >>> remap([3, 3, 3], lambda i, x: x > i + 1)
    ([3, 3], [0, 1, -1])
    """
    remapping = []
    result = []
    j = 0
    for i, v in enumerate(iterable):
        if predicate(i, v):
            result.append(v)
            remapping.append(j)
            j += 1
        else:
            remapping.append(-1)
    return (result, remapping)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
