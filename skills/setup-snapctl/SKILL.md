---
name: setup-snapctl
description: Install and configure the Snapser CLI (snapctl)
---

# Skill: Set Up Snapser CLI (snapctl)

Walks a new user through installing the Snapser CLI, logging in with `snapctl login`,
creating an application, and verifying everything works.

## Trigger Phrases
- "set up snapctl"
- "install the snapser cli"
- "I'm new to Snapser"
- "how do I get started with Snapser?"
- "configure my snapser api key"
- "snapctl validate is failing"

## Requirements
- Python 3.x installed on the user's machine
- Internet access to install packages

## Full Workflow

### Phase 1 — Check if snapctl is already installed

Run a quick check:
```bash
snapctl --help
```

If this succeeds, snapctl is already installed — skip to Phase 3.
If it fails, proceed to Phase 2.

### Phase 2 — Install snapctl

**Step 1 — Ensure pip or pipx is available:**

Check if pip is installed:
```bash
pip3 --version
```

If pip is missing, guide the user to install it:
```bash
# MacOS / Linux
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py

# Windows
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

Optionally install pipx (recommended for CLI tools):
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

**Step 2 — Install snapctl:**

```bash
# Using pip
pip3 install --user snapctl

# Or using pipx (recommended)
pipx install snapctl
```

**Step 3 — Verify it's on PATH:**

```bash
snapctl --help
```

If this fails, the user may need to add the Python bin directory to their PATH:
- **MacOS/Linux:** Usually `~/Library/Python/3.x/bin` or `~/.local/bin`
- **Windows:** Usually `C:\Users\<username>\AppData\Roaming\Python\Python3x\Scripts`

After updating PATH, ask the user to restart their terminal and try again.

### Phase 3 — Log in

The primary path is `snapctl login` — a fully automated browser flow. The user never sees, copies, or pastes a key.

1. Tell the user: "I'll run `snapctl login`. A browser window will open — confirm the code shown in your terminal matches, then click **Activate**."
2. Run:
```bash
snapctl login
```
3. snapctl prints a short code (`XXXX-XXXX`) and a verification URL, and opens the browser automatically. The user approves in the Snapser web app; a freshly minted API key flows back and is saved to `~/.snapser/config` automatically.
4. `snapctl login` is **idempotent**: if a valid key is already stored, it prints "Already logged in as …" and exits — it is always safe to run. An expired or invalid key self-heals into a new browser login. Use `--force` only to deliberately re-mint.

Useful flags: `--profile <name>` (save under a named profile), `--portal-endpoint <url>` (enterprise customers; persisted as `PORTAL_ENDPOINT` in the profile so subsequent logins don't need the flag).

**Fallback — no browser available (SSH box where the printed URL can't be opened anywhere, CI):**
The user generates a key manually in the **Snapser Web App → user icon → User Account → Developer** section, then:
```bash
snapctl login --paste
```
and pastes the key when prompted. In CI, pass it non-interactively with `snapctl login --api-key <key>`.

**IMPORTANT: Do NOT echo or print the API key in the terminal output, and never write `~/.snapser/config` by hand — `snapctl login` owns that file.**

### Phase 4 — Set up the application

Ask the user if they already have an application on Snapser:
- If yes, run `snapctl application enumerate` to list their applications and let them pick the right one. Note the application ID for use with `--application-id` in subsequent commands.
- If no, guide them through `skills/create-application/SKILL.md`.

**Note:** The application ID does not need to be stored as an environment variable. It will be passed via `--application-id` to commands that need it, or the user can add it to their `~/.snapser/config` under the `SNAPSER_APPLICATION_ID` key.

### Phase 5 — Validate the setup

Run the validation command to confirm everything is connected:
```bash
snapctl validate
```

This checks that:
- snapctl can reach the Snapser server
- The API key is valid
- The application is configured

If validation succeeds, the user is ready to go.

If validation fails:
- **API key issue** — Run `snapctl login` again; an invalid or expired key self-heals into a fresh browser login.
- **Application not configured** — Run `snapctl application enumerate` and pick one, or create a new one via `skills/create-application/SKILL.md`.
- **Network issue** — Check internet connectivity and any corporate proxy/VPN settings.
- **Version issue** — Suggest upgrading: `pip3 install --user snapctl --upgrade` or `pipx upgrade snapctl`

### Phase 6 — Next steps

The user is now set up. Ask them what they want to do:
- **Create a backend?** Guide them through `skills/create-backend/SKILL.md`.
- **Build a custom microservice?** Guide them through `skills/create-byosnap/SKILL.md`.
- **Check existing backends?** Guide them through `skills/snapend-status/SKILL.md`.

## Notes
- Be conversational and patient — this is often the user's first interaction with Snapser.
- **Never expose the API key in terminal output or logs.**
- If any step fails, explain the error clearly and offer alternatives.
