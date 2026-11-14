# /cycle - Full job cycle: alerts, scrape, apply, clean up

One command for the standing routine in `CLAUDE.md`. Run it end to end without asking per step.
Read `profile/profile.md` and `profile/deal-breakers.md` first; if `profile/` is missing, run
`/onboard` instead. The gates (fit score, auto-submit scope, standing rules) are the user's, in
`profile/deal-breakers.md` ("Apply gates", "Standing rules", "Housekeeping rules"); answers and
edge cases live in the commands this one calls. The rules below are only the cycle's own: what
to open, what to draft, when to flag.

## Steps

1. **Discover, in parallel.** Launch `alert-scout` (`/job-alerts`: Gmail alert emails into
   `profile/job_alerts/alerts.json`) and `portal-scout` (`/scrape`: the boards in
   `profile/portals.md`) as two Agent calls in one message, in the foreground (no background
   flag): they run side by side and both results come back before you go on. Tell both "no
   Playwright" (they would share the one browser page you need for forms). Never launch them
   in the background and end your turn to wait: an unattended run can exit before a scout
   reports, which ends the cycle with nothing applied or cleaned. Gmail not configured: skip
   `alert-scout` and say so in the report. In Codex, run the two scouts as
   `.codex/agents/alert-scout.toml` and `portal-scout.toml`.
2. **Drop closed postings first.** Run `python3 tools/liveness.py <url> <url> ...` once over
   every alert role and scraped lead. A `closed` one is not evaluated: its alert role is
   `skipped` with the liveness reason (a scraped lead is marked `expired` in
   `job_scraper/seen_jobs.json`). `unknown` carries on as normal.
3. **Apply, alert roles first, then scraped leads.** For each role: evaluate fit
   (`04-job-evaluation.md`); if it clears the apply gates in `profile/deal-breakers.md` or is
   covered by one of its standing rules, run `/apply` then `/submit` (`/submit` only within the
   auto-submit scope the user set there; outside it, stop after `/apply` and leave the row
   `drafted`).
   - **portal-scout's quick fit is triage from a listing, not the fit.** Open the posting and
     score properly every scraped lead whose quick fit is within 10 points of the gate or above
     it, before deciding. One further below may be skipped on the quick score, with that as its
     reason. A lead that lands within 10 points under the gate after the read is drafted
     (`/apply`, no `/submit`) and left `drafted` for the user; lower is skipped with its score.
   - Finish open application tabs before starting new ones.
   - **LinkedIn Easy Apply: at most 10 sends per cycle.** LinkedIn restricts accounts it sees
     automating. Roles past the cap stay `new` in `alerts.json`, so their email stays in the
     inbox, and go first next cycle. That is the one exception to step 4.
   - **Never skip or park a role as "needs a login" on a guess.** Only when the page itself shows
     the login wall or the browser says it is logged out. A cycle that drops every LinkedIn role
     as "needs login" while the browser was logged in loses days of leads without anyone noticing.
4. **Settle every alert.** Each role in `profile/job_alerts/alerts.json` ends as `sent` or
   `skipped` (never `new` or `drafted`), except LinkedIn roles held back by the cap in step 3.
   Work only the user can do (creating an account on the employer's site, a captcha, a login, a
   judgment call such as a hybrid role in another city) goes into the tracker as a `drafted` row
   whose note names the exact step ("needs you: create an account at <site>, then Submit"), and
   the alert role is set to `skipped` with that reason. The tracker, not the inbox, is where
   parked work lives, so `/mail-cleanup` can trash the alert email.
5. **Clean up, LAST**, after the final send: run `/mail-cleanup`. That trashes handled job-alert
   emails, submission receipts, "viewed" pings and rejections (tracker row updated first). Read
   its output and resolve every flagged line (an "ALERT still open" line for LinkedIn roles held
   back by the cap is expected: leave it). Do the by-hand sweep it describes, then check
   `python3 tools/gmail_client.py search "in:inbox newer_than:3d"`. Only person threads
   (recruiters, interviews, personal mail) may remain, and each is named in the report.
   **A person thread that schedules or confirms a call or interview, or sends an assessment, for
   a tracked application moves that row to `interview`** with a dated note (`/outcome` Step 4:
   status and notes only). Never reply; a reply is a draft, and only when asked
   (`10-email-replies.md`).
6. **Close the browser** (`browser_close`). Exception: a form parked for the user that exists
   only in that window stays open, and the report says so.

## Report

Sent, drafted and skipped roles (one line each, with the reason), what cleanup trashed, and the
person threads still in the inbox.

**When nothing was sent but roles came in, say why in counts.** Open the report with the skip
reasons grouped and counted, for example "18 skipped: 9 relocation, 5 fit below the gate, 4
closed". If one reason that is about access rather than the role (a login, a page that will not
load, a refused command) covers most of them, start the final message with "Needs you: <reason>
blocked <N> roles", so a scheduled run shows a problem instead of a quiet success.

End with the first two lines of `python3 tools/patterns.py` (rows sent so far, interviews) once
the tracker exists, so the trend is visible each cycle; the full `/patterns` report is run on
request.
