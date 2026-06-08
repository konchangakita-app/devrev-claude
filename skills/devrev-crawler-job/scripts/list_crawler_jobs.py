#!/usr/bin/env python3
"""List all Web Crawler Jobs.

Usage:
    python3 list_crawler_jobs.py

Environment Variables:
    DEVREV_PAT: DevRev Personal Access Token (required)
"""
import json
import sys
import urllib.parse
from devrev_api import devrev_get, get_pat, print_error, print_success


def fetch_all_jobs() -> list:
    """Fetch all crawler jobs with pagination."""
    if not get_pat():
        print_error("DEVREV_PAT not set")
        return []

    all_jobs = []
    cursor = ""

    while True:
        query = "limit=50"
        if cursor:
            query += "&cursor=" + urllib.parse.quote(cursor)

        try:
            status, body = devrev_get("web-crawler-jobs.list", query=query)
        except Exception as e:
            print_error(f"Request failed: {e}")
            return []

        if status != 200:
            print_error(f"API error: {status}")
            print(body, file=sys.stderr)
            return []

        data = json.loads(body)
        jobs = data.get("web_crawler_jobs", [])
        all_jobs.extend(jobs)

        next_cursor = (data.get("next_cursor") or "").strip()
        if not next_cursor or not jobs:
            break
        cursor = next_cursor

    return all_jobs


def format_job_list(jobs: list) -> str:
    """Format job list as a table."""
    lines = [
        f"[OK] Web Crawler Jobs: {len(jobs)} total",
        "",
        "  display_id             URL                               frequency  state            created_date",
        "  " + "-" * 95,
    ]

    for job in jobs:
        urls = job.get("urls") or []
        url_display = (urls[0][:42] + "..." if urls and len(urls[0]) > 42 else (urls[0] if urls else "")) or "-"
        if len(urls) > 1:
            url_display += f" +{len(urls)-1}"

        freq = job.get("frequency", 0)
        display_id = str(job.get("display_id", ""))
        state = str(job.get("state", ""))
        created = (job.get("created_date") or "").replace("T", " ").rstrip("Z")[:19] or "-"

        lines.append(f"  {display_id:<23} {url_display:<34} {freq:<10} {state:<16} {created}")

    return "\n".join(lines)


def main():
    """Main entry point."""
    if not get_pat():
        print_error("DEVREV_PAT environment variable not set")
        print_error("Please set it using devrev-pat-manager skill")
        sys.exit(1)

    jobs = fetch_all_jobs()
    if jobs is None:
        sys.exit(1)

    output = format_job_list(jobs)
    print(output)

    # Output JSON for programmatic use
    print("\n" + "="*95)
    print(json.dumps({"web_crawler_jobs": jobs}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
