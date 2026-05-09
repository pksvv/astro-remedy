# Astrology Remedy Intelligence Platform (ARIP)
## Exhaustive Business Requirements Document (BRD)

---

# 1. Executive Summary

## Vision
Build a scalable AI-assisted astrology intelligence platform that:
- Computes astrological charts automatically
- Extracts remedies and interpretations from curated astrologer video transcripts
- Maps remedies to user-specific astrological conditions
- Provides instant self-service guidance
- Uses AI agents for content ingestion, knowledge extraction, SEO, social growth, and marketing automation
- Operates primarily as a mobile-optimized web platform initially

The core differentiation is:
> Personalized remedy intelligence at scale.

Instead of requiring users to:
- book astrologers,
- watch long videos,
- read lengthy reports,
- or manually search for remedies,

The system computes charts and instantly surfaces relevant remedies from a curated knowledge graph.

---

# 2. Business Objective

## Primary Objective
Create a subscription-driven astrology intelligence platform capable of generating recurring monthly revenue.

## Secondary Objectives
- Build a scalable knowledge graph of astrology remedies
- Create a long-term SEO authority platform
- Build a large searchable repository of astrological remedies
- Automate content marketing pipelines using AI agents
- Create reusable infrastructure for future spirituality/self-help products

---

# 3. Core Product Thesis

Current astrology platforms focus on:
- horoscope reports
- consultations
- generic predictions
- gemstones
- numerology

This platform will instead focus on:

## "Problem → Remedy → Personalized Action"

Examples:
- Enemy issues
- Career blockage
- Financial stress
- Marriage delays
- Burnout
- Health challenges
- Legal disputes
- Reputation damage
- Mental stress
- Saturn periods
- Rahu/Ketu periods
- Relationship conflicts

The user enters birth details.
The system computes charts.
The system identifies conditions.
The system maps conditions to remedies extracted from curated transcripts.

The user receives:
- targeted guidance
- contextual explanations
- practical remedies
- mantra suggestions
- behavioral guidance
- spiritual practices
- astrologer-derived interpretations

---

# 4. Target Audience

## Primary Audience

### Astrology-aware users
People who:
- already consume astrology content
- follow astrologers on YouTube/Instagram
- search remedies online
- believe in astrology guidance
- seek emotional/spiritual clarity

Age Group:
- 22–50

Geography:
- India initially
- NRI audience later
- English-first initially
- Hinglish later

---

## Secondary Audience

### Self-help seekers
Users interested in:
- spirituality
- manifestation
- meditation
- karma
- Vedic systems
- self-improvement

---

# 5. Business Model

## Initial Model

### Freemium Subscription

#### Free Tier
- limited remedy access
- limited charts
- limited daily usage
- limited transcript explanations

#### Paid Tier
- unlimited remedies
- advanced chart access
- dasha analysis
- personalized insights
- saved profiles
- historical tracking
- advanced search
- premium content

---

## Potential Future Revenue Streams

### Premium Features
- advanced AI interpretations
- advanced dasha analysis
- transit analysis
- personalized dashboards

### Affiliate Opportunities
- books
- courses
- consultations
- meditation products
- spiritual tools

### API Access
- astrology computation APIs
- remedy recommendation APIs

### White-label SaaS
Provide backend engine to astrologers.

---

# 6. Core Differentiators (USP)

## Primary USP
Automated personalized remedies.

---

## Secondary USPs

### 1. Transcript Intelligence Engine
Curated astrologer video transcripts transformed into structured knowledge.

### 2. Remedy Retrieval System
Problem-oriented remedy discovery.

### 3. Deterministic + AI Hybrid
- deterministic chart computation
- AI-assisted interpretation layer

### 4. Self-Service Experience
No astrologer booking required.

### 5. Large-Scale Knowledge Graph
Structured astrological intelligence system.

### 6. Agentic Content Pipeline
AI-assisted SEO + social content generation.

---

# 7. Platform Scope

## Phase 1 Scope

