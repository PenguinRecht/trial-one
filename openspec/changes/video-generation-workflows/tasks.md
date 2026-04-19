## 1. Verify Node Names Against Live Instance

- [ ] 1.1 Query `/object_info/LTXVScheduler` and confirm input field names (`steps`, `width`, `height`, `length`, `fps`)
- [ ] 1.2 Query `/object_info/EmptyLTXVLatentVideo` and confirm input field names
- [ ] 1.3 Query `/object_info/ModelSamplingLTXV` and confirm it exists and its inputs
- [ ] 1.4 Query Wan sampler nodes (`WanImageToVideo`, any T2V-specific node) and confirm the correct text-to-video node chain

## 2. LTX-V Workflow Builder

- [ ] 2.1 Implement `ltxv_workflow(prompt, width, height, frames, fps, steps, seed, filename_prefix)` in `comfy_client.py`
- [ ] 2.2 Wire nodes: UNETLoader → CLIPLoader(ltxv) → CLIPTextEncode → BasicGuider → KSamplerSelect → LTXVScheduler → RandomNoise → EmptyLTXVLatentVideo → SamplerCustomAdvanced → VAEDecode → SaveVideo
- [ ] 2.3 Default values: 768×512, 25 frames, 24 fps, 20 steps

## 3. Wan 2.2 Workflow Builder

- [ ] 3.1 Implement `wan_workflow(prompt, width, height, frames, fps, steps, seed, noise, filename_prefix)` in `comfy_client.py`
- [ ] 3.2 Wire nodes: UNETLoader (noise-variant UNET) → CLIPLoader(umt5_xxl) → CLIPTextEncode → BasicGuider → KSamplerSelect → scheduler → RandomNoise → EmptyLatentVideo → SamplerCustomAdvanced → VAEDecode → SaveVideo
- [ ] 3.3 Implement frame count validation: round up to nearest (multiple of 4 + 1)
- [ ] 3.4 Default values: 832×480, 81 frames, 16 fps, 20 steps, noise="high"

## 4. Extend generate()

- [ ] 4.1 Add `model="ltxv"` routing in `generate()` — pass `frames`, `fps` kwargs through
- [ ] 4.2 Add `model="wan"` routing in `generate()` — pass `frames`, `fps`, `noise` kwargs through
- [ ] 4.3 Update `ValueError` message to list all valid model names including new ones

## 5. Update CLI

- [ ] 5.1 Add `"ltxv"` and `"wan"` to `--model` choices in `generate_samples.py`
- [ ] 5.2 Add `--frames` and `--fps` override flags
- [ ] 5.3 Add video sample entries to `BUILTIN_SAMPLES`

## 6. Validation

- [ ] 6.1 Generate a short LTX-V clip (25 frames) with a test prompt and confirm file saved to `outputs/`
- [ ] 6.2 Generate a short Wan clip (high-noise, 81 frames) with a test prompt and confirm file saved to `outputs/`
