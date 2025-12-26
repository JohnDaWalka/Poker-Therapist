"""Tests for JSON Merge Patch implementation."""


from dossier.json_merge_patch import merge_patch


def test_merge_patch_simple_replace() -> None:
    """Test simple field replacement."""
    target = {"a": "b"}
    patch = {"a": "c"}
    result = merge_patch(target, patch)
    assert result == {"a": "c"}


def test_merge_patch_add_field() -> None:
    """Test adding a new field."""
    target = {"a": "b"}
    patch = {"b": "c"}
    result = merge_patch(target, patch)
    assert result == {"a": "b", "b": "c"}


def test_merge_patch_delete_field() -> None:
    """Test deleting a field with null."""
    target = {"a": "b", "c": "d"}
    patch = {"a": None}
    result = merge_patch(target, patch)
    assert result == {"c": "d"}


def test_merge_patch_nested_object() -> None:
    """Test nested object update."""
    target = {"a": {"b": "c"}}
    patch = {"a": {"b": "d", "e": "f"}}
    result = merge_patch(target, patch)
    assert result == {"a": {"b": "d", "e": "f"}}


def test_merge_patch_nested_delete() -> None:
    """Test deleting nested field."""
    target = {"a": {"b": "c", "d": "e"}}
    patch = {"a": {"b": None}}
    result = merge_patch(target, patch)
    assert result == {"a": {"d": "e"}}


def test_merge_patch_replace_object_with_value() -> None:
    """Test replacing an object with a value."""
    target = {"a": {"b": "c"}}
    patch = {"a": "d"}
    result = merge_patch(target, patch)
    assert result == {"a": "d"}


def test_merge_patch_empty_patch() -> None:
    """Test empty patch returns unchanged target."""
    target = {"a": "b", "c": "d"}
    patch = {}
    result = merge_patch(target, patch)
    assert result == {"a": "b", "c": "d"}


def test_merge_patch_complex_scenario() -> None:
    """Test complex merge patch scenario."""
    target = {
        "title": "Goodbye!",
        "author": {"givenName": "John", "familyName": "Doe"},
        "tags": ["example", "sample"],
        "content": "This will be unchanged",
    }
    patch = {
        "title": "Hello!",
        "phoneNumber": "+01-123-456-7890",
        "author": {"familyName": None},
        "tags": ["example"],
    }
    result = merge_patch(target, patch)
    assert result == {
        "title": "Hello!",
        "author": {"givenName": "John"},
        "tags": ["example"],
        "content": "This will be unchanged",
        "phoneNumber": "+01-123-456-7890",
    }


def test_merge_patch_empty_target() -> None:
    """Test patching an empty target."""
    target = {}
    patch = {"a": "b", "c": {"d": "e"}}
    result = merge_patch(target, patch)
    assert result == {"a": "b", "c": {"d": "e"}}
