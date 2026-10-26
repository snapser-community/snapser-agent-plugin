---
name: test-fleet-e2e
description: Deploy and test a game server fleet end-to-end on Snapser
---

# Skill: End-to-End Fleet Test

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
- Snapser CLI (`snapctl`) installed
- Docker installed and running
- A game server project with a Dockerfile (or willingness to scaffold one via `skills/byogs-publish/SKILL.md`)

## Full Workflow

### Phase 1 — Publish the game server image

Follow the `skills/byogs-publish/SKILL.md` skill to publish a game server image.

**Keep note of the image tag** used during the publish — you will need it in Phase 2.

If the user already has a published BYOGS image and knows the tag, skip this phase.

### Phase 2 — Prepare the test manifest

Use the pre-built sample manifest below (do NOT generate a manifest from scratch — use this exact template). For detailed fleet settings documentation, see `data/docs/infra/snaps/game-server-fleets/`. For post-create settings changes, use the Admin SDK (`skills/configure-snap-settings/SKILL.md`).

You need to modify three fields before creating the Snapend:

1. **`name`** (top level) — Pick a test Snapend name (max 20 chars, alphanumeric + dashes, starts with letter). Example: `fleet-test-1`
2. **`settings[1].data.fleets[0].image_tag`** — Set this to the **exact tag** from Phase 1. **Do NOT add any prefix** — use the tag exactly as passed to `--tag` during publish. For example, if you published with `--tag byogs-go-v1`, the value here must be `"image_tag": "byogs-go-v1"` — NOT `"byogs.byogs-go-v1"`, NOT `"snapser/byogs-go-v1"`, NOT any other prefixed form.
3. **`settings[1].data.fleets[0].name`** — Set a fleet name (e.g. `test-fleet`)
4. **`settings[1].data.fleets[0].port`** — Set the port your game server listens on

Write the modified manifest to a local file (e.g. `fleet-test-manifest.json`).

**Sample manifest:**

```json
{
  "version": "v1",
  "id": "z4zddcet",
  "name": "REPLACE_WITH_SNAPEND_NAME",
  "environment": "DEVELOPMENT",
  "service_definitions": [
    {
      "id": "auth",
      "language": "go",
      "version": "v1.5.0",
      "author_id": "snapser",
      "category": "SNAPSER",
      "subcategory": "SERVICE",
      "data_dependencies": [
        {
          "type": "POSTGRES",
          "postgres": {
            "database": "auth"
          }
        },
        {
          "type": "POSTGRES",
          "postgres": {
            "database": "auth_settings"
          }
        },
        {
          "type": "REDIS",
          "redis": {}
        }
      ]
    },
    {
      "id": "game-server-fleets",
      "language": "go",
      "version": "v1.7.0",
      "author_id": "snapser",
      "category": "SNAPSER",
      "subcategory": "FLEET",
      "data_dependencies": [
        {
          "type": "POSTGRES",
          "postgres": {
            "database": "game_server_fleets_settings"
          }
        },
        {
          "type": "REDIS",
          "redis": {}
        }
      ]
    }
  ],
  "settings": [
    {
      "id": "auth",
      "data": {
        "dev": {
          "anon": {
            "enabled": true
          },
          "api_keys": [],
          "app_auth": null,
          "app_verify": null,
          "apple": null,
          "disable_user_creation": false,
          "discord": null,
          "email": null,
          "email_password": null,
          "epic": null,
          "facebook": null,
          "fixed_rate_limiter_settings": [
            {
              "allow_list": [],
              "deny_list": [],
              "duration_in_seconds": 60,
              "limit": 5,
              "lockout_duration_in_seconds": 60,
              "type": "email_login"
            },
            {
              "allow_list": [],
              "deny_list": [],
              "duration_in_seconds": 60,
              "limit": 5,
              "lockout_duration_in_seconds": 60,
              "type": "email_verification"
            },
            {
              "allow_list": [],
              "deny_list": [],
              "duration_in_seconds": 60,
              "limit": 5,
              "lockout_duration_in_seconds": 60,
              "type": "account_recovery"
            }
          ],
          "google": null,
          "password": null,
          "session_inactivity_timeout": 604800,
          "session_token_validity": 2592000,
          "single_session_per_user": false,
          "steam": null,
          "user_auth_restrictions": [],
          "username_password": null,
          "x": null,
          "xbox": null
        },
        "email_templates": [],
        "prod": {
          "anon": null,
          "api_keys": [],
          "app_auth": null,
          "app_verify": null,
          "apple": null,
          "disable_user_creation": false,
          "discord": null,
          "email": null,
          "email_password": null,
          "epic": null,
          "facebook": null,
          "fixed_rate_limiter_settings": [
            {
              "allow_list": [],
              "deny_list": [],
              "duration_in_seconds": 60,
              "limit": 5,
              "lockout_duration_in_seconds": 60,
              "type": "email_login"
            },
            {
              "allow_list": [],
              "deny_list": [],
              "duration_in_seconds": 60,
              "limit": 5,
              "lockout_duration_in_seconds": 60,
              "type": "email_verification"
            },
            {
              "allow_list": [],
              "deny_list": [],
              "duration_in_seconds": 60,
              "limit": 5,
              "lockout_duration_in_seconds": 60,
              "type": "account_recovery"
            }
          ],
          "google": null,
          "password": null,
          "session_inactivity_timeout": 604800,
          "session_token_validity": 2592000,
          "single_session_per_user": false,
          "steam": null,
          "user_auth_restrictions": [],
          "username_password": null,
          "x": null,
          "xbox": null
        },
        "stage": {
          "anon": {
            "enabled": true
          },
          "api_keys": [],
          "app_auth": null,
          "app_verify": null,
          "apple": null,
          "disable_user_creation": false,
          "discord": null,
          "email": null,
          "email_password": null,
          "epic": null,
          "facebook": null,
          "fixed_rate_limiter_settings": [
            {
              "allow_list": [],
              "deny_list": [],
              "duration_in_seconds": 60,
              "limit": 5,
              "lockout_duration_in_seconds": 60,
              "type": "email_login"
            },
            {
              "allow_list": [],
              "deny_list": [],
              "duration_in_seconds": 60,
              "limit": 5,
              "lockout_duration_in_seconds": 60,
              "type": "email_verification"
            },
            {
              "allow_list": [],
              "deny_list": [],
              "duration_in_seconds": 60,
              "limit": 5,
              "lockout_duration_in_seconds": 60,
              "type": "account_recovery"
            }
          ],
          "google": null,
          "password": null,
          "session_inactivity_timeout": 604800,
          "session_token_validity": 2592000,
          "single_session_per_user": false,
          "steam": null,
          "user_auth_restrictions": [],
          "username_password": null,
          "x": null,
          "xbox": null
        }
      },
      "version": "v1.5.0",
      "exported_at": "1774413538"
    },
    {
      "id": "game-server-fleets",
      "data": {
        "fleets": [
          {
            "debug_port": 0,
            "description": "desc",
            "dev_profile": {
              "args": [],
              "buffer": "1",
              "cmd": "",
              "cpu": 100,
              "env_params": [],
              "max_replicas": 1,
              "memory": 0.125,
              "min_replicas": 1,
              "regions": [
                "oregon"
              ]
            },
            "fleet_deployments": [],
            "image_tag": "REPLACE_WITH_IMAGE_TAG",
            "name": "REPLACE_WITH_FLEET_NAME",
            "port": 7654,
            "prod_profile": {
              "args": [],
              "buffer": "1",
              "cmd": "",
              "cpu": 100,
              "env_params": [],
              "max_replicas": 1,
              "memory": 0.125,
              "min_replicas": 1,
              "regions": [
                "oregon"
              ]
            },
            "stage_profile": {
              "args": [],
              "buffer": "1",
              "cmd": "",
              "cpu": 100,
              "env_params": [],
              "max_replicas": 1,
              "memory": 0.125,
              "min_replicas": 1,
              "regions": [
                "oregon"
              ]
            },
            "status": "IN_PROGRESS"
          }
        ]
      },
      "version": "v1.7.0",
      "exported_at": "-62135596800"
    }
  ],
  "applied_configuration": ""
}
```

