# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

This project is derived from [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search)
(MIT). The history of that project is not carried over.

## [Unreleased]

### Added

- CV template: optional `CERTIFICATIONS`; job/school dates and `company` are optional and year-only dates
  are accepted; empty Projects/References sections draw no heading; language rows no longer show
  flags. `.env.example` is now tracked.
- **`/onboard`** - runtime-neutral onboarding (Claude Code and Codex) that builds the private
  `profile/` folder, selects job boards for the user's role, seniority, country and languages,
  configures the CV/letter theme with a test render, and ends with a dry-run evaluation.
- **Portal selection** - ranked board proposal (global, country, niche), verified with
  `tools/robots_check.py`, stored in `profile/portals.md`; `/scrape` reads it.
- `requirements.txt`.
- **`/cycle`** - the whole routine in one command: both scouts side by side, closed postings dropped
  before evaluation, alert roles first, at most 10 LinkedIn Easy Apply sends per cycle, every alert
  settled, `/mail-cleanup` last, skip reasons counted and access blockers flagged in the report.
  Codex gets matching `alert-scout` / `portal-scout` agents.
- **`/patterns`** and `tools/patterns.py` - outcome rates by fit band, role type, channel and ATS;
  `tools/tracker_labels.py` fixes the `role_type` and `channel` vocabularies (own role families in
  `profile/role_types.txt`).
- `tools/liveness.py` - open / closed / unknown per posting URL through the Greenhouse, Lever and
  Ashby APIs and LinkedIn's guest page; `/apply`, `/rank` and `/cycle` run it first.
- `ats-boards-search` - reads the public Greenhouse, Ashby and Lever boards of the companies in
  `profile/ats-companies.txt` (stdlib Python, no bun).
- `gmail_client.py`: `draft-reply --sent` (follow-up to your own email) and `--trash`;
  `clean-drafts` trashes drafts whose thread was already sent.
- ATS resume: optional `ANSWER_TITLE` / `ANSWER` section for a posting's own question.

### Changed

- Personal data moved out of tracked files into the gitignored `profile/` folder.
- `/reset` wipes `profile/` (and optionally `documents/`) after explicit confirmation.
- `/add-portal` registers new boards in `profile/portals.md`.
- `/setup` is now an alias for `/onboard`.
- `/apply` writes a cover letter only when the application route takes one, never reuses sentences
  from earlier letters, names at most one or two gaps, and its grounding audit checks years per
  technology, stack per employer, titles, shipped claims, adjacent work and salary one by one.
- `/submit`, `/mail-cleanup`, `/job-alerts` and `/scrape` carry the form workarounds and cleanup
  rules from daily use (Greenhouse email codes, LinkedIn prefills, the by-hand inbox sweep, ...).

### Fixed

- CI never ran: it was triggered on `master`, the default branch is `main`. The Python test job now
  installs `requirements.txt` and Chromium, and the placeholder check looks for the tokens in
  `profile.example/profile.md` (the old ones left `CLAUDE.md` and `04-job-evaluation.md` with the
  move to `profile/`).
- Mail cleanup: rejections match the full company name only, two open roles at one company need the
  role named, receipt-shaped rejections are kept, ATS footers no longer name the company, filed
  rejections in the Bin are not re-flagged.
- Low-cost market filter: unknown places and a bare "Remote" no longer let low-cost postings through;
  a posting that also names an accepted place is kept; LATAM in the title is caught.
- Duplicate matching ignores legal suffixes and "- Remote" tags, so applied roles are not re-ranked.
- Himalayas: null categories crashed queries; 429 now honours `Retry-After`. Adzuna: request
  timeouts, salaries compared in EUR. Danish CLIs: `@types/node` pinned for Bun 1.4.
- ATS resume: a long skill wraps in its own column instead of overlapping the other.
- `/submit` no longer hardcodes a residence country or engagement type.
