"""DevRev API utility functions for crawler job management."""
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from typing import Tuple, Optional


def get_pat() -> Optional[str]:
    """Get PAT from environment variable."""
    return os.environ.get("DEVREV_PAT", "").strip() or None


def devrev_request(endpoint: str, method: str = "GET", body: Optional[dict] = None, query: str = "") -> Tuple[int, str]:
    """Make a DevRev API request.

    Args:
        endpoint: API endpoint (e.g., "web-crawler-jobs.list")
        method: HTTP method (GET or POST)
        body: Request body for POST requests
        query: Query string for GET requests

    Returns:
        Tuple of (status_code, response_body)
    """
    pat = get_pat()
    if not pat:
        return 401, json.dumps({"error": "DEVREV_PAT not set"})

    gateway_url = os.environ.get("DEVREV_GATEWAY_URL", "https://app.devrev.ai/api/gateway/internal")
    url = f"{gateway_url}/{endpoint}"
    if query:
        url += f"?{query}"

    headers = {
        "Authorization": pat,
        "Content-Type": "application/json",
    }

    try:
        if method == "POST" and body:
            data = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        else:
            req = urllib.request.Request(url, headers=headers, method=method)

        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except Exception as e:
        return 500, json.dumps({"error": str(e)})


def devrev_get(endpoint: str, query: str = "") -> Tuple[int, str]:
    """Convenience wrapper for GET requests."""
    return devrev_request(endpoint, "GET", query=query)


def devrev_post(endpoint: str, body: dict) -> Tuple[int, str]:
    """Convenience wrapper for POST requests."""
    return devrev_request(endpoint, "POST", body=body)


def resolve_part_ids(display_ids: list) -> list:
    """Resolve part display_ids to internal IDs.

    Args:
        display_ids: List of part display_ids (e.g., ["PROD-1", "PROD-2"])

    Returns:
        List of resolved internal IDs
    """
    if not display_ids:
        return []

    try:
        status, body = devrev_get("parts.list", query="limit=100")
        if status != 200:
            return []

        data = json.loads(body)
        parts_map = {
            p.get("display_id"): p.get("id")
            for p in data.get("parts", [])
            if p.get("id")
        }

        return [parts_map[did] for did in display_ids if did in parts_map]
    except Exception:
        return []


def print_error(message: str):
    """Print error message to stderr."""
    print(f"[ERROR] {message}", file=sys.stderr)


def print_warning(message: str):
    """Print warning message to stderr."""
    print(f"[WARN] {message}", file=sys.stderr)


def print_info(message: str):
    """Print info message to stdout."""
    print(f"[INFO] {message}")


def print_success(message: str):
    """Print success message to stdout."""
    print(f"[OK] {message}")
