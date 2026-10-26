---
name: update-backend
description: Add, remove, or update snaps on an existing Snapend
---

# Skill: Update or Upgrade an Existing Snapend

Guides the developer through modifying an existing Snapend — adding or removing snaps,
upgrading snap versions, or enabling/disabling features like WebSockets.

## Trigger Phrases
- "update my snapend"
- "add a snap to my backend"
- "remove a snap from my backend"
- "upgrade my snaps"
- "update my backend"
- "I want to change the snaps on my snapend"
- "enable websockets on my snapend"

## Requirements
- Snapser CLI (`snapctl`) installed and configured
- The user must have an existing Snapend. If they don't, guide them through `skills/create-backend/SKILL.md` first.

## Full Workflow

### Phase 1 — Identify the target Snapend

Ask the user for the **Snapend ID** they want to update.

If they don't remember it, run `snapctl snapend enumerate` to list all their Snapends and let them pick.

Once the user provides a Snapend ID, confirm it exists in the enumerate output before proceeding. If it doesn't match, let the user know and ask them to double-check.

### Phase 1b — Inspect current snap configuration (optional)

If you need to understand how a specific snap is currently configured before making changes, use:
```bash
snapctl snap-config get-config --snaps $snapIds --snapend-id $snapendId
```
This returns the live settings for the requested snaps without downloading the full manifest. Useful for quickly checking what auth methods are enabled, what leaderboards exist, etc.

### Phase 2 — Download the current manifest

Download the latest manifest for the target Snapend. This ensures we're working with the current state — **never skip this step**.

```bash
snapctl snapend download \
  --snapend-id $snapendId \
  --category snapend-manifest \
  --format json \
  --out-path .
```

This saves a manifest file (e.g. `snapser-$snapendId-manifest.json`) in the current directory. Note the exact filename from the output — you'll need it in the next steps.

### Phase 3 — Determine what the user wants to change

Ask the user what they'd like to do. The options are:

**Option A — Add or remove snaps (and/or features):**
Use the `snapctl snapend-manifest update` command.

**Option B — Upgrade existing snaps to the latest version:**
Use the `snapctl snapend-manifest upgrade` command.

The user can also combine both — upgrade first, then add/remove. Handle them in sequence if needed.

### Phase 4 — Validate snap names

Before modifying the manifest:
- Run `snapctl snaps enumerate` to get the current snap catalog
- Verify that every snap the user wants to add or upgrade exists in the catalog
- **Exception:** If a snap name starts with `byosnap-`, it's the user's own BYOSnap — no need to validate it against the snap catalog
- If a snap name doesn't match, let the user know and suggest the closest match

### Phase 5 — Modify the manifest

**For adding/removing snaps or features (Option A):**
```bash
snapctl snapend-manifest update \
  --manifest-path-filename $downloadedManifest \
  --add-snaps $addSnaps \
  --remove-snaps $removeSnaps \
  --add-features $addFeatures \
  --remove-features $removeFeatures \
  --out-path-filename ./snapend-updated-manifest.json
```
Only include the flags that apply. At least one of `--add-snaps`, `--remove-snaps`, `--add-features`, or `--remove-features` is required.

**IMPORTANT:** The `--add-snaps` and `--remove-snaps` flags accept **both** Snapser snaps and BYOSnaps in the same comma-separated list. Do NOT use a separate command to add BYOSnaps. For example: `--add-snaps leaderboards,byosnap-my-service` is correct. This also applies to `snapctl snapend-manifest sync`.

Note: Additions are performed before removals. If the user needs strict input-to-output mapping, use `snapctl snapend-manifest sync` instead.

**For upgrading snap versions (Option B):**
```bash
# Upgrade specific snaps
snapctl snapend-manifest upgrade \
  --manifest-path-filename $downloadedManifest \
  --snaps $snapsToUpgrade \
  --out-path-filename ./snapend-updated-manifest.json

# Or upgrade ALL snaps to latest versions (omit --snaps)
snapctl snapend-manifest upgrade \
  --manifest-path-filename $downloadedManifest \
  --out-path-filename ./snapend-updated-manifest.json
```

If the user wants to upgrade all snaps, omit the `--snaps` flag. If they want to upgrade specific snaps only, pass a comma-separated list.

### Phase 5b — Configure settings for newly added snaps

Settings are NOT configured in the manifest. **Never** edit or script the manifest to
add a settings block — no `python`, `jq`, `sed`, or here-doc, and not even a block
grounded in the Admin SDK source or config docs. The manifest here is only ever
modified by the `snapctl snapend-manifest` commands in Phase 5. Apply the manifest
first (Phase 6) so the new snaps are live, then configure their settings via the Admin
SDK — follow `skills/configure-snap-settings/SKILL.md` (gather what the user wants now;
apply in Phase 6b). Structure and settings are two separate phases — never combine them.

If only removing snaps or upgrading versions (no new snaps added), skip this phase.

### Phase 6 — Apply the updated manifest

Apply the modified manifest to the Snapend:
```bash
snapctl snapend apply \
  --manifest-path-filename ./snapend-updated-manifest.json \
  --blocking
```

The `--blocking` flag ensures the command waits until the Snapend is fully updated and online. **Do not skip `--blocking`** — subsequent steps may fail if the Snapend isn't ready.

### Phase 6b — Apply settings and re-download the manifest

If new snaps need configuration (from Phase 5b), follow
`skills/configure-snap-settings/SKILL.md` against the now-updated Snapend. When done —
or after ANY mutation in this workflow — download the fresh manifest to the project
root:
```bash
snapctl snapend download --snapend-id $snapendId --category snapend-manifest --format json --out-path .
```

### Phase 7 — Confirm the update

After the apply completes, verify the Snapend is online:
- Run `snapctl snapend enumerate` to check the Snapend status
- Let the user know which snaps were added, removed, or upgraded

Then immediately download the fresh manifest to keep things in sync for future updates:
```bash
snapctl snapend download \
  --snapend-id $snapendId \
  --category snapend-manifest \
  --format json \
  --out-path .
```

### Phase 8 — Next steps

Ask the user:
- **Want to download an updated SDK?** The SDK may have changed if snaps were added or removed. Run `snapctl snapend download --snapend-id $snapendId --category sdk`.
- **Want to add a custom microservice?** Guide them through `skills/create-byosnap/SKILL.md`.
- **Want to deploy a BYOSnap?** Guide them through `skills/direct-deploy-byosnap/SKILL.md`.

## Notes
- **Always download the latest manifest before modifying it.** Applying a stale manifest will fail.
- **Always re-download the manifest after a successful apply.** This keeps your local copy in sync.
- Be conversational — guide the user step by step, don't dump all commands at once.
- If any step fails, explain the error clearly using `skills/error_codes.md` and offer to retry or adjust.
- The auth snap cannot be removed — it is mandatory on every Snapend.
