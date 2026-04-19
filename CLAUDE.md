# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

Python venv at `.venv/`. Always use `.venv/bin/python` / `.venv/bin/pip`.

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

The remote ComfyUI endpoint is in `.env` (gitignored). Load it via `python-dotenv` or export before running.

## Running generations

```bash
# All prompts in prompts.json (gitignored, user's private descriptions)
python generate_samples.py

# Single model or fixed seed
python generate_samples.py --model flux2 --seed 1234 --steps 25
```

## Architecture

Two files, no framework:

- **`comfy_client.py`** — all network logic. `generate()` is the main entry point: builds a workflow dict, POSTs to `/prompt`, polls `/history/<id>` until done, downloads files to `outputs/`. Also exposes `health()`, `queue_prompt()`, `poll()`, `download_outputs()` for lower-level use.
- **`generate_samples.py`** — CLI wrapper. Loads `prompts.json` if present, otherwise falls back to `BUILTIN_SAMPLES`. Calls `generate()` for each entry.

## Workflow format

ComfyUI uses a node graph serialized as a flat JSON dict (`"1"`, `"2"`, … node IDs). Edges are `["node_id", output_index]` references. Two workflow builders live in `comfy_client.py`:

- `flux2_workflow()` — Flux.2 [dev] bf16 via `UNETLoader` + `CLIPLoader(type="flux2")` + `VAELoader` + `BasicGuider` + `SamplerCustomAdvanced`
- `flux1_fast_workflow()` — Flux.1-dev-fp8 via `CheckpointLoaderSimple` + `KSampler`

## What stays off GitHub

| Path | Contents |
|------|----------|
| `.env` | `COMFYUI_BASE_URL` |
| `prompts.json` | User's image descriptions |
| `outputs/` | Generated images |
| `.venv/` | Python environment |

Templates: `.env.example`, `prompts.example.json`.
