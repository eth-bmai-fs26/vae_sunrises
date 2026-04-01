# Implementation Agents — Launch Order

This document defines 7 agents (GitHub issues) to implement the Sunrise Machine.
Launch them sequentially in Vibe Kanban. Each agent builds on the previous.

---

## Overview

```
Agent 1: Synthetic Sunrise Generator     (no dependencies)
Agent 2: VAE Training Pipeline           (depends on Agent 1)
Agent 3: Model Export & Sprite Atlas     (depends on Agent 2)
Agent 4: Phase 1 — Scrollytelling Shell  (depends on Agent 3)
Agent 5: Phase 2 — Core Interactions     (depends on Agent 4)
Agent 6: Phase 2b — Encoder & Disclosure (depends on Agent 5)
Agent 7: Phase 3 — Polish & Games        (depends on Agent 6)
```

---

## Agent 1: Synthetic Sunrise Generator

**Title:** `Generate synthetic sunrise dataset`

**What it builds:**
A Python script (`generate_dataset.py`) that procedurally creates 32×32 sunrise images from two parameters:
- `sun_x` ∈ [0, 1]: horizontal sun position (time of year)
- `sun_y` ∈ [0, 1]: vertical sun position / elevation (time of day)

These two numbers fully determine: sky gradient colors, sun disc position and color, atmospheric glow, horizon silhouette.

**Deliverables:**
- `generate_dataset.py` — pure NumPy + PIL, no PyTorch
- Outputs: `dataset/images.npy` (N×32×32×3, float32 [0,1]), `dataset/coords.npy` (N×2)
- Outputs: `dataset/preview.png` — grid showing sunrises across the (sun_x, sun_y) space
- Default: 2000 images on a grid sampling of the parameter space
- Flags: `--n_images`, `--size`, `--output_dir`

**Rendering recipe:**
1. Sky gradient: vertical color blend. When sun_y is low (dawn), use indigo→violet→rose→gold. When high (noon), blue→light blue→white. sun_x (time of year) shifts the palette warmth — winter is cooler/bluer, summer is warmer/more orange.
2. Sun disc: Gaussian blob at position (sun_x × width, (1 - sun_y) × height × 0.7). Color: deep orange when low, golden-white when high.
3. Atmospheric glow: large soft radial gradient centered on sun, tinting nearby sky pixels warm.
4. Horizon: dark silhouette at bottom ~15%, slight variation (low-frequency sine wave).
5. Optional color noise: tiny per-pixel jitter for texture.

**Acceptance criteria:**
- `python generate_dataset.py` runs in < 30 seconds for 2000 images at 32×32
- Preview grid shows visually distinct, recognizable sunrises
- Smooth variation: adjacent parameter values produce visually similar images
- Images look like stylized sunrises, not random noise

**Agent instructions:** See `agents/01_dataset_generator.md`

---

## Agent 2: VAE Training Pipeline

**Title:** `Train VAE on synthetic sunrises`

**Depends on:** Agent 1 (dataset must exist in `dataset/`)

**What it builds:**
A PyTorch training script that trains a small VAE with 2-dimensional latent space on the synthetic sunrise dataset.

**Deliverables:**
- `train_vae.py` — PyTorch training script
- `models/vae.py` — VAE model definition (encoder + decoder)
- Outputs: `checkpoints/vae_final.pt` — trained model weights
- Outputs: `checkpoints/training_log.json` — loss curves
- Outputs: `checkpoints/reconstructions.png` — original vs. reconstructed comparison
- Outputs: `checkpoints/latent_space.png` — 2D scatter of encoded training data, colored by sun_x and sun_y

**Architecture:**
- Encoder: Conv2D layers → flatten → Linear → (mu, logvar) each ∈ R²
- Decoder: Linear → reshape → ConvTranspose2D layers → Sigmoid → 32×32×3
- Loss: reconstruction (MSE or BCE) + β·KL divergence (β=1.0 default)
- Optimizer: Adam, lr=1e-3
- Epochs: 200 (should converge well before)
- Batch size: 64

**Key requirement:** The latent space must be interpretable — the learned z₁ and z₂ should correlate with sun_x and sun_y (possibly rotated/scaled). The latent_space.png plot should show clear structure.

**Acceptance criteria:**
- Training completes in < 5 minutes on CPU
- Reconstructions are recognizable as the original sunrises
- Latent space scatter shows smooth, structured distribution (not collapsed, not scattered)
- Loss decreases monotonically after initial warmup

**Agent instructions:** See `agents/02_vae_training.md`

