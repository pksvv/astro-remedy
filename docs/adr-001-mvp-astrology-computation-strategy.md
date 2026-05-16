# ADR-001: MVP Astrology Computation Strategy

Status: Accepted for MVP planning
Date: 2026-05-10
Issue: DEV-6

## Context

ARIP needs chart data so the product can connect a user's selected problem category to relevant remedy snippets. The BRD's long-term requirement is reliable astronomical calculation with D1, divisional charts, planetary positions, nakshatras, houses, aspects, yogas, retrograde states, dashas, and future transits. It names Swiss Ephemeris, `pyswisseph`, Jagannatha Hora references, and PyJHora references as candidate sources.

The MVP architecture narrows the first slice to a mobile-first remedy finder with a basic chart snapshot through a replaceable astrology service. It explicitly keeps real Swiss Ephemeris and production `pyswisseph` integration out of MVP scope, while requiring the first service to accept date, time, place text, and timezone metadata, return a normalized chart snapshot, expose `engineName`, `engineVersion`, and `isPlaceholder`, and clearly mark placeholder output in UI and data.

Chart computation must remain separate from remedy matching. AI must not be used for chart math.

## Decision Summary

- MVP approach for now: use a replaceable astrology service interface and allow a third-party chart provider such as FreeAstrologyAPI for short-term delivery.
- Long-term direction: do not rely permanently on third-party chart-generation vendors; plan to own chart computation ourselves behind the same interface.
- Replacement interface: a stable `services/astrology` contract that future engines can implement without changing remedy matching callers.
- Fallback policy: if vendor access or quality is unreliable, use a clearly labeled placeholder path rather than implying false precision.

## Decision

For the current MVP phase, allow a third-party chart provider such as FreeAstrologyAPI behind a strict `services/astrology` interface so the product can move forward without making custom astrology computation a critical-path blocker.

The MVP service must:

- Accept normalized birth inputs plus resolved location/timezone metadata.
- Be replaceable without changing remedy matching callers.
- Record `engineName`, `engineVersion`, and enough metadata to distinguish vendor output from placeholder output.
- Keep a fallback path for unresolved vendor/network/rate-limit situations.
- Avoid overstating precision when location, timezone, or vendor reliability is uncertain.

This is a temporary delivery choice, not the end-state architecture. The long-term target remains an in-house computation engine that we control ourselves, most likely a Python/FastAPI service backed by Swiss Ephemeris or an equivalent validated computation stack.

Third-party chart vendors may be used to accelerate MVP learning, but they should be treated as transitional dependencies. A backlog item should track removing long-term reliance on external chart-generation services.

## Options Considered

### Option A: TypeScript Placeholder D1 Engine

Summary: Implement a small deterministic TypeScript service that normalizes user birth inputs and emits a clearly labeled placeholder chart snapshot with stable tags for matching tests.

Pros:

- Fastest path to build and verify the end-to-end MVP loop.
- Fits the planned Next.js/TypeScript stack with no extra runtime.
- Keeps chart service boundaries visible before production computation is ready.
- Allows remedy matching, persistence, results UI, privacy handling, and disclaimers to be implemented incrementally.
- Avoids shipping unverified astronomical calculations under a misleading precision claim.

Cons:

- Not astrologically accurate.
- Cannot support real planetary positions, ascendant, nakshatras, houses, divisional charts, or dashas.
- Risks user or future-agent confusion if labels and UI warnings are weak.

Use for MVP: Yes, as a fallback path and test harness.

### Option B: Third-Party Chart API (for example FreeAstrologyAPI)

Summary: Use an external chart API for short-term MVP chart generation while keeping the app behind a replaceable service boundary.

Pros:

- Fastest path to real chart-like output without building our own engine first.
- Lets product and UX learn from real-looking chart responses earlier.
- Can provide SVG chart outputs plus structured planet data, depending on the provider endpoint.
- Keeps custom computation work off the MVP critical path.

Cons:

- Adds vendor dependency, rate-limit risk, and network dependency.
- Payload and endpoint behavior may be inconsistent across chart types.
- Geo lookup, timezone handling, and chart output quality may still need our own guardrails.
- Long-term reliance would create product and infrastructure risk.

Use for MVP: Yes, temporarily, if wrapped behind our own stable interface and backed by a fallback path.

### Option C: JavaScript Astrology Libraries

Summary: Use a Node-compatible astrology or astronomy package to compute chart-like values directly in the web app.

Pros:

- Stays in the TypeScript runtime.
- May provide quicker real calculations than building a Python service.
- Easier deployment than a separate compute service if the chosen library is compatible with Vercel.

Cons:

- Library accuracy, sidereal settings, ayanamsa handling, house systems, timezone behavior, and maintenance status need careful validation.
- Many JavaScript packages are astronomy-focused rather than Vedic astrology-complete.
- Incorrect "real-looking" values are riskier than an explicitly marked placeholder.
- Could entangle MVP delivery with library selection before requirements such as Lahiri ayanamsa, house system, divisional chart method, and dasha rules are finalized.

