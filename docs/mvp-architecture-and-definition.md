# ARIP MVP Architecture and Definition

## Purpose

This document is the concise implementation north star for Codex agents working through Symphony. The BRD explains the full product vision; this document defines what the MVP is, what it is not, and the architecture agents should implement first.

## MVP Definition

The MVP is a mobile-first web application that proves this loop:

1. Admin manually adds curated astrologer transcript content.
2. System creates reviewable draft remedy snippets from that content.
3. Admin reviews, edits, and publishes remedy snippets.
4. User enters birth details and chooses a problem category.
5. System creates a basic chart snapshot through a replaceable astrology service.
6. System matches the request to published remedy snippets.
7. User sees spiritual/self-reflection guidance with source citations, confidence, and disclaimers.
8. Background jobs prepare the platform for automated ingestion, extraction, drafting, analytics, and review queues.

## MVP Problem Categories

Initial categories:

- `ENEMIES_WORKPLACE_POLITICS`
- `CAREER`
- `DEBT`
- `HEALTH`
- `MARRIAGE_RELATIONSHIP`

Labels shown to users should be gentle and non-fear-based, for example “workplace conflict” instead of aggressive language.

## MVP In Scope

- Next.js App Router web app.
- TypeScript and Tailwind CSS.
- PostgreSQL/Supabase-compatible Prisma schema.
- Manual admin transcript ingestion.
- Deterministic baseline remedy extraction from pasted transcripts.
- Admin review/edit/publish workflow.
- Birth details form with date, time, place, and selected problem category.
- Placeholder D1-style chart snapshot behind a replaceable service interface.
- Deterministic remedy matching by problem category, tags, source confidence, and chart metadata.
- Results page with explanation, remedies, citations, confidence, and disclaimer.
- Basic blog and category pages for SEO.
- Basic analytics events.
- Postgres-backed jobs and a simple cron/process route for automation readiness.
- Typed future-agent interfaces that create drafts/jobs only.

## MVP Out of Scope

- Real Swiss Ephemeris or pyswisseph production integration.
- Automated YouTube crawling.
- Autonomous social posting.
- Auto-publishing remedies or personalized interpretations.
- Payments and subscriptions.
- User accounts and saved profiles.
- Advanced D9/D10/D60 charts.
- Full dasha/transit computation.
- Vector database or knowledge graph.
- Native app/PWA polish.

## Architecture Principles

- Keep chart computation separate from remedy matching.
- Keep content ingestion separate from user-facing retrieval.
- Keep AI outputs reviewable and editable by admins.
- Prefer deterministic logic for extraction, matching, safety checks, routing, validation, and scoring.
- Use AI only for high-value drafting/extraction/summarization, behind service interfaces.
- Do not bury business logic inside prompts.
- Store enough source metadata to audit transcript-derived claims.
- Treat birth details, place data, chart snapshots, saved profiles, emails, and subscription metadata as sensitive.
- Keep the first implementation deployable on Vercel and Supabase.

## Target Stack

- Frontend/backend: Next.js App Router.
- Language: TypeScript.
- Styling: Tailwind CSS.
- Database: PostgreSQL via Supabase or local Postgres.
- ORM: Prisma.
- AI: OpenAI through `services/ai` adapters, optional for MVP.
- Automation: Postgres-backed jobs plus scheduled route first; upgrade later to Inngest, Trigger.dev, Vercel Workflow, BullMQ, or Temporal.
- Astrology compute: TypeScript placeholder engine first; future Python/FastAPI or native service for Swiss Ephemeris if needed.

## Proposed Module Boundaries

- `app/`: App Router pages, route handlers, layouts.
- `components/`: reusable UI components.
- `lib/`: config, constants, validation helpers, disclaimers, logger.
- `types/`: shared domain and API types.
- `services/astrology/`: chart service interface and implementations.
- `services/transcripts/`: transcript ingestion, normalization, chunking.
- `services/remedies/`: remedy extraction, review workflow, publication.
- `services/matching/`: deterministic matching and scoring.
- `services/ai/`: model provider adapters and prompt wrappers.
- `services/jobs/`: durable job queue and runner.
- `services/agents/`: future agent actions that create drafts/jobs.
- `services/analytics/`: event capture and summaries.
- `prisma/`: schema, migrations, and seed data.
- `content/`: static starter content if used before DB-backed content is ready.
- `docs/`: architecture notes, ADRs, runbooks, QA notes.

