from testcontainers.core.labels import (
    LABEL_LANG,
    LABEL_SESSION_ID,
    LABEL_TESTCONTAINERS,
    LABEL_VERSION,
    create_labels,
    TESTCONTAINERS_NAMESPACE,
)
import pytest
from testcontainers.core.config import RYUK_IMAGE


def assert_in_with_value(labels: dict, label: str, value: str, known_before_test_time: bool) -> None:
    assert label in labels
    if known_before_test_time:
        assert labels[label] == value


testdata = [
    (LABEL_LANG, "python", True),
    (LABEL_TESTCONTAINERS, "true", True),
    (LABEL_SESSION_ID, "some", False),
    (LABEL_VERSION, "some", False),
]


@pytest.mark.parametrize("label,value,known_before_test_time", testdata)
def test_containers_creates_expected_labels(label, value, known_before_test_time):
    actual_labels = create_labels("not-ryuk", None)
    assert_in_with_value(actual_labels, label, value, known_before_test_time)


def test_containers_throws_on_namespace_collision():
    with pytest.raises(ValueError):
        create_labels("not-ryuk", {TESTCONTAINERS_NAMESPACE: "fake"})


def test_containers_respect_custom_labels_if_no_collision():
    custom_namespace = "org.foo.bar"
    value = "fake"
    actual_labels = create_labels("not-ryuk", {custom_namespace: value})
    assert_in_with_value(actual_labels, custom_namespace, value, True)


def test_if_ryuk_no_session():
    actual_labels = create_labels(RYUK_IMAGE, None)
    assert LABEL_SESSION_ID not in actual_labels


def test_session_are_module_import_scoped():
    """
    Asserts that sessions are a module-level variable and don't differ between invocation
    """
    first_labels = create_labels("not-ryuk", None)
    second_labels = create_labels("not-ryuk", None)
    assert LABEL_SESSION_ID in first_labels
    assert LABEL_SESSION_ID in second_labels
    assert first_labels[LABEL_SESSION_ID] == second_labels[LABEL_SESSION_ID]
