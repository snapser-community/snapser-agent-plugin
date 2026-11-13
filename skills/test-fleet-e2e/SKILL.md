---
name: test-fleet-e2e
description: Deploy and test a game server fleet end-to-end on Snapser
---

# Skill: End-to-End Fleet Test

> **Before you start:** read `${CLAUDE_PLUGIN_ROOT}/skills/core-rules.md` if you have
> not read it in this session. It holds the prerequisite check and the rules that
> apply to every Snapser workflow.
>
> All `skills/` and `data/` paths in this file start at the plugin root,
> `${CLAUDE_PLUGIN_ROOT}`. If that value is not an absolute path, the plugin root is
> the folder two levels above this file.

Tests that a game server fleet is working end-to-end on a Snapend — from publishing the
game server image, to creating a Snapend with a fleet, to verifying it comes online.

## Trigger Phrases
- "test my game server fleet"
- "verify my fleet is working"
- "end to end fleet test"
- "is my game server running?"
- "test byogs end to end"
- "I want a game server fleet"
- "set up game server hosting"
- "deploy a game server"
- "help me with game server fleets"
- "create a fleet for my game server"
- "I need game server hosting"
- "get a game server fleet running"

## Requirements
- Snapser CLI (`snapctl`) installed and configured
- Docker installed and running
- A game server project with a Dockerfile (or willingness to scaffold one via `skills/byogs-publish/SKILL.md`)

## Full Workflow

### Phase 1 — Publish the game server image

Follow the `skills/byogs-publish/SKILL.md` skill to publish a game server image.

**Keep note of the image tag** used during the publish — you will need it in Phase 3.

If the user already has a published BYOGS image and knows the tag, skip this phase.

### Phase 2 — Create the Snapend (structure)

The Snapend comes first, with no settings. The fleet is a **setting** — you create it in
Phase 3, on the live Snapend. Do NOT write or edit manifest JSON, and do NOT put a fleet
or any other settings block into the manifest (see the HARD RULE in
`skills/core-rules.md`).

1. Ask for a test Snapend name (max 20 chars, alphanumeric + dashes, starts with a
   letter). Example: `fleet-test-1`

2. Generate the base manifest with `auth` and `game-server-fleets`:
```bash
snapctl snapend-manifest create \
  --name $snapendName \
  --env DEVELOPMENT \
  --snaps auth,game-server-fleets \
  --out-path-filename ./$snapendName-manifest.json
```

3. Create the Snapend from the generated manifest. Do not edit the manifest first:
```bash
snapctl snapend create \
  --manifest-path-filename ./$snapendName-manifest.json \
  --application-id $applicationId \
  --blocking
```
**Always use `--blocking`** so the command waits until the Snapend is fully online.
Omit `--application-id` only if `SNAPSER_APPLICATION_ID` is set in the Snapser config.

4. If the create times out (exit code 79), the Snapend is still provisioning. Check
   status with `snapctl snapend enumerate` and wait for it to come online. For any other
   failure, check the exit code against `skills/error_codes.md`.

5. Note the **Snapend ID** from the output — you need it in every later step.

### Phase 3 — Create the fleet (settings, via the Admin SDK)

Create the fleet on the live Snapend with the bundled Admin SDK. Follow
`skills/configure-snap-settings/SKILL.md` for the environment setup, the API key, and
the base URL — and read its cheat sheet first. The fleet-specific part of the script is:

```python
from snapser.api.game_server_fleets_service_api import GameServerFleetsServiceApi
from snapser.models.game_server_fleets_create_fleet_request import GameServerFleetsCreateFleetRequest
from snapser.models.game_server_fleets_fleet_profile import GameServerFleetsFleetProfile


def profile():
    # Smallest hardware profile — enough for a test fleet
    return GameServerFleetsFleetProfile(
        buffer="1", cpu=100, memory=0.125, min_replicas=1, max_replicas=1,
        regions=["oregon"],
    )


fleets = GameServerFleetsServiceApi(ApiClient(config))
fleets.game_server_fleets_create_fleet(
    api_key=api_key,
    cluster_id=snapend_id,
    body=GameServerFleetsCreateFleetRequest(
        name=fleet_name,          # e.g. "test-fleet"
        description="Fleet end-to-end test",
        image_tag=image_tag,      # the exact tag from Phase 1
        port=port,                # the port the game server listens on
        dev_profile=profile(),
        stage_profile=profile(),
        prod_profile=profile(),
    ),
)
```

