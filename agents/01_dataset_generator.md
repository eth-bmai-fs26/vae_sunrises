# Agent 1: Synthetic Sunrise Generator

## Your Task

Create `generate_dataset.py` — a Python script that procedurally generates small synthetic sunrise images parameterized by two variables.

## Parameters

- `sun_x` ∈ [0, 1]: horizontal position of the sun (represents time of year). 0 = winter, 1 = summer.
- `sun_y` ∈ [0, 1]: vertical position / elevation of the sun (represents time of day). 0 = just below horizon (dawn), 1 = high in sky (noon).

These two numbers must fully determine the image.

## Rendering Pipeline

For each (sun_x, sun_y), generate a 32×32 RGB image:

### 1. Sky Gradient (vertical blend, 3-4 color stops)

The sky is a vertical gradient from top to bottom. The colors depend on BOTH parameters:

**sun_y controls the base palette:**
- sun_y ≈ 0 (dawn): dark indigo at top → deep violet → rose → gold at horizon
- sun_y ≈ 0.3 (early morning): navy at top → blue → peach → orange at horizon
- sun_y ≈ 0.7 (mid-morning): blue at top → light blue → pale yellow at horizon
- sun_y ≈ 1.0 (noon): deep blue at top → sky blue → white at horizon

**sun_x shifts the warmth:**
- sun_x ≈ 0 (winter): cooler, more blue/violet tones, less saturated
- sun_x ≈ 1 (summer): warmer, more orange/gold tones, more saturated

Interpolate smoothly between these reference palettes.

### 2. Sun Disc

- Position: x = sun_x × image_width, y = (1 - sun_y) × image_height × 0.7 + 0.1 × image_height
- Render as a Gaussian blob (soft circular glow, not a hard circle)
- Radius: ~3-5 pixels at 32×32
- Color: deep orange/red when sun_y is low, golden-yellow when sun_y is mid, white-yellow when sun_y is high
- Brightness: the sun should be the brightest element in the image

### 3. Atmospheric Glow

- Large soft radial gradient centered on the sun position
- Tints nearby sky pixels with warm colors (orange/gold)
- Radius: ~40-60% of image width
- Intensity: stronger when sun is low (sun_y < 0.3), weaker when high
- This creates the "golden hour" effect near the sun

### 4. Horizon Silhouette

- Dark band at the bottom ~15% of the image
- Color: very dark blue-black (#0A0A1A) to dark green-brown (#1A2A1A)
- Slight undulation: use a low-frequency sine wave for gentle hills
- The undulation phase can vary slightly with sun_x for variety

### 5. Color Variation

- Add very subtle per-pixel Gaussian noise (σ ≈ 0.01) for texture
- Clip all values to [0, 1]

## Output Format

```
dataset/
  images.npy     — shape (N, 32, 32, 3), dtype float32, values in [0, 1]
  coords.npy     — shape (N, 2), dtype float32, columns are [sun_x, sun_y]
  preview.png    — 10×10 grid of sample images spanning the parameter space
```

## CLI Interface

```bash
python generate_dataset.py [--n_images 2000] [--size 32] [--output_dir dataset]
```

- Default grid sampling: create a sqrt(N) × sqrt(N) grid over [0,1]² with slight random jitter
- If N is not a perfect square, use the nearest square and add random samples to reach N

## Dependencies

Only use: `numpy`, `PIL` (Pillow). No PyTorch, no matplotlib (except for the preview grid).

## Quality Criteria

The images must:
1. Be immediately recognizable as stylized sunrises
2. Show smooth, continuous variation across the parameter space
3. Have the sun visibly move across the image as sun_x changes
4. Have the sky colors and brightness change as sun_y changes
5. Look aesthetically pleasing — warm colors, soft gradients, no harsh artifacts
6. Run fast: < 30 seconds for 2000 images at 32×32

## Preview Grid

Generate a 10×10 grid where:
- Horizontal axis = sun_x (0 to 1, left to right)
- Vertical axis = sun_y (0 to 1, bottom to top)
- Each cell shows the sunrise for that (sun_x, sun_y)
- Save as `preview.png` at reasonable resolution (e.g., 640×640)
