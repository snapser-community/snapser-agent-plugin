---
name: create-backend
description: Create a new Snapend backend from Snapser snap catalog
---

# Skill: Create a Backend on Snapser aka Snapend

Guides the developer through setting up a complete Snapser development environment
from scratch — backend and SDK.

## Trigger Phrases
- "set up my Snapser backend"
- "I want to get started with Snapser"
- "create a new game backend"
- "bootstrap my Snapser project"

## Requirement
- Snapser CLI (`snapctl`) installed and configured

## Full Workflow

### Setup
1. Get the application ID. Run `snapctl application enumerate` to list existing applications, or ask the user for their application ID.
    - If the user has no applications and wants to create one:
        - Ask the user for an application name.
        - Create an application using the `snapctl application create --name $app_name` command.
        - Note the application ID returned by the CLI.
    - Use the application ID with `--application-id` in subsequent commands.

### Phase 1 — Understand the project
Ask the user:
- What kind of game are they building?
- What game engine or platform? (Unity, Unreal, Roblox, web, mobile etc)
- Do they already have a Snapser application? If yes, what is the application ID?

### Phase 2 — Pick snaps
1. Run `snapctl snaps enumerate` to fetch all available snaps
2. Use the following lookup to suggest snaps only if the user does not explicitly specify which snaps they need

