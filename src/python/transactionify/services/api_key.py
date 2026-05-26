from transactionify.tools.aws.dynamodb import get_by_full_match, is_expired, put_item
from transactionify.tools.validators import is_valid_uuidv7
from transactionify.tools.generators.uuid import generate_uuidv7


def get_api_key(value: str) -> dict:
    """
    Get API key from DynamoDB by its value.

    Args:
        value: The API key value (UUID)

    Returns:
        API key item dict if found and valid, empty dict otherwise
    """
    pk = f"API_KEY#{value}"
    item = get_by_full_match(pk=pk, sk="METADATA")

    if not item:
        return {}

    # Check if expired
    if is_expired(item):
        return {}

    return item


def register_new_api_key(user_id: str) -> str:
    """
    Register a new API key for a user.

    Creates a new UUIDv7 API key and stores it in DynamoDB.
    API keys do not expire.

    Args:
        user_id: The user identifier (must be valid UUIDv7)

    Returns:
        The generated API key (UUIDv7)

    Raises:
        ValueError: If user_id is not a valid UUIDv7

    Example:
        >>> api_key = register_new_api_key("019a4757-c049-7ea8-a110-2ea110c5a6f7")
        >>> print(api_key)
        "019a4757-c049-7ea8-a110-2ea110c5a6f6"
    """
    # Validate user_id format
    if not is_valid_uuidv7(user_id):
        raise ValueError(f"Invalid user_id format. Must be UUIDv7: {user_id}")

    # Generate API key (UUIDv7)
    api_key = generate_uuidv7()

    # Store API key in DynamoDB
    pk = f"API_KEY#{api_key}"
    put_item(pk=pk, sk="METADATA", attributes={"user_id": user_id})

    return api_key
