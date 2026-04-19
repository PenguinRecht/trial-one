## Context

ComfyUI exposes a REST API: POST `/prompt` to queue a job, GET `/history/<id>` to poll, GET `/view` to download. Workflows are flat JSON dicts of numbered nodes with edge references. The target GPU has Flux.2 [dev] bf16 and Flux.1-dev-fp8 available.

## Goals / Non-Goals

**Goals:**
- Thin, dependency-light Python client (only `requests` + `python-dotenv`)
- Support Flux.2 (high-fidelity) and Flux.1-fp8 (fast draft) workflow variants
- Single `generate()` entry point that handles the full queue → poll → download lifecycle

**Non-Goals:**
- WebSocket / real-time progress streaming
- Local model loading or ComfyUI server management
- GUI or web interface

## Decisions

**Flat workflow builders over a graph abstraction** — ComfyUI's API format is already a flat dict; wrapping it in a node-graph class adds complexity with no practical benefit for a two-model pipeline.

**Polling over WebSockets** — simpler to implement and debug; 5 s poll interval is acceptable given generation times of 60–600 s.

**`generate()` as the primary API** — callers don't need to know about `queue_prompt` / `poll` / `download_outputs`; those are exposed for power users but not the main interface.

**Seed defaults to `time() % 2^32`** — reproducible when explicitly set, varied by default without requiring user input.

## Risks / Trade-offs

- Polling adds ~0–5 s latency per job; acceptable given job durations
- Workflow node IDs are hardcoded strings — adding new nodes requires careful numbering to avoid conflicts
