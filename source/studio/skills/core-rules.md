<!--
Snapser Studio overlay for skills/core-rules.md. Each `## ` section here REPLACES the section
with the same heading in skills/core-rules.md, in the Studio build only (build/studio/).
Every heading must exist in the base file, or the build fails. See CONTRIBUTING.md.
-->

## 2. Prerequisite check

You are running inside **Snapser Studio**. Studio installs `snapctl` for the user and
usually signs them in already (Settings → Connectors → Snapser). These rules replace the
setup steps in every skill file:

- **Don't install snapctl yourself** — Studio does that. If it's missing, say in one plain
  sentence that the user can set up Snapser in Settings → Connectors, and stop.
- **Answering a question needs no check.** Read the bundled docs (section 7). Do not run
  `snapctl validate` to answer a question.
- **Before your first `snapctl` command in a step**, run `snapctl validate`. If the key is
  missing or expired, run `snapctl login`: it opens the browser and the user clicks
  **Activate**. Tell them in one plain sentence to look for the browser window. If no
  application is set up yet, create one or pick one, as the skills describe.

## 3. Execution mode

Studio has no execution modes: never offer the user a choice between running commands
yourself and showing them commands to run. Studio decides what you may do in each run:

- **In a chat reply** you cannot run commands. Answer from the docs. When the backend
  needs work, propose it as a step in a plan. It runs only after the user says go ahead.
- **In a step the user approved**, run the commands that step needs and nothing more.
  Anything else that creates, deploys or spends needs its own approved step.
- **Never delete a Snapend.** Any other `snapctl` command the step needs is fine. Don't
  touch a STAGING or PRODUCTION Snapend unless the approved step says so.
- **Talk about results, not commands.** The person you work for is often making their
  first game. Say what changed ("Your game has a leaderboard now"), not which command
  ran. Show a command only when they ask for it.
