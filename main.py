from contextlib import contextmanager
from typing import Callable

type Result[T, E] = Ok[T, E] | Err[T, E]


class Ok[T, E]:
    def __init__(self, value: T):
        self.value = value

    def is_ok(self):
        return True

    def is_err(self):
        return False

    def ok(self):
        return self.value

    def err(self):
        return None

    def map[S](self, fn: Callable[[T], S]) -> Result[S, E]:
        return Ok(fn(self.value))

    def map_err[F](self, fn: Callable[[E], F]) -> Result[T, F]:
        return self

    def and_then[U](self, fn: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return fn(self.value)

    def unwrap(self):
        return self.value

    def unwrap_or(self, value: T):
        return self.value

    def set(self, value: T):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Ok) and self.value == other.value

    def __repr__(self):
        return f"Ok({self.value!r})"


class Err[T, E]:
    def __init__(self, value: E):
        self.value = value

    def is_ok(self):
        return False

    def is_err(self):
        return True

    def ok(self):
        return None

    def err(self):
        return self.value

    def map[S](self, fn: Callable[[T], S]) -> Result[S, E]:
        return self

    def map_err[F](self, fn: Callable[[E], F]) -> Err[T, F]:
        return Err(fn(self.value))

    def and_then[U](self, fn: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return self

    def unwrap(self):
        raise ValueError(self.value)

    def unwrap_or(self, value: T):
        return value

    def set(self, value: E):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Err) and self.value == other.value

    def __repr__(self):
        return f"Err({self.value!r})"


class Maybe[T, E]:
    result: Result[T, E] = Err(None)  # type: ignore


def safe[**P, T, E](func: Callable[P, T]) -> Callable[P, Result[T, E]]:
    def safeFunc(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as e:
            return Err(e)

    return safeFunc


@contextmanager
def sure[T, E](maybe: Maybe[T, E]):
    """
    Usage:
        res = Maybe()
        with sure(res):
            x = risky_thing()
            y = depends_on(x)
            res.result = Ok(y)

        # res.result is Ok(y) if body succeeded
        # res.result is Err(exception) if body threw
    """
    try:
        yield maybe
    except Exception as e:
        maybe.result = Err(e)
