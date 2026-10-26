# Snapser Error Code Reference

Use this reference to explain errors to the user. **Do not guess error meanings** — look up the code below.

---

## How to Handle Errors

When a snapctl command fails:
1. Check the exit code against the tables below
2. Explain the error clearly to the user
3. Suggest the recommended recovery action
4. If the error persists after recovery, suggest the user contact Snapser support

---

## CLI Return Codes

| Code | Description | Recovery |
|------|-------------|----------|
| 0 | Success | N/A |
| 1 | General error | Check command syntax. Run `snapctl <command> --help` for usage. |
| 2 | Input error | Validate all arguments — check for typos, missing required flags, or invalid formats. |
| 3 | Resource not found | Verify the resource ID exists. Use the relevant `enumerate` command to list available resources. |
| 4 | Internal server error | Retry after a short wait. If persistent, the Snapser platform may be experiencing issues. |

## Configuration Errors

| Code | Description | Recovery |
|------|-------------|----------|
| 10 | Configuration incorrect | Run `snapctl validate` to check your API key and application config. Verify `~/.snapser/config` is correct. |
| 11 | Configuration error | Run `snapctl validate` to diagnose. Check `~/.snapser/config` is correct. |
| 12 | Dependency missing | Install missing dependencies — check that Docker, snapctl, and required tools are available. |

## Snaps Errors

| Code | Description | Recovery |
|------|-------------|----------|
| 13 | Snaps generic error | Retry. If persistent, run `snapctl snaps enumerate` to verify snap availability. |
| 14 | Snaps enumerate error | Check API key permissions and network connectivity. |

## Snapend Manifest Errors

| Code | Description | Recovery |
|------|-------------|----------|
| 16 | Manifest create error | Validate snap names with `snapctl snaps enumerate`. Ensure no duplicate entries. |
| 17 | Manifest update error | Verify the manifest file exists and is valid JSON (always use JSON, not YAML). |
| 18 | Manifest upgrade error | Check that target snap versions exist. |

## BYOGS Errors

| Code | Description | Recovery |
|------|-------------|----------|
| 20 | Generic BYOGS error | Check BYOGS configuration and retry. |
| 21 | BYOGS dependency missing | Ensure Docker is installed and running. |
| 22 | BYOGS ECR login error | Re-authenticate: verify API key has ECR permissions. |
| 23 | BYOGS build error | Check Dockerfile syntax and build context. Run `docker build` locally to debug. |
| 24 | BYOGS tag error | Verify tag format — must be valid Docker tag. |
| 25 | BYOGS publish error | Check network connectivity and ECR permissions. |
| 26 | BYOGS publish permission error | User lacks publish permissions. Verify API key scopes or contact org admin. |
| 27 | BYOGS publish duplicate tag error | Use a different tag — this tag already exists in the registry. |

## BYOSnap Errors

| Code | Description | Recovery |
|------|-------------|----------|
| 30 | Generic BYOSnap error | Check BYOSnap configuration and retry. |
| 31 | BYOSnap dependency missing | Ensure Docker is installed and running. Verify snapctl is up to date. |
| 32 | BYOSnap ECR login error | Re-authenticate: verify API key has ECR permissions. |
| 33 | BYOSnap build error | Check Dockerfile and build context. Run `docker build` locally to isolate the issue. |
| 34 | BYOSnap tag error | Verify tag follows semantic versioning (e.g., `v0.0.1`). |
| 35 | BYOSnap publish image error | Check network and ECR permissions. Retry. |
| 36 | BYOSnap publish image permission error | API key lacks publish permissions. Verify scopes or contact org admin. |
| 37 | BYOSnap publish image duplicate tag error | This image tag already exists. Bump the version. |
| 38 | BYOSnap create error | Verify profile with `snapctl byosnap validate-profile` before retrying. |
| 39 | BYOSnap create permission error | API key lacks create permissions. Check scopes. |
| 40 | BYOSnap create duplicate name error | A BYOSnap with this name already exists. Choose a different name. |
| 41 | BYOSnap publish version error | Validate profile and ensure image was published first. |
| 42 | BYOSnap publish version permission error | API key lacks version publish permissions. |
| 43 | BYOSnap publish version duplicate version error | This version already exists. Bump the version number. |
| 44 | BYOSnap publish version duplicate tag error | Tag already in use. Use a unique tag. |
| 45 | BYOSnap update version error | Verify the version exists and the BYOSnap ID is correct. |
| 46 | BYOSnap update version — service in use | Cannot update: this version is actively deployed. Deploy a new version instead, or remove it from the Snapend first. |
| 47 | BYOSnap update version tag error | Invalid tag format. |
| 48 | BYOSnap update version — invalid version | Version format invalid. Use semantic versioning: `v0.0.1`, `v1.0.0`. |
| 49 | BYOSnap publish error | General publish failure. Validate profile, check permissions, retry. |
| 86 | BYOSnap generate-profile error | Check the project structure. Ensure a valid Dockerfile and service entry point exist. |
| 87 | BYOSnap swagger error | Verify the Swagger/OpenAPI spec is valid JSON or YAML. |

## Application Errors