## Core Data Model

Minimum concepts:

- Transcript source: title, source URL, source/astrologer name, rights/attribution notes.
- Transcript chunk: text segment, order, optional timestamp, source reference.
- Remedy snippet: problem category, remedy text, condition tags, source reference, confidence, review status.
- User remedy request: birth input, selected problem category, disclaimer acknowledgement.
- Chart snapshot: engine name/version, input metadata, placeholder or computed chart data.
- Match result: selected remedies, explanation, confidence, source citations, disclaimer.
- Blog post: title, slug, body, status, SEO metadata, related category/remedy links.
- Job: type, status, payload, output, error, retry count, schedule/completion timestamps.
- Analytics event: event name, timestamp, anonymous/session/user reference, minimal non-sensitive payload.

## Public Routes

- `/`: homepage with direct CTA to remedy finder.
- `/remedy-finder`: birth details and problem category form.
- `/remedy-finder/results/[id]`: personalized result page.
- `/blog`: blog index.
- `/blog/[slug]`: blog detail.
- `/remedies/[category]`: SEO category landing page.

## Admin Routes

- `/admin`: internal admin dashboard.
- `/admin/transcripts/new`: paste transcript and metadata.
- `/admin/transcripts/[id]`: transcript detail and draft snippets.
- `/admin/remedies/[id]/edit`: review/edit/publish remedy.
- `/admin/automation`: background job queue and failures.
- `/admin/automation/jobs/[id]`: job details and retry path.

Authentication is out of MVP unless explicitly ticketed. Until auth exists, admin routes are internal/local-only and must not be treated as production-safe.

## API and Service Behavior

- Admin transcript APIs save source metadata and queue or run deterministic extraction.
- Remedy APIs must never publish AI/draft output without an explicit reviewed/published status.
- Remedy finder APIs validate user input and persist only the minimum needed data.
- Matching APIs load a request, create or fetch a chart snapshot, fetch published remedies, score them, and persist a match result.
- Cron/job APIs process small batches, record failures, and avoid leaking sensitive payloads in logs.

## Matching MVP Rules

First implementation should be simple and inspectable:

- Filter to published remedies.
- Prefer selected problem category.
- Boost remedies whose condition tags match chart snapshot tags.
- Use stored source confidence as one scoring input.
- Return a small ranked set with confidence and citations.
- Fall back to general category remedies if chart-specific conditions are unavailable.

No prompt-only matching logic is allowed for MVP.

## Astrology MVP Rules

The first chart service may be a deterministic placeholder if real calculation is not feasible in the first slice.

Requirements:

- Accept date, time, place text, and timezone metadata.
- Return a normalized chart snapshot object.
- Include `engineName`, `engineVersion`, and `isPlaceholder`.
- Clearly mark placeholder output in UI and data.
- Keep interface compatible with future Swiss Ephemeris/FastAPI implementation.

## Automation MVP Rules

Initial automation should support:

- Transcript processing jobs.
- Remedy extraction jobs.
- Blog draft jobs.
- Analytics summary jobs.
- Review reminder jobs.

Agents and jobs create drafts, summaries, tags, citations, and review tasks. They do not auto-publish remedies or personalized interpretations.

## Safety and Compliance Defaults

- Astrology guidance is spiritual, entertainment, and self-reflection support.
- No medical, legal, or financial guarantees.
- No fear-based language.
- Health, debt, legal, and relationship categories must avoid definitive claims.
- Transcript-derived remedies require source references.
- Do not publicly expose long transcript passages unless rights are clear.
- Protect birth details and chart data from logs and analytics payloads.

## Initial Symphony Execution Order

1. Configure Linear workflow states for Symphony.
2. Research MVP astrology computation strategy.
3. Scaffold Next.js App Router foundation.
4. Define database schema and content model.
5. Build admin transcript and remedy ingestion MVP.
6. Build user birth details and remedy finder flow.
7. Implement remedy matching engine MVP.
8. Add blog and SEO content pages.
9. Add basic analytics and logging.
10. Build automation engine and background job workflow.
11. Prepare deployment readiness for Vercel and Supabase.
12. Add future agent hooks and documentation.
13. QA MVP end-to-end flow and safety guardrails.
