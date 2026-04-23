from __future__ import annotations

import pytest

from main import Err, Ok, Result, Slot, safe, sure

# ── Ok ────────────────────────────────────────────────────────────────


class TestOk:
    def test_is_ok(self):
        assert Ok(1).is_ok() is True

    def test_is_err(self):
        assert Ok(1).is_err() is False

    def test_ok(self):
        assert Ok(42).ok() == 42

    def test_err(self):
        assert Ok(42).err() is None

    def test_map(self):
        assert Ok(2).map(lambda x: x * 3) == Ok(6)

    def test_map_changes_type(self):
        assert Ok(5).map(str) == Ok("5")

    def test_map_err_noop(self):
        result = Ok(5).map_err(str)
        assert result == Ok(5)

    def test_and_then(self):
        assert Ok(4).and_then(lambda x: Ok(x + 1)) == Ok(5)

    def test_and_then_to_err(self):
        assert Ok(-1).and_then(lambda _: Err("bad")) == Err("bad")

    def test_unwrap(self):
        assert Ok(99).unwrap() == 99

    def test_unwrap_or(self):
        assert Ok(99).unwrap_or(0) == 99

    def test_set(self):
        o = Ok(1)
        o.set(2)
        assert o.value == 2


# ── Err ───────────────────────────────────────────────────────────────


class TestErr:
    def test_is_ok(self):
        assert Err("e").is_ok() is False

    def test_is_err(self):
        assert Err("e").is_err() is True

    def test_ok(self):
        assert Err("e").ok() is None

    def test_err(self):
        assert Err("boom").err() == "boom"

    def test_map_noop(self):
        assert Err("e").map(lambda x: x * 2) == Err("e")

    def test_map_err(self):
        assert Err(404).map_err(str) == Err("404")

    def test_map_err_changes_type(self):
        result: Err[str, str] = Err(404).map_err(str)
        assert result == Err("404")

    def test_and_then_noop(self):
        assert Err("e").and_then(lambda x: Ok(x + 1)) == Err("e")

    def test_unwrap_raises(self):
        with pytest.raises(ValueError, match="boom"):
            Err("boom").unwrap()

    def test_unwrap_or(self):
        assert Err("e").unwrap_or(42) == 42

    def test_set(self):
        e = Err("a")
        e.set("b")
        assert e.value == "b"


# ── safe decorator ────────────────────────────────────────────────────


class TestSafe:
    def test_success(self):
        @safe
        def add(a, b):
            return a + b

        assert add(2, 3) == Ok(5)

    def test_failure(self):
        @safe
        def boom():
            raise RuntimeError("nope")

        result = boom()
        assert result.is_err()
        assert isinstance(result, Err)
        assert isinstance(result.err(), RuntimeError)

    def test_preserves_args(self):
        @safe
        def greet(name, greeting="hi"):
            return f"{greeting} {name}"

        assert greet("bob") == Ok("hi bob")
        assert greet("bob", greeting="yo") == Ok("yo bob")

    def test_does_not_catch_base_exception(self):
        @safe
        def interrupt():
            raise KeyboardInterrupt

        with pytest.raises(KeyboardInterrupt):
            interrupt()


# ── sure context manager ──────────────────────────────────────────────


class TestSure:
    def test_success_path(self):
        m = Slot()
        with sure(m):
            m.result = Ok("done")
        assert m.result == Ok("done")

    def test_exception_path(self):
        m = Slot()
        with sure(m):
            raise ValueError("oops")
        assert m.result.is_err()
        assert isinstance(m.result.err(), ValueError)

    def test_default_is_err(self):
        m = Slot()
        assert m.result.is_err()

    def test_nested_exceptions(self):
        m = Slot()
        with sure(m):
            m.result = Ok("partial")
            raise RuntimeError("late fail")
        # exception overrides the partial set
        assert m.result.is_err()
        assert isinstance(m.result.err(), RuntimeError)


# ── Chaining / integration ────────────────────────────────────────────


class TestChaining:
    def test_map_chain(self):
        result = Ok(1).map(lambda x: x + 1).map(lambda x: x * 3)
        assert result == Ok(6)

    def test_map_chain_err_short_circuits(self):
        result: Result[int, str] = Err("stop").map(lambda x: x + 1).map(lambda x: x * 3)
        assert result == Err("stop")

    def test_and_then_chain(self):
        result = Ok(10).and_then(lambda x: Ok(x + 5)).and_then(lambda x: Ok(str(x)))
        assert result == Ok("15")

    def test_and_then_chain_err_short_circuits(self):
        result: Result[int, str] = (
            Ok(10).and_then(lambda _: Err("halt")).and_then(lambda x: Ok(x + 1))
        )
        assert result == Err("halt")

    def test_safe_with_sure(self):
        @safe
        def parse(s):
            return int(s)

        res = parse("42")
        assert res == Ok(42)

        res = parse("abc")
        assert res.is_err()

    def test_sure_with_risky_ops(self):
        m = Slot()

        def risky(x):
            if x < 0:
                raise ValueError("negative")
            return x * 2

        with sure(m):
            val = risky(5)
            m.result = Ok(val)

        assert m.result == Ok(10)
