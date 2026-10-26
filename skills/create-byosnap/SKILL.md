---
name: create-byosnap
description: Create a custom BYOSnap microservice from scratch
---

# Skill: Create a BYOSnap (Custom Microservice)

Guides the developer through creating a new custom microservice (BYOSnap) from scratch,
including project scaffolding, required files, and optional deployment.

## Trigger Phrases
- "create a byosnap"
- "initialize a byosnap"
- "build a custom microservice"
- "I want to write my own microservice"
- "scaffold a byosnap"

## Requirement
- This skill needs the Snapser CLI tool (`snapctl`)
- The community examples repo (use the `core/` scaffolds): https://github.com/snapser-community/snapser-byosnaps/tree/main/core

## Full Workflow

### Phase 1 — Gather inputs from the user
Ask the user:
- What **programming language** do they want to use for the microservice?
- What **BYOSnap ID** do they want? (Must start with `byosnap-`. Validate this before proceeding.)
- What **name** for the BYOSnap? (Max 50 characters)
- A brief **description** of what the microservice does

### Phase 2 — Scaffold the project

Snapser has a community repo with BYOSnap scaffolds. **Always start from the `core/` directory** — minimal starter scaffolds, one per supported language, with everything Snapser expects already wired up (auth middleware, health check, CORS, config/import-export/user-data hooks, custom dashboard tools, SDK generation) and every handler body stubbed with a `// TODO`:

| Language | Framework | Folder |
| --- | --- | --- |
| Python | Flask | `core/byosnap-python` |
| Go | Gorilla Mux | `core/byosnap-go` |
| Node (TypeScript) | Express + tsoa | `core/byosnap-node-ts` |
| C# | ASP.NET Core | `core/ByoSnapCSharp` |
| Rust | actix-web | `core/byosnap-rust-api` |
| Java | Spring Boot | `core/byosnap-java` |
| Kotlin | Ktor | `core/byosnap-kotlin` |

