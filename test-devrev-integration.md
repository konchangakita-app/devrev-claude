# DevRev GitHub Integration Test

This file is created to test DevRev's GitHub integration.

## Test Details

- **Issue**: ISS-3
- **Purpose**: Verify that commits and PRs are properly linked to DevRev issues
- **Date**: 2026-06-09

## Expected Behavior

When this PR is created with ISS-3 in the commit message and PR title:
- DevRev should automatically link this PR to ISS-3
- Commit history should be visible in DevRev
- Status updates should sync between GitHub and DevRev

## Test Checklist

- [ ] Commit created with ISS-3 reference
- [ ] PR created with ISS-3 reference
- [ ] DevRev shows linked PR
- [ ] Commit appears in DevRev issue timeline