### User Features
- birth chart input
- D1 chart computation
- basic dasha computation
- remedy retrieval
- transcript explanations
- searchable problem categories
- blog content
- authentication
- subscriptions

### Admin Features
- transcript ingestion
- video management
- remedy tagging
- content moderation
- analytics dashboard

### AI Agent Features
- transcript extraction
- transcript cleaning
- remedy extraction
- content drafting
- SEO article generation
- social media draft generation

---

## Future Scope
- D1–D60 charts
- AI voice astrologer
- multilingual support
- app/PWA
- community features
- astrology memory/profile engine
- compatibility analysis
- event prediction systems
- agentic recommendation systems

---

# 8. Functional Requirements

# 8.1 User Authentication

## Features
- email login
- Google login
- OTP login
- subscription management
- profile management

---

# 8.2 Birth Data Input Engine

## Inputs
- name
- date of birth
- time of birth
- place of birth

## Requirements
- timezone resolution
- latitude/longitude lookup
- validation
- chart recalculation

---

# 8.3 Astrology Computation Engine

## Charts Required

### Core Charts
- D1
- D9
- D10
- D7
- D12
- D20
- D24
- D30
- D60

### Additional Computations
- planetary positions
- nakshatras
- houses
- aspects
- conjunctions
- yogas
- retrograde states
- exaltation/debilitation

### Dashas
- Vimshottari Mahadasha
- Antardasha
- Pratyantardasha

### Transit Support (Future)
- Saturn transit
- Jupiter transit
- Rahu/Ketu transit

---

## Technical Requirement
Use reliable astronomical libraries.

### Candidate Libraries
- Swiss Ephemeris
- pyswisseph
- Jagannatha Hora references
- PyJHora references

---

# 8.4 Remedy Recommendation Engine

## Core Logic

### Inputs
- chart data
- current dasha
- active problem category
- planetary conditions

### Outputs
- remedies
- explanations
- transcript snippets
- behavioral suggestions
- mantra suggestions
- lifestyle recommendations

---

## Matching Logic

### Example
IF:
- Taurus ascendant
- Libra 6th house
- Saturn Mahadasha
- Venus afflicted

THEN:
Return:
- relationship negotiation remedies
- workplace diplomacy remedies
- Venus balancing practices
- transcript references

---

# 8.5 Transcript Intelligence Engine

## Pipeline

### Step 1
User/admin submits YouTube link.

### Step 2
Transcript extraction.

### Step 3
Transcript cleanup.

### Step 4
Semantic chunking.

### Step 5
Astrological entity extraction.

### Step 6
Remedy extraction.

### Step 7
Knowledge graph tagging.

### Step 8
Storage/indexing.

---

## Metadata to Extract
- astrologer
- topic
- houses
- planets
- signs
- dashas
- remedies
- problem categories
- emotional tone
- cautionary notes
- spiritual references

---

# 8.6 Search Engine

## Search Types
- natural language search
- chart-driven search
- problem-based search
- remedy-based search
- astrologer-style search

### Example Queries
- enemy remedies
- Saturn Mahadasha remedies
- career blockage
- Rahu problems
- marriage delay

---

# 8.7 Blog Engine

## Purpose
- SEO growth
- authority building
- funnel traffic
- educational content

## Blog Types
- educational
- remedy-focused
- astrology explainers
- case studies
- transcript summaries
- trend analysis

---

# 8.8 Social Content Engine

## Platforms
- X
- Instagram
- LinkedIn
- Reddit
- YouTube Shorts

## Content Types
- threads
- short insights
- chart explainers
- remedy snippets
- quote graphics
- astrology observations

---

# 9. AI Agent Architecture

# 9.0 Agentic Delivery Layer: Symphony + Codex CLI

The platform should be developed and operated with an agentic delivery loop using Symphony as the work orchestrator and Codex CLI as the coding agent runtime.

## Purpose
Use Symphony to convert product and engineering tasks into isolated autonomous implementation runs. Instead of manually supervising many Codex sessions, the team manages work through Linear issues while Symphony provisions workspaces and runs Codex against each eligible issue.

