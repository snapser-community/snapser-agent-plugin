# Snapser Plugin — Multi-Platform + Modernization Plan

Four workstreams: (A) one repo that ships to Claude, Codex, and OpenCode; (B) BYOSnap examples move from `advanced/` to `core/`; (C) `snapctl login` replaces manual API key setup; (D) admin-sdk becomes the primary way to configure snap settings, replacing hand-injection of JSON into manifests.

Decisions already made (confirmed with AJ):

- Single repo, single source of truth, with a build script that generates per-platform distributions.
- Admin-sdk applies settings via **live Snapend API calls**; after every settings change we download the manifest to the project root as the record.
- `snapctl login` is browser-based (RFC 8628 device flow): agent runs it, user approves in browser, key is minted server-side and stored at `~/.snapser/config` automatically. `--paste` / `--api-key` remain as the manual/CI fallback.
- `data/snap-settings/*.md` are **deleted entirely**. The admin-sdk covers all 7 snaps they documented. For the remaining snaps that don't yet have `has_admin=true` (admin-sdk covers ~10–12 of 33 this release, all soon), the fallback is the **web portal Config tool** (documented in `data/docs/infra/snaps/<snap>/config-tools/`) — not manifest JSON injection.
- BYOSnap examples: agents use `core/` **exclusively**; `basic/inter/advanced` are tied to doc tutorials only.
- Version strings in `--snaps` require the `v` prefix (`auth:v1.0.0`).
- Admin SDK is not tied to a Snapend — its methods take the Snapend id at call time; the download is scoped by `snap:version`.
- Agent discovers SDK methods by reading the downloaded SDK source — no per-method docs shipped in the plugin (for now).

All snapctl behavior below is **verified against the snapctl repo source** (`snapctl/commands/login.py`, `admin_sdk.py`, `main.py`, `docs/DESIGN-login-device-flow.md`) — no longer assumptions.

---

## Workstream A — One repo, three platforms

### A1. Restructure to a single source of truth

Current problem: `CLAUDE.md` and `AGENTS.md` are near-identical 450-line copies (they already drifted by 2 lines). Skills and data are platform-neutral already.

Target layout:

```
source/
  CONTEXT.md            ← the single master context doc (today's CLAUDE.md content)
skills/                 ← unchanged, shared by all platforms
data/                   ← unchanged, shared by all platforms
scripts/
  build.py (or .sh)     ← generates dist/ for all three platforms
dist/                   ← generated, gitignored OR committed (decide at exec time; committed
  claude/                 is simpler for marketplace installs that point at a repo path)
  codex/
  opencode/
.claude-plugin/         ← stays at root so this repo remains directly installable in Claude
CLAUDE.md               ← generated from source/CONTEXT.md (do not hand-edit; header comment says so)
AGENTS.md               ← generated from source/CONTEXT.md (Codex + OpenCode both read AGENTS.md)
```

Build script responsibilities:

1. Generate `CLAUDE.md` and `AGENTS.md` from `source/CONTEXT.md` (platform-specific header/footer tweaks only — e.g. skill-invocation phrasing differs: Claude auto-triggers skills; Codex/OpenCode need "read `skills/<name>/SKILL.md` before doing X" wording).
2. Assemble `dist/codex/` and `dist/opencode/` packages (see A2/A3).
3. Fail the build if a skill referenced in CONTEXT.md doesn't exist on disk (link check).

### A2. Codex distribution

Codex reads `AGENTS.md` from the repo/project root. There is no skill-autoload mechanism equivalent to Claude plugins, so:

