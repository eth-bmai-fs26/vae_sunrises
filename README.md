# Sunrise Machine

An interactive visualization of Variational Autoencoders (VAEs) using procedurally generated sunrises. Explore a 2D latent space, decode sunrises in real time, watch an encoder particle animation, and play "Find the Sunrise."

## Quick Start (Web App Only)

The web app is a single HTML file with all dependencies loaded from CDNs. Just serve the `web/` directory:

```bash
cd web
python3 -m http.server 8000
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

> **Note:** The pre-built model and sprite assets are already committed in `web/assets/`. You only need the Python pipeline below if you want to regenerate them.

## Full Pipeline Setup

If you want to regenerate the dataset, retrain the VAE, or re-export the model:

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate the dataset

```bash
python generate_dataset.py
```

This creates `dataset/images.npy`, `dataset/coords.npy`, and `dataset/preview.png` (2000 synthetic 32x32 sunrise images).

### 4. Train the VAE

```bash
python train_vae.py
```

Trains for 200 epochs on CPU (takes ~2-3 minutes). Outputs to `checkpoints/`:
- `vae_final.pt` — trained weights
- `training_log.json` — loss curves
- `reconstructions.png` — original vs. reconstructed comparison
- `latent_space.png` — 2D scatter of encoded training data

### 5. Export to TF.js and generate web assets

```bash
python export_tfjs.py          # Exports decoder to web/assets/model/
python export_latents.py       # Exports latent coordinates to web/assets/data/
python generate_atlas.py       # Generates sprite atlas to web/assets/sprites/
```

### 6. Launch the web app

```bash
cd web
python3 -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000).

## Project Structure

```
├── generate_dataset.py        # Synthetic sunrise generator (NumPy + PIL)
├── train_vae.py               # VAE training pipeline (PyTorch)
├── models/vae.py              # VAE model definition
├── export_tfjs.py             # PyTorch → TF.js decoder export
├── export_latents.py          # Encode training set → JSON coordinates
├── generate_atlas.py          # Pre-computed sprite atlas for fallback
├── requirements.txt           # Python dependencies
├── dataset/                   # Generated training data
├── checkpoints/               # Trained model + diagnostics
└── web/
    ├── index.html             # Single-file web app (HTML + CSS + JS)
    └── assets/
        ├── model/             # TF.js decoder model
        ├── sprites/           # Sprite atlas + thumbnails
        └── data/              # Latent coordinates JSON
```

## Requirements

- **Python 3.10+** for the training pipeline
- A modern browser (Chrome, Firefox, Safari, Edge) for the web app
- No Node.js or build tools needed — the web app uses CDN-loaded libraries
