#!/usr/bin/env python3
"""Is a job posting still open? Checked before any CV is written for it.

Greenhouse, Lever and Ashby are asked through their public job-board APIs, which
answer exactly. LinkedIn uses its guest posting page. Any other page is fetched and
read for closure wording ("no longer accepting applications"). Idea from career-ops'
liveness-core.mjs, cut down to the common cases.

    python3 tools/liveness.py <url> [<url> ...]

One JSON line per URL: {"url", "status": "open" | "closed" | "unknown", "reason"}.
"unknown" (blocked, timeout, page with no signal) means: go ahead and fetch it
normally. Only "closed" is a reason to skip. Exit code is 0 unless an argument is
missing.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import parse_qs, urlsplit

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
TIMEOUT = 20

CLOSED_PATTERNS = [re.compile(p, re.I) for p in (
    r"no longer accepting applications",
    r"job (?:ad )?(?:is )?no longer (?:available|open|active)",  # "ad": djinni
    r"(?:position|role|job|posting|vacancy) (?:has been|is) (?:filled|closed)\b(?!-)",
    r"this (?:job|role|position|posting|vacancy)(?: listing)? (?:has )?(?:expired|is closed\b(?!-))",
    r"job posting has expired",
    r"(?:job|posting|position) (?:listing )?not found",
    r"(?:the )?(?:job|position|vacancy) you (?:are|were) looking for (?:is no longer|has been|no longer)",
    r"applications? (?:for this (?:job|role|position) )?(?:are|is) (?:now )?closed",
    r"can't view this job because it's not available",
    r"offerta (?:non e piu|scaduta)",  # Italian boards
)]


def normalize(text: str) -> str:
    """ASCII quotes, no accents, single spaces: portals write "n’est" and "è"."""
    text = re.sub(r"[‘’ʼ′´`]", "'", text or "")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text)


def page_signal(text: str) -> str | None:
    """The closure phrase found in a page's text, if any."""
    text = normalize(re.sub(r"<[^>]+>", " ", text))
    for pattern in CLOSED_PATTERNS:
        if m := pattern.search(text):
            return m.group(0)
    return None


def api_target(url: str):
    """(kind, api_url, posting_id) for URLs an ATS API can answer, else None."""
    parts = urlsplit(url.strip())
    host, path = parts.netloc.lower(), [p for p in parts.path.split("/") if p]
    if host.endswith(".greenhouse.io"):
        gh_id = parse_qs(parts.query).get("gh_jid", [None])[0]
        board = parse_qs(parts.query).get("for", [None])[0]
        if "jobs" in path and path.index("jobs") + 1 < len(path):
            board, gh_id = path[0], path[path.index("jobs") + 1]
        if board and gh_id and gh_id.isdigit():
            return "greenhouse", f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{gh_id}", gh_id
    if host in ("jobs.lever.co", "jobs.eu.lever.co") and len(path) >= 2:
        api = "api.eu.lever.co" if ".eu." in host else "api.lever.co"
        return "lever", f"https://{api}/v0/postings/{path[0]}/{path[1]}", path[1]
    if host == "jobs.ashbyhq.com" and len(path) >= 2:
        return "ashby", f"https://api.ashbyhq.com/posting-api/job-board/{path[0]}", path[1]
    if (host == "linkedin.com" or host.endswith(".linkedin.com")) and (m := re.search(r"(?:/jobs/view/(?:[^/]*-)?|currentJobId=)(\d{6,})", url)):
        return "linkedin", f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{m[1]}", m[1]
    return None


def fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read(2_000_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""


def check(url: str) -> dict:
    result = {"url": url, "status": "unknown", "reason": ""}
    try:
        target = api_target(url)
        if target:
            kind, api_url, posting_id = target
            code, body = fetch(api_url)
            if kind == "ashby":
                if code == 200:
                    ids = {job.get("id") for job in json.loads(body).get("jobs", [])}
                    open_ = posting_id in ids
                    result.update(status="open" if open_ else "closed",
                                  reason=f"ashby board {'lists' if open_ else 'does not list'} the posting")
                    return result
            elif code == 200:
                signal = page_signal(body) if kind == "linkedin" else None
                result.update(status="closed" if signal else "open",
                              reason=f"{kind}: {signal}" if signal else f"{kind} api 200")
                return result
            elif code in (404, 410):
                result.update(status="closed", reason=f"{kind} api {code}")
                return result
            result["reason"] = f"{kind} api {code}; "
        code, body = fetch(url)
        if code in (404, 410):
            result.update(status="closed", reason=result["reason"] + f"page {code}")
        elif code == 200 and (signal := page_signal(body)):
            result.update(status="closed", reason=result["reason"] + f"page says: {signal}")
        elif code == 200:
            result.update(reason=result["reason"] + "page 200, no closure wording")
        else:
            result.update(reason=result["reason"] + f"page {code}")
    except Exception as e:  # network trouble is "unknown", never "closed"
        result["reason"] += f"{type(e).__name__}: {e}"
    return result


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    with ThreadPoolExecutor(max_workers=8) as pool:  # a cycle passes every lead at once
        for result in pool.map(check, sys.argv[1:]):
            print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
