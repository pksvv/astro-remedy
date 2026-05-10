# ARIP MVP Architecture and Definition

## Purpose

This document is the concise implementation north star for Codex agents working through Symphony. The BRD explains the full product vision; this document defines what the MVP is, what it is not, and the architecture agents should implement first.

## MVP Definition

The MVP is a mobile-first web application that proves only this loop:

1. Transcript ingestion.
2. Basic chart computation.
3. Remedy matching.
4. Simple results page.
5. Basic SEO blog pages.

Do not build everything in the first MVP. Complex agents, auto-posting, advanced video generation, D60-level astrology, mobile apps, and community features are explicitly post-MVP.

## High-Level Product Flow

This is the long-term product machine:

```text
YouTube Videos
  -> Transcript Extraction
  -> Transcript Intelligence Pipeline
  -> Knowledge Graph / Remedy DB
  -> User Birth Details + Problem Input
  -> Astrology Computation Engine
  -> Remedy Matching Engine
  -> Personalized Remedy Output
  -> SEO + Social + Video Content Generation
  -> Traffic
  -> New Users
  -> More Data + More Engagement
```

The business loop is:

1. Curated astrologer videos become structured remedy knowledge.
2. Structured remedy knowledge powers personalized user results.
3. Approved remedy knowledge also powers SEO/blog/social distribution.
4. Analytics identifies which topics and categories deserve more ingestion.
5. Operators or agents feed more videos into Slack/manual intake.

The system should therefore be designed as a content-to-remedy-to-distribution flywheel, not only as a one-off remedy finder. The MVP only implements the smallest useful slice of that flywheel.

## Knowledge Ingestion Flow

```text
YouTube URL added
  -> Transcript fetched
  -> Transcript cleaned
  -> Transcript chunked
  -> Astrology entities extracted
  -> Remedies extracted
  -> Tagged + stored in DB
  -> Knowledge graph updated
```

MVP implementation: manual transcript paste plus deterministic extraction into a remedy DB. Automated YouTube fetching, Slack intake, and knowledge graph updates are post-MVP unless explicitly pulled forward.

## Astrology Computation Flow

```text
Birth details entered
  -> Timezone/location resolved
  -> Planetary positions calculated
  -> Ascendant calculated
  -> Houses calculated
  -> D1/D9/etc generated
  -> Dashas calculated
  -> Structured chart JSON created
```

MVP implementation: basic chart computation or placeholder chart JSON behind a replaceable service interface. Real timezone/location resolution, planetary positions, D9, dashas, and advanced divisional charts are post-MVP.

## Core Computation Stack

Recommended long-term computation stack:

- Python microservice.
- `pyswisseph`.
- Swiss Ephemeris.
- PyJHora references.

MVP default: TypeScript chart service interface with a clearly marked placeholder/basic implementation unless the astrology research ticket proves a real computation library is feasible immediately.

## Remedy Matching Flow

```text
Chart JSON
  + Problem category
  + Knowledge DB
  -> Matching engine
  -> Personalized remedies
```

MVP implementation: deterministic matching from selected problem category, published remedies, source confidence, and basic chart tags.

## User Delivery Flow

```text
Landing page
  -> User enters birth details
  -> Selects issue
  -> System computes chart
  -> System retrieves remedies
  -> Results shown
  -> Subscription prompt
```

MVP implementation: no subscription processing; show a simple future subscription prompt or CTA only if trivial.

## Blog/SEO Flow

```text
Transcript knowledge
  -> SEO blog generation
  -> Internal linking
  -> Google indexing
  -> Organic traffic
  -> Users try remedy engine
```

MVP implementation: basic blog/category pages and internal links. Automated SEO generation is post-MVP.

## Social Media Flow: Awareness Engine

Platforms:

- X
- Instagram
- Reddit
- LinkedIn
- YouTube Shorts

```text
Knowledge DB
  -> Content agent
  -> Drafts: threads, short posts, carousels, captions, hooks
  -> Human approval
  -> Posting
  -> Traffic to website
```

MVP implementation: out of scope except documenting future hooks. No auto-posting.

## Video Generation Flow

This is the future virality engine:

```text
Transcript chunk
  -> Script generator
  -> Storyboard generator
  -> Visual prompt generator
  -> Caption generator
  -> Review UI
  -> Remotion/FFmpeg render
  -> Short-form video
```

MVP implementation: out of scope.

## Analytics Flywheel

Track later:

