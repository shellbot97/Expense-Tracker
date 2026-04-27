# API Documentation

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Authentication

Most API endpoints require authentication using JWT Bearer tokens.

### Flow

1. **Register** a new user account
2. **Login** to receive an access token
3. **Include token** in all subsequent requests

### Headers

```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

---

## Endpoints

### 1. Authentication (`/api/v1/auth`)

#### 1.1 Register User

Create a new user account.

**Endpoint**: `POST /api/v1/auth/register`

**Auth Required**: No

**Request Body**:
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**Example (curl)**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

#### 1.2 Login

Authenticate and receive JWT access token.

**Endpoint**: `POST /api/v1/auth/login`

**Auth Required**: No

**Request Body**:
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Example (curl)**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

**Token Validity**: 24 hours (configurable)

---

### 2. Categories (`/api/v1/categories`)

Manage expense and income categories.

#### 2.1 Create Category

**Endpoint**: `POST /api/v1/categories`

**Auth Required**: Yes

**Request Body**:
```json
{
  "name": "Groceries",
  "category_type": "expense",
  "description": "Food and household items",
  "parent_id": null,
  "is_active": true
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Groceries",
  "category_type": "expense",
  "description": "Food and household items",
  "parent_id": null,
  "is_active": true,
  "created_at": "2024-01-15T10:35:00",
  "updated_at": "2024-01-15T10:35:00"
}
```

**Example (curl)**:
```bash
curl -X POST http://localhost:8000/api/v1/categories \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Groceries",
    "category_type": "expense"
  }'
```

#### 2.2 List Categories

**Endpoint**: `GET /api/v1/categories`

**Auth Required**: Yes

**Query Parameters**:
- `category_type` (optional): Filter by type (`expense`, `income`, `transfer`)
- `is_active` (optional): Filter by active status (true/false)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Groceries",
    "category_type": "expense",
    "description": "Food and household items",
    "parent_id": null,
    "is_active": true,
    "created_at": "2024-01-15T10:35:00"
  },
  {
    "id": 2,
    "name": "Salary",
    "category_type": "income",
    "description": "Monthly salary",
    "parent_id": null,
    "is_active": true,
    "created_at": "2024-01-15T10:36:00"
  }
]
```

**Example (curl)**:
```bash
# All categories
curl -X GET http://localhost:8000/api/v1/categories \
  -H "Authorization: Bearer <your_token>"

# Only expenses
curl -X GET "http://localhost:8000/api/v1/categories?category_type=expense" \
  -H "Authorization: Bearer <your_token>"
```

#### 2.3 Get Category

**Endpoint**: `GET /api/v1/categories/{id}`

**Auth Required**: Yes

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Groceries",
  "category_type": "expense",
  "description": "Food and household items",
  "parent_id": null,
  "is_active": true,
  "created_at": "2024-01-15T10:35:00"
}
```

#### 2.4 Update Category

**Endpoint**: `PUT /api/v1/categories/{id}`

**Auth Required**: Yes

**Request Body**:
```json
{
  "name": "Groceries & Food",
  "description": "Updated description"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Groceries & Food",
  "description": "Updated description",
  ...
}
```

#### 2.5 Delete Category

**Endpoint**: `DELETE /api/v1/categories/{id}`

**Auth Required**: Yes

**Response** (204 No Content)

---

### 3. Sources (`/api/v1/sources`)

Manage financial sources (bank accounts, credit cards, etc.).

#### 3.1 Create Source

**Endpoint**: `POST /api/v1/sources`

**Auth Required**: Yes

**Request Body**:
```json
{
  "name": "Chase Checking",
  "source_type": "bank_account",
  "description": "Primary checking account",
  "currency": "USD",
  "is_active": true
}
```

**Source Types**:
- `bank_account`
- `credit_card`
- `cash`
- `digital_wallet`
- `investment`
- `other`

**Response** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Chase Checking",
  "source_type": "bank_account",
  "description": "Primary checking account",
  "currency": "USD",
  "is_active": true,
  "created_at": "2024-01-15T10:40:00"
}
```

#### 3.2 List Sources

**Endpoint**: `GET /api/v1/sources`

**Auth Required**: Yes

