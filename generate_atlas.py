"""Generate a sprite atlas of decoded images from a grid of latent space points.

Produces a 24×24 grid of 64×64 cells → 1536×1536 atlas image.
"""

import argparse
import os

import numpy as np
import torch
from PIL import Image

from models.vae import SunriseVAE


def generate_atlas(
    checkpoint_path: str,
    grid_size: int = 24,
    cell_size: int = 64,
    output_dir: str = "web/assets/sprites",
):
    """Generate sprite atlas by decoding a grid of latent space points."""
    # Load model
    vae = SunriseVAE(latent_dim=2, img_size=32)
    state = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    vae.load_state_dict(state)
    vae.eval()

    # Generate grid of z values in [-3, 3]²
    ticks = np.linspace(-3, 3, grid_size, dtype=np.float32)
    zx, zy = np.meshgrid(ticks, ticks)
    # zy goes top-to-bottom, so flip so row 0 = z_y=+3 (top of atlas = high z_y)
    zy = zy[::-1].copy()

    atlas_size = grid_size * cell_size
    atlas = np.zeros((atlas_size, atlas_size, 3), dtype=np.uint8)

    with torch.no_grad():
        for row in range(grid_size):
            # Batch decode an entire row
            z_row = torch.tensor(
                np.stack([zx[row], zy[row]], axis=1), dtype=torch.float32
            )
            decoded = vae.decode(z_row)  # (grid_size, 3, 32, 32)
            decoded = decoded.permute(0, 2, 3, 1).numpy()  # (grid_size, 32, 32, 3)
            decoded = np.clip(decoded * 255, 0, 255).astype(np.uint8)

            for col in range(grid_size):
                img = Image.fromarray(decoded[col])
                if cell_size != 32:
                    img = img.resize((cell_size, cell_size), Image.BILINEAR)
                y0 = row * cell_size
                x0 = col * cell_size
                atlas[y0:y0 + cell_size, x0:x0 + cell_size] = np.array(img)

    os.makedirs(output_dir, exist_ok=True)
    atlas_img = Image.fromarray(atlas)

    # Save as WebP (primary) and PNG (fallback)
    webp_path = os.path.join(output_dir, "atlas.webp")
    png_path = os.path.join(output_dir, "atlas.png")

    atlas_img.save(webp_path, "WEBP", quality=90)
    print(f"Saved atlas: {webp_path} ({os.path.getsize(webp_path):,} bytes)")

    atlas_img.save(png_path, "PNG")
    print(f"Saved atlas: {png_path} ({os.path.getsize(png_path):,} bytes)")

    print(f"Atlas: {grid_size}×{grid_size} grid, {cell_size}×{cell_size} cells, "
          f"{atlas_size}×{atlas_size} total")


def main():
    parser = argparse.ArgumentParser(description="Generate sprite atlas from VAE decoder")
    parser.add_argument("--checkpoint", default="checkpoints/vae_final.pt")
    parser.add_argument("--grid_size", type=int, default=24)
    parser.add_argument("--cell_size", type=int, default=64)
    parser.add_argument("--output_dir", default="web/assets/sprites")
    args = parser.parse_args()

    generate_atlas(args.checkpoint, args.grid_size, args.cell_size, args.output_dir)


if __name__ == "__main__":
    main()