Every example is functionally identical across languages — same routes, same auth model, same tools. (The repo's `basic/`, `inter/`, and `advanced/` directories exist for the documentation tutorials — do not scaffold from them.)

**IMPORTANT: You MUST use `git clone` to get the example code. Do NOT fetch individual files via curl, wget, or any HTTP requests. Do NOT spawn an agent to download files. Just clone the repo with the single command below.**

1. Clone the community repo:
   ```bash
   git clone --depth 1 https://github.com/snapser-community/snapser-byosnaps.git
   ```

2. Copy the matching example to a new directory named after the user's BYOSnap ID:
   ```bash
   # Example for Go — adjust the source path based on the user's language choice
   cp -r snapser-byosnaps/core/byosnap-go ./$byosnapId
   ```

3. Remove the cloned repo — we only need the copied example:
   ```bash
   rm -rf snapser-byosnaps
   ```

4. If the user's language does **not** match any of the seven examples, copy the closest example as a reference, then rewrite it in the user's chosen language, keeping the same route coverage and auth model.

5. **Rename the Snap id in the copied code.** The core scaffolds use `byosnap-core` as the BYOSnap identifier, defined as a **single constant** (e.g. `constants.go` in Go) that drives every route prefix. Change that one constant to the user's actual BYOSnap ID — routes move from `/v1/byosnap-core/...` to `/v1/$byosnapId/...` automatically. Also update `snapser-resources/snapser-byosnap-profile.json` (name, description, language).

**Note — Eventbus is OPTIONAL, not a requirement.** The core scaffolds include best-effort Eventbus stubs (`registerEventTypes()` on startup, a `publishEvent()` helper, and a reserved `POST /internal/events` receiver). These are safe no-ops when the eventbus snap is not in the Snapend — failures are logged and swallowed. Do NOT add the `eventbus` snap to a Snapend just because a BYOSnap is present; only add it if the user explicitly wants realtime events/webhooks. A minimal BYOSnap Snapend is `auth` + the BYOSnap.

### Phase 3 — Ensure all required files are present

Every BYOSnap **must** have these files (at the project root or in a resources folder like `snapser-resources/`):

**1. BYOSnap Profile (`snapser-byosnap-profile.json`)**

Generate this using the user's inputs. Here is the full schema with annotations:

```json
{
    "name": "<user-provided name, max 50 chars>",
    "description": "<user-provided description>",
    "platform": "linux/arm64",
    "language": "<user-provided language>",
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

Key fields to set correctly:
- `platform`: Either `linux/arm64` or `linux/amd64`
- `prefix`: Always `/v1` — this determines the URL prefix for every endpoint
- `ingress.external_port.port`: Must match the port the microservice listens on
- `readiness_probe_config.path`: The health check endpoint (e.g. `/healthz`)
- `cpu`: Supported values — 100, 250, 500, 750, 1000, 1500, 2000, 3000
- `memory`: Supported values — 0.125, 0.25, 0.5, 1, 2, 3, 4

**2. Dockerfile**

Every BYOSnap must have a Dockerfile that containerizes the microservice.

If using a resources folder, both files go there and the path is passed to snapctl via `--resources-path`.

### Phase 4 — Code requirements

Ensure the scaffolded microservice follows these rules:
1. It is an **HTTP-based** microservice
2. Every externally reachable endpoint must be prefixed with `<prefix>/<byosnap-id>` — e.g. `/v1/byosnap-my-code/...` where `/v1` comes from the profile `prefix` field and `byosnap-my-code` is the BYOSnap identifier
3. It has a **health check endpoint** registered in the profile's `readiness_probe_config.path`. The readiness URL never has the prefix or the byosnap ID (the core scaffolds use `GET /healthz` at the root).
4. All required files are present

### Phase 4b — Calling other snaps (optional)

If the BYOSnap needs to talk to other snaps in the Snapend (e.g. read a profile, grant currency, update a leaderboard), it uses the **Snapser internal SDK**:

1. Download the internal SDK in the BYOSnap's language for the target Snapend:
   ```bash
   # $format = server SDK format matching the BYOSnap language, e.g. go, python, node, kotlin, java, rust, csharp
   snapctl snapend download --snapend-id $snapendId --category sdk --format $format --type internal --out-path .
   ```
   (Run `snapctl snapend download --help` to see the full format list.)
2. Add the SDK to the BYOSnap project and call other snap APIs through it. Internal calls go over the intra-Snapend gateway — no public round-trip, no user token needed.

Do not hand-roll HTTP calls to other snaps; the internal SDK carries the correct routing and auth headers.

### Phase 5 — Validate the profile
Run the validation command to catch issues early:
```bash
snapctl byosnap validate-profile --path <project-or-resources-path>
```

### Phase 6 — Optional files
Mention to the user that they can optionally add:
- `swagger.json` — Swagger 1.3 spec for the microservice
- `snapser-config-tool-*.html` — HTML files rendered in the BYOSnap configuration web app iframe (replace `*` with a tool name, no spaces)
- `snapser-user-tool-*.html` — HTML files rendered in the BYOSnap user manager tool web app iframe (replace `*` with a tool name, no spaces)

These go in the same location as the required files (root or resources folder).

### Phase 7 — Optionally test the BYOSnap in the Snapser cloud

Ask the user if they want to run a quick end-to-end test to verify the BYOSnap works correctly when deployed. If they decline, skip to Phase 8.

If they agree, follow these steps:

**Step 1 — Ensure a testable endpoint exists**

The microservice needs at least one endpoint that uses `user` authorization so we can verify the auth gateway is wired up correctly. Confirm the code has an endpoint like:
```
GET /v1/<byosnapId>/user-auth/<user_id>
```
Where `<byosnapId>` is the user's actual BYOSnap ID (e.g. `byosnap-my-service`).

If this endpoint doesn't exist, help the user add one. It should validate the caller's identity using the `user` authorization scheme — meaning the Snapser gateway verifies the session token and passes the authenticated user context to the BYOSnap.

**Step 2 — Create a minimal test Snapend**

Generate a base manifest with just the `auth` snap (do NOT write manifest JSON from scratch, and do NOT add eventbus or any other snap — auth is all a BYOSnap test needs):
```bash
# $testName = test Snapend name from the user (max 20 chars, alphanumeric + dashes, starts with a letter)
snapctl snapend-manifest create \
  --name $testName \
  --env DEVELOPMENT \
  --snaps auth \
  --out-path-filename ./$testName-manifest.json
```

**Step 3 — Create the test Snapend and enable anonymous login**

```bash
snapctl snapend create \
  --name $testName \
  --env DEVELOPMENT \
  --manifest-path-filename ./$testName-manifest.json \
  --blocking
```
Save the `snapendId` returned by this command — it's needed for all subsequent steps.

Then enable **anonymous login** on the dev environment via the Admin SDK — follow
`skills/configure-snap-settings/SKILL.md` (auth's `authAdminEnableAnonLogin` method), and
download the fresh manifest to the project root afterwards.

**Step 4 — Direct-deploy the BYOSnap to the test Snapend**
```bash
snapctl byosnap direct-deploy \
  --byosnap-id $byosnapId \
  --snapend-id $snapendId \
  --path $pathToByosnap \
  --resources-path $pathToResources \
  --blocking
```
Omit `--resources-path` if the profile and Dockerfile are at the project root.

**Step 5 — Run the verification tests**

Once the Snapend is online, run three curl calls to verify everything is wired up:

**5a. Create a test user via anonymous auth:**
```bash
curl -XPUT \
  -H 'Content-Type: application/json' \
  -d '{"create_user": true, "username": "test"}' \
  "https://gateway.snapser.com/$snapendId/v1/auth/login/anon"
```
The response contains a JSON object with `user.id` and `user.session_token`. Extract and save both values for the next calls.

**5b. Hit the BYOSnap endpoint with valid credentials (expect 200):**
```bash
curl -XGET \
  -H 'Content-Type: application/json' \
  -H "Token: $sessionToken" \
  "https://gateway.snapser.com/$snapendId/v1/$byosnapId/user-auth/$userId"
```
Confirm the response is HTTP 200. This proves the BYOSnap is deployed, reachable through the gateway, and the `user` authorization scheme is working.

**5c. Hit the same endpoint with a bad user ID (expect failure):**
```bash
curl -XGET \
  -H 'Content-Type: application/json' \
  -H "Token: $sessionToken" \
  "https://gateway.snapser.com/$snapendId/v1/$byosnapId/user-auth/12345"
```
Confirm this returns an error (not 200). This proves the authorization scheme is correctly rejecting mismatched user IDs.

**Step 6 — Report results**

If all three tests pass, let the user know their BYOSnap is working correctly end-to-end. Ask them to delete this test Snapend as for security reasons Snapser does not allow snapend deletion via an agent or CLI.

If any test fails:
- **5a fails** — the test Snapend may not be fully online yet. Wait and retry. Check `snapctl snapend enumerate` for status.
- **5b fails with 404** — the BYOSnap may not be deployed or the endpoint path is wrong. Verify the BYOSnap ID in the URL matches the profile and the code's route prefix.
- **5b fails with 401/403** — the authorization scheme may not be configured correctly in the endpoint. Verify the endpoint uses `user` auth.
- **5c returns 200** — the endpoint is not validating user identity correctly. The code should check that the authenticated user matches the `<user_id>` path parameter.

### Phase 8 — Next steps
Ask the user:
- Do they want to **direct-deploy** this BYOSnap to an existing DEVELOPMENT Snapend for fast iteration? If yes, guide them through `skills/direct-deploy-byosnap/SKILL.md`.
- Do they want to **publish** this BYOSnap to the registry so it can be added to any Snapend and shared with the team? If yes, guide them through `skills/publish-byosnap/SKILL.md`.

## Notes
- Be conversational throughout — guide the user, don't just dump commands
- If any step fails, explain the error clearly and offer to retry or adjust
- Always validate the BYOSnap ID starts with `byosnap-` before running any command
- Default to reasonable values (cpu: 100, memory: 0.125, port: 5003) but let the user override