## Operating Model
- Linear is the control plane for implementation work.
- Each active issue maps to a dedicated Symphony workspace.
- Symphony launches Codex CLI in app-server mode inside that workspace.
- Repository-owned workflow policy lives in `WORKFLOW.md`.
- Agents work until the ticket reaches a handoff state such as Human Review, Rework, Merging, or Done.
- Humans review strategy, astrology-domain correctness, safety language, compliance, and final product quality.

## Recommended Task Types
- product requirement decomposition
- technical design drafts
- database schema proposals
- transcript ingestion pipeline implementation
- remedy extraction and retrieval implementation
- SEO/content automation scripts
- test coverage and QA smoke tests
- bug fixes and review-feedback loops

## Required Guardrails
- Start with low concurrency while the repo is immature.
- Keep all agent-generated astrology remedies behind human review before publishing.
- Require citations or source references for transcript-derived interpretations.
- Avoid medical, legal, financial, or fear-based guarantees.
- Protect birth data, location data, chart data, saved profiles, and subscription metadata.
- Require tests or explicit verification notes on every implementation task.

## Repo Contract
- `WORKFLOW.md` defines Symphony tracker configuration, workspace hooks, Codex runtime settings, and the per-issue prompt.
- `docs/mvp-architecture-and-definition.md` defines MVP scope, architecture, routes, module boundaries, data concepts, and safety defaults.
- `docs/agentic-delivery-model.md` defines detailed Linear decomposition, ticket templates, automation architecture, and product guardrails for Codex agents.
- `docs/symphony-codex-cli-runbook.md` documents how to run Symphony against this repo.
- Linear tickets should include acceptance criteria, verification expectations, and any astrology/compliance constraints.

---

# 9.1 Video Discovery Agent

## Responsibilities
- discover relevant videos
- track astrologer channels
- identify trending topics
- prioritize high-value content

---

# 9.2 Transcript Extraction Agent

## Responsibilities
- fetch transcripts
- clean transcripts
- normalize formatting
- remove noise

---

# 9.3 Remedy Intelligence Agent

## Responsibilities
- identify remedies
- classify remedies
- extract astrological conditions
- create structured mappings

---

# 9.4 Knowledge Graph Agent

## Responsibilities
- build graph relationships
- connect planets/houses/remedies
- create searchable semantic network

---

# 9.5 SEO Blog Agent

## Responsibilities
- generate blog drafts
- optimize SEO
- create headings
- generate FAQs
- internal linking

---

# 9.6 Social Media Agent

## Responsibilities
- identify trending discussions
- draft posts
- generate hashtags
- generate short-form content
- suggest engagement opportunities

---

# 9.7 Human-in-the-Loop Review Agent

## Responsibilities
- approval workflow
- moderation
- quality control
- ethical review

---

# 9.8 Analytics Agent

## Responsibilities
- engagement analysis
- SEO analysis
- funnel optimization
- conversion tracking
- topic opportunity analysis

---

# 10. User Experience Flow

# 10.1 First-Time User Journey

### Step 1
User lands from:
- X
- Instagram
- Google
- Reddit
- YouTube

### Step 2
User reads:
- blog
- remedy page
- astrology insight

### Step 3
CTA:
"Get Personalized Remedies"

### Step 4
User enters birth details.

### Step 5
System computes chart.

### Step 6
System identifies conditions.

### Step 7
System retrieves remedies.

### Step 8
User sees:
- explanation
- remedy
- transcript snippets
- next actions

### Step 9
Upsell subscription.

---

# 11. Marketing Funnel

# Top of Funnel

## Discovery Channels
- X
- Reddit
- Instagram
- SEO blogs
- YouTube Shorts
- LinkedIn

## Content Strategy
- astrology observations
- short remedy insights
- chart examples
- Saturn/Rahu discussions
- trending astrology topics

---

# Middle of Funnel

## Lead Capture
- free remedies
- free reports
- email signup
- newsletter

## Trust Building
- blog content
- case studies
- detailed explainers
- astrology education

---

# Bottom of Funnel

## Conversion
- subscription plans
- premium remedies
- advanced chart access

---

# Retention Funnel

## Retention Features
- daily insights
- dasha notifications
- transit alerts
- new remedy recommendations
- saved charts

---

# 12. Technical Architecture

# Frontend

## Recommended Stack
- Next.js
- React
- Tailwind CSS
- TypeScript

---

# Backend

## Recommended Stack
- Node.js
- Python microservices
- FastAPI
- PostgreSQL
- Redis

---

# AI Layer

## Models
- OpenAI APIs
- Claude APIs
- local models later

---

# Data Layer

## Databases
- PostgreSQL
- Vector DB
- Graph DB (future)

---

# Search Layer

## Options
- Elasticsearch
- Meilisearch
- Pinecone/Weaviate

---

# Infrastructure

## Hosting
- Vercel
- GCP
- Railway
- Supabase

---

# 13. Non-Functional Requirements

## Scalability
- support large transcript ingestion
- support concurrent chart computation

## Reliability
- accurate astrology calculations
- transcript integrity

## Security
- encrypted user data
- secure authentication

## Performance
- fast chart generation
- low-latency search

## Mobile Optimization
- responsive UI
- fast mobile loading

---

# 14. Compliance & Ethical Requirements

## Important Considerations
- avoid medical/legal guarantees
- disclaimers required
- avoid exploitative fear-based language
- user privacy protections
- transcript copyright considerations

---

# 15. MVP Roadmap

# MVP 1

## Goal
Core astrology remedy engine.

## Features
- D1 chart
- basic dashas
- transcript ingestion
- remedy retrieval
- search
- mobile website

---

# MVP 2

## Goal
SEO + growth engine.

## Features
- blog engine
- social media drafts
- analytics
- subscriptions

---

# MVP 3

## Goal
Advanced intelligence platform.

## Features
- D1–D60
- advanced recommendation engine
- knowledge graph
- PWA/app

---

# 16. Success Metrics

## Product Metrics
- daily active users
- search usage
- chart computations
- retention rate

## Marketing Metrics
- SEO traffic
- social engagement
- conversion rate
- CAC
- subscription growth

## Revenue Metrics
- MRR
- churn
- ARPU
- LTV

---

# 17. Risks

## Business Risks
- content legality
- platform dependency
- SEO volatility
- trust/reputation risk

## Technical Risks
- inaccurate calculations
- AI hallucinations
- poor remedy mapping

## Product Risks
- low retention
- poor onboarding
- overwhelming UI

---

# 18. Long-Term Vision

The platform evolves into:

## "Astrology Intelligence Operating System"

Where:
- astrology knowledge becomes structured
- remedies become searchable
- users receive personalized guidance instantly
- AI agents automate discovery, interpretation, and growth
- the platform becomes an authority engine in spiritual/self-help intelligence

---

# 19. Immediate Next Steps

## Phase 1
- finalize BRD
- define architecture
- define transcript schema
- define astrology computation stack

## Phase 2
- create MVP backlog
- create technical design docs
- define database schema
- define APIs

## Phase 3
- start implementation using Codex
- build ingestion pipeline
- build chart engine
- build search engine

---

# 20. Final Strategic Recommendation

This idea has strong potential IF:
- positioned as personalized remedy intelligence
- executed with strong SEO/social distribution
- focused on retention via recurring guidance
- built with scalable content ingestion
- kept operationally lean through automation

The moat is NOT astrology itself.
The moat is:
- structured knowledge
- personalization
- automation
- discoverability
- distribution
- speed of insight retrieval.

---

# 21. Agentic Delivery Model

## Objective

ARIP should be built and maintained through an agentic delivery system where OpenAI Symphony orchestrates Codex CLI agents against Linear issues. The goal is to reduce manual coordination while preserving human review for sensitive astrology, privacy, copyright, and product-quality decisions.

## Delivery Source of Truth

The repository must preserve a clear separation of responsibilities:

### `WORKFLOW.md`
- Symphony/Codex runtime contract.
- Contains tracker configuration, eligible Linear states, workspace setup, Codex command, and the concise agent prompt.
- Should stay operational and compact.
- Should not become the full product specification.

