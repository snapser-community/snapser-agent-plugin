# Snap Config Cheat Sheet — Admin SDK

Practical nuances for configuring Snapser snaps via the **Admin SDK** — the
Python SDK (`snapser`) and the three TypeScript variants (node / axios / fetch).
Learned by building integration-test harnesses against the dev environment.
Intended to be fed to tooling/assistants so they generate correct admin-config
calls the first time.

In Python every call has the shape `<snap>_<action>(api_key, cluster_id, body=...)`.
The API key goes in the `Api-Key` header; `cluster_id` is a path param. The
snap-level config semantics below (enums, required fields, PUT-vs-PATCH,
eventual-consistency, etc.) are **language-agnostic** — they apply equally to the
TypeScript SDKs. The TypeScript-specific mechanics (method casing, int64 as
`bigint`, argument order, per-variant quirks) are collected in their own section
near the end.

---

## Cross-cutting (applies to every snap)

- **Base URL needs the `/snapser` segment** or the server 404s ("no Route
  matched"). Resolution order: `PORTAL_ENDPOINT` from `~/.snapser/config` (+
  `/v1/snapser-api/clusters`) if present, else the bundled SDK's default
  (`https://gateway.snapser.com/snapser/v1/snapser-api/clusters`). Note: SDKs
  freshly downloaded via `snapctl admin-sdk download` may carry a wrong default
  host — always apply the same resolution. Dev-environment host is
  `https://gateway.dev.snapser.io/snapser/v1/snapser-api/clusters`.
- **Method names have no `admin` infix.** It's `leaderboards_create_leaderboard`,
  not `leaderboards_admin_create_leaderboard`.
- **int64 fields travel as JSON strings on the wire** (proto3 JSON). The SDK's
  `Int64` type accepts a string or number in and serializes back to a string.
  Plain `int` values you pass in Python are fine.
- **Timestamps are Unix seconds** (10-digit), not milliseconds.
- **`PUT` update = full replace.** You must resend all required fields
  (including enums), not just the ones you're changing. Use the `PATCH`/`patch_*`
  variant for partial updates.
- **Delete can be eventually consistent.** After a successful delete, an
  immediate list/get may still show the resource for a second or two (seen on
  storage and profiles). Poll before asserting it's gone.
- **Duplicate names return HTTP 409** ("... already exists"); missing resources
  return 404.

---

## Per-snap notes

### leaderboards
- `start_time` is **only honored on a recurring leaderboard** — you must set
  `duration > 0` **and** a `time_unit`. On a non-recurring board (`duration=0`)
  the server ignores `start_time` (treats it as 0).
- On create/update of a recurring board, `start_time` must be **≥ 5 minutes in
  the future** (server-clock seconds), else HTTP 400.
- Enums: `behavior` = counter | maximum | minimum | most_recent_score;
  `sort` = descending | ascending; `scope` = internal | external;
  `type` = global | tiered; `time_unit` = hours | days | weeks | months.
- `create` = POST, `update` = PUT (full replace), `patch` = partial.

