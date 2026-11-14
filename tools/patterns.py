#!/usr/bin/env python3
"""Where applications go and what comes back, from profile/tracker.csv.

Groups every sent application by fit band, role type, channel (where the lead was
found) and ATS (how it was submitted), with rejection, interview and silence rates.
Counts only; it never edits the tracker.

    python3 tools/patterns.py [--min 5] [--silent-days 30]
"""

from __future__ import annotations

import argparse
import collections
from datetime import date
from urllib.parse import urlsplit

try:
    from tools.tracker_labels import normalize_channel, normalize_role_type, read_tracker
except ImportError:  # run as a script: tools/ itself is on sys.path
    from tracker_labels import normalize_channel, normalize_role_type, read_tracker

# /outcome's "Tracker status vocabulary": everything that was actually sent.
POSITIVE = {"interview", "offer", "hired", "offer_declined", "offer declined"}
NEGATIVE = {"rejected"}
SENT = POSITIVE | NEGATIVE | {"applied", "no_response", "no response"}
MIN_POSITIVES_FOR_CUTOFF = 5

ATS_HOSTS = (("greenhouse", "greenhouse"), ("ashbyhq", "ashby"), ("lever.co", "lever"),
             ("linkedin.com", "linkedin"), ("workable", "workable"), ("teamtailor", "teamtailor"),
             ("myworkdayjobs", "workday"), ("smartrecruiters", "smartrecruiters"),
             ("himalayas", "himalayas"), ("freehire", "freehire"), ("indeed", "indeed"))


def fit_band(value: str) -> str:
    if not value.strip().isdigit():
        return "no score"
    n = int(value)
    return next(label for floor, label in ((80, "80+"), (70, "70-79"), (60, "60-69"),
                                           (50, "50-59"), (0, "<50")) if n >= floor)


def ats(source: str) -> str:
    host = urlsplit((source or "").strip()).netloc.lower()
    return next((name for key, name in ATS_HOSTS if key in host), "other site" if host else "no url")


def days_since(value: str, today: date) -> int | None:
    try:
        return (today - date.fromisoformat(value.strip()[:10])).days
    except ValueError:
        return None


def summarize(rows, key, silent_days: int, today: date):
    groups = collections.defaultdict(collections.Counter)
    for row in rows:
        g = groups[key(row)]
        status = row["status"].strip().lower()
        g["sent"] += 1
        g["positive"] += status in POSITIVE
        g["rejected"] += status in NEGATIVE
        age = days_since(row["date"], today)
        g["silent"] += status in ("applied", "no_response", "no response") and (age or 0) >= silent_days
    return groups


def print_table(title, groups, min_sent):
    print(f"\n## By {title}")
    print(f"{'':22} {'sent':>5} {'interview':>10} {'rejected':>9} {'silent':>7}")
    small = collections.Counter()
    for name, g in sorted(groups.items(), key=lambda kv: -kv[1]["sent"]):
        if g["sent"] < min_sent:
            small.update(g)
            continue
        print(f"{name[:22]:22} {g['sent']:5} {g['positive']:10} "
              f"{g['rejected'] / g['sent']:9.0%} {g['silent'] / g['sent']:7.0%}")
    if small:
        print(f"{'(smaller groups)':22} {small['sent']:5} {small['positive']:10}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Application outcome patterns")
    parser.add_argument("--min", type=int, default=5, help="smallest group shown on its own")
    parser.add_argument("--silent-days", type=int, default=30,
                        help="an applied row with no answer after this many days counts as silent")
    args = parser.parse_args()
    today = date.today()

    _, all_rows = read_tracker()
    rows = [r for r in all_rows if r["status"].strip().lower() in SENT]
    statuses = collections.Counter(r["status"].strip().lower() for r in all_rows)
    positives = [r for r in rows if r["status"].strip().lower() in POSITIVE]

    print(f"# Application patterns ({today})")
    print(f"tracker rows {len(all_rows)}, sent {len(rows)}, interviews or better {len(positives)}"
          f" ({len(positives) / max(len(rows), 1):.1%})")
    print("statuses:", ", ".join(f"{k or '(empty)'} {v}" for k, v in statuses.most_common()))

    for title, key in (
        ("fit band", lambda r: fit_band(r["fit_rating"])),
        ("role type", lambda r: normalize_role_type(r["role_type"], r["role"])),
        ("channel (where found)", lambda r: normalize_channel(r["channel"], r["source"])),
        ("ATS (where sent)", lambda r: ats(r["source"])),
    ):
        print_table(title, summarize(rows, key, args.silent_days, today), args.min)

    print("\n## Fit score vs outcome")
    for label, group in (("interview+", POSITIVE), ("rejected", NEGATIVE),
                         ("still waiting", {"applied"})):
        scores = [int(r["fit_rating"]) for r in rows
                  if r["status"].strip().lower() in group and r["fit_rating"].strip().isdigit()]
        if scores:
            print(f"{label:14} n={len(scores):4}  mean fit {sum(scores) / len(scores):.0f}")
    if len(positives) < MIN_POSITIVES_FOR_CUTOFF:
        print(f"Too few interviews ({len(positives)}) to suggest a fit cutoff; "
              f"needs {MIN_POSITIVES_FOR_CUTOFF}.")
    else:
        floor = min(int(r["fit_rating"]) for r in positives if r["fit_rating"].strip().isdigit())
        below = sum(1 for r in rows if r["fit_rating"].strip().isdigit() and int(r["fit_rating"]) < floor)
        print(f"Lowest fit that reached interview: {floor}. {below} applications sent below it.")
    for r in positives:
        print(f"  interview+: {r['company']} - {r['role']} (fit {r['fit_rating'] or '?'}, "
              f"{normalize_channel(r['channel'], r['source'])}, {ats(r['source'])})")


if __name__ == "__main__":
    main()
