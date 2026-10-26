# Handoff: Embedding the Snapser Agent Plugin in the Hosted App

Audience: the team/agent building Snapser's hosted Cowork-type app, where customers
import their project and work with a coding agent (Claude Code, Codex, or OpenCode).
This doc is self-contained — follow it top to bottom to give every customer session
full Snapser capabilities out of the box.

## What the plugin is

One repo — `https://github.com/snapser-engine/snapser-agent-plugin` — serves all
agents. It contains:

| Path | Purpose |
|---|---|
| `CLAUDE.md` / `AGENTS.md` | Agent context: Snapser concepts, rules, workflows (generated files — identical content) |
| `skills/` | Step-by-step workflow instructions (create backend, BYOSnap, configure settings, …) |
| `data/docs/` + `data/snap-swaggers/` | Full offline Snapser docs and per-snap OpenAPI specs |
| `data/releases/` | Platform release notes, one `.mdx` per release, plus a generated `INDEX.md` lookup table. Read-only user-facing info — answers "what changed", never drives a manifest or a setting |
| `data/admin-sdk/sdk-python` | Bundled Python Admin SDK for programmatic snap-settings changes |
| `.claude-plugin/` | Claude plugin + marketplace manifest |

## Rule zero

**Never write plugin files into the customer's imported project.** Everything below
installs at the sandbox/image level, invisible to the customer's git diff.

## 1. Bake the plugin into the session image

```dockerfile
# Pin to a release tag — never main, never `git pull` at session start
RUN git clone --depth 1 --branch v0.3.2 \
    https://github.com/snapser-engine/snapser-agent-plugin.git /opt/snapser-plugin
```

Why pinned + baked: deterministic sessions, no GitHub dependency at runtime, no
supply-chain surprise, zero cold-start latency. Plugin updates = bump the tag,
rebuild the image, roll out.

## 2. Wire up each agent globally (at image build time)

| Agent | Wiring |
|---|---|
| Claude Code | `claude plugin marketplace add /opt/snapser-plugin && claude plugin install snapser@snapser-plugins` → every session gets auto-triggering skills + slash commands |
| Codex | Write `~/.codex/AGENTS.md` containing the pointer block below |
| OpenCode | Write `~/.config/opencode/AGENTS.md` containing the pointer block below |

Pointer block (Codex / OpenCode):

```markdown
## Snapser
For anything Snapser-related (backends, Snapends, BYOSnaps, SDKs, snap settings),
read /opt/snapser-plugin/AGENTS.md first and follow the skill files it points to
under /opt/snapser-plugin/skills/.
```

Smoke-test the Claude local-path marketplace install once in your actual image build
before shipping.

## 3. Preinstall the toolchain

- `pipx install snapctl` (Python 3.9+ required — also needed by the bundled Admin SDK)
- Docker only if sessions must build/publish BYOSnap or game-server images
- Node 18+ (used by the web-game workflow to bundle the web-ts SDK with esbuild)

## 4. Authentication — `snapctl login` device flow

Do NOT inject or store customer API keys in the app. The agent runs `snapctl login`
inside the sandbox on first Snapser action:

1. The CLI prints a short code (`XXXX-XXXX`) and a verification URL.
2. **Your app's UI must surface that URL + code to the customer** (clickable). The
   customer opens it in their own browser, confirms the code matches, clicks
   **Activate**.
3. A freshly minted API key flows back to the CLI and is saved to the sandbox's
   `~/.snapser/config` (permissions 600). The key never passes through your app.

Operational notes:

- **Persist `~/.snapser/config` in the customer's session state** so login happens
  once per customer, not once per thread.
- `snapctl login` is idempotent and self-heals expired keys — always safe for the
  agent to re-run.
- Enterprise customers on private deployments: `snapctl login --portal-endpoint <url>`
  persists a `PORTAL_ENDPOINT` in the same config file; the plugin's settings skill
  reads it automatically to route Admin SDK calls. No extra work in the app.

## 5. Update policy

- Plugin version ↔ image version: one-to-one. Track plugin releases (git tags) and
  rebuild when you want to pick one up.
- The bundled Admin SDK targets the snap versions in
  `/opt/snapser-plugin/data/admin-sdk/VERSION.md`. Customers on older snaps are
  handled by the plugin's own error-handling ladder (it offers a snap upgrade or a
  version-matched SDK download) — nothing to build app-side.

## 6. Verification checklist (per image build)

1. Ask the agent: "What is a Snapend?" → answers from `/opt/snapser-plugin/data/docs/`,
   no web search.
2. Ask: "Validate my snapctl setup" → runs `snapctl validate`, and on a fresh session
   walks the customer through `snapctl login` (check the URL+code surfaces in your UI).
3. In Claude sessions: `/create-backend` autocompletes as a slash command.
4. In Codex/OpenCode sessions: ask "scaffold a Snapser BYOSnap in Go" → the agent reads
   `/opt/snapser-plugin/skills/create-byosnap/SKILL.md` before acting (visible in its
   tool calls).
5. `~/.snapser/config` survives session restart (state persistence works).
6. Ask: "What's new in the latest Snapser release?" → the agent reads
   `/opt/snapser-plugin/data/releases/INDEX.md` first (not a blind grep of every release
   file), then the newest release note. No web search.
