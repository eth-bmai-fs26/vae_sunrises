# Sunrise Machine — Interactive VAE Visualization

**Status:** Converged Design (3 rounds of multi-agent debate)
**Date:** 2026-04-01
**Agents:** V (Visual Designer), I (Interaction Designer), T (Technical Architect)
**Rounds:** 3 (independent proposals → cross-critique → final positions)

---

## 1. Vision

An interactive scrollytelling webpage that teaches Variational Autoencoders through fabricated sunrise images. The page itself enacts a sunrise — scrolling from deep indigo night to golden dawn to warm cream daylight — so the medium embodies the message.

**The core insight:** The VAE's decoder IS the rendering engine. Every point the user touches in latent space generates a sunrise in real time via TensorFlow.js in the browser (~1-2ms per decode). The user's pointer becomes the latent vector. Their scroll becomes the sunrise.

### Guiding Principles (unanimous)

1. **Direct manipulation over explanation.** Every concept is touchable. No "submit" buttons. Linked representations everywhere (Bret Victor). The decoded image is always visible when the latent space is on screen.
2. **Progressive disclosure.** Default layer: intuitive, no equations, plain language. Technical terminology and math (KaTeX) are expandable via `<details>`, never forced. Three layers: intuitive → technical → deep dive.
3. **Performance is a feature.** If it can't be instant, pre-compute it. Sprite atlas fallback guarantees the experience works on any device.
4. **Beauty as pedagogy.** The sunrises ARE the reward. Every interaction produces something visually pleasing. The user explores because the output is gorgeous.

---

## 2. Narrative Structure — 5 Acts (converged Round 1, all agents agreed by Round 2)

Decoder-first pedagogy: show what the decoder produces BEFORE explaining the encoder. The user must understand "2 numbers → image" before "image → 2 numbers" makes sense.

| Act | Theme Name | Scroll % | Background | Content |
|-----|-----------|----------|------------|---------|
| **I: Twilight** | The Hook | 0–18% | #0B0E1A → #141832 | Hero "First Pixel" bloom, sunrise grid, grid-to-scatter FLIP animation |
| **II: First Light** | The Decoder | 18–45% | #2A1F4E → #4A2545 | Latent canvas sticky. Hover-to-decode. Click-to-pin. Interpolation slider. |
| **III: Golden Hour** | The Encoder | 45–65% | #7A3B2E → #C2753A | Gallery → particle compression animation → point lands in latent space → drag to verify |
| **IV: Full Day** | The Variational Part | 65–82% | #C2753A → #E8A84C | Temperature slider, KL divergence breathing, beta tug-of-war |
| **V: Reflection** | The Full Picture | 82–100% | #E8A84C → #FFF8F0 | Find the Sunrise game, sandbox, "ghost sunrise" souvenir, outro |

**Page length:** ~5500px (converged Round 3: V proposed 4000-5000, I proposed 6000-8000, settled at 5500 for decisive gradient shifts while allowing breathing room for sticky sections).

---

## 3. Resolved Disagreements (3-round debate record)

### 3.1 Cursor Trail
- **V (R1):** 8-position trail with spring-bounce physics
- **I (R1):** No trail, crosshair only
- **T (R2):** Cut to P2
- **V (R3):** Accepts I. No trail.
- **I (R3):** Cut to P2.
- **T (R3):** No trail, crosshair only.
- **RESOLUTION: No cursor trail for P0. Simple crosshair. The decoded image is the feedback, not the cursor.** (Unanimous by R3)

### 3.2 Canvas Architecture
- **V (R1):** Elaborate multi-layer
- **I (R1):** Canvas2D everywhere, single event layer
- **T (R1):** 4 layers (grid + particle + decode + UI)
- **V (R3):** Accepts T's 3-layer
- **I (R3):** Accepts T's 3-layer
- **T (R3):** Revised to 2 layers (Canvas2D + SVG overlay)
- **RESOLUTION: 2 layers for P0 — one Canvas2D (latent space, decoded images, particles, training dots) + one SVG overlay (axes, labels, coordinates, interactive controls). Add WebGL particle canvas in Phase 2 only if Canvas2D proves insufficient for 200 particles.** (Converged: simplest approach wins)

