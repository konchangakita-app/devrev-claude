---
name: devrev-pat-manager
version: 1.0.0
description: >
  Securely store, retrieve, and manage DevRev Personal Access Tokens (PATs) across
  multiple orgs. Foundational skill for all DevRev agent management with encrypted
  vault storage and secure web dashboard.
---

# PAT Manager

## Path Resolution
`SKILL_DIR` in all commands below = the **absolute path of the directory containing this SKILL.md file**.
- As the AI agent: substitute the actual filesystem path you read this file from.
- Example: if this file is at `/Users/username/.claude/skills/devrev-pat-manager/SKILL.md`, then `SKILL_DIR=/Users/username/.claude/skills/devrev-pat-manager`

## Description
Securely store, retrieve, and manage DevRev Personal Access Tokens (PATs) across multiple orgs. This is the foundational skill for all DevRev agent management — every other skill depends on this to authenticate API calls.

## When to Use
- User asks you to perform ANY action on a DevRev org (create agent, deploy, check analytics, etc.)
- User shares a PAT token (starts with `eyJ...`)
- User shares a DevRev URL and you need to identify the org + find stored credentials
- User asks to manage their stored tokens (list, remove, check expiry)

## Workflow

### Step 0: Auto-detect org from browser (Optional)
If browser context detection is available, you can automatically identify the target org.
This step is optional and can be skipped if context detection tools are not configured.

**If context detection is unavailable, proceed directly to Step 1.**

### Step 1: Determine the target org (fallback)
From the user's request, extract the org identifier. This can be:
- An org slug (e.g., `my-company`)
- A DevRev URL (e.g., `https://app.devrev.ai/my-company/trails`)
- An org display name (e.g., `My Company Inc`)

### Step 2: Check for existing PAT
```bash
python3 "${SKILL_DIR}/scripts/pat_manager.py" get "<org_identifier_or_url>"
```

The `get` command now performs:
1. **Expiry check** - Verifies token hasn't expired
2. **API validation** - Tests actual connectivity if token appears expired
3. **Warning for near-expiry** - Alerts if token expires within 7 days

Response includes:
- `found`: boolean
- `token`: the decrypted PAT (if found and valid)
- `expired`: boolean (true if token is expired)
- `error`: error message (if expired or invalid)
- `warning`: warning message (if expiring soon)

**Actions based on response:**
- If `found` = true AND `expired` = false → use the token
- If `expired` = true → inform user and go to Step 3 (get new PAT)
- If `warning` exists → inform user token is expiring soon
- If `found` = false → go to Step 3

### Step 3: Open the PAT Manager Web Dashboard (PREFERRED)
**NEVER ask users to paste PATs in chat.** Always use the secure web form:

```bash
python3 "${SKILL_DIR}/scripts/pat_entry_server.py" &
```

This opens a secure web dashboard at `http://localhost:19847` that:
- Lists all stored PATs (masked) with org names, users, and expiry
- Lets the user paste a new PAT and click **Add PAT** to validate + store
- Lets the user remove existing PATs via trash icon
- Auto-shuts down when the user closes the tab (or after 2 min timeout)
- Uses the HTML template at `${SKILL_DIR}/templates/pat-entry.html`
- Emits events to the shared event log at `~/.config/computer-events/events.jsonl`

Tell the user:
> "I've opened the PAT Manager in your browser. Paste the token and click **Add PAT**. Close the tab when you're done. You can generate a PAT at **Settings → Account → Tokens** in DevRev."

### Step 4: Detect changes after dashboard closes
After the server stops, verify what changed by diffing the vault:

```bash
# Check the event log for what happened
python3 "${SKILL_DIR}/scripts/event_log.py" --source pat_manager --json

# Always verify by checking current vault state
python3 "${SKILL_DIR}/scripts/pat_manager.py" list-masked
```

Look for:
- **`pat_added` events** → new PAT was stored
- **`pat_removed` events** → PAT was deleted
- **`window_closed` / `heartbeat_timeout`** → user closed the dashboard

**Always reflect back the org info** so the user confirms:
> "Got it! This PAT is for **Acme Corp** (`acme-corp`), authenticated as **Jane Doe** (jane@acme.com), role: **admin**. Expires **2026-09-15**. Stored securely. ✅"

