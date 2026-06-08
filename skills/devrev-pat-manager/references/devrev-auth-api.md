# DevRev Auth API Reference

## Base URL
`https://api.devrev.ai/`

## Authentication
All requests require:
```
Authorization: <PAT_TOKEN>
Content-Type: application/json
```

## Endpoints Used

### GET /dev-users.self
Returns the authenticated user's profile.

**Response:**
```json
{
  "dev_user": {
    "id": "don:identity:dvrv-us-1:devo/ORGID:devu/N",
    "display_id": "DEVU-32",
    "display_name": "Ribhu Chawla",
    "email": "ribhu.chawla@devrev.ai",
    "full_name": "Ribhu Chawla",
    "state": "active"
  }
}
```

### GET /dev-orgs.self
Returns the org the PAT belongs to.

**Response:**
```json
{
  "dev_org": {
    "id": "don:identity:dvrv-us-1:devo/ORGID",
    "display_id": "DEV-ORGID",
    "display_name": "My Company",
    "slug": "my-company",
    "tier": "enterprise",
    "created_date": "2024-01-15T..."
  }
}
```

## PAT JWT Claims
DevRev PATs are JWTs. Decoding the payload (base64) reveals:
- `exp` — expiry timestamp (Unix epoch)
- `http://devrev.ai/devoid` — org display ID
- `http://devrev.ai/devuid` — user display ID
- `http://devrev.ai/displayname` — username
- `http://devrev.ai/email` — email
- `http://devrev.ai/fullname` — full name
- `jti` — token DON ID

## DevRev URL Format
```
https://{host}/{org_slug}/{path}
```
- **host:** `app.devrev.ai` (production), `beta.devrev.ai` (beta), `staging.devrev.ai` (staging)
- **org_slug:** Always the first path segment after host
- **path:** Rest of the URL (trails, computer/settings, etc.)
- **DON IDs** may appear URL-encoded: `don%3Acore%3A...` → `don:core:...`

## DON ID Formats
- Org: `don:identity:dvrv-us-1:devo/{ORGID}`
- User: `don:identity:dvrv-us-1:devo/{ORGID}:devu/{N}`
- Agent: `don:core:dvrv-us-1:devo/{ORGID}:ai_agent/{N}`
- Service Account: `don:core:dvrv-us-1:devo/{ORGID}:service_account/{N}`
