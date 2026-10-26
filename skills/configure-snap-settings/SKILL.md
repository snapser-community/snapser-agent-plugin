---
name: configure-snap-settings
description: Configure snap settings on a live Snapend programmatically using the bundled Snapser Admin SDK
---

# Skill: Configure Snap Settings (Admin SDK)

The Admin SDK is the primary way to read and change snap settings — auth connectors,
leaderboards, storage keys, profiles, statistics, trackables, inventory, and more — on a
**live Snapend**. It replaces hand-editing manifest JSON: every operation is a typed,
runtime-validated method call, so there is no settings-block surgery and no
version-matching foot-guns.

The Python Admin SDK is **bundled with this plugin** at `data/admin-sdk/sdk-python`
(relative to the plugin root — two levels up from this skill file). No download is
needed. It is generated against the snap versions recorded in `data/admin-sdk/VERSION.md`.

## Trigger Phrases
- "enable anonymous login" / "add Google login" / "configure auth"
- "create a leaderboard" / "add a storage key" / "define profile attributes"
- "change snap settings" / "configure the <snap> snap"
- Any workflow step that says "delegate to configure-snap-settings"

## MANDATORY FIRST STEP — read the cheat sheet

Before writing ANY settings script, read
`skills/configure-snap-settings/config-cheatsheet.md`. It contains hard-won,
integration-tested gotchas — correct base URL, method naming, enum values,
PUT-vs-PATCH semantics, int64-as-string wire format, eventual-consistency polling,
and per-snap landmines. Skipping it is the main cause of first-attempt failures.

## The model

1. Settings changes are applied to the **live Snapend** via the bundled Python SDK.
   Do not download other SDK formats; Python is guaranteed present (snapctl requires it)
   and the SDK is pydantic v2 — every method is `@validate_call`-decorated, so wrong
   field names, types, or values fail locally before any HTTP request is sent.
2. **Optimistic-first:** do not pre-check snap versions or `has_admin` flags. Attempt
   the call with the bundled SDK; handle version mismatches only if the server rejects
   the call (see Error handling).
3. After **every** settings mutation, download the Snapend manifest to the **project
   root**. The manifest is the canonical, version-controllable record of the backend.
4. Setting values still need to make sense — the meaning of a setting is documented per
   snap in `data/docs/infra/snaps/<snap-name>/`, and the cheat sheet covers the
   practical constraints.

## Full Workflow

### Phase 1 — One-time environment setup (per project)

Create a venv **in the user's project** (never inside the plugin directory — it may be
a read-only cache) and install the bundled SDK from the plugin path:

```bash
python3 -m venv ./.snapser/venv
./.snapser/venv/bin/pip install --quiet <plugin-root>/data/admin-sdk/sdk-python
```

`<plugin-root>` is this plugin's directory on disk (the folder containing this
skill's `skills/` and `data/` directories). Recommend adding `.snapser/` to the
project's `.gitignore`.

### Phase 2 — Find the method and model

Read `snapser/api/<snap>_service_api.py` in the bundled SDK to find the method you
need. Methods are named `<snap>_<action>` — e.g. `auth_enable_anon_login`,
`leaderboards_create_leaderboard`, `storage_add_keys`. (There is NO `admin` infix in
method names.) Each call has the shape `<snap>_<action>(api_key, cluster_id, body=...)`:

- `api_key` — sent as an `Api-Key` header
- `cluster_id` — the **Snapend id** (the SDK is not tied to a Snapend; you pass it per call)
- `body` — a pydantic request model from `snapser/models/` where applicable; the
  environment scope (`dev`, `stage`, or `prod`) is usually a field on the body model

**Base URL resolution — always do this, in order:**

1. Check `~/.snapser/config` for a `PORTAL_ENDPOINT` entry (written by
   `snapctl login --portal-endpoint` for enterprise/private deployments), e.g.
   `PORTAL_ENDPOINT = https://gateway.snapser.poe-dev.scopely.com/snapser`.
   If present, the host is `{PORTAL_ENDPOINT}/v1/snapser-api/clusters` — the
   endpoint already includes the trailing `/snapser` segment.
2. If absent, use the bundled SDK's baked-in default
   (`https://gateway.snapser.com/snapser/v1/snapser-api/clusters` — the standard
   production gateway).

The example script below implements this resolution.

### Phase 3 — Write and run the script

