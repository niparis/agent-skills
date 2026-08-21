# API Reference

**Base URL:** `https://api.example.com/v1`  
**Authentication:** Bearer token  
**Last Verified:** [Date]

## When to use
- [Primary use cases]

## When not to use
- [Constraints or alternative paths]

## Endpoints

### `POST /auth/login`
**Purpose:** Authenticate user

**Request Body:**
```json
{ "email": "", "password": "" }
```

**Responses:**
- `200 OK`
- `401 Unauthorized`

**Rate Limiting:** [If known]

**Example:**
```bash
curl -X POST ...
```

## Error Codes
| Code | Meaning |
|------|--------|
| 400 | Bad request |
| 401 | Unauthorized |
| 500 | Server error |

## Evidence Sources
- [ ] Code
- [ ] API spec
- [ ] Runtime observation

## Unknown / Unverified
- [ ] Rate limits
- [ ] Edge cases
