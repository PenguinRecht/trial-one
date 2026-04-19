"""Run image/video generations from prompts.json (local, gitignored) or built-in samples."""

import argparse
import json
import pathlib
from comfy_client import health, generate

PROMPTS_FILE = pathlib.Path("prompts.json")

BUILTIN_SAMPLES = [
    {
        "label": "graphic_novel_panel",
        "prompt": "A rain-soaked cyberpunk alley at midnight, graphic novel ink-wash style",
        "model": "flux2",
        "width": 1024,
        "height": 1024,
        "steps": 20,
    },
    {
        "label": "claymation_keyframe",
        "prompt": "A cheerful clay robot tending a tiny garden, Laika-style stop-motion aesthetic",
        "model": "flux1",
        "width": 1024,
        "height": 1024,
        "steps": 20,
    },
    {
        "label": "ltxv_sample",
        "prompt": "A glowing lantern drifting upward through misty ancient trees at night, cinematic",
        "model": "ltxv",
        "width": 768,
        "height": 512,
        "frames": 25,
        "fps": 24,
        "steps": 20,
    },
    {
        "label": "wan_sample",
        "prompt": "Ocean waves crashing against rocky sea cliffs at golden hour, ultra detailed",
        "model": "wan",
        "width": 832,
        "height": 480,
        "frames": 81,
        "fps": 16,
        "steps": 20,
        "noise": "high",
    },
]


def load_prompts() -> list[dict]:
    if PROMPTS_FILE.exists():
        prompts = json.loads(PROMPTS_FILE.read_text())
        print(f"Loaded {len(prompts)} prompt(s) from {PROMPTS_FILE}\n")
        return prompts
    print(f"No {PROMPTS_FILE} found -- using built-in samples. "
          f"Copy prompts.example.json to prompts.json to use your own.\n")
    return BUILTIN_SAMPLES


def main():
    parser = argparse.ArgumentParser(description="Generate images/videos via ComfyUI.")
    parser.add_argument("--model", choices=["flux2", "flux1", "ltxv", "wan", "all"], default="all",
                        help="Which model to use (default: all)")
    parser.add_argument("--steps", type=int, default=None,
                        help="Override step count for all prompts")
    parser.add_argument("--seed", type=int, default=None,
                        help="Fixed seed for reproducibility")
    parser.add_argument("--frames", type=int, default=None,
                        help="Override frame count for all video prompts")
    parser.add_argument("--fps", type=float, default=None,
                        help="Override fps for all video prompts")
    args = parser.parse_args()

    print("Checking DGX Spark health ...")
    stats = health()
    gpu = stats.get("devices", [{}])[0]
    print(f"  GPU: {gpu.get('name', 'unknown')}  "
          f"VRAM free: {gpu.get('vram_free', '?')} / {gpu.get('vram_total', '?')}\n")

    for sample in load_prompts():
        model = sample["model"]
        if args.model != "all" and model != args.model:
            continue
        files = generate(
            sample["prompt"],
            model=model,
            width=sample.get("width"),
            height=sample.get("height"),
            steps=args.steps or sample.get("steps", 20),
            seed=args.seed,
            frames=args.frames or sample.get("frames"),
            fps=args.fps or sample.get("fps"),
            noise=sample.get("noise", "high"),
            filename_prefix=sample["label"],
        )
        print(f"  -> {len(files)} file(s) written\n")


if __name__ == "__main__":
    main()