| Code | Description | Recovery |
|------|-------------|----------|
| 50 | Generic application error | Retry. Check API key and application ID. |
| 51 | Application create error | Verify application name and parameters. |
| 52 | Application create permission error | API key lacks application create permissions. |
| 53 | Application create limit error | Organization has reached its application limit. Contact Snapser to increase. |
| 54 | Application create duplicate name error | An application with this name already exists. Choose a different name. |
| 55 | Application enumerate error | Check API key permissions and network connectivity. |

## Snapend Errors

| Code | Description | Recovery |
|------|-------------|----------|
| 60 | Generic Snapend error | Check Snapend ID and retry. |
| 61 | Snapend enumerate error | Verify API key and application ID are correct. |
| 62 | Snapend clone error | Verify source Snapend exists and is healthy. |
| 63 | Snapend clone server error | Server-side issue. Retry after a short wait. |
| 64 | Snapend clone timeout | Operation timed out. Retry — the Snapend may still be provisioning. Run `snapctl snapend enumerate` to check status. |
| 65 | Snapend apply error | Validate the manifest before applying. |
| 66 | Snapend apply server error | Server-side issue. Retry. |
| 67 | Snapend apply timeout | Operation timed out. Check Snapend status with `snapctl snapend enumerate`. |
| 68 | Snapend promote error | Verify the Snapend is healthy before promoting. |
| 69 | Snapend promote server error | Server-side issue. Retry. |
| 70 | Snapend promote timeout | Retry. Check target environment availability. |
| 71 | Snapend download error | Verify the Snapend is fully deployed. Retry. |
| 72 | Snapend update error | Validate snap names/versions. Check manifest. |
| 73 | Snapend update server error | Server-side issue. Retry. |
| 74 | Snapend update timeout | Operation timed out. Run `snapctl snapend enumerate` to check status. May need to retry. |
| 75 | Snapend state error | Snapend is in an unexpected state. Run `snapctl snapend enumerate` to check. May need to wait for a transition to complete. |
| 76 | Snapend manifest mismatch | The manifest doesn't match the Snapend's current state. Re-sync with `snapctl snapend-manifest sync`. |
| 77 | Snapend create error | Validate manifest and snap names. Ensure Snapend name is unique (max 20 chars, alphanumeric + dashes, starts with letter). |
| 78 | Snapend create server error | Server-side issue. Retry. |
| 79 | Snapend create timeout | Operation timed out. Run `snapctl snapend enumerate` to check if creation succeeded. |

## Generate Errors

| Code | Description | Recovery |
|------|-------------|----------|
| 80 | Generic generate error | Retry. Check input parameters. |
| 81 | Generate credentials error | Verify API key is valid and has correct permissions. |

## BYOWS Errors

| Code | Description | Recovery |
|------|-------------|----------|
| 95 | Generic BYOWS error | Verify the Snapend is in DEVELOPMENT and has a BYOSnap deployed. |
| 96 | BYOWS attach error | Check that the Snapend and BYOSnap IDs are correct. Ensure no other BYOWS session is attached. |
| 97 | BYOWS reset error | Try detaching first (`snapctl byows detach`), then re-attach. |
| 98 | BYOWS detach error | The session may already be detached. Verify with `snapctl snapend enumerate`. |

## Secret Errors

| Code | Description | Recovery |
|------|-------------|----------|
| 100 | Generic secret error | Retry. Verify `--application-id` is set (flag, `SNAPSER_APPLICATION_ID` env var, or config). |
| 101 | Secret enumerate error | Retry. Verify the application ID and API key permissions. |
| 102 | Secret get error | Verify the `--file-name` exists — list secrets with `snapctl secret enumerate`. |
| 103 | Secret create error | Check `--file-name` and `--tag` match `^[-._a-zA-Z0-9]+$` (1–253 chars) and the value is under 65536 bytes. Pass exactly one of `--value` or `--from-file`. |
| 104 | Secret create duplicate error | The (file_name, tag) pair already exists (backend api_error_code 588). Secrets are append-only — create again with a new `--tag` to rotate. |
| 106 | Secret delete error | Verify the file_name (and tag, if passed) exists via `snapctl secret get`. |
| 107 | Secret delete blocked | The secret/tag is referenced by a cluster manifest (backend api_error_code 582). Remove the SecretRef from the BYOSnap profile / Snapend first, then delete. |
| 108 | Secret reveal error | `--tag` is required on reveal. Verify the (file_name, tag) pair exists via `snapctl secret get`. |

## Login Errors

| Code | Description | Recovery |
|------|-------------|----------|
| 110 | Login error | Retry `snapctl login`. If the browser did not open, use the printed verification URL and code manually. As a fallback, use `snapctl login --paste` with a key from the Developer Center. |
| 111 | Login flow error | The browser device flow failed or timed out. Retry `snapctl login`; check network/proxy. Fall back to `snapctl login --paste`. |

## Admin SDK Errors

| Code | Description | Recovery |
|------|-------------|----------|
| 113 | Generic Admin SDK error | Verify the `--snaps name:version` pairs against `snapctl snaps enumerate` — only versions with `has_admin=true` are accepted, and versions require the `v` prefix (e.g. `auth:v1.0.0`). |
| 114 | Admin SDK download error | Retry the download. Check network connectivity and that `--out-path` is an existing directory. |
