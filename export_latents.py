"""Export latent coordinates for all training images and generate thumbnails sprite sheet.

Outputs:
  - web/assets/data/latent_coords.json
  - web/assets/sprites/thumbnails.webp
"""

import argparse
import json
import math
import os

import numpy as np
import torch
from PIL import Image

from models.vae import SunriseVAE


def export_latents(
    checkpoint_path: str,
    data_dir: str = "dataset",
    output_dir: str = "web/assets",
):
    """Encode all training images and export latent coords + thumbnails."""
    # Load model
    vae = SunriseVAE(latent_dim=2, img_size=32)
    state = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    vae.load_state_dict(state)
    vae.eval()

    # Load dataset
    images = np.load(os.path.join(data_dir, "images.npy"))  # (N, 32, 32, 3)
    coords = np.load(os.path.join(data_dir, "coords.npy"))  # (N, 2) → (sun_x, sun_y)
    n_images = len(images)
    print(f"Loaded {n_images} images and coords")

    # Encode all images (in batches)
    # Images are (N, H, W, C) float32 [0,1] — convert to (N, C, H, W) for PyTorch
    images_chw = torch.from_numpy(images).permute(0, 3, 1, 2).float()

    all_mu = []
    all_logvar = []
    batch_size = 256
    with torch.no_grad():
        for i in range(0, n_images, batch_size):
            batch = images_chw[i:i + batch_size]
            mu, logvar = vae.encode(batch)
            all_mu.append(mu.numpy())
            all_logvar.append(logvar.numpy())

    all_mu = np.concatenate(all_mu, axis=0)
    all_logvar = np.concatenate(all_logvar, axis=0)

    # Build JSON records
    records = []
    for i in range(n_images):
        records.append({
            "z": [round(float(all_mu[i, 0]), 4), round(float(all_mu[i, 1]), 4)],
            "sun_x": round(float(coords[i, 0]), 4),
            "sun_y": round(float(coords[i, 1]), 4),
            "thumb_idx": i,
        })

    # Save JSON
    data_out = os.path.join(output_dir, "data")
    os.makedirs(data_out, exist_ok=True)
    json_path = os.path.join(data_out, "latent_coords.json")
    with open(json_path, "w") as f:
        json.dump(records, f)
    print(f"Saved {json_path} ({os.path.getsize(json_path):,} bytes, {n_images} records)")

    # Print z-value statistics
    z_min = all_mu.min(axis=0)
    z_max = all_mu.max(axis=0)
    print(f"z ranges: z0=[{z_min[0]:.2f}, {z_max[0]:.2f}], z1=[{z_min[1]:.2f}, {z_max[1]:.2f}]")

    # Generate thumbnails sprite sheet
    cols = math.ceil(math.sqrt(n_images))
    rows = math.ceil(n_images / cols)
    thumb_size = 32
    sheet_w = cols * thumb_size
    sheet_h = rows * thumb_size

    sheet = np.zeros((sheet_h, sheet_w, 3), dtype=np.uint8)
    for i in range(n_images):
        r = i // cols
        c = i % cols
        img_uint8 = np.clip(images[i] * 255, 0, 255).astype(np.uint8)
        y0 = r * thumb_size
        x0 = c * thumb_size
        sheet[y0:y0 + thumb_size, x0:x0 + thumb_size] = img_uint8

    sprites_dir = os.path.join(output_dir, "sprites")
    os.makedirs(sprites_dir, exist_ok=True)

    sheet_img = Image.fromarray(sheet)
    webp_path = os.path.join(sprites_dir, "thumbnails.webp")
    sheet_img.save(webp_path, "WEBP", quality=90)
    print(f"Saved {webp_path} ({os.path.getsize(webp_path):,} bytes, "
          f"{cols}×{rows} grid = {sheet_w}×{sheet_h} px)")


def main():
    parser = argparse.ArgumentParser(description="Export latent coordinates and thumbnails")
    parser.add_argument("--checkpoint", default="checkpoints/vae_final.pt")
    parser.add_argument("--data_dir", default="dataset")
    parser.add_argument("--output_dir", default="web/assets")
    args = parser.parse_args()

    export_latents(args.checkpoint, args.data_dir, args.output_dir)


if __name__ == "__main__":
    main()
