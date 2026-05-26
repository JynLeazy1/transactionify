"""HTTP response utilities for API Gateway Lambda handlers."""

import json
from typing import Dict, Any, Optional


def ok(body: Dict[str, Any]) -> Dict:
    """
    Create a successful HTTP response.

    Args:
        body: The response body (will be JSON serialized)
        status_code: HTTP status code (default: 200)

    Returns:
        API Gateway Lambda response format

    Example:
        >>> ok({'message': 'Success'})
        {'statusCode': 200, 'body': '{"message": "Success"}'}
    """
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }


def bad_request(message: str, error_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a 400 Bad Request response.

    Args:
        message: Error message
        error_type: Optional error type/category (deprecated, not used in response)

    Returns:
        API Gateway Lambda response format

    Example:
        >>> bad_request('Invalid input')
        {'statusCode': 400, 'body': '{"message": "Invalid input"}'}
    """
    body = {"message": message}

    return {
        "statusCode": 400,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }


def unauthorized(message: str, error_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a 401 Unauthorized response.

    Args:
        message: Error message
        error_type: Optional error type/category (deprecated, not used in response)

    Returns:
        API Gateway Lambda response format
    """
    body = {"message": message}

    return {
        "statusCode": 401,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }


def not_found(message: str, error_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a 404 Not Found response.

    Args:
        message: Error message
        error_type: Optional error type/category (deprecated, not used in response)

    Returns:
        API Gateway Lambda response format
    """
    body = {"message": message}

    return {
        "statusCode": 404,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }


def internal_server_error(
    message: str, error_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a 500 Internal Server Error response.

    Args:
        message: Error message
        error_type: Optional error type/category (deprecated, not used in response)

    Returns:
        API Gateway Lambda response format
    """
    body = {"message": message}

    return {
        "statusCode": 500,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }
