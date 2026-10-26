# Snapser — Background & Context

This file gives you the foundational knowledge to help developers build and manage
backends on Snapser. Read this before executing any skill or command.

> **IMPORTANT: NEVER use web search or fetch remote URLs for Snapser questions.**
> All Snapser documentation, API specs, and settings references are bundled locally
> in this plugin at `data/docs/` and `data/snap-swaggers/`.
> If a user asks a question about Snapser, read the local files — never search the
> web or fetch snapser.com. Use the `skills/snapser-help/SKILL.md` skill for guidance
> on finding the right local file.

---

## First: Check Pre-requisites

Before running any Snapser command, verify the following:

**1. Snapctl is installed and configured.**
Run:
```bash
snapctl validate
```
This checks that snapctl is installed, the API key is valid, and the application is configured. If it fails:
- If snapctl is not found → guide the user through `skills/setup-snapctl/SKILL.md`
- If the API key is missing or invalid → run `snapctl login`. It opens a browser where the user clicks **Activate**; the key is minted and stored automatically. It is idempotent (safe to run any time) and self-heals expired keys. Tell the user to watch for the browser window and confirm the short code shown in the terminal.
- If no application is configured → ask the user if they want to create a new application (use the `create_application` skill), or run `snapctl application enumerate` to list their applications and let them pick

**Do not proceed with any workflow until `snapctl validate` passes.**

**2. Choose execution mode.**
After confirming snapctl is set up, tell the user:

> "I'm running in **Agent Mode** — I'll execute commands on your behalf. If you'd prefer **Guide Mode** where I walk you through each step and show you the commands to run yourself, just let me know."

If the user chooses **Guide Mode**, follow these rules for the rest of the session:
- **Do NOT execute** any `snapctl` commands. Instead, show the user the exact command to run with all parameters filled in, and explain what it does.
- Wait for the user to confirm they ran each command and share the output before moving to the next step.
- If the user shares an error, look it up in `skills/error_codes.md` and explain the fix — but still show the recovery command rather than running it.

If the user stays in **Agent Mode** (the default), execute commands normally as described in the skill files.

The user can switch modes at any time during the session by saying "switch to guide mode" or "switch to agent mode."

**Do not proceed with any workflow until prerequisites 1–2 are confirmed.**

---

## What is Snapser?

Snapser is a Backend-as-a-Service (BaaS) platform built for games and apps. When a user
creates a backend on Snapser, they get their own isolated Kubernetes cluster — called a
**Snapend** — that runs entirely on Snapser's infrastructure. Users never manage
Kubernetes directly. Snapser handles all of that.

---

## Core Concepts

### Snapend

A Snapend is a backend you create on Snapser. Snapends run on Kubernetes and come with a
gateway, reserved compute for the Snaps the user has chosen, custom code they add (BYOSnaps),
and the data plane that powers all Snap microservices. Snapends are secure by default and
auto-scaled.

### Snapend Environments

Every Snapend has an environment:
- **DEVELOPMENT** — for active development and testing. Supports BYOWS and direct-deploy.
- **STAGING** — for pre-production validation
- **PRODUCTION** — live, customer-facing backend

Always default to DEVELOPMENT when helping a user create their first backend or when
they are iterating on a BYOSnap. Never suggest staging or production unless the user
explicitly asks for it.

### Manifests

A manifest is a JSON or YAML representation of a complete Snapser backend — its snaps,
their versions, and all configuration settings per snap.

**Always use JSON for manifests.** YAML is supported by snapctl but currently has a
long-integer serialization issue and can be flaky — agents must pass `--format json`
on manifest downloads and use `.json` filenames for all manifest commands.

Manifests are the ideal way to create a new backend reproducibly, clone into a new
environment, update configuration in a controlled way, and version control backend
config alongside code.

Key manifest commands:
- `snapctl snapend-manifest create` — build a new manifest from scratch
- `snapctl snapend-manifest update` — add or remove snaps from an existing manifest
- `snapctl snapend-manifest sync` — reconcile a manifest with a target snap list
- `snapctl snapend-manifest upgrade` — upgrade snaps to their latest versions
- `snapctl snapend apply` — apply a manifest to an existing Snapend
- `snapctl snapend create` — create a brand new Snapend from a manifest

