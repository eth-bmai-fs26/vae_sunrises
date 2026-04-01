"""Synthetic sunrise image generator.

Generates 32x32 RGB sunrise images parameterized by (sun_x, sun_y).
  sun_x ∈ [0,1]: horizontal sun position (winter → summer)
  sun_y ∈ [0,1]: sun elevation (dawn → noon)
"""

import argparse
import math
import os

import numpy as np
from PIL import Image


# ---------------------------------------------------------------------------
# Reference sky palettes: each is a list of (row_fraction, RGB) color stops.
# We define four palettes keyed by sun_y, and interpolate between them.
# ---------------------------------------------------------------------------

# Dawn  (sun_y ≈ 0)
_PALETTE_DAWN = np.array([
    [0.08, 0.04, 0.18],  # top: dark indigo
    [0.20, 0.08, 0.28],  # deep violet
    [0.70, 0.25, 0.35],  # rose
    [0.90, 0.60, 0.20],  # gold at horizon
])

# Early morning (sun_y ≈ 0.3)
_PALETTE_EARLY = np.array([
    [0.05, 0.05, 0.20],  # navy
    [0.15, 0.25, 0.55],  # blue
    [0.85, 0.60, 0.45],  # peach
    [0.90, 0.50, 0.15],  # orange at horizon
])

# Mid morning (sun_y ≈ 0.7)
_PALETTE_MID = np.array([
    [0.15, 0.30, 0.65],  # blue
    [0.40, 0.60, 0.85],  # light blue
    [0.80, 0.80, 0.60],  # pale yellow
    [0.90, 0.85, 0.55],  # yellow at horizon
])

# Noon (sun_y ≈ 1.0)
_PALETTE_NOON = np.array([
    [0.10, 0.20, 0.55],  # deep blue
    [0.30, 0.55, 0.85],  # sky blue
    [0.70, 0.80, 0.95],  # light sky
    [0.90, 0.90, 0.92],  # white at horizon
])

_PALETTES = np.stack([_PALETTE_DAWN, _PALETTE_EARLY, _PALETTE_MID, _PALETTE_NOON])
_PALETTE_Y_KEYS = np.array([0.0, 0.3, 0.7, 1.0])

# Row fractions where each colour stop sits (same for every palette)
_STOP_ROWS = np.array([0.0, 0.33, 0.66, 1.0])


def _interpolate_palette(sun_y: float, sun_x: float) -> np.ndarray:
    """Return a (4, 3) palette interpolated for the given sun_y, then
    warm-shifted by sun_x."""
    # Piecewise-linear interp between the 4 reference palettes
    idx = np.searchsorted(_PALETTE_Y_KEYS, sun_y, side="right") - 1
    idx = np.clip(idx, 0, len(_PALETTE_Y_KEYS) - 2)
    t = (sun_y - _PALETTE_Y_KEYS[idx]) / (_PALETTE_Y_KEYS[idx + 1] - _PALETTE_Y_KEYS[idx])
    palette = (1 - t) * _PALETTES[idx] + t * _PALETTES[idx + 1]

    # sun_x warmth shift: push towards orange/gold, boost saturation
    warm_shift = np.array([0.08, 0.02, -0.06])  # add red/green, remove blue
    palette = palette + warm_shift * (sun_x - 0.5) * 2  # centred at 0.5
    return np.clip(palette, 0, 1)


