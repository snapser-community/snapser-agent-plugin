---
name: clone-snapend
description: Clone a Snapend to a new environment (dev to staging)
---

# Skill: Clone a Snapend to a New Environment

Clones an existing Snapend into a new environment — typically dev → dev, or dev → staging.
IMPORTANT: You cannot clone stage → prod. That can only be done via the web tool for security reasons.

## Trigger Phrases
- "clone my snapend"
- "promote my backend to staging"
- "I want to create a staging version of my backend"
- "clone my backend"

## Requirements
- Snapser CLI (`snapctl`) installed
- The user must have an existing Snapend to clone from. If they don't, guide them through `skills/create-backend/SKILL.md` first.

## Full Workflow

### Phase 1 — Identify the source Snapend

Ask the user which Snapend they want to clone.

If they don't remember the Snapend ID, run `snapctl snapend enumerate` to show all their Snapends and let them pick.

Confirm the Snapend ID exists in the enumerate output before proceeding.

Optionally, inspect the current snap settings on the source Snapend to understand what will be cloned:
```bash
snapctl snap-config get-config --snaps auth,leaderboards,storage --snapend-id $sourceSnapendId
```
This is especially useful if the user wants to verify configuration before promoting to a new environment.

### Phase 2 — Download the source manifest

Download the latest manifest from the source Snapend. **Always do this — never use a previously downloaded manifest.**

```bash
snapctl snapend download \
  --snapend-id $sourceSnapendId \
  --category snapend-manifest \
  --format json \
  --out-path .
```

Note the exact filename from the output (e.g. `snapser-$snapendId-manifest.json`).

### Phase 3 — Gather clone inputs

Ask the user:
- **Target environment** — `staging` or `development` if they want a second dev instance. Confirm this explicitly — cloning to the wrong environment is hard to undo.
- **New Snapend name** — must be max 20 characters, alphanumeric and dashes only, starts with a letter, unique in the target environment.

### Phase 4 — Clone the Snapend

Run the clone command:
```bash
snapctl snapend clone \
  --name $newSnapendName \
  --env $targetEnvironment \
  --manifest-path-filename $pathToManifest \
  --blocking
```

The `--blocking` flag ensures the command waits until the new Snapend is fully online. **Do not skip `--blocking`.**

Pass `--application-id $applicationId` if not already configured in your `~/.snapser/config`.

### Phase 5 — Confirm the clone

After the clone completes:
- Run `snapctl snapend enumerate` to verify the new Snapend is online in the target environment
- Report the new Snapend ID to the user — tell them to save it
- Immediately download the new Snapend's manifest to keep things in sync:
  ```bash
  snapctl snapend download \
    --snapend-id $newSnapendId \
    --category snapend-manifest \
    --format json \
    --out-path .
  ```

### Phase 6 — Next steps

Ask the user:
- **Want to download the SDK for the new environment?** Guide them through `skills/download-sdk/SKILL.md`.
- **Want to update the cloned Snapend?** Maybe they need different snap versions or configuration for staging/production. Guide them through `skills/update-backend/SKILL.md`.

## Notes
- **Always download a fresh manifest before cloning.** A stale manifest will cause the clone to fail.
- **Always re-download the manifest after a successful clone.** This keeps the local copy in sync.
- Be conversational — confirm the target environment before proceeding, as cloning to the wrong environment is a common mistake.
- If any step fails, explain the error clearly using `skills/error_codes.md` and offer to retry or adjust.
- Clone timeout errors (code 64) are common for large Snapends. Suggest retrying and checking status with `snapctl snapend enumerate`.
