"""Show this month's GitHub Actions minutes: used, remaining and a projection."""

import calendar
import os
import sys
from collections import defaultdict
from datetime import date

import httpx


API = "https://api.github.com"
USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("BILLING_TOKEN", "")
INCLUDED = int(os.getenv("INCLUDED_MINUTES", "2000"))

def get_json(path, **params):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "profile-api",
    }
    r = httpx.get(f"{API}{path}", headers=headers, params=params, timeout=20)
    return r.status_code, r.json()

def count_minutes(items):
    total = 0.0
    per_repo = defaultdict(float)
    for item in items:
        if item.get("product", "").lower() != "actions":
            continue
        if item.get("unitType", "").lower() != "minutes":
            continue
        minutes = float(item.get("quantity", 0))
        total += minutes
        per_repo[item.get("repositoryName") or "(unknown)"] += minutes
    return total, per_repo

def get_usage(today):
    status, data = get_json(f"/users/{USERNAME}/settings/billing/usage",
                            year=today.year, month=today.month)
    if status == 200 and "usageItems" in data:
        used, per_repo = count_minutes(data["usageItems"])
        return used, INCLUDED, per_repo

    # Older billing accounts only have this endpoint.
    status, data = get_json(f"/users/{USERNAME}/settings/billing/actions")
    if status == 200:
        used = float(data.get("total_minutes_used", 0))
        included = int(data.get("included_minutes") or INCLUDED)
        return used, included, {}

    raise RuntimeError(f"GitHub API error {status}: {data.get('message', data)}")

def main():
    if not TOKEN:
        print("BILLING_TOKEN is not set. Add it to .env and load it first.")
        return 1

    today = date.today()
    try:
        used, included, per_repo = get_usage(today)
    except (httpx.HTTPError, RuntimeError) as e:
        print(e)
        return 1
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_left = days_in_month - today.day
    remaining = max(included - used, 0)
    projected = used / today.day * days_in_month

    print(f"GitHub Actions minutes for @{USERNAME} - {today:%B %Y}")
    print(f"  Used so far : {used:,.0f} / {included:,} min ({used / included:.0%})")
    print(f"  Remaining   : {remaining:,.0f} min")
    print(f"  Days left   : {days_left} (resets on the 1st)")
    status = "over the limit!" if projected > included else "within the limit"
    print(f"  Projection  : ~{projected:,.0f} min by month end ({status})")

    if per_repo:
        print("  By repository:")
        for repo, minutes in sorted(per_repo.items(), key=lambda kv: -kv[1]):
            print(f"    {repo:<30} {minutes:>6,.0f} min")
    return 0

if __name__ == "__main__":
    sys.exit(main())
