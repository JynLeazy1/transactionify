"""Lambda handler for creating new accounts."""

import json
from typing import Dict, Any
from transactionify.tools.response import (
    ok,
    bad_request,
    unauthorized,
    internal_server_error,
)
from transactionify.services.account import create_account


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Create a new account for the authenticated user.

    The user_id comes from the authorizer context.

    Event format:
    {
        "requestContext": {
            "authorizer": {
                "lambda": {
                    "user_id": "019a4757-c049-7ea8-a110-2ea110c5a6f7"
                }
            }
        },
        "body": "{\"currency\": \"USD\"}"
    }

    Args:
        event: API Gateway event with user_id in authorizer context
        context: Lambda context object

    Returns:
        API Gateway response with account details

    Example response:
        {
            "statusCode": 200,
            "body": "{\"id\": \"019a4757-c049-7ea8-a110-2ea110c5a6f8\", \"balance\": {\"value\": \"0.00\", \"currency\": \"USD\"}}"
        }
    """
    print(f"Create account event: {json.dumps(event)}")

    # Extract user_id from authorizer context
    try:
        user_id = event["requestContext"]["authorizer"]["lambda"]["user_id"]
    except (KeyError, TypeError):
        return unauthorized("Unauthorized", "AuthorizationError")

    # Parse request body
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return bad_request("Invalid JSON in request body", "ValidationError")

    # Extract currency
    currency = body.get("currency", "").upper()
    if not currency:
        return bad_request("Missing required field: currency", "ValidationError")

    # Create account
    try:
        account = create_account(user_id, currency)
        print(f"Successfully created account for user: {user_id}")

        # Return id and balance
        return ok({"id": account["account_id"], "balance": account["balance"]})

    except ValueError as e:
        # Validation error from service - log the actual error but return safe message
        print(f"Validation error creating account: {str(e)}")
        # Check if it's a currency validation error
        if "currency" in str(e).lower():
            return bad_request(
                "Invalid currency. Allowed values: USD, EUR, GBP", "ValidationError"
            )
        # Generic validation error
        return bad_request("Invalid request data", "ValidationError")

    except Exception as e:
        # Log the actual error for debugging
        error_msg = f"Failed to create account: {str(e)}"
        print(error_msg)
        # Return safe generic message to client
        return internal_server_error(
            "An error occurred while creating the account", "InternalError"
        )
