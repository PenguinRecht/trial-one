## 1. Verify Node Names Against Live Instance

- [x] 1.1 Query `/object_info/LTXVScheduler` and confirm input field names (`steps`, `width`, `height`, `length`, `fps`)
- [x] 1.2 Query `/object_info/EmptyLTXVLatentVideo` and confirm input field names
- [x] 1.3 Query `/object_info/ModelSamplingLTXV` and confirm it exists and its inputs
- [x] 1.4 Query Wan sampler nodes (`WanImageToVideo`, any T2V-specific node) and confirm the correct text-to-video node chain

## 2. LTX-V Workflow Builder

- [x] 2.1 Implement `ltxv_workflow(prompt, width, height, frames, fps, steps, seed, filename_prefix)` in `comfy_client.py`
- [x] 2.2 Wire nodes: UNETLoader → ModelSamplingLTXV → CLIPLoader(ltxv) → CLIPTextEncode x2 → LTXVConditioning → CFGGuider → KSamplerSelect → LTXVScheduler → RandomNoise → EmptyLTXVLatentVideo → SamplerCustomAdvanced → VAEDecode → SaveAnimatedWEBP
- [x] 2.3 Default values: 768×512, 25 frames, 24 fps, 20 steps

## 3. Wan 2.2 Workflow Builder

- [x] 3.1 Implement `wan_workflow(prompt, width, height, frames, fps, steps, seed, noise, filename_prefix)` in `comfy_client.py`
- [x] 3.2 Wire nodes: UNETLoader → CLIPLoader(wan) → VAELoader → CLIPTextEncode x2 → WanImageToVideo (outputs pos/neg/latent) → CFGGuider → KSamplerSelect → BasicScheduler → RandomNoise → SamplerCustomAdvanced → VAEDecode → SaveAnimatedWEBP
- [x] 3.3 Implement frame count validation: round up to nearest (multiple of 4 + 1)
- [x] 3.4 Default values: 832×480, 81 frames, 16 fps, 20 steps, noise="high"

## 4. Extend generate()

- [x] 4.1 Add `model="ltxv"` routing in `generate()` — pass `frames`, `fps` kwargs through
- [x] 4.2 Add `model="wan"` routing in `generate()` — pass `frames`, `fps`, `noise` kwargs through
- [x] 4.3 Update `ValueError` message to list all valid model names including new ones

## 5. Update CLI

- [x] 5.1 Add `"ltxv"` and `"wan"` to `--model` choices in `generate_samples.py`
- [x] 5.2 Add `--frames` and `--fps` override flags
- [x] 5.3 Add video sample entries to `BUILTIN_SAMPLES`

## 6. Validation

- [ ] 6.1 Generate a short LTX-V clip (25 frames) with a test prompt and confirm file saved to `outputs/`
      BLOCKED: ComfyUI 0.17.0 bug — `LTXBaseModel.forward()` missing `attention_mask` kwarg during
      sampling. Affects all T2V workflows using the `SamplerCustomAdvanced` chain. Needs a ComfyUI
      patch or server update before this can be validated.
- [ ] 6.2 Generate a short Wan clip (high-noise, 81 frames) with a test prompt and confirm file saved to `outputs/`
      BLOCKED: `umt5_xxl_fp8_e4m3fn_scaled.safetensors` on the Spark is corrupted/incomplete
      (`safetensors: incomplete metadata, file not fully covered`). Re-download the file on the
      DGX Spark to unblock.
