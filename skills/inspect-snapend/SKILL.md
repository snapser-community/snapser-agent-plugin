---
name: inspect-snapend
description: Pull live logs, infrastructure metrics (CPU, memory, latency, RPS), and business metrics (DAU, MAU, installs, revenue) for a Snapend to diagnose issues or review performance
---

# Skill: Inspect a Snapend

Pulls live diagnostic data from a Snapend using `snapctl inspect` — deployment/snap/fleet
logs, infrastructure graphs (CPU, memory, latency, RPS, errors, restarts), and business
metrics (DAU, MAU, installs, revenue, locations). This mirrors the Logs, Monitor, and
Analytics tools in the Snapser web app, but from the terminal.

This skill is **read-only and diagnostic**. It never changes a Snapend's snaps, manifest,
or settings — if the user wants to fix something, use the relevant skill
(`skills/update-backend/SKILL.md`, `skills/configure-snap-settings/SKILL.md`) after
diagnosing with this one.

## Trigger Phrases
- "why is my snapend/backend failing/crashing/down?"
- "show me the logs for my snapend"
- "get me the CPU/memory/latency for my snapend"
- "is my snapend slow?"
- "what's my DAU/MAU/revenue/installs?"
- "diagnose my snapend"
- "debug my backend"
- "pull logs for an incident"
- "show me errors from the auth snap"
- "how many players logged in today?"

## Requirements
- Snapser CLI (`snapctl`) installed and configured
- A known Snapend id. If the user doesn't have one, use `skills/snapend-status/SKILL.md`
  (`snapctl snapend enumerate`) to find it first.
- `inspect metrics` additionally requires the Snapend to have the `analytics` snap. If it
  doesn't, tell the user and point them at `skills/update-backend/SKILL.md` to add it.
- `--application-id` is **not** required by any `inspect` subcommand — only `--snapend-id`.

## Full Workflow

### Phase 1 — Identify the Snapend

If the user hasn't given a Snapend id, list them:
```bash
snapctl snapend enumerate
```
Let the user pick one.

### Phase 2 — Route the question to the right subcommand

| The user is asking about... | Use |
|---|---|
| Snapend not coming up / pods failing / BYOSnap or BYOGS startup errors / SDK download errors | `inspect logs --category deployment` (the default category) |
| Errors from a specific snap or BYOSnap | `inspect logs --category snap --snaps <ids>` |
| Game server fleet issues | `inspect logs --category fleet`, filter with `--regions` and/or `--game-servers` |
| It's slow / high CPU / high memory / error rate / restarts | `inspect monitor` with the matching `--metric` |
| DAU / MAU / installs / revenue / player locations | `inspect metrics` (needs the `analytics` snap) |

If it's unclear which the user wants, ask — or start with `inspect logs --category deployment`
for a generally "unhealthy Snapend" report, since that's where the web app's own Logs tool
starts too.

### Phase 3 — Build the command

**Logs:**
```bash
# Defaults: --category deployment, --since 15m, --format text, --limit 5000
snapctl inspect logs --snapend-id $snapendId
snapctl inspect logs --snapend-id $snapendId --category snap --snaps auth --filter "error" --since 1h
snapctl inspect logs --snapend-id $snapendId --category fleet --regions frankfurt-ga --since 3h
```
- `--since` (e.g. `5m`, `15m`, `1h`, `12h`, `1d`) is simplest for "recent" questions; use
  `--start-time`/`--end-time` (ISO-8601) for an exact window, e.g. an incident review.
- Logs page oldest-first and keep the newest `--limit` lines (default 5000, max 50000). If
  the result includes `next_end_time`, older logs exist — tell the user and offer to re-run
  with `--start-time`/`--end-time` to page further back, like "Load more" in the web app.
- Use `--format json` (writes `.jsonl`, one JSON object per line) if the user wants to
  script against the output rather than read it directly.

**Monitor (infra graphs):**
```bash
# category=snap metrics: cpu, memory, latency, rps, errors, restarts, top-requests, top-snaps
# category=fleet metrics: cpu, memory, ingress-rate, egress-rate, ingress-total, egress-total
snapctl inspect monitor --snapend-id $snapendId --metric cpu --since 1h
snapctl inspect monitor --snapend-id $snapendId --metric rps --status-code 5xx --snaps auth,storage --since 3h
snapctl inspect monitor --snapend-id $snapendId --metric latency --quantile p99 --since 1d
```
- `cpu`/`memory` are a percentage of the limit; `latency` is in milliseconds.
- `--quantile` (p50/p75/p95/p99, default p95) only applies to `--metric latency`.
- `--status-code` (2xx/3xx/4xx/5xx) only applies to `--metric rps`.
- `--fleets` is required for `--category fleet`; `--regions`/`--game-servers` narrow further.
- Time range is capped at 30 days.

**Metrics (business):**
```bash
# $metric = dau, mau, installs, revenue, locations
snapctl inspect metrics --snapend-id $snapendId --metric dau
snapctl inspect metrics --snapend-id $snapendId --metric revenue --since 7d
```
- dau/installs/revenue are per day, mau is per month, locations has no timestamp (it's a
  count of logins per location).
- Default `--since` is 30d for metrics (vs. 15m for logs/monitor); time range is capped at
  30 days either way.

All three subcommands accept `--out-path-filename` for a `.json`/`.csv` (monitor, metrics)
or `.log`/`.jsonl` (logs) file — remember this is `--out-path-filename` (full path +
filename), the same flag family as the manifest commands, **not** `--out-path` like
`snapend download`. Don't default these exports into the project root — they're ad-hoc
diagnostic snapshots, not canonical backend state like a manifest. Ask the user where they
want it saved, or just let snapctl write its default-named file in the current directory.

### Phase 4 — Present the results

- **Logs:** summarize what's in the file rather than dumping it — call out error lines,
  crash loops, or repeated failures you spot, and mention the file path.
- **Monitor/Metrics (JSON):** don't paste raw JSON at the user. Summarize the trend (e.g.
  "CPU on the auth snap averaged 40%, peaking at 78% around 14:00 UTC") and mention the
  saved file path if `--out-path-filename` was used.
- If a log result had `next_end_time`, say so and offer to page further back.

### Phase 5 — Errors

`snapctl inspect` exit codes: `122` generic, `123` logs, `124` monitor, `125` metrics. Look
these up in `skills/error_codes.md` for recovery guidance.

## Notes
- This is read-only — never a reason to touch the manifest or settings. If diagnosis points
  to a real fix (bad setting, missing snap), hand off to
  `skills/configure-snap-settings/SKILL.md` or `skills/update-backend/SKILL.md`.
- Time range for `monitor` and `metrics` is capped at 30 days; `logs` has no such cap but
  defaults to a 5000-line (max 50000) window per call.
- For broader "is my Snapend healthy" triage before drilling into logs/metrics, start with
  `skills/snapend-status/SKILL.md`.
