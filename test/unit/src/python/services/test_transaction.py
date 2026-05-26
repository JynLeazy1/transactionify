"""Tests for transaction service."""

import pytest
from unittest.mock import patch
from src.python.transactionify.services.transaction import list_transactions


class TestListTransactions:
    """Test cases for list_transactions function."""

    @patch("src.python.transactionify.services.transaction.query_by_pk_paginated")
    @patch("src.python.transactionify.services.transaction.get_by_full_match")
    def test_list_transactions_success(self, mock_get_item, mock_query):
        """Test successful transaction listing."""
        mock_get_item.return_value = {
            "PK": "USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7",
            "SK": "ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8",
            "currency": "USD",
        }
        mock_query.return_value = {
            "items": [
                {
                    "PK": "ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8",
                    "SK": "TRANSACTION#019a4757-c049-7ea8-a110-2ea110c5a6f9",
                    "type": "payment",
                    "value": "100.00",
                    "currency": "USD",
                    "timestamp": "2024-02-22T10:00:00Z",
                },
                {
                    "PK": "ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8",
                    "SK": "TRANSACTION#019a4757-c049-7ea8-a110-2ea110c5a700",
                    "type": "payment",
                    "value": "50.00",
                    "currency": "USD",
                    "timestamp": "2024-02-22T11:00:00Z",
                },
            ],
        }

        result = list_transactions(
            user_id="019a4757-c049-7ea8-a110-2ea110c5a6f7",
            account_id="019a4757-c049-7ea8-a110-2ea110c5a6f8",
        )

        transactions = result["transactions"]
        assert len(transactions) == 2
        assert transactions[0]["id"] == "019a4757-c049-7ea8-a110-2ea110c5a6f9"
        assert transactions[0]["type"] == "payment"
        assert transactions[0]["amount"]["value"] == "100.00"
        assert transactions[0]["amount"]["currency"] == "USD"
        assert transactions[0]["timestamp"] == "2024-02-22T10:00:00Z"
        assert transactions[1]["id"] == "019a4757-c049-7ea8-a110-2ea110c5a700"
        assert transactions[1]["amount"]["value"] == "50.00"
        assert result["has_more"] is False
        assert "next_cursor" not in result

    @patch("src.python.transactionify.services.transaction.query_by_pk_paginated")
    @patch("src.python.transactionify.services.transaction.get_by_full_match")
    def test_list_transactions_empty(self, mock_get_item, mock_query):
        """Test transaction listing with no transactions."""
        mock_get_item.return_value = {
            "PK": "USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7",
            "SK": "ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8",
            "currency": "EUR",
        }
        mock_query.return_value = {"items": []}

        result = list_transactions(
            user_id="019a4757-c049-7ea8-a110-2ea110c5a6f7",
            account_id="019a4757-c049-7ea8-a110-2ea110c5a6f8",
        )

        assert result["transactions"] == []
        assert result["has_more"] is False

    @patch("src.python.transactionify.services.transaction.get_by_full_match")
    def test_list_transactions_account_not_found(self, mock_get_item):
        """Test error when account doesn't exist."""
        mock_get_item.return_value = None

        with pytest.raises(ValueError) as exc_info:
            list_transactions(
                user_id="019a4757-c049-7ea8-a110-2ea110c5a6f7",
                account_id="019a4757-c049-7ea8-a110-2ea110c5a6f8",
            )

        assert "Account not found" in str(exc_info.value)

    @patch("src.python.transactionify.services.transaction.get_by_full_match")
    def test_list_transactions_validates_user_ownership(self, mock_get_item):
        """Test that listing validates account belongs to user."""
        mock_get_item.return_value = None

        with pytest.raises(ValueError):
            list_transactions(
                user_id="019a4757-c049-7ea8-a110-2ea110c5a6f7",
                account_id="019a4757-c049-7ea8-a110-2ea110c5a6f8",
            )

        mock_get_item.assert_called_once_with(
            pk="USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7",
            sk="ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8",
        )

    @patch("src.python.transactionify.services.transaction.query_by_pk_paginated")
    @patch("src.python.transactionify.services.transaction.get_by_full_match")
    def test_list_transactions_uses_account_currency(self, mock_get_item, mock_query):
        """Test that transactions use account currency when missing."""
        mock_get_item.return_value = {
            "PK": "USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7",
            "SK": "ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8",
            "currency": "GBP",
        }
        mock_query.return_value = {
            "items": [
                {
                    "PK": "ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8",
                    "SK": "TRANSACTION#019a4757-c049-7ea8-a110-2ea110c5a6f9",
                    "type": "payment",
                    "value": "75.50",
                    "timestamp": "2024-02-22T10:00:00Z",
                    # No currency field — service should fall back to account currency
                }
            ],
        }

        result = list_transactions(
            user_id="019a4757-c049-7ea8-a110-2ea110c5a6f7",
            account_id="019a4757-c049-7ea8-a110-2ea110c5a6f8",
        )

        transactions = result["transactions"]
        assert len(transactions) == 1
        assert transactions[0]["amount"]["currency"] == "GBP"

    @patch("src.python.transactionify.services.transaction.query_by_pk_paginated")
    @patch("src.python.transactionify.services.transaction.get_by_full_match")
    def test_list_transactions_query_parameters(self, mock_get_item, mock_query):
        """Verify the paginated query is called with the expected kwargs."""
        mock_get_item.return_value = {
            "PK": "USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7",
            "SK": "ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8",
            "currency": "USD",
        }
        mock_query.return_value = {"items": []}

        list_transactions(
            user_id="019a4757-c049-7ea8-a110-2ea110c5a6f7",
            account_id="019a4757-c049-7ea8-a110-2ea110c5a6f8",
        )

        mock_query.assert_called_once_with(
            pk="ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8",
            sk_prefix="TRANSACTION#",
            limit=20,
            exclusive_start_key=None,
        )

    @patch("src.python.transactionify.services.transaction.query_by_pk_paginated")
    @patch("src.python.transactionify.services.transaction.get_by_full_match")
    def test_list_transactions_emits_next_cursor_when_more_results(
        self, mock_get_item, mock_query
    ):
        """When DynamoDB returns a last_evaluated_key, the service exposes next_cursor."""
        mock_get_item.return_value = {
            "PK": "USER_ID#019a4757-c049-7ea8-a110-2ea110c5a6f7",
            "SK": "ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8",
            "currency": "USD",
        }
        mock_query.return_value = {
            "items": [],
            "last_evaluated_key": {
                "PK": "ACCOUNT#019a4757-c049-7ea8-a110-2ea110c5a6f8",
                "SK": "TRANSACTION#abc",
            },
        }

        result = list_transactions(
            user_id="019a4757-c049-7ea8-a110-2ea110c5a6f7",
            account_id="019a4757-c049-7ea8-a110-2ea110c5a6f8",
        )

        assert result["has_more"] is True
        assert "next_cursor" in result
        assert isinstance(result["next_cursor"], str)
