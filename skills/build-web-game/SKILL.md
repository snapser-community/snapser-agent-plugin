---
name: build-web-game
description: Build a playable browser game with a Snapser backend from scratch
---

# Skill: Build a Web Game with Snapser Backend

Builds a fully playable browser-based game from scratch, creates a Snapser backend with
the right snaps, downloads the web-ts SDK (bundled to a single JS file), and wires everything together — so the user goes
from zero to a working game with a live backend in a single session.

**This skill is for web/browser games only.** If the user wants Unity, Unreal, Roblox, or
another engine-based game, redirect them to `skills/full-game-backend-wizard/SKILL.md` which
sets up the backend and SDK for their platform. Explain: "This skill builds a browser-based
game for quick prototyping. For engine-based games, I can set up your backend and download
the SDK for your platform instead."

## Trigger Phrases
- "build me a game"
- "make a web game"
- "create a browser game with a backend"
- "build a game with Snapser"
- "I want to prototype a game"
- "make me a simple game with leaderboards"
- "build a clicker game"
- "create a game from scratch"
- "demo game with Snapser"

## Requirements
- Snapser CLI (`snapctl`) installed and configured
- A modern web browser (Chrome, Firefox, Safari, Edge)

## Overview

```
Stage 1: Understand what game the user wants
Stage 2: Build the HTML/JS game (playable locally, no backend yet)
Stage 3: User tests the game in their browser
Stage 4: Create the Snapend with the right snaps
Stage 5: Download the web-ts SDK and bundle it to a single JS file
Stage 6: Integrate the SDK into the game (auth, save/load, leaderboards, etc.)
Stage 7: User tests the full game with live backend
Stage 8: Recap and next steps
```

## Full Workflow

### Stage 1 — Understand the game

Ask the user what kind of game they want. Be creative and encouraging — this should feel fun.

Gather:
- **What type of game?** Suggest options if they're unsure:
  - Clicker / idle game
  - Quiz / trivia
  - Memory / card matching
  - Snake / arcade
  - Simple platformer
  - Tower defense
  - Turn-based RPG combat
  - Word puzzle
  - Reaction speed game
  - Space shooter
- **What backend features?** Suggest based on game type:
  - Auth (always included)
  - Leaderboards (high scores)
  - Storage (save/load game state)
  - Statistics (track player stats)
  - Profiles (player display names)
- **Any theme or style preferences?** (colors, pixel art feel, minimal, etc.)

If the user just says "surprise me" or "anything" — pick a clicker or arcade game with
leaderboards. These are simple, fun, and showcase the backend integration well.

### Stage 2 — Build the game

Build a **single-file HTML game** that works standalone in a browser. This means all HTML,
CSS, and JavaScript in one `.html` file.

**Game requirements:**
- Must be playable and fun without any backend — the backend integration comes later
- Clean, responsive UI that looks good on desktop
- Use vanilla JS — no frameworks, no npm, no build tools
- Include a clear score or progress mechanic that will later connect to the backend
- Add placeholder UI elements for backend features (e.g. a "Login" button that doesn't
  work yet, a "Leaderboard" panel that shows dummy data)
- Include comments in the code marking where backend integration will go:
  ```js
  // TODO: Replace with Snapser auth login
  // TODO: Replace with Snapser leaderboard fetch
  // TODO: Replace with Snapser storage save
  ```

**Quality bar:**
- The game should feel polished — not a bare-bones tech demo
- Smooth animations, clear visual feedback on player actions
- Sound effects are optional but nice (use Web Audio API if adding them)
- Mobile-friendly layout is a bonus but not required

Save the game file to the user's workspace. Name it something descriptive
(e.g. `space-clicker.html`, `trivia-game.html`).

### Stage 3 — User tests the standalone game

Tell the user to open the HTML file in their browser and try it out.

> Open the game file in your browser and give it a try! Everything works locally
> for now — the login button and leaderboard are just placeholders. Once you're
> happy with the gameplay, we'll connect it to a real Snapser backend.

Wait for the user to confirm they've tested it. If they want changes to the game
(different colors, mechanics, difficulty), make those adjustments before proceeding.

**Do NOT move to Stage 4 until the user is happy with the base game.**

### Stage 4 — Create the Snapend

**Reference:** `skills/create-backend/SKILL.md` and `skills/backend_templates.md`

1. Run `snapctl snaps enumerate` to get the current snap catalog
2. Based on the game type and features discussed in Stage 1, recommend a snap set.
   Common combinations for web games:
   - **Clicker/arcade:** `auth`, `leaderboards`, `storage`, `statistics`
   - **Quiz/trivia:** `auth`, `leaderboards`, `storage`, `profiles`
   - **RPG/progression:** `auth`, `storage`, `inventory`, `statistics`, `profiles`, `quests`
   - **Social game:** `auth`, `leaderboards`, `storage`, `profiles`, `social-graph`, `chat`
