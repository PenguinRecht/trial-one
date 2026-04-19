"""Run a set of sample generations to test the pipeline."""

import argparse
from comfy_client import health, generate

SAMPLES = [
    {
        "label": "graphic_novel_panel",
        "prompt": (
            "A rain-soaked cyberpunk alley at midnight, neon reflections on wet cobblestones, "
            "a lone figure in a trench coat pauses beneath a flickering holographic sign, "
            "graphic novel ink-wash style, dramatic chiaroscuro lighting"
        ),
        "model": "flux2",
        "width": 1024,
        "height": 1024,
        "steps": 20,
    },
    {
        "label": "claymation_keyframe",
        "prompt": (
            "A cheerful clay robot tending a tiny garden of glowing mushrooms, "
            "soft studio lighting, Laika-style stop-motion aesthetic, pastel colour palette"
        ),
        "model": "flux1",
        "width": 1024,
        "height": 1024,
        "steps": 20,
    },
    {
        "label": "landscape_wide",
        "prompt": (
            "Sweeping aerial view of a bioluminescent forest at dusk, "
            "ancient trees with ember-orange foliage, mist threading through valleys, "
            "Studio Ghibli painterly style, ultra-detailed"
        ),
        "model": "flux2",
        "width": 1280,
        "height": 768,
        "steps": 25,
    },
]


def main():
    parser = argparse.ArgumentParser(description="Generate sample images via ComfyUI.")
    parser.add_argument("--model", choices=["flux2", "flux1", "all"], default="all",
                        help="Which model to use (default: all)")
    parser.add_argument("--steps", type=int, default=None,
                        help="Override step count for all samples")
    parser.add_argument("--seed", type=int, default=None,
                        help="Fixed seed for reproducibility")
    args = parser.parse_args()

    print("Checking DGX Spark health …")
    stats = health()
    gpu = stats.get("devices", [{}])[0]
    print(f"  GPU: {gpu.get('name', 'unknown')}  "
          f"VRAM free: {gpu.get('vram_free', '?')} / {gpu.get('vram_total', '?')}\n")

    for sample in SAMPLES:
        if args.model != "all" and sample["model"] != args.model:
            continue
        files = generate(
            sample["prompt"],
            model=sample["model"],
            width=sample["width"],
            height=sample["height"],
            steps=args.steps or sample["steps"],
            seed=args.seed,
            filename_prefix=sample["label"],
        )
        print(f"  → {len(files)} file(s) written\n")


if __name__ == "__main__":
    main()