**Query Parameters**:
- `source_type` (optional): Filter by type
- `is_active` (optional): Filter by active status

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Chase Checking",
    "source_type": "bank_account",
    "currency": "USD",
    "is_active": true
  },
  {
    "id": 2,
    "name": "Visa Credit Card",
    "source_type": "credit_card",
    "currency": "USD",
    "is_active": true
  }
]
```

---

### 4. Transactions (`/api/v1/transactions`)

Manage financial transactions.

#### 4.1 Create Transaction

**Endpoint**: `POST /api/v1/transactions`

**Auth Required**: Yes

**Request Body**:
```json
{
  "source_id": 1,
  "category_id": 1,
  "transaction_date": "2024-01-15",
  "amount": 5499,
  "transaction_type": "expense",
  "description": "Whole Foods Market",
  "notes": "Weekly grocery shopping"
}
```

**Important**: Amounts are stored in cents (5499 = $54.99)

**Transaction Types**:
- `expense`: Money spent
- `income`: Money received
- `transfer`: Between accounts

**Response** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "source_id": 1,
  "category_id": 1,
  "transaction_date": "2024-01-15",
  "amount": 5499,
  "transaction_type": "expense",
  "description": "Whole Foods Market",
  "notes": "Weekly grocery shopping",
  "created_at": "2024-01-15T11:00:00"
}
```

**Example (curl)**:
```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": 1,
    "category_id": 1,
    "transaction_date": "2024-01-15",
    "amount": 5499,
    "transaction_type": "expense",
    "description": "Whole Foods Market"
  }'
```

#### 4.2 List Transactions

**Endpoint**: `GET /api/v1/transactions`

**Auth Required**: Yes

**Query Parameters**:
- `start_date` (optional): Filter from date (YYYY-MM-DD)
- `end_date` (optional): Filter to date (YYYY-MM-DD)
- `category_id` (optional): Filter by category
- `source_id` (optional): Filter by source
- `transaction_type` (optional): Filter by type
- `min_amount` (optional): Minimum amount (cents)
- `max_amount` (optional): Maximum amount (cents)
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Page size (default: 100, max: 1000)

**Response** (200 OK):
```json
{
  "transactions": [
    {
      "id": 1,
      "source_id": 1,
      "category_id": 1,
      "transaction_date": "2024-01-15",
      "amount": 5499,
      "transaction_type": "expense",
      "description": "Whole Foods Market"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Example (curl)**:
```bash
# All transactions
curl -X GET http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer <your_token>"

# Filter by date range
curl -X GET "http://localhost:8000/api/v1/transactions?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer <your_token>"

# Filter by category
curl -X GET "http://localhost:8000/api/v1/transactions?category_id=1" \
  -H "Authorization: Bearer <your_token>"

# Pagination
curl -X GET "http://localhost:8000/api/v1/transactions?skip=0&limit=50" \
  -H "Authorization: Bearer <your_token>"
```

#### 4.3 Get Transaction

**Endpoint**: `GET /api/v1/transactions/{id}`

**Auth Required**: Yes

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "source_id": 1,
  "category_id": 1,
  "transaction_date": "2024-01-15",
  "amount": 5499,
  "transaction_type": "expense",
  "description": "Whole Foods Market",
  "notes": "Weekly grocery shopping",
  "created_at": "2024-01-15T11:00:00"
}
```

#### 4.4 Update Transaction

**Endpoint**: `PUT /api/v1/transactions/{id}`

**Auth Required**: Yes

**Request Body** (all fields optional):
```json
{
  "category_id": 2,
  "amount": 5999,
  "description": "Whole Foods Market - Updated",
  "notes": "Included household items"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "category_id": 2,
  "amount": 5999,
  "description": "Whole Foods Market - Updated",
  ...
}
```

#### 4.5 Delete Transaction

**Endpoint**: `DELETE /api/v1/transactions/{id}`

**Auth Required**: Yes

**Response** (204 No Content)

---

### 5. Categorization (`/api/v1/categorization`)

Automatic transaction categorization.

#### 5.1 Categorize Transaction

**Endpoint**: `POST /api/v1/categorization/categorize`

**Auth Required**: Yes

**Request Body**:
```json
{
  "transaction_id": 1
}
```

**Response** (200 OK):
```json
{
  "transaction_id": 1,
  "suggested_category_id": 1,
  "category_name": "Groceries",
  "confidence": 0.95,
  "method": "rule_based"
}
```

**Methods**:
- `rule_based`: Using category rules
- `ai`: Using AI model (if enabled)
- `manual`: User assigned

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "Descriptive error message"
}
```

### Common Error Codes

- **400 Bad Request**: Invalid request data or validation failure
- **401 Unauthorized**: Missing or invalid authentication token
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Duplicate resource (e.g., username already exists)
- **500 Internal Server Error**: Unexpected server error

### Example Error Responses

**401 Unauthorized**:
```json
{
  "error": "Invalid or expired token"
}
```

**400 Bad Request**:
```json
{
  "error": "Validation error: password must be at least 8 characters"
}
```

**404 Not Found**:
```json
{
  "error": "Transaction not found"
}
```

---

## Complete Workflow Example

### 1. Register and Login

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"SecurePass123!"}'

# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"SecurePass123!"}' \
  | jq -r '.access_token')
```

### 2. Create Category

```bash
curl -X POST http://localhost:8000/api/v1/categories \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Groceries","category_type":"expense"}'
```

### 3. Create Source

