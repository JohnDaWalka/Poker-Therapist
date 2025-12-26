"""JSON Merge Patch implementation (RFC 7396)."""

from typing import Any


def merge_patch(target: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    """
    Apply a JSON Merge Patch to a target object.
    
    Implementation of RFC 7396: https://tools.ietf.org/html/rfc7396
    
    Args:
        target: The target JSON object to be patched
        patch: The patch to apply
        
    Returns:
        The patched JSON object
    """
    if not isinstance(patch, dict):
        return patch

    if not isinstance(target, dict):
        target = {}

    result = target.copy()

    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        elif isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = merge_patch(result[key], value)
        else:
            result[key] = value

    return result
