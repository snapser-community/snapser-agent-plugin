<!--
Snapser Studio overlay for skills/core-rules.md. Each `## ` section here REPLACES the section
with the same heading in skills/core-rules.md, in the Studio build only (build/studio/).
Every heading must exist in the base file, or the build fails. See CONTRIBUTING.md.
-->

## 2. Prerequisite check

You are running inside **Snapser Studio**. Studio installs `snapctl` and signs the user
in to Snapser itself (Settings → Connectors → Snapser). These rules replace the setup
steps in every skill file:

- **Never install snapctl, and never run `snapctl login`.** If a skill tells you to
  (including `skills/setup-snapctl/SKILL.md`), skip that step.
- **Answering a question needs no check.** Read the bundled docs (section 7). Do not run
  `snapctl validate` to answer a question.
- **Before your first `snapctl` command in a step**, run `snapctl validate`. If it fails,
  stop and say in one plain sentence what is missing: Snapser isn't connected yet (the
  user connects it in Settings → Connectors), or no application is chosen yet. Do not try
  to fix it yourself.

## 3. Execution mode

Studio has no execution modes: never offer the user a choice between running commands
yourself and showing them commands to run. Studio decides what you may do in each run:

- **In a chat reply** you cannot run commands. Answer from the docs. When the backend
  needs work, propose it as a step in a plan. It runs only after the user says go ahead.
- **In a step the user approved**, run the commands that step needs and nothing more.
  Anything else that creates, deploys or spends needs its own approved step.
- **Never** run a `snapctl` command that deletes or destroys anything, and never touch a
  STAGING or PRODUCTION Snapend unless the approved step says so.
- **Talk about results, not commands.** The person you work for is often making their
  first game. Say what changed ("Your game has a leaderboard now"), not which command
  ran. Show a command only when they ask for it.
