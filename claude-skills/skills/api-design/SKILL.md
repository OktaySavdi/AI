---
name: "api-design"
description: >
  REST API design patterns covering resource naming, pagination, error responses,
  versioning, and security. Activate when designing or reviewing API endpoints.
license: MIT
metadata:
  version: 1.0.0
  author: ECC
  category: engineering
---

# API Design Skill

## Resource Naming

```
# Nouns, not verbs
GET    /users           # list users
GET    /users/{id}      # get user
POST   /users           # create user
PUT    /users/{id}      # replace user
PATCH  /users/{id}      # update user fields
DELETE /users/{id}      # delete user

# Nested resources
GET    /users/{id}/orders
GET    /users/{id}/orders/{order_id}

# Actions (when REST doesn't fit)
POST   /users/{id}/activate
POST   /payments/{id}/refund
```

## HTTP Status Codes

| Code | When to Use |
|---|---|
| 200 OK | Success with body |
| 201 Created | POST success, include `Location` header |
| 204 No Content | DELETE or PUT with no response body |
| 400 Bad Request | Invalid input (validation error) |
| 401 Unauthorized | Not authenticated |
| 403 Forbidden | Authenticated but not authorized |
| 404 Not Found | Resource does not exist |
| 409 Conflict | State conflict (duplicate, optimistic lock) |
| 422 Unprocessable Entity | Semantic validation failure |
| 429 Too Many Requests | Rate limited |
| 500 Internal Server Error | Unexpected server error |

## Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "request_id": "req_abc123"
  }
}
```

## Pagination

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8,
    "next": "/users?page=2",
    "prev": null
  }
}
```

Cursor-based (better for large datasets):
```json
{
  "data": [...],
  "cursor": {
    "next": "eyJpZCI6MTAwfQ==",
    "has_more": true
  }
}
```

## Versioning

- URL versioning: `/v1/users` (simple, visible)
- Header versioning: `Accept: application/vnd.api+json;version=1`
- Prefer URL versioning for public APIs

## Security

- Always HTTPS
- Rate limiting on all endpoints
- Auth required by default — explicit public opt-in
- Input validation before processing
- Sensitive data not in URL (use POST body or headers)