### BRD and Product Docs
- `astrology_remedy_platform_exhaustive_brd.md` remains the product requirements source of truth.
- `docs/mvp-architecture-and-definition.md` defines the concise implementation architecture and MVP boundary for Codex agents.
- Detailed delivery and automation guidance lives in `docs/agentic-delivery-model.md`.
- Architecture decisions, QA notes, and implementation runbooks should be added under `docs/`.

### Linear Tickets
- Linear is the executable task queue.
- Each ticket should be small, scoped, and independently runnable in one Symphony-created workspace.
- Tickets must include acceptance criteria, verification expectations, and guardrails relevant to the work.

## Symphony Operating Model

Symphony should:
- Watch the ARIP Linear project.
- Select eligible issues from configured states.
- Create an isolated workspace per issue.
- Clone or prepare the repo.
- Run `codex app-server`.
- Provide the issue title, state, labels, priority, and description to Codex through `WORKFLOW.md`.
- Allow Codex to implement, test, and hand off scoped changes.

Codex agents should:
- Read the Linear issue first.
- Read relevant repo docs instead of relying on previous chat memory.
- Keep changes scoped to the issue.
- Prefer deterministic logic for business rules.
- Keep AI integrations behind service interfaces.
- Produce a handoff with files touched, verification, risks, and follow-up tickets.

## Recommended Linear States

- `Todo`: ready for Symphony dispatch.
- `In Progress`: active Codex workspace or agent run.
- `Rework`: reviewer requested targeted fixes; eligible for Symphony dispatch.
- `Human Review`: Codex completed work; person must review before merge/publication.
- `Merging`: approved and being landed.
- `Done`: merged, verified, and complete.

Dispatch states should initially be:
- `Todo`
- `In Progress`
- `Rework`

Non-dispatch states should initially be:
- `Human Review`
- `Merging`
- `Done`

## Task Decomposition for Symphony

### Research/Design Tickets
Use for unresolved implementation decisions.

Examples:
- Select the MVP astrology computation approach and define the replacement interface for Swiss Ephemeris.
- Design the transcript/remedy schema with citations, copyright metadata, and review states.
- Define first-pass remedy matching rules for the MVP problem categories.

Expected output:
- Design doc, ADR, or implementation recommendation.
- Follow-up implementation tickets.

### Implementation Tickets
Use for scoped code changes.

Examples:
- Scaffold Next.js App Router foundation.
- Implement admin transcript ingestion.
- Implement placeholder chart service behind an interface.
- Implement remedy matching service and results UI.

Expected output:
- Code changes.
- Tests or verification notes.
- Clear handoff.

### QA/Test Tickets
Use to verify existing behavior.

Examples:
- Add tests for remedy extraction parsing.
- Verify mobile remedy finder flow.
- Run build and document deployment blockers.

Expected output:
- Automated tests where feasible.
- Manual QA notes when needed.
- Follow-up bug tickets for out-of-scope failures.

### Review-Feedback Tickets
Use to address human review comments.

Examples:
- Add missing citations to remedy result cards.
- Tighten disclaimer language.
- Fix privacy issue in analytics payloads.

Expected output:
- Targeted fixes only.
- Explanation of how review feedback was addressed.

### Follow-Up/Refactor Tickets
Use after core functionality exists.

Examples:
- Extract shared form controls.
- Add typed job payload helpers.
- Replace placeholder location handling with a geocoding interface.

Expected output:
- Low-risk cleanup.
- No hidden feature expansion.

## Symphony-Ready Linear Ticket Template