Use for MVP: No. Re-evaluate only after an accuracy spike compares candidates against trusted reference outputs.

### Option D: Python/FastAPI Swiss Ephemeris Integration

Summary: Build a separate astrology compute service using Python, FastAPI, and `pyswisseph` or another Swiss Ephemeris binding.

Pros:

- Best fit for reliable astronomical calculation requirements.
- Aligns with BRD candidate libraries and long-term chart accuracy needs.
- Can evolve independently from Next.js and scale as a computation service.
- Enables explicit versioning of ephemeris files, ayanamsa, house system, and chart algorithms.

Cons:

- More deployment complexity for the first slice.
- Requires decisions on ephemeris data licensing, packaging, reference tests, geocoding, timezone historical offsets, and Vedic calculation conventions.
- Premature for MVP while remedy ingestion, review, matching, and UI are still being validated.

Use for MVP: Not for the first implementation. Treat as the planned production replacement.

## Service Interface

Future agents should implement `services/astrology` around this contract. Names can be adjusted to local TypeScript conventions, but the semantics should remain stable.

```ts
export type AstrologyEngineKind =
  | "placeholder-d1"
  | "swiss-ephemeris"
  | "javascript-library";

export type ChartComputationInput = {
  birthDate: string; // YYYY-MM-DD
  birthTime: string; // HH:mm, 24-hour local civil time
  birthPlaceText: string;
  timezone: {
    mode: "userProvided" | "resolved" | "placeholder";
    ianaTimeZone?: string;
    utcOffsetMinutes?: number;
    source: "form" | "geocoder" | "adminOverride" | "notResolved";
  };
  location?: {
    mode: "resolved" | "placeholder" | "notResolved";
    latitude?: number;
    longitude?: number;
    countryCode?: string;
    source?: "geocoder" | "adminOverride" | "notResolved";
  };
  calculationPreferences?: {
    zodiac: "sidereal";
    ayanamsa?: "lahiri" | "unknown";
    houseSystem?: "whole-sign" | "equal" | "placidus" | "unknown";
    locale?: string;
  };
  requestContext?: {
    requestId?: string;
    problemCategory?: string;
  };
};

export type ChartBody = {
  chartType: "D1";
  ascendant?: ChartPoint;
  planets: ChartPoint[];
  houses: ChartHouse[];
  conditionTags: string[];
  unsupported: string[];
};

export type ChartPoint = {
  key: string;
  label: string;
  sign?: string;
  house?: number;
  longitudeDegrees?: number;
  nakshatra?: string;
  retrograde?: boolean;
  dignity?: "exalted" | "debilitated" | "own" | "friendly" | "neutral" | "unknown";
  precision: "placeholder" | "computed" | "unknown";
};

export type ChartHouse = {
  house: number;
  sign?: string;
  precision: "placeholder" | "computed" | "unknown";
};

export type ChartComputationResult = {
  engine: {
    engineName: string;
    engineVersion: string;
    engineKind: AstrologyEngineKind;
    isPlaceholder: boolean;
    calculationProfile: string;
  };
  inputMetadata: {
    normalizedBirthDate: string;
    normalizedBirthTime: string;
    birthPlaceText: string;
    timezoneMode: ChartComputationInput["timezone"]["mode"];
    ianaTimeZone?: string;
    utcOffsetMinutes?: number;
    locationMode?: NonNullable<ChartComputationInput["location"]>["mode"];
    latitude?: number;
    longitude?: number;
  };
  chart: ChartBody;
  quality: {
    status: "placeholder" | "computed" | "failed";
    warnings: string[];
    missingInputs: string[];
    accuracyNotes: string[];
  };
  computedAt: string; // ISO timestamp
};

export interface ChartService {
  computeChart(input: ChartComputationInput): Promise<ChartComputationResult>;
}
```

## Fallback Output Rules

If the MVP is using a placeholder fallback instead of a live vendor or owned computation engine, it should return:

- `engine.engineName: "arip-placeholder-d1"`
- `engine.engineKind: "placeholder-d1"`
- `engine.isPlaceholder: true`
- `engine.calculationProfile: "deterministic-placeholder-v1"`
- `quality.status: "placeholder"`
- A warning such as `This chart snapshot is a deterministic placeholder and is not an astronomical calculation.`
- `chart.unsupported` entries for real ascendant, planetary longitudes, nakshatras, houses, divisional charts, dashas, yogas, aspects, retrograde states, and transits.
- Stable `conditionTags` suitable only for exercising matcher behavior, for example category-level or input-derived placeholder tags.

It must not fabricate real-looking degrees, nakshatras, dashas, or precise placements.

If the MVP is using a third-party vendor response, the stored chart snapshot should still preserve:

