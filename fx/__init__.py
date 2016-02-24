from __future__ import absolute_import

import sys
import itertools
import heapq
import random

if sys.version_info < (3, 0):
    import __builtin__
    map = itertools.imap
    zip = itertools.izip
    filter = itertools.ifilter
    range = __builtin__.xrange
else:
    map = map
    zip = zip
    filter = filter
    range = range

from .semigroups import DefaultSemigroupKs

slice = itertools.islice
identity = lambda value: value
slice = itertools.islice
chain = itertools.chain
product = itertools.product
run_group_by = itertools.groupby


def bag(lst):
    result = {}
    for x in lst:
        result[x] = result.setdefault(x, 0) + 1
    return result


def take(iterable, n):
    return itertools.islice(iterable, n)


def takewhile(iterable, predicate):
    for v in iterable:
        if predicate(v):
            yield v
        else:
            break


def count(iterable):
    return sum(1 for _ in iterable)


def countwhile(iterable, predicate):
    return count(takewhile(iterable, predicate))


def join(iterable):
    return (v for it in iterable for v in it)


def peek(iterable, n=1):
    if n <= 0:
        return iterable

    iterable = iter(iterable)

    elements = []
    try:
        for i in range(n):
            elements.append(next(iterable))
    except:
        return elements[:], iter(elements)
    else:
        return elements[:], chain(iter(elements), iterable)


def concat(*args):
    return chain(*(iter(a) for a in args))


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


def item_indices(lst):
    result = {}
    for i, v in enumerate(lst):
        result.setdefault(v, i)
    return result


def max_by(iterable, key):
    result = None
    result_key = None
    iterable = iter(iterable)
    for v in iterable:
        k = key(v)
        if result_key is None or result_key < k:
            result_key = k
            result = v
    return result


def skip_duplicates(iterable, key=None):
    iterable = iter(iterable)
    key = identity if key is None else key

    seen = set([])
    for v in iterable:
        k = key(v)
        if k not in seen:
            seen.add(k)
            yield v


def hash_sample(iterable, key=None, rate=1):
    iterable = iter(iterable)
    key = identity if key is None else key

    for v in iterable:
        k = key(v)
        if hash(k) % rate == 0:
            yield v


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


def reservoir_sample(iterable, n, rng=None):
    sample = []

    if rng is None:
        rng = random

    for i, v in enumerate(iterable):
        if i < n:
            sample.append(v)
        elif i >= n and rng.random() < n / float(i+1):
            replace = rng.randint(0, len(sample) - 1)
            sample[replace] = v
    return sample


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

            remove = countwhile(old_keys, lambda k: k < window_start)
            del old_keys[:remove]
            old_keys.extend(new_keys)

            yield (window_start, window_start + window_size,
                   remove, new_values)

            new_keys = []
            new_values = []
            window_start = new_window_start

        new_keys.append(key)
        new_values.append(value)

    remove = countwhile(old_keys, lambda k: k < window_start)
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
