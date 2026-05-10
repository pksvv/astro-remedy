# Symphony + Codex CLI Runbook

This repo is prepared to be driven by Symphony with Codex CLI in app-server mode.

## What Symphony Does

Symphony watches an issue tracker, creates one isolated workspace per issue, and launches a Codex agent session inside that workspace. The repo-owned `WORKFLOW.md` controls tracker settings, workspace hooks, Codex runtime settings, and the prompt sent to each agent.

For ARIP, Symphony should be used for implementation tickets, research tickets, schema/design tasks, content-pipeline work, QA follow-ups, and small product iterations. Keep high-ambiguity product strategy decisions in human review before dispatching implementation work.

## Where The Work Lives

Symphony does its work inside per-issue clones under:

```text
~/code/symphony-workspaces/astro-remedy/<ISSUE-ID>
```

Example:

```text
~/code/symphony-workspaces/astro-remedy/DEV-6
```

That means a Symphony agent can create files that exist in the issue workspace even before those changes are merged or copied back into your main repo checkout.

Operator rule:

- Treat the issue workspace as the live scratch repo for that ticket.
- Treat your main repo checkout as the stable view.
- Before approving `Human Review`, confirm whether the reported files exist in the main repo or only in the issue workspace.
- If an agent mentions a file you cannot see in the main repo, check the corresponding issue workspace path first.

Useful commands:

```bash
tree ~/code/symphony-workspaces/astro-remedy/DEV-6 -L 3
git -C ~/code/symphony-workspaces/astro-remedy/DEV-6 status --short
git -C ~/code/symphony-workspaces/astro-remedy/DEV-6 log --oneline -5
```

The workflow should not rely on humans guessing this. Agents must say clearly in the handoff whether an artifact was landed in the main repo or exists only in the issue workspace.

## Repo-Owned Context

- `WORKFLOW.md`: concise Symphony/Codex runtime prompt and config.
- `astrology_remedy_platform_exhaustive_brd.md`: product requirements source of truth.
- `docs/mvp-architecture-and-definition.md`: concise MVP architecture, scope, routes, modules, data model, and guardrails for implementation tickets.
- `docs/agentic-delivery-model.md`: detailed Symphony delivery model, Linear ticket design, automation architecture, product guardrails, and technical roadmap.
- Linear issues: executable task queue for Symphony.

Future Codex agents should not rely on chat history. Put product decisions in the BRD, operating decisions in `WORKFLOW.md` or this runbook, and scoped execution details in Linear.

## Required Local Setup

1. Install and authenticate Codex CLI.
2. Install and authenticate the Linear CLI/API token path used by Symphony.
3. Clone the Symphony reference implementation:

```bash
git clone https://github.com/openai/symphony
cd symphony/elixir
```

4. Install the Symphony runtime dependencies from the Symphony repo instructions.
5. Export the environment variables expected by this repo workflow:

```bash
export LINEAR_API_KEY="..."
export SOURCE_REPO_URL="git@github.com:YOUR_ORG/astro-remedy.git"
```

If this repo is not yet hosted on GitHub, set `SOURCE_REPO_URL` after publishing it.

## Workflow Configuration

The local orchestration contract is:

```text
WORKFLOW.md
```

Customize these fields before running Symphony:

- `tracker.project_slug`: the Linear project slug for ARIP.
- `workspace.root`: where Symphony should create per-issue workspaces.
- `agent.max_concurrent_agents`: start low until tests, scripts, and guardrails are mature.
- `codex.command`: use `codex app-server`, or wrap it with config flags if your local Codex CLI requires a specific model or profile.

## Run Symphony

From the Symphony reference implementation:

```bash
mise exec -- ./bin/symphony /Users/admin/code/vipul/astro-remedy/WORKFLOW.md
```

To enable the optional dashboard:

```bash
mise exec -- ./bin/symphony /Users/admin/code/vipul/astro-remedy/WORKFLOW.md --port 4000
```

## Daily EOD Project Update

Every operating day, the always-on Mac mini/Symphony setup should produce a PM-readable end-of-day update for:

- the human owner
- `agent-product-manager`

Default schedule:

- Time: 21:30 Asia/Kolkata.
- Project: `astro-remedy`.
- Primary source: Linear project issues and states.
- Secondary source: latest Symphony/Codex handoffs and repo changes.

Recommended update format:

```markdown
# ARIP Daily Project Update - YYYY-MM-DD

## Executive Summary
- 3-5 bullets on meaningful progress, risk, and next move.

## Completed Today
- Issue ID: outcome, verification, links if available.

## In Progress
- Issue ID: current status, owner/agent, expected next action.

## Blocked / At Risk
- Issue ID: blocker, decision needed, recommended action.

## Product / UX / Technical Decisions
- Decisions made or proposed today.

## Verification Status
- Builds, tests, browser checks, or docs-only verification.

## Safety and Compliance Notes
- Astrology disclaimer, citation, privacy, copyright, or no-fear-language concerns.

## Tomorrow's Dispatch Recommendation
- Issues to move to `Todo`.
- Issues to keep in `Backlog`.

## Questions for Human / Agent Product Manager
- Short list of decisions needed.
```

Do not include secrets, raw birth data, private chart data, subscription data, or long transcript text.

Implementation options:

- Preferred: create a scheduled PM agent run that queries Linear daily and writes the update to the agreed channel/doc.
- Fallback: create a daily Linear issue/comment workflow for `agent-product-manager` to review.
- If Slack is used later, post the same update into the approved project channel.

## Recommended Linear States

Use these states for a simple ARIP loop:

- `Todo`: ready for Symphony to pick up.
- `In Progress`: agent-active work.
- `Rework`: agent should address review feedback.
- `Human Review`: agent is done and waiting for a person.
- `Merging`: optional state for PR landing.
- `Done`: complete.

The current `WORKFLOW.md` dispatches `Todo`, `In Progress`, and `Rework`, and treats `Done`, `Closed`, `Cancelled`, `Canceled`, and `Duplicate` as terminal.

Do not dispatch `Human Review` or `Merging` by default. Those states are intended for people or merge automation.

## Ticket Shape

Good Symphony tickets should include:

- User-facing outcome.
- Files or product area in scope.
- Acceptance criteria.
- Verification expectation.
- Any compliance or astrology-domain constraints.

Use `docs/agentic-delivery-model.md` for the full Symphony-ready Linear issue template and task decomposition guidance.

Example:

```text
Title: Define transcript ingestion schema for remedy extraction

Create a first-pass schema for transcript ingestion based on the BRD. Include video metadata, transcript chunks, astrological entities, extracted remedies, confidence, source attribution, and moderation status. Add validation examples and note copyright/attribution risks.

Acceptance criteria:
- Schema covers planets, houses, signs, dashas, problem categories, remedies, and citations.
- Includes human-review states.
- Includes at least 3 example records.
- Does not implement a database migration yet.
```

## Guardrails

- Do not dispatch large vague epics directly. Ask Codex to turn them into smaller issues first.
- Keep concurrency low until the repo has automated tests and a working implementation scaffold.
- Require human review for astrology interpretation, remedy safety language, subscription/payment changes, and user-data handling.
- Prefer research/design tickets before implementation when the stack is not yet chosen.
- Require source citations for transcript-derived remedy claims.
- Protect birth details, place data, saved chart data, and subscription metadata.
- Respect transcript copyright and attribution; avoid exposing long transcript passages unless rights are clear.
