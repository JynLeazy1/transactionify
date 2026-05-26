import os
import boto3
import base64
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Initialize DynamoDB client and table
dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("TABLE_NAME")
table = dynamodb.Table(TABLE_NAME) if TABLE_NAME else None


def get_by_full_match(pk: str, sk: str = "") -> Optional[Dict[str, Any]]:
    """
    Get an item from DynamoDB by exact PK and SK match.

    Args:
        pk: Partition key value
        sk: Sort key value (defaults to empty string)

    Returns:
        Item dict if found, None otherwise
    """
    if not table:
        raise ValueError("TABLE_NAME environment variable not set")

    try:
        response = table.get_item(Key={"PK": pk, "SK": sk})
        return response.get("Item")
    except Exception as e:
        print(f"Error getting item from DynamoDB: {str(e)}")
        raise


def put_item(pk: str, sk: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Put an item into DynamoDB.

    Args:
        pk: Partition key value
        sk: Sort key value
        attributes: Additional attributes to store

    Returns:
        Response from DynamoDB put_item operation
    """
    if not table:
        raise ValueError("TABLE_NAME environment variable not set")

    try:
        item = {"PK": pk, "SK": sk, **attributes}

        response = table.put_item(Item=item)
        return response
    except Exception as e:
        print(f"Error putting item to DynamoDB: {str(e)}")
        raise


def query_by_pk(
    pk: str, sk_prefix: Optional[str] = None, limit: Optional[int] = None
) -> list:
    """
    Query items by partition key and optional sort key prefix.

    Args:
        pk: Partition key value
        sk_prefix: Optional sort key prefix to filter results
        limit: Optional limit on number of items to return

    Returns:
        List of items matching the query
    """
    if not table:
        raise ValueError("TABLE_NAME environment variable not set")

    try:
        query_params = {"KeyConditionExpression": "PK = :pk"}

        expression_values = {":pk": pk}

        if sk_prefix:
            query_params["KeyConditionExpression"] += " AND begins_with(SK, :sk_prefix)"
            expression_values[":sk_prefix"] = sk_prefix

        query_params["ExpressionAttributeValues"] = expression_values

        if limit:
            query_params["Limit"] = limit

        response = table.query(**query_params)
        return response.get("Items", [])
    except Exception as e:
        print(f"Error querying DynamoDB: {str(e)}")
        raise


def is_expired(item: Dict[str, Any]) -> bool:
    """
    Check if an item has expired based on its TTL attribute.

    Args:
        item: DynamoDB item with optional 'ttl' attribute

    Returns:
        True if expired, False otherwise
    """
    ttl = item.get("ttl")
    if not ttl:
        return False

    current_time = int(datetime.utcnow().timestamp())
    return current_time > ttl


def get_ttl_2_weeks() -> int:
    """
    Calculate TTL timestamp for 2 weeks from now.

    Returns:
        Unix timestamp for 2 weeks from now
    """
    two_weeks = datetime.utcnow() + timedelta(weeks=2)
    return int(two_weeks.timestamp())


def query_by_pk_paginated(
    pk: str,
    sk_prefix: Optional[str] = None,
    limit: int = 20,
    exclusive_start_key: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Query items by partition key with pagination support.

    Args:
        pk: Partition key value
        sk_prefix: Optional sort key prefix to filter results
        limit: Number of items per page (default 20, max 100)
        exclusive_start_key: The key to start from for pagination

    Returns:
        Dict with 'items' and optional 'last_evaluated_key'
    """
    if not table:
        raise ValueError("TABLE_NAME environment variable not set")

    # Enforce max limit
    limit = min(limit, 100)

    try:
        query_params = {
            "KeyConditionExpression": "PK = :pk",
            "Limit": limit,
            "ScanIndexForward": False,  # Most recent first (DESC order by SK)
        }

        expression_values = {":pk": pk}

        if sk_prefix:
            query_params["KeyConditionExpression"] += " AND begins_with(SK, :sk_prefix)"
            expression_values[":sk_prefix"] = sk_prefix

        query_params["ExpressionAttributeValues"] = expression_values

        if exclusive_start_key:
            query_params["ExclusiveStartKey"] = exclusive_start_key

        response = table.query(**query_params)

        result = {"items": response.get("Items", [])}

        # Include LastEvaluatedKey if there are more results
        if "LastEvaluatedKey" in response:
            result["last_evaluated_key"] = response["LastEvaluatedKey"]

        return result
    except Exception as e:
        print(f"Error querying DynamoDB: {str(e)}")
        raise


def encode_cursor(last_evaluated_key: Dict[str, Any]) -> str:
    """
    Encode DynamoDB LastEvaluatedKey as a base64 cursor.

    Args:
        last_evaluated_key: DynamoDB LastEvaluatedKey dict

    Returns:
        Base64-encoded cursor string
    """
    json_str = json.dumps(last_evaluated_key, sort_keys=True)
    return base64.b64encode(json_str.encode()).decode()


def decode_cursor(cursor: str) -> Dict[str, Any]:
    """
    Decode a base64 cursor back to DynamoDB ExclusiveStartKey.

    Args:
        cursor: Base64-encoded cursor string

    Returns:
        DynamoDB ExclusiveStartKey dict

    Raises:
        ValueError: If cursor is invalid
    """
    try:
        json_str = base64.b64decode(cursor.encode()).decode()
        return json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Invalid cursor: {str(e)}")
