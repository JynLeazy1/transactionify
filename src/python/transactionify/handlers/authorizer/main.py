import json
from typing import Dict, Any
from transactionify.tools.validators import is_valid_uuidv7
from transactionify.services.api_key import get_api_key


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda authorizer for API Gateway HTTP API using response format 2.0.

    Validates UUIDv7 API keys from the Authorization header against DynamoDB.
    Returns a simple boolean response indicating authorization status.

    Args:
        event: API Gateway authorizer event containing headers
        context: Lambda context object

    Returns:
        Authorization response with isAuthorized boolean and optional context
    """

    print(f"Authorizer event: {json.dumps(event)}")

    # Extract the API key from the Authorization header
    api_key = extract_api_key(event)

    if not api_key:
        print("No API key provided in Authorization header")
        return {"isAuthorized": False}

    # Validate UUIDv7 format
    if not is_valid_uuidv7(api_key):
        print(f"Invalid UUIDv7 format: {api_key}")
        return {"isAuthorized": False}

    # Validate the API key against DynamoDB
    try:
        api_key_item = get_api_key(api_key)

        if api_key_item:
            user_id = api_key_item.get("user_id", "")
            print(f"API key validated successfully for user: {user_id}")
            return {"isAuthorized": True, "context": {"user_id": user_id}}
        else:
            print(f"Invalid or expired API key: {api_key}")
            return {"isAuthorized": False}

    except Exception as e:
        print(f"Error validating API key: {str(e)}")
        return {"isAuthorized": False}


def extract_api_key(event: Dict[str, Any]) -> str:
    """
    Extract API key from the Authorization header.

    Expected format: "APIKey <UUIDv7>" (case-insensitive schema).

    Args:
        event: API Gateway event

    Returns:
        API key string or empty string if not found/invalid format

    Examples:
        "APIKey 019a4757-c049-7ea8-a110-2ea110c5a6f6" -> "019a4757-c049-7ea8-a110-2ea110c5a6f6"
        "apikey 019a4757-c049-7ea8-a110-2ea110c5a6f6" -> "019a4757-c049-7ea8-a110-2ea110c5a6f6"
        "Bearer 019a..." -> "" (not supported)
    """
    headers = event.get("headers", {})

    # Try Authorization header (case-insensitive)
    auth_header = None
    for key, value in headers.items():
        if key.lower() == "authorization":
            auth_header = value.strip()
            break

    if not auth_header:
        return ""

    # Check for "APIKey" schema (case-insensitive)
    parts = auth_header.split(maxsplit=1)
    if len(parts) != 2:
        return ""

    schema, api_key = parts
    if schema.lower() != "apikey":
        return ""

    return api_key.strip()
