"""Sunrise VAE model definition.

Small convolutional VAE with 2D latent space for 32×32×3 sunrise images.
"""

import torch
import torch.nn as nn


class SunriseVAE(nn.Module):
    def __init__(self, latent_dim=2, img_size=32):
        super().__init__()
        self.latent_dim = latent_dim
        self.img_size = img_size

        # Encoder: 32×32×3 → 2D latent
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 32, 3, stride=2, padding=1),   # → 16×16
            nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1),  # → 8×8
            nn.ReLU(),
            nn.Conv2d(64, 128, 3, stride=2, padding=1), # → 4×4
            nn.ReLU(),
            nn.Flatten(),                                # → 128*4*4 = 2048
            nn.Linear(128 * 4 * 4, 256),
            nn.ReLU(),
        )
        self.fc_mu = nn.Linear(256, latent_dim)
        self.fc_logvar = nn.Linear(256, latent_dim)

        # Decoder: 2D latent → 32×32×3
        self.decoder_fc = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128 * 4 * 4),
            nn.ReLU(),
        )
        self.decoder_conv = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 4, stride=2, padding=1),  # → 8×8
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1),   # → 16×16
            nn.ReLU(),
            nn.ConvTranspose2d(32, 3, 4, stride=2, padding=1),    # → 32×32
            nn.Sigmoid(),
        )

    def encode(self, x):
        """Encode input images to latent distribution parameters.

        Args:
            x: (B, 3, 32, 32) tensor

        Returns:
            mu: (B, latent_dim) mean
            logvar: (B, latent_dim) log-variance
        """
        h = self.encoder(x)
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu, logvar):
        """Sample z from q(z|x) using reparameterization trick."""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        """Decode latent vectors to images.

        Args:
            z: (B, latent_dim) tensor

        Returns:
            (B, 3, 32, 32) reconstructed images in [0, 1]
        """
        h = self.decoder_fc(z)
        h = h.view(-1, 128, 4, 4)
        return self.decoder_conv(h)

    def forward(self, x):
        """Full forward pass: encode → sample → decode.

        Returns:
            recon_x: (B, 3, 32, 32) reconstructed images
            mu: (B, latent_dim) mean
            logvar: (B, latent_dim) log-variance
        """
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar
