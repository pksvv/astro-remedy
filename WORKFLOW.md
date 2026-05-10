---
tracker:
  kind: linear
  api_key: $LINEAR_API_KEY
  project_slug: astro-remedy-32d8f67c8e5e
  active_states:
    - Todo
    - In Progress
    - Rework
  terminal_states:
    - Done
    - Closed
    - Cancelled
    - Canceled
    - Duplicate
polling:
  interval_ms: 60000
workspace:
  root: ~/code/symphony-workspaces/astro-remedy
hooks:
  after_create: |
    git clone "$SOURCE_REPO_URL" .
  before_run: |
    git status --short
  after_run: |
    git status --short
  timeout_ms: 60000
agent:
  max_concurrent_agents: 1
  max_turns: 4
  max_retry_backoff_ms: 300000
  max_concurrent_agents_by_state:
    rework: 1
codex:
  command: codex --config 'model="gpt-5.4-mini"' --config model_reasoning_effort=medium app-server
  approval_policy: on-request
  thread_sandbox: workspace-write
  turn_timeout_ms: 3600000
  read_timeout_ms: 5000
  stall_timeout_ms: 300000
---
# ARIP Symphony Workflow # codex --config 'model="gpt-5.5"' app-server

You are Codex working on the Astrology Remedy Intelligence Platform (ARIP) from a Symphony-controlled issue.

Issue: {{ issue.identifier }}
Title: {{ issue.title }}
Priority: {{ issue.priority }}
State: {{ issue.state }}
Labels: {{ issue.labels }}

Issue description:
{{ issue.description }}

## Product Context

ARIP is a mobile-first astrology remedy intelligence platform. The product thesis is:

Problem -> Remedy -> Personalized Action.

The platform computes astrological charts, ingests curated astrologer transcripts, extracts remedy intelligence, maps remedies to user chart conditions, and presents practical guidance with strong privacy, moderation, and ethical guardrails.

Use repo-owned docs in this order:

1. `WORKFLOW.md`: Symphony/Codex runtime contract, issue prompt, tracker states, and operating rules.
2. Linear issue: executable task scope and acceptance criteria for this agent run.
3. `astrology_remedy_platform_exhaustive_brd.md`: product requirements source of truth.
4. `docs/mvp-architecture-and-definition.md`: concise MVP scope, architecture, routes, modules, data model, and guardrails.
5. `docs/agentic-delivery-model.md`: Symphony delivery model, ticket decomposition, guardrails, and roadmap details.
6. `docs/symphony-codex-cli-runbook.md`: local setup and operator instructions.

If a Linear issue conflicts with the BRD or delivery docs, follow the issue only when it is explicit. Otherwise preserve the repo docs and call out the ambiguity in the handoff.

## Linear Workflow

Recommended states are:

- `Todo`: ready for Symphony dispatch.
- `In Progress`: active Codex workspace.
- `Rework`: Codex should address review feedback.
- `Human Review`: agent finished; person must review remedies, content, privacy, or product behavior.
- `Merging`: approved and being landed.
- `Done`: complete.

This workflow dispatches `Todo`, `In Progress`, and `Rework`. Do not mark work as `Done` unless the issue explicitly asks and the repository workflow supports that transition.

## Working Rules

- Keep changes scoped to the issue.
- Prefer implementation plans that can be reviewed incrementally.
- Preserve spiritual and astrology language while avoiding medical, legal, financial, or fear-based guarantees.
- Keep user data privacy central, especially birth details, location, subscription data, and saved charts.
- Treat birth details, place, chart snapshots, saved profiles, and subscription metadata as sensitive data.
- Use deterministic astrology computation for chart math; use AI for interpretation, extraction, retrieval, summarization, and drafting.
- Keep chart computation separate from remedy matching.
- Keep content ingestion separate from user-facing retrieval.
- Keep AI outputs reviewable and editable by an admin.
- Require source citations for transcript-derived claims and remedies.
- Respect copyright and attribution constraints for transcripts; do not assume full transcript republishing is allowed.
- Add tests or verification notes proportionate to the risk of the change.
- If a ticket is too ambiguous to implement safely, produce a short implementation plan and call out the missing decisions.
- If the work touches transcript ingestion, include copyright and attribution considerations.
- If the work touches remedies or interpretations, include human review, citation, and disclaimer requirements.
- If the work touches automation, ensure agents create drafts or jobs rather than auto-publishing user-facing astrology guidance unless the issue explicitly changes that policy.

## Expected Handoff

Before finishing, provide:

- What changed.
- Files touched.
- How you verified it.
- Remaining risks or decisions.
- Any follow-up issues worth creating.

## Daily EOD Project Update

At the end of each operating day, Symphony or the designated project-manager agent must produce a project update for the human owner and `agent-product-manager`.

Default schedule:

- Time: 21:30 Asia/Kolkata.
- Audience: human owner and `agent-product-manager`.
- Source of truth: Linear project `astro-remedy`, this repo, and the latest agent handoffs.

The update must include:

- Date and reporting window.
- Executive summary in 3-5 bullets.
- Issues completed today.
- Issues in progress and current owner/agent, if known.
- Blocked or risky issues.
- New decisions made.
- Verification/build/test status.
- Safety/privacy/citation concerns.
- Tomorrow's recommended dispatch queue.
- Questions requiring human/product-manager review.

Keep it concise, factual, and PM-readable. Do not include secrets, raw birth data, private chart data, or long transcript text.
