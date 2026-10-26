---
name: byogs-publish
description: Publish a custom game server image to Snapser (BYOGS)
---

# Skill: Publish a BYO Game Server (BYOGS)

Guides the developer through creating and publishing a custom game server image to Snapser.
Once published, the user can create a fleet from the Snapser web portal and deploy it to
their Snapend.

## Trigger Phrases
- "publish my game server"
- "I want to create a custom game server"
- "upload my game server to Snapser"
- "set up a dedicated game server"
- "build a game server for my fleet"
- "byogs publish"

## Requirements
- Snapser CLI (`snapctl`) installed
- Docker installed and running (BYOGS builds a container image)
- The user must have game server code with a Dockerfile, or want to start from a Snapser example

## Full Workflow

### Phase 1 — Determine starting point

Ask the user:
- **Do they already have game server code?** If yes, skip to Phase 3.
- **What programming language?**

### Phase 2 — Scaffold from community examples

Snapser has a community repo with BYOGS examples at:
```
https://github.com/snapser-community/snapser-byogs/tree/main/inter
```

**IMPORTANT: You MUST use `git clone` to get the example code. Do NOT fetch individual files via curl, wget, or any HTTP requests. Do NOT spawn an agent to download files.**

1. Clone the community repo:
   ```bash
   git clone https://github.com/snapser-community/snapser-byogs.git
   ```

2. List the available examples under `inter/` and show the user what's available. Let them pick an example that matches their needs.

3. Copy the chosen example to a new directory:
   ```bash
   cp -r snapser-byogs/inter/<chosen-example> ./<user-project-name>
   ```

4. Remove the cloned repo:
   ```bash
   rm -rf snapser-byogs
   ```

5. If the user's language or server type doesn't match any example, use the closest one as a reference and scaffold a new project in their chosen language.

### Phase 3 — Verify required files

The game server project **must** have a `Dockerfile` at the root of the project (or in a resources folder).

Verify:
- A `Dockerfile` exists and is valid
- The game server binds to a known port
- The Dockerfile builds and produces a runnable container

**Architecture note:** Remind the user to check their Dockerfile for hardware architecture compatibility. Snapser runs on `linux/arm64` by default. If their Dockerfile has architecture-specific commands (e.g. downloading amd64 binaries), they may need to adjust. Snapser will warn if it detects a mismatch.

### Phase 4 — Gather publish inputs

Confirm the following with the user:
- **Image tag** — a label for this build (e.g. `my-game-server-v1`, `beta-build`). This is a Docker image tag, not a semantic version.
- **Code path** — the local directory containing the game server code and Dockerfile.
- **Resources path** (optional) — if the Dockerfile is in a subdirectory rather than the project root, get this path.

### Phase 5 — Publish the game server

Run the publish command:
```bash
snapctl byogs publish \
  --tag $imageTag \
  --path $pathToCode \
  --resources-path $pathToResources  # only if applicable
```

This builds the Docker image, pushes it to the Snapser registry, and makes it available for fleet creation.

If the command fails, check the exit code against `skills/error_codes.md`:
- **Code 22** — ECR login error. Re-authenticate, verify API key.
- **Code 23** — Build error. Check Dockerfile syntax.
- **Code 25** — Publish error. Check network and permissions.
- **Code 26** — Permission error. Verify API key scopes.
- **Code 27** — Duplicate tag. Use a different tag name.

### Phase 6 — Confirm and guide fleet creation

After a successful publish, let the user know:
- Their game server image is now in the Snapser registry with tag `$imageTag`
- **IMPORTANT:** The image tag is the exact string passed to `--tag` during publish. Do NOT add any prefix like `byogs.`, `snapser/`, or any namespace. If the user published with `--tag my-game-v1`, the tag is `my-game-v1` — nothing more.

### Phase 7 — Next steps

Ask the user:
- **Need to add game-server-fleets snap to their Snapend?** Guide them through `skills/update-backend/SKILL.md` to add the `game-server-fleets` snap if it's not already present.

## Notes
- BYOGS images are published to the organization's private registry — other team members can use them.
- Fleet creation and management happens in the Snapser Web App, not via CLI.
- Be conversational — guide the user step by step, don't dump all commands at once.
- If any step fails, explain the error clearly using `skills/error_codes.md` and offer to retry or adjust.