**IMPORTANT — Keep manifests in sync:** After every Snapend mutation (`snapctl snapend create`, `snapctl snapend apply`, `snapctl snapend clone`, or any settings change via the Admin SDK), immediately download the latest manifest with `snapctl snapend download` and keep it at the **project root** — it is the canonical, version-controllable record of the backend. Always use a freshly downloaded manifest before running any manifest update or apply. Applying a stale manifest will fail.

### Snaps

Snaps are the building blocks of every Snapend. Each snap is a pre-built microservice
that combines code and a data plane — e.g. authentication, leaderboards, analytics,
storage, economy, game server fleets, and more.

Key facts:
- Every Snapend **always includes the auth snap** — it is mandatory. Never ask the user whether they want it.
- All other snaps are optional and chosen by the user
- Snaps are maintained and versioned by Snapser — users do not manage the underlying code
- Partner snaps are also available alongside Snapser's own snaps
- **Always run `snapctl snaps enumerate`** to get the current snap catalog before making recommendations. Never hardcode snap names or IDs.

When helping a user pick snaps, recommend a set based on their game or app type.
See `skills/backend_templates.md` for recommended snap sets organized by use case
(arcade, RPG, battle royale, SaaS, e-commerce, etc.).

### BYOSnaps — Bring Your Own Snap

BYOSnap is how customers bring their own custom microservices into their Snapend.

The BYOSnap workflow:
1. Developer writes their microservice code in any language (Go, Python, Node, etc.)
2. They add a `Dockerfile` to containerize it
3. They create a BYOSnap profile (`snapser-byosnap-profile.json`) describing the service
4. They publish it to their private Snapser registry using `snapctl`
5. It becomes available in their private marketplace, just like any other snap
6. They add it to their Snapend alongside other snaps using `snapctl`

BYOSnaps give customers full flexibility of custom code with the same infrastructure
and SDK access as first-party snaps. A BYOSnap can call other snaps internally using
the internal SDK.

### BYOWS — Bring Your Own Workstation

BYOWS lets a developer attach their local machine to a remote Snapend so that traffic
intended for their BYOSnap is routed to their local server instead. This enables
local editing with instant feedback, local debugger against real Snapend traffic, and
full-speed iteration without rebuild/redeploy cycles.

BYOWS only works with **DEVELOPMENT** Snapends. It is not available for staging or production.

After attaching, the developer must source the environment setup script in the same
terminal where they start their local server:
```bash
# MacOS / Linux
source ~/.snapser/byows_env_setup.sh

# Windows
.\.snapser\byows_env_setup.ps1
```

**IMPORTANT:** BYOWS requires an existing deployed Snapend that has a BYOSnap present.
If the user doesn't have one yet, guide them through Workflow 3 first to create a
Snapend with a BYOSnap, then come back to attach BYOWS.

---

## Tools

### Snapctl — Snapser CLI
Snapctl is the CLI tool for all Snapser operations — creating Snapends, managing snaps,
publishing BYOSnaps, downloading SDKs, and more.

Key commands:

| Command | What it does |
|---|---|
| `snapctl validate` | Verify snapctl is installed and configured correctly |
| `snapctl snaps enumerate` | Fetch all available snaps and their IDs |
| `snapctl snapend enumerate` | List all Snapends for the application |
| `snapctl snapend create` | Create a new Snapend |
| `snapctl snapend update` | Add or remove snaps from a Snapend |
| `snapctl snapend download` | Download an SDK, manifest, or protos for a Snapend |
| `snapctl login` | Log in via the browser; mints and stores the API key automatically |
| `snapctl admin-sdk download` | Fallback download of the Admin SDK (the plugin bundles it at `data/admin-sdk/`) |
| `snapctl snapend-manifest create` | Generate a base manifest from a snap list |

See `skills/snapctl_commands.md` for the complete command reference.

**`--application-id` usage:** Only Snapend-level commands (`snapend create`, `snapend enumerate`, `snapend update`, `snapend clone`, etc.) require `--application-id`. Catalog commands like `snapctl snaps enumerate` list globally available snaps and do **not** take `--application-id`. When in doubt, check `snapctl <command> --help`.

**Output path flags — do not mix these up:**
- `--out-path-filename` = full file path including filename. Used by **manifest commands**: `snapend-manifest create`, `snapend-manifest sync`, `snapend-manifest update`, `snapend-manifest upgrade`.
- `--out-path` = directory path only (no filename). Used by **download commands**: `snapend download`. The file is created inside this directory automatically.

