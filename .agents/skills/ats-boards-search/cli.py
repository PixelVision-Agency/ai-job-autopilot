#!/usr/bin/env python3
"""Search the public job boards of chosen companies on Greenhouse, Ashby and Lever.

Each ATS exposes an unauthenticated JSON board per company, so this reads the source
directly instead of an aggregator: new roles show up the day they are posted.
The company list is yours: profile/ats-companies.txt (gitignored with profile/), one
"<ats> <board slug>" per line. See companies.example.txt next to this file. Stdlib only.

    python3 .agents/skills/ats-boards-search/cli.py search -q "designer,frontend" [-x "intern,director"] [--days 14] [--no-onsite]
"""

from __future__ import annotations

import argparse
import http.client
import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COMPANIES = ROOT / "profile" / "ats-companies.txt"
UA = "Mozilla/5.0 (ai-job-autopilot ats-boards-search)"


def keywords(text: str | None) -> re.Pattern | None:
    """Comma-separated title keywords as one case-insensitive pattern; None when empty."""
    words = [k.strip() for k in (text or "").split(",") if k.strip()]
    return re.compile("|".join(re.escape(k) for k in words), re.I) if words else None


def get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.load(resp)


def iso(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):  # Lever: epoch milliseconds
        return datetime.fromtimestamp(value / 1000, timezone.utc).date().isoformat()
    return str(value)[:10]


def board(ats: str, slug: str) -> list[dict]:
    company = slug.replace("-", " ").replace(".", " ").title()
    if ats == "greenhouse":
        data = get_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")["jobs"]
        return [{"id": f"gh-{slug}-{j['id']}", "title": j["title"],
                 "company": j.get("company_name") or company,
                 "location": (j.get("location") or {}).get("name"),
                 "date": iso(j.get("first_published") or j.get("updated_at")),
                 "url": j["absolute_url"], "workplace": None} for j in data]
    if ats == "ashby":
        data = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")["jobs"]
        return [{"id": f"ashby-{slug}-{j['id']}", "title": j["title"], "company": company,
                 "location": j.get("location"), "date": iso(j.get("publishedAt")),
                 "url": j.get("jobUrl") or f"https://jobs.ashbyhq.com/{slug}/{j['id']}",
                 "workplace": "remote" if j.get("isRemote") else (j.get("workplaceType") or "").lower() or None}
                for j in data if j.get("isListed", True)]
    if ats == "lever":
        data = get_json(f"https://api.lever.co/v0/postings/{slug}?mode=json")
        return [{"id": f"lever-{slug}-{j['id']}", "title": j["text"], "company": company,
                 "location": (j.get("categories") or {}).get("location"),
                 "date": iso(j.get("createdAt")), "url": j["hostedUrl"],
                 "workplace": (j.get("workplaceType") or "").lower() or None} for j in data]
    raise ValueError(f"unknown ats {ats!r}")


def load_companies(path: Path) -> list[tuple[str, str]]:
    if not path.exists():
        sys.exit(f"No company list at {path}. Create it with one '<ats> <board slug>' per line "
                 "(see .agents/skills/ats-boards-search/companies.example.txt).")
    pairs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            ats, slug = line.split()
            pairs.append((ats, slug))
    return pairs


def search(args) -> dict:
    companies = load_companies(Path(args.companies))
    include, exclude = keywords(args.query), keywords(getattr(args, "exclude", None))
    since = (datetime.now(timezone.utc) - timedelta(days=args.days)).date().isoformat()
    results, failed = [], []

    def one(pair):
        error = None
        for _ in (1, 2):
            try:
                return pair, board(*pair), None
            # OSError covers URLError, resets and timeouts; HTTPException a body cut off mid-read.
            except (OSError, http.client.HTTPException, ValueError, KeyError, TypeError) as e:
                error = f"{type(e).__name__}: {e}"
                # One retry for a network blip (boards that time out mid-scrape often answer in under
                # 2 s alone). An HTTP status such as 404, or bad data, is final.
                if not isinstance(e, OSError) or isinstance(e, urllib.error.HTTPError):
                    break
        return pair, [], error

    with ThreadPoolExecutor(max_workers=12) as pool:
        for (ats, slug), jobs, error in pool.map(one, companies):
            if error:
                failed.append({"board": f"{ats}/{slug}", "error": error})
            for job in jobs:
                title = job["title"] or ""
                if include and not include.search(title) or exclude and exclude.search(title):
                    continue
                if job["date"] and job["date"] < since:
                    continue
                if getattr(args, "no_onsite", False) and job["workplace"] in ("onsite", "on-site"):
                    continue
                results.append({**job, "ats": ats, "board": slug, "description": None})
    results.sort(key=lambda j: j["date"] or "", reverse=True)
    return {"meta": {"boards": len(companies), "failed_boards": failed, "count": len(results),
                     "since": since}, "results": results}


def main() -> None:
    parser = argparse.ArgumentParser(description="Search company job boards (Greenhouse/Ashby/Lever)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("-q", "--query", help="comma-separated title keywords; a title must contain one (default: all)")
    s.add_argument("-x", "--exclude", help="comma-separated title keywords that drop a role (e.g. intern,director)")
    s.add_argument("--days", type=int, default=14, help="posted within N days (default 14)")
    s.add_argument("--no-onsite", action="store_true", help="drop roles the ATS marks fully on-site")
    s.add_argument("--companies", default=str(COMPANIES), help="company list (default: profile/ats-companies.txt)")
    s.add_argument("--format", choices=("json", "table"), default="json")
    args = parser.parse_args()

    out = search(args)
    if args.format == "json":
        json.dump(out, sys.stdout, indent=1)
        print()
    else:
        for j in out["results"]:
            print(f"{j['date'] or '?':10}  {j['company'][:18]:18}  {j['title'][:60]:60}  {j['location'] or ''}")
        print(f"{out['meta']['count']} roles from {out['meta']['boards']} boards; "
              f"{len(out['meta']['failed_boards'])} boards failed", file=sys.stderr)


if __name__ == "__main__":
    main()
