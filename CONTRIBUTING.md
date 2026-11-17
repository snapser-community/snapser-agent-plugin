# Contributing to the Snapser Plugin

This guide is for people and agents that change this repository. It is not for plugin
users. Claude Code loads it in each session in this repository, through
`.claude/CLAUDE.md`.

## How each agent gets the content

| Agent | What it loads |
|---|---|
| Claude Code and Cowork (plugin install) | Only the skills in `skills/`. Each skill description is always in context. A skill body loads when the skill starts. |
| Codex, OpenCode, Cursor | `AGENTS.md`, then the skill files it points to. |

Claude Code does **not** load `AGENTS.md` or a `CLAUDE.md` from an installed plugin.
Two rules follow from this:

- A rule that all workflows share goes in `skills/core-rules.md`. Every `SKILL.md`
  points to that file. Do not put such a rule only in `source/CONTEXT.md`.
- Do not add a `CLAUDE.md` at the repository root. Plugin users never get it, and
  `claude plugin validate` gives a warning for it.

## Source files and generated files

Do not edit a generated file. Edit the source, then run `python3 scripts/build.py`.

| Generated file | Source |
|---|---|
| `AGENTS.md` | `source/CONTEXT.md` |
| `data/docs/INDEX.md` | The `.mdx` files in `data/docs/` |
| `data/releases/INDEX.md` | The `.mdx` files in `data/releases/` |
| The docs-version line in `README.md` | The newest file in `data/releases/` |

To add a documentation page or a release note, put the `.mdx` file in its folder and
run the build.

## The Snapser Studio build

Snapser Studio ships this plugin inside the app and loads it into every agent it runs.
Studio installs snapctl and signs the user in itself, and it decides in each run whether
the agent may run commands. So two parts of the shared rules read differently there: the
prerequisite check and the execution mode choice.

The build writes a second copy of the plugin to `build/studio/` (gitignored). It is the
same plugin, except that each `## ` section in an overlay file replaces the section with
the same heading in its base file:

| Overlay | Base | Becomes |
|---|---|---|
| `source/studio/skills/core-rules.md` | `skills/core-rules.md` | `build/studio/skills/core-rules.md` |
| `source/studio/CONTEXT.md` | `source/CONTEXT.md` | `build/studio/AGENTS.md` |

Rules:

- Change a shared rule in the base file. Both builds get it.
- Put only Studio's differences in an overlay, as whole `## ` sections.
- If you rename or remove a section that an overlay replaces, the build fails. Update the
  overlay heading in the same change.
- The Studio build must not mention Agent Mode or Guide Mode. The build fails if it does.
- `build/studio/BUILD.json` records the plugin version and the commit it was built from.
  Snapser Studio vendors from `build/studio/`, never from the repository root.

## Rules for skill files

- Each skill is `skills/<name>/SKILL.md` with `name` and `description` frontmatter.
- Each skill starts with the preamble that points to
  `${CLAUDE_PLUGIN_ROOT}/skills/core-rules.md`. Copy the preamble from an existing skill.
  The build fails if a skill does not have it.
- Write each `skills/...` and `data/...` path from the plugin root. The build checks
  that each path exists.
- Compare each `snapctl` command with `skills/snapctl_commands.md` before you add it.
- Do not put customer names, internal hostnames, or notes for other teams in a skill.
  This repository is public.

## Before you open a pull request

```bash
python3 scripts/build.py      # regenerate, then check links and skill preambles
claude plugin validate .      # check the plugin and marketplace manifests
```

Then test the changed skill in a real session. Start Claude Code in an empty folder
with the local plugin:

```bash
claude --plugin-dir /path/to/snapser-agent-plugin
```

Give it a prompt that a user would write, and confirm that the correct skill starts.
After you edit a file, run `/reload-plugins` in that session to load the change.

## Release

Agents cache the plugin for each version. Users do not get a change until the version
changes.

```bash
python3 scripts/bump-version.py           # patch
python3 scripts/bump-version.py minor     # or: major, or an explicit X.Y.Z
python3 scripts/bump-version.py --dry     # show the change, write nothing
```

The script keeps `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`, and
`gemini-extension.json` on the same version. Then do the next step that the script prints.
