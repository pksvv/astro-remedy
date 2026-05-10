# Agentic Delivery Model for Symphony + Codex CLI

## Purpose

This document defines how ARIP should be built by automated Codex agents coordinated by OpenAI Symphony. It is the durable delivery plan for future agents that will not have prior chat context.

`WORKFLOW.md` is the concise runtime contract that Symphony reads. This file is the detailed operating model behind that contract.

## Source of Truth Hierarchy

1. `WORKFLOW.md`
   - Symphony tracker config, eligible states, workspace setup, Codex runtime command, and per-issue operating prompt.
   - Keep it concise and operational.
2. `astrology_remedy_platform_exhaustive_brd.md`
   - Product requirements, domain vision, MVP scope, user/admin features, ethics, and roadmap.
   - Treat it as product source of truth unless a Linear ticket explicitly overrides it.
3. `docs/mvp-architecture-and-definition.md`
   - Concise MVP definition, architecture, module boundaries, routes, data concepts, and safety defaults.
   - Treat it as the implementation north star for scoped Codex tickets.
4. Linear tickets
   - Executable task queue for Symphony.
   - Each ticket should be small enough for one isolated Codex workspace.
5. Supporting docs under `docs/`
   - Engineering runbooks, architecture decisions, implementation notes, QA checklists, and future-agent guidance.

## Symphony Orchestration Model

Symphony should watch Linear, create one isolated workspace per eligible issue, and run `codex app-server` in that workspace. Codex agents should implement, verify, and hand off one ticket at a time.

Recommended flow:

1. Human or planning agent creates Linear issues from the BRD roadmap.
2. Symphony picks up issues in eligible states.
3. Symphony creates an isolated workspace for the issue.
4. Symphony launches Codex with the repo `WORKFLOW.md` prompt.
5. Codex reads the ticket, checks relevant repo docs, implements scoped changes, runs verification, and reports a handoff.
6. Ticket moves to `Human Review`.
7. Human review either approves for `Merging`, sends to `Rework`, or creates follow-up tickets.
8. At end of day, Symphony or a designated project-manager agent produces the daily project update for the human owner and `agent-product-manager`.

Codex should not rely on previous chat memory. Every ticket must contain enough context or point to a repo doc section.

## Daily Project Update Contract

The project must produce one PM-readable update every operating day.

Default schedule:

- 21:30 Asia/Kolkata.
- Project: `astro-remedy`.
- Audience: human owner and `agent-product-manager`.

Inputs:

- Linear issue states, due dates, blockers, and recent changes.
- Symphony/Codex handoffs.
- Repo changes and verification results when available.
- Human review decisions.

Required sections:

- Executive summary.
- Completed today.
- In progress.
- Blocked or at risk.
- Decisions made.
- Verification/build/test status.
- Safety/privacy/citation concerns.
- Tomorrow's recommended dispatch queue.
- Questions for human or `agent-product-manager`.

Rules:

- Keep it short and operational.
- Prefer issue IDs and concrete next actions.
- Do not include secrets, raw birth details, private chart data, subscription data, or long transcript text.
- Clearly separate MVP work from post-MVP work.

## Recommended Linear States

- `Todo`: scoped, ready for Symphony to dispatch.
- `In Progress`: active Codex workspace or agent run.
- `Rework`: reviewed but needs targeted fixes.
- `Human Review`: agent completed work; person must review before merge or publication.
- `Merging`: approved and being landed.
- `Done`: merged, verified, and complete.

Dispatch states should be `Todo`, `In Progress`, and `Rework`. `Human Review`, `Merging`, and `Done` should not start new implementation runs unless deliberately configured later.

## Task Decomposition for Symphony

### Research/Design Tickets

Use these when the implementation decision is not obvious.

Good examples:

- Choose MVP astrology computation strategy and replacement interface for Swiss Ephemeris.
- Design transcript/remedy schema with citations and review states.
- Define matching engine scoring rules for the first five problem categories.

Expected output:

- A concise design doc or ADR.
- Explicit implementation recommendations.
- Risks, tradeoffs, and follow-up implementation tickets.

### Implementation Tickets

Use these for scoped code changes with clear acceptance criteria.