These are different flags and are **not interchangeable**. Using the wrong one will cause the command to fail.

Useful snapctl command for inspecting live snap settings on an existing Snapend:
```bash
snapctl snap-config get-config --snaps auth,leaderboards --snapend-id $snapendId
```
This pulls the current settings for specific snaps from a deployed Snapend. Use it to inspect, verify, or troubleshoot snap configuration without downloading the full manifest.

When in doubt about a command, run `snapctl --help` or `snapctl <command> --help`.

### Answering Questions — Lookup Priority

**IMPORTANT: NEVER use web search or fetch remote URLs for Snapser questions.** All Snapser documentation and API specs are bundled locally in this plugin. Always answer from local files only.

When the user asks a question about Snapser, follow this priority order:

1. **Snap API questions** (endpoints, request/response, SDK examples) → read the LOCAL swagger file at `data/snap-swaggers/<snap-name>.swagger3.json`.
2. **Snap feature/concept/config-tool questions** (how does auth work, how do I configure leaderboards, what connectors are available) → read `data/docs/INDEX.md` first — it lists every documentation page with the topic it covers — then read the page(s) it points to.
3. **"What changed / what's new / when did X ship" questions** → read `data/releases/INDEX.md` first, then the specific release file(s) it points to. See "Release Notes" below.

See `skills/snapser-help/SKILL.md` for the full workflow including a term-to-snap-name mapping.

### Local Documentation — `data/docs/`

The `data/docs/` folder contains the full Snapser documentation as `.mdx` files. These are
MDX (Markdown + JSX) — ignore the `import` statements and JSX component tags at the top of
each file; the useful content is the prose, headings, code blocks, and tables below them.

**Always start at `data/docs/INDEX.md`** — a generated map of all 201 pages, grouped by
area, each with the topic it covers. Read the index, pick the page that answers the
question, read that page. Do not grep the whole folder blind, and never read the folder
into context wholesale. (`data/docs/index.mdx` is the docs *landing page* — prose for a
human, not a map. `INDEX.md` is the map.) The index is generated by `scripts/build.py`:
drop a new `.mdx` into `data/docs/` and re-run it — never hand-edit `INDEX.md`.

**Folder map:**

| Path | What's there |
|---|---|
| `data/docs/index.mdx` | Docs landing page — high-level intro |
| `data/docs/overview.mdx` | Platform overview |
| `data/docs/concept.mdx` | Core Snapser concepts (Snaps, Snapends, environments, etc.) |
| `data/docs/ai/` | AI integrations — Cortex, MCP, OpenAI |
| `data/docs/business-intelligence/` | BI dashboards, charts, SQL lab, alerts/reports |
| `data/docs/custom/` | BYOSnap, BYOWS (workstation), BYOGS (game server), BYO data store, BYO external server |
| `data/docs/custom/tools/` | Config tool, profile tool, tool builder, user manager tool |
| `data/docs/guides/samples/` | Sample projects — Unity, Unreal, Roblox, web apps, mobile, e-commerce, social |
| `data/docs/guides/tutorials/` | Step-by-step tutorials — setup snapctl, create Snapend, auth, BYOSnap (basic→advanced), BYOGS, security, cloning, tools |
| `data/docs/infra/` | Infrastructure layer — generic errors, snap index |
| `data/docs/infra/snaps/<snap-name>/index.mdx` | Per-snap overview (what it does, key features) |
| `data/docs/infra/snaps/<snap-name>/config-tools/` | Per-snap config tool docs (web portal settings UI) |
| `data/docs/infra/snaps/auth/connectors/` | Auth connector setup guides — anonymous, Apple, Discord, email, Epic, Facebook, Google, Steam, username/password, X, Xbox |
| `data/docs/resources/cli.mdx` | Snapctl CLI reference |
| `data/docs/resources/marketplace.mdx` | Snap marketplace docs |
| `data/docs/resources/portal/` | Web portal — access management, team settings |
| `data/docs/resources/tools/` | Audit tool, examples |
| `data/docs/snapend/` | Snapend deep-dive — admin tools, dev pipeline, infra-as-code, logs, monitoring, protos, SDKs, WebSocket |
| `data/docs/snapend/networking/` | Gateway, intra-Snapend networking, security |
| `data/docs/snapend/tools/` | API explorer, cluster clone/sync, inspector, user data, user manager, WS tester |

**How to find the right file:**

