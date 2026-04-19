## ADDED Requirements

### Requirement: Run all prompts from file or built-ins
The CLI SHALL load prompts from `prompts.json` if present, otherwise fall back to `BUILTIN_SAMPLES`, and call `generate()` for each entry.

#### Scenario: prompts.json present
- **WHEN** `generate_samples.py` is run and `prompts.json` exists
- **THEN** all entries in `prompts.json` are generated in order

#### Scenario: No prompts.json
- **WHEN** `generate_samples.py` is run without a `prompts.json`
- **THEN** built-in sample prompts are used and a message is printed indicating the fallback

### Requirement: Filter by model flag
The CLI SHALL accept `--model flux2|flux1|all` and skip prompts not matching the selected model.

#### Scenario: Model filter applied
- **WHEN** `--model flux2` is passed
- **THEN** only entries with `"model": "flux2"` are generated

### Requirement: Override steps and seed
The CLI SHALL accept `--steps` and `--seed` flags that override per-prompt values for the entire run.

#### Scenario: Steps override
- **WHEN** `--steps 30` is passed
- **THEN** all prompts use 30 steps regardless of their individual setting

### Requirement: Print GPU health at startup
The CLI SHALL call `health()` and print GPU name and free VRAM before any generation begins.

#### Scenario: Health check success
- **WHEN** the CLI starts
- **THEN** GPU name and VRAM stats are printed before the first generation