- most searched problems
- highest converting remedies
- highest retention categories
- best-performing videos
- SEO winners
- social winners

```text
Analytics
  -> Content prioritization
  -> More blogs/videos
  -> More traffic
```

MVP implementation: optional minimal event logging only if it does not slow the core remedy flow.

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

## MVP Out of Scope

- Real Swiss Ephemeris or pyswisseph production integration.
- Automated YouTube crawling.
- Autonomous social posting.
- Auto-publishing remedies or personalized interpretations.
- Fully automated Slack production bot that publishes or approves content without review.
- Payments and subscriptions.
- User accounts and saved profiles.
- Advanced D9/D10/D60 charts.
- Full dasha/transit computation.
- Vector database or knowledge graph.
- Native app/PWA polish.
- Complex agents.
- Slack video intake automation.
- SEO/social draft automation.
- Advanced video generation.
- Remotion/FFmpeg rendering.
- Auto-posting.
- Community features.

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
- `services/jobs/`: post-MVP durable job queue and runner.
- `services/agents/`: post-MVP agent actions that create drafts/jobs.
- `services/analytics/`: post-MVP event capture and summaries.
- `services/slack-intake/`: post-MVP Slack channel parsing and video ingestion queue creation.
- `services/content-marketing/`: post-MVP SEO/blog/social draft generation from approved remedies.
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
- Job: post-MVP type, status, payload, output, error, retry count, schedule/completion timestamps.
- Analytics event: post-MVP event name, timestamp, anonymous/session/user reference, minimal non-sensitive payload.
- Video intake item: post-MVP source channel/message metadata, video ID/URL, status, dedupe key, transcript job reference.
- Marketing draft: post-MVP channel, format, source remedies, draft body, status, review notes.

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
- `/admin/automation`: post-MVP background job queue and failures.
- `/admin/automation/jobs/[id]`: post-MVP job details and retry path.

Authentication is out of MVP unless explicitly ticketed. Until auth exists, admin routes are internal/local-only and must not be treated as production-safe.

## API and Service Behavior

- Admin transcript APIs save source metadata and queue or run deterministic extraction.
- Remedy APIs must never publish AI/draft output without an explicit reviewed/published status.
- Remedy finder APIs validate user input and persist only the minimum needed data.
- Matching APIs load a request, create or fetch a chart snapshot, fetch published remedies, score them, and persist a match result.
- Post-MVP cron/job APIs process small batches, record failures, and avoid leaking sensitive payloads in logs.

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

## Post-MVP Automation Rules

Post-MVP automation should support:

- Slack video intake jobs.
- Transcript processing jobs.
- Remedy extraction jobs.
- Blog draft jobs.
- Social draft jobs.
- Analytics summary jobs.
- Review reminder jobs.

Agents and jobs create drafts, summaries, tags, citations, and review tasks. They do not auto-publish remedies or personalized interpretations.

## Slack Video Intake Workflow

Target workflow:

1. User drops one or more YouTube video IDs or URLs into an approved Slack channel.
2. Slack intake service parses each message and extracts video IDs/URLs.
3. System stores each unique video as a video intake item with Slack message metadata.
4. System queues transcript extraction for each item.
5. Transcript extraction stores source metadata, transcript text/chunks, and attribution/copyright notes.
6. Remedy extraction creates draft remedy snippets linked to transcript chunks.
7. Admin reviews, edits, and publishes remedy snippets.
8. Approved remedies can feed matching, blog drafts, and social drafts.

Slack intake is the first automated ingestion expansion after the core MVP and should be designed so it uses the same transcript/remedy services.

## SEO Blog and Social Content Workflow

Target workflow:

1. Approved remedy snippets and transcript citations become the source material.
2. SEO/blog agent proposes category pages, blog outlines, FAQs, and internal links.
3. Blog drafts are stored as reviewable content, not auto-published by default.
4. Social draft agent proposes short posts for X, Instagram, LinkedIn, Reddit, and YouTube Shorts scripts.
5. Social drafts keep source remedy references and safety notes.
6. Humans approve publication until a future policy explicitly allows low-risk auto-scheduling.

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
9. Prepare deployment readiness for Vercel and Supabase.
10. QA MVP end-to-end flow and safety guardrails.

Post-MVP order:

1. Add basic analytics and logging.
2. Build automation engine and background job workflow.
3. Design Slack video intake automation.
4. Expand SEO/blog/social draft automation.
5. Add future agent hooks and documentation.
6. Add video generation pipeline.
