from typing import Callable

from packaging.version import Version


class ComparableVersion:
    def __init__(self, version):
        self.version = Version(version)

    def __lt__(self, other: str):
        return self._apply_op(other, lambda x, y: x < y)

    def __le__(self, other: str):
        return self._apply_op(other, lambda x, y: x <= y)

    def __eq__(self, other: str):
        return self._apply_op(other, lambda x, y: x == y)

    def __ne__(self, other: str):
        return self._apply_op(other, lambda x, y: x != y)

    def __gt__(self, other: str):
        return self._apply_op(other, lambda x, y: x > y)

    def __ge__(self, other: str):
        return self._apply_op(other, lambda x, y: x >= y)

    def _apply_op(self, other: str, op: Callable[[Version, Version], bool]):
        other = Version(other)
        return op(self.version, other)