### statistics
- `statistic.key`: lowercase alphanumeric, hyphens, underscores.
- `scope` = internal | external; `type` = string | counter | timestamp | float.
- `delete_statistic` takes a `cascade` flag.
- A **segment** needs `predicate_groups` (groups OR'd together, predicates within
  a group AND'd). `predicate.operator` = `==` | `>` | `>=` | `<` | `<=` | `!=`;
  each predicate references an existing `statistic_key`.
- statistics: create/get/list/delete + segments (full CRUD). Note there is **no
  `update_statistic`** — it was removed from the SDK (previously returned 501 Not
  Implemented server-side).
- `get_discounts` (inventory) takes `discount_name` as a **list** filter, not a
  single string.

### storage
- `add_keys` registers key definitions: `access_type` = public | protected |
  private; `scope` = internal | external; `storage_type` = blob | append-blob |
  counter | json. Optional JSON `schema` (field alias `schema`, Python attr
  `var_schema`).
- Delete is eventually consistent.

### profiles
- `type` = text | number | single_select | multi_select | timestamp | file;
  `visibility` = public | private | custom (with `visibility_group` when custom).
- **`edit_key` body only supports `visibility`, `validations`, `visibility_group`**
  — not `required` or `type`. Set those at `add_key` time.
- Delete is eventually consistent.

### inventory
- **Currency** is the simplest resource: `InventoryCurrency(name, display_name)`.
- **Catalog item** requires `class_name`, `display_name`, `name`, `stackable`,
  `tradable`. Note: a **durable (non-consumable) item must have `stackable=false`**
  — the server rejects "durable items cannot be stackable".
- **Currency conversion** (keyed by `from_currency`/`to_currency`): set the
  **`multiplier`** field (must be > 0) — the server validates the deprecated
  `multiplier`, not just `multiplier_64`, so set both.
- **Import catalog** (`import_catalog`): `data` is a **base64-encoded CSV** (not
  JSON). Columns: name, display_name, class_name, description, stackable, tradable,
  ttl, consumable, container, purchasable, sub_inventory,
  user_inventory_instance_limit, user_inventory_instance_limit_per_sub_inventory,
  metadata, tags. Optional cells may be blank; JSON-valued cells (e.g.
  `sub_inventory`) are JSON strings. ⚠️ Sending non-CSV `data` (e.g. `"{}"`)
  returned 502 and destabilized the service — a bad import should not crash it.
- `update_inventory_settings` is **PATCH** `/inventory/settings/inventory-settings`;
  body `InventoryInventorySettings` = a new-user **`default_grant`** +
  **`drop_table_max_nesting_depth`**. `default_grant` grants existing items
  (`items`: name→count) and/or currencies (`currencies_64`: name→int64-string;
  `currencies` is deprecated). The grant is optional — currency-only, item-only,
  or both are all valid — and referenced items/currencies must exist.
- **One-time grant** must specify **at least one reward** (one of `currencies_64`,
  `items`, `drop_tables`, `trackables_energy`, `trackables_xp`); `currencies_64`
  maps currency name → int64-as-string amount, e.g. `{"coins": "100"}`.
- **Discount** requires `description`, `discount_formula`, `display_name`,
  `eligibility_groups`, `formula`, `name`.
- **Discount** requires `name`, `display_name`, `description`, `formula`
  (type + value), `discount_formula` (one of fixed/percentage/statistic), and
  `eligibility_groups` — each group needs **≥1 eligibility**. A `time_range`
  eligibility (`start_time`/`end_time`) is self-contained (no other resource
  needed). Update is **full-replace**: resend `eligibility_groups` or the server
  rejects with "eligibility groups cannot be empty".
- **Drop table** requires `name` + `drops`. ⚠️ The SDK types the create `drops`
  as `Dict[str,Any]`, but sending an object yields a server proto error
  ("unexpected token {"); the response model uses `List[InventoryDropTableDrops]`.
  Request/response shape mismatch — likely can't be created via the SDK as-is;
  confirm the real payload and report to team.
- **One-time grant** requires `grant_id` + `name`.
- Currency conversions are keyed by `from_currency` + `to_currency` (path params).
- Monetary/quantity fields use the `*_64` variants (e.g. `multiplier_64`,
  `currencies_64`) — the non-`_64` fields are deprecated.

### iap
- A **bundle** grants inventory currencies/items: `grants=[IapGrant(id=<inventory
  id>, quantity_64=N, type="currency"|"item")]`. The grant `id` must reference a
  real inventory currency/item.
- `get_settings` and provider enable/disable require an `environment`
  (dev | stage | prod).
- Provider enable (apple/google/steam/tebex) needs real credentials — not
  automatable without secrets.

### trackables
- Three resources: **energy**, **streak**, **xp**. All take a `scope`
  (internal | external) and a unique `name`.
- Energy (simplest): `max_energy`, `seconds_to_recover` required; `default_energy`,
  `overflow` optional.
- Streak requires `period_duration` + `type` (fixed | rolling_window) +
  `time_unit` (seconds | minutes | hours | days | ...).
- XP requires `levels`, and the levels must **tile the range with no gaps or
  overlaps** — two levels sharing a boundary (e.g. end=100, start=100) counts as
  an overlap and is rejected.
- Duration-ish fields (`period_duration`, `cooldown_duration_seconds`) are
  unsigned int64 → strings on the wire (handled by the SDK's `Int64`).

### queues
- `action.type` = ACTION_TYPE_PULL | ACTION_TYPE_DELIVER | ACTION_TYPE_EMIT.
  A **PULL** queue needs no target. **DELIVER** needs `byosnap` (target snap id,
  e.g. `byosnap-<name>`) + `path` (HTTP path to POST to).
- Dead-letter operations (`list/purge/requeue/delete_dead_letters`) are per queue.

### game_server_fleets
- Creating a fleet needs a **real, published BYO game-server `image_tag`** and a
  hardware profile (dev/stage/prod) — environment-specific, not automatable
  without a deployed image. Reads (`get_fleets`, `list_game_servers`) are safe.

### guilds / parties / lobbies
- Settings-style: `get_settings` + `patch_settings`/`update_settings`. Read
  first, mutate, restore.
- Lobbies is **settings-only** now (`get_settings`/`update_settings`). The webhook
  event enable/disable endpoints were removed from the SDK after the server
  returned 500 Unimplemented for them.

### remote_config
- **App config**: `base_value` and `schema` are arbitrary JSON (any shape);
  `version` is a unique string. Revisions are tracked and revertable.
- **Base config** must be **set before it can be read** — `get_base_config` on a
  fresh cluster returns 404 "base config not set". `set_base_config` takes a body
  with **both `schema` and `base_value`** keys (not a raw config object); sending
  just the config returns 400 "Schema/BaseValue: value is required".
- Revision-list responses return a **list**, not a dict. `get_all_base_config_revisions`,
  `get_all_app_config_revisions`, and `get_all_override_revisions` all now return
  `List[...]` (fixed). Revert takes a revision number from those lists.
- **Override** requires `name`, `path`, `sort_order`, `value`, and an audience
  (`all_users=true` | `segment_name` | `override_user_ids`), plus a base config to
  reference. `path` is written **without a leading slash** (e.g. `"greeting"`).
  Update is full-replace (resend audience + value). (`value` field is present in
  the SDK now — earlier gap fixed.)
- **Preview endpoints are runtime lookup tools, not config setup.**
  `preview_config(overrides=[<override names>])` applies named overrides and
  returns the resulting config (self-contained, testable).
  `preview_user_config(user_id=...)` needs a **real runtime user** (created via the
  game-client SDK) — not testable from an admin-config harness.

### auth (51 endpoints)
- Many auth calls take an **`environment`** argument (dev | stage | prod) —
  `get_settings`, `get_api_keys`, and `delete_api_key` all require it;
  `get_email_templates` needs a template `type`. These are call arguments, not
  body fields.
- **API keys**: create needs `length` (bits: 0, 128, or 256), `state`
  (`AuthApiKeyState`, e.g. `API_KEY_STATE_ENABLED`), and — **required by the
  server though the SDK model marks them optional** — `description`,
  `environment` (dev | stage | prod), expiry (`never_expire` + `expiry_seconds`),
  and a **complete `apis` object**. ⚠️ A partial / wildcard-only `apis` object
  triggers a server **504** (this was the cause of the auth timeouts). Use the
  full shape — both `endpoints.snaps` and `snap_wildcards`:

  ```json
  {
    "name": "test", "description": "test",
    "never_expire": false, "expiry_seconds": 15552000,
    "length": 128, "environment": "dev", "state": "API_KEY_STATE_ENABLED",
    "apis": {
      "endpoints": { "snaps": {} },
      "snap_wildcards": { "snaps": [], "all": true }
    }
  }
  ```
- Per-provider **logins** each have enable / toggle / delete (anon, apple,
  discord, email, email_password, epic, facebook, google, steam,
  username_password, x, xbox). Credential-free: anon, username_password,
  email/OTP. Credentialed (server-enforced even where the SDK marks fields
  optional): google/facebook/discord/epic (`client_id`+`client_secret`),
  x/xbox (`client_id`), apple (`key_id`/`private_key`/`service_id`/`team_id`),
  **steam (`web_api_key` or Steamworks key — required despite being optional in
  the model)**. Apple login has enable+toggle but no delete.
- Also: settings, session-token validity, email templates, user auth
  restrictions, app auth/verify.
- int64 fields here (`expiry_seconds`, `session_token_validity`,
  `*_retention_seconds`) are strings on the wire.

---

## TypeScript Admin SDK (node / axios / fetch variants)

Snapser ships three TypeScript Admin SDKs, all generated from the same spec:
`typescript-node` (legacy `request` lib), `typescript-axios`, and
`typescript-fetch`. Customers pick one; the same snap-config rules above apply.
These are the mechanical differences that bite when writing calls or a shared
test harness.

**Common to all three:**

- **Methods are camelCase**, no `admin` infix — `leaderboardsCreateLeaderboard`,
  `authGetSettings`, `inventoryCreateOneTimeGrant`.
- **Body fields are camelCase** — `startTime`, `maxUsers`, `snapWildcards`,
  `expirySeconds` (vs the Python/wire `start_time`, `max_users`, …). The server
  accepts **both** camelCase and snake_case in request bodies (proto3 JSON
  `json_name`), so a camelCase body always works regardless of variant.
- **int64 fields are `bigint`** — pass bigint literals: leaderboards
  `duration`/`startTime`, guilds `maxUsers`/`inviteTtlHours`, auth
  `expirySeconds`/`otpLength`/`otpValidity`/`verificationCode*`/`session*`,
  discount `timeRange` `startTime`/`endTime`, streak `periodDuration`, xp level
  `start`/`end`. Serializers stringify bigint on the wire.
- **`apiKey` + `clusterId` are supplied on every call** (not global config).

**Argument shape differs by variant:**

- **node** & **axios**: positional args. ⚠️ **The parameter order is
  order-sensitive and NOT uniform across methods.** Required path/query params
  come **before** `apiKey`/`clusterId`, but *optional* query params come
  **after** them — e.g.
  `authGetSettings(environment, apiKey, clusterId, options)` but
  `authGetApiKeys(apiKey, clusterId, names?, environment?, options)` and
  `authEnableAnonLogin(apiKey, clusterId, body, options)`. There is no single
  fixed ordering; read the actual generated signature (or map args by parameter
  name at runtime).
- **fetch**: a single request-object param (named fields), so ordering is a
  non-issue: `authGetSettings({ environment, apiKey, clusterId })`.

**Return / error shape by variant:**

- **node**: resolves `{ response, body }` — read `.body`; errors are
  `HttpError` (`err.statusCode`, `err.body`).
- **axios**: resolves an `AxiosResponse` — read `.data`; errors are `AxiosError`
  (`err.response.status`, `err.response.data`).
- **fetch**: resolves the model directly; errors are a `ResponseError` whose
  `err.response` is the raw `Response` (`await err.response.json()` for the body).

**Per-variant quirks (real, caught by the harness):**

- **axios responses are snake_case.** node (via `ObjectSerializer`) and fetch
  (via `*FromJSON`) deserialize responses to **camelCase** model fields, but
  `typescript-axios` was generated with **snake_case** interface properties
  (`max_users`, `api_keys`, `snap_wildcards`, `match_profile`,
  `exclusion_groups`, …). int64→bigint is still handled. So reading a multi-word
  field off an axios response needs snake_case (or normalize keys back to
  camelCase). **Flag for SDK team:** regenerate axios with camelCase model naming
  so all three variants match.
- **node array query params need `useQuerystring = true`.** The legacy `request`
  lib defaults to bracket form (`overrides[0]=x`), which the gateway ignores;
  set `api.useQuerystring = true` so arrays serialize as repeated keys
  (`overrides=a&overrides=b`), matching how Python `requests` and axios/fetch
  behave. Only matters for endpoints with an array query param (e.g.
  `remoteConfigPreviewConfig(overrides)`); a mis-serialized `overrides` returns
  404 "override not found".

**Cross-language field-name divergences (TS spec lags the refreshed Python spec):**

- **`IapGrant`**: TS has `quantity` (optional `number`); Python has `quantity_64`
  (required). Different field.
- **`InventoryDefaultGrant`**: TS has `currencies` (number map); Python has
  `currencies_64` (string map). (Note: the one-time-grant reward field *is*
  `currencies64`/`currencies_64` in TS too — the divergence is specifically the
  inventory-**settings** default grant.)

These mean a value valid in one language can be silently dropped in another;
worth reconciling SDK-side.

---

## SDK generation gotchas (history — fixed, but watch on regen)

These were real SDK-generation bugs the harness caught; note them in case a
future regen reintroduces them:

- **int64 response fields typed as strict `int`** → the SDK couldn't deserialize
  its own backend's string-encoded int64s. Fixed by a custom `Int64` type
  (`snapser/int64.py`). On regen, confirm int64 fields use `Int64`, not
  `StrictInt`.
- **`UnsignedLong` referenced but never generated** → `NameError` in `from_dict`
  for unsigned-64 fields (`duration`, `bucket_size`, `period_duration`,
  `cooldown_duration_seconds`). Fixed by mapping them to `Int64`.
- **statistics `get_statistic` / `delete_statistic` briefly disappeared** in one
  regen. If a lifecycle suddenly can't find a get/delete method, suspect the
  regen dropped it.
