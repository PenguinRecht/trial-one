## Why

The project needed a reproducible, scriptable way to generate images from a remote ComfyUI instance running on a GPU server, without requiring a browser or manual workflow configuration each time.

## What Changes

- Introduce a Python client library (`comfy_client.py`) that wraps the ComfyUI REST API
- Introduce a CLI generation script (`generate_samples.py`) for batch image generation
- Add `requirements.txt` and `.venv` Python environment support
- Add `.gitignore` to exclude secrets, outputs, and environment files

## Capabilities

### New Capabilities
- `comfyui-client`: HTTP client for ComfyUI — queues prompts, polls completion, downloads outputs
- `workflow-builders`: Composable workflow dict builders for Flux.2 and Flux.1-fp8 models
- `generation-cli`: CLI wrapper that loads prompts and drives generation end-to-end

### Modified Capabilities
<!-- None -->

## Impact

- New files: `comfy_client.py`, `generate_samples.py`, `requirements.txt`
- Runtime dependency on a reachable ComfyUI endpoint (configured via `.env`)
- Outputs written to `outputs/` (gitignored)
