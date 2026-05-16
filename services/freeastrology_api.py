from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


API_BASE = "https://json.freeastrologyapi.com"
DEFAULT_CACHE_PATH = Path(".cache/freeastrology_places.json")
LOGGER = logging.getLogger("freeastrology_api")
CHART_SVG_ENDPOINTS = {
    "d1": "horoscope-chart-svg-code",
    "d2": "hora-chart-svg-code",
    "d3": "drekkana-chart-svg-code",
    "d4": "chaturthamsa-chart-svg-code",
    "d5": "panchamasa-chart-svg-code",
    "d6": "d6-chart-svg-url",
    "d7": "d7-chart-svg-url",
    "d8": "d8-chart-svg-url",
    "d9": "navamsa-chart-svg-code",
    "d10": "d10-chart-svg-url",
    "d11": "d11-chart-svg-url",
    "d12": "d12-chart-svg-url",
    "d16": "d16-chart-svg-url",
    "d20": "d20-chart-svg-url",
    "d24": "d24-chart-svg-url",
    "d27": "d27-chart-svg-url",
    "d30": "d30-chart-svg-url",
    "d40": "d40-chart-svg-url",
    "d45": "d45-chart-svg-url",
    "d60": "d60-chart-svg-url",
}


class FreeAstrologyApiError(RuntimeError):
    pass


