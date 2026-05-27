# Transactionify API

> To enroll a new user simply invoke lambda "transactionify-provisioning", it will provision an API Key and a balance, both attached to the new user, and it will return the API Key value.

### Create new Account
POST /api/v1/accounts
```
{
  "currency": "USD"
}
```

### Create new Payment
POST /api/v1/accounts/{account_id}/payments
```
{
  "type": "payment",
  "amount": {
    "value": "0.00",
    "currency": "USD"
  }
}
```

### Get Balance
GET /api/v1/accounts/{account_id}/balance

### List Transactions (Paginated)
GET /api/v1/accounts/{account_id}/transactions?limit=20&cursor=eyJQSyI6...

Query parameters:
- `limit`: Number of transactions per page (default: 20, max: 100)
- `cursor`: Pagination cursor from previous response

### Prerequisites
- Python 3.9+
- Node.js 18+
- AWS CDK CLI

### Setup Development Environment

1. Install production Python dependencies:
```bash
cd src/python
pip install -r requirements.txt
```

2. Install testing dependencies:
```bash
pip install -r test/unit/src/python/requirements.txt
```

3. Install Node.js dependencies:
```bash
npm install
```

### Running Tests

All tests should be run from the `test/unit/src/python/` directory:

```bash
cd test/unit/src/python
```

#### Run all tests:
```bash
pytest
```

#### Run tests with coverage:
```bash
pytest --cov=src/python/transactionify --cov-report=html --cov-report=term
```

#### Run specific test file:
```bash
pytest handlers/test_authorizer.py
pytest tools/validators/test_uuid.py
```

#### Run tests with verbose output:
```bash
pytest -v
```

#### Run tests and stop on first failure:
```bash
pytest -x
```

### Code Quality

#### Format code with black:
```bash
black src/python/
```

#### Run linter:
```bash
flake8 src/python/
```

#### Run type checker:
```bash
mypy src/python/
```

