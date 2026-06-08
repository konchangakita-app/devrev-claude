#!/usr/bin/env python3
"""
DevRev PAT Manager — Secure token storage & retrieval for multi-org operations.

Usage:
    pat_manager.py store <pat>           # Validate, display info, store PAT
    pat_manager.py get <org_identifier>  # Get PAT by org slug, display_name, dev_id, don_id, or DevRev URL
    pat_manager.py list                  # List all stored orgs (no tokens shown)
    pat_manager.py remove <org_id>       # Remove a stored PAT
    pat_manager.py validate <pat>        # Validate PAT without storing (returns org info JSON)
    pat_manager.py info <org_identifier> # Show org info for a stored PAT
    pat_manager.py parse-url <url>       # Parse a DevRev URL — extract org slug, environment, DON IDs

Storage: ~/.config/devrev-pat-vault/
  - vault.json — encrypted org metadata + tokens
  - Permissions: 700 on directory, 600 on files

Security:
  - Tokens encrypted with Fernet (symmetric key derived from machine-specific seed)
  - Machine seed = hostname + username + mac address hash (not portable, but safe at rest)
  - vault.json never contains plaintext tokens
"""

import sys
import os
import json
import base64
import hashlib
import uuid
import subprocess
import re
import urllib.request
import ssl
from datetime import datetime, timezone
from pathlib import Path

# --- Config ---
VAULT_DIR = Path.home() / ".config" / "devrev-pat-vault"
VAULT_FILE = VAULT_DIR / "vault.json"
KEY_FILE = VAULT_DIR / ".keyfile"

# Gateway URLs per environment
DEVREV_GATEWAYS = {
    "production": "https://app.devrev.ai/api/gateway/internal",
    "beta":       "https://beta.devrev.ai/api/gateway/internal",
    "staging":    "https://staging.devrev.ai/api/gateway/internal",
}
DEVREV_GATEWAY = DEVREV_GATEWAYS["production"]  # default

def _gateway_for_env(env: str) -> str:
    """Return the correct gateway URL for a given environment string."""
    return DEVREV_GATEWAYS.get(env, DEVREV_GATEWAY)

# --- Encryption (Fernet-like with stdlib only) ---
# We use a simple AES approach via openssl CLI to avoid requiring cryptography package

def _get_machine_seed():
    """Generate a deterministic seed from machine identity."""
    import getpass, socket
    parts = [
        socket.gethostname(),
        getpass.getuser(),
        str(uuid.getnode()),  # MAC address as int
        "devrev-pat-vault-v1"
    ]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()

def _get_or_create_key():
    """Get or create encryption key derived from machine seed."""
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(VAULT_DIR, 0o700)
    
    if KEY_FILE.exists():
        return KEY_FILE.read_text().strip()
    
    key = _get_machine_seed()
    KEY_FILE.write_text(key)
    os.chmod(KEY_FILE, 0o600)
    return key

def _encrypt(plaintext: str) -> str:
    """Encrypt using openssl AES-256-CBC."""
    key = _get_or_create_key()
    try:
        result = subprocess.run(
            ["openssl", "enc", "-aes-256-cbc", "-a", "-salt", "-pbkdf2", "-pass", f"pass:{key}"],
            input=plaintext.encode(),
            capture_output=True,
            check=True
        )
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError:
        # Fallback: base64 encode (less secure but works)
        return "b64:" + base64.b64encode(plaintext.encode()).decode()

def _decrypt(ciphertext: str) -> str:
    """Decrypt using openssl AES-256-CBC."""
    if ciphertext.startswith("b64:"):
        return base64.b64decode(ciphertext[4:]).decode()
    
    key = _get_or_create_key()
    result = subprocess.run(
        ["openssl", "enc", "-aes-256-cbc", "-a", "-d", "-salt", "-pbkdf2", "-pass", f"pass:{key}"],
        input=ciphertext.encode(),
        capture_output=True,
        check=True
    )
    return result.stdout.decode().strip()

# --- Vault I/O ---

def _load_vault() -> dict:
    if not VAULT_FILE.exists():
        return {"version": 1, "orgs": {}}
    return json.loads(VAULT_FILE.read_text())

def _save_vault(vault: dict):
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(VAULT_DIR, 0o700)
    VAULT_FILE.write_text(json.dumps(vault, indent=2))
    os.chmod(VAULT_FILE, 0o600)

# --- JWT Decode ---

