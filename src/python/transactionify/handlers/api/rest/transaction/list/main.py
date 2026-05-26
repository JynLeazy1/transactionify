"""Lambda handler for listing account transactions."""

import json
from typing import Dict, Any
from transactionify.tools.response import (
    ok,
    bad_request,
    unauthorized,
    not_found,
    internal_server_error,
)
from transactionify.services.transaction import list_transactions


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    List transactions for an account with pagination support.

    The user_id comes from the authorizer context.
    The account_id comes from the path parameters.
    Pagination parameters come from query string.

    Event format:
    {
        "requestContext": {
            "authorizer": {
                "lambda": {
                    "user_id": "019a4757-c049-7ea8-a110-2ea110c5a6f7"
                }
            }
        },
        "pathParameters": {
            "account_id": "019a4757-c049-7ea8-a110-2ea110c5a6f8"
        },
        "queryStringParameters": {
            "limit": "20",
            "cursor": "eyJQSyI6..."
        }
    }

    Args:
        event: API Gateway event with user_id in authorizer context and account_id in path
        context: Lambda context object

    Returns:
        API Gateway response with paginated transactions

    Example response:
        {
            "statusCode": 200,
            "body": "{\"transactions\": [...], \"has_more\": true, \"next_cursor\": \"eyJQSyI6...\"}"
        }
    """
    print(f"List transactions event: {json.dumps(event)}")

    # Extract user_id from authorizer context
    try:
        user_id = event["requestContext"]["authorizer"]["lambda"]["user_id"]
    except (KeyError, TypeError):
        return unauthorized("Unauthorized")

    # Extract account_id from path parameters
    try:
        account_id = event["pathParameters"]["account_id"]
    except (KeyError, TypeError):
        return not_found("Account not found")

    # Extract query parameters for pagination
    query_params = event.get("queryStringParameters") or {}

    # Parse limit (default 20, max 100)
    try:
        limit = int(query_params.get("limit", 20))
        limit = max(1, min(limit, 100))  # Clamp between 1 and 100
    except (ValueError, TypeError):
        limit = 20

    # Get cursor for pagination
    cursor = query_params.get("cursor")

    # List transactions
    try:
        result = list_transactions(user_id, account_id, limit=limit, cursor=cursor)
        transaction_count = len(result.get("transactions", []))
        print(
            f"Successfully retrieved {transaction_count} transactions for account: {account_id}"
        )

        return ok(result)

    except ValueError as e:
        # Validation error from service - log the actual error but return safe message
        print(f"Validation error listing transactions: {str(e)}")
        error_msg = str(e).lower()

        # Check for specific error types
        if "cursor" in error_msg or "pagination" in error_msg:
            return bad_request("Invalid pagination cursor", "ValidationError")
        elif "account not found" in error_msg or "does not belong" in error_msg:
            return not_found("Account not found")

        # Generic validation error
        return not_found("Resource not found")

    except Exception as e:
        # Log the actual error for debugging
        error_msg = f"Failed to list transactions: {str(e)}"
        print(error_msg)
        # Return safe generic message to client
        return internal_server_error("An error occurred while retrieving transactions")
