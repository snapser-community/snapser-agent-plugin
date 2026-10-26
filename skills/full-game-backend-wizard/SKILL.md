---
name: full-game-backend-wizard
description: Complete end-to-end game backend setup with snaps, BYOSnap, and SDK
---

# Skill: Full Game Backend Wizard

The end-to-end wizard that takes a developer from zero to a fully working game backend
with Snapser snaps, a custom microservice (BYOSnap), and an SDK — all in one guided flow.

This is the complete onboarding experience. It chains together multiple skills into a
single cohesive journey.

## Trigger Phrases
- "set up everything for my game"
- "I want a complete backend for my game"
- "full game backend setup"
- "build me a complete game backend"
- "I'm starting a new game and need the whole backend"
- "end to end backend setup"
- "game backend wizard"

## Requirements
- Snapser CLI (`snapctl`) installed and configured
- Docker installed and running (needed for BYOSnap)
- If the user hasn't set up snapctl yet, start with `skills/setup-snapctl/SKILL.md` before proceeding

## Overview

This wizard walks through 7 stages. Each stage maps to an existing skill, but the wizard
ties them together so the user doesn't have to know which skill to invoke next.

```
Stage 1: Understand the game → gather requirements
Stage 2: Pick snaps → recommend based on game type
Stage 3: Create the Snapend → deploy the backend
Stage 4: Build a BYOSnap → custom microservice (optional)
Stage 5: Deploy the BYOSnap → direct-deploy to the Snapend
Stage 6: Download the SDK → client integration
Stage 7: Verify everything works → end-to-end test
```

The user can exit at any stage. If they don't need a BYOSnap, skip stages 4–5.
If they already have some pieces in place, skip those stages.

## Full Workflow

### Stage 1 — Understand the game

Ask the user about their project. Be conversational — this sets the tone for the whole experience.

Gather:
- **What kind of game or app?** (arcade, RPG, battle royale, multiplayer, SaaS, etc.)
- **What platform/engine?** (Unity, Unreal, Godot, Roblox, web, mobile, etc.)
- **What features do they need?** (leaderboards, matchmaking, chat, inventory, etc.)
  - If they're not sure, that's fine — we'll recommend based on game type