```markdown
## Goal

State the user/admin/system outcome in one paragraph.

## Context

Reference relevant repo docs and product constraints. Include enough detail for a Codex agent with no chat memory.

Relevant docs:
- `astrology_remedy_platform_exhaustive_brd.md`
- `docs/agentic-delivery-model.md`

## Scope

In scope:
- Exact behavior, files, or modules expected.

Out of scope:
- Adjacent work the agent must not do.

## Acceptance Criteria

- Concrete, testable criterion.
- Concrete, testable criterion.
- Include mobile, privacy, citation, disclaimer, or admin-review requirements where relevant.

## Technical Notes

- Preferred stack, interfaces, APIs, schema names, or service boundaries.
- Mention whether AI calls should be real, mocked, or abstracted.
- Mention whether data should be persisted, seeded, or local-only.

## Verification

- Commands or manual checks to run.
- Expected result for each check.

## Guardrails

- Human review required for remedy/interpretation output.
- No medical/legal/financial guarantees.
- Source citations required for transcript-derived claims.
- Protect birth details, location, chart snapshots, and saved profile data.
- Respect transcript copyright and attribution.
```

---

# 22. Automation and Agent Runtime Roadmap

## Objective

The platform should eventually run as an automated system, not as a manually driven admin tool. Automation should be implemented through durable jobs, scheduled workflows, typed agent services, and human review gates.

## MVP Automation Architecture

Initial automation should use:
- Vercel Cron or a simple scheduled route.
- Postgres-backed job table.
- Next.js route handlers for job execution.
- Typed service modules for agent actions.
- Admin review UI for drafts, failed jobs, and generated outputs.

Candidate future orchestration layers:
- Inngest
- Trigger.dev
- Vercel Workflow
- BullMQ + Redis
- Temporal

The MVP should keep job payloads typed and runtime-agnostic so the orchestration layer can be replaced later.

## Initial Automated Job Types

- `TRANSCRIPT_PROCESSING`: normalize transcript text, chunk it, and preserve source references.
- `REMEDY_EXTRACTION`: create draft remedy snippets with problem categories, tags, confidence, and citations.
- `BLOG_DRAFT`: create draft SEO content from approved remedies and transcript references.
- `ANALYTICS_SUMMARY`: summarize usage, content performance, and topic opportunities.
- `REVIEW_REMINDER`: surface stale drafts, failed jobs, or high-risk generated outputs.

## Automation Policy

- Agents may create drafts, summaries, tags, citations, and review tasks.
- Agents should not auto-publish remedies or personalized interpretations by default.
- Human review is required before user-facing remedy guidance becomes published.
- AI-generated claims must be traceable to source transcripts, curated content, or deterministic chart data.
- Failed jobs must be visible and retryable.
- Automation must not leak sensitive birth data, chart data, or subscription data into logs.

## Product Guardrails

- Astrology guidance must be framed as spiritual, entertainment, and self-reflection support.
- No medical, legal, or financial guarantees.
- No fear-based language.
- Transcript-derived claims require source citations.
- Copyright and attribution must be tracked for transcript content.
- Long transcript passages should not be publicly republished unless rights are clear.
- Birth details, place data, saved chart data, subscription data, and account data are sensitive.
- Chart computation must remain separate from remedy matching.
- Content ingestion must remain separate from user-facing retrieval.
- AI outputs must remain reviewable and editable by an admin.

## Technical Details Future Codex Agents Need

Preferred stack:
- Next.js App Router
- TypeScript
- Tailwind CSS
- PostgreSQL/Supabase
- Prisma unless a future ticket explicitly changes the data layer
- OpenAI/LLM integration behind service interfaces
- Python/FastAPI only if real astrology computation requires it

Core service boundaries:
- `services/astrology`: chart computation interface and implementations
- `services/transcripts`: ingestion, normalization, chunking
- `services/remedies`: extraction, review workflow, publication
- `services/matching`: deterministic matching and scoring
- `services/ai`: model provider adapters and prompt wrappers
- `services/jobs`: durable job queue and runner
- `services/agents`: typed agent actions that create drafts or jobs
- `services/analytics`: event capture and summaries

MVP implementation order:
1. Project foundation and architecture
2. Database schema and content model
3. Admin transcript/remedy ingestion
4. User birth details and remedy finder flow
5. Remedy matching engine
6. Blog/SEO pages
7. Basic analytics and logging
8. Automation engine and background workflows
9. Deployment readiness
10. Future agent expansion hooks
