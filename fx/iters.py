from __future__ import absolute_import

import heapq
import random
from collections import deque, defaultdict
from operator import add, attrgetter, itemgetter
from .semigroups import DefaultSemigroupKs

from sys import version_info

# Uniform map, zip, filter, range
if version_info[0] == 2:
    from itertools import imap as map
    from itertools import izip as zip
    from itertools import ifilter as filter
    from __builtin__ import xrange as range
else:
    from functools import reduce

# Uniform itertools_filterfalse and itertools_zip_longest
if version_info[0] == 2:
    from itertools import ifilterfalse as itertools_filterfalse
    from itertools import izip_longest as itertools_zip_longest
else:
    from itertools import filterfalse as itertools_filterfalse
    from itertools import zip_longest as itertools_zip_longest

import itertools

map = map
starmap = itertools.starmap
zip = zip
zip_longest = itertools_zip_longest
filter = filter
reduce = reduce
range = range
reversed = reversed
tee = itertools.tee
chain = itertools.chain
islice = itertools.islice

identity = lambda value: value

def const(value):
    def f(*args):
        return value
    return f


def iterate(f, x, times=None):
    """
    Return an iterator yielding x, f(x), f(f(x)) etc.
    """
    r = repeat(None) if times is None else range(times)
    for _ in r:
        yield x
        x = f(x)


repeat = itertools.repeat


def repeatfunc(func, times=None, *args):
    """Repeat calls to func with specified arguments.
    Example:  repeatfunc(random.random)
    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    if times is None:
        return starmap(func, repeat(args))
    return starmap(func, repeat(args, times))


def cycle(iterable, times=None):
    """Returns the sequence elements n times
    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    if times is None:
        return itertools.cycle(iterable)
    return chain.from_iterable(repeat(tuple(iterable), n))


def padnone(iterable):
    """Returns the sequence elements and then returns None indefinitely.
    Useful for emulating the behavior of the built-in map() function.
    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    return chain(iterable, repeat(None))


product = itertools.product


def concat(*args):
    return chain(*(iter(a) for a in args))


def take(limit, base):
    """
    >>> list(take(2, [1, 2, 3, 4]))
    [1, 2]
    >>> list(take(2, [1]))
    [1]
    """
    assert limit >= 0

    return islice(base, limit)


def drop(limit, base):
    """
    >>> list(drop(2, [1, 2, 3, 4]))
    [3, 4]
    >>> list(drop(2, [1]))
    []
    """
    assert limit >= 0

    return islice(base, limit, None)


def peek(limit, base):
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


def takelast(limit, base):
    """
    Return iterator to produce last n items from origin.

    >>> list(takelast(2, [1, 2, 3, 4]))
    [3, 4]
    >>> list(takelast(2, [1]))
    [1]
    """
    return iter(deque(base, maxlen=limit))


def droplast(limit, base):
    """
    Return iterator to produce items from origin except last n

    >>> list(droplast(2, [1, 2, 3, 4]))
    [1, 2]
    >>> list(droplast(2, [1]))
    []
    """
    t1, t2 = tee(base)
    return map(itemgetter(0), zip(t1, islice(t2, limit, None)))

"""
>>> list(takewhile(lambda x: x <= 2, [1, 2, 3, 4, 2]))
[1, 2]
>>> list(takewhile(lambda x: x <= 2, [1]))
[1]
"""
takewhile = itertools.takewhile

"""
>>> list(dropwhile(lambda x: x <= 2, [1, 2, 3, 4, 2]))
[3, 4, 2]
>>> list(dropwhile(lambda x: x <= 2, [1]))
[]
"""
dropwhile = itertools.dropwhile


def peekwhile(predicate, base):
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


def nth(iterable, n, default=None):
    """Returns the nth item or a default value
    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    return next(islice(iterable, n, None), default)


def head(iterable, default=None):
    return nth(iterable, 0, default)


def tail(iterable, default=None):
    return drop(1, iterable)


def find(predicate, iterable, default=None):
    return next(dropwhile(lambda x: not predicate(x), iterable), default)


def count(predicate, iterable):
    """Count how many times the predicate is true."""
    if predicate is None:
        return sum(1 for x in iterable)
    else:
        return sum(1 for x in iterable if predicate(x))


def countwhile(predicate, iterable):
    return count(None, takewhile(predicate, iterable))


def counts(iterable, key=None):
    key = identity if key is None else key

    result = defaultdict(int)
    for x in iterable:
        result[x] += 1
    return result