3. Show the recommendation and let the user adjust
4. Ask for a **Snapend name** (max 20 chars, alphanumeric + dashes, starts with letter)
5. **Note the settings each snap will need** (applied after the Snapend is live, via the Admin SDK — `skills/configure-snap-settings/SKILL.md`). Recommended defaults for web games:
   - Auth → enable **anonymous login** (best default for web games — no signup friction)
   - Leaderboards → one global leaderboard for the game's score
   - Storage → a storage key for save/load game state
   - Profiles → profile attributes (display name, avatar)
   - Statistics → stat keys for tracked metrics
   - Trackables → XP ladders or energy systems
   For what individual settings mean, read `data/docs/infra/snaps/<snap-name>/`.
6. **Generate the base manifest** using `snapctl snapend-manifest create --name $name --env DEVELOPMENT --snaps $commaSeparatedSnaps --out-path-filename ./$name-manifest.json`. **NEVER write manifest JSON from scratch** — the schema is complex and hand-written manifests will fail. Do NOT edit the generated manifest.
7. **Create the Snapend from the manifest:**
   ```bash
   snapctl snapend create \
     --name $snapendName \
     --env DEVELOPMENT \
     --manifest-path-filename $pathToManifest \
     --blocking
   ```
8. If the create times out (exit code 79), check status with `snapctl snapend enumerate` — this is normal.
9. Save the Snapend ID
10. **Apply the settings from step 5 via the Admin SDK** — follow `skills/configure-snap-settings/SKILL.md` (enumerate versions → download the Admin SDK → run the settings script against the live Snapend).
11. Download the latest manifest to the project root (MANDATORY after settings changes):
    ```bash
    snapctl snapend download --snapend-id $snapendId --category snapend-manifest --format json --out-path .
    ```

### Stage 5 — Download the web-ts SDK and bundle it to a single JS file

**Reference:** `skills/download-sdk/SKILL.md`

For browser games, use the **`web-ts`** (TypeScript, fetch-based) SDK — NOT `web-js`.
The `web-js` SDK assumes a bundler pipeline; the `web-ts` SDK can be bundled into one
minified, dependency-free JS file that drops straight into a `<script>` tag.

1. Download the SDK:

```bash
snapctl snapend download \
  --snapend-id $snapendId \
  --category sdk \
  --format web-ts \
  --type user \
  --out-path .
```

2. Unzip it and locate the SDK's `index.ts` entry point (note the exact extracted
   folder name from the output).

3. Bundle + minify into a single file with esbuild (no install needed beyond Node):

```bash
# Default — classic script-tag global, simplest for single-file HTML games:
npx --yes esbuild@0.24.0 $extractedSdkPath/index.ts \
    --bundle --format=iife --global-name=Snapser --target=es2020 --minify \
    --outfile=snapser-sdk.min.js

# Alternative — ES module, if the game code lives in a <script type="module">:
npx --yes esbuild@0.24.0 $extractedSdkPath/index.ts \
    --bundle --format=esm --target=es2020 --minify \
    --outfile=snapser-sdk.min.js
```

4. Include it in the game HTML:

```html
<!-- IIFE (default): everything is available under the Snapser global -->
<script src="snapser-sdk.min.js"></script>
<script>
  // e.g. new Snapser.AuthServiceApi(new Snapser.Configuration({...}))
</script>

<!-- ESM alternative -->
<script type="module">
  import { AuthServiceApi, Configuration } from './snapser-sdk.min.js';
</script>
```

**IMPORTANT:** Examine the downloaded SDK source to understand its structure before
integrating. Check:
- What the client initialization looks like (the `Configuration` class and its `basePath`)
- How auth methods are called
- How API calls are structured

Read the SDK files to understand the actual API surface. **Do NOT guess the SDK's API —
read the actual code.**

### Stage 6 — Integrate the SDK

This is the critical stage. Wire the Snapser SDK into the game.

**Integration approach:**
1. Add the SDK to the HTML file (via `<script>` tag or inline)
2. Initialize the Snapser client with the Snapend ID
3. Replace the placeholder backend code with real SDK calls

**Typical integrations to wire up:**

**Auth — Anonymous login:**
- When the user clicks "Play" or "Login", call the anonymous auth endpoint
- Store the session token for subsequent API calls
- Show the user's ID or a generated display name after login
- Reference the auth swagger at `data/snap-swaggers/auth.swagger3.json` for exact request/response formats

**Leaderboards — High scores:**
- After a game ends, submit the score to the leaderboard
- Fetch and display the top scores in the leaderboard panel
- Reference `data/snap-swaggers/leaderboards.swagger3.json` for the API

**Storage — Save/load game state:**
- Save game progress (level, upgrades, currency) to Snapser storage
- Load saved state when the user returns
- Reference `data/snap-swaggers/storage.swagger3.json` for the API

**Statistics — Player stats:**
- Track things like total games played, highest combo, time played
- Reference `data/snap-swaggers/statistics.swagger3.json` for the API

**For each integration:**
1. Read the relevant swagger file at `data/snap-swaggers/<snap-name>.swagger3.json` to get the exact endpoint paths, methods, request bodies, and response formats
2. Read the downloaded SDK code to understand how it wraps these APIs
3. Wire it into the game code, replacing the TODO comments from Stage 2

**IMPORTANT:** Read the local swagger files and the downloaded SDK code. Do NOT guess
API signatures or make assumptions about how the SDK works. The swagger files are the
source of truth for API contracts, and the SDK code shows how to call them.

After integration, save the updated game file.

### Stage 7 — User tests with live backend

Tell the user to refresh the game in their browser and test the full experience.

> Refresh the game in your browser. This time, the login, leaderboard, and save/load
> features are connected to your live Snapser backend. Try:
> 1. Click Login — you should get a real session
> 2. Play a round and check if your score appears on the leaderboard
> 3. Close the tab and reopen — your saved progress should load

Wait for the user to confirm it works. Debug any issues:
- **Login fails** — Check the Snapend is online (`snapctl snapend enumerate`), verify the gateway URL
  and Snapend ID are correct in the game code
- **Leaderboard empty** — Confirm the leaderboard name matches what the API expects.
  Check if scores need to be created before they can be fetched.
- **Save/load fails** — Check storage API calls. Verify the session token is being passed
  correctly in the request headers.
- **CORS errors** — This may happen if the game is opened as a `file://` URL. Suggest
  running a local server: `python3 -m http.server 8080` and opening `http://localhost:8080`
- **Settings mismatch** — If a snap's behavior doesn't match expectations (e.g. wrong auth
  method, missing leaderboard), inspect the live snap settings to verify configuration:
  ```bash
  snapctl snap-config get-config --snaps auth,leaderboards,storage --snapend-id $snapendId
  ```
  Compare the output against what was configured in the manifest. Fix and re-apply if needed.

### Stage 8 — Recap and next steps

Give the user a summary:
- Game: what was built, where the file is saved
- Snapend: name, ID, environment, snaps included
- What's working: auth, leaderboard, storage, etc.

Then offer next steps:
- **Want to add more features?** Can add snaps like chat, inventory, matchmaking
  → `skills/update-backend/SKILL.md`
- **Want custom server logic?** Build a BYOSnap for game-specific backend code
  → `skills/create-byosnap/SKILL.md`
- **Want to iterate locally with live backend?** → `skills/attach-workstation/SKILL.md`
- **Want to promote to staging?** → `skills/clone-snapend/SKILL.md`
- **Want to build a native version?** Download the SDK for Unity/Unreal/etc.
  → `skills/download-sdk/SKILL.md`

## Skill Behavior Guidelines

- **This should feel magical.** The user starts with nothing and ends with a playable game
  backed by a real production-grade backend. Keep the energy up.
- **Don't dump all stages at once.** Present one stage at a time.
- **Let the user play before adding the backend.** Stage 3 is important — the game must
  be fun on its own before we add complexity.
- **Read the SDK and swagger files.** Do NOT guess how the APIs work. Read the local
  swagger files at `data/snap-swaggers/` and the downloaded SDK code before writing
  integration code.
- **Single file only.** Everything — HTML, CSS, JS, SDK integration — goes in one .html
  file. No separate files, no build tools, no npm.
- **If the user asks for Unity/Unreal/Roblox**, politely redirect to
  `skills/full-game-backend-wizard/SKILL.md`. This skill is browser-only.
- **Default to sensible values.** DEVELOPMENT environment, anonymous auth enabled, simple
  leaderboard with one board. Don't overwhelm with options.
- **If any Snapser step fails,** use `skills/error_codes.md` to diagnose and recover.

## Notes
- Auth snap is always included — never ask about it.
- Always use `--blocking` for Snapend creation.
- The gateway URL pattern is: `https://gateway.snapser.com/$snapendId/`
- For web games, the SDK type should be `user` and format should be `web-ts`, bundled to one minified JS file via esbuild (Stage 5). Do not use `web-js` — it assumes a bundler pipeline.
- If the user is behind a restrictive firewall or CORS is an issue, suggest using
  `python3 -m http.server` to serve the game locally.
