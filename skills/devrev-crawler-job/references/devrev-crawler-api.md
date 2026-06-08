# DevRev Web Crawler Jobs API Reference

## Base URL
`https://app.devrev.ai/api/gateway/internal/`

## Authentication
All requests require:
```
Authorization: <PAT_TOKEN>
Content-Type: application/json
```

## Endpoints

### 1. web-crawler-jobs.list
List all crawler jobs with pagination.

**Request:**
```
GET /web-crawler-jobs.list?limit=50&cursor=<cursor>
```

**Parameters:**
- `limit` (optional): Number of items per page (default: 50, max: 100)
- `cursor` (optional): Pagination cursor from previous response

**Response:**
```json
{
  "web_crawler_jobs": [
    {
      "id": "don:core:dvrv-us-1:devo/123:web_crawler_job/456",
      "display_id": "WCJ-1",
      "urls": [
        "https://docs.example.com/",
        "https://help.example.com/"
      ],
      "applies_to_parts": [
        "don:core:dvrv-us-1:devo/123:product/1"
      ],
      "frequency": 0,
      "max_depth": 4,
      "state": "active",
      "created_date": "2026-06-08T10:00:00Z",
      "modified_date": "2026-06-08T10:00:00Z",
      "description": "公式ドキュメント"
    }
  ],
  "next_cursor": "eyJvcmRlcl9ieV9maWVsZCI..."
}
```

**States:**
- `active` - Job is running
- `paused` - Job is temporarily paused
- `completed` - Job finished successfully
- `aborted` - Job was manually aborted
- `failed` - Job failed with error

---

### 2. web-crawler-jobs.create
Create a new crawler job.

**Request:**
```
POST /web-crawler-jobs.create
Content-Type: application/json

{
  "urls": [
    "https://docs.example.com/",
    "https://help.example.com/"
  ],
  "applies_to_parts": [
    "don:core:dvrv-us-1:devo/123:product/1"
  ],
  "frequency": 0,
  "max_depth": 4,
  "description": "公式ドキュメント"
}
```

**Parameters:**
- `urls` (required): Array of URLs to crawl (max 50)
- `applies_to_parts` (required): Array of part IDs (internal IDs, not display_ids)
- `frequency` (optional): Crawl frequency
  - `0` - Run once only (default)
  - `1` - Daily
  - `2-12` - Every N days
- `max_depth` (optional): Crawl depth (1-10, default: 4)
- `description` (optional): Job description

**Response:**
```json
{
  "web_crawler_job": {
    "id": "don:core:dvrv-us-1:devo/123:web_crawler_job/456",
    "display_id": "WCJ-1",
    "urls": ["https://docs.example.com/"],
    "frequency": 0,
    "max_depth": 4,
    "state": "active",
    "created_date": "2026-06-08T10:00:00Z"
  }
}
```

---

### 3. web-crawler-jobs.control
Control job execution (pause/resume/abort).

**Request:**
```
POST /web-crawler-jobs.control
Content-Type: application/json

{
  "id": "WCJ-1",
  "action": "pause"
}
```

**Parameters:**
- `id` (required): Job ID or display_id
- `action` (required): Action to perform
  - `pause` - Temporarily pause the job
  - `resume` - Resume a paused job
  - `abort` - Permanently stop the job

**Response:**
```json
{
  "web_crawler_job": {
    "id": "don:core:dvrv-us-1:devo/123:web_crawler_job/456",
    "display_id": "WCJ-1",
    "state": "paused",
    "modified_date": "2026-06-08T11:00:00Z"
  }
}
```

---

### 4. parts.list
List all parts (used to resolve display_id → internal ID).

**Request:**
```
GET /parts.list?limit=100
```

**Response:**
```json
{
  "parts": [
    {
      "id": "don:core:dvrv-us-1:devo/123:product/1",
      "display_id": "PROD-1",
      "name": "My Product",
      "type": "product"
    }
  ]
}
```

---

## Frequency Values

| Value | Meaning |
|-------|---------|
| 0 | Run once only (default) |
| 1 | Daily |
| 2 | Every 2 days |
| 3 | Every 3 days |
| 7 | Weekly |
| 14 | Bi-weekly |
| 30 | Monthly (approximately) |

Maximum: 12 days

---

## State Transitions

```
      create
        ↓
    [active]
        ↓
   ┌────┴────┐
   │         │
 pause     abort
   │         │
   ↓         ↓
[paused]  [aborted]
   │
 resume
   │
   ↓
[active]
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": {
    "message": "Invalid frequency value",
    "code": "INVALID_PARAMETER"
  }
}
```

### 401 Unauthorized
```json
{
  "error": {
    "message": "Invalid or expired token",
    "code": "UNAUTHORIZED"
  }
}
```

### 404 Not Found
```json
{
  "error": {
    "message": "Job not found",
    "code": "NOT_FOUND"
  }
}
```

### 429 Too Many Requests
```json
{
  "error": {
    "message": "Rate limit exceeded",
    "code": "RATE_LIMIT"
  }
}
```

---

## Best Practices

1. **Pagination**: Always use `next_cursor` for listing jobs (don't rely on fixed page numbers)
2. **Part ID Resolution**: Always resolve display_id → internal ID using `parts.list`
3. **URL Limits**: Maximum 50 URLs per job
4. **Depth Limits**: Keep `max_depth` ≤ 5 for large sites to avoid performance issues
5. **Frequency**: Use `frequency=0` for one-time imports, `frequency≥1` for ongoing sync
6. **State Checking**: Always check job state before performing control actions
7. **Error Handling**: Implement exponential backoff for rate limit errors (429)

---

## Common Patterns

### Pattern 1: One-time doc import
```json
{
  "urls": ["https://docs.example.com/"],
  "applies_to_parts": ["don:core:..."],
  "frequency": 0,
  "max_depth": 4
}
```

### Pattern 2: Daily sync for docs site
```json
{
  "urls": ["https://docs.example.com/"],
  "applies_to_parts": ["don:core:..."],
  "frequency": 1,
  "max_depth": 3,
  "description": "Daily documentation sync"
}
```

### Pattern 3: Multi-site crawl
```json
{
  "urls": [
    "https://docs.example.com/",
    "https://help.example.com/",
    "https://support.example.com/"
  ],
  "applies_to_parts": ["don:core:..."],
  "frequency": 7,
  "max_depth": 4,
  "description": "Weekly multi-site sync"
}
```

---

## Rate Limits

- **List**: 100 requests/minute
- **Create**: 10 requests/minute
- **Control**: 50 requests/minute

Exceeded limits return 429 with `Retry-After` header.
