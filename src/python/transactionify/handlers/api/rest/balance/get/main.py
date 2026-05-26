"""Lambda handler for getting account balance."""

import json
from typing import Dict, Any
from transactionify.tools.response import (
    ok,
    unauthorized,
    not_found,
    internal_server_error,
)
from transactionify.services.balance import get_balance


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get the balance for an account.

    The user_id comes from the authorizer context.
    The account_id comes from the path parameters.

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
        }
    }

    Args:
        event: API Gateway event with user_id in authorizer context and account_id in path
        context: Lambda context object

    Returns:
        API Gateway response with balance details

    Example response:
        {
            "statusCode": 200,
            "body": "{\"balance\": {\"value\": \"0.00\", \"currency\": \"USD\"}, \"date\": \"2024-02-23T12:00:00Z\"}"
        }
    """
    print(f"Get balance event: {json.dumps(event)}")

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

    # Get balance
    try:
        balance_data = get_balance(user_id, account_id)
        print(f"Successfully retrieved balance for account: {account_id}")

        return ok(balance_data)

    except ValueError as e:
        # Validation error from service - log the actual error but return safe message
        print(f"Validation error getting balance: {str(e)}")
        error_msg = str(e).lower()

        # Check for specific error types
        if "account not found" in error_msg or "does not belong" in error_msg:
            return not_found("Account not found")
        elif "balance record not found" in error_msg:
            return not_found("Balance not found")

        # Generic validation error
        return not_found("Resource not found")

    except Exception as e:
        # Log the actual error for debugging
        error_msg = f"Failed to get balance: {str(e)}"
        print(error_msg)
        # Return safe generic message to client
        return internal_server_error("An error occurred while retrieving the balance")