- If the question is about a specific snap → go to `data/docs/infra/snaps/<snap-name>/`
- If it's about how to configure a snap in the web portal → check `config-tools/` under that snap
- If it's about auth connectors (Google login, Steam, etc.) → `data/docs/infra/snaps/auth/connectors/`
- If it's about BYOSnap/BYOWS/BYOGS → `data/docs/custom/`
- If it's about Snapend architecture, networking, SDKs → `data/docs/snapend/`
- If it's a how-to or tutorial → `data/docs/guides/tutorials/`
- If it's about a sample project → `data/docs/guides/samples/`
- If you're unsure which file → read `data/docs/INDEX.md` and match the question against the topic column. Grep `data/docs/` only if the index leaves you with nothing.

### Release Notes — `data/releases/`

Snapser **platform** release notes, one `.mdx` per release (`data/releases/1.12.0.mdx`),
covering what shipped in the platform, snaps, Web App, snapctl, and SDKs. Use them to
answer "what's new", "did anything change in <snap>", "when did <feature> ship", or
"what should I know before upgrading my SDK".

**Always start at `data/releases/INDEX.md`** — a generated lookup table with every
release, its date, its sections, and a snap → releases reverse index. Read it first,
then open only the release file(s) it points you to. Never grep all 30 release files
blind, and never read them all into context.

> **HARD RULE — release notes are read-only, user-facing information.**
> They exist to tell a human what changed. They are NEVER an input to building or
> changing anything. Do not take snap versions, manifest structure, `settings` values,
> API shapes, or command flags from a release note. Structure still comes only from
> `snapctl snapend-manifest ...`, settings only from the Admin SDK, API shapes only from
> `data/snap-swaggers/`, and the live snap catalog only from `snapctl snaps enumerate`.
> A version number mentioned in a release note is **not** a version to pin.

The index is generated by `scripts/build.py`. To add a release, drop the new `.mdx` into
`data/releases/` and re-run `python3 scripts/build.py` — never hand-edit `INDEX.md`.

---

## Important Rules

> ### HARD RULE — structure and settings are two separate phases. Never combine them.
>
> This is non-negotiable. Building/changing a backend's snaps is one phase; changing
> snap settings is a completely separate phase. They are never done in the same step.
>
> **Phase 1 — Structure (snaps & features).** The ONLY way to build or change a
> manifest is `snapctl snapend-manifest create/update/sync/upgrade`. Bring the Snapend
> online with `snapctl snapend create` / `snapctl snapend apply` (always `--blocking`).
> The manifest you create or apply MUST have an empty `settings` array. Do NOT put snap
> settings into the manifest.
>
> **Phase 2 — Settings.** Once the Snapend is live, change EVERY snap setting through
> the bundled Admin SDK by following `skills/configure-snap-settings/SKILL.md`. The
> Admin SDK is the *only* sanctioned way to change a setting.
>
> **After every settings change, immediately download the manifest to the project
> root:** `snapctl snapend download --snapend-id $id --category snapend-manifest --format json --out-path .`
> The downloaded manifest is the canonical, version-controllable record — it is an
> OUTPUT of the Admin SDK phase, never a hand-authored input.
>
> **Never manipulate the manifest with any other tool.** No `python`, no `jq`, no
> `sed`, no here-doc scripts, no hand-editing. In particular, never assemble a
> `settings` block — even one grounded in the Admin SDK source or the config docs — and
> write/inject it into the manifest. That it produces "valid JSON" or that it worked
> once does not make it allowed: settings ONLY change via live Admin SDK calls.
>
> **Configure-only requests** (the snap already exists and the user just wants to
> change its settings): skip Phase 1 entirely — go straight to the Admin SDK against the
> live Snapend, then download the manifest to the project root.

**Do:**
- **Always fetch snaps dynamically** using `snapctl snaps enumerate`. Never assume snap names or IDs.
- **Always use `--blocking`** when creating or updating a Snapend so the agent waits for it to be live before proceeding.
- **Always validate** the BYOSnap profile before publishing: `snapctl byosnap validate-profile`.
- **Default to DEVELOPMENT** for any new backend unless the user explicitly says otherwise.
- **Auth snap is always included** — never ask the user whether they want it.
- **Configure snap settings ONLY via the Admin SDK, never by editing or scripting manifest JSON.** For any settings change (auth methods, leaderboards, storage keys, profiles, statistics, trackables, inventory, fleets), follow `skills/configure-snap-settings/SKILL.md`: read its config-cheatsheet.md first, use the **plugin-bundled Python SDK** at `data/admin-sdk/sdk-python` optimistically (no upfront version checks), apply the change to the live Snapend, then download the manifest to the project root. See the HARD RULE at the top of this section. Handle version mismatches only when the server rejects a call — the skill's error-handling ladder covers upgrade / matched-SDK download / web portal Config tool.

