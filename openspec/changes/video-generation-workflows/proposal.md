## Why

The pipeline currently only generates still images. The DGX Spark has two local video models ready to use — LTX-V 13B distilled fp8 and Wan 2.2 14B T2V (high-noise and low-noise variants) — and the `generate()` interface needs to support them so animated art can be produced without manual ComfyUI workflow configuration.

## What Changes

- Add `ltxv_workflow()` builder — text-to-video using LTX-V 13B distilled fp8 via `UNETLoader` + `LTXVScheduler` + `SamplerCustomAdvanced`
- Add `wan_workflow()` builder — text-to-video using Wan 2.2 14B fp8 (selectable high-noise / low-noise variant) via `UNETLoader` + `umt5_xxl` CLIP + wan VAE
- Extend `generate()` to accept `model="ltxv"` and `model="wan"` and route to the new builders
- Add `frames` and `fps` parameters to `generate()` for video length control
- Download outputs as video files (`.mp4` / `.webp`) alongside the existing image path

## Capabilities

### New Capabilities
- `video-workflow-builders`: Workflow dict builders for LTX-V and Wan 2.2 local video models

### Modified Capabilities
- `workflow-builders`: `generate()` gains `model="ltxv"` and `model="wan"` routing, plus `frames` and `fps` params
- `generation-cli`: `--model` flag extended to include `ltxv` and `wan` choices

## Impact

- `comfy_client.py` — new workflow builder functions, updated `generate()`
- `generate_samples.py` — `--model` choices updated
- No new dependencies
