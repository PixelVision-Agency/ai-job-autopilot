# /mail-cleanup - Clean the Gmail inbox after an apply cycle

Run LAST in every apply cycle, after the final send, without being asked, and whenever the user asks.
Works on the user's Gmail through `tools/gmail_client.py` (configure the address and app password as
described in that module); no mail client needs to be open. Trashed mail stays recoverable in Gmail's Bin for 30 days.

## Run

```bash
python3 tools/clean_confirmations.py --reject --delete --days 120 --settle 6
```

`--days 120` reads the whole recent inbox, not just the last few days, so a receipt or rejection
that arrived while no cycle ran is still handled. One command does all of it:

- **Receipts** ("your application was sent", "Thanks for applying", Ashby/Workable/Breezy receipts)
  are logged into the application's `confirmation.txt`, then trashed. Receipts arrive 1-3 minutes
  after a send, so `--settle 6` re-runs the pass every minute for up to 6 minutes, stops once every
  fresh send's receipt is trashed, and names any send whose receipt never came (some boards, e.g.
  Breezy, send none - say so in the report). Cleanup is part of every cycle, never an afterthought.
- **Handled job alerts**: every email in `profile/job_alerts/alerts.json` (written by `/job-alerts`) whose
  roles are all `sent`/`skipped` (or have a settled tracker row for the same posting: same URL, or
  same company and role dated on/after the alert), or that carries a `skip_reason` with no `drafted`
  role, is trashed and logged to `reports/mail-cleanup.log`, then dropped from the file. `ALERT still open`
  lines are roles not handled yet - a `drafted` role keeps its email until the user decides.
- **Rejections**: the matched tracker row is set to `status=rejected` with a
  dated note *before* the email is trashed - never the other way round, since the email is often
  the only record. No match or several matches: printed and left alone. Matching uses the
  **subject** only - a rejection worded only in the body (e.g. "Thank You for Your Interest in..."
  with the decision inside) won't match, so read anything ambiguous with
  `gmail_client.py read <id>` and handle a real rejection the same way by hand. This includes
  LinkedIn's "Your application to <role> at <company>" emails: while one is still in the inbox it is
  not recognised; once it is in the Bin, the Trash pass reads its body and files it.
- **"Your application was viewed by X"** pings matched to an
  applied/interview/offer row are trashed outright; unmatched ones are left alone.
- **Trash**: Gmail's Bin (last 14 days, newest 400) is read once per run; a
  real rejection the user trashed themselves sets its still-open row to `rejected` with a "found in
  Trash" note. Company AND role words must match, so multi-role companies are never filed on the
  wrong row; for LinkedIn-style subjects the company comes from the subject alone, because those
  emails end with a "Top jobs" block that names unrelated companies. A rejection already filed on
  its row is not flagged again while it sits in the Bin.
- **Receipt-shaped rejections**: "Thank you for your application to X" is also how many ATSs word a
  rejection, with the decision only in the body. Receipt bodies are read before anything is
  trashed, and one that reads like a rejection is kept and flagged (see below).

Dry run first when unsure: the same command without `--delete`.
One-off alert outside `alerts.json`:
`python3 tools/clean_confirmations.py --trash-alert <gmail id> --reason "<why>"`.

## Read the output - these lines need a human

- `TRASH needs eyes` - an interview invite, questionnaire or a person's reply sitting in the Bin.
- `TRASH rejection matched N open rows, ambiguous` and `TRASH rejection, role not confirmed`.
- `UNMATCHED (kept)`, `REJECTION, no open tracker row matched`, `REJECTION matched N open rows`,
  `ALERT has no roles recorded`, `ALERT looks like a person or an invite`, `ALERT has malformed roles`,
  `ALERTS file unreadable`, `receipt NOT seen`.
- `RECEIPT-SHAPED but the body reads like a rejection` - read it; file the row `rejected` if it is one.

Resolve each by hand and say what you did in the report. Do not skip reading the tool's output.

## Drafts the user already sent

Some mail clients send a fresh copy and leave the draft this kit saved in Drafts. Trash those:

```bash
python3 tools/gmail_client.py clean-drafts
```

It trashes only drafts whose thread has a later message in Sent Mail.

## Then look at the inbox

```bash
python3 tools/gmail_client.py search "in:inbox newer_than:3d" --limit 50
```

Anything job-related still there (a receipt, a rejection, an alert) is handled by hand or explained
in the report. "I ran the tool" is not done; a clean inbox is.

### The by-hand sweep

The tool misses mail whose decision is only in the body, and it ignores job-site noise, so after it
runs, list the job-related inbox (`search "in:inbox newer_than:30d" --limit 300`, skipping personal
senders) and clear it in the same turn, without being asked again:

- **Unmatched rejections** ("we decided to move forward with other candidates", or the same in the
  posting's language): read the body, set the tracker row to `rejected` with a dated note first,
  then `gmail_client.py trash <id>`. Ones the user trashed themselves are in the Bin: read them
  with `--trash`.
- **Job-site noise** (marketing from job boards, "accepted your invitation", old "new application"
  digests, recruiter-agency "thanks for choosing us" mail): trash.
- **Alert emails**: no role may stay `new` or `drafted` at the end of a cycle (`/cycle` step 4),
  so no alert email lingers.
- **Stays**: person threads only (recruiters, interviews, personal mail). Name each in the report.
- A finished process (a rejected interview, an expired take-home) is trashed too once the tracker
  row holds the outcome; keep the email only if a reply is still to be drafted (use
  `draft-reply --trash` if it is already in the Bin).
- Never list or read the user's own browser tabs to find a page; only touch a tab you opened,
  matched by its exact URL.