**Validate:**
- **Snapend names:** Max 20 characters, alphanumeric and dashes only, must start with a letter, must be unique per environment. No spaces.
- **BYOSnap IDs:** Must start with `byosnap-`. Validate this before running any BYOSnap command.
- **Versions:** Must be semantic — e.g. `v0.0.1`, `v1.0.0`. Remind the user if they pass an invalid format.

**Don't:**
- Don't guess error meanings — look up the code in `skills/error_codes.md` and use the recovery guidance there.
- Don't hardcode snap names — always run `snapctl snaps enumerate` first.
- Don't suggest staging/production unless the user asks for it.
- Don't skip `--blocking` — without it, subsequent steps may fail because the Snapend isn't ready.
- **Don't use web search or fetch remote URLs for anything Snapser-related.** All documentation and API specs are bundled locally in this plugin at `data/docs/` and `data/snap-swaggers/`. If a user asks a question about Snapser, read the local files — never search the web or fetch snapser.com.
- **Don't write, edit, or inject manifest JSON with any tool** — not from scratch, and not with `python`, `jq`, `sed`, or a here-doc script. The manifest is produced and modified ONLY by `snapctl snapend-manifest create/update/sync/upgrade`. Never construct `service_definitions`/`feature_definitions` manually, and never assemble a `settings` block (even one grounded in the Admin SDK source or config docs) and write it into the manifest — settings go through the Admin SDK against the live Snapend. A manifest passed to `snapend create`/`apply` must have an empty `settings` array.
- **The bundled Admin SDK is the default; downloads are a fallback.** The plugin ships the Python Admin SDK at `data/admin-sdk/sdk-python` (target snap versions in `data/admin-sdk/VERSION.md`). Only use `snapctl admin-sdk download` when a Snapend runs deliberately pinned older snaps — pin `--snaps` to the deployed `name:version` pairs (required `v` prefix, e.g. `auth:v1.12.0`; only versions with `has_admin=true` are accepted).

---

## Error Handling

See `skills/error_codes.md` for the complete error code reference with recovery actions.

When a command fails:
1. Check the exit code against `skills/error_codes.md`
2. Explain the error clearly to the user using the description and suggested recovery
3. If the error is a timeout (codes 64, 67, 70, 74, 79), suggest retrying and checking status with `snapctl snapend enumerate`
4. If the error is a permission issue (codes 26, 36, 39, 42, 52), ask the user to verify their API key scopes
5. If the error persists after recovery, suggest contacting Snapser support

---

## Skill Index

Every skill file lives in `skills/`. **Always read the skill file before executing a workflow** —
it contains the detailed step-by-step instructions.

### Setup & Onboarding

| Skill | When to use |
|---|---|
| `skills/setup-snapctl/SKILL.md` | User needs to install or configure `snapctl` for the first time |
| `skills/create-application/SKILL.md` | User needs to create a new Snapser application space |
| `skills/full-game-backend-wizard/SKILL.md` | User wants a complete end-to-end setup — snaps + BYOSnap + SDK in one guided flow. Use when they say "set up everything" or "complete backend" |
| `skills/build-web-game/SKILL.md` | User wants to build a playable browser game with a Snapser backend — end-to-end from game code to live integration. Use when they say "build me a game", "make a web game", "prototype a game". **Web/browser games only** — for Unity/Unreal/Roblox redirect to `skills/full-game-backend-wizard/SKILL.md` |

### Creating & Managing Backends

| Skill | When to use |
|---|---|
| `skills/create-backend/SKILL.md` | User wants a backend built entirely from Snapser's snap catalog |
| `skills/update-backend/SKILL.md` | User wants to add/remove snaps, upgrade snap versions, or modify an existing Snapend |
| `skills/configure-snap-settings/SKILL.md` | User wants to change snap settings (auth connectors, leaderboards, storage keys, etc.) on a live Snapend — the Admin SDK workflow |
| `skills/clone-snapend/SKILL.md` | User wants to clone a Snapend to a different environment (e.g. dev → staging). Note: stage → prod is not supported via CLI — web portal only |
| `skills/snapend-status/SKILL.md` | User wants to check the health, state, or details of a Snapend |
| `skills/download-sdk/SKILL.md` | User wants to download an SDK, protobuf files, or manifest for a Snapend |