### Phase 3 — Create the Snapend

Create the Snapend using the modified manifest:

```bash
snapctl snapend create \
  --manifest-path-filename $pathToManifest \
  --blocking
```

**Always use `--blocking`** so the command waits until the Snapend is fully online before returning.

If the command fails, check the exit code against `skills/error_codes.md` and help the user recover.

Once the create completes, note the **Snapend ID** from the output — save it for reference.

### Phase 4 — Verify the fleet in the web app

After the Snapend comes up, ask the user to verify their fleet is running:

> Your Snapend is online. Please go to the **Snapser Web App**, navigate to your Snapend, and confirm that your fleet is listed and its status shows as running. You should see the fleet name and image tag you configured.

Wait for the user to confirm before proceeding.

If the user reports issues:
- **Fleet not visible** — The Snapend may still be provisioning the fleet. Ask them to wait a minute and refresh.
- **Fleet in error state** — Check the fleet configuration in the manifest (image tag, port) and verify the BYOGS image was published successfully. Inspect the live fleet settings to confirm they match what was configured:
  ```bash
  snapctl snap-config get-config --snaps game-server-fleets --snapend-id $snapendId
  ```
- **Snapend in error state** — Use `skills/snapend-status/SKILL.md` to diagnose.

### Phase 5 — Report results and next steps

If the fleet is confirmed running:
- Report success — the game server image was published, the Snapend was created, and the fleet is live.
- Provide the Snapend ID for their records.

Offer next steps:
- **Want to update the game server?** Publish a new image with a new tag via `skills/byogs-publish/SKILL.md`, then update the fleet configuration.
- **Want to clone this Snapend to staging?** → `skills/clone-snapend/SKILL.md`
- **Want to add more snaps?** → `skills/update-backend/SKILL.md`
- **Want to download the SDK?** → `skills/download-sdk/SKILL.md`

## Notes
- Be conversational — guide the user step by step, don't dump all commands at once.
- The manifest includes auth (always required) and game-server-fleets snaps with sensible defaults for dev.
- The three fields you MUST update in the manifest are: top-level `name`, `fleets[0].image_tag`, `fleets[0].name`, and optionally `fleets[0].port` if the user's game server uses a different port.
- Default port in the manifest is `7654` — confirm with the user if their game server uses a different port.
- If any step fails, explain the error clearly using `skills/error_codes.md` and offer to retry or adjust.