Set these values from the user's input:

- **`image_tag`** — the **exact tag** from Phase 1. **Do NOT add any prefix** — use the
  tag exactly as passed to `--tag` during publish. If the user published with
  `--tag byogs-go-v1`, the value is `"byogs-go-v1"` — NOT `"byogs.byogs-go-v1"`, NOT
  `"snapser/byogs-go-v1"`, NOT any other prefixed form.
- **`name`** — the fleet name, unique per Snapend, 1-25 characters from `[a-z0-9-_]`
  (e.g. `test-fleet`).
- **`port`** — the port the game server listens on. Ask the user; do not guess it.
- **`regions`** — default to the standard region `oregon`. The valid region ids are in
  `data/docs/infra/snaps/game-server-fleets/index.mdx`. Do not pick a protected region
  (an id that ends in `-ga`) for this test unless the user asks — a protected region pins
  the fleet's ports to `7777` and `7778`.

All three profiles (`dev_profile`, `stage_profile`, `prod_profile`) are required, and
each profile requires `buffer` and `regions`. For what the other fleet settings mean,
read `data/docs/infra/snaps/game-server-fleets/config-tools/fleets.mdx`.

### Phase 4 — Download the manifest

The fleet is a settings change, so download the manifest to the project root —
MANDATORY:
```bash
snapctl snapend download \
  --snapend-id $snapendId \
  --category snapend-manifest \
  --format json \
  --out-path .
```

### Phase 5 — Verify the fleet

1. Read the fleet back with the Admin SDK and check its status:
```python
fleet = fleets.game_server_fleets_get_fleet(
    fleet_name=fleet_name, api_key=api_key, cluster_id=snapend_id,
).fleet
print(fleet.status)
for d in fleet.fleet_deployments or []:
    print(d.region, d.fleet_deployment_status)
```
   - `IN_PROGRESS` — the fleet is still deploying. Wait a minute and read it again.
   - `LIVE` — the fleet is up.
   - `FAILED` — see the issues list below.

2. Ask the user to confirm in the web app:

> Your Snapend is online and the fleet is created. Please go to the **Snapser Web App**, navigate to your Snapend, and confirm that your fleet is listed and its status shows as running. You should see the fleet name and image tag you configured.

Wait for the user to confirm before proceeding.

If there are issues:
- **Fleet not visible** — The Snapend may still be provisioning the fleet. Ask the user to wait a minute and refresh.
- **Fleet in error state** — Check the image tag and port, and verify the BYOGS image was published successfully. Inspect the live fleet settings:
  ```bash
  snapctl snap-config get-config --snaps game-server-fleets --snapend-id $snapendId
  ```
  For fleet logs, use `skills/inspect-snapend/SKILL.md` (`snapctl inspect logs --category fleet`).
- **Snapend in error state** — Use `skills/snapend-status/SKILL.md` to diagnose.

### Phase 6 — Report results and next steps

If the fleet is confirmed running:
- Report success — the game server image was published, the Snapend was created, and the fleet is live.
- Provide the Snapend ID for their records.

Offer next steps:
- **Want to update the game server?** Publish a new image with a new tag via `skills/byogs-publish/SKILL.md`, then update the fleet through the Admin SDK (`skills/configure-snap-settings/SKILL.md`).
- **Want players to log in?** Enable an auth method, e.g. anonymous login → `skills/configure-snap-settings/SKILL.md`
- **Want to clone this Snapend to staging?** → `skills/clone-snapend/SKILL.md`
- **Want to add more snaps?** → `skills/update-backend/SKILL.md`
- **Want to download the SDK?** → `skills/download-sdk/SKILL.md`

## Notes
- Be conversational — guide the user step by step, don't dump all commands at once.
- The Snapend has `auth` (always required) and `game-server-fleets`. The fleet itself is a setting, created through the Admin SDK after the Snapend is live — never through the manifest.
- The values you MUST get from the user are the Snapend name, the image tag, the fleet name, and the game server port.
- In Guide Mode, show the user the commands and the script instead of running them.
- If any step fails, explain the error clearly using `skills/error_codes.md` and offer to retry or adjust.
