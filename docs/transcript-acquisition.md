# Transcript Acquisition Service

This module implements the DEV-39 / DEV-44 transcript acquisition slice.

## Scope

Implemented:

- YouTube URL or video ID input.
- Primary automated path through `youtube-transcript-api`.
- Fallback automated path through `yt-dlp` caption metadata/download.
- Manual admin paste.
- Manual admin upload for `.txt`, `.vtt`, and `.srt`.
- Structured acquisition attempts and copyright metadata defaults.
- Job-state scaffold with in-memory and JSON-file stores.

Not implemented in this slice:

- Remedy extraction.
- Knowledge graph updates.
- Paid transcript APIs.
- ASR/audio transcription.
- Full admin UI.

## Local Setup

Install dependencies into the local virtualenv:

```bash
.venv/bin/python -m pip install -r requirements-freeastrologyapi.txt
```

Run the targeted tests:

```bash
.venv/bin/python -m pytest tests/test_transcript_acquisition.py
```

Run the FastAPI app:

```bash
.venv/bin/uvicorn app:app --reload
```

Open docs:

```text
http://127.0.0.1:8000/docs
```

## HTTP Endpoints

### POST `/transcripts/acquire/youtube`

Request body:

```json
{
  "source": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

Optional `jobId` lets you continue an existing job.

### POST `/transcripts/acquire/manual-paste`

Request body:

```json
{
  "text": "Transcript pasted by admin",
  "sourceUrl": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "videoId": "dQw4w9WgXcQ"
}
```

### POST `/transcripts/acquire/manual-upload`

This is JSON-based for now, so the file content is sent as text.

Request body:

```json
{
  "fileName": "sample.vtt",
  "content": "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nHello world",
  "mimeType": "text/vtt",
  "sourceUrl": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "videoId": "dQw4w9WgXcQ"
}
```

### GET `/transcripts/jobs/{job_id}`

Returns stored job state from the JSON-backed job store.

### POST `/transcripts/process`

Turns raw transcript text into normalized text and deterministic chunks for
downstream extraction.

Request body:

```json
{
  "rawTranscriptText": "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nChant the mantra with attention.",
  "sourceType": "manual-paste",
  "sourceUrl": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "videoId": "dQw4w9WgXcQ",
  "maxChunkChars": 1200
}
```

Response data includes:

- `cleanedText`
- `chunks[]`
- `chunks[].sourceStartChar`
- `chunks[].sourceEndChar`
- `metadata.rules[]`

## Cleaning And Chunking Rules

The DEV-40 processing layer is deterministic and does not use LangChain,
LangGraph, LLM calls, or a vector database.

Cleaning rules:

- Convert Windows and classic Mac line endings to Unix newlines.
- Trim each kept line and collapse repeated inline whitespace.
- Drop standalone timestamps, caption sequence numbers, WEBVTT headers, and
  simple sound markers such as `[Music]`.
- Collapse repeated blank lines into paragraph boundaries.
- Drop consecutive duplicate spoken lines after normalization.

Chunking rules:

- Preserve source order.
- Build chunks up to `maxChunkChars`; default is `1200`, minimum is `300`.
- Prefer paragraph and line boundaries.
- Split unusually long lines on sentence boundaries when possible.
- Assign stable sequence-based chunk IDs.
- Preserve source traceability with raw transcript character spans on every
  chunk.

## Python Usage

```python
from services.transcript_acquisition import (
    TranscriptAcquisitionService,
    TranscriptProcessingService,
)

service = TranscriptAcquisitionService()
result = service.acquire_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

if result.metadata.acquisition_outcome == "manual-required":
    result = service.acquire_manual_paste(
        "Transcript pasted by admin...",
        source_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        video_id="dQw4w9WgXcQ",
    )

processed = TranscriptProcessingService().process_acquisition_result(result)
```

By default, automated acquisition creates structured job state. For durable local
state, pass `JsonFileJobStore`; the default service store is in-memory for simple
embedding and tests.
