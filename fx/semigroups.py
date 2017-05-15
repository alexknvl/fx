#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import TypeVar, Generic, Iterable, List, Any, Set
T = TypeVar('T')
U = TypeVar('U')

import collections as _collections


class AlgebraK(Generic[U, T]):
    def is_commutative(self) -> bool:
        return False

    def is_idempotent(self) -> bool:
        return False

    def is_mutable(self) -> bool:
        raise NotImplementedError()

    def unit(self, x: U) -> T: raise NotImplementedError()

    def add(self, x: T, y: T) -> T: raise NotImplementedError()

    def append(self, x: T, y: U) -> T:
        return self.add(x, self.unit(y))

    def extend(self, a: T, b: Iterable[U]) -> T:
        result = a
        for x in b:
            result = self.add(result, self.unit(x))
        return result

    def iadd(self, x: T, y: T) -> T:
        return self.add(x, y)

    def iappend(self, x: T, y: U) -> T:
        return self.append(x, y)

    def iextend(self, a: T, b: Iterable[U]) -> T:
        return self.extend(a, b)


class ListK(AlgebraK[U, List[U]], Generic[U]):
    def is_mutable(self) -> bool:
        return True

    def unit(self, x: U) -> List[U]:
        return [x]

    def add(self, x: List[U], y: List[U]) -> List[U]:
        return x + y

    def append(self, x: List[U], y: U) -> List[U]:
        return x + [y]

    def extend(self, a: List[U], b: Iterable[U]) -> List[U]:
        if not isinstance(b, list):
            return a + list(b)
        return a + b

    def iadd(self, xs: List[U], ys: List[U]) -> List[U]:
        xs.extend(ys)
        return xs

    def iappend(self, xs: List[U], x: U) -> List[U]:
        xs.append(x)
        return xs

    def iextend(self, xs: List[U], ys: Iterable[U]) -> List[U]:
        xs.extend(ys)
        return xs


class SetK(AlgebraK[U, Set[U]], Generic[U]):
    def is_mutable(self) -> bool:
        return True

    def unit(self, x: U) -> Set[U]:
        return set([x])

    def add(self, x: Set[U], y: Set[U]) -> Set[U]:
        return x | y

    def append(self, x: Set[U], y: U) -> Set[U]:
        return x | set((y,))

    def extend(self, a: Set[U], b: Iterable[U]) -> Set[U]:
        if not isinstance(b, set):
            return a | set(b)
        return a | b

    def iadd(self, xs: Set[U], ys: Set[U]) -> Set[U]:
        xs.update(ys)
        return xs

    def iappend(self, xs: Set[U], x: U) -> Set[U]:
        xs.add(x)
        return xs

    def iextend(self, xs: Set[U], ys: Iterable[U]) -> Set[U]:
        xs.update(ys)
        return xs


class CountK(AlgebraK[U, int], Generic[U]):
    def is_mutable(self) -> bool:
        return False

    def unit(self, x: U) -> int:
        return 1

    def add(self, x: int, y: int) -> int:
        return x + y

    def append(self, x: int, y: U) -> int:
        return x + 1

    def extend(self, a: int, b: Iterable[U]) -> int:
        if isinstance(b, _collections.Sized):
            return a + len(b)
        return a + sum(1 for _ in b)


class SumK(AlgebraK[float, float]):
    def is_mutable(self) -> bool:
        return False

    def unit(self, x: float) -> float:
        return x

    def add(self, x: float, y: float) -> float:
        return x + y

    def append(self, x: float, y: float) -> float:
        return x + y

    def extend(self, a: float, b: Iterable[float]) -> float:
        return a + sum(b)

_DEFAULT = {
    'list': ListK,
    'set': SetK,
    'count': CountK,
    'sum': SumK }

def get_named(name: str) -> AlgebraK[U, T]:
    return _DEFAULT.get(name)()
