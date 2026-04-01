#!/usr/bin/env python3
"""Train a VAE on synthetic sunrise images.

Usage:
    python train_vae.py [--epochs 200] [--batch_size 64] [--lr 1e-3]
                        [--beta 1.0] [--latent_dim 2]
                        [--data_dir dataset] [--output_dir checkpoints]
"""

import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

from models.vae import SunriseVAE


def vae_loss(recon_x, x, mu, logvar, beta=1.0):
    """VAE loss = reconstruction + beta * KL divergence."""
    recon_loss = F.mse_loss(recon_x, x, reduction="sum") / x.size(0)
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp()) / x.size(0)
    return recon_loss + beta * kl_loss, recon_loss, kl_loss


def load_data(data_dir, val_split=0.1):
    """Load dataset and create train/val DataLoaders."""
    images = np.load(os.path.join(data_dir, "images.npy"))  # (N, 32, 32, 3)
    coords = np.load(os.path.join(data_dir, "coords.npy"))  # (N, 2)

    # Transpose to channels-first: (N, 3, 32, 32)
    images = np.transpose(images, (0, 3, 1, 2))

    # Train/val split
    n = len(images)
    n_val = int(n * val_split)
    n_train = n - n_val

    perm = np.random.RandomState(42).permutation(n)
    train_idx = perm[:n_train]
    val_idx = perm[n_train:]

    train_images = torch.from_numpy(images[train_idx])
    val_images = torch.from_numpy(images[val_idx])
    train_coords = coords[train_idx]
    val_coords = coords[val_idx]

    return train_images, val_images, train_coords, val_coords, images, coords


def save_reconstructions(model, val_images, output_dir, device):
    """Save original vs reconstructed comparison."""
    model.eval()
    with torch.no_grad():
        sample = val_images[:10].to(device)
        recon, _, _ = model(sample)

    fig, axes = plt.subplots(2, 10, figsize=(20, 4))
    for i in range(10):
        # Original
        img = sample[i].cpu().numpy().transpose(1, 2, 0)
        axes[0, i].imshow(img)
        axes[0, i].axis("off")
        if i == 0:
            axes[0, i].set_title("Original", fontsize=10)
        # Reconstruction
        img = recon[i].cpu().numpy().transpose(1, 2, 0)
        axes[1, i].imshow(img)
        axes[1, i].axis("off")
        if i == 0:
            axes[1, i].set_title("Reconstructed", fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "reconstructions.png"), dpi=150)
    plt.close()


def save_latent_space(model, all_images, all_coords, output_dir, device):
    """Save latent space scatter plots colored by sun_x and sun_y."""
    model.eval()
    all_mu = []
    with torch.no_grad():
        # Encode in batches
        dataset = torch.from_numpy(np.transpose(all_images, (0, 3, 1, 2)) if all_images.ndim == 4 and all_images.shape[-1] == 3 else all_images)
        for i in range(0, len(dataset), 128):
            batch = dataset[i : i + 128].to(device)
            mu, _ = model.encode(batch)
            all_mu.append(mu.cpu().numpy())
    all_mu = np.concatenate(all_mu, axis=0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    sc1 = ax1.scatter(all_mu[:, 0], all_mu[:, 1], c=all_coords[:, 0],
                      cmap="coolwarm", s=4, alpha=0.7)
    ax1.set_xlabel("z₁")
    ax1.set_ylabel("z₂")
    ax1.set_title("Latent space colored by sun_x (season)")
    plt.colorbar(sc1, ax=ax1, label="sun_x")

    sc2 = ax2.scatter(all_mu[:, 0], all_mu[:, 1], c=all_coords[:, 1],
                      cmap="viridis", s=4, alpha=0.7)
    ax2.set_xlabel("z₁")
    ax2.set_ylabel("z₂")
    ax2.set_title("Latent space colored by sun_y (time of day)")
    plt.colorbar(sc2, ax=ax2, label="sun_y")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "latent_space.png"), dpi=150)
    plt.close()


