## Context

The generation script originally had prompts hardcoded in `BUILTIN_SAMPLES`. These needed to be moved to a local file so users can maintain their own creative descriptions without risk of committing them.

## Goals / Non-Goals

**Goals:**
- Zero-friction local prompts: drop a `prompts.json` and it just works
- Safe fallback so the repo runs out of the box without any `prompts.json`
- Gitignore `inputs/` for reference images and source material

**Non-Goals:**
- Encrypted or remote secret storage
- Per-prompt access control

## Decisions

**`prompts.json` over a Python file** — JSON is easier to edit without coding knowledge and trivially machine-readable; no import or syntax risk.

**Fallback to `BUILTIN_SAMPLES`** — lets a fresh clone run immediately and serves as a live smoke test of the pipeline without requiring any setup.

**`inputs/` gitignored as a directory convention** — keeps reference images, masks, and LoRA inputs local alongside prompts without needing per-file gitignore rules.

## Risks / Trade-offs

- If a user accidentally names their file something other than `prompts.json` it will silently use built-ins; the startup message makes this visible