### Step 4b: Direct store (FALLBACK ONLY)
Only use if the web dashboard can't be opened:
```bash
python3 "${SKILL_DIR}/scripts/pat_manager.py" store "<pat_token>"
```

### Step 5: Proceed with the action
Retrieve the token and export it for downstream scripts. **Never pass it as a CLI arg** — use the env var pattern instead:
```bash
# Capture full vault entry (includes gateway_url for non-production orgs)
VAULT_ENTRY=$(python3 "${SKILL_DIR}/scripts/pat_manager.py" get "<org>")

# Export PAT as env var — keeps it out of process listings
export DEVREV_PAT=$(echo "$VAULT_ENTRY" | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Export gateway URL so scripts hit the right environment (beta/staging/production)
export DEVREV_GATEWAY_URL=$(echo "$VAULT_ENTRY" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('gateway_url','https://app.devrev.ai/api/gateway/internal'))")
```

## Parameters

### pat_manager.py Parameters
- `<pat>` - DevRev Personal Access Token (starts with `eyJ...`)
- `<org>` - Organization identifier (slug, name, ID, or DevRev URL)
- `<url>` - DevRev URL to parse

### event_log.py Parameters
- --source - Filter events by source name (e.g., `pat_manager`, `context`)
- --tail - Tail mode: continuously watch for new events (live updates)
- --since - Show only events after the given Unix timestamp
- --last - Show only the last N events (applied after other filters)
- --clear - Clear all events from the log file
- --json - Output results in JSON format instead of human-readable text

### Error Handling Parameters
- `FileNotFoundError` - Handles missing vault or event log files (auto-creates)
- `Exception` - Handles general errors (network, API, encryption failures)
- `KeyboardInterrupt` - Handles user cancellation (Ctrl+C) with graceful cleanup

## Run Instructions

### Basic PAT Management
```bash
# Store a new PAT (validates and encrypts)
python3 "${SKILL_DIR}/scripts/pat_manager.py" store "eyJhbGciOi..."

# Retrieve a PAT for an org
python3 "${SKILL_DIR}/scripts/pat_manager.py" get "acme-corp"

# List all stored PATs
python3 "${SKILL_DIR}/scripts/pat_manager.py" list

# Show detailed info for an org
python3 "${SKILL_DIR}/scripts/pat_manager.py" info "acme-corp"

# Remove a stored PAT
python3 "${SKILL_DIR}/scripts/pat_manager.py" remove "acme-corp"

# Validate a PAT without storing
python3 "${SKILL_DIR}/scripts/pat_manager.py" validate "eyJhbGciOi..."

# Parse a DevRev URL
python3 "${SKILL_DIR}/scripts/pat_manager.py" parse-url "https://app.devrev.ai/acme-corp/trails"
```

### Web Dashboard (Recommended)
```bash
# Launch the PAT Manager web dashboard
python3 "${SKILL_DIR}/scripts/pat_entry_server.py" &

# Opens at http://localhost:19847
# Add/remove/update PATs through the UI
# Auto-shuts down when tab closes or after 2 min timeout
```

### Event Log Monitoring
```bash
# View all events
python3 "${SKILL_DIR}/scripts/event_log.py"

# Filter by source
python3 "${SKILL_DIR}/scripts/event_log.py" --source pat_manager

# Tail new events (live updates)
python3 "${SKILL_DIR}/scripts/event_log.py" --tail

# Show last N events
python3 "${SKILL_DIR}/scripts/event_log.py" --last 10

# Show events since timestamp
python3 "${SKILL_DIR}/scripts/event_log.py" --since 1709251200

# Clear the event log
python3 "${SKILL_DIR}/scripts/event_log.py" --clear

# Output as JSON
python3 "${SKILL_DIR}/scripts/event_log.py" --json
```

## Commands Reference

### pat_manager.py Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `store <pat>` | Store a new PAT | Validates → shows org/user info → encrypts and stores |
| `get <org>` | Retrieve a PAT | Fuzzy matches by slug, name, ID, or DevRev URL. Returns JSON with `token` |
| `list` | List all stored orgs | Shows org names, slugs, expiry. No tokens exposed |
| `list-masked` | List with masked tokens | Shows org details with partially masked tokens for verification |
| `validate <pat>` | Validate without storing | Quick check — shows org/user info but doesn't save |
| `info <org>` | Show org details | Full metadata for a stored org |
| `remove <org>` | Delete a stored PAT | Removes from encrypted vault |
| `parse-url <url>` | Parse a DevRev URL | Extracts org slug, environment, DON IDs |