- the vendor engine name
- the vendor endpoint or chart mode used
- a stable marker that the result came from an external provider
- enough metadata to support later replacement or recalculation

## Location and Timezone Placeholder Policy

MVP input must accept birth date, birth time, place text, and timezone metadata. Because geocoding and historical timezone resolution are not in the first implementation, the policy is:

- Store `birthPlaceText` as user-provided text, treated as sensitive data.
- If the user explicitly provides an IANA timezone or UTC offset, record `timezone.mode: "userProvided"`.
- If no reliable timezone exists, record `timezone.mode: "placeholder"` and `timezone.source: "notResolved"`.
- If latitude/longitude are not resolved, record `location.mode: "notResolved"` or omit `location`.
- Do not infer coordinates or timezone from free-text place with ad hoc parsing.
- Do not use the server timezone as the user's birth timezone.
- Show a user-facing notice whenever timezone or location is unresolved and the chart is placeholder-based.
- Exclude raw birth date, birth time, place text, coordinates, and full chart snapshots from analytics events and routine logs.

Future real computation must add a geocoding and historical timezone resolver before claiming accurate ascendant, houses, divisional charts, or dashas.

## Replacement Requirements for a Real Engine

A production in-house engine can replace the temporary vendor or placeholder path when it satisfies:

- Deterministic output for a fixed input, engine version, ephemeris version, ayanamsa, and house system.
- Explicit support for sidereal zodiac and chosen ayanamsa, initially expected to be Lahiri unless product/domain review chooses otherwise.
- Historical timezone and latitude/longitude resolution with traceable source metadata.
- Reference test cases comparing D1 outputs against trusted tools or astrologer-approved fixtures.
- Clear error handling for ambiguous place, missing time, invalid date, unsupported geography, and ephemeris failures.
- Versioned `calculationProfile` so saved chart snapshots can be audited and recalculated later.
- No dependency from computation code to remedy matching, transcript ingestion, AI prompts, or UI copy.
- A migration path exists from vendor-generated chart snapshots to owned computation snapshots.

## Risks

- Placeholder leakage: Placeholder output could be shown as if it were a real chart. Mitigation: require `isPlaceholder`, warnings, UI labels, and `quality.status`.
- Accuracy debt: Future matching rules may overfit placeholder tags. Mitigation: keep placeholder tags coarse and mark chart-specific matching as fallback-quality until real computation lands.
- Timezone ambiguity: Birth time without historical timezone and coordinates cannot support precise ascendant or houses. Mitigation: record resolution mode and do not infer from server settings.
- Library mismatch: JavaScript libraries may produce inconsistent Vedic outputs. Mitigation: require an accuracy spike before adopting one.
- Third-party vendor lock-in: MVP success could accidentally turn a temporary dependency into a permanent one. Mitigation: maintain the stable service boundary and track an explicit backlog item for owned computation.
- Swiss Ephemeris deployment/licensing complexity: Production integration may need ephemeris files and license review. Mitigation: create a dedicated spike before implementation.
- Privacy exposure: Birth details and chart snapshots are sensitive. Mitigation: avoid routine logging and analytics payloads that include raw birth or full chart data.

## Suggested Follow-Up Tickets

1. Implement `services/astrology` with a replaceable provider boundary and typed contract from this ADR.
2. Add chart snapshot persistence and matcher plumbing that consumes `ChartComputationResult` without depending on vendor internals.
3. Add a dedicated backlog item for replacing long-term vendor dependence with an owned computation engine.
4. Add a dedicated Python/FastAPI Swiss Ephemeris spike with reference fixtures and deployment notes before any accuracy claims are made.
5. Add UI copy and test coverage for vendor/placeholder labeling, timezone resolution warnings, and sensitive-data logging guardrails.

## Implementation Guidance

Recommended first implementation tickets:

1. Implement `services/astrology` TypeScript interfaces and `PlaceholderD1ChartService`.
2. Add unit tests proving deterministic placeholder output, required metadata, and no fabricated precision fields.
3. Wire remedy finder request creation to persist a chart snapshot with `isPlaceholder: true`.
4. Add UI disclaimer/labeling for placeholder chart output on results pages.
5. Add a geocoding/timezone resolver interface with a no-op placeholder implementation.
6. Run an astrology engine spike comparing JavaScript libraries and Python Swiss Ephemeris against reference fixtures.
7. Implement the Swiss Ephemeris/FastAPI engine after reference fixtures, calculation conventions, deployment shape, and licensing are approved.

## Verification Against BRD

This ADR satisfies the BRD by preserving the long-term requirement for reliable astronomical libraries while preventing the MVP from implying precision it does not have. It keeps D1 chart computation as an MVP-facing concept, documents why advanced charts and dashas are deferred, protects sensitive birth/location/chart data, and maintains the required separation between chart computation and remedy matching.
