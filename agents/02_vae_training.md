# Agent 2: VAE Training Pipeline

## Your Task

Create a PyTorch VAE training pipeline that learns to encode and decode the synthetic sunrise images with a 2-dimensional latent space.

## Prerequisites

Run `python generate_dataset.py` first if `dataset/images.npy` doesn't exist.

## Files to Create

### `models/vae.py` — Model Definition

```python
class SunriseVAE(nn.Module):
    def __init__(self, latent_dim=2, img_size=32):
        ...
    def encode(self, x):  # returns mu, logvar
        ...
    def reparameterize(self, mu, logvar):  # returns z
        ...
    def decode(self, z):  # returns reconstructed image
        ...
    def forward(self, x):  # returns recon_x, mu, logvar
        ...
```

**Encoder architecture** (for 32×32×3 input):
- Conv2d(3, 32, 3, stride=2, padding=1) → ReLU  → 16×16
- Conv2d(32, 64, 3, stride=2, padding=1) → ReLU  → 8×8
- Conv2d(64, 128, 3, stride=2, padding=1) → ReLU → 4×4
- Flatten → Linear(128×4×4, 256) → ReLU
- Linear(256, 2) for mu, Linear(256, 2) for logvar

**Decoder architecture** (for z ∈ R²):
- Linear(2, 256) → ReLU
- Linear(256, 128×4×4) → ReLU → Reshape to 128×4×4
- ConvTranspose2d(128, 64, 4, stride=2, padding=1) → ReLU → 8×8
- ConvTranspose2d(64, 32, 4, stride=2, padding=1) → ReLU → 16×16
- ConvTranspose2d(32, 3, 4, stride=2, padding=1) → Sigmoid → 32×32×3

### `train_vae.py` — Training Script

**Data loading:**
- Load `dataset/images.npy` and `dataset/coords.npy`
- Transpose images to (N, 3, 32, 32) for PyTorch (channels first)
- 90/10 train/val split
- DataLoader with batch_size=64, shuffle=True

**Loss function:**
```python
def vae_loss(recon_x, x, mu, logvar, beta=1.0):
    recon_loss = F.mse_loss(recon_x, x, reduction='sum') / x.size(0)
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp()) / x.size(0)
    return recon_loss + beta * kl_loss, recon_loss, kl_loss
```

**Training loop:**
- Adam optimizer, lr=1e-3
- 200 epochs (with early stopping if val loss doesn't improve for 20 epochs)
- Log train/val loss every epoch
- Save best model by val loss

**CLI:**
```bash
python train_vae.py [--epochs 200] [--batch_size 64] [--lr 1e-3] [--beta 1.0] [--latent_dim 2] [--data_dir dataset] [--output_dir checkpoints]
```

## Outputs

All saved to `checkpoints/`:

1. **`vae_final.pt`** — best model state_dict
2. **`training_log.json`** — per-epoch: `{epoch, train_loss, val_loss, recon_loss, kl_loss}`
3. **`reconstructions.png`** — 2 rows: top = 10 original images, bottom = their reconstructions
4. **`latent_space.png`** — scatter plot of all training images encoded to 2D:
   - x-axis: z₁, y-axis: z₂
   - Color-coded by sun_x (one plot) and sun_y (another plot), side by side
   - Should show smooth gradient of colors = the latent space captured the structure
5. **`latent_grid.png`** — 10×10 grid of decoded images from evenly spaced z values in [-3, 3]²
   - Shows what the decoder generates across the latent space

## Quality Criteria

1. **Reconstructions must be recognizable** — the sunrise structure (sky gradient, sun position, horizon) should be clearly preserved
2. **Latent space must be structured** — the scatter plot should show a smooth distribution, not a collapsed point or random scatter. z₁ and z₂ should correlate with sun_x and sun_y (possibly rotated).
3. **Loss must converge** — training loss should decrease and stabilize
4. **Training must be fast** — < 5 minutes on CPU for 2000 images at 32×32
5. **No mode collapse** — the latent_grid.png should show diverse sunrises, not all the same image

## Tips

- If the KL loss dominates early and causes posterior collapse (all z values cluster at 0), try KL warmup: linearly increase beta from 0 to 1 over the first 50 epochs
- 32×32 is small — the model should be small too. Don't over-parameterize.
- Print loss every 10 epochs to show progress