def render_image(sun_x: float, sun_y: float, size: int = 32) -> np.ndarray:
    """Render a single sunrise image as (size, size, 3) float32 in [0,1]."""
    img = np.zeros((size, size, 3), dtype=np.float32)

    palette = _interpolate_palette(sun_y, sun_x)

    # ---- 1. Sky gradient ----
    row_fracs = np.linspace(0, 1, size).reshape(-1, 1)  # (H, 1)
    # Interpolate across the 4 colour stops
    for i in range(len(_STOP_ROWS) - 1):
        mask = (row_fracs >= _STOP_ROWS[i]) & (row_fracs <= _STOP_ROWS[i + 1])
        t = (row_fracs - _STOP_ROWS[i]) / (_STOP_ROWS[i + 1] - _STOP_ROWS[i])
        blend = (1 - t) * palette[i] + t * palette[i + 1]  # (H, 3)
        # broadcast across width
        for c in range(3):
            ch = blend[:, c:c+1] * np.ones((1, size))
            img[:, :, c] = np.where(mask, ch, img[:, :, c])

    # ---- 2. Sun disc (Gaussian blob) ----
    sx = sun_x * size
    sy = (1 - sun_y) * size * 0.7 + 0.1 * size
    radius = size * 0.12  # ~3.8 px at 32

    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    dist2 = (xx - sx) ** 2 + (yy - sy) ** 2
    sun_blob = np.exp(-dist2 / (2 * radius ** 2))

    # Sun colour depends on elevation
    if sun_y < 0.3:
        sun_color = np.array([1.0, 0.45, 0.15])  # deep orange
    elif sun_y < 0.7:
        t = (sun_y - 0.3) / 0.4
        sun_color = (1 - t) * np.array([1.0, 0.65, 0.2]) + t * np.array([1.0, 0.9, 0.5])
    else:
        t = (sun_y - 0.7) / 0.3
        sun_color = (1 - t) * np.array([1.0, 0.9, 0.5]) + t * np.array([1.0, 0.98, 0.85])

    for c in range(3):
        img[:, :, c] = img[:, :, c] + sun_blob * sun_color[c] * 1.2

    # ---- 3. Atmospheric glow ----
    glow_radius = size * 0.5
    glow = np.exp(-dist2 / (2 * glow_radius ** 2))
    glow_intensity = 0.4 * max(0, 1 - sun_y * 1.5)  # stronger at low sun
    glow_color = np.array([0.9, 0.55, 0.15])
    for c in range(3):
        img[:, :, c] = img[:, :, c] + glow * glow_color[c] * glow_intensity

    # ---- 4. Horizon silhouette ----
    horizon_base = int(size * 0.85)
    # gentle hills via sine
    phase = sun_x * 2 * math.pi
    hill_y = np.sin(np.linspace(0, 2 * math.pi, size) + phase) * size * 0.03
    for col in range(size):
        h = int(horizon_base + hill_y[col])
        h = max(0, min(size - 1, h))
        # dark land colour: blend dark blue-black to dark green-brown by sun_x
        land_a = np.array([0.04, 0.04, 0.10])
        land_b = np.array([0.10, 0.16, 0.10])
        land_color = (1 - sun_x) * land_a + sun_x * land_b
        img[h:, col, :] = land_color

    # ---- 5. Noise & clip ----
    img += np.random.normal(0, 0.01, img.shape).astype(np.float32)
    np.clip(img, 0, 1, out=img)

    return img


def generate_dataset(n_images: int = 2000, size: int = 32, seed: int = 42):
    """Generate n_images sunrise images with grid+jitter sampling."""
    rng = np.random.RandomState(seed)
    grid_side = int(math.isqrt(n_images))
    n_grid = grid_side * grid_side
    n_extra = n_images - n_grid

    # Grid coordinates with jitter
    ticks = np.linspace(0, 1, grid_side, endpoint=True)
    gx, gy = np.meshgrid(ticks, ticks)
    coords = np.stack([gx.ravel(), gy.ravel()], axis=1)
    jitter = rng.uniform(-0.5 / grid_side, 0.5 / grid_side, coords.shape)
    coords = np.clip(coords + jitter, 0, 1)

    # Extra random samples if needed
    if n_extra > 0:
        extra = rng.uniform(0, 1, (n_extra, 2))
        coords = np.concatenate([coords, extra], axis=0)

    coords = coords.astype(np.float32)

    images = np.empty((n_images, size, size, 3), dtype=np.float32)
    for i in range(n_images):
        images[i] = render_image(coords[i, 0], coords[i, 1], size)

    return images, coords


def make_preview(images: np.ndarray, coords: np.ndarray, size: int = 32,
                 grid_n: int = 10, out_path: str = "preview.png"):
    """Create a 10x10 grid preview sampling the parameter space."""
    cell = size * 2  # upscale each cell for visibility
    canvas = np.zeros((grid_n * cell, grid_n * cell, 3), dtype=np.float32)

    for iy in range(grid_n):
        for ix in range(grid_n):
            target_x = ix / (grid_n - 1)
            target_y = 1.0 - iy / (grid_n - 1)  # bottom=0, top=1
            img = render_image(target_x, target_y, size)
            # Upscale with nearest neighbour
            big = np.repeat(np.repeat(img, cell // size, axis=0), cell // size, axis=1)
            canvas[iy * cell:(iy + 1) * cell, ix * cell:(ix + 1) * cell] = big

    canvas_uint8 = (canvas * 255).clip(0, 255).astype(np.uint8)
    Image.fromarray(canvas_uint8).save(out_path)


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic sunrise dataset")
    parser.add_argument("--n_images", type=int, default=2000)
    parser.add_argument("--size", type=int, default=32)
    parser.add_argument("--output_dir", type=str, default="dataset")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Generating {args.n_images} images at {args.size}x{args.size}...")
    images, coords = generate_dataset(args.n_images, args.size)

    np.save(os.path.join(args.output_dir, "images.npy"), images)
    np.save(os.path.join(args.output_dir, "coords.npy"), coords)
    print(f"Saved images.npy {images.shape} and coords.npy {coords.shape}")

    preview_path = os.path.join(args.output_dir, "preview.png")
    make_preview(images, coords, args.size, out_path=preview_path)
    print(f"Saved {preview_path}")


if __name__ == "__main__":
    main()