def save_latent_grid(model, output_dir, device, grid_n=10):
    """Save a grid of decoded images from evenly spaced z values in [-3, 3]²."""
    model.eval()
    z1 = np.linspace(-3, 3, grid_n)
    z2 = np.linspace(-3, 3, grid_n)

    fig, axes = plt.subplots(grid_n, grid_n, figsize=(12, 12))
    with torch.no_grad():
        for i, z2_val in enumerate(reversed(z2)):  # top=high z2
            for j, z1_val in enumerate(z1):
                z = torch.tensor([[z1_val, z2_val]], dtype=torch.float32).to(device)
                img = model.decode(z)[0].cpu().numpy().transpose(1, 2, 0)
                axes[i, j].imshow(img)
                axes[i, j].axis("off")

    plt.suptitle("Decoded latent grid z ∈ [-3, 3]²", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "latent_grid.png"), dpi=100)
    plt.close()


def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    os.makedirs(args.output_dir, exist_ok=True)

    # Load data
    train_images, val_images, train_coords, val_coords, all_images_np, all_coords_np = load_data(args.data_dir)
    train_loader = DataLoader(
        TensorDataset(train_images), batch_size=args.batch_size, shuffle=True
    )
    val_loader = DataLoader(
        TensorDataset(val_images), batch_size=args.batch_size, shuffle=False
    )
    print(f"Train: {len(train_images)}, Val: {len(val_images)}")

    # Model
    model = SunriseVAE(latent_dim=args.latent_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    param_count = sum(p.numel() for p in model.parameters())
    print(f"Model parameters: {param_count:,}")

    # Training loop
    best_val_loss = float("inf")
    patience_counter = 0
    training_log = []

    # KL warmup: linearly increase beta from 0 to target over first 50 epochs
    kl_warmup_epochs = 50

    for epoch in range(1, args.epochs + 1):
        # KL warmup
        beta = args.beta * min(1.0, epoch / kl_warmup_epochs)

        # Train
        model.train()
        train_total = 0.0
        train_recon = 0.0
        train_kl = 0.0
        n_batches = 0

        for (batch,) in train_loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            recon, mu, logvar = model(batch)
            loss, recon_l, kl_l = vae_loss(recon, batch, mu, logvar, beta)
            loss.backward()
            optimizer.step()

            train_total += loss.item()
            train_recon += recon_l.item()
            train_kl += kl_l.item()
            n_batches += 1

        train_total /= n_batches
        train_recon /= n_batches
        train_kl /= n_batches

        # Validate
        model.eval()
        val_total = 0.0
        val_recon = 0.0
        val_kl = 0.0
        n_val = 0
        with torch.no_grad():
            for (batch,) in val_loader:
                batch = batch.to(device)
                recon, mu, logvar = model(batch)
                loss, recon_l, kl_l = vae_loss(recon, batch, mu, logvar, beta)
                val_total += loss.item()
                val_recon += recon_l.item()
                val_kl += kl_l.item()
                n_val += 1

        val_total /= n_val
        val_recon /= n_val
        val_kl /= n_val

        training_log.append({
            "epoch": epoch,
            "train_loss": round(train_total, 6),
            "val_loss": round(val_total, 6),
            "recon_loss": round(train_recon, 6),
            "kl_loss": round(train_kl, 6),
            "beta": round(beta, 4),
        })

        if epoch % 10 == 0 or epoch == 1:
            print(
                f"Epoch {epoch:3d} | train {train_total:.4f} (recon {train_recon:.4f}, "
                f"kl {train_kl:.4f}) | val {val_total:.4f} | β={beta:.3f}"
            )

        # Early stopping
        if val_total < best_val_loss:
            best_val_loss = val_total
            patience_counter = 0
            torch.save(model.state_dict(), os.path.join(args.output_dir, "vae_final.pt"))
        else:
            patience_counter += 1
            if patience_counter >= 20:
                print(f"Early stopping at epoch {epoch}")
                break

    # Save training log
    with open(os.path.join(args.output_dir, "training_log.json"), "w") as f:
        json.dump(training_log, f, indent=2)

    # Load best model for visualizations
    model.load_state_dict(torch.load(os.path.join(args.output_dir, "vae_final.pt"), weights_only=True))

    print("Generating visualizations...")
    save_reconstructions(model, val_images, args.output_dir, device)
    save_latent_space(model, all_images_np, all_coords_np, args.output_dir, device)
    save_latent_grid(model, args.output_dir, device)

    print(f"Done! Outputs saved to {args.output_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Train VAE on sunrise dataset")
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--beta", type=float, default=1.0)
    parser.add_argument("--latent_dim", type=int, default=2)
    parser.add_argument("--data_dir", type=str, default="dataset")
    parser.add_argument("--output_dir", type=str, default="checkpoints")
    args = parser.parse_args()
    train(args)


if __name__ == "__main__":
    main()
