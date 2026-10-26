---
name: create-application
description: Create a new Snapser application space
---

# Skill: Create an application space on Snapser

Creates an application space on Snapser. All backends belong to an application space.

## Trigger Phrases
- "create an application"
- "create a game"

## Requirement
- This skill only needs the Snapser CLI tool

## Full Workflow

### Setup
1. Check if the user has the Snapser CLI tool installed
```bash
snapctl -h
```
2. If not, point the user to PyPy Snapser to download and install the latest snapctl
3. Then confirm if the user has a valid Snapctl setup by running the validate command
```bash
snapctl validate
```

### Phase 1 — Get the application name
Ask the user:
- What is the name of the application.
- The name should be 20 characters long and without any special characters

### Phase 2 — Create the application
1. Run the `snapctl application create --name $app_name` command to create the application.
2. Note the application Id returned.

### Phase 3 — Note the application ID
3. Save the application ID for use with `--application-id` in subsequent snapctl commands. The user can also add it to their `~/.snapser/config` file under the `SNAPSER_APPLICATION_ID` key for convenience.
