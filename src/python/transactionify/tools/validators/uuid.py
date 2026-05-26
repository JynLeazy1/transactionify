import re
from typing import Optional


# UUIDv7 regex pattern (format: 8-4-4-4-12 hexadecimal characters)
# Version field (13th character) must be '7'
# Variant field (17th character) must be '8', '9', 'a', or 'b'
UUID_V7_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def is_valid_uuidv7(value: Optional[str]) -> bool:
    """
    Validate that a string matches UUIDv7 format.

    UUIDv7 format:
    - 8-4-4-4-12 hexadecimal characters separated by hyphens
    - Version field (13th character) must be '7'
    - Variant field (17th character) must be '8', '9', 'a', or 'b'

    Args:
        value: String to validate

    Returns:
        True if valid UUIDv7, False otherwise

    Examples:
        >>> is_valid_uuidv7("019a4757-c049-7ea8-a110-2ea110c5a6f6")
        True
        >>> is_valid_uuidv7("019a4757-c049-4ea8-a110-2ea110c5a6f6")  # version 4, not 7
        False
        >>> is_valid_uuidv7("invalid")
        False
    """
    if not value:
        return False

    return UUID_V7_PATTERN.match(value) is not None
