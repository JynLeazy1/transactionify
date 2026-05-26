"""Balance service for managing account balances."""

from typing import Dict, Any
from datetime import datetime, timezone
from transactionify.tools.aws.dynamodb import get_by_full_match


def get_balance(user_id: str, account_id: str) -> Dict[str, Any]:
    """
    Get the balance for an account.

    This function:
    1. Validates that the account exists and belongs to the user
    2. Retrieves the balance record from DynamoDB
    3. Returns balance with current timestamp

    Args:
        user_id: The user identifier (UUIDv7) from authorization context
        account_id: The account identifier (UUIDv7)

    Returns:
        Balance data with value, currency, and timestamp

    Raises:
        ValueError: If account doesn't exist or doesn't belong to user

    Example:
        >>> balance = get_balance("019a4757-c049-7ea8-a110-2ea110c5a6f7", "019a4757-c049-7ea8-a110-2ea110c5a6f8")
        >>> print(balance)
        {
            "balance": {
                "value": "0.00",
                "currency": "USD"
            },
            "date": "2024-02-23T12:00:00Z"
        }
    """
    # Validate that account exists and belongs to user
    account_pk = f"USER_ID#{user_id}"
    account_sk = f"ACCOUNT#{account_id}"
    account = get_by_full_match(pk=account_pk, sk=account_sk)

    if not account:
        raise ValueError("Account not found or does not belong to user")

    # Get account currency
    account_currency = account.get("currency", "")

    # Get balance record
    balance_pk = f"ACCOUNT#{account_id}"
    balance_sk = "BALANCE"
    balance_record = get_by_full_match(pk=balance_pk, sk=balance_sk)

    if not balance_record:
        raise ValueError("Balance record not found for account")

    # Get balance value
    balance_value = balance_record.get("value", "0.00")

    # Get current timestamp in ISO 8601 format
    current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return {
        "balance": {"value": balance_value, "currency": account_currency},
        "date": current_time,
    }
