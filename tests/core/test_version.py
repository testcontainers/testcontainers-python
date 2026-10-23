import pytest
from packaging.version import InvalidVersion

from testcontainers.core.version import ComparableVersion


@pytest.fixture
def version():
    return ComparableVersion("1.0.0")


@pytest.mark.parametrize("other_version, expected", [("0.9.0", False), ("1.0.0", False), ("1.1.0", True)])
def test_lt(version, other_version, expected):
    assert (version < other_version) == expected


@pytest.mark.parametrize("other_version, expected", [("0.9.0", False), ("1.0.0", True), ("1.1.0", True)])
def test_le(version, other_version, expected):
    assert (version <= other_version) == expected


@pytest.mark.parametrize("other_version, expected", [("0.9.0", False), ("1.0.0", True), ("1.1.0", False)])
def test_eq(version, other_version, expected):
    assert (version == other_version) == expected


@pytest.mark.parametrize("other_version, expected", [("0.9.0", True), ("1.0.0", False), ("1.1.0", True)])
def test_ne(version, other_version, expected):
    assert (version != other_version) == expected


@pytest.mark.parametrize("other_version, expected", [("0.9.0", True), ("1.0.0", False), ("1.1.0", False)])
def test_gt(version, other_version, expected):
    assert (version > other_version) == expected


@pytest.mark.parametrize("other_version, expected", [("0.9.0", True), ("1.0.0", True), ("1.1.0", False)])
def test_ge(version, other_version, expected):
    assert (version >= other_version) == expected


@pytest.mark.parametrize(
    "invalid_version",
    [
        "invalid",
        "1..0",
    ],
)
def test_invalid_version_raises_error(invalid_version):
    with pytest.raises(InvalidVersion):
        ComparableVersion(invalid_version)


@pytest.mark.parametrize(
    "invalid_version",
    [
        "invalid",
        "1..0",
    ],
)
def test_comparison_with_invalid_version_raises_error(version, invalid_version):
    with pytest.raises(InvalidVersion):
        assert version < invalid_version

    with pytest.raises(InvalidVersion):
        assert version <= invalid_version

    with pytest.raises(InvalidVersion):
        assert version == invalid_version

    with pytest.raises(InvalidVersion):
        assert version != invalid_version

    with pytest.raises(InvalidVersion):
        assert version > invalid_version

    with pytest.raises(InvalidVersion):
        assert version >= invalid_version
