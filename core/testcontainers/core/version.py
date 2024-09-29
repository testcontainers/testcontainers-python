from typing import Callable

from packaging.version import Version


class ComparableVersion:
    """A wrapper around packaging.version.Version that allows for comparison with strings"""

    def __init__(self, version: str) -> None:
        self.version = Version(version)

    def __lt__(self, other: object) -> bool:
        return self._apply_op(other, lambda x, y: x < y)

    def __le__(self, other: object) -> bool:
        return self._apply_op(other, lambda x, y: x <= y)

    def __eq__(self, other: object) -> bool:
        return self._apply_op(other, lambda x, y: x == y)

    def __ne__(self, other: object) -> bool:
        return self._apply_op(other, lambda x, y: x != y)

    def __gt__(self, other: object) -> bool:
        return self._apply_op(other, lambda x, y: x > y)

    def __ge__(self, other: object) -> bool:
        return self._apply_op(other, lambda x, y: x >= y)

    def _apply_op(self, other: object, op: Callable[[Version, Version], bool]) -> bool:
        other = Version(str(other))
        return op(self.version, other)
