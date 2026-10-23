# tiny_space_efficient_string_array

Concatenates string elements into a single internal buffer and tracks element boundaries, so iteration and indexed access work without holding a separate Python `str` object per element.

```python
from tiny_space_efficient_string_array import SpaceEfficientStringArray

arr = SpaceEfficientStringArray(["alpha", "beta", "gamma"])
print(len(arr))   # 3
print(arr[0])     # alpha
print(arr[-1])    # gamma
print(list(arr))  # ["alpha", "beta", "gamma"]
print("beta" in arr)  # True
print(repr(arr))  # SpaceEfficientStringArray(3 elements, 14 chars)
```

## Why

In CPython every `str` object carries roughly 49 bytes of overhead before its first character. For a collection of many short strings, that overhead dominates the actual text. `SpaceEfficientStringArray` joins all elements into one contiguous `str` buffer and stores a list of cumulative end-offsets, replacing per-element string objects with a pair of arrays. For a few thousand short strings the memory saving is measurable; for a handful of long strings it is negligible.

The trade-off is access cost: every `__getitem__` call slices the buffer, allocating a fresh `str`. The structure is built once and read with modest frequency -- it is not a drop-in replacement for a list when elements are mutated or scanned millions of times. Mutation is not supported at all; build a new array instead.

## Edge cases

Empty strings are stored as zero-length spans, so `SpaceEfficientStringArray(["", "a", ""])` has length 3 and iterates to `["", "a", ""]`. Negative indexing follows Python's usual wraparound. The constructor rejects non-`str` elements (including `bytes`) and non-list/tuple iterables, failing fast rather than producing a silently corrupt buffer.

## Layout

- `src/tiny_space_efficient_string_array/__init__.py` -- exports `SpaceEfficientStringArray`.
- `src/tiny_space_efficient_string_array/core.py` -- the implementation.
- `tests/test_core.py` -- the test suite.

## Running

```
PYTHONPATH=src python -m unittest discover -s tests
```
