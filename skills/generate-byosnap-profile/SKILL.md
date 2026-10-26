---
name: generate-byosnap-profile
description: Generate or edit a snapser-byosnap-profile.json file
---

# Skill: Generate or Edit a BYOSnap Profile

Generates a new BYOSnap profile (`snapser-byosnap-profile.json`) from scratch or helps
the user modify an existing one. The profile defines the BYOSnap's metadata, ingress,
health check, and resource allocation for each environment.

## Trigger Phrases
- "generate a byosnap profile"
- "create a byosnap profile"
- "I need a snapser-byosnap-profile.json"
- "edit my byosnap profile"
- "change the CPU on my byosnap"
- "update my byosnap's memory"
- "fix my byosnap profile"
- "my byosnap profile is invalid"

## Requirements
- Snapser CLI (`snapctl`) installed

## Full Workflow

### Phase 1 — Determine if generating new or editing existing

Ask the user:
- **Do they already have a profile?** If yes, ask for the path and read it. Skip to Phase 3 to help them edit specific fields.
- **Starting fresh?** Continue to Phase 2.

### Phase 2 — Generate a base profile

Use snapctl to generate a base profile file:
```bash
snapctl byosnap generate-profile \
  --out-path $projectPath \
  --profile-filename snapser-byosnap-profile.json
```

This creates a template profile with default values. Now gather the user's inputs to populate it properly.

### Phase 3 — Gather inputs and set profile fields

Walk the user through each section of the profile. Ask about the fields that matter — don't overwhelm them with everything at once.

**Basic info (always ask):**
- `name` — Display name for the BYOSnap (max 50 characters)
- `description` — Brief description of what the microservice does
- `language` — Programming language used (e.g. `go`, `python`, `node`, `csharp`)

**Platform (ask if unsure):**
- `platform` — Either `linux/arm64` (default) or `linux/amd64`. If the user is on an M-series Mac, default to `linux/arm64`. If on Intel or deploying to amd64, use `linux/amd64`.

**Ingress (ask about port):**
- `prefix` — Always `/v1`. Do not change this.
- `ingress.external_port.port` — The port the microservice listens on. Default is `5003`. Must match what the code actually binds to.
- `ingress.internal_ports` — Usually empty (`[]`). Only needed for inter-service communication on non-standard ports.

**Health check (ask about endpoint):**
- `readiness_probe_config.path` — The health check endpoint path (e.g. `/healthz`). This must exist in the code and return 200 when healthy.
- `readiness_probe_config.initial_delay_seconds` — How long to wait before the first health check. Default `5`. Increase if the service takes longer to start.

**Resource allocation per environment (use defaults unless user specifies):**

Each environment (dev, staging, production) has its own template with these fields:

| Field | Description | Supported values | Default |
|-------|-------------|------------------|---------|
| `cpu` | CPU allocation (millicores) | 100, 250, 500, 750, 1000, 1500, 2000, 3000 | 100 |
| `memory` | Memory allocation (GB) | 0.125, 0.25, 0.5, 1, 2, 3, 4 | 0.125 |
| `min_replicas` | Minimum running instances | 1+ | 1 (dev/stage), 2 (prod) |
| `cmd` | Override container CMD | string | `""` (use Dockerfile CMD) |
| `args` | Override container args | string array | `[]` |
| `env_params` | Environment variables | key/value pairs | `SNAPSER_ENVIRONMENT` set per env |

**Sensible defaults:**
- For **development**: cpu 100, memory 0.125, 1 replica
- For **staging**: cpu 100, memory 0.125, 1 replica
- For **production**: cpu 100, memory 0.125, 2 replicas (minimum for high availability)

Only ask the user about resource allocation if they mention performance concerns or have specific requirements. Otherwise, use the defaults.

### Phase 4 — Write the profile

After gathering inputs, write the complete profile file. The full schema:

```json
{
    "name": "<name>",
    "description": "<description>",
    "platform": "linux/arm64",
    "language": "<language>",
    "prefix": "/v1",
    "ingress": {
        "external_port": {
            "name": "http",
            "port": 5003
        },
        "internal_ports": []
    },
    "readiness_probe_config": {
        "initial_delay_seconds": 5,
        "path": "/healthz"
    },
    "dev_template": {
        "cpu": 100,
        "memory": 0.125,
        "min_replicas": 1,
        "cmd": "",
        "args": [],
        "env_params": [
            { "key": "SNAPSER_ENVIRONMENT", "value": "DEVELOPMENT" }
        ]
    },
    "stage_template": {
        "cpu": 100,
        "memory": 0.125,
        "min_replicas": 1,
        "cmd": "",
        "args": [],
        "env_params": [
            { "key": "SNAPSER_ENVIRONMENT", "value": "STAGING" }
        ]
    },
    "prod_template": {
        "cpu": 100,
        "memory": 0.125,
        "min_replicas": 2,
        "cmd": "",
        "args": [],
        "env_params": [
            { "key": "SNAPSER_ENVIRONMENT", "value": "PRODUCTION" }
        ]
    }
}
```

Save the file at the project root (or resources folder if the user prefers).

### Phase 5 — Validate the profile

Always validate after generating or editing:
```bash
snapctl byosnap validate-profile --path $projectPath
```

If validation fails, read the error message, explain what's wrong, fix the profile, and re-validate.

### Phase 6 — Next steps

Ask the user:
- **Want to create a BYOSnap from scratch?** Guide them through `skills/create-byosnap/SKILL.md`.
- **Want to direct-deploy?** Guide them through `skills/direct-deploy-byosnap/SKILL.md`.
- **Want to publish?** Guide them through `skills/publish-byosnap/SKILL.md`.

## Notes
- The profile supports both `.json` and `.yaml` formats. Default to JSON unless the user prefers YAML.
- `prefix` should always be `/v1` — do not change this.
- The `env_params` for each template should always include `SNAPSER_ENVIRONMENT` with the correct value for that environment. Users can add additional env vars alongside it.
- Be conversational — if the user just wants to change one field (e.g. "bump my CPU to 500"), read the existing profile, change that field, save, and validate. Don't make them re-enter everything.
- If any step fails, explain the error clearly using `skills/error_codes.md`.