---

## Agent 3: Model Export & Sprite Atlas

**Title:** `Export decoder to TF.js and generate sprite atlas`

**Depends on:** Agent 2 (trained model must exist in `checkpoints/`)

**What it builds:**
Scripts to export the trained PyTorch decoder to TensorFlow.js format and generate the pre-computed sprite atlas for the web visualization.

**Deliverables:**
- `export_decoder.py` — PyTorch → ONNX → TF.js conversion pipeline
- `generate_atlas.py` — generates the 24×24 sprite atlas PNG
- `export_latents.py` — encodes all training images and saves coordinates as JSON
- Outputs in `web/assets/`:
  - `model/decoder.json` + `model/decoder.bin` (TF.js float16)
  - `sprites/atlas.webp` (1536×1536, 24×24 grid of decoded sunrises)
  - `data/latent_coords.json` ([{z: [z1, z2], sun_x, sun_y, thumb_idx}])
  - `sprites/thumbnails.webp` (sprite sheet of training image thumbnails)

**Technical details:**
- Export: `torch.onnx.export(decoder)` → `onnx-tf` → `tensorflowjs_converter --quantize_float16`
- Atlas: decode 24×24 grid of z values in [-3, 3]², stitch into single image
- Latent coords: run encoder on full training set, save mu values

**Acceptance criteria:**
- `decoder.json` + `decoder.bin` total < 500KB
- Atlas renders correctly — visual inspection shows smooth sunrise grid
- `latent_coords.json` loads correctly and z values are in expected range
- All outputs in `web/assets/` directory, ready for the web app

**Agent instructions:** See `agents/03_model_export.md`

---

## Agent 4: Phase 1 — Scrollytelling Shell

**Title:** `Build scrollytelling skeleton with latent canvas and decode`

**Depends on:** Agent 3 (web assets must exist in `web/assets/`)

**What it builds:**
The foundational web page: scrollable 5-act structure with background gradient, latent space canvas, and working decode-on-click.

**Deliverables:**
- `web/index.html` — single HTML file with inlined CSS and JS
- Implements: P0.1 (scroll skeleton), P0.2 (background gradient), P0.5 (latent canvas), P0.9 (TF.js decode), P0.10 (sprite fallback), P0.12 (responsive), P0.13 (typography + colors)

