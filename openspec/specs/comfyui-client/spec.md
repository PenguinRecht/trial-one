## ADDED Requirements

### Requirement: Queue a generation job
The client SHALL POST a workflow to `/prompt` and return a `prompt_id` string.

#### Scenario: Successful queue
- **WHEN** a valid workflow dict is passed to `queue_prompt()`
- **THEN** the client returns a non-empty `prompt_id` string

#### Scenario: Server unreachable
- **WHEN** the ComfyUI endpoint is not reachable
- **THEN** a `requests.ConnectionError` is raised

### Requirement: Poll job to completion
The client SHALL poll `/history/<prompt_id>` until `status_str == "success"` or a timeout is exceeded.

#### Scenario: Job completes successfully
- **WHEN** `poll()` is called with a valid `prompt_id`
- **THEN** it returns the full history entry dict once status is `"success"`

#### Scenario: Job times out
- **WHEN** the job does not complete within the configured timeout
- **THEN** a `TimeoutError` is raised

#### Scenario: Job errors on server
- **WHEN** the server reports `status_str == "error"`
- **THEN** a `RuntimeError` is raised with the history entry

### Requirement: Download output images
The client SHALL download all images from a completed job's history entry to the `outputs/` directory.

#### Scenario: Single image output
- **WHEN** `download_outputs()` is called with a completed history entry
- **THEN** each image is saved to `outputs/<prefix>_<filename>` and its path is returned

### Requirement: Endpoint configured via environment
The client SHALL read `COMFYUI_BASE_URL` from the environment (via `.env` file or shell export).

#### Scenario: Env var present
- **WHEN** `COMFYUI_BASE_URL` is set
- **THEN** all requests use that base URL

#### Scenario: Env var missing
- **WHEN** `COMFYUI_BASE_URL` is not set
- **THEN** a `KeyError` is raised on import
