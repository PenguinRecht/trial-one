## ADDED Requirements

### Requirement: prompts.json is never committed
The repository SHALL gitignore `prompts.json` so user prompt descriptions cannot be accidentally committed.

#### Scenario: File present locally
- **WHEN** a `prompts.json` exists in the working directory
- **THEN** `git status` does not list it as a tracked or stageable file

### Requirement: prompts.example.json documents the schema
The repository SHALL include a tracked `prompts.example.json` showing all supported fields.

#### Scenario: New contributor setup
- **WHEN** a contributor clones the repo
- **THEN** they can copy `prompts.example.json` to `prompts.json` and run the pipeline immediately

### Requirement: inputs directory is gitignored
The repository SHALL gitignore the `inputs/` directory for storing local reference images and source material.

#### Scenario: Reference image added locally
- **WHEN** an image is placed in `inputs/`
- **THEN** `git status` does not list it

### Requirement: Endpoint template provided
The repository SHALL include `.env.example` with a placeholder `COMFYUI_BASE_URL` value.

#### Scenario: Fresh clone setup
- **WHEN** a user copies `.env.example` to `.env` and sets the URL
- **THEN** the pipeline connects to their endpoint without additional configuration