```typescript
export const STARTER_TEMPLATES_LOOKUP: Record<
  StarterTemplateCategories,
  GameTemplateRecord
> = {
  [StarterTemplateCategories.AUTH]: {
    name: 'Basic Auth',
    description:
      'Kickstart secure player logins in minutes. These templates support anonymous login, email OTP, or OAuth flows—so your players can jump in fast and stay connected.',
    snaps: [
      'analytics', // Basic analytics
      'auth', // Basic authentication
    ],
    image: '/images/templates/auth.png',
  },
  [StarterTemplateCategories.OFFLINE_SINGLE_PLAYER]: {
    name: 'Basic Game',
    description:
      'For games like Monument Valley, Alto’s Odyssey, or Limbo. These templates are tailored for solo experiences that prioritize story, puzzles, or casual offline play—with support for local saves, progression, and smooth startup without server calls.',
    snaps: [
      'analytics', // Basic analytics
      'auth', // Basic authentication
      'leaderboards', // Competitive features
      'profiles', // Player profiles
      'quests', // Mission/achievement system
      'remote-config', // Feature flags and content updates
      'statistics', // Basic in game usable statistics
      'storage', // Local game state
      'trackables', //XP and Energy
    ],
    image: '/images/templates/offline-single-player.jpg',
  },
  [StarterTemplateCategories.BASIC_STARTER]: {
    name: 'Basic App',
    description:
      'Get analytics, authentication and scalable cloud storage to start your development journey. Easily save and sync player data across devices with built-in security.',
    snaps: [
      'analytics', // Basic analytics
      'auth', // Basic authentication
      'storage', // Local game state
    ],
    image: '/images/templates/cloud-storage.png',
  },
  [StarterTemplateCategories.BASIC_SAAS]: {
    name: 'Basic SaaS',
    description:
      'Launch your SaaS application with essential features like user authentication, profiles, storage, and analytics. Ideal for startups and MVPs looking to validate their ideas.',
    snaps: [
      'auth',
      'profiles',
      'storage',
      'analytics',
      'notifications',
      'remote-config',
      'experiments',
      'client-logs',
      'gdpr',
    ],
    image: '/images/templates/saas.png',
  },
}

export const GAME_TEMPLATES_LOOKUP: Record<
  GameTemplateCategories,
  GameTemplateRecord
> = {
  [GameTemplateCategories.ARCADE_SOCIAL]: {
    name: 'Social Arcade',
    description:
      'Inspired by Candy Crush, Subway Surfers, or Temple Run. These templates are built for casual games with viral loops—supporting leaderboards, lives/energy systems, gifting, and lightweight social features.',
    snaps: [
      'analytics',
      'auth',
      'experiments', // A/B testing for optimization
      'leaderboards', // Competitive features
      'notifications', // Re-engagement
      'profiles',
      'quests',
      'remote-config',
      'social-graph', // Friend system
      'storage',
      'statistics',
      'trackables', // Progress tracking
    ],
    image: '/images/templates/arcade-social.jpg',
  },
  [GameTemplateCategories.PARTY_MULTIPLAYER]: {
    name: 'Party Multiplayer',
    description:
      'For games like Among Us, Fall Guys, or Stumble Guys. These templates help you spin up drop-in/drop-out multiplayer with lobbies, player sessions, and social chaos—perfect for party games focused on quick fun and group dynamics.',
    snaps: [
      'analytics',
      'auth',
      'chat', // In-game communication
      'experiments',
      'game-server-fleets', // Game session management
      'leaderboards',
      'matchmaking', // Player matching
      'notifications',
      'parties', // Party management
      'profiles',
      'remote-config',
      'social-graph',
      'statistics',
      'trackables',
    ],
    image: '/images/templates/party-multiplayer.jpg',
  },
  [GameTemplateCategories.COMPETITIVE_MULTIPLAYER]: {
    name: 'Real-time multiplayer',
    description:
      'Modeled after Clash Royale, Brawl Stars, or Hearthstone. These templates power real-time PvP, matchmaking, ELO-based ranking, and season resets—great for building games where every second counts and every match matters.',
    snaps: [
      'analytics',
      'auth',
      'chat',
      'experiments',
      'events', // Special events system
      'game-server-fleets', // Game session management
      'guilds', // Team/clan features
      'inventory', // Item management
      'leaderboards',
      'matchmaking',
      'notifications',
      'parties',
      'profiles',
      'quests',
      'remote-config',
      'scheduler', // Timed events
      'social-graph',
      'statistics',
      'trackables', // Progress tracking
    ],
    image: '/images/templates/competitive-multiplayer.png',
  },
  [GameTemplateCategories.LIVE_SERVICE_RPG]: {
    name: 'Live Service RPG',
    description:
      'Inspired by Genshin Impact, Diablo Immortal, or AFK Arena. These templates are ideal for RPGs with evolving content, gacha, dailies, inventory management, and live ops tooling—built to scale with your world.',
    snaps: [
      'analytics',
      'auth',
      'chat',
      'events',
      'experiments',
      'game-server-fleets', // Game session management
      'guilds',
      'inventory',
      'iap', // In-app purchases
      'inbox', // Rewards/mail system
      'leaderboards',
      'matchmaking',
      'notifications',
      'parties',
      'profiles',
      'quests',
      'remote-config',
      'scheduler', // Timed events
      'sequencer', // Event sequencing
      'social-graph',
      'statistics',
      'storage',
      'trackables',
    ],
    image: '/images/templates/live-service.png',
  },
  [GameTemplateCategories.BATTLE_ROYALE]: {
    name: 'Battle Royale',
    description:
      'For games like Fortnite, PUBG Mobile, or Call of Duty: Warzone Mobile. These templates support large-scale lobbies, player drops, shrinking zones, and real-time combat sync—your foundation for high-stakes, last-one-standing showdowns.',
    snaps: [
      'analytics',
      'auth',
      'chat',
      'client-logs', // Enhanced debugging
      'events',
      'experiments',
      'game-server-fleets', // Game session management
      'guilds',
      'inventory',
      'iap',
      'inbox',
      'leaderboards',
      'matchmaking',
      'notifications',
      'parties',
      'profiles',
      'quests',
      'remote-config',
      'relay', // Real-time networking
      'scheduler',
      'social-graph',
      'statistics',
      'storage',
      'trackables',
    ],
    image: '/images/templates/battle-royale.jpeg',
  },
  [GameTemplateCategories.HOSTING_STACK]: {
    name: 'Hosting Stack',
    description:
      'Spin up scalable game servers with matchmaking, regions, and live monitoring out of the box. These templates power your multiplayer or real-time experiences effortlessly.',
    snaps: [
      'analytics', // Basic analytics
      'auth', // Basic authentication
      'game-server-fleets', // Hosting
      'lobbies', // lobbies
      'matchmaking', // Player matching
      'parties', // Party management
    ],
    image: '/images/templates/hosting-stack.png',
  },
  [GameTemplateCategories.USER_ENGAGEMENT]: {
    name: 'User Engagement',
    description:
      'Engage your players with built-in chat, inbox messages, push notifications, and emails. These templates help you connect with players inside and outside the game.',
    snaps: [
      'analytics', // Basic analytics
      'auth', // Basic authentication
      'chat', // In-game communication
      'inbox', // Rewards/mail system
      'notifications', // Re-engagement
    ],
    image: '/images/templates/user-engagement.jpg',
  },
}

export const APP_TEMPLATES_LOOKUP: Record<
  AppTemplateCategories,
  GameTemplateRecord
> = {
  [AppTemplateCategories.E_COMMERCE]: {
    name: 'E-Commerce',
    description:
      'Build a full-featured e-commerce platform with secure authentication, user profiles, in-app purchases, and real-time notifications. Perfect for online stores and marketplaces.',
    snaps: [
      'auth',
      'profiles',
      'storage',
      'iap',
      'notifications',
      'analytics',
      'experiments',
      'gdpr',
      'client-logs',
      'remote-config',
    ],
    image: '/images/templates/e-commerce.png',
  },
  [AppTemplateCategories.SOCIAL_NETWORK]: {
    name: 'Social Network',
    description:
      'Create a vibrant social network with user profiles, chat, social graphs, and notifications. Engage your users with real-time interactions and personalized experiences.',
    snaps: [
      'auth',
      'profiles',
      'chat',
      'social-graph',
      'notifications',
      'analytics',
      'inbox',
      'gdpr',
      'storage',
      'experiments',
      'eventbus',
      'client-logs',
    ],
    image: '/images/templates/social-network.png',
  },

  [AppTemplateCategories.BLOG]: {
    name: 'Blog',
    description:
      'Kickstart your blogging platform with user authentication, profiles, and storage for posts. Engage readers with analytics and notifications for new content.',
    snaps: [
      'auth',
      'profiles',
      'storage',
      'social-graph',
      'analytics',
      'notifications',
      'experiments',
      'gdpr',
      'client-logs',
    ],
    image: '/images/templates/blog.png',
  },
  [AppTemplateCategories.MARKETPLACE]: {
    name: 'Marketplace',
    description:
      'Build a marketplace with user authentication, profiles, inventory management, and in-app purchases. Perfect for connecting buyers and sellers in a secure environment.',
    snaps: [
      'auth',
      'profiles',
      'storage',
      'inventory',
      'iap',
      'analytics',
      'notifications',
      'experiments',
      'gdpr',
    ],
    image: '/images/templates/marketplace.jpg',
  },
  [AppTemplateCategories.EDUCATION]: {
    name: 'Education',
    description:
      'Create an educational platform with user authentication, profiles, storage for course materials, and trackable quests. Engage learners with notifications and analytics.',
    snaps: [
      'auth',
      'profiles',
      'storage',
      'trackables',
      'statistics',
      'quests',
      'analytics',
      'notifications',
      'experiments',
      'inbox',
    ],
    image: '/images/templates/education.jpg',
  },
}
```


