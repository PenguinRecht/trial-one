## MODIFIED Requirements

### Requirement: High-level generate entry point
The module SHALL provide `generate()` which selects the correct workflow builder, queues the job, polls to completion, and downloads outputs. Accepted `model` values are `"flux2"`, `"flux1"`, `"ltxv"`, and `"wan"`. Video generations accept `frames`, `fps`, and `noise` kwargs.

#### Scenario: Model selection flux2
- **WHEN** `generate(prompt, model="flux2")` is called
- **THEN** a Flux.2 workflow is used and image files are saved to `outputs/`

#### Scenario: Model selection flux1
- **WHEN** `generate(prompt, model="flux1")` is called
- **THEN** a Flux.1-fp8 workflow is used and image files are saved to `outputs/`

#### Scenario: Model selection ltxv
- **WHEN** `generate(prompt, model="ltxv")` is called
- **THEN** an LTX-V workflow is used and video files are saved to `outputs/`

#### Scenario: Model selection wan
- **WHEN** `generate(prompt, model="wan")` is called
- **THEN** a Wan 2.2 workflow is used and video files are saved to `outputs/`

#### Scenario: Wan noise variant passthrough
- **WHEN** `generate(prompt, model="wan", noise="low")` is called
- **THEN** the low-noise Wan UNET variant is used

#### Scenario: Unknown model
- **WHEN** an unrecognised `model` string is passed
- **THEN** a `ValueError` is raised
