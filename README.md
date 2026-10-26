# Snapser Plugin

Build and manage game backends without leaving your editor. The Snapser plugin brings your entire backend infrastructure workflow into your AI coding agent — create backends, deploy custom microservices, manage game servers, and download SDKs through natural conversation.

Works with **Claude** (Claude Code + Cowork), **OpenAI Codex**, **OpenCode**, and **Cursor** from this single repo — see [docs/INSTALL.md](docs/INSTALL.md).

<!-- docs-version:start -->
> **Bundled Snapser docs:** up to platform release **1.16.0** (October 19, 2026) · Admin SDK targets: see [data/admin-sdk/VERSION.md](data/admin-sdk/VERSION.md)
<!-- docs-version:end -->

## What You Can Do

- **Create backends** — spin up a Snapser backend (Snapend) with the snaps you need in seconds
- **Build web games** — prototype a playable browser game with a live Snapser backend end-to-end
- **Full game backend wizard** — complete guided setup with snaps, BYOSnap, and SDK in one flow
- **Deploy BYOSnaps** — build, publish, and direct-deploy your custom microservices
- **Game server fleets** — publish and deploy game server images (BYOGS) with fleet management
- **Local debugging** — attach your workstation to a remote Snapend and debug live
- **Download SDKs** — grab your Unity, Unreal, Roblox, or any other platform SDK instantly
- **Configure snap settings** — change auth connectors, leaderboards, storage keys and more programmatically via the Admin SDK
- **Manage Snapends** — list, update, clone, and check the health of your backends
- **Ask questions** — the plugin ships with the full Snapser documentation and API specs locally, so your agent can answer questions about Snapser without network calls

---

## Requirements

### 1. snapctl
The Snapser CLI tool is required for BYOSnap, BYOGS and workstation commands.

**MacOS / Linux**
```bash
pipx install snapctl
```

**Windows**
```bash
pip install --user snapctl
```

Then log in — a browser opens and your API key is minted and stored automatically:
```bash
snapctl login
```

Verify your install:
```bash
snapctl validate
```

### 2. Docker
Required for BYOSnap and BYOGS commands (`publish`, `sync`, `build`). Not needed for Snapend management or SDK downloads.

Download from [docker.com](https://www.docker.com/products/docker-desktop).

> **Important:** In Docker Desktop settings, make sure **Use containerd for pulling and storing images** is **disabled**.

---

## Installation

Full per-platform instructions (Claude Code, Claude Cowork, Codex, OpenCode, Cursor) live in
**[docs/INSTALL.md](docs/INSTALL.md)**.

Quick start for Claude Code — add the Snapser marketplace, then install the plugin:

```
claude plugin marketplace add snapser-community/snapser-agent-plugin
claude plugin install snapser@snapser-plugins
```

The first command registers the marketplace using your GitHub credentials — as long as you have access to the repo, it works. The second installs the plugin from it.

For Codex and OpenCode, clone this repo into your project and point your `AGENTS.md` at it — see [docs/INSTALL.md](docs/INSTALL.md).

---

## Usage

Once installed, just talk to Claude Code naturally. The plugin handles the rest.

### Skills

| Skill | What it does |
|---|---|
| `/create-backend` | Create a new Snapend with snaps of your choice |
| `/full-game-backend-wizard` | Complete end-to-end backend setup — snaps, BYOSnap, and SDK |
| `/build-web-game` | Build a playable browser game with a Snapser backend |
| `/create-byosnap` | Scaffold a custom BYOSnap microservice from scratch |
| `/publish-byosnap` | Build and publish a BYOSnap to the Snapser registry |
| `/direct-deploy-byosnap` | Push BYOSnap code directly to a dev Snapend for fast iteration |
| `/attach-workstation` | Route remote traffic to your local server for live debugging |
| `/download-sdk` | Download an SDK for your game engine or platform |
| `/update-backend` | Add, remove, or update snaps on an existing Snapend |
| `/clone-snapend` | Clone a Snapend to a new environment (e.g. dev → staging) |
| `/snapend-status` | Check the health, state, and details of a Snapend |
| `/byogs-publish` | Publish a custom game server image to Snapser |
| `/test-fleet-e2e` | Deploy and test a game server fleet end-to-end |
| `/create-application` | Create a new Snapser application space |
| `/generate-byosnap-profile` | Generate or edit a BYOSnap profile JSON file |
| `/setup-snapctl` | Install the Snapser CLI and log in |
| `/configure-snap-settings` | Change snap settings on a live Snapend via the Admin SDK |

### Just Talk To Your Agent

You don't need to use slash commands explicitly. The agent understands what you want:

> *"Set up a new backend for my multiplayer game with auth and leaderboards"*

> *"Build me a flappy bird game with a leaderboard"*

> *"Publish my byosnap to my dev snapend"*

> *"I want to debug my microservice locally"*

> *"Download the Unity SDK for my dev backend"*

> *"Enable anonymous login on my dev snapend"*

> *"How do I set up Steam authentication?"*

---

## Bundled Documentation

The plugin ships with the full Snapser documentation and API specs as local files. This means your agent can answer questions about Snapser concepts, snap APIs, configuration, tutorials, and more without making network calls. The docs are updated with each plugin release.

---

## Supported Platforms

SDKs are available for:

**Game Engines:** Unity, Unreal, Roblox, Godot, Cocos

**Mobile:** iOS (Swift, ObjC), Android (Kotlin, Java)

**Web:** TypeScript, JavaScript

**Backend:** Go, Python, Node, C#, C++, Rust, Java, Kotlin, Ruby, Dart, PHP

---

## Troubleshooting

**snapctl not found**
Add the Python bin folder to your PATH. On MacOS this is typically `~/Library/Python/3.x/bin`. On Windows it is typically `C:\Users\username\AppData\Roaming\Python\Python3x\Scripts`.

**Docker errors during publish**
Make sure Docker Desktop is running and the **Use containerd for pulling and storing images** setting is disabled.

**API key errors**
Run `snapctl login` — it is safe to run any time and self-heals expired or invalid keys. Then `snapctl validate` to confirm.

---

## Links

- [Snapser Dashboard](https://snapser.com)
- [Snapser Docs](https://docs.snapser.com)
- [snapctl on PyPI](https://pypi.org/project/snapctl)
