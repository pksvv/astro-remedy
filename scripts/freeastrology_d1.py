#!/usr/bin/env python3
"""
Resolve birth-place metadata and fetch a D1 / rasi chart SVG from FreeAstrologyAPI.

Uses the project ASTROLOGY_API_KEY from the environment. Place lookups are cached
locally so repeated runs do not need to rediscover coordinates/timezone details.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


API_BASE = "https://json.freeastrologyapi.com"
GEO_ENDPOINT = f"{API_BASE}/geo-details"
CHART_ENDPOINT = f"{API_BASE}/horoscope-chart-svg-code"
PLANETS_ENDPOINT = f"{API_BASE}/planets"
DEFAULT_CACHE_PATH = Path(".cache/freeastrology_places.json")
LOGGER = logging.getLogger("freeastrology_d1")
DEFAULT_BIRTH_ENDPOINTS = ["horoscope-chart-svg-code", "planets"]


class ApiError(RuntimeError):
    pass


@dataclass
class PlaceResolution:
    query: str
    latitude: float
    longitude: float
    timezone_hours: float
    timezone_name: str | None
    raw: dict[str, Any]

    def as_cache_value(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone_hours": self.timezone_hours,
            "timezone_name": self.timezone_name,
            "raw": self.raw,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve place details and request a D1 / rasi chart SVG from "
            "FreeAstrologyAPI."
        )
    )
    parser.add_argument("--name", help="Optional label for the subject.")
    parser.add_argument(
        "--date",
        required=True,
        help="Birth date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--time",
        required=True,
        help="Birth time in HH:MM or HH:MM:SS 24-hour format.",
    )
    parser.add_argument(
        "--place",
        required=True,
        help="Birth place text, for example 'Sonipat, Haryana, India'.",
    )
    parser.add_argument(
        "--api-key-env",
        default="ASTROLOGY_API_KEY",
        help="Environment variable containing the FreeAstrologyAPI key.",
    )
    parser.add_argument(
        "--ayanamsha",
        default="lahiri",
        help="Ayanamsha setting for the chart request. Default: lahiri.",
    )
    parser.add_argument(
        "--observation-point",
        default="topocentric",
        help="Observation point for the chart request. Default: topocentric.",
    )
    parser.add_argument(
        "--output",
        help="Deprecated alias for --svg-output. Optional path to write the returned SVG.",
    )
    parser.add_argument(
        "--svg-output",
        help="Optional path to write the returned SVG.",
    )
    parser.add_argument(
        "--planets-output",
        help="Optional path to write the raw planets JSON response.",
    )
    parser.add_argument(
        "--houses-output",
        help="Optional path to write a derived house-to-planets summary JSON.",
    )
    parser.add_argument(
        "--latitude",
        type=float,
        help="Optional manual latitude override.",
    )
    parser.add_argument(
        "--longitude",
        type=float,
        help="Optional manual longitude override.",
    )
    parser.add_argument(
        "--timezone",
        type=float,
        help="Optional manual timezone offset override in hours, for example 5.5.",
    )
    parser.add_argument(
        "--timezone-name",
        help="Optional manual timezone name override, for example Asia/Kolkata.",
    )
    parser.add_argument(
        "--cache",
        default=str(DEFAULT_CACHE_PATH),
        help=f"Place lookup cache path. Default: {DEFAULT_CACHE_PATH}",
    )
    parser.add_argument(
        "--refresh-place",
        action="store_true",
        help="Ignore cached place data and resolve it again from the API.",
    )
    parser.add_argument(
        "--print-request",
        action="store_true",
        help="Print the final request payload JSON before calling the chart endpoint.",
    )
    parser.add_argument(
        "--endpoint",
        action="append",
        default=[],
        help=(
            "Additional FreeAstrologyAPI endpoint to call with the normalized birth "
            "payload, for example `planets/extended` or `d6-chart-info`. "
            "Can be passed multiple times."
        ),
    )
    parser.add_argument(
        "--skip-default-endpoints",
        action="store_true",
        help="Do not call the default horoscope SVG and planets endpoints.",
    )
    parser.add_argument(
        "--output-dir",
        help=(
            "Directory for generic endpoint response files. Each endpoint is saved as "
            "<endpoint>.json with slashes replaced by double underscores."
        ),
    )
    parser.add_argument(
        "--extra-json",
        help=(
            "Optional JSON object string merged into generic birth-endpoint payloads. "
            "Useful for settings/config/language."
        ),
    )
    parser.add_argument(
        "--list-endpoint-categories",
        action="store_true",
        help="Print the documented endpoint categories tracked in this script and exit.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity. Default: INFO.",
    )
    return parser.parse_args()


def configure_logging(level_name: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level_name),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def documented_endpoint_categories() -> dict[str, list[str]]:
    return {
        "indian_vedic_astrology": [
            "primitive",
            "planets",
            "planets/extended",
            "d2-chart-info",
            "d3-chart-info",
            "d4-chart-info",
            "d5-chart-info",
            "d6-chart-info",
            "d7-chart-info",
            "d8-chart-info",
            "d10-chart-info",
            "d11-chart-info",
            "d12-chart-info",
            "d16-chart-info",
            "d20-chart-info",
            "d24-chart-info",
            "d27-chart-info",
            "d30-chart-info",
            "d40-chart-info",
        ],
        "charts_svg_code": [
            "horoscope-chart-svg-code",
            "navamsa-chart-svg-code",
            "hora-chart-svg-code",
            "drekkana-chart-svg-code",
            "chaturthamsa-chart-svg-code",
            "panchamasa-chart-svg-code",
        ],
        "charts_svg_url": [
            "rasi-chart-svg-url",
            "navamsa-chart-svg-url",
            "hora-chart-svg-url",
            "drekkana-chart-svg-url",
            "chaturthamsa-chart-svg-url",
            "panchamasa-chart-svg-url",
            "d6-chart-svg-url",
            "d7-chart-svg-url",
            "d8-chart-svg-url",
            "d10-chart-svg-url",
            "d11-chart-svg-url",
            "d12-chart-svg-url",
            "d16-chart-svg-url",
            "d20-chart-svg-url",
            "d24-chart-svg-url",
            "d27-chart-svg-url",
            "d30-chart-svg-url",
            "d40-chart-svg-url",
            "d45-chart-svg-url",
            "d60-chart-svg-url",
        ],
        "panchang": [
            "sun-rise-and-sun-set",
            "tithi-timings",
            "nakshatra-durations",
            "yoga-timings",
            "karana-timings",
            "vedic-weekday",
            "lunar-month-info",
            "ritu-information",
            "samvat-information",
            "aayanam",
            "hora-timings",
            "choghadiya-timings",
            "good-and-bad-times",
            "abhijit-muhurat",
            "amrit-kaal",
            "brahma-muhurat",
            "rahu-kalam",
            "yama-gandam",
            "gulika-kalam",
            "dur-muhurat",
            "varjyam",
        ],
        "match_making": [
            "ashtakoot-score",
        ],
        "shad_bala": [
            "shad-bala",
            "shad-bala-summary",
            "shad-bala-break-up",
            "sthana-bala",
            "kaala-bala",
            "dig-bala",
            "cheshta-bala",
            "drig-bala",
            "naisargika-bala",
        ],
        "vimsottari_dasa": [
            "vimsottari-maha-dasas",
            "vimsottari-maha-dasas-and-antar-dasas",
            "dasa-information-for-a-given-date",
        ],
        "geo_location_api": [
            "geo-details",
        ],
        "time_zone_api": [
            "time-zone-with-dst",
        ],
    }


def load_cache(path: Path) -> dict[str, Any]:
    if not path.exists():
        LOGGER.debug("Cache file does not exist yet: %s", path)
        return {}
    LOGGER.debug("Loading cache from %s", path)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_cache(path: Path, cache: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    LOGGER.debug("Saving cache to %s", path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(cache, handle, indent=2, sort_keys=True)
        handle.write("\n")


def api_post_json(url: str, payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    LOGGER.info("POST %s", url)
    LOGGER.debug("Request payload: %s", json.dumps(payload, sort_keys=True))
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read().decode("utf-8")
            LOGGER.info("Response received from %s with HTTP %s", url, response.status)
            LOGGER.debug("Raw response body: %s", content[:2000])
            return json.loads(content)
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        LOGGER.error("HTTP %s from %s", exc.code, url)
        LOGGER.debug("Error response body: %s", error_body)
        raise ApiError(f"HTTP {exc.code} from {url}: {error_body}") from exc
    except urllib.error.URLError as exc:
        LOGGER.error("Request to %s failed: %s", url, exc.reason)
        raise ApiError(f"Request to {url} failed: {exc.reason}") from exc


def deep_merge(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in extra.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def normalize_date(value: str) -> tuple[int, int, int]:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise SystemExit(f"Invalid --date value '{value}'. Use YYYY-MM-DD.") from exc
    return parsed.year, parsed.month, parsed.day


def normalize_time(value: str) -> tuple[int, int, int]:
    formats = ("%H:%M", "%H:%M:%S")
    for fmt in formats:
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.hour, parsed.minute, parsed.second
        except ValueError:
            continue
    raise SystemExit(f"Invalid --time value '{value}'. Use HH:MM or HH:MM:SS.")


def extract_first_float(container: Any, keys: list[str]) -> float | None:
    if isinstance(container, dict):
        for key in keys:
            value = container.get(key)
            if value not in (None, ""):
                try:
                    return float(value)
                except (TypeError, ValueError):
                    pass
        for value in container.values():
            found = extract_first_float(value, keys)
            if found is not None:
                return found
    elif isinstance(container, list):
        for item in container:
            found = extract_first_float(item, keys)
            if found is not None:
                return found
    return None


def extract_first_text(container: Any, keys: list[str]) -> str | None:
    if isinstance(container, dict):
        for key in keys:
            value = container.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for value in container.values():
            found = extract_first_text(value, keys)
            if found is not None:
                return found
    elif isinstance(container, list):
        for item in container:
            found = extract_first_text(item, keys)
            if found is not None:
                return found
    return None


def resolve_place(
    place: str,
    api_key: str,
    cache_path: Path,
    refresh: bool,
) -> PlaceResolution:
    LOGGER.info("Resolving place: %s", place)
    cache = load_cache(cache_path)
    cache_key = place.strip().lower()
    if not refresh and cache_key in cache:
        LOGGER.info("Using cached place resolution for %s", place)
        cached = cache[cache_key]
        return PlaceResolution(
            query=cached["query"],
            latitude=float(cached["latitude"]),
            longitude=float(cached["longitude"]),
            timezone_hours=float(cached["timezone_hours"]),
            timezone_name=cached.get("timezone_name"),
            raw=cached.get("raw", {}),
        )
    LOGGER.info("Cache miss for %s, calling geo-details", place)

    candidates = build_location_candidates(place)
    last_response: dict[str, Any] | None = None
    selected_query: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone_hours: float | None = None
    timezone_name: str | None = None
    response: dict[str, Any] | None = None

    for candidate in candidates:
        LOGGER.info("Trying geo-details candidate: %s", candidate)
        payload = {"location": candidate}
        response = api_post_json(GEO_ENDPOINT, payload, api_key)
        last_response = response

        latitude = extract_first_float(response, ["latitude", "lat"])
        longitude = extract_first_float(response, ["longitude", "lng", "lon"])
        timezone_hours = extract_first_float(
            response,
            ["timezone_offset", "timezoneOffset", "tz_offset", "tz", "timezone"],
        )
        timezone_name = extract_first_text(
            response,
            ["timezone", "timezone_name", "timezoneName", "timezone_id", "timezoneId", "iana_timezone"],
        )

        if latitude is not None and longitude is not None and timezone_hours is not None:
            selected_query = candidate
            LOGGER.info("Geo-details matched candidate: %s", candidate)
            break

    if (
        latitude is None
        or longitude is None
        or timezone_hours is None
        or response is None
    ):
        LOGGER.error("Could not extract required location fields from any geo-details response")
        raise ApiError(
            "Could not extract latitude/longitude/timezone from geo-details response. "
            f"Tried candidates={candidates}. Last response="
            f"{json.dumps(last_response, indent=2) if last_response is not None else 'null'}"
        )

    resolved = PlaceResolution(
        query=selected_query or place,
        latitude=latitude,
        longitude=longitude,
        timezone_hours=timezone_hours,
        timezone_name=timezone_name,
        raw=response,
    )
    cache[cache_key] = resolved.as_cache_value()
    save_cache(cache_path, cache)
    LOGGER.info(
        "Resolved %s to lat=%s lon=%s timezone=%s",
        place,
        resolved.latitude,
        resolved.longitude,
        resolved.timezone_hours,
    )
    return resolved


def build_location_candidates(place: str) -> list[str]:
    parts = [part.strip() for part in place.split(",") if part.strip()]
    candidates: list[str] = []

    def add(candidate: str) -> None:
        normalized = candidate.strip()
        if normalized and normalized not in candidates:
            candidates.append(normalized)

    add(place)
    if parts:
        add(parts[0])
    if len(parts) >= 2:
        add(", ".join(parts[:2]))
    if len(parts) >= 3:
        add(f"{parts[0]}, {parts[-1]}")
    for part in parts[1:]:
        add(part)
    return candidates


def manual_place_resolution(
    place: str,
    latitude: float,
    longitude: float,
    timezone_hours: float,
    timezone_name: str | None,
) -> PlaceResolution:
    LOGGER.info(
        "Using manual place override lat=%s lon=%s timezone=%s",
        latitude,
        longitude,
        timezone_hours,
    )
    return PlaceResolution(
        query=place,
        latitude=latitude,
        longitude=longitude,
        timezone_hours=timezone_hours,
        timezone_name=timezone_name,
        raw={
            "source": "manual_override",
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_hours,
            "timezone": timezone_name,
        },
    )


def request_chart(
    api_key: str,
    year: int,
    month: int,
    day: int,
    hours: int,
    minutes: int,
    seconds: int,
    place: PlaceResolution,
    ayanamsha: str,
    observation_point: str,
) -> tuple[dict[str, Any], str]:
    LOGGER.info("Requesting D1 / rasi chart SVG")
    payload = {
        "year": year,
        "month": month,
        "date": day,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "latitude": place.latitude,
        "longitude": place.longitude,
        "timezone": place.timezone_hours,
        "config": {
            "observation_point": observation_point,
            "ayanamsha": ayanamsha,
        },
    }
    response = api_post_json(CHART_ENDPOINT, payload, api_key)
    svg = response.get("output")
    if not isinstance(svg, str) or "<svg" not in svg:
        LOGGER.error("Chart response did not contain SVG output")
        raise ApiError(
            "Chart response did not contain SVG output: "
            f"{json.dumps(response, indent=2)[:1200]}"
        )
    LOGGER.info("Chart SVG received successfully")
    return payload, svg


def request_planets(
    api_key: str,
    year: int,
    month: int,
    day: int,
    hours: int,
    minutes: int,
    seconds: int,
    place: PlaceResolution,
    observation_point: str,
) -> tuple[dict[str, Any], Any]:
    LOGGER.info("Requesting structured planets data")
    payload = {
        "year": year,
        "month": month,
        "date": day,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "latitude": place.latitude,
        "longitude": place.longitude,
        "timezone": place.timezone_hours,
        "observation_point": observation_point,
    }
    response = api_post_json(PLANETS_ENDPOINT, payload, api_key)
    LOGGER.info("Planets response received successfully")
    return payload, response


def build_birth_payload(
    year: int,
    month: int,
    day: int,
    hours: int,
    minutes: int,
    seconds: int,
    place: PlaceResolution,
    ayanamsha: str,
    observation_point: str,
) -> dict[str, Any]:
    return {
        "year": year,
        "month": month,
        "date": day,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "latitude": place.latitude,
        "longitude": place.longitude,
        "timezone": place.timezone_hours,
        "config": {
            "observation_point": observation_point,
            "ayanamsha": ayanamsha,
        },
        "settings": {
            "observation_point": observation_point,
            "ayanamsha": ayanamsha,
        },
    }


def call_generic_endpoint(
    endpoint: str,
    api_key: str,
    payload: dict[str, Any],
) -> Any:
    normalized = endpoint.lstrip("/")
    url = f"{API_BASE}/{normalized}"
    LOGGER.info("Calling generic endpoint: %s", normalized)
    return api_post_json(url, payload, api_key)


def extract_planet_rows(response: Any) -> list[dict[str, Any]]:
    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]
    if isinstance(response, dict):
        for key in ("output", "data", "response", "result", "planets"):
            value = response.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def derive_house_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    houses: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        house_value = row.get("house")
        if house_value in (None, ""):
            house_key = "unknown"
        else:
            house_key = str(house_value)

        planet_name = (
            row.get("name")
            or row.get("planet")
            or row.get("planet_name")
            or row.get("full_name")
            or "unknown"
        )
        houses.setdefault(house_key, []).append(
            {
                "planet": planet_name,
                "sign": row.get("sign") or row.get("sign_name"),
                "house": house_value,
                "retrograde": row.get("retrograde"),
                "raw": row,
            }
        )

    ordered_houses = dict(sorted(houses.items(), key=lambda item: sort_house_key(item[0])))
    return {"houses": ordered_houses}


def sort_house_key(value: str) -> tuple[int, str]:
    try:
        return (0, f"{int(value):02d}")
    except ValueError:
        return (1, value)


def write_output(path: Path, svg: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    LOGGER.info("SVG written to %s", path)


def write_json_output(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    LOGGER.info("JSON written to %s", path)


def endpoint_output_filename(endpoint: str) -> str:
    return endpoint.strip("/").replace("/", "__") + ".json"


def main() -> int:
    args = parse_args()
    configure_logging(args.log_level)
    if args.list_endpoint_categories:
        print(json.dumps(documented_endpoint_categories(), indent=2, sort_keys=True))
        return 0

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(
            f"Missing API key. Set environment variable {args.api_key_env} first."
        )
    LOGGER.info("Starting FreeAstrologyAPI D1 helper")
    LOGGER.info("Subject: %s", args.name or "unnamed")
    LOGGER.info("Birth input: date=%s time=%s place=%s", args.date, args.time, args.place)

    year, month, day = normalize_date(args.date)
    hours, minutes, seconds = normalize_time(args.time)
    cache_path = Path(args.cache)

    manual_override_requested = any(
        value is not None for value in (args.latitude, args.longitude, args.timezone)
    )
    if manual_override_requested:
        if None in (args.latitude, args.longitude, args.timezone):
            raise SystemExit(
                "Manual override requires --latitude, --longitude, and --timezone together."
            )
        place = manual_place_resolution(
            place=args.place,
            latitude=args.latitude,
            longitude=args.longitude,
            timezone_hours=args.timezone,
            timezone_name=args.timezone_name,
        )
    else:
        place = resolve_place(args.place, api_key, cache_path, args.refresh_place)
    base_birth_payload = build_birth_payload(
        year=year,
        month=month,
        day=day,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        place=place,
        ayanamsha=args.ayanamsha,
        observation_point=args.observation_point,
    )
    extra_json = json.loads(args.extra_json) if args.extra_json else {}
    generic_payload = deep_merge(base_birth_payload, extra_json)

    svg = None
    planets_payload: dict[str, Any] | None = None
    planets_response: Any = None
    planet_rows: list[dict[str, Any]] = []
    house_summary = {"houses": {}}

    if not args.skip_default_endpoints:
        payload, svg = request_chart(
            api_key=api_key,
            year=year,
            month=month,
            day=day,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            place=place,
            ayanamsha=args.ayanamsha,
            observation_point=args.observation_point,
        )
        planets_payload, planets_response = request_planets(
            api_key=api_key,
            year=year,
            month=month,
            day=day,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            place=place,
            observation_point=args.observation_point,
        )
        planet_rows = extract_planet_rows(planets_response)
        house_summary = derive_house_summary(planet_rows)

    if args.print_request:
        LOGGER.info("Printing normalized birth request payload")
        print("GENERIC_BIRTH_PAYLOAD")
        print(json.dumps(generic_payload, indent=2, sort_keys=True))
        if not args.skip_default_endpoints and svg is not None and planets_payload is not None:
            print("REQUEST_PAYLOAD")
            print(json.dumps(payload, indent=2, sort_keys=True))
            print("PLANETS_REQUEST_PAYLOAD")
            print(json.dumps(planets_payload, indent=2, sort_keys=True))

    print("PLACE_RESOLUTION")
    print(
        json.dumps(
            {
                "query": place.query,
                "latitude": place.latitude,
                "longitude": place.longitude,
                "timezone_hours": place.timezone_hours,
                "timezone_name": place.timezone_name,
            },
            indent=2,
            sort_keys=True,
        )
    )

    if not args.skip_default_endpoints and svg is not None:
        svg_output = args.svg_output or args.output
        if svg_output:
            output_path = Path(svg_output)
            write_output(output_path, svg)
            print(f"SVG_SAVED {output_path}")
        else:
            LOGGER.info("Printing SVG preview")
            print("SVG_PREVIEW")
            print(svg[:800])

        print("PLANETS_SUMMARY")
        print(
            json.dumps(
                {
                    "planet_count": len(planet_rows),
                    "house_keys": list(house_summary["houses"].keys()),
                },
                indent=2,
                sort_keys=True,
            )
        )

        if args.planets_output and planets_response is not None:
            planets_output_path = Path(args.planets_output)
            write_json_output(planets_output_path, planets_response)
            print(f"PLANETS_JSON_SAVED {planets_output_path}")

        if args.houses_output:
            houses_output_path = Path(args.houses_output)
            write_json_output(houses_output_path, house_summary)
            print(f"HOUSES_JSON_SAVED {houses_output_path}")

    generic_endpoints = list(args.endpoint)
    if args.skip_default_endpoints and not generic_endpoints:
        raise SystemExit(
            "--skip-default-endpoints requires at least one --endpoint to be useful."
        )

    generic_results: dict[str, Any] = {}
    for endpoint in generic_endpoints:
        generic_results[endpoint] = call_generic_endpoint(
            endpoint=endpoint,
            api_key=api_key,
            payload=generic_payload,
        )

    if generic_results:
        print("GENERIC_ENDPOINT_RESULTS")
        print(
            json.dumps(
                {
                    "endpoints": list(generic_results.keys()),
                },
                indent=2,
                sort_keys=True,
            )
        )
        if args.output_dir:
            output_dir = Path(args.output_dir)
            for endpoint, response in generic_results.items():
                target = output_dir / endpoint_output_filename(endpoint)
                write_json_output(target, response)
                print(f"GENERIC_JSON_SAVED {target}")

    LOGGER.info("Completed successfully")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ApiError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