class FreeAstrologyApiClient:
    def __init__(
        self,
        api_key: str | None = None,
        cache_path: Path | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("ASTROLOGY_API_KEY")
        if not self.api_key:
            raise FreeAstrologyApiError(
                "Missing API key. Set ASTROLOGY_API_KEY in the environment."
            )
        self.cache_path = cache_path or DEFAULT_CACHE_PATH

    def load_cache(self) -> dict[str, Any]:
        if not self.cache_path.exists():
            LOGGER.debug("Cache file does not exist yet: %s", self.cache_path)
            return {}
        LOGGER.debug("Loading cache from %s", self.cache_path)
        with self.cache_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save_cache(self, cache: dict[str, Any]) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        LOGGER.debug("Saving cache to %s", self.cache_path)
        with self.cache_path.open("w", encoding="utf-8") as handle:
            json.dump(cache, handle, indent=2, sort_keys=True)
            handle.write("\n")

    def post_json(self, endpoint: str, payload: dict[str, Any]) -> Any:
        normalized = endpoint.lstrip("/")
        url = f"{API_BASE}/{normalized}"
        LOGGER.info("POST %s", url)
        LOGGER.debug("Request payload: %s", json.dumps(payload, sort_keys=True))
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
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
            raise FreeAstrologyApiError(
                f"HTTP {exc.code} from {url}: {error_body}"
            ) from exc
        except urllib.error.URLError as exc:
            LOGGER.error("Request to %s failed: %s", url, exc.reason)
            raise FreeAstrologyApiError(f"Request to {url} failed: {exc.reason}") from exc

    @staticmethod
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

    @staticmethod
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
                found = FreeAstrologyApiClient.extract_first_float(value, keys)
                if found is not None:
                    return found
        elif isinstance(container, list):
            for item in container:
                found = FreeAstrologyApiClient.extract_first_float(item, keys)
                if found is not None:
                    return found
        return None

    @staticmethod
    def extract_first_text(container: Any, keys: list[str]) -> str | None:
        if isinstance(container, dict):
            for key in keys:
                value = container.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
            for value in container.values():
                found = FreeAstrologyApiClient.extract_first_text(value, keys)
                if found is not None:
                    return found
        elif isinstance(container, list):
            for item in container:
                found = FreeAstrologyApiClient.extract_first_text(item, keys)
                if found is not None:
                    return found
        return None

    def resolve_place(self, place: str, refresh: bool = False) -> dict[str, Any]:
        LOGGER.info("Resolving place: %s", place)
        cache = self.load_cache()
        cache_key = place.strip().lower()
        if not refresh and cache_key in cache:
            LOGGER.info("Using cached place resolution for %s", place)
            return cache[cache_key]

        candidates = self.build_location_candidates(place)
        last_response: Any = None
        for candidate in candidates:
            LOGGER.info("Trying geo-details candidate: %s", candidate)
            response = self.post_json("geo-details", {"location": candidate})
            last_response = response
            latitude = self.extract_first_float(response, ["latitude", "lat"])
            longitude = self.extract_first_float(response, ["longitude", "lng", "lon"])
            timezone_hours = self.extract_first_float(
                response,
                ["timezone_offset", "timezoneOffset", "tz_offset", "tz", "timezone"],
            )
            timezone_name = self.extract_first_text(
                response,
                [
                    "timezone",
                    "timezone_name",
                    "timezoneName",
                    "timezone_id",
                    "timezoneId",
                    "iana_timezone",
                ],
            )
            if latitude is not None and longitude is not None and timezone_hours is not None:
                resolved = {
                    "query": candidate,
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone_hours": timezone_hours,
                    "timezone_name": timezone_name,
                    "raw": response,
                }
                cache[cache_key] = resolved
                self.save_cache(cache)
                LOGGER.info(
                    "Resolved %s to lat=%s lon=%s timezone=%s",
                    candidate,
                    latitude,
                    longitude,
                    timezone_hours,
                )
                return resolved

        raise FreeAstrologyApiError(
            "Could not extract latitude/longitude/timezone from geo-details response. "
            f"Tried candidates={candidates}. Last response={json.dumps(last_response, indent=2)}"
        )

    @staticmethod
    def build_birth_payload(
        *,
        year: int,
        month: int,
        day: int,
        hours: int,
        minutes: int,
        seconds: int,
        latitude: float,
        longitude: float,
        timezone: float,
        ayanamsha: str = "lahiri",
        observation_point: str = "topocentric",
    ) -> dict[str, Any]:
        return {
            "year": year,
            "month": month,
            "date": day,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "config": {
                "observation_point": observation_point,
                "ayanamsha": ayanamsha,
            },
            "settings": {
                "observation_point": observation_point,
                "ayanamsha": ayanamsha,
            },
        }

    def fetch_chart_svg(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.post_json("horoscope-chart-svg-code", payload)

    def fetch_chart_svg_by_type(
        self,
        payload: dict[str, Any],
        chart_type: str,
    ) -> dict[str, Any]:
        normalized = chart_type.strip().lower()
        if normalized == "all":
            results: dict[str, Any] = {}
            for key, endpoint in CHART_SVG_ENDPOINTS.items():
                LOGGER.info("Fetching chart type %s via %s", key, endpoint)
                results[key] = {
                    "vendor_endpoint": endpoint,
                    "response": self.post_json(endpoint, payload),
                }
            return {
                "chart_type": "all",
                "results": results,
            }

        endpoint = CHART_SVG_ENDPOINTS.get(normalized)
        if not endpoint:
            raise FreeAstrologyApiError(
                f"Unsupported chart_type '{chart_type}'. Supported values: "
                f"{', '.join(sorted(CHART_SVG_ENDPOINTS))}, all"
            )
        LOGGER.info("Fetching chart type %s via %s", normalized, endpoint)
        return {
            "chart_type": normalized,
            "vendor_endpoint": endpoint,
            "response": self.post_json(endpoint, payload),
        }

    def fetch_planets(self, payload: dict[str, Any]) -> Any:
        planets_payload = {
            "year": payload["year"],
            "month": payload["month"],
            "date": payload["date"],
            "hours": payload["hours"],
            "minutes": payload["minutes"],
            "seconds": payload["seconds"],
            "latitude": payload["latitude"],
            "longitude": payload["longitude"],
            "timezone": payload["timezone"],
            "observation_point": payload.get("settings", {}).get(
                "observation_point", "topocentric"
            ),
        }
        return self.post_json("planets", planets_payload)

    def fetch_generic(self, endpoint: str, payload: dict[str, Any]) -> Any:
        return self.post_json(endpoint, payload)

    @staticmethod
    def extract_planet_rows(response: Any) -> list[dict[str, Any]]:
        if isinstance(response, list):
            return [item for item in response if isinstance(item, dict)]
        if isinstance(response, dict):
            for key in ("output", "data", "response", "result", "planets"):
                value = response.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
        return []

    @classmethod
    def derive_house_summary(cls, response: Any) -> dict[str, Any]:
        rows = cls.extract_planet_rows(response)
        houses: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            house_value = row.get("house")
            house_key = "unknown" if house_value in (None, "") else str(house_value)
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
        ordered = dict(sorted(houses.items(), key=lambda item: cls.sort_house_key(item[0])))
        return {"houses": ordered}

    @staticmethod
    def sort_house_key(value: str) -> tuple[int, str]:
        try:
            return (0, f"{int(value):02d}")
        except ValueError:
            return (1, value)
