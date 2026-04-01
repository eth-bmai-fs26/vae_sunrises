# Agent 6: Phase 2b — Encoder Animation & Progressive Disclosure

## Your Task

Add the Act III encoder particle animation and the progressive disclosure system to `web/index.html`.

## Prerequisites

- Working `web/index.html` from Agent 5 (hover, pin, interpolation, grid-to-scatter)
- `web/assets/data/latent_coords.json` with pre-computed (z, sun_x, sun_y) per image
- `web/assets/sprites/thumbnails.webp` sprite sheet

## What to Build

### 1. Encoder Gallery (Act III)

At the top of `#act-encoder`, add a horizontal gallery strip:

```html
<div id="encoder-gallery">
  <p>Pick a sunrise to see how it gets compressed to two numbers:</p>
  <div class="gallery-strip">
    <!-- 8-12 thumbnail images from the training set -->
  </div>
</div>
```

- Show 8-12 curated images from the training set (pick diverse ones: winter dawn, summer noon, etc.)
- Load thumbnails from the sprite sheet using `thumb_idx` from `latent_coords.json`
- Each thumbnail: 64×64 (upscaled from 32×32), with subtle border-radius and hover glow
- Clicking a thumbnail selects it (highlighted border in `--accent`)
- Selected image appears enlarged (128×128) in a "source panel" on the left

### 2. Encoder Particle Animation

**Trigger:** IntersectionObserver fires when Act III section enters viewport AND user has selected an image. If no image selected, auto-select the first one.

**Alternative trigger:** A "Watch it encode →" button below the source panel.

**Animation phases (Canvas2D, all on the latent canvas or a temporary overlay canvas):**

**Phase 1 — Decomposition (600ms):**
- Sample ~200 pixels from the source image (random positions, weighted toward bright/saturated pixels for visual impact)
- Each pixel becomes a Canvas2D filled circle (radius 2-3px) at its image position (mapped to canvas coordinates)
- The source image fades to 20% opacity
- Particles jitter slightly (Brownian motion: `+= Math.random()*2 - 1` per frame)

