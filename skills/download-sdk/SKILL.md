---
name: download-sdk
description: Download SDKs, protobuf files, or manifests for a Snapend
---

# Skill: Download SDK, Protobufs or Manifest for a Snapend

Guides the developer through downloading the correct SDK, protos, or manifest for their
Snapend based on their platform, language, and use case.

## Trigger Phrases
- "download my sdk"
- "get the sdk for my snapend"
- "I need the unity sdk"
- "download the client sdk"
- "get the server sdk"
- "download protos"
- "I need the sdk for my game"

## Requirements
- Snapser CLI (`snapctl`) installed and configured
- The user must have an existing Snapend. If they don't, guide them through `skills/create-backend/SKILL.md` first.

## Full Workflow

### Phase 1 — Identify the target Snapend

Ask the user which Snapend they want to download the SDK for.

If they don't remember the Snapend ID, run `snapctl snapend enumerate` to show all their Snapends and let them pick.

### Phase 2 — Determine what to download

Ask the user what they need. There are three download categories:

**Category: `sdk`** — Client and server SDKs for integrating with the Snapend.

Supported formats (game engines):
`unity`, `unreal`, `roblox`, `godot-csharp`, `godot-cpp`, `godot-gdscript`, `cocos`, `ios-objc`, `ios-swift`, `android-java`, `android-kotlin`, `web-ts`, `web-js`, `flutter-dart`

**Web format guidance:** for a browser game or page WITHOUT a bundler (plain HTML +
`<script>` tags), use **`web-ts`** and bundle it into a single minified JS file:
```bash
npx --yes esbuild@0.24.0 $extractedSdkPath/index.ts \
    --bundle --format=iife --global-name=Snapser --target=es2020 --minify \
    --outfile=snapser-sdk.min.js
```
(`--format=esm` instead of `--format=iife --global-name=Snapser` if the page uses
`<script type="module">`.) Only choose `web-js` when the project already has its own
bundler pipeline (webpack, vite, etc.).

Supported formats (languages):
`csharp`, `cpp`, `lua`, `ts`, `go`, `python`, `kotlin`, `java`, `c`, `node`, `js`, `perl`, `php`, `clojure`, `ruby`, `rust`, `dart`

SDK types:
- `user` — for client-side code running on behalf of an authenticated user (most common for game clients)
- `api-key` — for trusted server-side code that calls the Snapend with elevated permissions
- `internal` — for BYOSnaps calling other Snaps within the same Snapend
- `unified`, `app` — special-purpose access types; only use when the user explicitly asks for them

**Category: `protos`** — Protocol buffer definitions for gRPC integration.

Supported formats: `go`, `csharp`, `cpp`, `raw`

Proto types:
- `messages` — message definitions only
- `services` — full service definitions with RPC methods

**Category: `snapend-manifest`** — The Snapend's current manifest.

Supported formats: `json` (always use JSON — YAML currently has a long-integer issue and can be flaky)

### Phase 3 — Check for optional HTTP library preference

Some SDK formats support an optional HTTP library choice. Ask the user **only** if their chosen format is one of these:

| Format | Supported `--http-lib` values |
|--------|-------------------------------|
| `unity` | `httpclient`, `unitywebrequest`, `restsharp` |
| `csharp` | `httpclient`, `restsharp` |
| `web-ts` | `axios`, `fetch` |
| `ts` | `axios`, `fetch` |

If the user's format is not in this list, skip this step — the `--http-lib` flag is not needed.

### Phase 4 — Download the SDK

Use the snapctl command:

```bash
# Standard download (no http-lib)
snapctl snapend download \
  --snapend-id $snapendId \
  --category $category \
  --format $format \
  --type $type \
  --out-path .

# With http-lib preference (only for unity, csharp, web-ts, ts)
snapctl snapend download \
  --snapend-id $snapendId \
  --category $category \
  --format $format \
  --type $type \
  --http-lib $httpLib \
  --out-path .
```

The SDK will be saved to the current directory. Note the exact filename from the command output.

### Phase 5 — Confirm and guide integration

After the download completes:
- Tell the user exactly where the SDK was saved and what the filename is
- Give a brief pointer on how to import or integrate it based on their platform:
  - **Unity** — import the downloaded package into the Unity project's Assets folder
  - **Unreal** — add to the project's Source or Plugins directory
  - **Web (TS/JS)** — install via the downloaded package or copy into the project's dependencies
  - **Mobile (iOS/Android)** — add the SDK to the project's dependency manager (CocoaPods, Gradle, etc.)
  - **Other languages** — point the user to the downloaded files and suggest placing them in their project's library/vendor folder
- If the user downloaded protos, remind them they'll need a protobuf compiler (`protoc`) to generate code from the definitions

### Phase 6 — Next steps

Ask the user:
- **Need a different SDK type?** For example, they may want both a `user` SDK for the client and an `internal` SDK for their BYOSnap. Offer to download another.
- **Want to create a custom microservice?** Guide them through `skills/create-byosnap/SKILL.md`.
- **Want to update their Snapend?** Guide them through `skills/update-backend/SKILL.md`.

## Notes
- Be conversational — help the user pick the right format and type based on what they're building, don't just list all options.
- If the user says "Unity SDK" or "Python SDK" without specifying a type, default to `user` — that's the most common use case for game/app clients.
- If the user is building a BYOSnap that calls other Snaps, they need the `internal` SDK type. Point this out if relevant.
- If any step fails, explain the error clearly using `skills/error_codes.md` and offer to retry or adjust.
