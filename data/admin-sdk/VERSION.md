# Bundled Admin SDK

- Generated against: **all snaps v1.12.0** (Snapser coordinated release)
- Language: Python (package `snapser`, pydantic v2)
- Plugin release: 1.16.0 (plugin versions track Snapser platform releases)
- Baked-in base URL patched to the production gateway
  (`https://gateway.snapser.com/snapser/v1/snapser-api/clusters`); the SDK was
  originally generated on playtest. Enterprise deployments are handled at runtime
  via `PORTAL_ENDPOINT` in `~/.snapser/config` (see the configure-snap-settings skill).

If a settings call fails with a server-side error (404 route / unknown-field 400),
check the target Snapend's deployed snap versions against the version above —
see `skills/configure-snap-settings/SKILL.md` error handling.