### event_log.py Commands

| Command | Usage | Description |
|---------|-------|-------------|
| (no args) | Read all events | Displays all events from the shared event log |
| `--source <name>` | Filter by source | Show only events from specified source (e.g., `pat_manager`) |
| `--tail` | Tail new events | Live mode - blocks and shows new events as they arrive |
| `--since <timestamp>` | Events after timestamp | Show events after Unix timestamp |
| `--last <n>` | Last N events | Show only the last N events (after other filters) |
| `--clear` | Clear the log | Delete all events from the log file |
| `--json` | JSON output | Output events as JSON format |

## URL Handling
The tool accepts DevRev URLs anywhere an org identifier is expected:
- `https://app.devrev.ai/my-org/trails` → extracts `my-org`
- `https://app.devrev.ai/my-org/computer/settings/agent-studio/don%3Acore%3A...%3Aai_agent%2F77/build` → extracts `my-org` + DON IDs
- Environment detection: `app.devrev.ai` = production, `beta.devrev.ai` = beta, `staging.devrev.ai` = staging

## Security Model
- **Encryption:** AES-256-CBC via openssl
- **Key:** Machine-specific (derived from hostname + username + MAC address)
- **Vault location:** `~/.config/devrev-pat-vault/vault.json`
- **Permissions:** 700 on directory, 600 on files
- Tokens are NEVER stored in plaintext, environment variables, or config files

## Error Handling

The PAT Manager handles the following error conditions gracefully:

### FileNotFoundError
- **When**: Vault file doesn't exist yet, or event log not found
- **Handling**: Automatically creates necessary directories and files with proper permissions
- **User Impact**: Transparent - first-time users see initialization messages

### Exception (General Errors)
- **When**: Network failures, API errors, malformed JSON, encryption/decryption issues
- **Handling**: Returns JSON error format: `{"error": true, "message": "...", "code": 500}`
- **User Impact**: Clear error messages with actionable guidance

### KeyboardInterrupt (Ctrl+C)
- **When**: User cancels operation (e.g., web dashboard, tail mode)
- **Handling**: Graceful shutdown with cleanup (closes servers, saves state)
- **User Impact**: Clean exit without corrupted data or orphaned processes

### SSL/Certificate Errors
- **When**: Python 3.13+ on macOS without proper certificate setup
- **Handling**: Detailed troubleshooting guide in SKILL.md (see Troubleshooting section)
- **User Impact**: One-time setup required

### API Validation Errors
- **When**: Invalid PAT format, expired token, network issues
- **Handling**: Validates token structure before API calls, provides specific error messages
- **User Impact**: Immediate feedback on what's wrong and how to fix it

## File Structure
```
pat-manager/
├── SKILL.md                          # This file
├── scripts/
│   ├── pat_manager.py                # Core PAT vault manager (store, get, list, remove, validate)
│   ├── pat_entry_server.py           # Web dashboard server (localhost:19847)
│   └── event_log.py                  # Shared event log library (append-only JSONL)
├── templates/
│   └── pat-entry.html                # Web dashboard UI (Twenty UX design system)
├── static/
│   ├── design-tokens.css             # Twenty UX design tokens (colors, spacing, typography)
│   ├── components.css                # Twenty UX component styles
│   └── components.js                 # Twenty UX component behaviors
└── references/
    └── devrev-auth-api.md            # DevRev auth API reference
```

> **Self-contained:** All CSS/JS assets are bundled in `static/`. No external dependencies needed.

## Dependencies
- Python 3.7+
- `requests` library (`pip install requests`)
- `openssl` (pre-installed on macOS/Linux)
- No other external dependencies

## Troubleshooting

### SSL certificate errors on macOS (Python 3.13+)

**Symptom:** All HTTPS API calls from `urllib` (and sometimes `requests`) fail silently or with `SSLCertVerificationError`. The PAT store command appears to hang or returns an error like:
```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Cause:** Python 3.13 (and some 3.12 installs) on macOS does not automatically use the system certificate store. The bundled SSL context has no CA certificates, so every HTTPS request fails.

**Fix:** Link the `certifi` certificate bundle to Python's SSL directory:
```bash
# Install certifi if not already present
pip3 install certifi