def uniq(iterable, key=None, adjacent=True):
    """
    Similar to unix uniq command, selects unique elements from an iterator.
    """

    key = identity if key is None else key

    if adjacent:
        last_key = object()
        for v in iterable:
            k = key(v)
            if k == last_key:
                continue
            last_key = k
            yield v
    else:
        seen = set()
        for v in iterable:
            k = key(v)
            if k in seen:
                continue
            seen.add(k)
            yield v


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


def sliding(iterable, length, step=1):
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


def grouped(n, iterable, fillvalue=None):
    """Collect data into fixed-length chunks or blocks, so
    grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


rungroupby = itertools.groupby


def groupby(iterable, key=None, map=None, semigroup='list'):
    """
    ... # doctest: +NORMALIZE_WHITESPACE
    >>> d = groupby(['abc', 'acd', 'dsa', 'dw', 'd', 'k'],
    ...             key=lambda w: w[0]).items()
    >>> sorted(d)
    [('a', ['abc', 'acd']), ('d', ['dsa', 'dw', 'd']), ('k', ['k'])]
    """
    key = identity if key is None else key
    map = identity if map is None else map
    sgk = DefaultSemigroupKs.get(semigroup, semigroup)

    result = {}
    for v in iterable:
        k = key(v)
        if k in result:
            result[k] = sgk.iappend(result[k], map(v))
        else:
            result[k] = sgk.unit(map(v))
    return result


max = max
min = min


def remap(iterable, predicate):
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


def join(iterable):
    return (v for it in iterable for v in it)


def filter_by_min_freq(iterable, n, key=None):
    key = identity if key is None else key
    result = set()
    result_keys = set()
    candidates = {}

    for v in iterable:
        k = key(v)

        if k in result_keys:
            continue

        cnt = candidates.setdefault(k, 0)
        cnt = cnt + 1

        if cnt >= n:
            del candidates[k]
            result.add(k)
            result_keys.add(k)
        else:
            candidates[k] = cnt

    return result


def item_indices(lst):
    result = {}
    for i, v in enumerate(lst):
        result.setdefault(v, i)
    return result


def sample(iterable, key=None, rate=1):
    n = 0
    for v in iterable:
        if n % rate == 0:
            yield v
        n += 1


def hash_sample(iterable, key=None, rate=1):
    iterable = iter(iterable)
    key = identity if key is None else key

    for v in iterable:
        k = key(v)
        if hash(k) % rate == 0:
            yield v


def reservoir_sample(iterable, n, rng=None):
    sample = []

    if rng is None:
        rand = random.random
        # python's randint is inclusive
        randint = lambda x: random.randint(0, x)
    else:
        rand = rng.rand
        # numpy's randint is exclusive on the higher bound
        randint = lambda x: rng.randint(0, x + 1)

    for i, v in enumerate(iterable):
        if i < n:
            sample.append(v)
        elif i >= n and rand() < n / float(i+1):
            replace = randint(len(sample) - 1)
            sample[replace] = v
    return sample


def throttle(iterable, key=None, delay=0):
    iterable = iter(iterable)
    key = identity if key is None else key

    last = None
    for v in iterable:
        k = key(v)
        if last is None or last + delay <= k:
            last = k
            yield v


def throttle_threads(iterable, thread_key=None, time_key=None, delay=0):
    iterable = iter(iterable)
    thread_key = identity if thread_key is None else thread_key
    time_key = identity if time_key is None else time_key

    last = {}
    for v in iterable:
        thread = thread_key(v)
        time = time_key(v)

        if thread not in last or last[thread] + delay <= time:
            last[thread] = time
            yield v


def merge_many(*args, **kwargs):
    """Merge multiple sorted inputs into a single sorted output.

    Equivalent to:  sorted(itertools.chain(*iterables))

    >>> list(merge_many([1,3,5,7], [0,2,4,8], [5,10,15,20], [], [25]))
    [0, 1, 2, 3, 4, 5, 5, 7, 8, 10, 15, 20, 25]

    """
    key = kwargs.get('key', identity)
    heappop, siftup, _StopIteration = \
        heapq.heappop, heapq._siftup, StopIteration

    its = []
    h = []
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
    heapq.heapify(h)

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


def shuffle(iterable, rng=None):
    if rng is None:
        rng = random
    result = list(iterable)
    rng.shuffle(result)
    return result


def windowdiffs(sorted_iterable, key_func,
                window_size,
                window_step=None,
                window_start=None):
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

    old_keys = []
    new_keys = []
    new_values = []

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


def windows(sorted_iterable, key_func,
            window_size,
            window_step=None,
            window_start=None):
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

    items = []
    for t0, t1, remove, add in diffs:
        del items[:remove]
        items += add
        yield (t0, t1, items[:])


if __name__ == "__main__":
    import doctest
    doctest.testmod()