Good examples:

- Scaffold Next.js App Router foundation with Tailwind.
- Implement transcript ingestion form and draft remedy creation.
- Implement placeholder chart service behind a replaceable interface.

Expected output:

- Code changes.
- Tests or verification notes.
- Handoff listing changed files, verification, and remaining risks.

### QA/Test Tickets

Use these to validate already-built functionality.

Good examples:

- Add tests for remedy matcher scoring and category fallback.
- Verify mobile birth-details form states and validation.
- Run build and document deployment blockers.

Expected output:

- Automated tests where feasible.
- Manual QA notes where UI verification is required.
- Bug tickets for failures outside the QA ticket scope.

### Review-Feedback Tickets

Use these when a reviewer asks for specific changes after an agent run.

Good examples:

- Add missing transcript source citation to remedy result cards.
- Tighten disclaimer language on result pages.
- Fix Prisma migration naming and seed data.

Expected output:

- Targeted fixes only.
- Short explanation of how review feedback was addressed.

### Follow-Up/Refactor Tickets

Use these after the MVP path is working and a small cleanup is clearly valuable.

Good examples:

- Extract shared form controls after two forms exist.
- Add typed job payload helpers for automation jobs.
- Replace placeholder location handling with geocoding interface.

Expected output:

- Low-risk cleanup.
- No unrelated feature expansion.

## Symphony-Ready Linear Issue Template

```markdown
## Goal

State the user/admin/system outcome in one paragraph.

## Context

Reference relevant repo docs and product constraints. Include enough detail for a Codex agent with no chat memory.

Relevant docs:
- `astrology_remedy_platform_exhaustive_brd.md`
- `docs/mvp-architecture-and-definition.md`
- `docs/agentic-delivery-model.md`
- Add any specific ADR/runbook path here.

## Scope

In scope:
- Bullet the exact behavior or files/modules expected.

Out of scope:
- Bullet adjacent work the agent must not do.

## Acceptance Criteria

- Concrete, testable criterion.
- Concrete, testable criterion.
- Include mobile/responsive, privacy, citation, or disclaimer requirements where relevant.

## Technical Notes

- Preferred stack, interfaces, APIs, schema names, or service boundaries.
- Mention whether AI calls should be real, mocked, or abstracted.
- Mention whether data should be persisted, seeded, or local-only.

## Verification

- Commands to run, such as `npm run build`, `npm test`, or specific manual UI checks.
- Expected result for each command/check.

## Guardrails

- Human review required for remedy/interpretation output.
- No medical/legal/financial guarantees.
- Source citations required for transcript-derived claims.
- Protect birth details, location, chart snapshots, and saved profile data.
- Respect transcript copyright and attribution.
```

## Product Guardrails for Codex Agents

- Remedies and interpretations must be human-reviewable before publication.
- Do not generate medical, legal, or financial guarantees.
- Do not use fear-based copy, coercive urgency, or claims that imply inevitable harm.
- Always include spiritual/entertainment/self-reflection disclaimers on user-facing guidance.
- Transcript-derived claims must cite the source transcript/video and preserve enough reference metadata for audit.
- Do not republish long transcript passages unless rights are clear; store transcript text for internal processing and expose short cited snippets only.
- Birth data, place data, chart snapshots, saved profiles, subscription data, and emails are sensitive.
- Avoid logging raw birth details or full chart payloads unless a ticket explicitly adds secure audit storage.
- AI may assist extraction, summarization, tagging, and drafting, but business logic should remain inspectable in code.
- Keep chart computation separate from remedy matching.
- Keep content ingestion separate from user-facing retrieval.

## Automated System Architecture

The product should become self-operating through scheduled jobs, queued workflows, and review gates.

MVP automation runtime:

- Vercel Cron or a simple scheduled endpoint triggers job processing.
- Postgres stores durable jobs, statuses, inputs, outputs, retry count, errors, and review state.
- Next.js route handlers execute job batches.
- Typed service modules implement agent actions.
- Admin UI reviews generated drafts and failed jobs.

Initial job types:

