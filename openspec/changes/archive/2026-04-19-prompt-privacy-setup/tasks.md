## 1. Gitignore Updates

- [x] 1.1 Add `prompts.json` to `.gitignore`
- [x] 1.2 Add `inputs/` to `.gitignore`
- [x] 1.3 Create `inputs/` directory locally

## 2. Prompt Loading

- [x] 2.1 Extract `BUILTIN_SAMPLES` as minimal fallback in `generate_samples.py`
- [x] 2.2 Implement `load_prompts()` — loads `prompts.json` if present, otherwise uses `BUILTIN_SAMPLES` with a clear console message

## 3. Reference Templates

- [x] 3.1 Create `prompts.example.json` with documented schema
- [x] 3.2 Create `.env.example` with placeholder endpoint URL