### 3.3 Grid-to-Scatter Animation
- **V (R1):** CSS FLIP on DOM elements
- **I (R1):** FLIP, scroll-scrubbed via GSAP
- **T (R2):** Canvas2D — 64 DOM transforms is a compositing layer risk
- **ALL (R3):** Accept Canvas2D
- **RESOLUTION: Canvas2D rAF loop. Interpolate tile positions from grid to scatter coordinates. Scroll-scrubbed via GSAP ScrollTrigger (user controls animation speed by scrolling). Single compositing layer.** (Unanimous by R3)

### 3.4 GSAP ScrollTrigger vs. Vanilla
- **V (R1):** No GSAP, use rAF + scrollY
- **I (R2):** Adopt GSAP
- **T (R1):** GSAP
- **ALL (R3):** Adopt GSAP
- **RESOLUTION: Use GSAP ScrollTrigger (~28KB gzip). Handles momentum scroll, resize, mobile Safari rubber-banding, and section pinning. Also drives scroll-scrubbed grid-to-scatter animation and background gradient timeline.** (Unanimous by R3)

### 3.5 Font
- **V (R1):** Inter
- **I (R1):** Source Sans 3
- **V (R3):** Accepts Source Sans 3 (better readability at body text sizes, warmth carried by color palette instead)
- **I (R3):** Accepts Inter (better tabular numbers for coordinate displays)
- **RESOLUTION: Inter for body text.** (V and I swapped positions; both accept either. Inter chosen for its superior tabular number support, which matters for the scrubbable coordinate displays that appear throughout.)

### 3.6 Mobile Touch Interaction
- **I (R1):** Single-finger decode, two-finger scroll
- **T (R2):** Explicit "Tap to explore" mode switch
- **V (R3):** Accepts T's mode switch
- **I (R3):** Accepts T's mode switch
- **T (R3):** Accepts I's single-finger/two-finger model
- **RESOLUTION: Explicit mode switch for P0.** Two agents (V, I) agreed on mode switch vs. one (T) who reversed. On mobile, canvas starts in scroll-through mode. A "Tap to explore" button toggles `touch-action: none`, enabling single-finger decode. "Done exploring" exits the mode. This avoids the unsolved gesture disambiguation problem.

### 3.7 Quantization
- **V (R2):** Float16 (strongly — uint8 causes visible banding in sky gradients)
- **I (R2):** Float16
- **T (R1):** Float16
- **RESOLUTION: Float16. Non-negotiable.** Sunrise images are 90% smooth gradients by pixel area. Uint8 quantization maps 256 discrete levels per weight, introducing visible banding. Float16 is perceptually lossless. Model size: ~400KB (vs ~200KB uint8). Well within budget.

### 3.8 Encoder Animation: Scroll-Scrubbed vs. Fire-Once
- **I (R2):** Scroll-scrubbed (user controls particle convergence by scrolling)
- **I (R3):** Revised to fire-once (reversing particles on back-scroll is complex and uncanny)
- **T (R3):** Fire-once on section enter
- **RESOLUTION: Fire-once play animation, triggered by IntersectionObserver when Act III enters viewport.** Grid-to-scatter is scroll-scrubbed; encoder particles are not.

### 3.9 First Touch Ripple
- **V (R1):** Concentric rings from cursor on first touch
- **I (R2):** Cut it — competes with decoded image
- **V (R3):** Accepts I. Cut.
- **RESOLUTION: Cut.** The decoded image appearing IS the first touch moment.

### 3.10 Sprite Atlas Grid Size
- **T (R1):** 32×32 (2048×2048px)
- **V (R2):** 24×24 (1536×1536px) — safer for mobile GPU texture limits
- **T (R3):** Accepts 24×24
- **RESOLUTION: 24×24 grid at 64px per cell = 1536×1536 WebP (~150KB).** Under the 2048px MAX_TEXTURE_SIZE limit of older iOS devices.

### 3.11 Decode API: Sync vs. Async
- **T (R1):** `dataSync()` (faster for small tensors)
- **V (R2):** `data()` async (protects main thread from stalls)
- **T (R3):** Accepts async `data()` with double buffering
- **RESOLUTION: Async `data()` with double-buffered canvas.** Protects scroll and cursor smoothness from GPU readback stalls on cold/slow devices.

---

## 4. Final Feature List

### P0 — Launch Requirements

