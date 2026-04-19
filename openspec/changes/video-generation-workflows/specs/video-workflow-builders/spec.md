## ADDED Requirements

### Requirement: LTX-V text-to-video workflow builder
The module SHALL provide `ltxv_workflow()` returning a ComfyUI API-format dict using UNETLoader (ltxv-13b-0.9.8-distilled-fp8.safetensors), LTXVScheduler, EmptyLTXVLatentVideo, and SamplerCustomAdvanced nodes.

#### Scenario: Default parameters
- **WHEN** `ltxv_workflow(prompt)` is called with only a prompt
- **THEN** it returns a valid workflow dict with defaults of 768×512, 25 frames, 24 fps, 20 steps

#### Scenario: Custom frames and fps
- **WHEN** `frames` and `fps` are specified
- **THEN** the workflow dict reflects those values in the scheduler and latent nodes

#### Scenario: Reproducible seed
- **WHEN** an explicit `seed` is passed
- **THEN** the RandomNoise node uses exactly that seed value

### Requirement: Wan 2.2 text-to-video workflow builder
The module SHALL provide `wan_workflow()` returning a ComfyUI API-format dict using UNETLoader (selectable high-noise or low-noise variant), umt5_xxl CLIP, and wan_2.1_vae.safetensors.

#### Scenario: High-noise variant selected
- **WHEN** `wan_workflow(prompt, noise="high")` is called
- **THEN** the UNETLoader targets `wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors`

#### Scenario: Low-noise variant selected
- **WHEN** `wan_workflow(prompt, noise="low")` is called
- **THEN** the UNETLoader targets `wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors`

#### Scenario: Default noise variant
- **WHEN** `wan_workflow(prompt)` is called without a noise kwarg
- **THEN** the high-noise variant is used

#### Scenario: Frame count enforced
- **WHEN** a `frames` value not satisfying the model constraint (multiple of 4 + 1) is passed
- **THEN** the builder rounds up to the nearest valid value

#### Scenario: Default frames
- **WHEN** `wan_workflow(prompt)` is called without `frames`
- **THEN** the workflow uses 81 frames at 16 fps