3. Confirm the snap selection with the user before proceeding

### Phase 2b — Gather settings requirements

Settings are applied AFTER the Snapend is live, via the Admin SDK (see
`skills/configure-snap-settings/SKILL.md`). At this stage, only gather WHAT the user
wants configured, so you can apply it in Phase 3b:

1. For each selected snap, ask what they want to enable — e.g. which auth methods
   (anonymous, Google, Steam, ...), leaderboard names and sort orders, storage keys,
   profile attributes, stat keys, trackables.
2. For what individual settings mean, read the snap's docs at
   `data/docs/infra/snaps/<snap-name>/`.
3. Note the desired configuration — do NOT hand-edit manifest settings JSON.

### Phase 3 — Generate manifest and create Snapend

**CRITICAL: NEVER write, edit, or inject a manifest JSON with any tool** — not from scratch, and not with `python`, `jq`, `sed`, or a here-doc script. The manifest schema is complex and hand-written manifests will fail. ALWAYS use `snapctl snapend-manifest create` to generate the base manifest. Do NOT inject settings into it — not even a settings block grounded in the Admin SDK source or config docs, and even if the script "produces valid JSON." The manifest handed to `snapend create` MUST have an empty `settings` array. Settings are applied ONLY post-create, via the Admin SDK against the live Snapend (Phase 3b). Structure and settings are two separate phases — never combine them.