**Phase 2 — Flight (800ms):**
- Each particle travels from its image position to the target latent point
- Path: quadratic Bezier curve with randomized control point (creates a spread-out stream, not a straight line)
- Control point: midpoint offset perpendicular to the direct line by a random amount (±50px)
- Easing: ease-in-out per particle, with slight random delay (0-100ms) for staggering
- Color transition: particle starts as its source pixel color, blends to encoder violet (#6C8EBF) by the end of flight. Use `d3.interpolateRgb(pixelColor, '#6C8EBF')(flightProgress)`.
- Particle radius shrinks from 3px to 1.5px during flight

**Phase 3 — Convergence (600ms):**
- Particles arrive at the target mu position (from `latent_coords.json`)
- They cluster in a Gaussian cloud (σ proportional to the image's logvar)
- Over 400ms, the cloud tightens to a single point
- Final 200ms: a pin drops at mu with elastic bounce animation
- A small ring pulse emanates from the landing point (expanding circle, fading opacity)

**After animation:**
- The pin remains on the latent canvas
- The decoded image for that pin's z appears in the decoded panel
- The source image (at 20% opacity) and reconstruction appear side by side

**Implementation sketch:**
```javascript
function runEncoderAnimation(imageIdx) {
  const coords = latentCoords[imageIdx];
  const targetZ = coords.z;  // [z1, z2]
  const targetScreen = latentToScreen(targetZ[0], targetZ[1]);

  // Sample particles from source image
  const particles = samplePixels(imageIdx, 200);

  let startTime = null;
  function animate(timestamp) {
    if (!startTime) startTime = timestamp;
    const elapsed = timestamp - startTime;

    ctx.clearRect(0, 0, w, h);
    renderLatentSpace(); // redraw background (dots, pins)

    if (elapsed < 600) {
      // Phase 1: decomposition
      const t = elapsed / 600;
      particles.forEach(p => {
        p.x += (Math.random() - 0.5) * 2;
        p.y += (Math.random() - 0.5) * 2;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
        ctx.fill();
      });
    } else if (elapsed < 1400) {
      // Phase 2: flight along bezier curves
      const t = (elapsed - 600) / 800;
      const eased = easeInOutCubic(t);
      particles.forEach(p => {
        const pos = quadraticBezier(p.start, p.control, targetScreen, eased);
        const color = d3.interpolateRgb(p.color, '#6C8EBF')(eased);
        const radius = 3 - 1.5 * eased;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
        ctx.fill();
      });
    } else if (elapsed < 2000) {
      // Phase 3: convergence
      const t = (elapsed - 1400) / 600;
      const sigma = (1 - t) * 30; // pixels, shrinks to 0
      particles.forEach(p => {
        const jitter = { x: gaussian() * sigma, y: gaussian() * sigma };
        ctx.fillStyle = '#6C8EBF';
        ctx.beginPath();
        ctx.arc(targetScreen.x + jitter.x, targetScreen.y + jitter.y, 1.5, 0, Math.PI * 2);
        ctx.fill();
      });
    } else {
      // Done — drop pin
      addPin(targetZ, imageIdx);
      showReconstructionComparison(imageIdx, targetZ);
      return; // stop animation loop
    }

    requestAnimationFrame(animate);
  }
  requestAnimationFrame(animate);
}
```

### 3. Progressive Disclosure Annotations

Add 5 expandable annotations throughout the page:

**HTML pattern:**
```html
<details class="annotation" data-depth="technical">
  <summary>What is latent space? ▸</summary>
  <div class="annotation-content">
    <p>Formally, the <em>latent space</em> is...</p>
    <div class="math-block" data-katex="\mathbf{z} \in \mathbb{R}^2">
      <!-- KaTeX renders here on expand -->
    </div>
    <details class="annotation deep" data-depth="deep">
      <summary>Deep dive: connection to PCA ▸</summary>
      <p>...</p>
    </details>
  </div>
</details>
```

**Styling:**
```css
.annotation {
  margin: 1em 0;
  border-left: 3px solid var(--encoder-primary);
  padding-left: 1em;
}
.annotation summary {
  cursor: pointer;
  color: var(--accent);
  font-weight: 500;
}
.annotation.deep {
  border-left-style: dashed;
  opacity: 0.8;
}
```

**Lazy KaTeX rendering:**
```javascript
document.querySelectorAll('details.annotation').forEach(d => {
  d.addEventListener('toggle', () => {
    if (d.open) {
      d.querySelectorAll('[data-katex]').forEach(el => {
        if (!el.dataset.rendered) {
          katex.render(el.dataset.katex, el, { displayMode: el.classList.contains('math-block') });
          el.dataset.rendered = 'true';
        }
      });
    }
  });
});
```

**The 5 annotations:**

1. **After Act I scatter** — "What is latent space?"
   - Intuitive: "A map where similar sunrises live near each other."
   - Technical: Formal definition, z ∈ R², connection to dimensionality reduction
   - Deep: Comparison to PCA, t-SNE, UMAP

2. **During Act II hover-to-decode** — "What is a decoder?"
   - Intuitive: "A painter that only needs two instructions."
   - Technical: p_θ(x|z), neural network mapping z → image, Sigmoid output
   - Deep: Architecture details, receptive field, transposed convolutions

3. **During Act III encoder animation** — "What is an encoder?"
   - Intuitive: "A compressor that finds the two most important numbers."
   - Technical: q_φ(z|x), amortized inference, outputs (μ, σ²)
   - Deep: Why amortized vs. per-image optimization

4. **Act IV — temperature section** — "Why sample from a distribution?"
   - Intuitive: "Allowing a little randomness makes the generator more creative."
   - Technical: Reparameterization trick, z = μ + σ·ε, gradient flow
   - Deep: Why the reparameterization trick is needed for backprop

5. **Act IV — beta section** — "What is KL divergence?"
   - Intuitive: "A measure of how far the encoder's guesses are from a simple baseline."
   - Technical: ELBO = E[log p(x|z)] - β·KL(q(z|x) || p(z)), with each term color-coded
   - Deep: Information-theoretic interpretation, bits-back coding argument

### 4. Depth Toggle

Add a toggle in the header:
```html
<button id="depth-toggle" title="Show/hide math">
  <span class="toggle-label">Show math</span>
</button>
```

- Clicking toggles a CSS class on `<body>`: `body.show-all-math`
- When active, all `<details class="annotation">` are forced open
- State persists in localStorage

## Acceptance Criteria

1. Clicking a gallery image triggers the particle animation — visually compelling with clear 3 phases
2. Particles carry source image colors and blend to violet during flight
3. Pin lands at the correct latent position for the selected image
4. After animation, decoded reconstruction appears beside the original
5. All 5 annotations expand/collapse correctly
6. KaTeX renders proper math notation in each annotation
7. Depth toggle opens/closes all annotations simultaneously
8. Animation runs at ~60fps with 200 particles (Canvas2D)
9. Animation does not break the existing hover/pin/interpolation features
10. Animation can be replayed by clicking another gallery image
