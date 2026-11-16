<!--
Snapser Studio overlay for source/CONTEXT.md. Each `## ` section here REPLACES the section
with the same heading, and the result is build/studio/AGENTS.md. Every heading must exist
in source/CONTEXT.md, or the build fails. See CONTRIBUTING.md.
-->

## First: Read the Core Rules

You are running inside **Snapser Studio**, helping someone make a game. Before you run any
`snapctl` command, read `skills/core-rules.md`. It is the one canonical copy of the rules
every workflow shares:

- who runs commands in Studio, and when — Studio installs snapctl and signs the user in;
  never do either yourself
- the HARD RULE that keeps structure (manifest) and settings (Admin SDK) in separate phases
- the command rules — `--blocking`, `--application-id`, output path flags, input validation
- error handling

To answer a Snapser question you need no check at all: read the bundled docs (see
**Answering Questions** below).

All `skills/` and `data/` paths in this file and in the skill files start at the plugin
root — the folder that contains the `skills/` and `data/` directories.

---
