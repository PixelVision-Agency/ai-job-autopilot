---
name: ats-boards-search
version: 1.0.0
description: >
  Search the public Greenhouse, Ashby and Lever job boards of a list of companies the user
  wants to work for. Reads each company's own board, so roles appear the day they are posted
  and before aggregators pick them up. Needs profile/ats-companies.txt. Trigger phrases:
  company boards, target companies, ATS boards, "anything new at <company>".
context: fork
enabled: true  # set to false to keep this portal installed but have /scrape skip it
allowed-tools: Bash(python3 .agents/skills/ats-boards-search/cli.py *)
---

# ATS boards search

Greenhouse, Ashby and Lever expose an unauthenticated JSON board per company, so a company
list plus three small fetchers cover a large share of the companies that use them. Idea from
career-ops (`scan.mjs` + `providers/`, MIT). Python stdlib only, no bun.

## Command

```bash
python3 .agents/skills/ats-boards-search/cli.py search -q "keyword,keyword" [-x "keyword,keyword"] [--days 14] [--no-onsite] [--format json|table]
```

- `-q` - comma-separated title keywords; a role is kept when its title contains one. Build
  them from the role families and titles in `profile/search-queries.md`. Without `-q` every
  role on every board is returned.
- `-x` - comma-separated title keywords that drop a role (for example seniority levels or
  disciplines the profile rules out: `intern,director,sales`).
- `--days N` - posted within N days (default 14). Greenhouse reports `first_published`
  (falls back to `updated_at`), Ashby `publishedAt`, Lever `createdAt`.
- `--no-onsite` - drop roles the ATS marks fully on-site. Pass it when
  `profile/deal-breakers.md` rules out on-site work. Hybrid and unlabelled roles always stay
  for `/scrape` to judge.
- `--format json` (default) prints `{ "meta": { "boards", "count", "since", "failed_boards" },
  "results": [...] }`. Each result has `id`, `title`, `company`, `location`, `date`, `url`,
  `workplace` (`remote` / `hybrid` / null), `ats`, `board`, and `description: null`.
  Fetch the posting with WebFetch for the description (Step 2 of `/scrape`).

One call scans every board (12 in parallel). A board that times out is retried once; one that
still fails is listed under `failed_boards` and the rest still return. Exit code 2 only on bad
arguments; a missing company list exits with a message saying where to create it.

## Company list

`profile/ats-companies.txt` (private, gitignored), one `<ats> <slug>` per line (`ashby acme`,
`greenhouse acme`, `lever acme`); `companies.example.txt` here shows the format. The slug is
the path segment of the company's board URL: `jobs.ashbyhq.com/<slug>`,
`job-boards.greenhouse.io/<slug>`, `jobs.lever.co/<slug>`. Add a company when an application
or alert shows it hires for the profile; delete a line when it shows up under
`failed_boards` twice (the company moved ATS - check its careers page for the new board).

Company names come from the slug (`duck-duck-go` -> `Duck Duck Go`) except on Greenhouse,
which returns the real name.
