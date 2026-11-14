# /patterns - Where applications go and what comes back

Reads `profile/tracker.csv` and shows outcome rates by fit band, role type, channel (where the
lead was found) and ATS / posting site. It answers "what is working and what is wasting sends?".
Idea from career-ops' `patterns` mode. It never edits the tracker or the evaluation framework;
changing a threshold or a standing rule is the user's decision.

## Step 1: Run the report

```bash
python3 tools/patterns.py            # --min 5 (smallest group shown), --silent-days 30
```

Statuses are read with `/outcome`'s **Tracker status vocabulary**: `interview`, `offer`, `hired`
and `offer_declined` count as positive, `rejected` as negative, and an `applied` / `no_response`
row older than `--silent-days` as silent. `drafted` and `withdrawn` rows were never sent and are
left out. Labels are normalized on read by `tools/tracker_labels.py`, so an old free-text row
still lands in its group.

## Step 2: Read it back to the user

Lead with the one or two findings that would change what they do, then the tables. Rules:

- **Report yield, never cause.** "LinkedIn Easy Apply rejects 51% and has produced no interview"
  is a fact; "LinkedIn's filter is biased against you" is not something one tracker can show.
  Say the group size every time and call anything under ~20 sends "too few to say".
- **Interviews are the signal, rejections the noise.** A high rejection rate with fast replies
  can be healthier than a low one that is all silence. Look at interview counts first.
- **Fit cutoff.** The script only suggests one once there are 5+ interviews. Below that, say so
  and say what the fit score is (or is not) separating today. Do not invent a cutoff.
- End with at most three concrete suggestions (drop a channel, raise the bar for a role type,
  stop applying below a fit band), each tied to a number in the report. Never apply them
  yourself: the user decides, and the rules in `profile/deal-breakers.md` stand until they
  change them.

## Step 3: Clean labels

If rows show up under `other` or a label that is not in `tools/tracker_labels.py`, rewrite the
columns with `python3 tools/tracker_labels.py --apply` (dry run without the flag). It only
touches `role_type` and `channel`. The default role families cover common tech, design, product
and data roles; for another field, add the user's own families to `profile/role_types.txt`, one
`<label> <regex>` per line (tried first, in order).
