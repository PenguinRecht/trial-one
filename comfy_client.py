"""ComfyUI remote client — talks to the DGX Spark over HTTP."""

import os
import time
import uuid
import pathlib
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.environ["COMFYUI_BASE_URL"].rstrip("/")
OUTPUTS_DIR = pathlib.Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def health() -> dict:
    return requests.get(f"{BASE_URL}/system_stats", timeout=10).json()


def queue_prompt(workflow: dict, client_id: str | None = None) -> str:
    client_id = client_id or str(uuid.uuid4())
    resp = requests.post(
        f"{BASE_URL}/prompt",
        json={"prompt": workflow, "client_id": client_id},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["prompt_id"]


def poll(prompt_id: str, interval: float = 5.0, timeout: float = 600.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        history = requests.get(f"{BASE_URL}/history/{prompt_id}", timeout=10).json()
        if prompt_id in history:
            entry = history[prompt_id]
            status = entry.get("status", {}).get("status_str")
            if status == "success":
                return entry
            if status == "error":
                raise RuntimeError(f"ComfyUI job failed: {entry}")
        time.sleep(interval)
    raise TimeoutError(f"Job {prompt_id} did not finish within {timeout}s")


def download_outputs(history_entry: dict, prefix: str = "image") -> list[pathlib.Path]:
    saved = []
    for node_outputs in history_entry.get("outputs", {}).values():
        for img in node_outputs.get("images", []):
            params = {
                "filename": img["filename"],
                "subfolder": img.get("subfolder", ""),
                "type": img.get("type", "output"),
            }
            resp = requests.get(f"{BASE_URL}/view", params=params, timeout=60)
            resp.raise_for_status()
            ext = pathlib.Path(img["filename"]).suffix or ".png"
            dest = OUTPUTS_DIR / f"{prefix}_{img['filename']}"
            dest.write_bytes(resp.content)
            saved.append(dest)
            print(f"  saved → {dest}")
    return saved


# ---------------------------------------------------------------------------
# Workflow builders
# ---------------------------------------------------------------------------

def flux2_workflow(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    steps: int = 20,
    seed: int | None = None,
    filename_prefix: str = "flux2",
) -> dict:
    """High-fidelity Flux.2 [dev] bf16 workflow."""
    seed = seed if seed is not None else int(time.time()) % (2**32)
    return {
        "1":  {"class_type": "UNETLoader",   "inputs": {"unet_name": "flux2-dev.safetensors", "weight_dtype": "default"}},
        "2":  {"class_type": "CLIPLoader",   "inputs": {"clip_name": "mistral_3_small_flux2_bf16.safetensors", "type": "flux2"}},
        "3":  {"class_type": "VAELoader",    "inputs": {"vae_name": "flux2-vae.safetensors"}},
        "4":  {"class_type": "CLIPTextEncode","inputs": {"text": prompt, "clip": ["2", 0]}},
        "5":  {"class_type": "BasicGuider",  "inputs": {"model": ["1", 0], "conditioning": ["4", 0]}},
        "6":  {"class_type": "KSamplerSelect","inputs": {"sampler_name": "euler"}},
        "7":  {"class_type": "Flux2Scheduler","inputs": {"steps": steps, "width": width, "height": height}},
        "8":  {"class_type": "RandomNoise",  "inputs": {"noise_seed": seed}},
        "9":  {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "10": {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["8", 0], "guider": ["5", 0],
            "sampler": ["6", 0], "sigmas": ["7", 0], "latent_image": ["9", 0],
        }},
        "11": {"class_type": "VAEDecode",    "inputs": {"samples": ["10", 0], "vae": ["3", 0]}},
        "12": {"class_type": "SaveImage",    "inputs": {"filename_prefix": filename_prefix, "images": ["11", 0]}},
    }


def flux1_fast_workflow(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    steps: int = 20,
    seed: int | None = None,
    filename_prefix: str = "flux1",
) -> dict:
    """Fast draft keyframe workflow using Flux.1-dev-fp8."""
    seed = seed if seed is not None else int(time.time()) % (2**32)
    return {
        "1":  {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "flux1-dev-fp8.safetensors"}},
        "2":  {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3":  {"class_type": "CLIPTextEncode", "inputs": {"text": "",     "clip": ["1", 1]}},
        "4":  {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
            "latent_image": ["5", 0], "sampler_name": "euler",
            "scheduler": "simple", "steps": steps, "cfg": 1.0,
            "denoise": 1.0, "seed": seed,
        }},
        "5":  {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "6":  {"class_type": "VAEDecode",  "inputs": {"samples": ["4", 0], "vae": ["1", 2]}},
        "7":  {"class_type": "SaveImage",  "inputs": {"filename_prefix": filename_prefix, "images": ["6", 0]}},
    }


# ---------------------------------------------------------------------------
# High-level generate()
# ---------------------------------------------------------------------------

def generate(
    prompt: str,
    *,
    model: str = "flux2",
    width: int = 1024,
    height: int = 1024,
    steps: int = 20,
    seed: int | None = None,
    filename_prefix: str | None = None,
    poll_interval: float = 5.0,
    timeout: float = 600.0,
) -> list[pathlib.Path]:
    """Queue a generation job, wait for it, download outputs to ./outputs/."""
    prefix = filename_prefix or model
    if model == "flux2":
        workflow = flux2_workflow(prompt, width, height, steps, seed, prefix)
    elif model == "flux1":
        workflow = flux1_fast_workflow(prompt, width, height, steps, seed, prefix)
    else:
        raise ValueError(f"Unknown model '{model}'. Choose 'flux2' or 'flux1'.")

    print(f"Queuing [{model}] — \"{prompt[:60]}...\"")
    prompt_id = queue_prompt(workflow)
    print(f"  prompt_id: {prompt_id}")
    print(f"  waiting (up to {timeout}s) …")
    entry = poll(prompt_id, interval=poll_interval, timeout=timeout)
    return download_outputs(entry, prefix=prefix)
