"""A dependency-free command line report of public GitHub achievements."""

import argparse
import json
from pathlib import Path
import sys
from urllib.error import URLError

from checker import fetch_profile, parse_badges
from progress import build_report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("username", help="GitHub account to inspect")
    parser.add_argument("--html", type=Path, help="Read saved profile HTML instead of the network")
    parser.add_argument("--counts", type=Path, help="JSON object of independently checked event counts")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable report")
    args = parser.parse_args(argv)
    try:
        catalog = json.loads(Path(__file__).with_name("catalog.json").read_text())
        html = args.html.read_text() if args.html else fetch_profile(args.username)
        counts = json.loads(args.counts.read_text()) if args.counts else None
        badges = parse_badges(html)
        rows = build_report(catalog, badges, counts)
    except (OSError, ValueError, URLError) as error:
        parser.exit(1, f"Error: {error}\n")
    if args.json:
        print(json.dumps({"username": args.username, "achievements": rows}, indent=2))
        return 0
    print(f"GitHub achievements: {args.username}")
    print("Publicly visible badges only; hidden/private achievements cannot be inferred.")
    for row in rows:
        status = row["observed_tier"] if row["visible"] else "not visible"
        text = f"{row['name']}: {status}"
        if row["target"] is not None:
            text += f"; next {row['next_tier']} at {row['target']} {row['metric']}"
            if row["remaining"] is not None:
                text += f" ({row['remaining']} remaining from supplied count)"
        if row["requires_payment"]:
            text += "; requires sponsorship payment"
        print(text)
    if not badges:
        print("No badges detected. Visibility settings or a GitHub HTML change may explain this.")
    print("Thresholds are community observations. A count alone does not confirm an award.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
