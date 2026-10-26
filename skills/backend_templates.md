# Snap Templates — Recommended Snap Sets by Use Case

Use this reference when helping users pick snaps for their backend.
Always run `snapctl snaps enumerate` first to verify current availability — snap names or IDs may change.

> **Auth is always included.** Do not list it as optional or ask the user about it.

---

## Starter Templates

### Basic Auth
Secure player logins with anonymous login, email OTP, or OAuth flows.
Snaps: `analytics`, `auth`

### Basic Game (Offline Single Player)
For solo experiences like Monument Valley or Limbo — local saves, progression, casual offline play.
Snaps: `analytics`, `auth`, `leaderboards`, `profiles`, `quests`, `remote-config`, `statistics`, `storage`, `trackables`

### Basic App
Analytics, authentication, and scalable cloud storage for getting started.
Snaps: `analytics`, `auth`, `storage`

### Basic SaaS
Essential SaaS features for startups and MVPs.
Snaps: `auth`, `profiles`, `storage`, `analytics`, `notifications`, `remote-config`, `experiments`, `client-logs`, `gdpr`

---

## Game Templates

### Social Arcade
Casual games with viral loops — leaderboards, energy systems, social features. Think Candy Crush, Subway Surfers.
Snaps: `analytics`, `auth`, `experiments`, `leaderboards`, `notifications`, `profiles`, `quests`, `remote-config`, `social-graph`, `storage`, `statistics`, `trackables`

### Party Multiplayer
Drop-in/drop-out multiplayer with lobbies and social chaos. Think Among Us, Fall Guys.
Snaps: `analytics`, `auth`, `chat`, `experiments`, `game-server-fleets`, `leaderboards`, `matchmaking`, `notifications`, `parties`, `profiles`, `remote-config`, `social-graph`, `statistics`, `trackables`

### Real-time Multiplayer (Competitive)
Real-time PvP, ELO ranking, season resets. Think Clash Royale, Brawl Stars.
Snaps: `analytics`, `auth`, `chat`, `experiments`, `events`, `game-server-fleets`, `guilds`, `inventory`, `leaderboards`, `matchmaking`, `notifications`, `parties`, `profiles`, `quests`, `remote-config`, `scheduler`, `social-graph`, `statistics`, `trackables`

### Live Service RPG
Evolving content, gacha, dailies, inventory, live ops. Think Genshin Impact, Diablo Immortal.
Snaps: `analytics`, `auth`, `chat`, `events`, `experiments`, `game-server-fleets`, `guilds`, `inventory`, `iap`, `inbox`, `leaderboards`, `matchmaking`, `notifications`, `parties`, `profiles`, `quests`, `remote-config`, `scheduler`, `sequencer`, `social-graph`, `statistics`, `storage`, `trackables`

### Battle Royale
Large-scale lobbies, real-time combat sync. Think Fortnite, PUBG Mobile.
Snaps: `analytics`, `auth`, `chat`, `client-logs`, `events`, `experiments`, `game-server-fleets`, `guilds`, `inventory`, `iap`, `inbox`, `leaderboards`, `matchmaking`, `notifications`, `parties`, `profiles`, `quests`, `remote-config`, `relay`, `scheduler`, `social-graph`, `statistics`, `storage`, `trackables`

### Hosting Stack
Scalable game servers with matchmaking, regions, and monitoring.
Snaps: `analytics`, `auth`, `game-server-fleets`, `lobbies`, `matchmaking`, `parties`

### User Engagement
Chat, inbox, push notifications, and emails to connect with players.
Snaps: `analytics`, `auth`, `chat`, `inbox`, `notifications`

---

## App Templates

### E-Commerce
Online stores and marketplaces with authentication, profiles, IAP, and notifications.
Snaps: `auth`, `profiles`, `storage`, `iap`, `notifications`, `analytics`, `experiments`, `gdpr`, `client-logs`, `remote-config`

### Social Network
User profiles, chat, social graphs, real-time interactions.
Snaps: `auth`, `profiles`, `chat`, `social-graph`, `notifications`, `analytics`, `inbox`, `gdpr`, `storage`, `experiments`, `eventbus`, `client-logs`

### Blog
Blogging platform with user auth, profiles, storage, and reader engagement.
Snaps: `auth`, `profiles`, `storage`, `social-graph`, `analytics`, `notifications`, `experiments`, `gdpr`, `client-logs`

### Marketplace
Buyers and sellers with inventory management and in-app purchases.
Snaps: `auth`, `profiles`, `storage`, `inventory`, `iap`, `analytics`, `notifications`, `experiments`, `gdpr`

### Education
Educational platform with course materials, trackable progress, and quests.
Snaps: `auth`, `profiles`, `storage`, `trackables`, `statistics`, `quests`, `analytics`, `notifications`, `experiments`, `inbox`
