---
name: snapser-help
description: Answer any Snapser question from the docs bundled in this plugin — never web search. Use whenever the user mentions Snapser, a snap, Snapend, BYOSnap, BYOWS, BYOGS or snapctl: concepts, snap APIs and endpoints, configuration, connectors, SDKs, tutorials, release notes and what's new. Also for questions about what you know — "how much do you know about Snapser", "are you familiar with Snapser", "do you know anything about Snapser", "tell me what you know about Snapser".
---

# Skill: Snapser Help — Answer Any Question About Snapser

Answers any question that touches Snapser — from "what is Snapser?" to "what's the request body for the matchmaking create-ticket endpoint?". Use this skill whenever the user mentions Snapser, a specific snap, Snapends, BYOSnap, BYOWS, BYOGS, snapctl, or any other Snapser concept.

**IMPORTANT — All documentation is local. Do NOT fetch remote URLs or use web search.**
1. **Platform-level questions** (what is Snapser, how does it work, what are snaps, what's a Snapend) → read `data/docs/overview.mdx` and `data/docs/concept.mdx`.
2. **Snap API questions** (endpoints, request/response, how to call an API) → read the LOCAL swagger file at `data/snap-swaggers/<snap-name>.swagger3.json`.
3. **Snap feature/concept/config questions** (how does auth work, what connectors are available, how to configure leaderboards) → read `data/docs/INDEX.md` first (every page, with its topic), then the page it points to.
4. **"What changed / what's new" questions** (release notes, changelog, when did a feature ship, what's in the latest release) → read `data/releases/INDEX.md` first, then the release file(s) it points to. See Step 5 below.

## Trigger Phrases
- "what is Snapser?"
- "how does Snapser work?"
- "tell me about Snapser"
- "what are snaps?"
- "what is a Snapend?"
- "how do I use the auth API?"
- "what endpoints does leaderboards have?"
- "how do I create a user?"
- "what's the request body for matchmaking?"
- "show me the inventory API"
- "how does the chat snap work?"
- "what parameters does this endpoint take?"
- "help me with Snapser"
- "how much do you know about Snapser?"
- "are you familiar with Snapser?"
- "do you know anything about Snapser?"
- "tell me what you know about Snapser"
- "what can you tell me about Snapser?"
- "do you have the Snapser docs?"
- "how do I configure notifications?"
- "how do I update a score?"
- "what is BYOSnap / BYOWS / BYOGS?"
- "what's new in Snapser?"
- "what changed in the latest release?"
- "show me the release notes / changelog"
- "what's in 1.12.0?"
- "did anything change in leaderboards recently?"
- "when did the Admin SDK ship?"
- "were there any breaking changes?"
- "what's the latest Snapser version?"
- Any question that mentions Snapser, a snap name, Snapend, BYOSnap, BYOWS, BYOGS, or snapctl

## Requirements
- No external tools required — all documentation is bundled locally

## Swagger File Locations

**These are LOCAL files. Read them with the Read tool. Do NOT fetch them from any URL.**

The swagger files are OpenAPI 3.0 specs at this path relative to the plugin root:
```
data/snap-swaggers/<snap-name>.swagger3.json
```

Available files:
`analytics`, `assets`, `auth`, `chat`, `client-logs`, `decorators`, `eventbus`, `events`,
`experiments`, `game-server-fleets`, `gdpr`, `guilds`, `iap`, `inbox`, `inventory`, `kws`,
`leaderboards`, `lobbies`, `matchmaking`, `notifications`, `parties`, `photon`, `profiles`,
`quago`, `quests`, `remote-config`, `scheduler`, `sequencer`, `social-graph`, `statistics`,
`storage`, `trackables`, `xp`

**Mapping common terms to snap names:**
- "authentication", "login", "users", "sessions", "sign up" → `auth`
- "leaderboard", "scores", "rankings", "update score" → `leaderboards`
- "items", "inventory", "loot" → `inventory`
- "friends", "social", "follow" → `social-graph`
- "messages", "chat", "messaging" → `chat`
- "push notifications", "alerts" → `notifications`
- "purchases", "in-app purchases", "IAP" → `iap`
- "mail", "rewards mail" → `inbox`
- "quests", "missions", "achievements" → `quests`
- "guilds", "clans", "teams" → `guilds`
- "lobbies", "rooms" → `lobbies`
- "matchmaking", "matching" → `matchmaking`
- "parties", "groups" → `parties`
- "game servers", "fleets", "hosting" → `game-server-fleets`
- "stats", "statistics", "player stats" → `statistics`
- "progress", "XP", "energy", "trackable" → `trackables` or `xp`
- "feature flags", "remote config" → `remote-config`
- "A/B testing", "experiments" → `experiments`
- "storage", "cloud save", "player data" → `storage`
- "analytics", "telemetry" → `analytics`
- "GDPR", "data deletion", "privacy" → `gdpr`
- "events", "live events" → `events`
- "scheduling", "timed events" → `scheduler`
- "profiles", "player profiles" → `profiles`

## How to Answer Questions

### Step 0 — Is this a platform-level question?

If the user is asking a high-level question like "what is Snapser?", "how does Snapser work?", "what are snaps?", or "tell me about Snapser", start by reading:
- `data/docs/overview.mdx` — Platform overview
- `data/docs/concept.mdx` — Core concepts (Snaps, Snapends, environments, etc.)

Answer from these files in plain language. If the user then asks a follow-up about a specific snap or API, proceed to Step 1.

### Step 0.2 — Is the user asking what you know about Snapser?

Questions like "how much do you know about Snapser?", "are you familiar with Snapser?",
or "do you have the Snapser docs?" are asking what is available, not for a definition.
Answer from what is actually bundled here, never from memory:

1. Read `data/docs/INDEX.md` (every documentation page and its topic) and
   `data/releases/INDEX.md` (every release and its date).
2. Say what is on hand — the full product documentation, an OpenAPI spec per snap in
   `data/snap-swaggers/`, the platform release notes, and the snapctl workflows in
   `skills/` — and name a few areas the user can ask about.
3. Offer the obvious next question rather than dumping the index.

Answer these from the bundled files even if you already believe you know Snapser: what
you remember is older than what is in this folder.

### Step 0.5 — Is this a "what changed?" question?

If the user is asking about release notes, a changelog, what's new, what changed, what a
specific version contained, or when a feature shipped → **go straight to Step 5**. Don't
answer these from `data/docs/`; the docs describe the current state, not the change history.

### Step 1 — Can you identify a snap from the question?

Look at the user's question and check if it maps to one of the snap names above. Most
questions will — "how do I update a score?" maps to `leaderboards`, "how do I add a friend?"
maps to `social-graph`, etc.

**If yes and it's an API question** (endpoints, request/response) **→ go to Step 2.**
**If yes but it's a feature/concept/config question** (how does it work, what are my options) **→ go to Step 3.**
**If no snap identified → go to Step 3.**

### Step 2 — Read the LOCAL swagger file and answer from it

**Do NOT skip this step. Do NOT fetch remote URLs instead.**

1. Read the relevant swagger file using the Read tool:
   ```
   Read: data/snap-swaggers/<snap-name>.swagger3.json
   ```
2. Find the relevant endpoint(s), request/response schemas, and parameters
3. Explain the API in plain language — include the HTTP method, path, required headers,
   request body schema, and response format
4. Provide a curl example showing how to call the endpoint

If the swagger file answers the question, you're done. If the user also needs setup or
configuration guidance beyond the API spec, supplement with local docs (Step 3).

### Step 3 — Search local docs at `data/docs/`

The `data/docs/` folder contains the full Snapser documentation as `.mdx` files (Markdown
with JSX components — ignore the `import` statements and JSX tags at the top; the useful
content is the prose, headings, code blocks, and tables).

**How to find the right file:**

| Question about... | Where to look |
|---|---|
| Which page covers what (start here) | `data/docs/INDEX.md` |
| A specific snap's features/overview | `data/docs/infra/snaps/<snap-name>/index.mdx` |
| A snap's config tools (web portal UI) | `data/docs/infra/snaps/<snap-name>/config-tools/` |
| Auth connectors (Google, Steam, etc.) | `data/docs/infra/snaps/auth/connectors/` |
| BYOSnap, BYOWS, BYOGS, BYO data store | `data/docs/custom/` |
| Custom tools (config tool, profile tool) | `data/docs/custom/tools/` |
| Snapser concepts, architecture | `data/docs/concept.mdx`, `data/docs/overview.mdx` |
| Snapend internals (networking, SDKs, monitoring, logs) | `data/docs/snapend/` |
| Snapend tools (API explorer, inspector, clone, sync) | `data/docs/snapend/tools/` |
| Tutorials (setup, auth, BYOSnap, BYOGS, security) | `data/docs/guides/tutorials/` |
| Sample projects (Unity, Unreal, Roblox, web, mobile) | `data/docs/guides/samples/` |
| CLI reference | `data/docs/resources/cli.mdx` |
| Web portal (access, teams) | `data/docs/resources/portal/` |
| Marketplace | `data/docs/resources/marketplace.mdx` |
| AI integrations (Cortex, MCP, OpenAI) | `data/docs/ai/` |
| Business intelligence (dashboards, charts, SQL lab) | `data/docs/business-intelligence/` |
| Generic/infrastructure errors | `data/docs/infra/generic-errors.mdx` |

**Workflow:**
1. Read `data/docs/INDEX.md` — a generated map of all 191 pages, grouped by area, each
   with the topic it covers. Match the question against it and pick the page(s).
2. Read those file(s) with the Read tool and answer from the content.
3. Only if the index leaves you with nothing, grep `data/docs/` for keywords from the
   question. Never read the folder into context wholesale.

`data/docs/index.mdx` is the docs *landing page* (prose for a human). `data/docs/INDEX.md`
is the map. The table above is the coarse view; the index is the precise one.

### Step 4 — For mixed questions: Local swagger + local docs

Some questions need multiple sources. For example, "How do I set up anonymous login and
what's the API call?" — read the `auth` swagger file for the API details, then read
`data/docs/infra/snaps/auth/connectors/anon.mdx` for the setup guide.

### Step 5 — "What changed?" questions → `data/releases/`

`data/releases/` holds the Snapser **platform** release notes — one `.mdx` per release,
named after the version (`1.12.0.mdx`) — covering the platform, snaps, Web App, snapctl,
SDKs, and docs. Route here whenever the user asks what's new, what changed, when something
shipped, or what a specific release contained.

**Always read `data/releases/INDEX.md` first.** It is a generated lookup table with:
- the latest release and its date
- every release, newest first, with its date and section list
- a **snap → releases** reverse index, so you can jump straight to the releases that
  touched a given snap

Then open only the release file(s) the index points to.

**Do not** grep all 30 release files blind, and do not read them all into context — the
index exists precisely so you don't have to. Filenames don't sort chronologically
(`1.10.0` sorts before `1.2.0` lexically), so trust the index's ordering, not `ls`.

**Answering patterns:**

| User asks | What to do |
|---|---|
| "what's new?" / "latest release?" | Read `INDEX.md`, then the newest release file. Summarize its Spotlight and breaking changes. |
| "what's in 1.9.0?" | Read `data/releases/1.9.0.mdx` directly. |
| "did anything change in leaderboards?" | Use the snap → releases index, then read those files and pull only the `### Leaderboards` sections. |
| "when did <feature> ship?" | Grep `data/releases/` for the feature name, then read the matching release for the date. |
| "any breaking changes I should know about?" | Read `INDEX.md` for releases with a Breaking Changes section, then read those sections. |
| "what changed since <version/date>?" | Use `INDEX.md` to list the releases after that point, then read each and summarize. |

> **HARD RULE — release notes are read-only, user-facing information.**
> They tell a human what changed. They are NEVER an input to building or changing
> anything. Never take snap versions, manifest structure, `settings` values, API shapes,
> or command flags from a release note. Structure comes only from
> `snapctl snapend-manifest ...`, settings only from the Admin SDK, API shapes only from
> `data/snap-swaggers/`, and the live snap catalog only from `snapctl snaps enumerate`.
> A version number mentioned in a release note is **not** a version to pin.
>
> If a release note makes the user want to change their backend, hand off to the normal
> skill for that change (`skills/update-backend/SKILL.md`,
> `skills/configure-snap-settings/SKILL.md`) and gather the real state from `snapctl`
> there. Don't carry values over from the release note.

Also note the release notes describe the **hosted platform**, not this plugin. If the user
asks what version of the *plugin* they have, that's `.claude-plugin/plugin.json`, not
`data/releases/`.

## Response Guidelines

- **Be specific.** Include actual endpoint paths, HTTP methods, parameter names, and schema fields from the swagger file.
- **Use curl examples** when showing how to call an endpoint. Include the Snapser gateway URL format:
  ```
  https://gateway.snapser.com/$snapendId/v1/<snap>/<endpoint>
  ```
- **Explain authorization requirements.** Swagger files include security schemes — tell the user
  which headers or tokens are needed (e.g. `Token: <session_token>` for user-authenticated calls).
- **Keep it conversational.** Don't dump raw swagger JSON at the user. Translate it into
  clear, practical guidance.
- **If a swagger file doesn't exist** for the snap the user is asking about, check the local
  docs at `data/docs/infra/snaps/<snap-name>/`. If neither exists, let the user know this snap may not be fully documented locally and suggest checking the Snapser web docs.

## Notes
- **All documentation is local.** Do not fetch remote URLs — answer from local swagger files and docs.
- Only read the file(s) relevant to the question — not all of them.
- Some swagger files are large (1000+ lines). Read the full file, but focus your answer on the specific endpoints relevant to the user's question.
- If the user asks about a snap that isn't in the swagger list or docs, it may be a partner snap — let them know and suggest they check the Snapser web portal.
- If the user's question spans multiple snaps (e.g. "how do auth and leaderboards work together?"), read both swagger files and both snap doc pages to explain how they integrate.
- `data/docs/` describes how Snapser works **today**; `data/releases/` describes **what changed and when**. If the user asks "how does X work", use the docs. If they ask "did X change", use the release notes.
- The release notes are user-facing information only. Never let them drive a manifest, a settings value, or a version pin — see the HARD RULE in Step 5.
