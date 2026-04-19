"""ComfyUI remote client — talks to the DGX Spark over HTTP."""

import math
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


def download_outputs(history_entry: dict, prefix: str = "output") -> list[pathlib.Path]:
    """Download all images and videos from a completed job's history entry."""
    saved = []
    for node_outputs in history_entry.get("outputs", {}).values():
        # SaveImage / SaveAnimatedWEBP both use the 'images' key
        for img in node_outputs.get("images", []):
            _download_file(img, prefix, saved)
        # SaveVideo uses the 'gifs' key
        for vid in node_outputs.get("gifs", []):
            _download_file(vid, prefix, saved)
        # Future-proof: 'videos' key
        for vid in node_outputs.get("videos", []):
            _download_file(vid, prefix, saved)
    return saved


def _download_file(entry: dict, prefix: str, saved: list) -> None:
    params = {
        "filename": entry["filename"],
        "subfolder": entry.get("subfolder", ""),
        "type": entry.get("type", "output"),
    }
    resp = requests.get(f"{BASE_URL}/view", params=params, timeout=120)
    resp.raise_for_status()
    dest = OUTPUTS_DIR / f"{prefix}_{entry['filename']}"
    dest.write_bytes(resp.content)
    saved.append(dest)
    print(f"  saved -> {dest}")


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


def _wan_valid_frames(frames: int) -> int:
    """Round up to nearest valid Wan frame count (multiple of 4 + 1)."""
    if frames <= 1:
        return 1
    return math.ceil((frames - 1) / 4) * 4 + 1


def ltxv_workflow(
    prompt: str,
    width: int = 768,
    height: int = 512,
    frames: int = 25,
    fps: float = 24.0,
    steps: int = 20,
    seed: int | None = None,
    negative_prompt: str = "worst quality, blurry, jittery, distorted",
    filename_prefix: str = "ltxv",
) -> dict:
    """LTX-V 13B distilled fp8 text-to-video workflow.

    Uses LTXVImgToVideo with a black EmptyImage — this is the correct T2V
    pattern: the node embeds the attention mask internally and with
    strength=1.0 the seed image is fully denoised away (pure T2V).

    Node chain:
      UNETLoader -> ModelSamplingLTXV
      CLIPLoader -> CLIPTextEncode x2
      VAELoader + EmptyImage -> LTXVImgToVideo (outputs pos/neg/latent)
      -> CFGGuider -> KSamplerSelect + LTXVScheduler + RandomNoise
      -> SamplerCustomAdvanced -> VAEDecode -> SaveAnimatedWEBP
    """
    seed = seed if seed is not None else int(time.time()) % (2**32)
    # LTXVImgToVideo length must be a multiple of 8, min 9
    frames = max(9, math.ceil(frames / 8) * 8)
    return {
        "1":  {"class_type": "UNETLoader",         "inputs": {"unet_name": "ltxv-13b-0.9.8-distilled-fp8.safetensors", "weight_dtype": "fp8_e4m3fn"}},
        "2":  {"class_type": "ModelSamplingLTXV",   "inputs": {"model": ["1", 0], "max_shift": 2.05, "base_shift": 0.95}},
        "3":  {"class_type": "CLIPLoader",          "inputs": {"clip_name": "clip_l.safetensors", "type": "ltxv"}},
        "4":  {"class_type": "CLIPTextEncode",      "inputs": {"text": prompt,          "clip": ["3", 0]}},
        "5":  {"class_type": "CLIPTextEncode",      "inputs": {"text": negative_prompt, "clip": ["3", 0]}},
        "6":  {"class_type": "VAELoader",           "inputs": {"vae_name": "pixel_space"}},
        # Black seed image — fully denoised away at strength=1.0 (pure T2V)
        "7":  {"class_type": "EmptyImage",          "inputs": {"width": width, "height": height, "batch_size": 1, "color": 0}},
        # LTXVImgToVideo embeds attention mask; outputs [0]=pos, [1]=neg, [2]=latent
        "8":  {"class_type": "LTXVImgToVideo",      "inputs": {
            "positive": ["4", 0], "negative": ["5", 0], "vae": ["6", 0],
            "image": ["7", 0], "width": width, "height": height,
            "length": frames, "batch_size": 1, "strength": 1.0,
        }},
        "9":  {"class_type": "CFGGuider",           "inputs": {"model": ["2", 0], "positive": ["8", 0], "negative": ["8", 1], "cfg": 3.5}},
        "10": {"class_type": "KSamplerSelect",      "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "LTXVScheduler",       "inputs": {"steps": steps, "max_shift": 2.05, "base_shift": 0.95, "stretch": True, "terminal": 0.1}},
        "12": {"class_type": "RandomNoise",         "inputs": {"noise_seed": seed}},
        "13": {"class_type": "SamplerCustomAdvanced","inputs": {
            "noise": ["12", 0], "guider": ["9", 0],
            "sampler": ["10", 0], "sigmas": ["11", 0], "latent_image": ["8", 2],
        }},
        "14": {"class_type": "VAEDecode",           "inputs": {"samples": ["13", 0], "vae": ["6", 0]}},
        "15": {"class_type": "SaveAnimatedWEBP",    "inputs": {
            "images": ["14", 0], "filename_prefix": filename_prefix,
            "fps": fps, "lossless": False, "quality": 85, "method": "default",
        }},
    }


def wan_workflow(
    prompt: str,
    width: int = 832,
    height: int = 480,
    frames: int = 81,
    fps: float = 16.0,
    steps: int = 20,
    seed: int | None = None,
    noise: str = "high",
    negative_prompt: str = "worst quality, blurry, distorted",
    filename_prefix: str = "wan",
) -> dict:
    """Wan 2.2 14B T2V fp8 text-to-video workflow.

    Args:
        noise: "high" for more dynamic motion, "low" for controlled/clean motion.

    Node chain:
      UNETLoader + CLIPLoader(wan) + VAELoader
      -> CLIPTextEncode x2 -> WanImageToVideo (creates cond + latent)
      -> CFGGuider -> KSamplerSelect + BasicScheduler + RandomNoise
      -> SamplerCustomAdvanced -> VAEDecode -> SaveAnimatedWEBP
    """
    seed = seed if seed is not None else int(time.time()) % (2**32)
    frames = _wan_valid_frames(frames)

    unet_map = {
        "high": "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors",
        "low":  "wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors",
    }
    if noise not in unet_map:
        raise ValueError(f"noise must be 'high' or 'low', got '{noise}'")

    return {
        "1":  {"class_type": "UNETLoader",       "inputs": {"unet_name": unet_map[noise], "weight_dtype": "fp8_e4m3fn"}},
        "2":  {"class_type": "CLIPLoader",        "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan"}},
        "3":  {"class_type": "VAELoader",         "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
        "4":  {"class_type": "CLIPTextEncode",    "inputs": {"text": prompt,          "clip": ["2", 0]}},
        "5":  {"class_type": "CLIPTextEncode",    "inputs": {"text": negative_prompt, "clip": ["2", 0]}},
        # WanImageToVideo outputs: [0]=positive_cond, [1]=negative_cond, [2]=latent
        "6":  {"class_type": "WanImageToVideo",   "inputs": {
            "positive": ["4", 0], "negative": ["5", 0], "vae": ["3", 0],
            "width": width, "height": height, "length": frames, "batch_size": 1,
        }},
        "7":  {"class_type": "CFGGuider",         "inputs": {"model": ["1", 0], "positive": ["6", 0], "negative": ["6", 1], "cfg": 7.0}},
        "8":  {"class_type": "KSamplerSelect",    "inputs": {"sampler_name": "euler"}},
        "9":  {"class_type": "BasicScheduler",    "inputs": {"model": ["1", 0], "scheduler": "simple", "steps": steps, "denoise": 1.0}},
        "10": {"class_type": "RandomNoise",       "inputs": {"noise_seed": seed}},
        "11": {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["10", 0], "guider": ["7", 0],
            "sampler": ["8", 0], "sigmas": ["9", 0], "latent_image": ["6", 2],
        }},
        "12": {"class_type": "VAEDecode",         "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveAnimatedWEBP",  "inputs": {
            "images": ["12", 0], "filename_prefix": filename_prefix,
            "fps": fps, "lossless": False, "quality": 85, "method": "default",
        }},
    }