- **Do they need custom server-side logic?** (i.e. will they need a BYOSnap?)
- **What programming language** for any custom code? (Go, Python, Node, C#, etc.)

### Stage 2 — Pick snaps and create the backend

**Reference:** `skills/create-backend/SKILL.md` and `skills/backend_templates.md`

1. Run `snapctl snaps enumerate` to get the current snap catalog
2. Based on the game type from Stage 1, recommend a snap set from `skills/backend_templates.md`
3. Show the recommendation and let the user adjust (add/remove snaps)
4. Confirm the final snap list — remind them auth is always included automatically
5. Ask for a **Snapend name** (max 20 chars, alphanumeric + dashes, starts with letter)
6. **Gather settings requirements** — ask the user what they want to enable per snap (auth methods, leaderboard names, storage keys, etc.). Settings are applied AFTER the Snapend is live via the Admin SDK (`skills/configure-snap-settings/SKILL.md`); for what individual settings mean, read `data/docs/infra/snaps/<snap-name>/`. Do NOT hand-edit manifest settings JSON.
7. **Generate the base manifest** using `snapctl snapend-manifest create --name $name --env DEVELOPMENT --snaps $commaSeparatedSnaps --out-path-filename ./$name-manifest.json`. **NEVER write manifest JSON from scratch** — the schema is complex and hand-written manifests will fail. Do NOT edit the generated manifest.
8. **Create the Snapend from the manifest:**
   ```bash
   snapctl snapend create \
     --name $snapendName \
     --env DEVELOPMENT \
     --manifest-path-filename $pathToManifest \
     --blocking
   ```
9. If the create times out (exit code 79), check status with `snapctl snapend enumerate` — this is normal for larger snap sets.
10. Save the Snapend ID — we'll need it throughout
11. **Apply the settings from step 6 via the Admin SDK** — follow `skills/configure-snap-settings/SKILL.md`. For any snap version without admin support, direct the user to that snap's Config tool in the web portal.
12. Download the latest manifest to the project root (MANDATORY after settings changes):
    ```bash
    snapctl snapend download --snapend-id $snapendId --category snapend-manifest --format json --out-path .
    ```

### Stage 3 — Download the SDK

**Reference:** `skills/download-sdk/SKILL.md`

1. Based on the engine/platform from Stage 1, determine the right SDK format and type
2. Download the SDK using `snapctl snapend download --snapend-id $snapendId --category sdk`
3. Tell the user where the SDK was saved and give a brief integration pointer for their platform

### Stage 4 — Build a custom microservice (optional)

**Reference:** `skills/create-byosnap/SKILL.md`

If the user said they need custom server-side logic in Stage 1:

1. Gather BYOSnap inputs: ID (must start with `byosnap-`), name, description
2. Clone the community repo and scaffold from the matching language example under **`core/`** (seven languages: Python, Go, Node-TS, C#, Rust, Java, Kotlin — see `skills/create-byosnap/SKILL.md` for the folder table):
   ```bash
   git clone --depth 1 https://github.com/snapser-community/snapser-byosnaps.git
   ```
3. Copy the `core/` example, clean up, rename the single `byosnap-core` Snap-id constant to the user's BYOSnap ID (this updates every route prefix)
4. Generate the `snapser-byosnap-profile.json` with sensible defaults
5. Ensure Dockerfile is present
6. Validate the profile:
   ```bash
   snapctl byosnap validate-profile --path $projectPath
   ```

If the user said no custom logic, skip to Stage 6.

### Stage 5 — Deploy the BYOSnap

**Reference:** `skills/direct-deploy-byosnap/SKILL.md`

1. Direct-deploy the BYOSnap to the Snapend created in Stage 2:
   ```bash
   snapctl byosnap direct-deploy \
     --byosnap-id $byosnapId \
     --snapend-id $snapendId \
     --path $pathToByosnap \
     --blocking
   ```
2. Wait for deploy to complete
3. Confirm the BYOSnap is live on the Snapend

### Stage 6 — Verify everything works

**Reference:** `skills/create-byosnap/SKILL.md` Phase 7 (test procedure)

Run a quick smoke test. First, verify the snap settings are configured correctly:
```bash
snapctl snap-config get-config --snaps auth --snapend-id $snapendId
```
Confirm anonymous auth is enabled. If a BYOSnap was deployed, also check that the relevant snaps are configured as expected.

Then test the endpoints:

1. Create a test user via anonymous auth:
   ```bash
   curl -XPUT \
     -H 'Content-Type: application/json' \
     -d '{"create_user": true, "username": "test"}' \
     "https://gateway.snapser.com/$snapendId/v1/auth/login/anon"
   ```
   Extract `user.id` and `user.session_token` from the response.

2. If a BYOSnap was deployed, test one of its endpoints:
   ```bash
   curl -XGET \
     -H 'Content-Type: application/json' \
     -H "Token: $sessionToken" \
     "https://gateway.snapser.com/$snapendId/v1/$byosnapId/user-auth/$userId"
   ```
   Confirm HTTP 200.

3. Report results to the user.

### Stage 7 — Recap and next steps

Give the user a summary of everything that was set up:
- Snapend name, ID, and environment
- Snaps included
- BYOSnap deployed (if applicable)
- SDK downloaded and where it's saved

Then offer next steps:
- **Want to debug locally?** → `skills/attach-workstation/SKILL.md`
- **Want to publish the BYOSnap for the team?** → `skills/publish-byosnap/SKILL.md`
- **Want to promote to staging?** → `skills/clone-snapend/SKILL.md`
- **Need a game server fleet?** → `skills/byogs-publish/SKILL.md`
- **Have questions about a snap's API?** → `skills/snapser-help/SKILL.md`

## Wizard Behavior Guidelines

- **Be conversational throughout.** This is onboarding — the user may be new to Snapser. Explain what each step does and why.
- **Don't dump all stages at once.** Present one stage at a time. Let the user absorb and respond.
- **Let the user skip stages.** If they already have a Snapend, skip creation. If they don't need a BYOSnap, skip stages 4–5.
- **Checkpoint after each stage.** Confirm success before moving on. If something fails, fix it before proceeding.
- **Save IDs along the way.** Snapend ID, BYOSnap ID, and SDK paths are needed across stages. Keep track of them.
- **Default to sensible values.** DEVELOPMENT environment, cpu 100, memory 0.125, port 5003. Only ask for overrides if the user brings them up.
- **If any stage fails,** use `skills/error_codes.md` to diagnose and recover before continuing.

## Notes
- This wizard is designed to be run in a single session, but can be resumed if interrupted.
- Each stage references an existing skill — the wizard is the orchestration layer, not a replacement.
- The auth snap is always included — never ask about it.
- Always use `--blocking` for create and deploy operations.
- Always validate the BYOSnap profile before deploying.
