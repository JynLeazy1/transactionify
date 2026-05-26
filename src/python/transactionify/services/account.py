"""Account service for managing user accounts."""

from typing import Dict, Any
from transactionify.tools.aws.dynamodb import put_item, get_ttl_2_weeks
from transactionify.tools.generators.uuid import generate_uuidv7


ALLOWED_CURRENCIES = ["USD", "EUR", "GBP"]


def get_account_by_id(id: str) -> dict:
    """
    Get account by ID.

    Args:
        id: Account identifier

    Returns:
        Account data
    """
    # TODO: Implement
    pass


def create_account(user_id: str, currency: str) -> Dict[str, Any]:
    """
    Create a new account for a user.

    Creates both an account record and an initial balance record with value 0.00.

    Args:
        user_id: The user identifier (UUIDv7)
        currency: The account currency (USD, EUR, or GBP)

    Returns:
        Account data with account_id, currency, and balance

    Raises:
        ValueError: If currency is not valid

    Example:
        >>> account = create_account("019a4757-c049-7ea8-a110-2ea110c5a6f7", "USD")
        >>> print(account)
        {
            "account_id": "019a4757-c049-7ea8-a110-2ea110c5a6f8",
            "currency": "USD",
            "balance": {
                "value": "0.00",
                "currency": "USD"
            }
        }
    """
    # Validate currency
    if currency not in ALLOWED_CURRENCIES:
        raise ValueError(
            f"Invalid currency. Must be one of: {', '.join(ALLOWED_CURRENCIES)}"
        )

    # Generate account ID
    account_id = generate_uuidv7()

    # Get TTL for 2 weeks
    ttl = get_ttl_2_weeks()

    # Create account record
    put_item(
        pk=f"USER_ID#{user_id}",
        sk=f"ACCOUNT#{account_id}",
        attributes={"currency": currency, "ttl": ttl},
    )

    # Create initial balance record
    put_item(
        pk=f"ACCOUNT#{account_id}",
        sk="BALANCE",
        attributes={"value": "0.00", "ttl": ttl},
    )

    return {
        "account_id": account_id,
        "currency": currency,
        "balance": {"value": "0.00", "currency": currency},
    }
