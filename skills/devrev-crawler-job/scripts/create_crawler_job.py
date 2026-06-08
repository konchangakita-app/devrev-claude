#!/usr/bin/env python3
"""Create a new Web Crawler Job.

Usage:
    python3 create_crawler_job.py --urls URL [--part PART] [--frequency N] [--max-depth N] [--description DESC]

Arguments:
    --urls: Comma-separated list of URLs to crawl (required, max 50)
    --part: Part display_id to apply to (required, e.g., PROD-1)
    --frequency: Crawl frequency (0=once, 1-12=recurring days, default: 0)
    --max-depth: Crawl depth (1-10, default: 4)
    --description: Job description (optional)

Environment Variables:
    DEVREV_PAT: DevRev Personal Access Token (required)
"""
import argparse
import json
import sys
from devrev_api import (
    devrev_post,
    get_pat,
    resolve_part_ids,
    print_error,
    print_info,
    print_success,
    print_warning,
)
from list_crawler_jobs import fetch_all_jobs, format_job_list


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create a new Web Crawler Job",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--urls",
        required=True,
        help="Comma-separated URLs to crawl (max 50)",
    )
    parser.add_argument(
        "--part",
        required=True,
        help="Part display_id (e.g., PROD-1)",
    )
    parser.add_argument(
        "--frequency",
        type=int,
        default=0,
        help="Crawl frequency: 0=once, 1-12=recurring days (default: 0)",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=4,
        help="Crawl depth (1-10, default: 4)",
    )
    parser.add_argument(
        "--description",
        default="",
        help="Job description",
    )
    return parser.parse_args()


def validate_args(args):
    """Validate arguments."""
    # Validate URLs
    urls = [u.strip() for u in args.urls.split(",") if u.strip()]
    if not urls:
        print_error("No URLs provided")
        return None

    if len(urls) > 50:
        print_error("Maximum 50 URLs allowed")
        return None

    # Validate frequency
    frequency = max(0, min(12, args.frequency))
    if frequency != args.frequency:
        print_warning(f"Frequency adjusted to {frequency} (valid range: 0-12)")

    # Validate max_depth
    max_depth = max(1, min(10, args.max_depth))
    if max_depth != args.max_depth:
        print_warning(f"Max depth adjusted to {max_depth} (valid range: 1-10)")

    return {
        "urls": urls,
        "frequency": frequency,
        "max_depth": max_depth,
        "part": args.part,
        "description": args.description,
    }


def main():
    """Main entry point."""
    if not get_pat():
        print_error("DEVREV_PAT environment variable not set")
        print_error("Please set it using devrev-pat-manager skill")
        sys.exit(1)

    args = parse_args()
    validated = validate_args(args)
    if not validated:
        sys.exit(1)

    # Show BEFORE state
    print_info("Fetching job list (BEFORE)...")
    before_jobs = fetch_all_jobs()
    if before_jobs is not None:
        print(format_job_list(before_jobs))
        print("")

    # Resolve part IDs
    print_info(f"Resolving part ID for {validated['part']}...")
    part_ids = resolve_part_ids([validated["part"]])
    if not part_ids:
        print_error(f"Could not resolve part ID for {validated['part']}")
        print_error("Please check the part display_id and try again")
        sys.exit(1)

    print_success(f"Resolved part ID: {part_ids[0]}")

    # Create job
    body = {
        "urls": validated["urls"],
        "applies_to_parts": [part_ids[0]],
        "frequency": validated["frequency"],
        "max_depth": validated["max_depth"],
    }

    if validated["description"]:
        body["description"] = validated["description"]

    print_info("Creating crawler job...")
    try:
        status, response_body = devrev_post("web-crawler-jobs.create", body)
    except Exception as e:
        print_error(f"Request failed: {e}")
        sys.exit(1)

    if status != 200:
        print_error(f"API error: {status}")
        print(response_body, file=sys.stderr)
        sys.exit(1)

    data = json.loads(response_body)
    job = data.get("web_crawler_job", {})

    # Print result
    print("")
    print_success("Crawler job created successfully!")
    print("="*60)
    print(f"  Display ID:  {job.get('display_id')}")
    print(f"  State:       {job.get('state')}")
    print(f"  URLs:        {len(validated['urls'])} URL(s)")
    print(f"  Frequency:   {validated['frequency']} {'(once)' if validated['frequency'] == 0 else '(recurring)'}")
    print(f"  Max Depth:   {validated['max_depth']}")
    if validated["description"]:
        print(f"  Description: {validated['description']}")
    print("="*60)

    # Show AFTER state
    print("")
    print_info("Fetching job list (AFTER)...")
    after_jobs = fetch_all_jobs()
    if after_jobs is not None:
        print(format_job_list(after_jobs))

    # Output full JSON
    print("\n" + "="*60)
    print("Full response:")
    print(json.dumps(job, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
