# `sure`: Monadic Errors in Python

This is the outcome of me programming in gleam and rust for a bit.

`Result[T, E]` includes: 
- `.is_ok`, `.is_err`
- `.ok()` / `.err()`: value or `None` 
- `.map(fn)` / `.map_err(fn)`
- `.and_then(fn)`
- `.unwrap()` / `.unwrap_or(default)`
- `.set(value)`: Mutation for context manager

And extras to not even have to `try` on already existing functions or code blocks. 
- `@safe` decorator, returns Result
- `sure(result)`: context manager, mutates on exception.