# ---------------------------------------------------------------------------
# High-level generate()
# ---------------------------------------------------------------------------

def generate(
    prompt: str,
    *,
    model: str = "flux2",
    width: int | None = None,
    height: int | None = None,
    steps: int = 20,
    seed: int | None = None,
    frames: int | None = None,
    fps: float | None = None,
    noise: str = "high",
    filename_prefix: str | None = None,
    poll_interval: float = 5.0,
    timeout: float = 900.0,
) -> list[pathlib.Path]:
    """Queue a generation job, wait for it, download outputs to ./outputs/.

    Models:
        flux2  — Flux.2 [dev] bf16, high-fidelity stills (default 1024x1024)
        flux1  — Flux.1-dev-fp8, fast draft stills (default 1024x1024)
        ltxv   — LTX-V 13B distilled fp8, text-to-video (default 768x512, 25 frames)
        wan    — Wan 2.2 14B T2V fp8, text-to-video (default 832x480, 81 frames)

    Video kwargs:
        frames — number of frames (model defaults apply if omitted)
        fps    — frames per second (model defaults apply if omitted)
        noise  — Wan only: "high" (dynamic) or "low" (controlled)
    """
    prefix = filename_prefix or model

    if model == "flux2":
        w, h = width or 1024, height or 1024
        workflow = flux2_workflow(prompt, w, h, steps, seed, prefix)
    elif model == "flux1":
        w, h = width or 1024, height or 1024
        workflow = flux1_fast_workflow(prompt, w, h, steps, seed, prefix)
    elif model == "ltxv":
        w, h = width or 768, height or 512
        workflow = ltxv_workflow(
            prompt, w, h,
            frames=frames or 25,
            fps=fps or 24.0,
            steps=steps, seed=seed, filename_prefix=prefix,
        )
    elif model == "wan":
        w, h = width or 832, height or 480
        workflow = wan_workflow(
            prompt, w, h,
            frames=frames or 81,
            fps=fps or 16.0,
            steps=steps, seed=seed, noise=noise, filename_prefix=prefix,
        )
    else:
        raise ValueError(f"Unknown model '{model}'. Choose: flux2, flux1, ltxv, wan.")

    print(f"Queuing [{model}] -- \"{prompt[:60]}...\"")
    prompt_id = queue_prompt(workflow)
    print(f"  prompt_id: {prompt_id}")
    print(f"  waiting (up to {timeout}s) ...")
    entry = poll(prompt_id, interval=poll_interval, timeout=timeout)
    return download_outputs(entry, prefix=prefix)
