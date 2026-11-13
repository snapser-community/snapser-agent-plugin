<!-- GENERATED FILE — DO NOT EDIT. -->
<!-- Edit source/CONTEXT.md and run `python3 scripts/build.py`. -->

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

## First: Read the Core Rules

Before running any Snapser command, read `skills/core-rules.md` and do the prerequisite
check in it. That file is the one canonical copy of the rules every workflow shares:

- the `snapctl validate` prerequisite check
- the Agent Mode / Guide Mode choice
- the HARD RULE that keeps structure (manifest) and settings (Admin SDK) in separate phases
- the command rules — `--blocking`, `--application-id`, output path flags, input validation
- error handling

Every skill file points to it as well. All `skills/` and `data/` paths in this file and
in the skill files start at the plugin root — the folder that contains the `skills/` and `data/` directories.

**Do not proceed with any workflow until the prerequisite check in `skills/core-rules.md` passes.**

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
| `snapctl inspect logs` | Download deployment, snap, or fleet logs for a Snapend |
| `snapctl inspect monitor` | Get infra graphs (CPU, memory, latency, RPS, errors) for a Snapend's snaps or fleets |
| `snapctl inspect metrics` | Get business metrics (DAU, MAU, installs, revenue, locations) for a Snapend — needs the `analytics` snap |
| `snapctl login` | Log in via the browser; mints and stores the API key automatically |
| `snapctl admin-sdk download` | Fallback download of the Admin SDK (the plugin bundles it at `data/admin-sdk/`) |
| `snapctl snapend-manifest create` | Generate a base manifest from a snap list |

See `skills/snapctl_commands.md` for the complete command reference.

For the `--application-id` and output path flag rules (`--out-path` vs
`--out-path-filename`), see `skills/core-rules.md`.

Useful snapctl command for inspecting live snap settings on an existing Snapend:
```bash
snapctl snap-config get-config --snaps auth,leaderboards --snapend-id $snapendId
```
This pulls the current settings for specific snaps from a deployed Snapend. Use it to inspect, verify, or troubleshoot snap configuration without downloading the full manifest.

For logs, infra metrics (CPU, memory, latency, RPS), or business metrics (DAU, MAU, installs, revenue) on a live Snapend — as opposed to settings — use `snapctl inspect`. See `skills/inspect-snapend/SKILL.md` for the full workflow.

When in doubt about a command, run `snapctl --help` or `snapctl <command> --help`.

### Answering Questions

**IMPORTANT: NEVER use web search or fetch remote URLs for Snapser questions.** All Snapser
documentation, API specs, and release notes are bundled locally in this plugin under `data/`.

For any Snapser question, follow `skills/snapser-help/SKILL.md`. It holds the lookup
priority (swagger files for API questions, `data/docs/INDEX.md` for feature and
configuration questions, `data/releases/INDEX.md` for "what changed" questions), the
`data/docs/` folder map, and the rule that release notes are read-only information —
never an input to a manifest, a setting, or a version pin.

---

## Important Rules

The rules live in `skills/core-rules.md`. Read that file before any workflow. In short:

- **Structure and settings are two separate phases (HARD RULE).** Build and change the
  manifest only with `snapctl snapend-manifest ...`; change settings only through the
  Admin SDK on the live Snapend. Never write, edit, or script manifest JSON.
- **Download the manifest to the project root after every Snapend mutation.**
- **Look up every error code** in `skills/error_codes.md` — do not guess.

`skills/core-rules.md` has the full text of these rules and the command rules.

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
| `skills/inspect-snapend/SKILL.md` | User wants to diagnose a Snapend: view deployment/snap/fleet logs, or check infra metrics (CPU, memory, latency) or business metrics (DAU, MAU, revenue) |
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
| `skills/core-rules.md` | The rules every workflow shares — prerequisite check, execution mode, the manifest/settings HARD RULE, command rules, error handling. **Read before any workflow.** |
| `skills/backend_templates.md` | Recommended snap sets by game/app type (arcade, RPG, battle royale, SaaS, etc.) |
| `skills/error_codes.md` | Complete error code reference with recovery actions |
| `skills/snapctl_commands.md` | Complete snapctl CLI command reference |
| `skills/snapser-help/SKILL.md` | Workflow for answering questions — routes to local docs and swagger files |
| `data/docs/INDEX.md` | Generated map of all 201 documentation pages — path → topic, grouped by area. **Start here for any Snapser docs question**, then read the page it points to. |
| `data/docs/` | Full Snapser documentation (201 `.mdx` files). Reach it through `data/docs/INDEX.md`; the folder map in `skills/snapser-help/SKILL.md` is the coarse view. |
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
- **Diagnose issues (logs/metrics):** `skills/inspect-snapend/SKILL.md`