| # | Feature | Details |
|---|---------|---------|
| P0.1 | **Scrollytelling skeleton** | 5 `<section>` elements, GSAP ScrollTrigger for section pinning and progress tracking |
| P0.2 | **Background gradient** | 8-stop gradient from #0B0E1A to #FFF8F0, driven by GSAP timeline scrubbed to scroll position |
| P0.3 | **"First Pixel" hero** | Single dot blooms to 256×256 sunrise over 1400ms (blur(20px→0px), scale(1→256)), ease-out-expo |
| P0.4 | **Sunrise grid → scatter** | ~64 thumbnails in Canvas2D. GSAP scroll-scrubbed tween from grid positions to latent-space positions. |
| P0.5 | **Latent space canvas** | 500×500 Canvas2D + SVG overlay for axes/labels. Training point dots from latent_coords.json. |
| P0.6 | **Hover-to-decode** | Pointer over canvas → decode at 30fps via rAF gate → display 256×256 in adjacent panel. Crosshair + coordinate readout. |
| P0.7 | **Click-to-pin** | Up to 4 pins, numbered, color-coded (decoder warm palette). Each shows 48×48 thumbnail + coordinates. |
| P0.8 | **Interpolation slider** | Select 2 pins → line drawn between them → slider morphs decoded image. `z_interp = (1-t)*z_A + t*z_B`. |
| P0.9 | **Encoder particle animation** | Fire-once on Act III enter. 3 phases: decomposition (600ms), flight (800ms), convergence (600ms). ~200 particles via Canvas2D. Particles carry source pixel colors, blend to encoder violet (#6C5CE7) during flight. |
| P0.10 | **TF.js decoder** | Float16 quantized, ~400KB. Async `data()` with double-buffer. 3 warmup inferences on load. |
| P0.11 | **Sprite atlas fallback** | 24×24 grid, 1536×1536 WebP (~150KB). Bilinear interpolation. Auto-engaged if WebGL unavailable or decode > 33ms for 3 frames. |
| P0.12 | **Progressive disclosure** | 5 expandable `<details>` annotations: latent space, decoder, encoder, reconstruction loss, KL divergence. KaTeX renders lazily on expand. |
| P0.13 | **Responsive layout** | Desktop: two-column sticky (text left, canvas right). Mobile: single column, no sticky, explicit "Tap to explore" mode switch. |
| P0.14 | **Typography + color system** | DM Serif Display / Inter / JetBrains Mono. Encoder=cool (#6C8EBF), Decoder=warm (#D4845A). |

### P1 — Should Have

| # | Feature |
|---|---------|
| P1.1 | Hero Lissajous animation (looping decode path on load) |
| P1.2 | Temperature / sampling slider with filmstrip of 8 batched decodes |
| P1.3 | KL divergence visualization — breathing gaussians, beta slider tug-of-war |
| P1.4 | Path drawing — Catmull-Rom splines, preset paths, animated playback |
| P1.5 | "Find the Sunrise" game — 3 guesses, distance scoring, 3 difficulty levels, localStorage |
| P1.6 | Scrubbable numeric values (Bret Victor style) — all displayed numbers drag-adjustable |
| P1.7 | Post-encoding drag verification — drag encoded point, see reconstruction degrade |
| P1.8 | Film grain overlay (CSS tiled PNG, `pointer-events: none`) |
| P1.9 | Scroll-wheel zoom on latent canvas (0.5x-3x) |
| P1.10 | "Ghost sunrise" souvenir — user's last decoded image displayed in Act V reflection |

### P2 — Nice to Have

| # | Feature |
|---|---------|
| P2.1 | Cursor trail (3-position, linear fade, disabled on latent canvas) |
| P2.2 | Latent Space Cartographer game |
| P2.3 | Pinch-to-zoom with minimap |
| P2.4 | Density visualization overlays (prior, aggregate posterior) |
| P2.5 | Semantic region labels ("winter dawn", "summer noon") |
| P2.6 | Slerp interpolation toggle |
| P2.7 | Single-HTML build target (base64 assets) |
| P2.8 | Projector mode (>1920px) |
| P2.9 | WebGL2 particle system (upgrade from Canvas2D if needed) |

---

## 5. Technical Specification

### 5.1 Technology Stack (converged)

| Library | Version | Size (gzip) | Purpose |
|---------|---------|-------------|---------|
| TensorFlow.js | 4.22+ | ~330KB (core + webgl) | VAE decoder inference |
| GSAP + ScrollTrigger | 3.12+ | ~36KB | Scroll-driven animations, section pinning |
| D3.js (micro) | 7.x (d3-scale, d3-interpolate) | ~12KB | Axis scales, color interpolation |
| KaTeX | 0.16+ | ~80KB | Math rendering (lazy-loaded) |
| No framework | — | 0KB | Vanilla JS, IIFE modules |

**Total JS: ~458KB gzip.** Total first load with assets: ~1.1MB.

### 5.2 File Structure

```
index.html                  -- HTML + inlined CSS + inlined JS
assets/
  model/
    decoder.json            -- TF.js model topology (~3KB)
    decoder.bin             -- Float16 weights (~400KB)
  sprites/
    atlas.webp              -- 24×24 grid, 1536×1536 (~150KB)
  data/
    latent_coords.json      -- {z, sun_x, sun_y} per training image (~30KB)
    thumbnails.webp         -- Sprite sheet of training thumbnails (~300KB)
```

### 5.3 CDN Dependencies

```html
<!-- TF.js -->
<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-core@4.22.0/dist/tf-core.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@4.22.0/dist/tf-backend-webgl.min.js"></script>

<!-- GSAP + ScrollTrigger -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"></script>

<!-- D3 micro-modules -->
<script src="https://cdn.jsdelivr.net/npm/d3-scale@4.0.2/dist/d3-scale.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/d3-interpolate@3.0.1/dist/d3-interpolate.min.js"></script>

<!-- KaTeX (deferred) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.js"></script>

<!-- Fonts -->
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
```

### 5.4 Rendering Architecture

**2 layers (converged):**

1. **Canvas2D** (`latentCanvas`) — all pixel rendering: training point dots, hover-decoded image preview, pinned thumbnails, particle effects, grid/scatter tiles. Single compositing layer. Updates at up to 60fps during interaction.
2. **SVG overlay** — axes, labels, coordinate readout, crosshair lines, pin numbers. DOM-based for accessibility and crisp text at any zoom. Updates only on value change.

Pointer events captured on a transparent overlay div, dispatched to appropriate handlers based on current Act and interaction state.

### 5.5 Core Code Architecture

```
// MODULE: Config          — palette, breakpoints, latent bounds, timing
// MODULE: State           — reactive pub/sub on plain object (~30 lines)
// MODULE: Capabilities    — WebGL2 detection, device memory, touch detection
// MODULE: ModelManager    — TF.js load, warmup, async decode with double buffer
// MODULE: SpriteAtlas     — atlas load, bilinear interpolation lookup
// MODULE: Renderer        — Canvas2D + SVG management, draw loops
// MODULE: ScrollController — GSAP ScrollTrigger setup, background gradient timeline
// MODULE: Interactions    — PointerEvents (unified mouse+touch), pin/drag/hover
// MODULE: Animations      — gridToScatter, encoderParticles, heroLissajous (P1)
// MODULE: Disclosure      — <details> management, lazy KaTeX rendering
// MODULE: App             — init, asset loading, fallback logic
```

### 5.6 Key Code Patterns

**Double-buffered async decode:**
```javascript
const buffers = [new OffscreenCanvas(64, 64), new OffscreenCanvas(64, 64)];
let active = 0;

async function decode(z) {
  const back = 1 - active;
  const ctx = buffers[back].getContext('2d');
  const pixelData = await tf.tidy(() => {
    const input = tf.tensor2d([[z[0], z[1]]]);
    const output = decoder.predict(input);
    return output.squeeze().mul(255).clipByValue(0, 255).data(); // async
  });
  const rgba = new Uint8ClampedArray(64 * 64 * 4);
  for (let i = 0, j = 0; i < 64 * 64; i++, j += 3) {
    rgba[i * 4] = pixelData[j];
    rgba[i * 4 + 1] = pixelData[j + 1];
    rgba[i * 4 + 2] = pixelData[j + 2];
    rgba[i * 4 + 3] = 255;
  }
  ctx.putImageData(new ImageData(rgba, 64, 64), 0, 0);
  active = back;
  return buffers[active];
}
```

**Throttled pointer handler (30fps):**
```javascript
let pending = null, scheduled = false;
canvas.addEventListener('pointermove', (e) => {
  pending = screenToLatent(e.offsetX, e.offsetY);
  if (!scheduled) {
    scheduled = true;
    requestAnimationFrame(async () => {
      if (pending) await decodeAndRender(pending);
      pending = null;
      scheduled = false;
    });
  }
});
```

**Adaptive fallback:**
```javascript
let slowFrames = 0;
async function decodeAuto(z) {
  if (state.useSpriteFallback) return SpriteAtlas.lookup(z);
  const t0 = performance.now();
  const result = await decode(z);
  if (performance.now() - t0 > 33) {
    if (++slowFrames >= 3) state.useSpriteFallback = true;
  } else slowFrames = 0;
  return result;
}
```

**GSAP scroll-driven background gradient:**
```javascript
const colors = ['#0B0E1A','#141832','#2A1F4E','#4A2545','#7A3B2E','#C2753A','#E8A84C','#FFF8F0'];
gsap.to({}, {
  scrollTrigger: { trigger: '#app', start: 'top top', end: 'bottom bottom', scrub: true },
  onUpdate() {
    const p = this.progress();
    const bg = d3.interpolateRgbBasis(colors)(p);
    document.body.style.background = bg;
  }
});
```

### 5.7 VAE Model Pipeline

```
PyTorch VAE (2-dim latent, 64×64 RGB output)
  → torch.onnx.export(decoder, dummy_z, "decoder.onnx", opset_version=17)
  → onnx-tf convert to SavedModel
  → tensorflowjs_converter --quantize_float16 → decoder.json + decoder.bin

Sprite atlas (offline):
  24×24 grid, z ∈ [-3, 3], decode each → stitch into 1536×1536 WebP

Latent coordinates (offline):
  Encode full training set → save [{z: [z1, z2], sun_x, sun_y}] as JSON
```

### 5.8 Responsive Strategy

| Tier | Width | Canvas | Decoded Panel | Layout |
|------|-------|--------|---------------|--------|
| Mobile | <768px | clamp(280px, 90vw, 400px) | 128×128 above canvas | Single column, no sticky, "Tap to explore" mode |
| Desktop | 768–1920px | 500×500 | 256×256 side panel | Two-column sticky for Acts II–IV |
| Projector (P2) | >1920px | 700×700 | 384×384 | Scaled desktop |

### 5.9 Performance Budgets

| Metric | Target |
|--------|--------|
| First Contentful Paint | < 1.0s |
| Time to Interactive | < 2.5s |
| Decode latency (TF.js, p95) | < 5ms |
| Decode latency (sprite) | < 1ms |
| Hover-to-image update | < 33ms (30fps) |
| Particle animation | 60fps, 200 particles |
| Simultaneously animated layers | ≤ 3 |
| Total transfer | < 1.2MB |
| JS heap (steady state) | < 50MB |
| TF.js tensor count (steady) | < 20 |

### 5.10 Capability Detection & Fallback Tiers

| Tier | Condition | Behavior |
|------|-----------|----------|
| **Full** | WebGL2 + float32 textures + ≥2GB RAM | TF.js real-time decode |
| **Sprite** | No WebGL2 or TF.js load failure | Sprite atlas bilinear interpolation |
| **Canvas-only** | No WebGL at all | Sprite atlas, no particle animation |
| **Static** | Very old browser | Pre-rendered images, no interactivity |

### 5.11 Accessibility

- Canvas: `role="img"`, descriptive `aria-label`, `tabindex="0"`
- Keyboard: Tab → canvas, arrow keys move cursor (0.1 units), Shift+Arrow (0.01), Enter = pin, Escape = unpin
- `aria-live="polite"` region announces pin/decode changes
- `<details>/<summary>` for progressive disclosure (native, accessible)
- `prefers-reduced-motion`: all animations instant, scroll effects become opacity toggles
- WCAG AA contrast on all text against current gradient position

---

## 6. Color System

### Background Gradient Stops (scroll-driven)

```
  0%  #0B0E1A   Deep space navy
 15%  #141832   Midnight indigo
 30%  #2A1F4E   Pre-dawn violet
 45%  #4A2545   Twilight mauve
 55%  #7A3B2E   Sunrise ember
 70%  #C2753A   Golden hour amber
 85%  #E8A84C   Full morning gold
100%  #FFF8F0   Warm cream daylight
```

### Semantic Tokens

```
Encoder (cool/analytical):
  --encoder-primary:   #6C8EBF
  --encoder-light:     #A3C1E0
  --encoder-dark:      #3A5A8C

Decoder (warm/generative):
  --decoder-primary:   #D4845A
  --decoder-light:     #EAAC7A
  --decoder-dark:      #9E5A33

Interactive:
  --interactive-cursor: #FFFFFF
  --interactive-glow:   rgba(255, 200, 120, 0.3)
  --accent-highlight:   #F2C94C

Text on dark BG:  #E8E4DF (body), #FFFFFF (headings), rgba(232,228,223,0.55) (muted)
Text on light BG: #1A1A2E (body), #0B0E1A (headings)

Code/coordinates: #00CEC9 (on dark), #6C5CE7 (on light)
```

---

## 7. Typography

```
Headlines:     'DM Serif Display', serif       clamp(2rem, 5vw, 4rem)
Body:          'Inter', sans-serif             clamp(1rem, 1.5vw, 1.25rem)  line-height: 1.7  max-width: 65ch
Coordinates:   'JetBrains Mono', monospace     0.875em
Math:          KaTeX, inline or display-block
```

Key term treatment: first occurrence highlighted in `--accent-highlight` (#F2C94C) with `border-bottom: 1px dashed`, tooltip on hover with one-sentence definition.

---

## 8. Implementation Phases

### Phase 1: Foundation
**Goal:** Scrollable page + working latent canvas + decode on click.

- index.html with 5 sections, GSAP ScrollTrigger, background gradient
- Typography and color system
- Canvas2D + SVG overlay rendering latent space with axes
- TF.js decoder loads, warmup, decode on click
- Sprite atlas fallback
- Responsive: does not break at any width

**Exit:** User scrolls through gradient, clicks latent canvas, sees decoded sunrise.

### Phase 2: Core Interactions
**Goal:** All interactive teaching moments work.

- Grid-to-scatter scroll-scrubbed Canvas2D animation
- Hover-to-decode at 30fps
- Click-to-pin (up to 4)
- Interpolation slider between pin pairs
- Encoder particle animation (fire-once, 200 particles, Canvas2D)
- 5 progressive disclosure annotations with KaTeX

**Exit:** A non-ML-background user scrolls through and can explain what a VAE does.

### Phase 3: Polish & P1
**Goal:** The "wow" factor. Hacker News / Twitter shareable.

- Hero Lissajous, temperature/beta sliders, KL breathing
- Path drawing with splines
- Find the Sunrise game
- Scrubbable numbers, encode-and-verify, ghost sunrise souvenir
- Film grain, mobile touch optimization

### Phase 4: P2 Features
Based on user feedback after Phase 3.

---

## 9. 5 "Wow" Moments (converged)

1. **The First Pixel** — Page loads to near-black. A single point of light blooms into a full sunrise over 1.4 seconds. The thesis statement as animation: one point of information expands into a rich image.

2. **The Grid Crystallizes** — 64 sunrise thumbnails rearrange before the user's eyes from a random grid into a structured 2D scatter plot. Scroll-controlled — the user can scrub back and forth, watching order emerge from chaos.

3. **First Touch** — The user moves their pointer over the latent canvas and a sunrise materializes in real time. No click needed. The "it's alive" moment.

4. **The Encoder Particle Storm** — A sunrise image shatters into 200 colored particles that stream across the screen and converge to a single glowing point in latent space. The particles carry the image's colors and gradually blend to encoder violet. Compression made visceral.

5. **The Smooth Morph** — The user pins a winter dawn and a summer sunset, then drags the interpolation slider. The sunrise transforms continuously between the two — sky color flowing, sun position gliding, clouds dissolving and reforming. The proof that the latent space is meaningful.

---

## 10. Open Questions

1. **Training data:** Where are the sunrise images from? How many? License? Must resolve before Phase 1.
2. **Image resolution:** 64×64 sufficient for "wow"? If not, 128×128 adds ~400KB model weight but doubles visual quality. Decide after seeing 64×64 results.
3. **Encoder in browser:** Fake it with pre-computed (mu, logvar) from latent_coords.json for P0/P1. Real encoder inference is P2.

---

## 11. What Makes This Design Work

**The VAE's decoder is the rendering engine for the visualization.** The page doesn't show diagrams of what a VAE does — it IS a VAE running in real time. The user's cursor becomes the latent vector. Their scroll becomes the sunrise. Their curiosity becomes the exploration.

Three specialists with different priorities (beauty, pedagogy, performance) debated for three rounds and converged on a design that is:
- **Simple enough to build:** Single HTML file, no framework, 2 canvas layers
- **Beautiful enough to share:** Sunrise gradient page, warm color system, smooth 30fps decode
- **Deep enough to teach:** 5-act narrative, progressive disclosure, direct manipulation
- **Robust enough to ship:** Sprite atlas fallback, adaptive degradation, capability detection
