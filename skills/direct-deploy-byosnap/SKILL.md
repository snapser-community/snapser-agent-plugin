---
name: direct-deploy-byosnap
description: Deploy a BYOSnap directly to a dev Snapend for fast iteration
---

# Skill: Direct-Deploy a BYOSnap (Development Workflow)

Builds and deploys a BYOSnap directly to a DEVELOPMENT Snapend without publishing.
This is the fastest iteration loop — no versioning, no registry, just build and deploy.

## Trigger Phrases
- "direct deploy my byosnap"
- "deploy my byosnap to dev"
- "I want to run my byosnap in dev mode"
- "push my code to my dev snapend"
- "test my byosnap on a snapend"

## Requirements
- Snapser CLI (`snapctl`) installed
- Docker installed and running (direct-deploy builds a container image)
- The user must have BYOSnap code ready with a valid `snapser-byosnap-profile.json` and `Dockerfile`. If they don't, guide them through `skills/create-byosnap/SKILL.md` first.
- The user must have an existing DEVELOPMENT Snapend. If they don't, guide them through `skills/create-backend/SKILL.md` first, then return here.

## Full Workflow

### Phase 1 — Gather inputs

Confirm the following with the user:
- **BYOSnap ID** — must start with `byosnap-`. Validate before proceeding.
- **Snapend ID** — the target DEVELOPMENT Snapend. If the user isn't sure, run `snapctl snapend enumerate` to list their Snapends and let them pick.
- **Code path** — the local directory containing the BYOSnap code and Dockerfile.
- **Resources path** (optional) — if the profile and Dockerfile are in a subdirectory (e.g. `snapser-resources/`), get this path. Otherwise, omit the `--resources-path` flag.

### Phase 2 — Validate the profile

Before deploying, validate the BYOSnap profile to catch issues early:
```bash
snapctl byosnap validate-profile --path <code-path-or-resources-path>
```
If validation fails, explain the error and help the user fix the profile before retrying.

### Phase 3 — Direct-deploy

Run the direct-deploy command:
```bash
snapctl byosnap direct-deploy \
  --byosnap-id $byosnapId \
  --snapend-id $snapendId \
  --path $pathToByosnap \
  --resources-path $pathToResources \  # only if applicable
  --blocking
```

Wait for the command to complete. This builds the Docker image, pushes it to the Snapend, and deploys it — all in one step.

If the command fails, check the exit code against `skills/error_codes.md` and guide the user through recovery.

### Phase 4 — Confirm deployment

After a successful deploy, let the user know their BYOSnap is live on the Snapend. Suggest they test their endpoints using the Snapend's gateway URL.

### Phase 5 — Next steps

Ask the user:
- **Want to debug locally?** They can attach their workstation using BYOWS so traffic intended for the BYOSnap routes to their local machine. Guide them through `skills/attach-workstation/SKILL.md` if they're interested.
- **Ready to share with the team?** When they're happy with the code, they can publish the BYOSnap to the registry so other team members can use it. Guide them through `skills/publish-byosnap/SKILL.md`.

## Notes
- Direct-deploy only works with **DEVELOPMENT** Snapends. If the user targets staging or production, explain this limitation.
- Be conversational — guide the user step by step, don't dump all commands at once.
- If any step fails, explain the error clearly using `skills/error_codes.md` and offer to retry or adjust.
- Always validate the BYOSnap ID starts with `byosnap-` before running any command.
