## ADDED Requirements

### Requirement: Flux.2 workflow builder
The module SHALL provide `flux2_workflow()` returning a ComfyUI API-format dict using UNETLoader, CLIPLoader (type=flux2), VAELoader, BasicGuider, and SamplerCustomAdvanced nodes.

#### Scenario: Default parameters
- **WHEN** `flux2_workflow(prompt)` is called with only a prompt
- **THEN** it returns a dict with node keys "1"–"12" and defaults of 1024×1024, 20 steps

#### Scenario: Custom dimensions and steps
- **WHEN** `width`, `height`, and `steps` are specified
- **THEN** the workflow dict reflects those values in the appropriate nodes

#### Scenario: Reproducible seed
- **WHEN** an explicit `seed` is passed
- **THEN** node "8" (`RandomNoise`) uses exactly that seed value

### Requirement: Flux.1-fp8 fast workflow builder
The module SHALL provide `flux1_fast_workflow()` returning a ComfyUI API-format dict using CheckpointLoaderSimple and KSampler nodes.

#### Scenario: Default parameters
- **WHEN** `flux1_fast_workflow(prompt)` is called with only a prompt
- **THEN** it returns a dict targeting `flux1-dev-fp8.safetensors` with cfg=1.0

### Requirement: High-level generate entry point
The module SHALL provide `generate()` which selects the correct workflow builder, queues the job, polls to completion, and downloads outputs.

#### Scenario: Model selection flux2
- **WHEN** `generate(prompt, model="flux2")` is called
- **THEN** a Flux.2 workflow is used and files are saved to `outputs/`

#### Scenario: Model selection flux1
- **WHEN** `generate(prompt, model="flux1")` is called
- **THEN** a Flux.1-fp8 workflow is used and files are saved to `outputs/`

#### Scenario: Unknown model
- **WHEN** an unrecognised `model` string is passed
- **THEN** a `ValueError` is raised
