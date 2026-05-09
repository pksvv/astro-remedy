---
tracker:
  kind: linear
  api_key: $LINEAR_API_KEY
  project_slug: astro-remedy
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
  interval_ms: 30000
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
  max_concurrent_agents: 3
  max_turns: 12
  max_retry_backoff_ms: 300000
  max_concurrent_agents_by_state:
    rework: 1
codex:
  command: codex app-server
  thread_sandbox: workspace-write
  turn_timeout_ms: 3600000
  read_timeout_ms: 5000
  stall_timeout_ms: 300000
---
# ARIP Symphony Workflow

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

The current repository source of truth is `astrology_remedy_platform_exhaustive_brd.md`. Treat that BRD as product context unless a ticket explicitly overrides it.

## Working Rules

- Keep changes scoped to the issue.
- Prefer implementation plans that can be reviewed incrementally.
- Preserve spiritual and astrology language while avoiding medical, legal, financial, or fear-based guarantees.
- Keep user data privacy central, especially birth details, location, subscription data, and saved charts.
- Use deterministic astrology computation for chart math; use AI for interpretation, extraction, retrieval, summarization, and drafting.
- Add tests or verification notes proportionate to the risk of the change.
- If a ticket is too ambiguous to implement safely, produce a short implementation plan and call out the missing decisions.
- If the work touches transcript ingestion, include copyright and attribution considerations.
- If the work touches remedies or interpretations, include human review, citation, and disclaimer requirements.

## Expected Handoff

Before finishing, provide:

- What changed.
- Files touched.
- How you verified it.
- Remaining risks or decisions.
- Any follow-up issues worth creating.

