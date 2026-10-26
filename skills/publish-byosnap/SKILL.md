---
name: publish-byosnap
description: Publish a BYOSnap to the Snapser registry with a version
---

# Skill: Publish a BYOSnap

Publishes a BYOSnap to the user's private Snapser registry so it can be added to any
Snapend (dev, staging, or production) and is visible to other members of the organization.

## Trigger Phrases
- "publish my byosnap"
- "release my byosnap"
- "make my byosnap available to the team"
- "I want to version and publish my microservice"
- "push my byosnap to the registry"

## Requirements
- Snapser CLI (`snapctl`) installed
- Docker installed and running (publish builds a container image)
- The user must have BYOSnap code ready with a valid `snapser-byosnap-profile.json` and `Dockerfile`. If they don't, guide them through `skills/create-byosnap/SKILL.md` first.

## Full Workflow

### Phase 1 — Gather inputs

Confirm the following with the user:
- **BYOSnap ID** — must start with `byosnap-`. Validate before proceeding.
- **Version** — must be semantic versioning format (e.g. `v0.0.1`, `v1.0.0`). If the user provides an invalid format, explain the requirement and ask them to correct it.
- **Code path** — the local directory containing the BYOSnap code and Dockerfile.
- **Resources path** (optional) — if the profile and Dockerfile are in a subdirectory (e.g. `snapser-resources/`), get this path. Otherwise, omit the `--resources-path` flag.
- **Profile filename** (optional) — if the user has a custom profile name other than `snapser-byosnap-profile.json`, get it. Otherwise, omit the `--profile-filename` flag.

### Phase 2 — Validate the profile

Before publishing, validate the BYOSnap profile to catch issues early:
```bash
snapctl byosnap validate-profile --path <code-path-or-resources-path>
```
If validation fails, explain the error and help the user fix the profile before retrying.

### Phase 3 — Publish

Run the publish command. This is an all-in-one command that creates the BYOSnap namespace
(if it doesn't exist), builds and pushes the Docker image, and assigns the version:
```bash
snapctl byosnap publish \
  --byosnap-id $byosnapId \
  --version "$version" \
  --path $pathToByosnap \
  --resources-path $pathToResources \  # only if applicable
  --profile-filename $profileFilename  # only if applicable
```

Wait for the command to complete.

**Common publish errors:**
- **Code 37 / 44 — duplicate tag:** This version or tag already exists. Ask the user to bump the version number.
- **Code 36 / 42 — permission error:** The API key lacks publish permissions. Ask the user to verify their key scopes or contact their org admin.
- **Code 40 — duplicate name:** A BYOSnap with this name already exists. Use a different BYOSnap ID.

For all other errors, check `skills/error_codes.md`.

### Phase 4 — Confirm publication

After a successful publish, let the user know:
- Their BYOSnap is now in the private registry at version `$version`
- Other team members in the organization can now see and use it
- It can be added to any Snapend (dev, staging, or production)

### Phase 5 — Next steps

Ask the user:
- **Want to add it to a Snapend?** They can update an existing Snapend to include the newly published BYOSnap. The command is:
  ```bash
  snapctl snapend update --snapend-id $snapendId --byosnaps $byosnapId:$version --blocking
  ```
  Or guide them through `skills/update-backend/SKILL.md` to add the published BYOSnap to a Snapend.
- **Want to create a new backend with this BYOSnap?** Guide them through `skills/create-backend/SKILL.md` to set up a Snapend, then add the BYOSnap to it.

## Notes
- Publishing makes the BYOSnap available across all environments — not just development.
- Be conversational — guide the user step by step, don't dump all commands at once.
- If any step fails, explain the error clearly using `skills/error_codes.md` and offer to retry or adjust.
- Always validate the BYOSnap ID starts with `byosnap-` before running any command.
- Always validate the version follows semantic versioning before running publish.