1. Ask for a Snapend name:
```text
20 characters maximum
Contain only alphanumeric characters and dashes
Start with an alphabetic character
Unique name in current environment.
```

2. Generate the base manifest using snapctl:
```bash
snapctl snapend-manifest create \
  --name $snapendName \
  --env DEVELOPMENT \
  --snaps $commaSeparatedSnapList \
  --out-path-filename ./$snapendName-manifest.json
```
This produces a valid manifest file with the correct structure, service definitions, and an empty `settings` array.

3. Do NOT edit the generated manifest — it is created with correct structure and
   empty settings, which is exactly what `snapend create` needs. Settings come next,
   via the Admin SDK.

4. Create the Snapend from the manifest:
```bash
snapctl snapend create \
  --name $snapendName \
  --env DEVELOPMENT \
  --manifest-path-filename $pathToManifest \
  --blocking
```
The `--blocking` flag ensures the command waits until the Snapend is fully online. **Do not skip `--blocking`.**

5. If the create times out (exit code 79), the Snapend is still provisioning. Check status with `snapctl snapend enumerate` and wait for it to come online. This is not a failure.

6. Report the Snapend ID — tell the user to save it.

### Phase 3b — Apply snap settings via the Admin SDK

Apply everything gathered in Phase 2b to the now-live Snapend by following
`skills/configure-snap-settings/SKILL.md`:

1. Read `skills/configure-snap-settings/config-cheatsheet.md` (mandatory)
2. Install the plugin-bundled SDK (`data/admin-sdk/sdk-python`) into a project venv
3. Write and run a small script against the SDK to apply the settings (explicit host —
   see the skill; the SDK's baked-in default is wrong)
4. On version-mismatch errors or snaps without admin support, follow the skill's
   error-handling ladder (upgrade snaps / download matched SDK / web portal Config tool)

Then download the manifest to the project root — MANDATORY after settings changes:
```bash
snapctl snapend download \
  --snapend-id $snapendId \
  --category snapend-manifest \
  --format json \
  --out-path .
```

### Phase 4 — Download SDK
1. Run `snapctl snapend download --snapend-id $snapendId --category sdk` with their engine/platform
2. Tell the user exactly where the SDK was saved and how to import it
3. Here are the details that you need to pass to the format, type and optional http-lib inputs
```bash
# $format = One of the supported formats:
#   snapend-manifest(json) — YAML is supported by the CLI but do NOT use it (long-int issue)
#   sdk(unity, unreal, roblox, godot-csharp, godot-cpp, godot-gdscript, cocos, ios-objc, ios-swift, android-java, android-kotlin, web-ts, web-js, flutter-dart),
#   sdk(csharp, cpp, lua, ts, go, python, kotlin, java, c, node, js, perl, php, clojure, ruby, rust, dart),
#   protos(go, csharp, cpp, raw)
# $type = One of the supported types:
#   For category=sdk type=(user, api-key, internal, unified, app)
#   For category=protos type=(messages, services)
# $http_lib (optional) = One of the supported libs
#   For category=sdk format=unity http-lib=(httpclient, unitywebrequest, restsharp)
#   For category=sdk format=csharp http-lib=(httpclient, restsharp)
#   For category=sdk format=web-ts http-lib=(axios, fetch)
#   For category=sdk format=ts http-lib=(axios, fetch)
#   For category=sdk format=flutter-dart http-lib=(http, dio)
#   For category=sdk format=dart http-lib=(http, dio)
```

### Phase 5 — Next steps
Ask the user:
- If they want to now create a custom microservice or if they want to add any other snaps.
- If they want to add a new microservice go with the create-byosnap skill. If they want to add other snaps, you can go with the update-backend skill.

## Notes
- Be conversational throughout — this is an onboarding flow, not a script
- If any step fails, explain the error clearly and offer to retry or skip
- Default to DEVELOPMENT environment for all new backends
