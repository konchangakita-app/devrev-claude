#!/usr/bin/env python3
"""Control a Web Crawler Job (pause/resume/abort).

Usage:
    python3 control_crawler_job.py --job-id JOB_ID --action ACTION

Arguments:
    --job-id: Job ID or display_id (required, e.g., WCJ-1)
    --action: Action to perform (required: abort | pause | resume)

Environment Variables:
    DEVREV_PAT: DevRev Personal Access Token (required)
"""
import argparse
import json
import sys
from devrev_api import (
    devrev_post,
    get_pat,
    print_error,
    print_info,
    print_success,
)
from list_crawler_jobs import fetch_all_jobs, format_job_list


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Control a Web Crawler Job",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--job-id",
        required=True,
        help="Job ID or display_id (e.g., WCJ-1)",
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=["abort", "pause", "resume"],
        help="Action: abort | pause | resume",
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    if not get_pat():
        print_error("DEVREV_PAT environment variable not set")
        print_error("Please set it using devrev-pat-manager skill")
        sys.exit(1)

    args = parse_args()
    job_id = args.job_id.strip()
    action = args.action.strip().lower()

    if not job_id:
        print_error("Job ID cannot be empty")
        sys.exit(1)

    # Show BEFORE state
    print_info("Fetching job list (BEFORE)...")
    before_jobs = fetch_all_jobs()
    if before_jobs is not None:
        print(format_job_list(before_jobs))
        print("")

    # Control job
    print_info(f"Performing action '{action}' on job {job_id}...")
    try:
        status, response_body = devrev_post(
            "web-crawler-jobs.control",
            {"id": job_id, "action": action}
        )
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
    print_success(f"Job {action}ed successfully!")
    print("="*60)
    print(f"  Display ID:  {job.get('display_id')}")
    print(f"  State:       {job.get('state')}")
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