**Specifications (from DESIGN.md):**
- 5 `<section data-act="1-5">` elements with GSAP ScrollTrigger
- Background gradient: 8 stops (#0B0E1A → #FFF8F0) scrubbed to scroll
- Latent canvas: 500×500 Canvas2D + SVG overlay with D3 axes
- Click anywhere on canvas → decode via TF.js → show 256×256 image in side panel
- Sprite atlas fallback: bilinear interpolation if WebGL unavailable
- Fonts: DM Serif Display, Inter, JetBrains Mono from Google Fonts CDN
- Color system from DESIGN.md Section 6
- Responsive: two-column desktop, single-column mobile

**CDN dependencies:**
- TensorFlow.js (core + webgl backend)
- GSAP + ScrollTrigger
- D3 (d3-scale, d3-interpolate)
- KaTeX (deferred)

**Acceptance criteria:**
- Page loads, scrolls through 5 sections with visible gradient transition
- Clicking the latent canvas decodes and displays a sunrise image
- Fallback works with sprite atlas when WebGL is disabled
- Page does not break at any viewport width (320px to 1920px)
- Console shows no errors

**Agent instructions:** See `agents/04_scroll_shell.md`

---

## Agent 5: Phase 2 — Core Interactions

**Title:** `Add hover-to-decode, pin, interpolate, and grid-to-scatter`

**Depends on:** Agent 4 (working web page with decode)

**What it builds:**
The core interactive teaching moments: real-time hover decode, pinning, interpolation, and the Act I grid animation.

**Deliverables:**
Modifications to `web/index.html` implementing:
- P0.4: Grid of ~64 training thumbnails that animate to scatter plot positions (Canvas2D, GSAP scroll-scrubbed)
- P0.6: Hover-to-decode at 30fps (rAF-throttled pointermove → decode → render)
- P0.7: Click-to-pin (up to 4 pins, numbered, color-coded, with 48×48 thumbnails)
- P0.8: Interpolation slider between any two pinned points

**Interaction specs (from DESIGN.md):**
- Hover: crosshair follows pointer, axis ticks show z₁/z₂, decoded panel updates at 30fps
- Pin: click → dot scales from 0→6px with elastic ease, thumbnail + coordinates appear
- Interpolation: select 2 pins by clicking them sequentially → line draws → slider appears → `z_interp = (1-t)*z_A + t*z_B`
- Grid-to-scatter: GSAP ScrollTrigger scrubs tile positions from grid layout to latent coordinates on a single Canvas2D
- Adaptive fallback: if decode > 33ms for 3 consecutive frames, switch to sprite atlas

**Acceptance criteria:**
- Moving pointer over canvas produces smooth, real-time sunrise morphing
- Pinning 2 points and sliding interpolation shows smooth morph between them
- Scrolling through Act I shows grid rearranging into scatter plot
- Performance: no visible jank at 30fps on modern hardware

**Agent instructions:** See `agents/05_core_interactions.md`

---

## Agent 6: Phase 2b — Encoder Animation & Progressive Disclosure

**Title:** `Add encoder particle animation and math annotations`

**Depends on:** Agent 5 (interactive latent canvas working)

**What it builds:**
Act III encoder experience and the progressive disclosure system across all acts.

**Deliverables:**
Modifications to `web/index.html` implementing:
- P0.8: Encoder particle animation (fire-once on Act III enter)
- P0.11: Progressive disclosure annotations (5 `<details>` with KaTeX)
- Post-encoding state: encoded point appears on latent canvas

**Particle animation spec:**
1. Gallery of 8-12 curated training images at top of Act III
2. User clicks an image → it enlarges in a "source panel"
3. IntersectionObserver triggers the animation:
   - Phase 1 (600ms): image pixelates, ~200 particles lift off (Canvas2D filled circles)
   - Phase 2 (800ms): particles stream along quadratic Bezier curves toward latent canvas, color blends from pixel color to encoder violet (#6C8EBF)
   - Phase 3 (600ms): particles converge to the pre-computed mu from latent_coords.json, forming a tight cluster, then a pin drops
4. After animation: decoded reconstruction appears in panel beside original

**Progressive disclosure spec:**
5 annotations (at minimum):
1. "What is latent space?" (after Act I scatter)
2. "What is a decoder?" (during Act II hover-to-decode)
3. "What is an encoder?" (during Act III)
4. "Why sample from a distribution?" (Act IV)
5. "What is KL divergence?" (Act IV)

Each: `<details>` with styled `<summary>`, KaTeX renders lazily on expand, three depth layers (intuitive → technical → deep).

**Acceptance criteria:**
- Clicking a gallery image triggers a visually compelling particle animation
- Particles carry the image's colors and blend to violet during flight
- Pin lands at correct latent position for the selected image
- All 5 annotations expand/collapse, math renders correctly
- Animation runs at 60fps with 200 particles

**Agent instructions:** See `agents/06_encoder_disclosure.md`

---

## Agent 7: Phase 3 — Polish & Games

**Title:** `Add hero animation, temperature slider, game, and polish`

**Depends on:** Agent 6 (full pipeline working)

**What it builds:**
The "wow" layer: hero animation, Act IV controls, Find the Sunrise game, and visual polish.

**Deliverables:**
Modifications to `web/index.html` implementing:
- P1.1: Hero Lissajous animation (looping decoded path on Act I load)
- P1.2: Temperature slider with filmstrip of 8 batched decodes
- P1.3: KL divergence breathing visualization + beta slider
- P1.5: "Find the Sunrise" game (3 guesses, distance scoring, 3 difficulties)
- P1.7: Post-encoding drag verification
- P1.8: Film grain overlay (CSS tiled PNG, pointer-events: none)
- P1.10: "Ghost sunrise" souvenir in Act V
- Mobile: "Tap to explore" / "Done exploring" mode switch for touch canvas

**Game spec (Find the Sunrise):**
1. Show target sunrise (decoded from random z within 2σ of training distribution)
2. User clicks latent canvas to guess — pin drops, decoded image appears beside target
3. Distance meter (0-100 score, radial gauge, red→yellow→green)
4. 3 guesses per round, 5 rounds per session
5. Difficulties: Easy (halo hint), Medium (no halo, labeled axes), Hard (hidden axes)
6. localStorage for high scores (try/catch for Safari private mode)

**Acceptance criteria:**
- Hero animation loops smoothly on page load
- Temperature slider produces visible variation in decoded samples
- Game is playable and fun — scoring works, localStorage persists
- Film grain is subtle and does not interfere with interactions
- Mobile mode switch works on iOS Safari and Android Chrome
- Overall: the page is something you'd share on Hacker News

**Agent instructions:** See `agents/07_polish_games.md`