Read the API key from `~/.snapser/config` at runtime (it's what `snapctl login`
stored). **Never hardcode the key in the script, and never echo or print it.**

Example — enable anonymous login on a dev Snapend:

```python
# ./.snapser/configure.py
import re
import sys
from pathlib import Path

from snapser import ApiClient, Configuration
from snapser.api.auth_service_api import AuthServiceApi
from snapser.models.auth_enable_anon_login_request import AuthEnableAnonLoginRequest

# Key + optional portal endpoint from ~/.snapser/config
config_text = (Path.home() / ".snapser" / "config").read_text()
api_key = re.search(r"SNAPSER_API_KEY\s*=\s*(\S+)", config_text).group(1)

# Base URL: PORTAL_ENDPOINT (enterprise) wins; else the SDK's baked-in default
portal = re.search(r"PORTAL_ENDPOINT\s*=\s*(\S+)", config_text)
config = (
    Configuration(host=f"{portal.group(1).rstrip('/')}/v1/snapser-api/clusters")
    if portal
    else Configuration()
)

snapend_id = sys.argv[1]  # pass the Snapend id on the CLI

auth = AuthServiceApi(ApiClient(config))
auth.auth_enable_anon_login(
    api_key=api_key,
    cluster_id=snapend_id,
    body=AuthEnableAnonLoginRequest(environment="dev"),
)
print("anonymous login enabled")
```

Run it:

```bash
./.snapser/venv/bin/python ./.snapser/configure.py $snapendId
```

Prefer `get`/`list` methods first (e.g. `auth_get_settings`) to read current state
before mutating, and re-read after mutating to confirm the change landed — remembering
the cheat sheet's note that deletes can be eventually consistent (poll briefly before
asserting). If a call raises a pydantic `ValidationError`, the request never left the
machine — fix the field/type named in the error and re-run.

### Phase 4 — MANDATORY: download the manifest to the project root

After every settings mutation (one download after a batch of related changes is fine):

```bash
snapctl snapend download --snapend-id $snapendId --category snapend-manifest --format json --out-path .
```

The manifest at the project root is the canonical record of the backend. Skipping this
step leaves the local manifest stale — and applying a stale manifest later will fail.

## Error handling

Work through these in order:

1. **pydantic ValidationError** — local input mistake; the request was never sent. Fix
   the field or type named in the error. Check the cheat sheet for the field's
   constraints (enums, required-on-PUT, `*_64` variants).
2. **404 "no Route matched"** — almost always the base URL missing the `/snapser`
   segment (Phase 2). Fix the host first.
3. **Other 404s / 400s with unknown-field or unknown-route flavor** — likely a snap
   version mismatch. The bundled SDK targets the snap versions in
   `data/admin-sdk/VERSION.md`. Check what's deployed:
   `snapctl snaps enumerate` + the Snapend's manifest `service_definitions[]`.
   - If deployed snaps are **older** than the SDK's target version → tell the user
     their snaps predate the current settings API and offer to upgrade:
     `skills/update-backend/SKILL.md` (`snapctl snapend-manifest upgrade` +
     `snapctl snapend apply --blocking`). Then retry the settings call.
   - If the user cannot or will not upgrade (deliberately pinned versions) → last
     resort: download an SDK matched to their deployed versions with
     `snapctl admin-sdk download --format python --snaps <name:vX.Y.Z,...> --out-path ./.snapser/`
     (only versions with `has_admin=true` are accepted; `v` prefix required), install
     it into the venv in place of the bundled SDK, and retry.
   - If the snap version has no admin support at all → direct the user to that snap's
     Config tool in the web portal (`data/docs/infra/snaps/<snap-name>/config-tools/`).
4. **HTTP 401/403** — the API key is invalid or lacks scope. Run `snapctl login`
   (it self-heals expired keys), then retry.
5. **HTTP 409** — duplicate resource name ("already exists"); read-modify or rename.
6. **502 / 5xx** — server-side; retry once, then report to the user. Do NOT retry
   repeatedly with payload variations (see the cheat sheet's import_catalog warning).

## Notes
- Batch related changes in one script run, then download the manifest once.
- The environment values inside settings calls are `dev`, `stage`, `prod` — lowercase,
  distinct from the Snapend environment names (DEVELOPMENT/STAGING/PRODUCTION).
- In Guide Mode, show the user the script and commands instead of running them.
