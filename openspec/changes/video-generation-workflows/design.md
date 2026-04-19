## Context

The existing `comfy_client.py` has two workflow builders (`flux2_workflow`, `flux1_fast_workflow`) and a `generate()` dispatcher. Both video models are available as UNETs on the Spark:

- **LTX-V 13B distilled fp8** — uses `LTXVScheduler` + `SamplerCustomAdvanced` pipeline (same sampler chain as Flux.2 but with the LTXV scheduler). Supports `EmptyLTXVLatentVideo` for sizing. Native frame count and fps control.
- **Wan 2.2 14B T2V fp8** — two UNET variants: `wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors` (better dynamics/motion) and `wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors` (cleaner/controlled motion). Uses `umt5_xxl_fp8_e4m3fn_scaled.safetensors` CLIP and `wan_2.1_vae.safetensors`.

## Goals / Non-Goals

**Goals:**
- Text-to-video for both LTX-V and Wan 2.2 via the existing `generate()` interface
- `frames` and `fps` parameters for video length/rate control
- Selectable Wan noise variant (`high` / `low`) via a kwarg
- Video files saved to `outputs/` alongside images

**Non-Goals:**
- Image-to-video (separate change)
- Audio-driven video (Wan sound nodes)
- Camera-control or motion-track nodes
- Cloud API video services (Kling, Runway, etc.)

## Decisions

**Reuse `SamplerCustomAdvanced` for LTX-V** — LTX-V uses the same advanced sampler chain as Flux.2 (noise → guider → sampler → sigmas → latent). Only the scheduler and latent node differ, so the builder follows the same pattern.

**`model="wan"` with `noise="high"|"low"` kwarg** — rather than exposing `model="wan-high"` and `model="wan-low"` as separate model strings, a single `wan` model with a `noise` kwarg keeps the interface clean and mirrors the on-disk naming convention.

**`frames` defaults: LTX-V=25, Wan=81** — LTX-V distilled works well at shorter clips; Wan 2.2's default is 81 frames (~3 s at 24 fps). Both are overridable.

**No new top-level dependencies** — video output from ComfyUI's `SaveAnimatedWEBP` / `VHS_VideoCombine` or equivalent is downloaded via the same `/view` endpoint. No `ffmpeg` or video library needed client-side.

## Risks / Trade-offs

- Wan 2.2 14B at full quality is slow (~several minutes per clip on GB10); the CLI should print a clear progress message
- `frames` counts must satisfy model-specific step constraints (Wan requires multiples of 4 + 1); builders should enforce this
- LTX-V node names (`LTXVScheduler`, `EmptyLTXVLatentVideo`, `ModelSamplingLTXV`) need to be verified against `/object_info` before finalising — node names noted from the live instance inspection
