---
name: snapend-status
description: Check the health, state, and details of a Snapend
---

# Skill: Check Snapend Status

Checks the health and state of a Snapend — useful for diagnosing issues, verifying
deployments, or confirming a Snapend is online after an operation.

## Trigger Phrases
- "is my snapend running?"
- "check my snapend status"
- "what state is my backend in?"
- "is my backend online?"
- "my snapend isn't working"
- "check if my snapend is healthy"
- "list my snapends"
- "show me my backends"

## Requirements
- Snapser CLI (`snapctl`) installed and configured

## Full Workflow

### Phase 1 — Identify the Snapend

Ask the user which Snapend they want to check. If they want to see all their Snapends,
or don't remember the ID, start with listing everything.

**Option A — List all Snapends:**
Run:
```bash
snapctl snapend enumerate
```

Present the results to the user in a readable format — show the Snapend name, ID,
environment, and current state for each one.

**Option B — Check a specific Snapend:**
If the user provides a Snapend ID, get its detailed state:
```bash
snapctl snapend state $snapendId
```

### Phase 2 — Interpret and explain the state

After retrieving the status, explain to the user what it means:

- **RUNNING / ONLINE** — The Snapend is healthy and serving traffic. Everything is working.
- **CREATING / PROVISIONING** — The Snapend is being set up. This is expected after a create or clone. Ask the user to wait and check again shortly.
- **UPDATING** — An update is in progress (e.g. adding/removing snaps). Expected after an apply or update command. Wait for it to complete.
- **ERROR / FAILED** — Something went wrong. Check the error details and suggest recovery steps.
- **UNKNOWN** — The state couldn't be determined. Suggest retrying or checking the Snapser web portal.

If the Snapend is in an error state, help diagnose:
- Check recent operations (did a create/apply/clone fail?)
- Verify the manifest was valid
- Check error codes against `skills/error_codes.md`
- Inspect specific snap settings to verify they're configured correctly:
  ```bash
  snapctl snap-config get-config --snaps auth,leaderboards --snapend-id $snapendId
  ```
  This pulls the live settings for specific snaps — useful for verifying auth methods are enabled, leaderboards are defined, storage keys exist, etc.

### Phase 3 — Offer follow-up actions

Based on the status, suggest relevant next steps:
- **If healthy** — "Your Snapend is running. Want to update it, download an SDK, or deploy a BYOSnap?"
- **If still creating/updating** — "It's still provisioning. Let's wait and check again in a minute."
- **If failed** — "There's an issue" Report the error.
- **If user wants to see more detail** — Offer to download the current manifest for the Snapend to inspect its configuration.

## Notes
- This is often the first thing a user asks when something isn't working. Be helpful and diagnostic.
- If the user has multiple Snapends, present them in a clear table or list format.
- If any step fails, explain the error clearly using `skills/error_codes.md`.