### BYOSnap (Custom Microservices)

| Skill | When to use |
|---|---|
| `skills/create-byosnap/SKILL.md` | User wants to create a custom microservice from scratch (scaffold, profile, code) |
| `skills/generate-byosnap-profile/SKILL.md` | User needs to create or edit a `snapser-byosnap-profile.json` file |
| `skills/direct-deploy-byosnap/SKILL.md` | User wants fast iteration — deploy BYOSnap code directly to a dev Snapend without publishing |
| `skills/publish-byosnap/SKILL.md` | User wants to publish a BYOSnap to the Snapser registry with a version, making it available for any Snapend |
| `skills/attach-workstation/SKILL.md` | User wants to use BYOWS for local debugging. **This is an informational skill only — do NOT run `snapctl byows` commands on behalf of the user.** Provide copy-paste instructions instead |

### Game Server Fleets (BYOGS)

| Skill | When to use |
|---|---|
| `skills/byogs-publish/SKILL.md` | User wants to publish a custom game server image to Snapser |
| `skills/test-fleet-e2e/SKILL.md` | User wants to deploy a game server fleet, set up game server hosting, or test a fleet end-to-end. Covers the full flow: publish image → create Snapend with fleet → verify |

### Reference Files (Not Workflows)

These are data and reference files that other skills read — don't use them as standalone workflows:

| File | Purpose |
|---|---|
| `skills/backend_templates.md` | Recommended snap sets by game/app type (arcade, RPG, battle royale, SaaS, etc.) |
| `skills/error_codes.md` | Complete error code reference with recovery actions |
| `skills/snapctl_commands.md` | Complete snapctl CLI command reference |
| `skills/snapser-help/SKILL.md` | Workflow for answering questions — routes to local docs and swagger files |
| `data/docs/INDEX.md` | Generated map of all 201 documentation pages — path → topic, grouped by area. **Start here for any Snapser docs question**, then read the page it points to. |
| `data/docs/` | Full Snapser documentation (201 `.mdx` files). Reach it through `data/docs/INDEX.md`; the folder map in "Local Documentation" above is the coarse view. |
| `data/snap-swaggers/*.swagger3.json` | OpenAPI 3.0 specs for each snap's API endpoints. **Read these for any snap API question.** |
| `data/releases/INDEX.md` | Generated index of the platform release notes in `data/releases/`. **Start here for any "what changed / what's new" question.** Read-only user-facing info — never an input to manifests, settings, or version pinning. |
| `data/admin-sdk/sdk-python` | Bundled Python Admin SDK for configuring snap settings on a live Snapend (see `data/admin-sdk/VERSION.md` for target snap versions) |
| `skills/configure-snap-settings/config-cheatsheet.md` | Integration-tested gotchas for Admin SDK settings calls (base URL, enums, PUT-vs-PATCH, int64 wire format, per-snap landmines). **Read before writing any settings script.** |

---

## Workflows

The workflows below are quick summaries. **Always read the linked skill file for full instructions.**

### Workflow 1 — Creating a Backend with Snapser Snaps

**Skill:** `skills/create-backend/SKILL.md`
**When:** The user wants a backend built entirely from Snapser's snap catalog.

```
1. List available snaps → recommend a set based on game/app type (see skills/backend_templates.md)
2. Gather settings requirements → ask the user what to enable per snap
   (setting semantics live in data/docs/infra/snaps/<snap-name>/)
3. Generate base manifest → snapctl snapend-manifest create (NEVER write from
   scratch; do NOT edit it)
4. Create the Snapend → snapctl snapend create --manifest --blocking
5. Apply settings via the Admin SDK → skills/configure-snap-settings/SKILL.md
6. Download the manifest to the project root → snapctl snapend download
7. Download the SDK → snapctl snapend download; user integrates it into their game/app
```

### Workflow 2 — Building a BYOSnap

**Skill:** `skills/create-byosnap/SKILL.md`
**When:** The user wants to create a custom microservice from scratch.

