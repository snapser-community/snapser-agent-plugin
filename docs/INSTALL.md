# Installing the Snapser Plugin

The Snapser plugin works with **Claude** (Claude Code and Cowork), **OpenAI Codex**,
**OpenCode**, and **Cursor** from this single repository. All of them read the same content:

| File / folder | Purpose |
|---|---|
| `CLAUDE.md` / `AGENTS.md` | Agent context — concepts, rules, workflows (generated from `source/CONTEXT.md`) |
| `skills/` | Step-by-step workflow instructions the agent reads before executing |
| `data/docs/` | Full Snapser documentation (offline) |
| `data/snap-swaggers/` | OpenAPI specs for every snap's API |
| `.claude-plugin/` | Claude plugin + marketplace manifest |

## Prerequisites (all platforms)

1. **snapctl** — the Snapser CLI:
   ```bash
   pipx install snapctl      # or: pip3 install --user snapctl
   ```
2. **Log in** (opens a browser; your API key is minted and stored automatically):
   ```bash
   snapctl login
   ```
3. **Docker** — only needed for BYOSnap / BYOGS publish and deploy commands.

---

## Claude Code

Install via the plugin marketplace:

```
/plugin marketplace add snapser-engine/snapser-agent-plugin
/plugin install snapser@snapser-plugins
```

Restart Claude Code when prompted. The skills auto-trigger — just say things like
"create a Snapser backend" or "scaffold a BYOSnap".

To update later: `/plugin marketplace update snapser-plugins`.

## Claude Cowork (desktop)

1. Open **Settings → Capabilities → Plugins**.
2. Add the marketplace `snapser-engine/snapser-agent-plugin` and install **snapser**.

Alternatively, clone this repo and select it as a working folder — Claude picks up
`CLAUDE.md` and the `skills/` directory automatically.

## OpenAI Codex

Codex reads `AGENTS.md` from your workspace root.

1. Clone the plugin into your project (or add it as a git submodule):
   ```bash
   git clone https://github.com/snapser-engine/snapser-agent-plugin.git .snapser-plugin
   ```
2. Reference it from your project's `AGENTS.md` (create the file if you don't have one):
   ```markdown
   ## Snapser
   For anything Snapser-related (backends, Snapends, BYOSnaps, SDKs), read
   `.snapser-plugin/AGENTS.md` first and follow the skill files it points to
   under `.snapser-plugin/skills/`.
   ```
   If your project is Snapser-only, you can instead work directly inside the cloned
   repo — Codex will pick up its `AGENTS.md` automatically.

## OpenCode

OpenCode also honors `AGENTS.md`. The setup is identical to Codex:

1. Clone the plugin into your project:
   ```bash
   git clone https://github.com/snapser-engine/snapser-agent-plugin.git .snapser-plugin
   ```
2. Point your project's `AGENTS.md` at `.snapser-plugin/AGENTS.md` as shown above, or
   work directly inside the cloned repo.

## Cursor

Cursor has no plugin marketplace, but it natively supports `AGENTS.md` (alongside its
own Rules system). The setup is the same as Codex/OpenCode:

1. Clone the plugin into your project:
   ```bash
   git clone https://github.com/snapser-engine/snapser-agent-plugin.git .snapser-plugin
   ```
2. Point your project's `AGENTS.md` at `.snapser-plugin/AGENTS.md` as shown in the
   Codex section. If your team prefers Cursor Rules, an equivalent alternative is a
   project rule in `.cursor/rules/snapser.mdc` containing the same pointer text.

## One clone for all projects (optional)

You don't have to clone the plugin into every project. Codex, OpenCode, and Cursor all
support a **global** agent context file (e.g. `~/.codex/AGENTS.md`,
`~/.config/opencode/AGENTS.md`, Cursor User Rules). Clone this repo once to a central
location and add the Snapser pointer there — using the **absolute path** to the clone:

```markdown
## Snapser
For anything Snapser-related, read /home/you/tools/snapser-agent-plugin/AGENTS.md
first and follow the skill files it points to under its skills/ directory.
```

Project-local clones still win for teams (everyone gets the same pinned version via
git), but the global setup is convenient for individuals working across many repos.

## Embedding in a hosted app

If you are building a hosted product where users bring their own project and pick a
coding agent (Claude Code, Codex, OpenCode), embed the plugin at the **platform level**
so every session gets it automatically — never write plugin files into the customer's
imported project, where they would show up in their git diff.

**1. Bake the plugin into your session image.** Vendor this repo at a fixed path,
pinned to a release tag:

```dockerfile
# In your sandbox image build
RUN git clone --depth 1 --branch v0.3.0 \
    https://github.com/snapser-engine/snapser-agent-plugin.git /opt/snapser-plugin
```

Pinning to a tag makes sessions deterministic and turns plugin updates into a
deliberate rollout (bump the tag, rebuild, ship). Avoid cloning or pulling at session
start — it adds latency, a GitHub runtime dependency, and a moving target.

**2. Wire up each agent globally in the image** (the customer's repo stays untouched):

| Agent | At image build time |
|---|---|
| Claude Code | `claude plugin marketplace add /opt/snapser-plugin && claude plugin install snapser@snapser-plugins` — gives every session auto-triggering skills and slash commands |
| Codex | Write `~/.codex/AGENTS.md` with the pointer block below |
| OpenCode | Write `~/.config/opencode/AGENTS.md` with the pointer block below |

Pointer block for Codex / OpenCode:

```markdown
## Snapser
For anything Snapser-related (backends, Snapends, BYOSnaps, SDKs), read
/opt/snapser-plugin/AGENTS.md first and follow the skill files it points to
under /opt/snapser-plugin/skills/.
```

**3. Preinstall snapctl; authenticate with `snapctl login`.** Install `snapctl` in the
image. On a session's first Snapser action, the agent runs `snapctl login` — the
device flow is built for exactly this remote setup: the CLI (inside your sandbox)
prints a short code and a verification URL, the customer opens the URL **on their own
machine**, confirms the code, and clicks **Activate**. The minted key is stored in the
sandbox's `~/.snapser/config` automatically; no key ever passes through your app.
Surface the printed URL + code in your app's UI so the user can click it. If sessions
are ephemeral, persist `~/.snapser/config` in the customer's session state so they
log in once, not per thread — `snapctl login` is idempotent and self-heals expired
keys, so it is always safe for the agent to run it again.

**4. One clone serves every agent.** Because all platforms read the same `skills/` and
`data/` from this repo, a customer switching agents mid-project gets identical Snapser
behavior.

---

## Verifying the install

Ask your agent: *"What is a Snapend?"* — it should answer from the bundled docs without
searching the web. Then try: *"Validate my snapctl setup"* — it should run
`snapctl validate` and walk you through `snapctl login` if needed.

## For contributors

`CLAUDE.md` and `AGENTS.md` are **generated** — edit `source/CONTEXT.md` and run:

```bash
python3 scripts/build.py
```

The build also link-checks every `skills/` and `data/` path referenced from the context
and skill files.
