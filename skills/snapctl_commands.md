# Snapser CLI

Snapser has developed a CLI tool called **snapctl** that can be used on MacOSX, Linux and Windows machines.
Snapctl will be the best way for game studios to integrate Snapser into their build pipelines.

## What's new in the latest version?
### Breaking Changes
1. Renamed SDK type `server` to `api-key` to be consistent with the Snapser Web app.

### Features
1. Added `snapctl login` — a browser-based flow that mints and stores your API key automatically. Manual key setup is no longer needed. See "Setup" below.
2. Added `snapctl admin-sdk download` — download the Admin SDK to configure Snapend snap settings programmatically. See `skills/configure-snap-settings/SKILL.md`.
3. Added support for Bring your own Workstation commands. This enables local debugging for your BYOSnaps while clients continue to access your cloud Snapend APIs.
```bash
snapctl byows attach --snapend-id $snapend_id --byosnap-id $byosnap_id --http-port $http_port
```
```bash
snapctl byows reset --snapend-id $snapend_id
```

## Requirements
### Python 3.X and Pip
The Snapser CLI tool depends on Python 3.X and Pip. MacOS comes pre installed with Python. But
please make sure you are running Python 3.X. On Windows, you can download Python 3.X from the
Windows store.

### Docker
Some of the commands also need docker. You can download the latest version of Docker from the
[Docker website](https://www.docker.com/products/docker-desktop).

**IMPORTANT**: Open up Docker desktop and settings. Make sure this setting is disabled
**Use containerd for pulling and storing images**. This is because Snapser uses Docker
to build and push images to the Snapser registry. Having this setting enabled will
cause issues with the Snapser CLI tool.

## Installation

### Pip
Installing PIP on MacOS

```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

Installing PIP on Windows

```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

### Pipx
Now a days, pipx is recommended for CLI tools. Once you have Python and Pip installed, lets install `Pipx`.
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

### Install Snapctl
 - If you chose to use Pip
```bash
pip install --user snapctl
```

If you also have Python 2.X on your machine, you may have to run the following command instead

```bash
pip3 install --user snapctl
```
- If using, Pipx
```bash
pipx install snapctl
```

**IMPORTANT**: After you install snapctl you may have to add the python bin folder to your
path. For example, on MacOSX this is usually **~/Library/Python/3.9/bin**. On
Windows this is usually **C:\Users\username\AppData\Roaming\Python\Python39\Scripts**.
For, Windows users, after running pipx ensurepath, you may need to restart your terminal (Command Prompt, PowerShell, or Windows Terminal) for the PATH changes to take effect.


## Upgrade

Upgrade your snapctl version

- If using Pip

```bash
pip3 install --user snapctl --upgrade
```

- If using Pipx
```bash
pipx upgrade snapctl
```

## Setup

### Log in (recommended)

```bash
snapctl login
```

This runs a browser-based device flow: snapctl prints a short code (`XXXX-XXXX`) and a
verification URL, and opens your browser. Confirm the code matches and click **Activate**
in the Snapser web app. A freshly minted API key is saved to `~/.snapser/config`
automatically — you never see or handle the key itself.

Behavior and flags:

- **Idempotent** — if a valid key is already stored it prints "Already logged in as …" and exits. Safe to run any time. An expired/invalid key self-heals into a new login.
- `--force` — re-mint even if an active key exists.
- `--profile <name>` — save under `[profile <name>]` instead of `[default]`.
- `--portal-endpoint <url>` — (Enterprise) log in against a custom portal URL. Persisted as `PORTAL_ENDPOINT` in the profile, so subsequent logins don't need the flag.
- `--key-name <label>` — label for the minted key (default: `snapctl-<host>-<date>`).
- `--paste` — paste a key manually instead of the browser flow (see fallback below).
- `--api-key <key>` — non-interactive key injection for CI.

To sign out:

```bash
snapctl logout
```

### Fallback / CI setup

When no browser is available (headless box, CI pipeline), generate a key manually:
log in to the Snapser web app → user icon (top right) → **User Account** → **Developer** →
**Generate**. You can have up to 3 API keys per account, and a key is shown only once.

Then either:

1. `snapctl login --paste` and paste the key when prompted (stores it in `~/.snapser/config`), or
2. `snapctl login --api-key <your_key>` non-interactively (CI), or
3. Pass `--api-key <your_key>` per command, or set the `SNAPSER_API_KEY` environment variable. Precedence: command-line argument > environment variable > config file.

Multiple accounts are supported via profiles in `~/.snapser/config` — use `snapctl login --profile <name>` to add one, and `--profile <name>` on any command to select it. A custom config location can be set with `SNAPSER_CONFIG_PATH='<your_custom_path>'`.

**Never write `~/.snapser/config` by hand — `snapctl login` owns that file. Never echo an API key into terminal output or logs.**

## Verify Snapctl installation

```
snapctl validate
```

Output will tell you if the Snapctl was able successfully validate your setup with the remote Snapser server
or not.

## Advanced Setup

Snapser by default supports access to multiple accounts via profiles. Add a profile with:

```
snapctl login --profile <profile_name>
```

You can then set an environment variable telling Snapser which profile you want to use.

```
# Mac
export SNAPSER_PROFILE="my_profile_name";

```

```
# Windows
setx SNAPSER_PROFILE="my_profile_name";

```

Or you can pass **--profile professional** with every command to tell Snapser to use a particular profile.

## Command variable name nomenclature
All commands follow these rules with their input variables
1. A variable that is named `*path` = CLI tool expects a path to a **folder**
2. A variable that is named `*filename` = CLI tool expects the name of the file, without the path.
3. A variable that is named `*path_filename` = CLI tool expects the full path. The folder up to the name of the file.

## Response structure
Unless a command outputs a binary eg: Downloading of an SDK all success and error responses have this format
```json
{"error": $errorBool, "code": $responseCode, "msg": $message, "data": $object}
```
About the response object:
1. $errorBool = boolean: true or false
2. $responseCode = integer: Snapctl response codes mentioned below
3. $message = string: Message string describing the output
3. $object = object: JSON Object with the details about the request


## Commands

Run the following to see the list of commands Snapser supports

```bash
snapctl --help
```

### 1. Snaps
Snapctl commands for snaps

#### 1. snaps help
See all the supported commands.

```bash
# Help for the byosnap command
snapctl snaps --help
```

#### 2. snaps enumerate
See all the supported commands.

```bash
# Enumerate details for all the available snaps
# $output_path_filename = Optional path and filename ending in .json, where you want snapctl to save snap details. If not passed, the list is printed on the console.
snapctl snaps enumerate
snapctl snaps enumerate --out-path-filename ./snaps.json
```

### 2. BYO Snap - Bring your own Snap
Snapctl commands for your custom code

#### 1. byosnap help

See all the supported commands.

```bash
# Help for the byosnap command
snapctl byosnap --help
```

#### 2. byosnap generate-profile

This command generates a base BYOSnap profile. You will have to update the values within this file
and then you can use it in commands like `publish` and `sync`. It is recommended that you save this
file at the root of your BYOSnap code and commit it to version control.

```bash
# Help for the byosnap command
snapctl byosnap generate-profile --help

# Generate your BYOSnap profile
# $output_path = Directory where you want the BYOSnap profile to be saved.
# $profile_filename = Name of the BYOSnap profile you want to give. Only .json, .yaml, .yml extensions
#   are allowed. If you do not pass `--profile-filename` then Snapser choses
#   `snapser-byosnap-profile.json` as the filename.
snapctl byosnap generate-profile --out-path $output_path --profile-filename $profile_filename
snapctl byosnap generate-profile --out-path /Users/DevName/Development/SnapserEngine/byosnap-python --profile-filename=my-byosnap-profile.json
snapctl byosnap generate-profile --out-path /Users/DevName/Development/SnapserEngine/byosnap-python --profile-filename=my-byosnap-profile.yaml
```

#### 3. byosnap validate-profile

This command validates your BYOSnap profile.

```bash
# Help for the byosnap command
snapctl byosnap validate-profile --help

# Validate your BYOSnap profile
# $path = Directory Path to where your BYOSnap Profile is located. No need to add the file name.
# $resources_path = Optionally, you can place your BYOSnap profile at your resources path
# $profile_filename = Optional parameter. Name of your BYOSnap profile.
#   If you do not pass `--profile-filename` then
#   Snapser choses the default `snapser-byosnap-profile.json` as the filename to validate
snapctl byosnap validate-profile --path $path
snapctl byosnap validate-profile --resources-path $resources_path --profile-filename $profile_filename
snapctl byosnap validate-profile --path /Users/DevName/Development/SnapserEngine/byosnap-python
snapctl byosnap validate-profile --path /Users/DevName/Development/SnapserEngine/byosnap-python --profile-filename my-byosnap-profile.yaml
```

#### 4. byosnap publish

This command allows you to create and publish your BYOSnap. Running this command will first create a BYOSnap namespace on Snapser if not present. Then it will build and publish your code to your own
private ECR repo on Snapser. Finally it will assign a version to your BYOSnap so that you
can deploy it.

**Requirements**:
- This command needs docker.
- This command needs a BYOSnap profile. BYOSnap profile, holds information about
your BYOSnap like, name, description, etc and hardware requirements like CPU, Memory. We
recommend you store this file at the root of your BYOSnap and also add it to version control.
You can generate it using `snapctl byosnap generate-profile --out-path $outputPath --profile-filename $profileName`.

```bash
# Help for the byosnap command
snapctl byosnap publish --help

# Create and publish your BYOSnap
# $byosnap_id = Snap ID for your snap
# $version = Semantic version for your snap Eg: v0.0.1
# $code_root_path = Local code path where your Dockerfile is present
# $resources_path = Optional path to the resources directory in your Snap. This ensures, you are not forced to put the Dockerfile, snapser-byosnap-profile.json, swagger.json and README.md at the root directory of your Snap.
# $profile_filename = Optional parameter. Name of your BYOSnap profile.
#   If you do not pass `--profile-filename` then
#   Snapser choses the default `snapser-byosnap-profile.json` as the filename to validate
# $skip-build = true/false. Default is false. Pass this flag as true to skip the build and head straight to tag and push. Build step needs to run and tag using the --tag you pass to the publish-image command for this to work. Make sure the tag matches the version number you are passing.
# Example:
snapctl byosnap publish --byosnap-id byosnap-jinks-flask --version "v0.0.1" --path /Users/DevName/Development/SnapserEngine/byosnap-python --profile-filename $profile_filename
snapctl byosnap publish --byosnap-id $byosnap_id --version $version --path $code_root_path
snapctl byosnap publish --byosnap-id byosnap-python --version "v1.0.0" --path /Users/DevName/Development/SnapserEngine/byosnap-python --profile-filename my-byosnap-profile.yaml
```

#### 5. byosnap sync

This command is for development purposes. It allows developers to rapidly build, update and push their BYOSnap to a dev Snapend. Simply, make changes to your code locally, and then run this command to deploy your BYOSnap straight to your development Snapend.

**Requirements**:
- This command needs docker.

**IMPORTANT**: This command will only work for Dev Snapends. Additionally if the version you are using in this command happens to be used by a staging or a production snapend then `sync` will not work. We do this to ensure that your staging and production BYOSnap images do not get impacted.

```bash
# Help for the byosnap command
snapctl byosnap sync --help

# Deploy local code straight to your Snapend
# $byosnap_id = Snap ID for your snap
# $code_root_path = Local code path where your Dockerfile is present
# $resources_path = Optional path to the resources directory in your Snap. This ensures, you are not forced to put the Dockerfile, swagger.json and README.md in the root directory of your Snap.
# $skip-build = true/false. Default is false. Pass this flag as true to skip the build and head straight to tag and push. Build step needs to run and tagged using the --tag you pass to the publish-image command for this to work.
# $tag = Semantic version for your snap Eg: v0.0.1
# $version =
# $snapend_id = Dev Snapend Id
# Example:
snapctl byosnap sync --byosnap-id byosnap-jinks-flask --path /Users/DevName/Development/SnapserEngine/byosnap-python --version "v0.0.11" --snapend-id "jxmmfryo"
snapctl byosnap sync --byosnap-id $byosnap_id --path $code_root_path --version $version --snapend-id $snapend_id
```

#### 6. byosnap create

Create a custom snap. Note that you will have to build, push and publish your snap image, for it to be useable
in a Snapend.

```bash
# Help for the byosnap command
snapctl byosnap create --help

# Create a new snap
# $byosnap_id = Snap ID for your snap. Start start with `byosnap-`
# $name = User friendly name for your BYOSnap
# $desc = User friendly description
# $platform = One of linux/arm64, linux/amd64
# $language = One of go, python, ruby, c#, c++, rust, java, node

# Example:
# snapctl byosnap create --byosnap-id byosnap-jinks-flask --name "Jinks Flask Microservice" --desc "Custom Microservice" --platform "linux/arm64" --language "go"
snapctl byosnap create --byosnap-id $byosnap_id --name "$name" --desc "$desc" --platform "$platform" --language "$language"
```

#### 7. byosnap upload-docs

Upload swagger.json and README.md for you Snap

```bash
# Help for the byosnap command
snapctl byosnap upload-docs --help

# Publish a new image
# $byosnap_id = Snap ID for your snap
# $image_tag = An image tag for your snap
# $resources_path = Path to your swagger.json and README.md files
# Example:
# snapctl byosnap upload-docs --byosnap-id byosnap-jinks-flask --tag my-first-image --resources-path /Users/DevName/Development/SnapserEngine/byosnap-python
snapctl byosnap upload-docs --byosnap-id $byosnap_id --tag $image_tag --resources-path $resources_path
```

#### 8. byosnap publish-image

**Deprecation notice**: `byosnap create`, `byosnap publish-image`, `byosnap publish-version` and `byosnap update-version` will be deprecated soon. Use `byosnap publish` (or `byosnap direct-deploy` for development) instead.

Publish a custom snap code image. This command executes the build, push and `upload-docs` steps one
after the other.

**IMPORTANT**: Take note of the hardware architecture of machine and your Dockerfile commands.
Commands in docker file may be hardware architecture specific. Snapser throws a warning if it detects
a mismatch.

```bash
# Help for the byosnap command
snapctl byosnap publish-image --help

# Publish a new image
# $byosnap_id = Snap ID for your snap
# $image_tag = An image tag for your snap
# $code_root_path = Local code path where your Dockerfile is present
# $resources_path = Optional path to the resources directory in your Snap. This ensures, you are not forced to put the Dockerfile, swagger.json and README.md in the root directory of your Snap.
# $skip-build = true/false. Default is false. Pass this flag as true to skip the build and head straight to tag and push. Build step needs to run and tagged using the --tag you pass to the publish-image command for this to work.
# Example:
# snapctl byosnap publish-image --byosnap-id byosnap-jinks-flask --tag my-first-image --path /Users/DevName/Development/SnapserEngine/byosnap-python
snapctl byosnap publish-image --byosnap-id $byosnap_id --tag $image_tag --path $code_root_path
snapctl byosnap publish-image --byosnap-id $byosnap_id --tag $image_tag --path $code_root_path --resources-path $resources_path
snapctl byosnap publish-image --byosnap-id $byosnap_id --tag $image_tag --skip-build
```

#### 9. byosnap publish-version

Publish a new version for your Snap. Only after your Snap version is published, you will be able
to use your snap in your Snapend. This command should be run after `push` or `publish-image` commands.

IMPORTANT: You need to have $byosnapProfile to run this command. BYOSnap profile is a JSON configuration
of your BYOSnap for the development, staging and production environments. You can generate a base version of this file using the `snapctl byosnap generate-profile --out-path $outputPath --profile-filename $profileName` command.

```bash
# Help for the byosnap command
snapctl byosnap publish-version --help

# Publish a new image
# $byosnap_id = Snap ID for your snap
# $image_tag = An image tag for your snap
# $version = Semantic version for your snap Eg: v0.0.1
# $byosnap_profile_path = Path to the snapser-byosnap-profile.json BYOSnap profile to configure dev, stage and prod settings for this snap. You can generate a base version of this file using the `snapctl byosnap generate-profile --out-path $outputPath --profile-filename $profileName` command
# Example:
# snapctl byosnap publish-version --byosnap-id byosnap-jinks-flask --tag my-first-image --version v0.0.1 --path /Users/DevName/Development/SnapserEngine/byosnap-python
snapctl byosnap publish-version --byosnap-id $byosnap_id --tag $image_tag --version $version --path $byosnap_profile_path
```

#### 10. byosnap direct-deploy [NEW]

Direct deploy your BYOSnap to a Snapend, without having to publish it. With this new command, there is no need for you to publish your byosnap and or sync it before using. Any dev can now just directly deploy their byosnap to a snapend and then use byows to attach and start debugging locally. Once you are happy with your BYOSnap you can then publish it for others to use

```bash
# Help for the byosnap command
snapctl byosnap direct-deploy --help

# Direct deploy a new image
# $byosnap_id = Snap ID for your snap
# $snapend_id = Snapend Id
# $code_root_path = Local code path where your Dockerfile is present
# $resources_path = (Optional) path to the resources directory in your Snap. This ensures, you are not forced to put the Dockerfile, swagger.json and README.md in the root directory of your Snap.
# $platform = (Optional) One of linux/arm64, linux/amd64. In case you want to override the platform
# Example:
# snapctl byosnap direct-deploy --byosnap-id byosnap-jinks-flask --snapend-id jxmmfryo --path /Users/DevName/Development/SnapserEngine/byosnap-python
snapctl byosnap direct-deploy --byosnap-id $byosnap_id --snapend-id $snapend_id --path $code_root_path
```

#### 11. byosnap next-version

A read-only helper that tells you the next versions you can publish for a BYOSnap, based on its highest already-published version. Handy because `publish` requires a version strictly greater than the latest one. It prints the next patch, minor, and major options. For a BYOSnap that has nothing published yet, it suggests a valid starting version.

```bash
# Help for the byosnap command
snapctl byosnap next-version --help

# Show the next publishable versions
# $byosnap_id = Snap ID for your snap
# Example: if the latest published version is v1.0.1, this prints
#   patch -> v1.0.2 | minor -> v1.1.0 | major -> v2.0.0
snapctl byosnap next-version --byosnap-id $byosnap_id
```

### 3. BYO Workstation - Bring your own Workstation
Snapctl commands for bring your own workstation. This command allows you to attach your workstation to a Snapend. This is useful for testing and debugging your BYOSnap code.

#### 1. byows help
See all the supported commands

```bash
# Help for the byows command
snapctl byows --help
```
#### 2. byows attach
Attach your workstation to a Snapend. It should be noted, that this command outputs a file `byows_env_setup.sh|ps1` at `~/.snapser/` directory. This file contains the environment variables that the BYOWS technology will need to route internal calls to the appropriate Snaps.

```bash
# Attach your workstation to a Snapend
# $snapend_id = Snapend Id
# $byosnap_id = BYOSnap Id
# $http_port = Port that your local server is running on
snapctl byows attach --snapend-id $snapend_id --byosnap-id $byosnap_id --http-port $http_port
```

Then run, the following command in a separate terminal window, to setup the BYOWS environment variables.
```bash
# MacOSX
source ~/.snapser/byows_env_setup.sh
# Windows
.\.snapser\byows_env_setup.ps1
```

Then start your BYOSnap local server in the same tab that has the environment variables set up. This will ensure that the BYOSnap code can access the internal SDK and other Snaps in your Snapend.

#### 3. byows detach
Detach your workstation from a Snapend. This stops forwarding traffic to your local machine for the specified BYOSnap.

```bash
# Detach your workstation from a Snapend
# $snapend_id = Snapend Id
# $byosnap_id = BYOSnap Id
snapctl byows detach --snapend-id $snapend_id --byosnap-id $byosnap_id
```

#### 4. byows reset
Reset the BYOWS state for a Snapend. Useful when an attach is left in a bad state and you want to start fresh.

```bash
# Reset your workstation attachment state for a Snapend
# $snapend_id = Snapend Id
snapctl byows reset --snapend-id $snapend_id
```

### 4. BYO Game Server - Bring your own Game Server
Snapctl commands for your custom game server

#### 1. byogs help

See all the supported commands

```bash
# Help for the byogs command
snapctl byogs --help
```

#### 2. byogs publish

Publish your custom game server image. This commend replaces the old way of creating, publishing image and
then publishing the byogs. Now all you have to do is publish your image and create a fleet using the web portal.

**IMPORTANT**: Take note of the hardware architecture of machine and your Dockerfile commands.
Commands in docker file may be hardware architecture specific. Snapser throws a warning if it detects
a mismatch.

```bash
# Help for the byogs command
snapctl byogs publish --help

# Publish a new image
# $image_tag = An image tag for your snap
# $code_root_path = Local code path where your Dockerfile is present
# $resources_path = Optional path to the resources directory. This ensures, you are not forced to put the Dockerfile at the root directory of your Game Server code.
# $skip-build = Default is false. Pass this flag as true to skip the build and head straight to tag and push. Build step needs to run and tagged using the --tag you pass to the publish-image command for this to work.
# Example:
# snapctl byogs publish --tag my-first-image --path /Users/DevName/Development/SnapserEngine/game_server
snapctl byogs publish --tag $image_tag --path $code_root_path
snapctl byogs publish --tag $image_tag --path $code_root_path --resources-path $resources_path
snapctl byogs publish --tag $image_tag --skip-build
```

#### 3. byogs sync

This command allows developers to rapidly build, update and push their BYOGs out to a Snapend fleet. Simply, make changes to your code locally, and then run this command to deploy your BYOGs straight to your Snapend fleet.

```bash
# Help for the byogs command
snapctl byogs sync --help

# Publish a new image
# $code_root_path = Local code path where your Dockerfile is present
# $resources_path = Optional path to the resources directory in your Snap. This ensures, you are not forced to put the Dockerfile, swagger.json and README.md in the root directory of your Snap.
# $skip-build = true/false. Default is false. Pass this flag as true to skip the build and head straight to tag and push. Build step needs to run and tagged using the --tag you pass to the publish-image command for this to work.
# $image_tag = An image tag for your snap. Note snapctl adds a timestamp, allowing you to use the same command.
# $snapend_id = Snapend Id
# $fleet_names = Comma separated fleet names
# Example:
snapctl byogs sync --path /Users/DevName/Development/SnapserEngine/game_server --tag my-first-image --snapend-id "jxmmfryo" --fleet-names "my-fleet,my-second-fleet"
snapctl byogs sync --path $code_root_path --tag $image_tag --snapend-id $snapend_id --fleet-names $fleet_names
```

### 5. Application
Snapctl commands for your application

**Note**: The older `snapctl game` command (`create`, `enumerate`) is deprecated. Use the equivalent `snapctl application` commands instead.

#### 1. application help

See all the supported commands

```bash
# Help for the byogs command
snapctl application --help
```

#### 2. application create
Create an application
```bash
snapctl application create --name $app_name
```

#### 3. application enumerate
List all the applications
```bash
snapctl application enumerate
```

### 6. Snapend Manifest
Snapctl commands for the Snapend manifest. Manifest is the representation of your Snapser backend
stored as a JSON or YAML. The manifest can then be used to create, update your backend.
**Always use JSON** — YAML currently has a long-integer serialization issue and can be flaky.

#### 1. snapend-manifest help

See all the supported commands

```bash
# Help for the byogs command
snapctl snapend-manifest --help
```

#### 2. Snapend Manifest Create

Create a Snapend manifest. It should be noted that the latest versions of the snap at the time of running the command is what gets added to the manifest. For example, say the `analytics` snap has versions `v1.0.0`, `v1.1.0` available on the web portal. If you run the create command with `--snaps analytics` the `v1.1.0` which is the latest at that moment in time, gets added to your manifest.

The output manifest file can then be used with the `snapend create` or `snapend clone` commands.

```bash
# Create a Snapend manifest file
# $name = Name for your backend, which is stored in the outputted manifest
# $env = One of DEVELOPMENT, STAGING or PRODUCTION
# $output_path_filename = Path and file name to store the manifest. Use a .json filename (do NOT use yaml)
# $snaps = Comma separated list of snap ids you want to add.  You can get the snap ids from the
#     `snapctl snaps enumerate --out-path-filename ./snaps.json` command
# $features = Pass `WEB_SOCKETS` if you want to enable web sockets for your backend.
# Note: One of snaps or features is required
# Example:
#   snapend-manifest create --name my-dev-snapend --env DEVELOPMENT --snaps auth,analytics --add-features WEB_SOCKETS --out-path-filename ./snapend-manifest.json

snapctl snapend-manifest create --name $name --env $env --snaps $snaps --features $features --out-path-filename $output_path_filename
```

#### 3. Snapend Manifest Sync

Sync with an existing Snapend manifest. This command is idempotent and destructive.

- It ensures the input manifest gets replaced with the values you pass in `--snaps` and `--features`. For example: If your input manifest has a snap but you do not pass the snap in the `--snaps`, it will be removed from the output. Same goes for `--features`.
- Additionally, if a snap is present in the manifest and you pass it in as part of `--snaps` it will not be touched. But if a snap is not part of the manifest and you pass it in as part of `--snaps` it will be added with the latest version of the snap. For example, say the `analytics` snap has versions `v1.0.0`, `v1.1.0` available on the web portal. If you run the sync command with `--snaps analytics` and you had `v1.0.0` in the manifest then it wont be touched. However, if you did not have it in the manifest then the `v1.1.0` which is the latest at that moment in time, gets added to your manifest.

**IMPORTANT**: If you are looking for a command to purely add or remove snaps or features, consider using the `update` command instead.

```bash
# Sync a Snapend manifest file
# $input_manifest = Path and file name of the current manifest. Use a .json filename (do NOT use yaml)
# $output_path_filename = Path and file name to store the manifest. Use a .json filename (do NOT use yaml)
# $snaps = Comma separated list of snap ids you want to have at the end. You can get the snap ids from # the `snapctl snaps enumerate --out-path-filename ./snaps.json` command.
#   IMPORTANT: If your manifest has a snap but your --snaps does not. It will be removed.
# $features = Pass `WEB_SOCKETS` if you want to enable web sockets for your backend.
#   IMPORTANT: If your manifest has a feature but your --features does not. It will be removed.
# Note: One of snaps, and features is required
# Example:
#   snapctl snapend-manifest sync --manifest-path-filename ./snapser-jn86b0dv-manifest.json --snaps auth,game-server-fleets --features WEB_SOCKETS --out-path-filename ./snapend-updated-manifest.json

snapctl snapend-manifest sync --manifest-path-filename $input_manifest --snaps $snaps --features $features --out-path-filename $output_path_filename
```

#### 4. Snapend Manifest Upgrade

Upgrade all snaps or a list of snaps to the latest version of the snap available at that moment in time. If you do not pass in `--snaps` then all the snaps in the manifest will be upgraded. If you do pass a list of snaps then all snap Ids are expected to be valid.

```bash
# Update a Snapend manifest file
# $input_manifest = Path and file name of the current manifest. Use a .json filename (do NOT use yaml)
# $output_path_filename = Path and file name to store the manifest. Use a .json filename (do NOT use yaml)
# $snaps = (Optional) Comma separated list of snap ids you want to upgrade. You can get the snap ids
#   from the `snapctl snaps enumerate --out-path-filename ./snaps.json` command
#   IMPORTANT: If the --snaps parameter is not provided then all snaps in the manifest will be upgraded
# Example:
# snapctl snapend-manifest upgrade --manifest-path-filename ./snapser-jn86b0dv-manifest.json --snaps game-server-fleets --out-path-filename ./snapend-updated-manifest.json
# snapctl snapend-manifest upgrade --manifest-path-filename ./snapser-jn86b0dv-manifest.json --out-path-filename ./snapend-updated-manifest.json

snapctl snapend-manifest upgrade --manifest-path-filename $input_manifest --out-path-filename $output_path_filename

snapctl snapend-manifest upgrade --manifest-path-filename $input_manifest --snaps $snaps --out-path-filename $output_path_filename
```

#### 5. Snapend Manifest Update

Update your manifest. This command is additive and subtractive. It allows you to add or remove, snaps and features from an existing manifest. Unlike `sync`, this will only add or remove entities from your manifest, keeping the remaining part of the manifest intact. If your manifest has a snap and you pass it with `--add-snaps` then it will be ignored. However if you do not have a snap and you pass it with `--add-snaps` then the latest version of the snap will be added. If you pass a snap with `--remove-snaps` that is already not in the manifest, then it will be skipped. This ensures idempotency after the initial update is made to the snapend manifest.

**IMPORTANT**:
- All additions are performed before removals.
- If you are looking to have strict relation between your input (snaps + features) and your output manifest, consider using the `sync` command.

```bash
# Update a Snapend manifest file
# $input_manifest = Path and file name of the current manifest. Use a .json filename (do NOT use yaml)
# $output_path_filename = Path and file name to store the manifest. Use a .json filename (do NOT use yaml)
# $addSnaps = Comma separated list of snap ids you want to add to your manifest. You can get the snap ids from # the `snapctl snaps enumerate --out-path-filename ./snaps.json` command.
# $removeSnaps = Comma separated list of snap ids you want to remove from your manifest. You can get the snap ids from # the `snapctl snaps enumerate --out-path-filename ./snaps.json` command.
# $addFeatures = Pass `WEB_SOCKETS` if you want to enable web sockets for your backend.
# $removeFeatures = Pass `WEB_SOCKETS` if you want to disable web sockets for your backend.
# Note: One of add-snaps, remove-snaps, add-features or remove-features is required
# Example:
#   snapctl snapend-manifest update --manifest-path-filename ./snapser-jn86b0dv-manifest.json --add-snaps game-server-fleets --remove-snaps analytics --remove-features WEB_SOCKETS --out-path-filename ./snapend-updated-manifest.json

snapctl snapend-manifest update --manifest-path-filename $input_manifest --add-snaps $addSnaps --remove-snaps $removeSnaps --add-features $addFeatures --remove-features $removeFeatures --out-path-filename $output_path_filename
```


### 7. Snapend
Snapctl commands for your snapend

#### 1. snapend help

See all the supported commands

```bash
# Help for the snapend command
snapctl snapend --help
```

#### 2. snapend download

Download Manifest, SDKs and Protos for your Snapend

```bash
# Help for the download command
snapctl snapend download --help

# Download your Snapend SDK and Protos
# $snapend_id = Cluster Id
# $category = snapend-manifest, sdk, protos
# $format = One of the supported formats:
#   snapend-manifest(json) — yaml exists but do NOT use it (long-int issue)
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
# Example:
# snapctl snapend download --snapend-id gx5x6bc0 --category snapend-manifest --format json --out-path .
# snapctl snapend download --snapend-id gx5x6bc0 --category sdk --format unity --type user --out-path .
# snapctl snapend download --snapend-id gx5x6bc0 --category sdk --format cpp --type internal --out-path .
# snapctl snapend download --snapend-id gx5x6bc0 --category protos --format raw --type messages --out-path .
# snapctl snapend download --snapend-id gx5x6bc0 --category sdk --format unity --type user --http-lib unitywebrequest --out-path .
snapctl snapend download --snapend-id $snapend_id --category $category --format $format --type $type --out-path $out_path
snapctl snapend download --snapend-id $snapend_id --category $category --format $format --type $type --http-lib $http_lib --out-path $out_path
```

#### 3. snapend create

Create a Snapend from an existing manifest. Passing the blocking flag ensures your CLI command waits till the new Snapend is up.

```bash
# Help for the crete command
snapctl snapend create --help

# Create a Snapend
# $application_id = Application Id. Instead of passing this as an argument, you can set it with the SNAPSER_APPLICATION_ID environment variable or in your Snapser config under the SNAPSER_APPLICATION_ID key.
# $path_to_manifest = Path to the manifest file; should include the file name
# Optionally override name and environment by passing the --name and --environment overrides
# Example:
# snapctl snapend create --manifest-path-filename $path_to_manifest --application-id $application_id  --blocking
snapctl snapend create --manifest-path-filename $path_to_manifest --application-id $application_id
snapctl snapend create --manifest-path-filename $path_to_manifest --application-id $application_id --blocking
snapctl snapend create --name $name --env $env --manifest-path-filename $path_to_manifest --application-id $application_id --blocking
```

#### 4. snapend clone

Clone a Snapend from an existing manifest. Passing the blocking flag ensures your CLI command waits till the new Snapend is up.

```bash
# Help for the clone command
snapctl snapend clone --help

# Clone your Snapend
# $application_id = Application Id. Instead of passing this as an argument, you can set it with the SNAPSER_APPLICATION_ID environment variable or in your Snapser config under the SNAPSER_APPLICATION_ID key.
# $snapend_name = Name of your new Snapend
# $env = One of development, staging
# $path_to_manifest = Path to the manifest file; should include the file name
# Example:
# snapctl snapend clone --application-id 2581d802-aca-496c-8a76-1953ad0db165 --name new-snapend --env development --manifest-path-filename "C:\Users\name\Downloads\snapser-ox1bcyim-manifest.json" --blocking
snapctl snapend clone --application-id $application_id --name $snapend_name --env $env --manifest-path-filename "$path_to_manifest"
snapctl snapend clone --application-id $application_id --name $snapend_name --env $env --manifest-path-filename "$path_to_manifest" --blocking
```

#### 5. snapend apply

Apply changes to your Snapend from a manifest. You should have the latest manifest before applying changes. Basically, when you download a manifest, Snapser adds an `applied_configuration` section to your manifest, which stores the state of the Snapend during export. Now, if someone manually updates the Snapend or a configuration of a Snap, you are no longer going to have the latest Snapend representation in the `applied_configuration`. This is how Snapser prevents you from stomping over someone elses changes.

You can optionally pass a `--force` flag telling Snapser to ignore any diffs it may find in the current state of the Snapend and the one in the `applied_configuration` field of your manifest. Essentially, this flag allows you to stomp over any changes and tell Snapser to force apply.

Separately, you can pass a blocking flag to make your CLI wait for the Snapend update to complete.


```bash
# Help for the apply command
snapctl snapend apply --help

# Apply changes to a snapend via manifest
# $path_to_manifest = Path to the manifest file; should include the file name
# --force = Optional flag to tell Snapser that you do not want it to check the diff between the Snapend states and just force apply the changes
# Example:
# snapctl snapend apply --manifest-path-filename "C:\Users\name\Downloads\snapser-ox1bcyim-manifest.json" --force --blocking
snapctl snapend apply --manifest-path-filename "$path_to_manifest"
snapctl snapend apply --manifest-path-filename "$path_to_manifest" --blocking
snapctl snapend apply --manifest-path-filename "$path_to_manifest" --force --blocking
```

#### 6. snapend update

Update your BYOSnap or BYOGs versions for the Snapend

```bash
# Help for the byogs command
snapctl snapend update --help

# Update your Snapend with new BYOSnaps and BYOGs
# $snapend_id = Cluster Id
# $byosnaps = Comma separated list of BYOSnap ids and version.
# $byogs = Comma separated list of BYOGs fleet name, id and version.
# --blocking = (Optional) This makes sure the CLI waits till your Snapend is live.
# Note at least one of the two needs to be present
# Example:
# snapctl snapend update --snapend-id gx5x6bc0 --byosnaps byosnap-service-1:v1.0.0,byosnap-service--2:v1.0.0 --byogs byogs-fleet-one:gs-1:v0.0.1,my-fleet-two:gs-2:v0.0.4
# snapctl snapend update --snapend-id gx5x6bc0 --byosnaps byosnap-service-1:v1.0.0,byosnap-service--2:v1.0.0 --byogs fleet-one:v0.0.1,fleet-two:v0.0.4 --blocking
snapctl snapend update --snapend-id $snapend_id --byosnaps $byosnaps --byogs $byogs --blocking
```

#### 7. snapend state

Get the Snapend state

```bash
# Help for the byogs command
snapctl snapend state --help

# Get the Snapend state
# $snapend_id = Cluster Id
# Example:
# snapctl snapend state --snapend-id gx5x6bc0
snapctl snapend state --snapend-id $snapend_id
```

#### 8. snapend enumerate

List all the Snapends for an application

```bash
# Help for the enumerate command
snapctl snapend enumerate --help

# Enumerate all Snapends for an application
# $application_id = Application Id. Instead of passing this as an argument, you can set it with the SNAPSER_APPLICATION_ID environment variable or in your Snapser config under the SNAPSER_APPLICATION_ID key.
snapctl snapend enumerate --application-id $application_id
```

### 8. Generate
Generator tool to help generate credentials

#### 1. generate help
See all the supported commands
```bash
# Help for the generate command
snapctl generate --help
```

#### 2. Generate ECR Credentials
Generate the ECR credentials. Game studios can use these credentials to self publish their images to Snapser.

```bash
snapctl generate credentials --category "ecr" --out-path $output_path

```


### 9. Admin SDK

Download the Admin SDK — a per-snap, per-version SDK for configuring snap settings on a
live Snapend programmatically. **The plugin already bundles the current Python Admin SDK
at `data/admin-sdk/sdk-python` — use that by default.** This download command is the
fallback for Snapends running deliberately pinned older snap versions. See
`skills/configure-snap-settings/SKILL.md` for the full workflow.

#### 1. admin-sdk help
```bash
snapctl admin-sdk --help
```

#### 2. admin-sdk download
```bash
# $snaps = comma-separated name:version pairs. The `v` prefix on versions is REQUIRED.
#          Only snap versions with has_admin=true (see `snapctl snaps enumerate`,
#          services[].versions[].has_admin) are accepted (>= v1.12.0).
# --format = ALWAYS use python (guaranteed present — snapctl itself requires Python;
#            the Python SDK is pydantic v2 with runtime validation on every call)
# NOTE: there is NO --type flag — the Admin SDK is not scoped by access type.
# $out_path = DIRECTORY to save the zip into, e.g. ./.snapser/admin-sdk
# Example: snapctl admin-sdk download --format python --snaps auth:v1.12.0,storage:v1.12.0 --out-path ./.snapser/admin-sdk
snapctl admin-sdk download --format python --snaps $snaps --out-path $out_path
```

Notes:
- The SDK is NOT tied to a Snapend — its methods take the Snapend id (`clusterId`) at call time.
- The zip lands as `snapser-admin-sdk-python-<application-id>.zip` — the trailing UUID is the game/application ID the SDK was generated for.
- The SDK's baked-in base URL is minted for the environment it was downloaded from — use it as-is.

### 10. Snap Configuration
Retrieve snap-specific configuration from a deployed Snapend.

#### 1. snap-config help
See all the supported commands
```bash
# Help for the snap-config command
snapctl snap-config --help
```

#### 2. snap-config get-config
Get the configuration for specific snaps from a Snapend. This downloads the Snapend manifest and extracts the settings for the requested snap IDs.

```bash
# Get configuration for specific snaps from a snapend
# $snaps = Comma separated list of snap IDs (e.g., analytics,auth,inventory)
# $snapend_id = The Snapend ID to fetch the configuration from
snapctl snap-config get-config --snaps $snaps --snapend-id $snapend_id
```

### 11. Secret
Snapctl commands for managing application-scoped secrets. Secrets are append-only and **tag-keyed**: every `create` writes a new `(file_name, tag)` pair, values are stored encrypted at rest, and values are returned redacted (`********`) on every operation except `reveal`. The `file_name` is the secret's primary key; `tag` is a user-chosen identifier for a specific version of a secret. Both follow the regex `^[-._a-zA-Z0-9]+$` (1–253 chars). Secret values are limited to 65536 bytes.

**There is intentionally no `update` operation.** To rotate a secret value, call `create` again with a new tag. Older tags remain available until you explicitly delete them.

**Model**
- `create` writes a new `(file_name, tag)` entry. Duplicate `(file_name, tag)` pairs are rejected by the backend.
- `enumerate` returns a rollup per secret (file_name, list of tags, timestamps).
- `get` returns the **full tag history** for a single secret, including which clusters/byosnaps reference each tag.
- `reveal` is **tag-scoped**: it requires `--tag` and returns the plaintext for that one (file_name, tag).
- `delete` works at two granularities: without `--tag` it deletes the entire secret (every tag); with `--tag` it deletes only that one tag.

For every secret subcommand you must pass `--application-id`, or set the `SNAPSER_APPLICATION_ID` environment variable / Snapser config key (same fallback as `snapctl snapend`).

**Note:** `--tag` is strictly rejected on `enumerate` and `get` — this catches typos like `snapctl secret get --tag prod --file-name foo` when you actually meant `reveal`.

#### 1. secret help
```bash
snapctl secret --help
```

#### 2. secret enumerate
List all secrets for an application. Returns a rollup per secret: `file_name`, `tags[]`, `created_at` (oldest tag), `last_updated_at` (newest tag). Values are not included — call `get` for the per-tag view.

```bash
# $application_id = Application Id (or set via SNAPSER_APPLICATION_ID).
snapctl secret enumerate --application-id $application_id
```

#### 3. secret get
Get the full tag history for a single secret. The response is `{file_name, tags: [...]}` where each tag carries `tag`, `value` (redacted), `created_at`, `updated_at`, and `usage[]` (the clusters and byosnaps that reference that specific tag).

```bash
# $file_name = Secret file name (the secret's primary key).
snapctl secret get --application-id $application_id --file-name $file_name
```

#### 4. secret create
Create a new `(file_name, tag)` entry. `--tag` is required. Pass exactly one of `--value` (inline) or `--from-file` (path to a file whose contents will be used as the value).

```bash
# Inline value with a tag:
snapctl secret create --application-id $application_id --file-name $file_name --tag $tag --value $value

# Value sourced from a file (handy for multi-line values or large keys):
snapctl secret create --application-id $application_id --file-name $file_name --tag $tag --from-file ./my-secret.txt

# Rotate by creating a new tag for the same file_name:
snapctl secret create --application-id $application_id --file-name my-api-key --tag prod-2026-06 --value $new_value
```

#### 5. secret delete
Delete a secret. Fails if the targeted secret/tag is referenced by a cluster manifest.

```bash
# Delete the entire secret (every tag):
snapctl secret delete --application-id $application_id --file-name $file_name

# Delete only one tag:
snapctl secret delete --application-id $application_id --file-name $file_name --tag $tag
```

#### 6. secret reveal
Reveal the plaintext value of a **specific tag** of a secret. `--tag` is required. Without `--out-path`, the plaintext is printed on stdout. With `--out-path` set to an existing directory, the plaintext is written to `<out-path>/<file_name>.<tag>` (chmod `0600` on POSIX) and is NOT echoed on stdout. **Never echo revealed secrets into logs or terminal output — prefer `--out-path`.**

```bash
# Write plaintext to ./secrets/$file_name.$tag and keep it off stdout
snapctl secret reveal --application-id $application_id --file-name $file_name --tag $tag --out-path $out_path
```

### 12. Release Notes
View the release notes for Snapctl.

#### 1. release-notes help
```bash
snapctl release-notes --help
```

#### 2. release-notes releases
List the available Snapctl releases.

```bash
snapctl release-notes releases
```

#### 3. release-notes show
Show the release notes for a Snapctl version. Defaults to your installed version.

```bash
# $version = (Optional) Version to show the release notes for. Defaults to the current version.
# $out_path = (Optional) Path to save the release notes. If not passed, the notes are printed on the console.
snapctl release-notes show
snapctl release-notes show --version $version --out-path $out_path
```

## Error codes
### CLI Return Codes
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 0          | Operation completed successfully                         |
| 1          | General error                                            |
| 2          | Input error                                              |
| 3          | Resource not found                                       |
| 4          | Internal server error                                    |
| 5          | Maintenance Mode                                         |

### Configuration Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 10         | Configuration incorrect                                  |
| 11         | Configuration error                                      |
| 12         | Dependency missing                                       |

### Snaps Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 13         | Snaps Generic error                                      |
| 14         | Snaps Enumerate error                                    |

### Snapend Manifest Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 16         | Snapend Manifest create error                            |
| 17         | Snapend Manifest update error                            |
| 18         | Snapend Manifest upgrade error                           |
| 19         | Snapend Manifest update error                            |

### BYOGS Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 3          | Resource not found: BYOGs resource not found             |
| 20         | Generic BYOGS error                                      |
| 21         | BYOGS dependency missing                                 |
| 22         | BYOGS ECR login error                                    |
| 23         | BYOGS build error                                        |
| 24         | BYOGS tag error                                          |
| 25         | BYOGS publish error                                      |
| 26         | BYOGS publish permission error                           |
| 27         | BYOGS publish duplicate tag error                        |

### BYOSNAP Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 3          | Resource not found: BYOSnap resource not found           |
| 30         | Generic BYOSNAP error                                    |
| 31         | BYOSNAP dependency missing                               |
| 32         | BYOSNAP ECR login error                                  |
| 33         | BYOSNAP build error                                      |
| 34         | BYOSNAP tag error                                        |
| 35         | BYOSNAP publish image error                              |
| 36         | BYOSNAP publish image permission error                   |
| 37         | BYOSNAP publish image duplicate tag error                |
| 38         | BYOSNAP create error                                     |
| 39         | BYOSNAP create permission error                          |
| 40         | BYOSNAP create duplicate name error                      |
| 41         | BYOSNAP publish version error                            |
| 42         | BYOSNAP publish version permission error                 |
| 43         | BYOSNAP publish version duplicate version error          |
| 44         | BYOSNAP publish version duplicate tag error              |
| 45         | BYOSNAP update version error                             |
| 46         | BYOSNAP update version service in use                    |
| 47         | BYOSNAP update version tag error                         |
| 48         | BYOSNAP update version invalid version error             |
| 49         | BYOSNAP publish error                                    |
| 86         | BYOSNAP generate-profile                                 |
| 87         | BYOSNAP swagger error                                    |


### Application Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 3          | Resource not found: Application resource not found       |
| 50         | Generic application error                                |
| 51         | Application create error                                 |
| 52         | Application create permission error                      |
| 53         | Application create limit error                           |
| 54         | Application create duplicate name error                  |
| 55         | Application enumerate error                              |

### Snapend Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 3          | Resource not found: Snapend resource not found           |
| 60         | Generic snapend error                                    |
| 61         | Snapend enumerate error                                  |
| 62         | Snapend clone error                                      |
| 63         | Snapend clone server error                               |
| 64         | Snapend clone timeout error                              |
| 65         | Snapend apply error                                      |
| 66         | Snapend apply server error                               |
| 67         | Snapend apply timeout error                              |
| 68         | Snapend promote error                                    |
| 69         | Snapend promote server error                             |
| 70         | Snapend promote timeout error                            |
| 71         | Snapend download error                                   |
| 72         | Snapend update error                                     |
| 73         | Snapend update server error                              |
| 74         | Snapend update timeout error                             |
| 75         | Snapend state error                                      |
| 76         | Snapend manifest mismatch error                          |
| 77         | Snapend create error                                     |
| 78         | Snapend create server error                              |
| 79         | Snapend create timeout error                             |

### Generate Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 80         | Generic generate error                                   |
| 81         | Generate credentials error                               |

### Snap Configuration Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 91         | Snap Configuration error                                 |
| 92         | Snap Configuration download error                        |

### BYOWS Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 95         | Generic byows error                                      |
| 96         | Byows attach error                                       |
| 97         | Byows reset error                                        |
| 98         | Byows detach error                                       |

### Secret Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 3          | Resource not found: Secret resource not found            |
| 4          | Internal server error: Secret encryption failure (backend api_error_code 584) |
| 100        | Generic secret error                                     |
| 101        | Secret enumerate error                                   |
| 102        | Secret get error                                         |
| 103        | Secret create error                                      |
| 104        | Secret create duplicate error — (file_name, tag) already exists (backend api_error_code 588) |
| 106        | Secret delete error                                      |
| 107        | Secret delete failed — secret is referenced by a cluster manifest (backend api_error_code 582) |
| 108        | Secret reveal error                                      |

### Login Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 110        | Login error                                              |
| 111        | Login flow error                                         |

### Admin SDK Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 113        | Generic Admin SDK error                                  |
| 114        | Admin SDK download error                                 |
