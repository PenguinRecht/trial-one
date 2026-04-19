## MODIFIED Requirements

### Requirement: Filter by model flag
The CLI SHALL accept `--model flux2|flux1|ltxv|wan|all` and skip prompts not matching the selected model.

#### Scenario: Model filter applied to image model
- **WHEN** `--model flux2` is passed
- **THEN** only entries with `"model": "flux2"` are generated

#### Scenario: Model filter applied to video model
- **WHEN** `--model ltxv` is passed
- **THEN** only entries with `"model": "ltxv"` are generated

#### Scenario: All models run
- **WHEN** `--model all` is passed (or flag omitted)
- **THEN** all prompt entries are generated regardless of model type
