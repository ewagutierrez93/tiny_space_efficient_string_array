"""Core implementation of a space-efficient string array."""

from __future__ import annotations

from typing import Iterator, List, Union, overload


class SpaceEfficientStringArray:
    """A string array that stores all elements in one internal buffer.

    Instead of holding a Python ``str`` object per element, this class joins
    the supplied strings into a single ``str`` (the *buffer*) and keeps a
    separate list of *boundaries* -- the cumulative length of the buffer up to
    and including the end of each element.

    The memory saving comes from reducing per-element overhead in Python's
    object model: one contiguous string plus one list of integers is, for many
    short elements, significantly smaller than a list of individual string
    objects. Each ``str`` object in CPython carries roughly 49 bytes of
    overhead before the first character of payload; for a thousand elements
    that overhead dominates the actual text.

    Trade-off: indexed access and iteration both allocate a new ``str`` slice
    on every call, so this class is best when the working set is built once
    and read with modest frequency, not when elements are mutated or scanned
    millions of times.
    """

    __slots__ = ("_buffer", "_boundaries")

    def __init__(self, elements: "Union[List[str], tuple[str, ...]]") -> None:
        """Build from an iterable of strings.

        Materialising the whole list up front is deliberate: the class is
        read-only by construction, so there is no need to support streaming
        appends. This keeps the boundary array a plain list of exact lengths,
        never resized.
        """
        if not isinstance(elements, (list, tuple)):
            raise TypeError("elements must be a list or tuple of str")

        # Validate eagerly rather than mid-build, so a bad element never
        # leaves the object in a partially-constructed state.
        for i, s in enumerate(elements):
            if not isinstance(s, str):
                raise TypeError(
                    "element at index %d is not a str (got %r)"
                    % (i, type(s).__name__)
                )

        # A single join is O(n) in the total character count and lets CPython
        # allocate the destination buffer exactly once.
        self._buffer: str = "".join(elements)

        # boundaries[i] is the cumulative length *after* element i, so
        # element 0 occupies [0, boundaries[0]) and element i (i>0)
        # occupies [boundaries[i-1], boundaries[i]).
        boundaries: List[int] = []
        running = 0
        for s in elements:
            running += len(s)
            boundaries.append(running)
        self._boundaries: List[int] = boundaries

    def __len__(self) -> int:
        """Return the number of stored elements."""
        return len(self._boundaries)

    @overload
    def __getitem__(self, index: int) -> str: ...
    @overload
    def __getitem__(self, index: slice) -> "SpaceEfficientStringArray": ...

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union[str, "SpaceEfficientStringArray"]:
        """Return one element (int) or a sub-array (slice).

        Slicing returns a new ``SpaceEfficientStringArray`` built from the
        selected elements. We materialise the selected strings and re-join
        them; the alternative would be to share the parent buffer and store a
        separate boundary list, but that retains a reference to the entire
        parent buffer, which defeats the purpose for long-lived slices.
        """
        if isinstance(index, slice):
            # boundaries is a plain list, so slice indexing is O(k) for the
            # selected range rather than O(n) over the whole array.
            selected_boundaries = self._boundaries[index]
            if not selected_boundaries:
                return SpaceEfficientStringArray([])
            start = self._boundaries[index.start or 0] if index.start and index.start != 0 else 0
            # Compute the text span for the selected slice directly from the
            # first and last boundaries.
            first = 0
            if index.start is not None and index.start > 0:
                first = self._boundaries[index.start - 1]
            last = selected_boundaries[-1]
            return SpaceEfficientStringArray([self._buffer[first:last]])

        # Python's negative indexing is the common awkward case; delegating to
        # list.__getitem__ on boundaries gives correct wraparound for free.
        end = self._boundaries[index]
        start = 0 if index == 0 or index == -len(self._boundaries) else self._boundaries[index - 1]
        return self._buffer[start:end]

    def __iter__(self) -> Iterator[str]:
        """Iterate over elements in order."""
        prev = 0
        for b in self._boundaries:
            yield self._buffer[prev:b]
            prev = b

    def __contains__(self, item: object) -> bool:
        """Return True if ``item`` is one of the stored strings."""
        if not isinstance(item, str):
            return False
        return any(element == item for element in self)

    def __eq__(self, other: object) -> bool:
        """Two arrays are equal iff they hold the same elements in order."""
        if isinstance(other, SpaceEfficientStringArray):
            return self._buffer == other._buffer and self._boundaries == other._boundaries
        return NotImplemented

    def __repr__(self) -> str:
        """Developer representation showing length and buffer size."""
        return "SpaceEfficientStringArray(%d elements, %d chars)" % (
            len(self._boundaries),
            len(self._buffer),
        )
