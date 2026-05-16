from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from services.freeastrology_api import FreeAstrologyApiClient, FreeAstrologyApiError
from services.transcript_acquisition import (
    TranscriptAcquisitionService,
    TranscriptProcessingService,
)
from services.transcript_acquisition.jobs import JsonFileJobStore
from services.transcript_acquisition.models import (
    ManualUpload,
    TranscriptAcquisitionJob,
    TranscriptAcquisitionResult,
    TranscriptProcessingResult,
    TranscriptSourceType,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


class ResolvePlaceRequest(BaseModel):
    place: str = Field(..., examples=["Sonipat, Haryana, India"])
    refresh: bool = False


class BirthInput(BaseModel):
    year: int
    month: int
    date: int
    hours: int
    minutes: int
    seconds: int = 0
    latitude: float
    longitude: float
    timezone: float
    ayanamsha: str = "lahiri"
    observation_point: str = "topocentric"
    chart_type: str = Field(
        default="d1",
        description="Normalized chart type such as d1, d9, d10, d60, or all.",
    )


class GenericEndpointRequest(BirthInput):
    extra: dict[str, Any] = Field(default_factory=dict)


class ApiEnvelope(BaseModel):
    ok: bool
    data: Any


class TranscriptYoutubeRequest(BaseModel):
    source: str = Field(
        ...,
        description="YouTube URL or 11-character video ID.",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )
    job_id: str | None = Field(default=None, alias="jobId")


class TranscriptManualPasteRequest(BaseModel):
    text: str
    source_url: str | None = Field(default=None, alias="sourceUrl")
    video_id: str | None = Field(default=None, alias="videoId")
    job_id: str | None = Field(default=None, alias="jobId")


class TranscriptManualUploadRequest(BaseModel):
    file_name: str = Field(alias="fileName")
    content: str
    mime_type: str | None = Field(default=None, alias="mimeType")
    source_url: str | None = Field(default=None, alias="sourceUrl")
    video_id: str | None = Field(default=None, alias="videoId")
    job_id: str | None = Field(default=None, alias="jobId")


class TranscriptProcessRequest(BaseModel):
    raw_transcript_text: str = Field(alias="rawTranscriptText")
    source_type: TranscriptSourceType | None = Field(default=None, alias="sourceType")
    source_url: str | None = Field(default=None, alias="sourceUrl")
    video_id: str | None = Field(default=None, alias="videoId")
    max_chunk_chars: int = Field(default=1200, alias="maxChunkChars")


def build_payload(birth: BirthInput) -> dict[str, Any]:
    return FreeAstrologyApiClient.build_birth_payload(
        year=birth.year,
        month=birth.month,
        day=birth.date,
        hours=birth.hours,
        minutes=birth.minutes,
        seconds=birth.seconds,
        latitude=birth.latitude,
        longitude=birth.longitude,
        timezone=birth.timezone,
        ayanamsha=birth.ayanamsha,
        observation_point=birth.observation_point,
    )


def get_freeastrology_client() -> FreeAstrologyApiClient:
    client = getattr(app.state, "client", None)
    if client is None:
        client = FreeAstrologyApiClient()
        app.state.client = client
    return client


def get_transcript_service() -> TranscriptAcquisitionService:
    service = getattr(app.state, "transcript_service", None)
    if service is None:
        service = TranscriptAcquisitionService(
            job_store=JsonFileJobStore(),
        )
        app.state.transcript_service = service
    return service


def get_transcript_processing_service() -> TranscriptProcessingService:
    service = getattr(app.state, "transcript_processing_service", None)
    if service is None:
        service = TranscriptProcessingService()
        app.state.transcript_processing_service = service
    return service


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = None
    app.state.transcript_service = None
    app.state.transcript_processing_service = None
    yield


app = FastAPI(
    title="ARIP Platform API",
    version="0.1.0",
    summary="Local FastAPI surface for ARIP platform services and integrations",
    lifespan=lifespan,
)


@app.get("/health", response_model=ApiEnvelope)
async def health() -> ApiEnvelope:
    return ApiEnvelope(ok=True, data={"status": "ok"})


@app.post("/transcripts/acquire/youtube", response_model=ApiEnvelope)
async def transcript_acquire_youtube(request: TranscriptYoutubeRequest) -> ApiEnvelope:
    try:
        result = get_transcript_service().acquire_youtube(
            request.source,
            job_id=request.job_id,
        )
        return ApiEnvelope(ok=True, data=result.model_dump(by_alias=True, mode="json"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/transcripts/acquire/manual-paste", response_model=ApiEnvelope)
async def transcript_acquire_manual_paste(
    request: TranscriptManualPasteRequest,
) -> ApiEnvelope:
    result = get_transcript_service().acquire_manual_paste(
        request.text,
        source_url=request.source_url,
        video_id=request.video_id,
        job_id=request.job_id,
    )
    return ApiEnvelope(ok=True, data=result.model_dump(by_alias=True, mode="json"))


@app.post("/transcripts/acquire/manual-upload", response_model=ApiEnvelope)
async def transcript_acquire_manual_upload(
    request: TranscriptManualUploadRequest,
) -> ApiEnvelope:
    result = get_transcript_service().acquire_manual_upload(
        ManualUpload(
            fileName=request.file_name,
            content=request.content,
            mimeType=request.mime_type,
        ),
        source_url=request.source_url,
        video_id=request.video_id,
        job_id=request.job_id,
    )
    return ApiEnvelope(ok=True, data=result.model_dump(by_alias=True, mode="json"))


@app.post("/transcripts/process", response_model=ApiEnvelope)
async def transcript_process(request: TranscriptProcessRequest) -> ApiEnvelope:
    try:
        result = get_transcript_processing_service().process_text(
            request.raw_transcript_text,
            source_type=request.source_type,
            source_url=request.source_url,
            video_id=request.video_id,
            max_chunk_chars=request.max_chunk_chars,
        )
        return ApiEnvelope(ok=True, data=result.model_dump(by_alias=True, mode="json"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/transcripts/jobs/{job_id}", response_model=ApiEnvelope)
async def transcript_job(job_id: str) -> ApiEnvelope:
    job = get_transcript_service().job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Transcript job not found: {job_id}")
    return ApiEnvelope(ok=True, data=job.model_dump(by_alias=True, mode="json"))


@app.post("/resolve-place", response_model=ApiEnvelope)
async def resolve_place(request: ResolvePlaceRequest) -> ApiEnvelope:
    try:
        data = get_freeastrology_client().resolve_place(
            request.place,
            refresh=request.refresh,
        )
        return ApiEnvelope(ok=True, data=data)
    except FreeAstrologyApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/chart/svg", response_model=ApiEnvelope)
async def chart_svg(request: BirthInput) -> ApiEnvelope:
    try:
        payload = build_payload(request)
        data = get_freeastrology_client().fetch_chart_svg_by_type(
            payload,
            request.chart_type,
        )
        return ApiEnvelope(ok=True, data=data)
    except FreeAstrologyApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/planets", response_model=ApiEnvelope)
async def planets(request: BirthInput) -> ApiEnvelope:
    try:
        payload = build_payload(request)
        data = get_freeastrology_client().fetch_planets(payload)
        return ApiEnvelope(ok=True, data=data)
    except FreeAstrologyApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/houses", response_model=ApiEnvelope)
async def houses(request: BirthInput) -> ApiEnvelope:
    try:
        payload = build_payload(request)
        client = get_freeastrology_client()
        planets_response = client.fetch_planets(payload)
        data = client.derive_house_summary(planets_response)
        return ApiEnvelope(ok=True, data=data)
    except FreeAstrologyApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/vendor/{endpoint:path}", response_model=ApiEnvelope)
async def vendor_endpoint(endpoint: str, request: GenericEndpointRequest) -> ApiEnvelope:
    try:
        payload = build_payload(request)
        if request.extra:
            payload.update(request.extra)
        data = get_freeastrology_client().fetch_generic(endpoint, payload)
        return ApiEnvelope(ok=True, data=data)
    except FreeAstrologyApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