- `dist/codex/` = `AGENTS.md` + `skills/` + `data/` (skills become plain referenced markdown; AGENTS.md's Skill Index already instructs the agent to read skill files before executing — that pattern works as-is on Codex).
- Installation story: user clones/copies the folder into their project, or we document adding it as a git submodule / running an install script that copies `AGENTS.md` and folders into their project root.
- **Exec-time verification:** check current Codex docs for any newer plugin/packaging format (Codex evolves fast; if it now supports a native skills/plugin format, use it).

### A3. OpenCode distribution

OpenCode also honors `AGENTS.md`, and additionally has its own config dir (`.opencode/` with commands/agents/plugins).

- `dist/opencode/` = `AGENTS.md` + `skills/` + `data/`, plus optionally `.opencode/command/*.md` wrappers for the top workflows (create-backend, create-byosnap, setup-snapctl) so users get slash-command ergonomics.
- **Exec-time verification:** confirm current OpenCode plugin/command format from its docs before writing the wrappers.

### A4. Repo hygiene

- Delete stray files: `.DS_Store`, `data/.DS_Store`, and `data/snapend-byosnaptest-manifest*.json` (confirmed harmful — see B3: they're the source of the "eventbus is required" hallucination).
- README: rewrite install section with three tabs — Claude (marketplace/plugin install), Codex, OpenCode.
- Bump plugin version to `0.2.0` in `.claude-plugin/plugin.json` and `marketplace.json` when B–D land.

---

## Workstream B — BYOSnap examples: `advanced/` → `core/`

New canonical source: `https://github.com/snapser-community/snapser-byosnaps/tree/main/core` with examples for **Go, Java, Kotlin, Node-TypeScript, Python, Rust, C#**.

Files to change:

| File | Change |
|---|---|
| `skills/create-byosnap/SKILL.md` | Point repo links and `cp -r snapser-byosnaps/advanced/byosnap-go` scaffold commands at `core/`. Replace "four examples" language with the seven core languages. Replace the "use Python advanced example for endpoint coverage" instruction with the core Python example. |
| `skills/full-game-backend-wizard/SKILL.md` | Same repo-path updates in its clone/scaffold step. |
| `source/CONTEXT.md` (→ CLAUDE.md/AGENTS.md) | Workflow 2 currently says "three categories: basic, inter, advanced" and links the advanced Python `app.py` — rewrite around `core/` and the seven languages. |
| Endpoint prefix rule | CONTEXT.md says all endpoints need prefix `/v1/byosnap-advanced` — generalize to `/<prefix>/<byosnap-id>` where both come from the BYOSnap profile, and verify what the core examples actually use. |

Exec-time verification: `git clone` or fetch the core repo tree, confirm exact folder names (e.g. `core/byosnap-node-ts` vs `core/byosnap-typescript`), the endpoint prefix convention used, and whether each example ships a Dockerfile + profile. Do **not** guess folder names in the skill files.

`basic/`, `inter/`, `advanced/` remain in the community repo but are tied to doc tutorials only — the plugin references `core/` exclusively.

### B2. Inter-snap communication guidance

If a BYOSnap needs to call other snaps, the flow is: download the **Snapser internal SDK** in the BYOSnap's language, add it to the BYOSnap, and call other snap APIs through it. (Verified: `--type internal` is a supported SDK access type in snapctl; confirm the exact `snapctl snapend download` invocation at exec time.)

Add this as an explicit section in `skills/create-byosnap/SKILL.md` so agents don't invent their own inter-snap mechanism.

### B3. Kill the "eventbus is required" hallucination

Root cause found: `data/snapend-byosnaptest-manifest.json` and `data/snapend-byosnaptest-manifest-old.json` are leftover test manifests that pair a BYOSnap with the `eventbus` snap — an agent hunting for a BYOSnap manifest example finds these and copies the pattern. Reinforced by `data/docs/custom/bring-your-own-snap.mdx`, which features the eventbus realtime tutorial prominently.

Fix:

1. Delete both `snapend-byosnaptest-manifest*.json` files from `data/` (already flagged in A4; now confirmed harmful, not just untidy).
2. Add an explicit line to `skills/create-byosnap/SKILL.md` and CONTEXT.md Workflow 2: "**Eventbus is NOT a BYOSnap requirement.** Only add the eventbus snap if the user explicitly wants realtime events/webhooks. A minimal BYOSnap Snapend is auth + the BYOSnap."

---

## Workstream C — `snapctl login`

Verified behavior (from snapctl source + `docs/DESIGN-login-device-flow.md`):

- `snapctl login` → device flow: prints a short `XXXX-XXXX` code + verification URL, opens the browser (`webbrowser.open`), user clicks **Activate**, backend mints an API key that flows back and is saved to `~/.snapser/config` (permissions 600). The user never sees the key.
- **Idempotent**: if the stored key is still valid it prints "Already logged in as …" and exits — safe for the agent to run unconditionally as a prerequisite step. `--force` re-mints deliberately.
- Invalid/expired keys self-heal into a new browser login.
- Flags: `--paste` or `--api-key <key>` (manual/CI Tier-1 flow), `--profile`, `--env dev|devtwo|playtest|prod`, `--portal-endpoint` (enterprise, mutually exclusive with `--env`), `--key-name`, `--no-validate`, `--force`, `--quiet`.
- Works headless: code + URL are always printed even if no browser opens.
- There is also `snapctl logout`. Login errors: codes **110** (`SNAPCTL_LOGIN_ERROR`) and **111** (`SNAPCTL_LOGIN_FLOW_ERROR`) — add to `skills/error_codes.md`.

Agent pattern to encode in the skills: `snapctl validate` fails on key → run `snapctl login`, tell the user a browser window will open (or give them the printed URL + code), wait for activation, re-run `snapctl validate`.

Files to change:

| File | Change |
|---|---|
| `skills/setup-snapctl/SKILL.md` | Rewrite Phase 3: primary path is `snapctl login` (device flow above). Fallback for no-browser cases: `snapctl login --paste` or `--api-key` with a key from the Developer Center — this replaces the "write `~/.snapser/config` by hand" instructions entirely. Keep "never echo the key" rule. |
| `source/CONTEXT.md` | Prerequisites section: on `snapctl validate` API-key failure → run `snapctl login` (instead of directing user to the web portal). |
| `skills/snapctl_commands.md` | Add `snapctl login` / `snapctl logout` to the command reference with the flags above; demote the three manual key-config methods to a "fallback / CI" subsection built around `login --paste` / `--api-key` rather than hand-editing config files. |
| `README.md` | Requirements section: `snapctl login` becomes the setup step. |
| `skills/error_codes.md` | Add codes 110 and 111 with recovery guidance (retry login, check browser/URL, fall back to `--paste`). |

---

## Workstream D — Admin SDK for snap settings (the big one)

### D1. The new settings model

Old model (being **deleted**): read `data/snap-settings/<snap>.md` → hand-inject JSON blocks into the generated manifest's `settings[]` → `snapend create/apply`. Fragile: JSON surgery, version-matching foot-guns.

New model (verified against `snapctl/commands/admin_sdk.py`):

```
1. snapctl snaps enumerate
     → services[].versions[] each carry has_admin (per snap VERSION, not per snap)
     → note each selected snap's deployed version and its has_admin flag
2. For snaps with has_admin=true:
     snapctl admin-sdk download --format web-ts --type api-key \
       --snaps auth:v1.0.0,storage:v1.2.0 \
       --out-path ./.snapser/admin-sdk
     → --out-path is a DIRECTORY (consistent with other download commands)
     → the `v` prefix on versions is required
     → snapctl validates every name:version pair against enumerate and rejects
       pairs without admin support — precise per-pair error messages
     → lands as snapser-admin-sdk-<format>-external-api-key[-<httplib>].zip → unzip in place
3. Agent unzips, reads the SDK source to discover available methods (no method
     docs shipped), writes/runs a script against the LIVE Snapend.
4. After EVERY settings mutation:
     snapctl snapend download --category manifest --out-path .   ← manifest lands at
     project root and is the canonical record / version-controllable artifact
```

**Verified against a real downloaded SDK** (typescript-fetch, inspected 2026-07-06):

- It's a bare openapi-generator **typescript-fetch** source tree — `index.ts`, `runtime.ts`, `apis/<Snap>ServiceApi.ts`, `models/` (~170 typed models). No `package.json`, no README: the skill must scaffold a tiny runner (a `package.json` + `npx tsx script.ts`; zero runtime deps since fetch is native in Node 18+).
- One API class per snap. The sample covers 9 snaps: Auth, GameServerFleets, Guilds, Leaderboards, Profiles, RemoteConfig, Statistics, Storage, Trackables — a superset of the 7 old snap-settings files, confirming deletion is safe.
- Method shape: `authAdminEnableAnonLogin({ clusterId, environment, apiKey, body })` — **snapend id (`clusterId`), environment, and the API key are per-call required params**; the key goes out as an `Api-Key` header. The agent reads the key from `~/.snapser/config` (what `snapctl login` stored) and must never hardcode it in the script.
- Methods are typed and granular (`enable*/toggle*/update*/get*/delete*` per connector/feature) — exactly the JSON-surgery replacement we wanted; request bodies are typed models, not raw JSON.
- Baked-in `BASE_PATH` is authoritative: the download service bakes the correct gateway URL for the environment/enterprise mode it was downloaded from (the sample shows the dev gateway because admin-sdk is in internal testing). **The agent uses the SDK's default basePath as-is — never overrides it.**

Notes:

- Default `--format` is **`python`** (DECISION REVISED after comparing both real SDKs): Python is guaranteed present (snapctl itself requires it), and the Python SDK is pydantic v2 with `@validate_call` runtime validation on every method — stricter in practice than typescript-fetch run via `npx tsx`, which skips type-checking and does no runtime validation. Skills instruct Python only.
- `--type api-key` is the type for this flow (`external` access + `api-key` auth).
- Error codes: **113** (`SNAPCTL_ADMIN_SDK_GENERIC_ERROR`), **114** (`SNAPCTL_ADMIN_SDK_DOWNLOAD_ERROR`) → add to `skills/error_codes.md`.

Snaps whose deployed version has `has_admin=false` (this release covers ~10–12 of 33): the agent configures nothing programmatically — it directs the user to the **web portal Config tool** for that snap and points at `data/docs/infra/snaps/<snap>/config-tools/`. No manifest-injection fallback, no snap-settings files.

### D1b. Decision — bundle the admin SDK inside the plugin's `data/` folder?

AJ raised: once admin-sdk covers all snaps, we could ship it in `data/` and skip the download step. Recommendation: **don't bundle yet; download-on-demand with a local cache.** Reasons:

1. The SDK is generated per `snap:version`, and settings must match the version actually deployed in the user's Snapend. A bundled SDK pins whatever versions existed at plugin release; users' Snapends will run newer (or older) snap versions the moment Snapser ships one, and the plugin's release cadence would become a correctness dependency.
2. `snapctl` already validates the requested pairs against live enumerate — downloading is the mechanism that guarantees SDK ↔ deployed-version agreement.
3. Bundling all snaps × languages bloats the plugin; bundling one language forecloses the choice.
4. The download service bakes the correct gateway `BASE_PATH` into the SDK per environment/enterprise mode — a bundled SDK can't know which gateway the user targets, so bundling would reintroduce a config step the download eliminates.

Mitigation for the download cost: cache at `~/.snapser/admin-sdk/<snap>-<version>/` (or project-local `./.snapser/admin-sdk/`) and skip the download when the needed snap:version is already present. Revisit bundling if Snapser starts shipping a version-stable "latest" admin SDK artifact — at that point put it in `data/` and keep download as the version-mismatch escape hatch. **AJ to confirm or override.**

### D2. New skill: `skills/configure-snap-settings/SKILL.md`

Create one dedicated skill that owns the admin-sdk workflow end to end, so other skills can delegate to it instead of each re-explaining it. Contents:

- When to use (any settings change on a snap version with `has_admin=true`).
- SDK download recipe incl. version pinning from `snaps enumerate` output (never hardcode versions; `v` prefix required), storage/cache location `./.snapser/admin-sdk/`, unzip step, and a `.gitignore` entry recommendation for it.
- Runner scaffold: the SDK is bare TS source — the skill ships a minimal `package.json` + `npx tsx` recipe (Node 18+, zero deps) and a worked example script.
- Auth + targeting: read the API key from `~/.snapser/config` at runtime (never hardcode/echo it); pass `clusterId` (snapend id), `environment`, and `apiKey` per call; use the SDK's baked-in `BASE_PATH` as-is (it's minted correctly per environment at download time).
- How to discover operations: read `apis/<Snap>ServiceApi.ts` method signatures and the typed models directly.
- Mandatory post-step: download manifest to project root after every change.
- Error handling (codes 113/114) + fallback when `has_admin` is false or download fails: direct the user to the web portal Config tool for that snap.

### D3. Changes to existing skills

| File | Change |
|---|---|
| `skills/create-backend/SKILL.md` | Rework Phases 2b/3: gather *what* the user wants configured (auth methods, leaderboard names, storage keys) up front as before → generate base manifest with **empty settings** → `snapend create --blocking` → delegate to configure-snap-settings skill → download manifest to project root. Delete all snap-settings references and the version-match injection instructions. |
| `skills/update-backend/SKILL.md` | Settings-change path routes through configure-snap-settings; keep add/remove-snaps flow; end with manifest download. |
| `skills/build-web-game/SKILL.md` | Replace the snap-settings recipe phase: the *what* (anonymous auth, a global leaderboard, save/load storage keys) moves inline into the skill; the *how* delegates to configure-snap-settings. |
| `skills/full-game-backend-wizard/SKILL.md` | Same rework as create-backend step 6. |
| `skills/snapctl_commands.md` | Add `snapctl admin-sdk download` reference (verified flags: `--format`, `--type`, `--http-lib`, `--snaps name:vX.Y.Z,...`, `--out-path <dir>`). Extend the flag-disambiguation rule: admin-sdk uses `--out-path` (directory). |
| `skills/error_codes.md` | Add codes 113/114 with recovery guidance. |
| `data/snap-settings/` | **Delete the directory.** Before deleting, port any value-semantics recipes worth keeping (e.g. anonymous-auth defaults for web games, XP-ladder shapes) inline into the skills that used them. |
| `source/CONTEXT.md` | Update: Important Rules (drop "read snap-settings" + version-match injection rules; add admin-sdk rule + "manifest at project root after every mutation", extending keep-manifests-in-sync), Workflow 1 steps, Skill Index (add configure-snap-settings), Reference Files table (drop snap-settings row). |

### D4. Remaining exec-time verification

1. ~~Unzipped SDK layout / auth / snapend-id passing~~ — resolved by inspecting the real typescript-fetch SDK (see D1).
2. ~~Exact `--format` string~~ — resolved: `web-ts` (defaults to `--http-lib fetch`). ~~basePath derivation~~ — resolved: the download bakes in the correct URL per environment/enterprise mode; use it as-is.
3. Confirm `snapctl snapend download` flags for the manifest category as used in the reworked skills.
4. Don't hardcode the admin-capable snap list in skills — always check `has_admin` per version at runtime via `snaps enumerate`.

---

## Execution order

1. **Phase 1 — Workstream A skeleton**: create `source/CONTEXT.md` from current CLAUDE.md, write `scripts/build.py`, generate CLAUDE.md/AGENTS.md, verify no content drift, repo hygiene. (Everything after this edits `source/CONTEXT.md` only.)
2. **Phase 2 — Workstream C** (smallest, unblocks D since login precedes everything): setup-snapctl + prereq updates.
3. **Phase 3 — Workstream B**: verify core repo structure, update BYOSnap skills.
4. **Phase 4 — Workstream D**: (SDK already inspected — see D1) write configure-snap-settings skill with the tsx runner recipe + worked example, rework the four workflow skills, port keeper-recipes inline, delete `data/snap-settings/`.
5. **Phase 5 — Distributions & install docs**: the repo root itself serves all three platforms (`.claude-plugin/` for Claude; `AGENTS.md` + `skills/` + `data/` for Codex and OpenCode) — no `dist/` copies needed. Write `docs/INSTALL.md` with per-platform install instructions (Claude, Codex, OpenCode) per AJ's request; rewrite README install section to link it; bump to 0.2.0.
6. **Phase 6 — Verification pass**: link-check every path referenced in CONTEXT.md and skills; dry-read each modified skill start-to-finish as an agent would; if snapctl is installed locally, smoke-test `snapctl login --help`, `snapctl snaps enumerate`, and `snapctl admin-sdk download --help` against a dev app.

## Out of scope (flag if wanted later)

- Auto-generating a settings "capability map" from downloaded admin SDKs into docs.
- CI that runs the build script and link checks on every push.
- Publishing dist/codex and dist/opencode as separate release artifacts.
