"""UUID generation utilities.

This module provides functions for generating UUIDs, with a focus on UUIDv7
which uses timestamp-based ordering for better database performance.
"""

import uuid


def generate_uuidv7() -> str:
    """
    Generate a UUIDv7 string.

    UUIDv7 uses timestamp-based ordering for better database performance.
    Tries to use uuid_utils library, falls back to modified UUID4.

    Returns:
        UUIDv7 string in format: 8-4-4-4-12 hexadecimal characters

    Example:
        >>> api_key = generate_uuidv7()
        >>> print(api_key)
        "019a4757-c049-7ea8-a110-2ea110c5a6f6"
    """
    try:
        # Try to use uuid7 if available
        import uuid_utils as uuid_lib

        return str(uuid_lib.uuid7())
    except ImportError:
        # Fallback: Generate uuid4 and modify version bits to 7
        # This is a simplified approach - in production, use proper uuid7 library
        uid = uuid.uuid4()
        uid_str = str(uid)
        # Replace version nibble (13th char after hyphens) with '7'
        parts = uid_str.split("-")
        parts[2] = "7" + parts[2][1:]
        return "-".join(parts)
