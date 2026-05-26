"""Lambda handler for creating new payments."""

import json
from typing import Dict, Any
from transactionify.tools.response import (
    ok,
    bad_request,
    unauthorized,
    not_found,
    internal_server_error,
)
from transactionify.services.payment import create_payment


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Create a new payment for an account.

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
        },
        "body": "{\"type\": \"payment\", \"amount\": {\"value\": \"100.00\", \"currency\": \"USD\"}}"
    }

    Args:
        event: API Gateway event with user_id in authorizer context and account_id in path
        context: Lambda context object

    Returns:
        API Gateway response with payment details

    Example response:
        {
            "statusCode": 200,
            "body": "{\"id\": \"019a4757-c049-7ea8-a110-2ea110c5a6f9\", \"type\": \"payment\", \"amount\": {\"value\": \"100.00\", \"currency\": \"USD\"}, \"status\": \"pending\"}"
        }
    """
    print(f"Create payment event: {json.dumps(event)}")

    # Extract user_id from authorizer context
    try:
        user_id = event["requestContext"]["authorizer"]["lambda"]["user_id"]
    except (KeyError, TypeError):
        return unauthorized("Unauthorized", "AuthorizationError")

    # Extract account_id from path parameters
    try:
        account_id = event["pathParameters"]["account_id"]
    except (KeyError, TypeError):
        return bad_request("Missing account_id in path", "ValidationError")

    # Parse request body
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return bad_request("Invalid JSON in request body", "ValidationError")

    # Extract amount
    amount = body.get("amount", {})
    if not isinstance(amount, dict):
        return bad_request("Missing or invalid amount object", "ValidationError")

    amount_value = amount.get("value", "")
    amount_currency = amount.get("currency", "").upper()

    if not amount_value:
        return bad_request("Missing required field: amount.value", "ValidationError")

    if not amount_currency:
        return bad_request("Missing required field: amount.currency", "ValidationError")

    # Create payment
    try:
        payment = create_payment(user_id, account_id, amount_value, amount_currency)
        print(f"Successfully created payment for account: {account_id}")

        return ok(payment)

    except ValueError as e:
        # Validation error from service - log the actual error but return safe message
        print(f"Validation error creating payment: {str(e)}")
        error_msg = str(e).lower()

        # Check for specific error types
        if "account not found" in error_msg or "does not belong" in error_msg:
            return not_found("Account not found", "NotFoundError")
        elif "currency mismatch" in error_msg:
            return bad_request(
                "Currency does not match account currency", "ValidationError"
            )

        # Generic validation error
        return bad_request("Invalid request data", "ValidationError")

    except Exception as e:
        # Log the actual error for debugging
        error_msg = f"Failed to create payment: {str(e)}"
        print(error_msg)
        # Return safe generic message to client
        return internal_server_error(
            "An error occurred while creating the payment", "InternalError"
        )
