"""Payment service for managing payments."""

from typing import Dict, Any
from datetime import datetime, timezone
from transactionify.tools.aws.dynamodb import (
    put_item,
    get_by_full_match,
    get_ttl_2_weeks,
)
from transactionify.tools.generators.uuid import generate_uuidv7


def create_payment(
    user_id: str, account_id: str, amount_value: str, amount_currency: str
) -> Dict[str, Any]:
    """
    Create a new payment for an account.

    This function:
    1. Validates that the account exists and belongs to the user
    2. Validates that the payment currency matches the account currency
    3. Creates a transaction record in DynamoDB
    4. Returns payment details with "pending" status

    Args:
        user_id: The user identifier (UUIDv7) from authorization context
        account_id: The account identifier (UUIDv7)
        amount_value: The payment amount as a string (e.g., "100.00")
        amount_currency: The payment currency (USD, EUR, or GBP)

    Returns:
        Payment data with id, type, amount, and status

    Raises:
        ValueError: If account doesn't exist, doesn't belong to user, or currency mismatch

    Example:
        >>> payment = create_payment("019a4757-c049-7ea8-a110-2ea110c5a6f7", "019a4757-c049-7ea8-a110-2ea110c5a6f8", "100.00", "USD")
        >>> print(payment)
        {
            "id": "019a4757-c049-7ea8-a110-2ea110c5a6f9",
            "type": "payment",
            "amount": {
                "value": "100.00",
                "currency": "USD"
            },
            "status": "pending"
        }
    """
    # Validate that account exists and belongs to user
    account_pk = f"USER_ID#{user_id}"
    account_sk = f"ACCOUNT#{account_id}"
    account = get_by_full_match(pk=account_pk, sk=account_sk)

    if not account:
        raise ValueError("Account not found or does not belong to user")

    # Validate currency matches account currency
    account_currency = account.get("currency", "")
    if amount_currency != account_currency:
        raise ValueError(
            f"Currency mismatch. Account currency is {account_currency}, but payment currency is {amount_currency}"
        )

    # Generate transaction ID
    transaction_id = generate_uuidv7()

    # Get TTL for 2 weeks
    ttl = get_ttl_2_weeks()

    # Get current timestamp in ISO 8601 format
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Create transaction record
    transaction_pk = f"ACCOUNT#{account_id}"
    transaction_sk = f"TRANSACTION#{transaction_id}"
    put_item(
        pk=transaction_pk,
        sk=transaction_sk,
        attributes={
            "type": "payment",
            "value": amount_value,
            "currency": amount_currency,
            "status": "pending",
            "timestamp": timestamp,
            "ttl": ttl,
        },
    )

    return {
        "id": transaction_id,
        "type": "payment",
        "amount": {"value": amount_value, "currency": amount_currency},
        "status": "pending",
    }
