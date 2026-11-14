#!/usr/bin/env python3
"""Fixed vocabularies for the tracker's role_type and channel columns.

Free text spells the same thing many ways ("Product Designer", "Product design", "product
designer") and then nothing can be counted. Every writer uses the values below; readers
(tools/patterns.py) normalize on the fly so a stray label still counts.

The default role families cover common tech, design, product and data roles. For other fields,
put your own in profile/role_types.txt, one "<label> <regex>" per line (# for comments). They
are tried first, in order, and the first match wins.

    python3 tools/tracker_labels.py           # show what would change
    python3 tools/tracker_labels.py --apply   # rewrite the tracker in place
"""

from __future__ import annotations

import argparse
import collections
import csv
import io
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACKER = ROOT / "profile" / "tracker.csv"
ROLE_FILE = ROOT / "profile" / "role_types.txt"

# First match wins, so the order matters: "AI product designer" is product-design,
# "AI solutions engineer" is solutions, "design engineer" is not product-design.
DEFAULT_ROLE_RULES = (
    ("conversation-design", r"conversation|prompt"),
    ("design-engineering", r"design[\s-]*(?:systems?[\s-]*)?engineer|design technologist|"
                           r"creative technologist|ux engineer"),
    ("product-design", r"\b(?:product|ux|ui|interaction|digital|visual)\b.*design|"
                       r"design(?:er)?\b.*\b(?:product|ux|ui)\b|head of design|^design(?:er)?$"),
    ("web-design", r"web(?:site)?[\s-]*design|brand|graphic|editorial"),
    ("product-design", r"design"),  # any other designer ("Senior Designer")
    ("product-management", r"product[\s-]*(?:manager|owner|management|lead)|\bpm\b"),
    ("solutions", r"solution|forward[\s-]*deployed|implementation|pre-?sales|"
                  r"sales engineer|partner"),
    ("ai-engineering", r"\bai\b|\bml\b|machine learning|\bllm|agentic|genai"),
    ("data", r"\bdata\b|analytics|analyst|\bbi\b"),
    ("devops", r"devops|\bsre\b|site reliability|platform engineer|infrastructure|cloud engineer"),
    ("qa", r"\bqa\b|quality assurance|\btest(?:ing)? engineer|\bsdet\b"),
    ("mobile", r"\bios\b|android|mobile|react native|flutter"),
    ("frontend", r"front[\s-]*end|\bui\b|react|vue|angular|web develop"),
    ("backend", r"back[\s-]*end"),
    ("product-engineering", r"product[\s-]*engineer"),
    ("fullstack", r"full[\s-]*stack|software|engineer|developer|programmer"),
)


def _load_rules() -> tuple:
    """profile/role_types.txt: "<label> <regex>" per line, tried before the defaults."""
    try:
        lines = ROLE_FILE.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ()
    rules = []
    for line in lines:
        label, _, pattern = line.strip().partition(" ")
        if label and not label.startswith("#") and pattern.strip():
            rules.append((label, pattern.strip()))
    return tuple(rules)


ROLE_RULES = _load_rules() + DEFAULT_ROLE_RULES
ROLE_TYPES = tuple(dict.fromkeys(name for name, _ in ROLE_RULES)) + ("other",)

# Where the lead was found. How it was submitted (ATS) is read from the source URL instead.
CHANNELS = ("email-alert", "linkedin", "job-board", "careers-page", "hn", "direct", "other")
JOB_BOARDS = {"portal", "job-board", "himalayas", "adzuna", "indeed", "freehire", "jobindex",
              "jobnet", "jobdanmark", "jobbank", "ats-boards", "glassdoor", "welcometothejungle"}
ATS_NAMES = {"ashby", "greenhouse", "lever", "workable", "online", "careers page",
             "company-portal"}


def _match_role(text: str) -> str | None:
    text = (text or "").strip().lower()
    for name, pattern in ROLE_RULES:
        if re.search(pattern, text):
            return name
    return None


def normalize_role_type(role_type: str, title: str = "") -> str:
    """role_type when it names a role, else the job title, else 'other'.

    Some rows hold "Full-time" or "On-site (Lisbon)" in role_type; the title decides those.
    """
    if role_type in ROLE_TYPES:
        return role_type
    return _match_role(role_type) or _match_role(title) or "other"


def normalize_channel(channel: str, source: str = "") -> str:
    c = (channel or "").strip().lower()
    if c in CHANNELS and c != "job-board":
        return c
    if "alert" in c:
        return "email-alert"
    if "hacker news" in c:
        return "hn"
    if "linkedin" in c:
        return "linkedin"
    if c in JOB_BOARDS or c.startswith("portal") or "joinrs" in c:
        # /scrape writes "portal" for every board, LinkedIn search included.
        return "linkedin" if "linkedin.com" in (source or "") else "job-board"
    if c in ATS_NAMES or "careers" in c or "form" in c:
        return "careers-page"
    if c == "email":
        return "direct"
    return "other"


def read_tracker(path: Path = TRACKER):
    if not path.exists():
        sys.exit(f"No tracker at {path}: /apply creates it with the first application.")
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def write_tracker(fields, rows, path: Path = TRACKER) -> None:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tracker-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(output.getvalue())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize tracker labels")
    parser.add_argument("--apply", action="store_true", help="rewrite the tracker in place")
    args = parser.parse_args()

    fields, rows = read_tracker()
    changes = collections.Counter()
    for row in rows:
        new_role = normalize_role_type(row["role_type"], row["role"])
        new_channel = normalize_channel(row["channel"], row["source"])
        changes[("role_type", row["role_type"], new_role)] += row["role_type"] != new_role
        changes[("channel", row["channel"], new_channel)] += row["channel"] != new_channel
        row["role_type"], row["channel"] = new_role, new_channel
    for (column, old, new), n in sorted(changes.items(), key=lambda kv: -kv[1]):
        if n:
            print(f"{column:9} {n:4}  {old!r} -> {new}")
    for column in ("role_type", "channel"):
        print(column, dict(collections.Counter(r[column] for r in rows).most_common()))
    if args.apply:
        write_tracker(fields, rows)
        print(f"rewrote {TRACKER.name}: {sum(changes.values())} cells changed")


if __name__ == "__main__":
    main()
