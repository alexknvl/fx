from collections import namedtuple

SemigroupK = namedtuple(
    'SemigroupK',
    ['unit',
     'add', 'append', 'extend',
     'iadd', 'iappend', 'iextend'])


def make_semigroupk(unit,
                    add, append=None, extend=None,
                    iadd=None, iappend=None, iextend=None):
    def append_impl(a, b):
        return add(a, unit(b))

    def extend_impl(a, b):
        r = a
        for x in b:
            r = add(r, unit(x))
        return r

    append = append if append is not None else append_impl
    extend = extend if extend is not None else extend_impl
    iadd = iadd if iadd is not None else add
    iappend = iappend if iappend is not None else append
    iextend = iextend if iextend is not None else extend

    return SemigroupK(unit,
                      add, append, extend,
                      iadd, iappend, iextend)


def list_iadd(xs, ys):
    xs.extend(ys)
    return xs


def list_iappend(xs, x):
    xs.append(x)
    return xs


def list_iextend(xs, ys):
    xs.extend(ys)
    return xs


def set_iadd(xs, ys):
    xs.update(ys)
    return xs


def set_iappend(xs, x):
    xs.add(x)
    return xs


def set_iextend(xs, ys):
    xs.update(ys)
    return xs

ListSemigroupK = SemigroupK(
    unit=lambda a: [a],
    add=lambda a, b: a + b,
    append=lambda a, b: a + [b],
    extend=lambda a, b: a + b,
    iadd=list_iadd,
    iappend=list_iappend,
    iextend=list_iextend)

SetSemigroupK = SemigroupK(
    unit=lambda a: set([a]),
    add=lambda a, b: a | b,
    append=lambda a, b: a | set((b,)),
    extend=lambda a, b: a | set(b),
    iadd=set_iadd,
    iappend=set_iappend,
    iextend=set_iextend)

CountSemigroupK = SemigroupK(
    unit=lambda a: 1,
    add=lambda a, b: a + b,
    append=lambda a, b: a + 1,
    extend=lambda a, b: a + len(b),
    iadd=lambda a, b: a + b,
    iappend=lambda a, b: a + 1,
    iextend=lambda a, b: a + len(b))

SumSemigroupK = SemigroupK(
    unit=lambda a: a,
    add=lambda a, b: a + b,
    append=lambda a, b: a + b,
    extend=lambda a, b: a + sum(b),
    iadd=lambda a, b: a + b,
    iappend=lambda a, b: a + b,
    iextend=lambda a, b: a + sum(b))

DefaultSemigroupKs = {
    'list': ListSemigroupK,
    'set': SetSemigroupK,
    'count': CountSemigroupK,
    'sum': SumSemigroupK}
