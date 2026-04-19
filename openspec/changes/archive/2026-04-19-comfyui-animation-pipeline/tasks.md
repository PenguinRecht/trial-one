## 1. Project Scaffolding

- [x] 1.1 Create `.gitignore` excluding `.env`, `outputs/`, `.venv/`
- [x] 1.2 Create `requirements.txt` with `requests` and `python-dotenv`
- [x] 1.3 Set up `.venv` Python environment

## 2. ComfyUI Client Library

- [x] 2.1 Implement `health()` — GET `/system_stats`
- [x] 2.2 Implement `queue_prompt()` — POST `/prompt`, return `prompt_id`
- [x] 2.3 Implement `poll()` — GET `/history/<id>` until `status_str == "success"` or timeout
- [x] 2.4 Implement `download_outputs()` — GET `/view` for each image, save to `outputs/`
- [x] 2.5 Implement `flux2_workflow()` builder — UNETLoader + CLIPLoader(flux2) + VAELoader + BasicGuider + SamplerCustomAdvanced
- [x] 2.6 Implement `flux1_fast_workflow()` builder — CheckpointLoaderSimple + KSampler
- [x] 2.7 Implement `generate()` — high-level entry point combining all of the above

## 3. Generation CLI

- [x] 3.1 Implement `generate_samples.py` with `--model`, `--steps`, `--seed` flags
- [x] 3.2 Print GPU health summary at startup
- [x] 3.3 Validate pipeline end-to-end with sample prompts (cyberpunk alley, clay robot, bioluminescent forest)
