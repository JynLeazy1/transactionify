"""Transaction service for managing transactions."""

from typing import Dict, Any, Optional
from transactionify.tools.aws.dynamodb import (
    query_by_pk_paginated,
    get_by_full_match,
    encode_cursor,
    decode_cursor,
)


def list_transactions(
    user_id: str, account_id: str, limit: int = 20, cursor: Optional[str] = None
) -> Dict[str, Any]:
    """
    List transactions for an account with pagination support.

    This function:
    1. Validates that the account exists and belongs to the user
    2. Queries transactions for the account with pagination
    3. Returns paginated list of transactions with metadata

    Args:
        user_id: The user identifier (UUIDv7) from authorization context
        account_id: The account identifier (UUIDv7)
        limit: Number of transactions per page (default 20, max 100)
        cursor: Optional pagination cursor from previous response

    Returns:
        Dict with:
        - transactions: List of transaction data
        - next_cursor: Cursor for next page (if more results exist)
        - has_more: Boolean indicating if more results exist

    Raises:
        ValueError: If account doesn't exist, doesn't belong to user, or cursor is invalid

    Example:
        >>> result = list_transactions("019a4757-c049-7ea8-a110-2ea110c5a6f7", "019a4757-c049-7ea8-a110-2ea110c5a6f8", limit=20)
        >>> print(result)
        {
            "transactions": [
                {
                    "id": "019a4757-c049-7ea8-a110-2ea110c5a6f9",
                    "type": "payment",
                    "amount": {
                        "value": "100.00",
                        "currency": "USD"
                    },
                    "timestamp": "2024-02-22T10:00:00Z"
                }
            ],
            "has_more": true,
            "next_cursor": "eyJQSyI6IkFDQ09VTlQj..."
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

    # Decode cursor if provided
    exclusive_start_key = None
    if cursor:
        try:
            exclusive_start_key = decode_cursor(cursor)
        except ValueError as e:
            raise ValueError(f"Invalid pagination cursor: {str(e)}")

    # Query transactions with pagination
    transaction_pk = f"ACCOUNT#{account_id}"
    transaction_sk_prefix = "TRANSACTION#"

    result = query_by_pk_paginated(
        pk=transaction_pk,
        sk_prefix=transaction_sk_prefix,
        limit=limit,
        exclusive_start_key=exclusive_start_key,
    )

    # Transform transaction records to API format
    transactions = []
    for record in result["items"]:
        # Extract transaction ID from SK (format: TRANSACTION#<id>)
        sk = record.get("SK", "")
        transaction_id = (
            sk.replace("TRANSACTION#", "") if sk.startswith("TRANSACTION#") else ""
        )

        # Build transaction object
        transaction = {
            "id": transaction_id,
            "type": record.get("type", "payment"),
            "amount": {
                "value": record.get("value", "0.00"),
                "currency": record.get("currency", account_currency),
            },
            "timestamp": record.get("timestamp", ""),
        }

        transactions.append(transaction)

    # Build response with pagination metadata
    response = {
        "transactions": transactions,
        "has_more": "last_evaluated_key" in result,
    }

    # Include next cursor if there are more results
    if "last_evaluated_key" in result:
        response["next_cursor"] = encode_cursor(result["last_evaluated_key"])

    return response