- `SLACK_VIDEO_INTAKE`: parse approved Slack channel messages for video IDs/URLs and create deduped video intake items.
- `TRANSCRIPT_PROCESSING`: normalize transcript text and chunk it.
- `REMEDY_EXTRACTION`: create draft remedy snippets with source references.
- `BLOG_DRAFT`: create draft SEO content from approved remedies.
- `SOCIAL_DRAFT`: create channel-specific social drafts from approved remedies and blog content.
- `ANALYTICS_SUMMARY`: summarize usage and content performance.
- `REVIEW_REMINDER`: surface stale drafts or failed jobs for human action.

Automation policy:

- Agents may create drafts, tags, citations, summaries, and review tasks.
- Agents should not auto-publish remedies or interpretation pages by default.
- Slack intake may create video intake records and transcript jobs, but must not publish remedies without review.
- Agents may auto-publish only low-risk operational artifacts if a future ticket explicitly changes the policy.
- All generated user-facing astrology guidance must remain editable and traceable.

Future runtime options:

- Inngest, Trigger.dev, Vercel Workflow, BullMQ + Redis, or Temporal can replace the simple job runner later.
- Keep job payloads typed and runtime-agnostic so orchestration can migrate without rewriting domain services.

## Technical Roadmap Details Codex Agents Need

### Preferred Stack

- Next.js App Router.
- TypeScript.
- Tailwind CSS.
- PostgreSQL/Supabase.
- Prisma for schema and migrations unless a ticket chooses another data layer.
- OpenAI/LLM integrations behind service interfaces.
- Python/FastAPI only if needed for real astrology computation.

### Core Service Boundaries

- `services/astrology`: chart computation interface and implementations.
- `services/transcripts`: transcript ingestion, normalization, chunking.
- `services/remedies`: remedy extraction, review workflow, publication.
- `services/matching`: deterministic remedy matching and scoring.
- `services/ai`: provider adapters and prompt wrappers.
- `services/jobs`: post-MVP durable job queue and runner.
- `services/agents`: post-MVP typed agent actions that create drafts or jobs.
- `services/analytics`: post-MVP event capture and summaries.
- `services/slack-intake`: post-MVP approved Slack channel parsing, video ID extraction, dedupe, and intake job creation.
- `services/content-marketing`: post-MVP SEO/blog/social draft generation from approved remedies and citations.

### MVP Data Concepts

- Transcript source: video/article metadata, source URL, astrologer/source name, rights/attribution notes.
- Transcript chunk: text segment, order, optional timestamp, source reference.
- Remedy snippet: problem category, remedy text, condition tags, source chunk reference, confidence, review status.
- User request: birth details input, selected problem category, consent/disclaimer acknowledgement.
- Chart snapshot: computed or placeholder chart output, engine version, metadata.
- Match result: selected remedies, explanation, confidence score, citations, disclaimer.
- Blog post: slug, title, body, status, source remedy links, SEO metadata.
- Job: post-MVP type, status, payload, output, error, retry count, scheduled/completed timestamps.
- Analytics event: post-MVP event name, timestamp, anonymous/session/user reference, minimal payload.
- Video intake item: post-MVP Slack message metadata, video ID/URL, dedupe key, status, transcript job reference.
- Marketing draft: post-MVP target channel, format, source citations, draft body, review status.

### MVP Implementation Order

1. Project foundation and architecture.
2. Database schema and content model.
3. Admin transcript/remedy ingestion.
4. User birth details and remedy finder flow.
5. Remedy matching engine.
6. Blog/SEO pages.
7. Deployment readiness.
8. MVP end-to-end QA and safety guardrails.

### Post-MVP Implementation Order

1. Basic analytics and logging.
2. Automation engine and background workflows.
3. Slack video intake automation.
4. SEO/blog/social draft automation.
5. Future agent expansion hooks.
6. Short-form video generation pipeline.

### Acceptance Defaults

- Mobile-first pages must be usable on narrow screens.
- Empty states must be graceful.
- Tests should cover deterministic services and risky route handlers.
- AI integrations should support mock/fallback behavior for local development.
- Any placeholder astrology computation must clearly expose engine metadata and be replaceable.
- Every user-facing result must show a disclaimer and source references when based on transcript knowledge.
