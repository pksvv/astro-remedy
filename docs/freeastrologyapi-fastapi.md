# ARIP Platform API

This repo now includes a local FastAPI wrapper around FreeAstrologyAPI so the integration is reusable from:

- Symphony tickets
- manual testing
- future app/backend code

Files:

- [app.py](/Users/admin/code/vipul/astro-remedy/app.py:1)
- [services/freeastrology_api.py](/Users/admin/code/vipul/astro-remedy/services/freeastrology_api.py:1)
- [requirements-freeastrologyapi.txt](/Users/admin/code/vipul/astro-remedy/requirements-freeastrologyapi.txt:1)

## What It Exposes

Routes:

- `GET /health`
- `POST /resolve-place`
- `POST /chart/svg`
- `POST /planets`
- `POST /houses`
- `POST /vendor/{endpoint}`

Swagger UI:

- `/docs`

OpenAPI JSON:

- `/openapi.json`

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-freeastrologyapi.txt
```

The service expects:

- `ASTROLOGY_API_KEY` in the environment

Example:

```bash
set -a
source /Users/admin/code/vipul/astro-remedy/.env
set +a
```

## Run

```bash
source .venv/bin/activate
set -a
source /Users/admin/code/vipul/astro-remedy/.env
set +a
uvicorn app:app --reload --port 8010
```

Then open:

- [http://127.0.0.1:8010/docs](http://127.0.0.1:8010/docs)

## Request Shapes

### Resolve place

`POST /resolve-place`

```json
{
  "place": "Sonipat, Haryana, India",
  "refresh": false
}
```

### Chart / planets / houses

`POST /chart/svg`
`POST /planets`
`POST /houses`

```json
{
  "year": 1981,
  "month": 7,
  "date": 9,
  "hours": 3,
  "minutes": 24,
  "seconds": 0,
  "latitude": 28.9948,
  "longitude": 77.0194,
  "timezone": 5.5,
  "ayanamsha": "lahiri",
  "observation_point": "topocentric",
  "chart_type": "d1"
}
```

`chart_type` supports:

- single chart types:
  - `d1`
  - `d2`
  - `d3`
  - `d4`
  - `d5`
  - `d6`
  - `d7`
  - `d8`
  - `d9`
  - `d10`
  - `d11`
  - `d12`
  - `d16`
  - `d20`
  - `d24`
  - `d27`
  - `d30`
  - `d40`
  - `d45`
  - `d60`
- fan-out mode:
  - `all`

When `chart_type` is `all`, the wrapper calls each mapped vendor chart endpoint one by one and returns a combined object keyed by chart type.

### Generic vendor endpoint

`POST /vendor/{endpoint}`

Example:

`POST /vendor/d6-chart-info`

```json
{
  "year": 1981,
  "month": 7,
  "date": 9,
  "hours": 3,
  "minutes": 24,
  "seconds": 0,
  "latitude": 28.9948,
  "longitude": 77.0194,
  "timezone": 5.5,
  "ayanamsha": "lahiri",
  "observation_point": "topocentric",
  "extra": {}
}
```

## Strategy

Recommended usage split:

- `/chart/svg`: use for chart rendering, with `chart_type` selecting one chart or `all`
- `/planets`: use for structured planet details
- `/houses`: use for a house-grouped summary derived from planets
- `/vendor/{endpoint}`: use as an admin or exploration escape hatch for other documented vendor APIs

## Notes

- The wrapper reuses the same cache and place-lookup fallback logic as the earlier script.
- `geo-details` may rate-limit quickly, so manual coordinates/timezone may still be the most reliable path for repeated tests.
- `horoscope-chart-svg-code` returns SVG markup, not structured house/planet JSON.
- for structured placements, prefer `/planets` or `/houses`.
- chart SVG endpoints are not uniform on the vendor side. Some return SVG code while others return SVG URLs. The wrapper normalizes the route shape, but the response payload may still differ by chart type.
