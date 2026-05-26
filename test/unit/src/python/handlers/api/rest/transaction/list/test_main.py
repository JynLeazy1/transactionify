"""Tests for list transactions Lambda handler."""

import json
from unittest.mock import patch

from src.python.transactionify.handlers.api.rest.transaction.list.main import handler


HANDLER_LIST_TX = (
    "src.python.transactionify.handlers.api.rest.transaction.list.main.list_transactions"
)


class TestListTransactionsHandler:
    """Test cases for the list transactions Lambda handler."""

    @patch(HANDLER_LIST_TX)
    def test_handler_success(self, mock_list_transactions):
        """Successful listing returns the paginated dict from the service."""
        mock_list_transactions.return_value = {
            "transactions": [
                {
                    "id": "019a4757-c049-7ea8-a110-2ea110c5a6f9",
                    "type": "payment",
                    "amount": {"value": "100.00", "currency": "USD"},
                    "timestamp": "2024-02-22T10:00:00Z",
                },
                {
                    "id": "019a4757-c049-7ea8-a110-2ea110c5a700",
                    "type": "payment",
                    "amount": {"value": "50.00", "currency": "USD"},
                    "timestamp": "2024-02-22T11:00:00Z",
                },
            ],
            "has_more": False,
        }

        event = {
            "requestContext": {
                "authorizer": {"lambda": {"user_id": "019a4757-c049-7ea8-a110-2ea110c5a6f7"}}
            },
            "pathParameters": {"account_id": "019a4757-c049-7ea8-a110-2ea110c5a6f8"},
        }

        response = handler(event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert len(body["transactions"]) == 2
        assert body["transactions"][0]["id"] == "019a4757-c049-7ea8-a110-2ea110c5a6f9"
        assert body["transactions"][0]["amount"]["value"] == "100.00"
        assert body["has_more"] is False
        mock_list_transactions.assert_called_once_with(
            "019a4757-c049-7ea8-a110-2ea110c5a6f7",
            "019a4757-c049-7ea8-a110-2ea110c5a6f8",
            limit=20,
            cursor=None,
        )

    @patch(HANDLER_LIST_TX)
    def test_handler_empty_list(self, mock_list_transactions):
        """Empty result returns 200 with empty transactions array."""
        mock_list_transactions.return_value = {"transactions": [], "has_more": False}

        event = {
            "requestContext": {
                "authorizer": {"lambda": {"user_id": "019a4757-c049-7ea8-a110-2ea110c5a6f7"}}
            },
            "pathParameters": {"account_id": "019a4757-c049-7ea8-a110-2ea110c5a6f8"},
        }

        response = handler(event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["transactions"] == []
        assert body["has_more"] is False

    def test_handler_missing_user_id(self):
        """Missing user_id in authorizer → 401."""
        event = {
            "requestContext": {"authorizer": {"lambda": {}}},
            "pathParameters": {"account_id": "019a4757-c049-7ea8-a110-2ea110c5a6f8"},
        }

        response = handler(event, None)

        assert response["statusCode"] == 401
        body = json.loads(response["body"])
        assert body["message"] == "Unauthorized"

    def test_handler_missing_account_id(self):
        """Missing account_id in path → 404."""
        event = {
            "requestContext": {
                "authorizer": {"lambda": {"user_id": "019a4757-c049-7ea8-a110-2ea110c5a6f7"}}
            },
            "pathParameters": {},
        }

        response = handler(event, None)

        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert body["message"] == "Account not found"

    @patch(HANDLER_LIST_TX)
    def test_handler_account_not_found(self, mock_list_transactions):
        """Service raising 'Account not found' → 404."""
        mock_list_transactions.side_effect = ValueError(
            "Account not found or does not belong to user"
        )

        event = {
            "requestContext": {
                "authorizer": {"lambda": {"user_id": "019a4757-c049-7ea8-a110-2ea110c5a6f7"}}
            },
            "pathParameters": {"account_id": "019a4757-c049-7ea8-a110-2ea110c5a6f8"},
        }

        response = handler(event, None)

        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert body["message"] == "Account not found"

    @patch(HANDLER_LIST_TX)
    def test_handler_internal_error(self, mock_list_transactions):
        """Unexpected exception → 500 with generic message."""
        mock_list_transactions.side_effect = Exception("DynamoDB error")

        event = {
            "requestContext": {
                "authorizer": {"lambda": {"user_id": "019a4757-c049-7ea8-a110-2ea110c5a6f7"}}
            },
            "pathParameters": {"account_id": "019a4757-c049-7ea8-a110-2ea110c5a6f8"},
        }

        response = handler(event, None)

        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert body["message"] == "An error occurred while retrieving transactions"

    @patch(HANDLER_LIST_TX)
    def test_handler_does_not_expose_internal_errors(self, mock_list_transactions):
        """Internal error details are not leaked to the client."""
        mock_list_transactions.side_effect = Exception(
            "Database connection failed: host=internal-db.company.com"
        )

        event = {
            "requestContext": {
                "authorizer": {"lambda": {"user_id": "019a4757-c049-7ea8-a110-2ea110c5a6f7"}}
            },
            "pathParameters": {"account_id": "019a4757-c049-7ea8-a110-2ea110c5a6f8"},
        }

        response = handler(event, None)

        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert body["message"] == "An error occurred while retrieving transactions"
        assert "Database connection" not in body["message"]
        assert "internal-db.company.com" not in body["message"]