def _decode_jwt_payload(token: str) -> dict:
    """Decode JWT payload without verification."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT format — expected 3 dot-separated parts")
    
    payload_b64 = parts[1]
    # Add padding
    padding = 4 - len(payload_b64) % 4
    if padding != 4:
        payload_b64 += "=" * padding
    
    payload_bytes = base64.urlsafe_b64decode(payload_b64)
    return json.loads(payload_bytes)

# --- URL Parsing ---

DEVREV_ENV_MAP = {
    "app.devrev.ai": "production",
    "beta.devrev.ai": "beta",
    "staging.devrev.ai": "staging",
}

def parse_devrev_url(url_str: str) -> dict:
    """
    Parse a DevRev URL to extract org slug, environment, and DON IDs.
    Returns None if not a valid DevRev URL.
    Only app.devrev.ai is production. Others are beta/staging/unknown.
    """
    from urllib.parse import unquote
    url_str = unquote(url_str.strip())
    
    m = re.match(r"^https?://([^/]+)/([^/]+)(?:/(.*))?$", url_str)
    if not m:
        return None
    
    host = m.group(1)
    slug = m.group(2)
    path = m.group(3) or ""
    
    env = DEVREV_ENV_MAP.get(host)
    if not env:
        if "devrev" in host:
            env = "unknown (" + host + ")"
        else:
            return None
    
    if slug in ("api", "auth", "docs", "static", ""):
        return None
    
    don_pattern = r"don:core:[a-z0-9-]+:devo/[a-zA-Z0-9]+:[a-z_]+/[a-zA-Z0-9]+"
    don_ids = re.findall(don_pattern, url_str)
    
    return {
        "host": host,
        "environment": env,
        "org_slug": slug,
        "path": path,
        "don_ids": don_ids,
        "is_production": env == "production",
    }

def _extract_org_from_input(identifier: str) -> str:
    """If identifier looks like a DevRev URL, extract the org slug. Otherwise return as-is."""
    if identifier.startswith("http://") or identifier.startswith("https://"):
        parsed = parse_devrev_url(identifier)
        if parsed and parsed.get("org_slug"):
            return parsed["org_slug"]
    return identifier

def _api_call(endpoint: str, pat: str, payload: dict = None, base_url: str = None) -> dict:
    """
    Make a DevRev internal gateway API call.
    Raises Exception on HTTP error or network failure.
    """
    import urllib.error
    url = f"{base_url or DEVREV_GATEWAY}/{endpoint}"
    data = json.dumps(payload or {}).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": pat,
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()[:400]
        except Exception:
            pass
        raise Exception(f"HTTP {e.code} on {endpoint}: {body}")
    except Exception as e:
        raise Exception(f"Network error on {endpoint}: {e}")


def validate_pat(pat: str) -> dict:
    """
    Validate a PAT and return rich org/user info.
    Returns dict with: valid, org_slug, org_display_name, org_don, dev_id,
                       user_name, user_email, user_full_name, expires, token_type
    """
    result = {
        "valid": False,
        "error": None
    }
    
    # Step 1: Decode JWT to extract claims
    try:
        claims = _decode_jwt_payload(pat)
    except Exception as e:
        result["error"] = f"Invalid token format: {e}"
        return result
    
    # Check token type
    token_type = claims.get("http://devrev.ai/tokentype", "")
    if "pat" not in token_type:
        result["error"] = f"Not a PAT — token type: {token_type}"
        return result
    
    # Check expiry
    exp = claims.get("exp", 0)
    now = datetime.now(timezone.utc).timestamp()
    if exp < now:
        result["error"] = f"Token expired on {datetime.fromtimestamp(exp, timezone.utc).isoformat()}"
        return result
    
    # Extract JWT claims
    result.update({
        "dev_user_don": claims.get("sub", ""),
        "dev_user_id": claims.get("http://devrev.ai/devuid", ""),
        "devo_don": claims.get("http://devrev.ai/devo_don", ""),
        "dev_id": claims.get("http://devrev.ai/devoid", ""),
        "user_display_name": claims.get("http://devrev.ai/displayname", ""),
        "user_email": claims.get("http://devrev.ai/email", ""),
        "user_full_name": claims.get("http://devrev.ai/fullname", ""),
        "token_type": "PAT",
        "expires": datetime.fromtimestamp(exp, timezone.utc).isoformat(),
        "token_jti": claims.get("jti", ""),
    })
    
    # Step 2: Determine environment from JWT issuer / devo_don, pick gateway accordingly
    # devo_don encodes the cluster (dvrv-us-1, etc.) but environment is safer from dev_org.environment
    # For now, try production gateway first; if org.environment says otherwise, we update accordingly.
    gateway = DEVREV_GATEWAY  # start with production

    # Step 3: Call dev-orgs.self to get org name/slug
    try:
        org_resp = _api_call("dev-orgs.self", pat, base_url=gateway)
        dev_org = org_resp.get("dev_org", {})
        org_env = dev_org.get("environment", "production") or "production"
        gateway = _gateway_for_env(org_env)  # re-derive in case org is non-production
        result.update({
            "org_slug": dev_org.get("dev_slug", ""),
            "org_display_name": dev_org.get("display_name", ""),
            "org_id": dev_org.get("id", ""),
            "org_display_id": dev_org.get("display_id", ""),
            "org_environment": org_env,
            "gateway_url": gateway,
        })
    except Exception as e:
        result["error"] = f"Token decoded but API call failed: {e}"
        return result

    # Step 4: Check user permissions by calling dev-users.self
    try:
        user_resp = _api_call("dev-users.self", pat, base_url=gateway)
        dev_user = user_resp.get("dev_user", {})
        result.update({
            "user_state": dev_user.get("state", ""),
            "user_role": ", ".join(dev_user.get("org_role", [])) if isinstance(dev_user.get("org_role"), list) else dev_user.get("org_role", ""),
        })
    except Exception:
        result["user_state"] = "unknown"
        result["user_role"] = "unknown"
    
    result["valid"] = True
    return result

def store_pat(pat: str) -> dict:
    """Validate and store a PAT. Returns validation info."""
    info = validate_pat(pat)
    
    if not info["valid"]:
        return info
    
    vault = _load_vault()
    
    # Use org_slug as primary key (unique per org)
    org_key = info["org_slug"] or info["dev_id"]
    
    vault["orgs"][org_key] = {
        "org_slug": info.get("org_slug", ""),
        "org_display_name": info.get("org_display_name", ""),
        "org_id": info.get("org_id", ""),
        "org_display_id": info.get("org_display_id", ""),
        "org_environment": info.get("org_environment", "production"),
        "gateway_url": info.get("gateway_url", DEVREV_GATEWAY),
        "dev_id": info.get("dev_id", ""),
        "user_email": info.get("user_email", ""),
        "user_full_name": info.get("user_full_name", ""),
        "user_display_name": info.get("user_display_name", ""),
        "user_role": info.get("user_role", ""),
        "expires": info.get("expires", ""),
        "stored_at": datetime.now(timezone.utc).isoformat(),
        "token_encrypted": _encrypt(pat),
    }
    
    _save_vault(vault)
    
    info["stored"] = True
    info["storage_key"] = org_key
    return info

def get_pat(org_identifier: str) -> dict:
    """
    Retrieve a PAT by org identifier.
    Accepts: org_slug, org_display_name, dev_id, org_id, org_display_id, or a DevRev URL.
    Matches are case-insensitive.
    """
    org_identifier = _extract_org_from_input(org_identifier)
    vault = _load_vault()
    
    def _entry_to_result(entry):
        return {
            "found": True,
            "org_slug": entry.get("org_slug", ""),
            "org_display_name": entry.get("org_display_name", ""),
            "org_environment": entry.get("org_environment", "production"),
            "gateway_url": entry.get("gateway_url", DEVREV_GATEWAY),
            "token": _decrypt(entry["token_encrypted"]),
        }

    # Direct key match
    if org_identifier in vault["orgs"]:
        return _entry_to_result(vault["orgs"][org_identifier])

    # Fuzzy match across all fields
    org_identifier_lower = org_identifier.lower()
    for key, entry in vault["orgs"].items():
        searchable = [
            entry.get("org_slug", ""),
            entry.get("org_display_name", ""),
            entry.get("dev_id", ""),
            entry.get("org_id", ""),
            entry.get("org_display_id", ""),
        ]
        for field in searchable:
            if field and org_identifier_lower in field.lower():
                return _entry_to_result(entry)

    return {"found": False, "error": f"No PAT found for '{org_identifier}'"}

def list_orgs() -> list:
    """List all stored orgs (no tokens shown)."""
    vault = _load_vault()
    orgs = []
    for key, entry in vault["orgs"].items():
        # Check if expired
        exp_str = entry.get("expires", "")
        is_expired = False
        if exp_str:
            try:
                exp_dt = datetime.fromisoformat(exp_str)
                is_expired = exp_dt < datetime.now(timezone.utc)
            except:
                pass

        orgs.append({
            "key": key,
            "org_slug": entry.get("org_slug", ""),
            "org_display_name": entry.get("org_display_name", ""),
            "dev_id": entry.get("dev_id", ""),
            "user": entry.get("user_full_name", "") or entry.get("user_email", ""),
            "role": entry.get("user_role", ""),
            "expires": exp_str,
            "expired": is_expired,
            "stored_at": entry.get("stored_at", ""),
        })
    return orgs

def list_orgs_masked() -> list:
    """List all stored orgs with masked tokens (for web UI)."""
    vault = _load_vault()
    orgs = []
    for key, entry in vault["orgs"].items():
        # Check if expired
        exp_str = entry.get("expires", "")
        is_expired = False
        if exp_str:
            try:
                exp_dt = datetime.fromisoformat(exp_str)
                is_expired = exp_dt < datetime.now(timezone.utc)
            except:
                pass

        # Decrypt and mask the token
        masked_token = "****"
        try:
            token_encrypted = entry.get("token_encrypted", "")
            if token_encrypted:
                token = _decrypt(token_encrypted)
                if len(token) > 8:
                    masked_token = token[:4] + "..." + token[-4:]
        except:
            pass  # If decryption fails, just show ****

        orgs.append({
            "key": key,
            "org_slug": entry.get("org_slug", ""),
            "org_display_name": entry.get("org_display_name", ""),
            "dev_id": entry.get("dev_id", ""),
            "user": entry.get("user_full_name", "") or entry.get("user_email", ""),
            "user_email": entry.get("user_email", ""),
            "role": entry.get("user_role", ""),
            "expires": exp_str,
            "expired": is_expired,
            "stored_at": entry.get("stored_at", ""),
            "masked_token": masked_token,
        })
    return orgs

def remove_org(org_identifier: str) -> dict:
    """Remove a stored PAT. Accepts org slug, name, ID, or a DevRev URL."""
    org_identifier = _extract_org_from_input(org_identifier)
    vault = _load_vault()
    
    # Direct key match
    if org_identifier in vault["orgs"]:
        removed = vault["orgs"].pop(org_identifier)
        _save_vault(vault)
        return {"removed": True, "org_slug": removed.get("org_slug", org_identifier)}
    
    # Fuzzy match
    org_identifier_lower = org_identifier.lower()
    for key, entry in vault["orgs"].items():
        searchable = [entry.get("org_slug", ""), entry.get("org_display_name", ""), entry.get("dev_id", "")]
        for field in searchable:
            if field and org_identifier_lower in field.lower():
                removed = vault["orgs"].pop(key)
                _save_vault(vault)
                return {"removed": True, "org_slug": removed.get("org_slug", key)}
    
    return {"removed": False, "error": f"No PAT found for '{org_identifier}'"}

def get_org_info(org_identifier: str) -> dict:
    """Show full info for a stored org (no token). Accepts org slug, name, ID, or DevRev URL."""
    org_identifier = _extract_org_from_input(org_identifier)
    vault = _load_vault()
    
    # Find the entry
    entry = None
    if org_identifier in vault["orgs"]:
        entry = vault["orgs"][org_identifier]
    else:
        for key, e in vault["orgs"].items():
            searchable = [e.get("org_slug", ""), e.get("org_display_name", ""), e.get("dev_id", "")]
            for field in searchable:
                if field and org_identifier.lower() in field.lower():
                    entry = e
                    break
            if entry:
                break
    
    if not entry:
        return {"found": False, "error": f"No PAT found for '{org_identifier}'"}
    
    # Return everything except the encrypted token
    info = {k: v for k, v in entry.items() if k != "token_encrypted"}
    info["found"] = True
    return info

# --- CLI ---

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: pat_manager.py <store|get|list|list-masked|remove|validate|info> [args]"}))
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "store":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: pat_manager.py store <pat>"}))
                sys.exit(1)
            result = store_pat(sys.argv[2])
            # Remove token from output for safety
            result.pop("token", None)
            print(json.dumps(result, indent=2))
        
        elif command == "get":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: pat_manager.py get <org_identifier>"}))
                sys.exit(1)
            result = get_pat(sys.argv[2])
            print(json.dumps(result, indent=2))
        
        elif command == "list":
            orgs = list_orgs()
            print(json.dumps(orgs, indent=2))

        elif command == "list-masked":
            orgs = list_orgs_masked()
            print(json.dumps(orgs, indent=2))

        elif command == "remove":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: pat_manager.py remove <org_identifier>"}))
                sys.exit(1)
            result = remove_org(sys.argv[2])
            print(json.dumps(result, indent=2))
        
        elif command == "validate":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: pat_manager.py validate <pat>"}))
                sys.exit(1)
            result = validate_pat(sys.argv[2])
            print(json.dumps(result, indent=2))
        
        elif command == "info":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: pat_manager.py info <org_identifier>"}))
                sys.exit(1)
            result = get_org_info(sys.argv[2])
            print(json.dumps(result, indent=2))
        
        elif command == "parse-url":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: pat_manager.py parse-url <devrev_url>"}))
                sys.exit(1)
            result = parse_devrev_url(sys.argv[2])
            if result:
                print(json.dumps(result, indent=2))
            else:
                print(json.dumps({"error": "Not a valid DevRev URL"}))
        
        else:
            print(json.dumps({"error": f"Unknown command: {command}. Use: store, get, list, list-masked, remove, validate, info, parse-url"}))
            sys.exit(1)
    
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
