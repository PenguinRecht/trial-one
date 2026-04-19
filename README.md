# Animation Pipeline

A Python client for generating animated art via [ComfyUI](https://github.com/comfyanonymous/ComfyUI) running on a remote DGX Spark GPU.

## Models

| Model | Use case | Speed |
|-------|----------|-------|
| `flux2` | High-fidelity stills, graphic novel panels | ~185 s / 1024×1024 @ 20 steps |
| `flux1` | Draft keyframes, puppet/claymation sketches | Faster |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` and fill in your endpoint:

```bash
cp .env.example .env   # then edit COMFYUI_BASE_URL
```

## Your prompts

Your prompts live in a local `prompts.json` that is **never committed to git**.

```bash
cp prompts.example.json prompts.json
# edit prompts.json with your own descriptions
```

See [`prompts.example.json`](prompts.example.json) for the schema.

## Generate images

```bash
# Run all prompts in prompts.json
python generate_samples.py

# Only flux2 prompts, fixed seed
python generate_samples.py --model flux2 --seed 1234

# Override step count
python generate_samples.py --steps 30
```

Outputs are saved to `outputs/` (also gitignored).

## Use the client directly

```python
from comfy_client import generate

generate(
    "A misty highland loch at dawn, oil painting style",
    model="flux2",
    width=1280,
    height=768,
    steps=25,
)
```

## What stays off GitHub

| Path | Contents |
|------|----------|
| `.env` | Endpoint URL |
| `prompts.json` | Your image descriptions |
| `outputs/` | Generated images |
| `.venv/` | Python environment |
