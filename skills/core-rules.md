# Snapser Core Rules

These rules apply to every Snapser workflow. Read this file one time in each session,
before you run a `snapctl` command or change a Snapend. Each skill file adds the steps
for one workflow; this file holds the rules that all workflows share.

---

## 1. Paths

- Every `skills/...` and `data/...` path in a skill file starts at the **plugin root** —
  the folder that contains the `skills/` and `data/` directories. This file is
  `<plugin-root>/skills/core-rules.md`.
- The plugin root is **not** the user's project. Read plugin files from the plugin root.
- Write project files (manifests, SDKs, the Admin SDK venv, game code) in the **user's
  project**. Never write inside the plugin folder — it may be a read-only cache.

## 2. Prerequisite check

Before the first `snapctl` command of a session, run:

```bash
snapctl validate
```

This checks that snapctl is installed, the API key is valid, and the application is
configured. If it fails:

- **snapctl is not found** → follow `skills/setup-snapctl/SKILL.md`.
- **The API key is missing or invalid** → run `snapctl login`. It opens a browser where
  the user clicks **Activate**; the key is minted and stored automatically. It is
  idempotent (safe to run any time) and self-heals expired keys. Tell the user to watch
  for the browser window and confirm the short code shown in the terminal.
- **No application is configured** → ask the user if they want to create a new
  application (`skills/create-application/SKILL.md`), or run
  `snapctl application enumerate` and let them pick one.

**Do not proceed with any workflow until `snapctl validate` passes.**

## 3. Execution mode

After `snapctl validate` passes, tell the user:

> "I'm running in **Agent Mode** — I'll execute commands on your behalf. If you'd prefer
> **Guide Mode** where I walk you through each step and show you the commands to run
> yourself, just let me know."

In **Guide Mode**, for the rest of the session:

- **Do NOT execute** any `snapctl` commands or settings scripts. Show the user the exact
  command with all parameters filled in, and explain what it does.
- Wait for the user to confirm they ran each command and share the output before moving
  to the next step.
- If the user shares an error, look it up in `skills/error_codes.md` and explain the
  fix — but still show the recovery command rather than running it.

In **Agent Mode** (the default), execute commands as the skill files describe. The user
can switch at any time by saying "switch to guide mode" or "switch to agent mode."

## 4. HARD RULE — structure and settings are two separate phases

This is non-negotiable. Building or changing a backend's snaps is one phase; changing
snap settings is a completely separate phase. Never combine them in one step.

**Phase 1 — Structure (snaps and features).** The ONLY way to build or change a manifest
is `snapctl snapend-manifest create/update/sync/upgrade`. Bring the Snapend online with
`snapctl snapend create` / `snapctl snapend apply` (always `--blocking`). The manifest
you create or apply MUST have an empty `settings` array.

**Phase 2 — Settings.** Once the Snapend is live, change EVERY snap setting through the
bundled Admin SDK by following `skills/configure-snap-settings/SKILL.md`. The Admin SDK
is the only sanctioned way to change a setting. The plugin bundles the Python Admin SDK
at `data/admin-sdk/sdk-python` — use it by default; `snapctl admin-sdk download` is a
fallback that the skill's error-handling ladder covers.

**Never manipulate the manifest with any other tool.** No `python`, no `jq`, no `sed`,
no here-doc scripts, no hand-editing. Never construct `service_definitions` or
`feature_definitions` manually. Never assemble a `settings` block — even one grounded in
the Admin SDK source or the config docs — and write it into the manifest. That it
produces "valid JSON" or that it worked once does not make it allowed.

**Keep the manifest in sync.** After every Snapend mutation (`snapend create`,
`snapend apply`, `snapend clone`, or any Admin SDK settings change), immediately
download the manifest to the user's project root:

```bash
snapctl snapend download --snapend-id $snapendId --category snapend-manifest --format json --out-path .
```

The downloaded manifest is the canonical, version-controllable record of the backend —
an OUTPUT, never a hand-authored input. Always download a fresh manifest before a
manifest update or apply; applying a stale manifest fails.

**Configure-only requests** (the snap already exists and the user only wants to change
its settings): skip Phase 1 — go straight to the Admin SDK against the live Snapend,
then download the manifest.

## 5. Command rules

**Always:**

- **Fetch snaps dynamically** with `snapctl snaps enumerate`. Never assume or hardcode
  snap names or IDs.
- **Use `--blocking`** when you create, apply, clone, or update a Snapend, so the next
  step runs against a live Snapend.
- **Default to DEVELOPMENT.** Do not suggest staging or production unless the user asks.
- **Include the auth snap.** It is mandatory on every Snapend — never ask the user
  whether they want it.
- **Use JSON for manifests.** Pass `--format json` on manifest downloads and use `.json`
  filenames. YAML has a long-integer serialization issue.
- **Validate the BYOSnap profile** before a publish or deploy:
  `snapctl byosnap validate-profile`.

**Validate user input before you run a command:**

- **Snapend names:** max 20 characters, alphanumeric and dashes only, must start with a
  letter, unique per environment. No spaces.
- **BYOSnap IDs:** must start with `byosnap-`.
- **Versions:** must be semantic — e.g. `v0.0.1`, `v1.0.0`.

**`--application-id`:** Snapend-level commands (`snapend create`, `snapend enumerate`,
`snapend update`, `snapend clone`, etc.) require `--application-id`. Catalog commands
like `snapctl snaps enumerate` do **not** take it. `snapctl inspect` subcommands take
only `--snapend-id`.

**Output path flags — these are not interchangeable:**

- `--out-path-filename` = full file path including the filename. Used by the manifest
  commands (`snapend-manifest create/sync/update/upgrade`) and by
  `snapctl inspect logs/monitor/metrics`.
- `--out-path` = directory only, no filename. Used by `snapend download`; snapctl
  creates the file inside this directory.

When in doubt about a command, read `skills/snapctl_commands.md` or run
`snapctl <command> --help`.

## 6. Error handling

Do not guess what an error means. When a command fails:

1. Look up the exit code in `skills/error_codes.md`.
2. Explain the error to the user with the description and recovery action from that file.
3. For a timeout (codes 64, 67, 70, 74, 79), suggest a retry and check status with
   `snapctl snapend enumerate`.
4. For a permission issue (codes 26, 36, 39, 42, 52), ask the user to verify their API
   key scopes.
5. If the error persists after recovery, suggest contacting Snapser support.

## 7. Questions and documentation

**Never use web search or fetch remote URLs for anything Snapser-related.** All
documentation, API specs, and release notes are bundled in this plugin under `data/`.
To answer a Snapser question, follow `skills/snapser-help/SKILL.md`.
