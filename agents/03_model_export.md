# Agent 3: Model Export & Sprite Atlas

## Your Task

Export the trained PyTorch VAE decoder to TensorFlow.js format and generate all pre-computed assets needed by the web visualization.

## Prerequisites

- Trained model at `checkpoints/vae_final.pt`
- Model definition in `models/vae.py`
- Dataset in `dataset/`

## Files to Create

### `export_decoder.py` — PyTorch → TF.js

**Pipeline:**
1. Load the trained VAE from `checkpoints/vae_final.pt`
2. Extract the decoder only (we don't ship the encoder to the browser)
3. Create a standalone decoder module that takes `z ∈ R²` and outputs `image ∈ R^{32×32×3}`
4. Export to ONNX: `torch.onnx.export(decoder, dummy_z, "decoder.onnx", opset_version=17)`
5. Convert ONNX → TF.js:
   ```bash
   pip install tensorflowjs onnx-tf
   # ONNX → SavedModel
   onnx-tf convert -i decoder.onnx -o decoder_savedmodel
   # SavedModel → TF.js with float16 quantization
   tensorflowjs_converter --input_format=tf_saved_model --output_format=tfjs_graph_model --quantize_float16 decoder_savedmodel web/assets/model
   ```
6. Verify the output: `web/assets/model/model.json` + `web/assets/model/*.bin`

**Important:** The decoder output must be in channels-last format (H, W, C) for the browser. If the PyTorch decoder outputs channels-first (C, H, W), add a permute operation before export.

**Important:** Output values must be in [0, 1] (Sigmoid on last layer). Verify this.

**CLI:**
```bash
python export_decoder.py [--checkpoint checkpoints/vae_final.pt] [--output_dir web/assets/model]
```

### `generate_atlas.py` — Sprite Atlas

**What it does:**
1. Load the trained decoder
2. Generate a 24×24 grid of z values evenly spaced in [-3, 3]²
3. Decode each z to a 32×32 image (or 64×64 if upscaled)
4. Stitch all images into a single atlas image
5. Save as WebP (with PNG fallback)

**Output:** `web/assets/sprites/atlas.webp`
- Grid: 24×24 cells
- Cell size: 64×64 pixels (upscale from 32×32 using bilinear interpolation for better visual quality)
- Total atlas: 1536×1536 pixels
- Format: WebP at quality 90 (with PNG fallback for compatibility)

**CLI:**
```bash
python generate_atlas.py [--checkpoint checkpoints/vae_final.pt] [--grid_size 24] [--cell_size 64] [--output_dir web/assets/sprites]
```

### `export_latents.py` — Latent Coordinates

**What it does:**
1. Load the trained encoder
2. Run all training images through the encoder
3. Save the (mu, logvar) for each image along with its ground-truth (sun_x, sun_y)

**Output:** `web/assets/data/latent_coords.json`
```json
[
  {"z": [0.42, -1.31], "sun_x": 0.25, "sun_y": 0.75, "thumb_idx": 0},
  {"z": [1.87, 0.55], "sun_x": 0.80, "sun_y": 0.40, "thumb_idx": 1},
  ...
]
```

Also generate a thumbnails sprite sheet:
**Output:** `web/assets/sprites/thumbnails.webp`
- Arrange all training images in a grid (e.g., 45×45 for 2000 images)
- Each thumbnail: 32×32 pixels
- `thumb_idx` in the JSON maps to position in this grid: row = idx // cols, col = idx % cols

**CLI:**
```bash
python export_latents.py [--checkpoint checkpoints/vae_final.pt] [--data_dir dataset] [--output_dir web/assets]
```

## Output Directory Structure

```
web/
  assets/
    model/
      model.json          -- TF.js model topology
      group1-shard1of1.bin -- Float16 weights
    sprites/
      atlas.webp          -- 24×24 decoded grid (1536×1536)
      atlas.png           -- PNG fallback
      thumbnails.webp     -- Training image sprite sheet
    data/
      latent_coords.json  -- Encoded coordinates for all training images
```

## Dependencies

```
pip install torch onnx onnx-tf tensorflowjs Pillow numpy
```

If `onnx-tf` is problematic, an alternative path:
```
torch → ONNX → onnxruntime (verify) → manual TF.js conversion
```

Or use `torch.jit.trace` → export directly if `ai.onnx` ops are all supported.

## Acceptance Criteria

1. `model.json` + `*.bin` files exist and total < 500KB
2. Atlas image shows a smooth 24×24 grid of sunrises — no black cells, no artifacts
3. `latent_coords.json` is valid JSON, z values are in roughly [-3, 3] range
4. Thumbnails sprite sheet contains recognizable sunrise thumbnails
5. The TF.js model can be loaded in a browser (test with a simple HTML file if possible)

## Verification Script

Create a simple `verify_export.py` that:
1. Loads the ONNX model and runs inference on a test z value
2. Compares the output with the original PyTorch decoder output
3. Reports the max absolute difference (should be < 0.01 for float16)
