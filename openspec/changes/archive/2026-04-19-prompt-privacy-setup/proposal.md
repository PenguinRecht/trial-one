## Why

Image generation prompts are personal creative work and should not be committed to a public repository. A convention was needed to keep prompts local while still providing a clear structure for contributors.

## What Changes

- `prompts.json` is gitignored — the user's real prompts never leave their machine
- `prompts.example.json` is tracked — documents the expected prompt schema
- `generate_samples.py` loads `prompts.json` if present, falling back to minimal built-in samples
- `inputs/` directory gitignored for local reference images and source material
- `.env.example` added as a safe template for the endpoint configuration

## Capabilities

### New Capabilities
- `prompt-privacy`: Convention and tooling to keep prompts and personal assets off version control

### Modified Capabilities
<!-- None -->

## Impact

- `.gitignore` updated with `prompts.json`, `inputs/`, `.venv/`
- `generate_samples.py` updated with `load_prompts()` fallback logic
- New tracked files: `prompts.example.json`, `.env.example`
