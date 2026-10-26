---
name: attach-workstation
description: Attach your local workstation to a Snapend for live debugging (BYOWS)
---

# Skill: Attach Workstation to Snapend (BYOWS)

Guides the developer through attaching their local machine to a remote DEVELOPMENT Snapend
so that traffic intended for their BYOSnap is reverse-proxied to their local server.
This enables live local debugging against real Snapend traffic without rebuild/redeploy cycles.

**IMPORTANT: This is an informational skill. The BYOWS commands start a live reverse proxy
session that must stay running in the user's own terminal. Do NOT run any `snapctl byows`
commands on behalf of the user. Instead, provide the commands for the user to copy and
run in their own terminal.**

## Trigger Phrases
- "attach my workstation"
- "connect my machine to the snapend"
- "I want to debug my byosnap locally"
- "set up byows"
- "route traffic to my local server"
- "live debug my byosnap"

## Requirements
- Snapser CLI (`snapctl`) installed on the user's machine
- The user must have an existing **DEVELOPMENT** Snapend with a BYOSnap deployed on it. BYOWS does not work with staging or production Snapends. If they don't have one yet, guide them through `skills/direct-deploy-byosnap/SKILL.md` first.
- The user must have their BYOSnap server ready to run locally on a known port.

## Full Workflow

### Phase 1 — Gather inputs

Confirm the following with the user:
- **Snapend ID** — the target DEVELOPMENT Snapend. If the user isn't sure, run `snapctl snapend enumerate` and let them pick.
- **BYOSnap ID** — must start with `byosnap-`. Validate before proceeding.
- **Local HTTP port** — the port their local server will listen on (e.g. `5003`).

### Phase 2 — Provide the commands to the user

Once you have the inputs, give the user the following commands to run in their own terminal. **Do NOT execute these yourself** — the attach command starts a live session that must run in the user's terminal.

**Step 1 — Attach the workstation.** Tell the user to run this in their terminal:
```bash
snapctl byows attach --snapend-id <snapendId> --byosnap-id <byosnapId> --http-port <port>
```
Replace the placeholders with the actual values gathered in Phase 1.

Explain what this does: it registers their machine with the Snapend so that all traffic destined for the BYOSnap is routed to their local machine instead. The command also generates an environment setup file at `~/.snapser/byows_env_setup.sh` (or `.ps1` on Windows).

**Step 2 — Source the environment file.** Tell the user to open a **new terminal** and run:
```bash
# MacOS / Linux
source ~/.snapser/byows_env_setup.sh

# Windows
.\.snapser\byows_env_setup.ps1
```
This file contains the environment variables that allow the local BYOSnap to call other Snaps in the Snapend via the internal SDK.

**Step 3 — Start the local server in that same terminal.** Remind the user to start their BYOSnap server in the **same terminal where they sourced the environment file**:
```bash
# Example for Python:
python app.py

# Example for Node:
npm start

# Example for Go:
go run main.go
```

### Phase 3 — Remind the user of key gotchas

Make sure the user is aware of these:
- The server **must** listen on the same port they specified in the attach command.
- The environment file **must** be sourced in the **same terminal** where the server runs. Sourcing in one terminal and starting the server in another is a common mistake — internal SDK calls to other Snaps will silently fail.
- Only **one** BYOWS session can be attached per BYOSnap on a Snapend at a time.

### Phase 4 — Provide detach and reset commands

Tell the user that when they're done debugging, they should detach:
```bash
snapctl byows detach --snapend-id <snapendId> --byosnap-id <byosnapId>
```

If things get into a bad state, they can reset BYOWS for the entire Snapend:
```bash
snapctl byows reset --snapend-id <snapendId>
```

### Phase 5 — Next steps

Ask the user:
- **Happy with the code?** They can publish the BYOSnap to the registry for the team. Guide them through `skills/publish-byosnap/SKILL.md`.
- **Want to redeploy changes?** They can run another direct-deploy to push updated code to the Snapend. Guide them through `skills/direct-deploy-byosnap/SKILL.md`.

## Notes
- **Do NOT run `snapctl byows attach`, `snapctl byows detach`, or `snapctl byows reset` yourself.** These are live session commands that must run in the user's own terminal.
- BYOWS only works with **DEVELOPMENT** Snapends. If the user asks about staging or production, explain this limitation.
- Be conversational — explain what each command does as you provide it, so the user understands the flow.
- Always validate the BYOSnap ID starts with `byosnap-` before providing commands.