# Find where certifi's CA bundle lives
python3 -c "import certifi; print(certifi.where())"

# Run the macOS certificate installer that ships with Python
# (adjust path to match your Python version)
open /Applications/Python\ 3.13/Install\ Certificates.command
```

Or, as a one-liner that works for any Python 3.x install:
```bash
pip3 install certifi && \
  /Applications/Python\ 3.*/Install\ Certificates.command 2>/dev/null || \
  python3 -c "import certifi, ssl, urllib.request; ssl._create_default_https_context = ssl.create_default_context; print('SSL OK')"
```

After running the installer, restart your terminal and retry `pat_manager.py store`.

## Examples

### Example 1: Monitor PAT Manager events in real-time
```bash
# Tail the event log to see PAT operations as they happen
python3 "${SKILL_DIR}/scripts/event_log.py" --tail --source pat_manager

# In another terminal, add a PAT via the web dashboard
python3 "${SKILL_DIR}/scripts/pat_entry_server.py"

# The first terminal will show:
# {"source": "pat_manager", "type": "server_started", "timestamp": 1709251200, ...}
# {"source": "pat_manager", "type": "pat_added", "org_slug": "acme-corp", ...}
# {"source": "pat_manager", "type": "window_closed", "timestamp": 1709251250}
```

### Example 2: View recent PAT operations
```bash
# Show last 10 events from PAT Manager
python3 "${SKILL_DIR}/scripts/event_log.py" --source pat_manager --last 10

# Show events since a specific timestamp (Unix time)
python3 "${SKILL_DIR}/scripts/event_log.py" --source pat_manager --since 1709251200

# Export all PAT Manager events as JSON
python3 "${SKILL_DIR}/scripts/event_log.py" --source pat_manager --json
```

### Example 3: User wants to create an agent on a new org
```
User: "Create a CX agent on https://app.devrev.ai/acme-corp/computer/settings/agent-studio"

Agent thinks: I need a PAT for acme-corp. Let me check the vault.
→ python3 pat_manager.py get "https://app.devrev.ai/acme-corp/..."
→ Not found.

Agent says: "I don't have credentials for acme-corp. Could you share a PAT? 
             Generate one at Settings → Account → Tokens in DevRev."

User: "eyJhbGciOiJS..."

Agent: → python3 pat_manager.py store "eyJhbGciOiJS..."
       → "This PAT is for Acme Corp (acme-corp), user: john@acme.com, role: admin. 
          Expires 2026-12-01. Stored securely. ✅"
       → Proceeds to create the agent using the stored PAT.
```

### Example 2: User works across multiple orgs
```
User: "List my stored orgs"

Agent: → python3 pat_manager.py list
       → "You have PATs for:
          1. acme-corp (Acme Corp) — expires 2026-12-01 ✅
          2. beta-testing (Beta Testing Inc) — expires 2026-03-01 ⚠️ expiring soon
          3. old-project (Old Project) — EXPIRED ❌"
```

### Example 3: User shares a PAT unprompted
```
User: "Here's my PAT for the new org: eyJhbGciOiJS..."

Agent: → python3 pat_manager.py store "eyJhbGciOiJS..."
       → Validates and reflects back org info for confirmation
       → "Stored! What would you like me to do on this org?"
```

## Version History

### v1.0.0 (2026-03-31)
**Initial Release**

Core Features:
- PAT storage with AES-256-CBC encryption (machine-specific keys)
- Secure web dashboard at localhost:19847 for PAT entry
- Event log system for tracking PAT operations (append-only JSONL)
- Auto-detection of org context from browser
- Support for multiple DevRev orgs with fuzzy matching
- Environment detection (production, beta, staging)
- SSL certificate troubleshooting for macOS Python 3.13+

Security:
- Encrypted vault storage at `~/.config/devrev-pat-vault/vault.json`
- File permissions: 700 (directory), 600 (files)
- No plaintext token storage anywhere
- Token validation via DevRev API before storage

Documentation:
- Complete SKILL.md with 6 examples
- All CLI parameters documented (8 parameters)
- Error handling documented (3 error types)
- Troubleshooting guide for common issues