```bash
curl -X POST http://localhost:8000/api/v1/sources \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Checking Account","source_type":"bank_account","currency":"USD"}'
```

### 4. Create Transaction

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_id":1,
    "category_id":1,
    "transaction_date":"2024-01-15",
    "amount":5499,
    "transaction_type":"expense",
    "description":"Whole Foods"
  }'
```

### 5. List Transactions

```bash
curl -X GET http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer $TOKEN"
```

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Register
response = requests.post(
    f"{BASE_URL}/api/v1/auth/register",
    json={
        "username": "john",
        "email": "john@example.com",
        "password": "SecurePass123!"
    }
)
user = response.json()
print(f"Registered user: {user['username']}")

# 2. Login
response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={
        "username": "john",
        "password": "SecurePass123!"
    }
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 3. Create category
response = requests.post(
    f"{BASE_URL}/api/v1/categories",
    headers=headers,
    json={
        "name": "Groceries",
        "category_type": "expense"
    }
)
category = response.json()

# 4. Create source
response = requests.post(
    f"{BASE_URL}/api/v1/sources",
    headers=headers,
    json={
        "name": "Checking Account",
        "source_type": "bank_account",
        "currency": "USD"
    }
)
source = response.json()

# 5. Create transaction
response = requests.post(
    f"{BASE_URL}/api/v1/transactions",
    headers=headers,
    json={
        "source_id": source["id"],
        "category_id": category["id"],
        "transaction_date": "2024-01-15",
        "amount": 5499,  # $54.99 in cents
        "transaction_type": "expense",
        "description": "Whole Foods Market"
    }
)
transaction = response.json()
print(f"Created transaction: ${transaction['amount']/100:.2f}")

# 6. List transactions
response = requests.get(
    f"{BASE_URL}/api/v1/transactions",
    headers=headers,
    params={"limit": 10}
)
data = response.json()
print(f"Total transactions: {data['total']}")
```

---

## JavaScript (Fetch) Example

```javascript
const BASE_URL = "http://localhost:8000";

// 1. Register
const registerResponse = await fetch(`${BASE_URL}/api/v1/auth/register`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "john",
    email: "john@example.com",
    password: "SecurePass123!"
  })
});
const user = await registerResponse.json();

// 2. Login
const loginResponse = await fetch(`${BASE_URL}/api/v1/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "john",
    password: "SecurePass123!"
  })
});
const { access_token } = await loginResponse.json();

// 3. Create transaction (with auth)
const transactionResponse = await fetch(`${BASE_URL}/api/v1/transactions`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${access_token}`
  },
  body: JSON.stringify({
    source_id: 1,
    category_id: 1,
    transaction_date: "2024-01-15",
    amount: 5499,
    transaction_type: "expense",
    description: "Whole Foods Market"
  })
});
const transaction = await transactionResponse.json();
console.log(`Created transaction: $${transaction.amount / 100}`);
```

---

## Testing the API

### Using Swagger UI

1. Open http://localhost:8000/docs
2. Click "Authorize" button
3. Enter Bearer token: `Bearer <your_token>`
4. Try out endpoints interactively

### Using ReDoc

1. Open http://localhost:8000/redoc
2. Browse API documentation
3. View request/response schemas
4. See error codes and examples

### Using cURL

See examples throughout this document.

### Using Postman

1. Import OpenAPI spec from http://localhost:8000/openapi.json
2. Set up environment variables (BASE_URL, TOKEN)
3. Use collection runner for automated testing

---

## Rate Limiting

Currently no rate limiting is implemented. For production deployments, consider:

- Implementing rate limiting middleware
- Using API gateways (Kong, Traefik)
- Caching frequently accessed data

---

## Best Practices

### 1. Token Management
- Store tokens securely (HTTP-only cookies or secure storage)
- Refresh tokens before expiry (24 hours)
- Implement token refresh endpoint if needed

### 2. Error Handling
- Always check response status codes
- Parse error messages from response body
- Implement retry logic for 5xx errors

### 3. Pagination
- Use `skip` and `limit` parameters for large datasets
- Default limit is 100, maximum is 1000
- Implement infinite scroll or pagination in UI

### 4. Date Handling
- Use ISO 8601 format (YYYY-MM-DD)
- Store dates in UTC
- Convert to user's timezone in client

### 5. Amount Handling
- Always store amounts in cents (integer)
- Convert to dollars for display ($54.99 = 5499 cents)
- Avoid floating-point arithmetic

---

## Versioning

Current API version: **v1**

API version is included in URL path: `/api/v1/...`

Future versions will use:
- `/api/v2/...` for breaking changes
- Deprecation notices for removed endpoints
- Migration guides for version upgrades

---

## Support

For issues or questions:
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health
- GitHub: [repository-url]

---

**Last Updated**: 2026-04-26  
**API Version**: 0.1.0