```
1. Scaffold from Snapser's community repo, ALWAYS from the core/ directory:
   https://github.com/snapser-community/snapser-byosnaps/tree/main/core
2. core/ has functionally identical starter scaffolds in seven languages:
   Python, Go, Node-TypeScript, C#, Rust, Java, Kotlin
   (basic/, inter/ and advanced/ exist for the documentation tutorials — do not scaffold from them)
3. Pick the scaffold matching the user's preferred language; if none matches,
   rewrite the closest one in their language keeping the same route coverage
4. Rename the single `byosnap-core` Snap-id constant to the user's BYOSnap ID —
   every externally reachable endpoint is prefixed `<prefix>/<byosnap-id>`
   (e.g. `/v1/byosnap-my-code/...`); both values live in the BYOSnap profile file
5. Eventbus is NOT a BYOSnap requirement. The scaffolds' eventbus hooks are
   best-effort no-ops when the eventbus snap is absent. Only add the eventbus
   snap if the user explicitly wants realtime events/webhooks — a minimal
   BYOSnap Snapend is auth + the BYOSnap.
6. If the BYOSnap must call other snaps, download the Snapser internal SDK in the
   BYOSnap's language (snapctl snapend download --category sdk --type internal)
   and call other snap APIs through it.
```

**If still developing (dev mode) — fast iteration:**
```
→ Direct-deploy for instant feedback: skills/direct-deploy-byosnap/SKILL.md
→ Optionally attach BYOWS for live local debugging: skills/attach-workstation/SKILL.md
```

**If ready to publish — share with org:**
```
→ Publish the BYOSnap: skills/publish-byosnap/SKILL.md
→ Update the Snapend: skills/update-backend/SKILL.md
```

### Workflow 3 — Snapser Snaps + Custom BYOSnap

**Skill:** `skills/full-game-backend-wizard/SKILL.md`
**When:** The user wants a backend with both Snapser snaps and their own custom microservice,
or wants the complete end-to-end setup experience.

```
1. Follow Workflow 1 to create the base backend
2. Ask the user if they have an existing published BYOSnap or need to build one
3. If building new → follow Workflow 2
4. If using existing → get the name and version, create a manifest including it,
   and apply it to the Snapend
```

### Workflow 4 — Game Server Fleet (BYOGS)

**Skill:** `skills/test-fleet-e2e/SKILL.md`
**When:** The user wants to deploy a game server fleet, set up game server hosting,
or test their game server end-to-end on Snapser. This includes users who say things like
"I want a game server fleet", "help me deploy my game server", "set up game server hosting",
or "test my fleet."

```
1. Publish the game server image → skills/byogs-publish/SKILL.md
2. Prepare a Snapend manifest with auth + game-server-fleets (sample manifest is in the skill)
3. Create the Snapend → snapctl snapend create --blocking
4. User verifies fleet is running in the Snapser web app
```

If the user doesn't have a game server yet, guide them through `skills/byogs-publish/SKILL.md` first
which includes scaffolding a game server project.

### Workflow 5 — Build a Web Game with Snapser

**Skill:** `skills/build-web-game/SKILL.md`
**When:** The user wants to build a playable browser game from scratch with a Snapser
backend. This includes users who say things like "build me a game", "make a web game",
"create a game with leaderboards", or "prototype a game." **Web/browser games only.**
If they ask for Unity, Unreal, or Roblox, redirect to `skills/full-game-backend-wizard/SKILL.md`.

```
1. Ask what kind of game → clicker, quiz, arcade, puzzle, etc.
2. Build a single-file HTML/JS game → playable in the browser with no backend
3. User tests and approves the base game
4. Create the Snapend with the right snaps → auth + leaderboards/storage/etc.
5. Download the web-ts SDK → bundle to one minified JS with esbuild
   (see skills/build-web-game/SKILL.md Stage 5; do NOT use web-js for unbundled games)
6. Wire the SDK into the game → auth login, leaderboard, save/load
7. User tests the full game with live backend
```

### Modifying an Existing Snapend

**Skill:** `skills/update-backend/SKILL.md`

If the user already has a Snapend and wants to change it:

- **Add/remove snaps:** `snapctl snapend update --snapend-id $id --add-snaps snap1,snap2 --blocking`
- **Apply a full manifest:** `snapctl snapend apply --snapend-id $id --manifest $path --blocking`
- **Check current state:** `snapctl snapend enumerate`
- **Clone to another environment:** `skills/clone-snapend/SKILL.md`
- **Check Snapend health:** `skills/snapend-status/SKILL.md`
