# Agent 4: Phase 1 — Scrollytelling Shell

## Your Task

Build the foundational web page: `web/index.html`. A single HTML file with inlined CSS and JS that creates a scrollable 5-act page with a working latent space canvas and decode-on-click.

## Prerequisites

Assets must exist in `web/assets/` (from Agent 3):
- `model/model.json` + `model/*.bin`
- `sprites/atlas.webp`
- `data/latent_coords.json`

## What to Build

### HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- CDN: TF.js, GSAP+ScrollTrigger, D3 micro, KaTeX (defer), Fonts -->
  <style>/* all CSS inlined */</style>
</head>
<body>
  <header><!-- progress dots (5), depth toggle --></header>

  <section data-act="1" id="act-hook">
    <h1>Sunrise Machine</h1>
    <p>What if two numbers could paint a sunrise?</p>
    <!-- Placeholder for grid/scatter (Agent 5 will add) -->
  </section>

  <section data-act="2" id="act-decoder">
    <div class="sticky-container">
      <div class="text-column">
        <!-- Scrolling explanatory text -->
      </div>
      <div class="canvas-column">
        <canvas id="latent-canvas" width="500" height="500"></canvas>
        <svg id="canvas-overlay"><!-- axes, labels --></svg>
        <div id="decoded-panel">
          <canvas id="decoded-image" width="256" height="256"></canvas>
          <div id="coord-readout">z = (0.00, 0.00)</div>
        </div>
      </div>
    </div>
  </section>

  <section data-act="3" id="act-encoder">
    <!-- Placeholder for encoder experience (Agent 6) -->
  </section>

  <section data-act="4" id="act-variational">
    <!-- Placeholder for temperature/beta (Agent 7) -->
  </section>

  <section data-act="5" id="act-sandbox">
    <!-- Placeholder for game/sandbox (Agent 7) -->
  </section>

  <script>/* all JS inlined */</script>
</body>
</html>
```

### CSS (inlined in `<style>`)

**Background gradient (scroll-driven):**
- 8 stops: `#0B0E1A → #141832 → #2A1F4E → #4A2545 → #7A3B2E → #C2753A → #E8A84C → #FFF8F0`
- Driven by GSAP ScrollTrigger timeline scrubbed to scroll position
- Use `d3.interpolateRgbBasis()` for smooth multi-stop interpolation

**Typography:**
```css
h1, h2 { font-family: 'DM Serif Display', serif; }
body, p { font-family: 'Inter', sans-serif; line-height: 1.7; }
code, .coord { font-family: 'JetBrains Mono', monospace; }
```

**Layout:**
- Sections are full-width, min-height varies by act
- Act II uses `position: sticky` for the canvas column
- Two-column layout: text (55%) + canvas (45%)
- Mobile (<768px): single column, canvas inline (not sticky)
- Use `clamp()` for fluid sizing

**Color tokens (CSS custom properties):**
```css
:root {
  --encoder-primary: #6C8EBF;
  --decoder-primary: #D4845A;
  --interactive-glow: rgba(255, 200, 120, 0.3);
  --accent: #F2C94C;
  --text-on-dark: #E8E4DF;
  --text-on-light: #1A1A2E;
}
```

**`prefers-reduced-motion`:** Skip all transitions, use opacity toggles.

### JavaScript Modules (all in one `<script>`)

**1. Config:**
```javascript
const CONFIG = {
  LATENT_RANGE: [-3, 3],
  CANVAS_SIZE: 500,        // desktop
  DECODED_SIZE: 256,
  ATLAS_GRID: 24,
  ATLAS_CELL: 64,
  COLORS: { /* from DESIGN.md */ }
};
```

**2. State:**
```javascript
const state = {
  scrollProgress: 0,
  currentAct: 1,
  modelReady: false,
  useSpriteFallback: false,
  latentCursor: null,
  pinnedPoints: [],
};
```

**3. Model & Inference:**
- Load TF.js model from `assets/model/model.json`
- Run 3 warmup inferences on load
- `async decode(z)` — TF.js inference with double-buffered canvas
- `decodeFromAtlas(z)` — bilinear interpolation from sprite atlas
- `decodeAuto(z)` — try TF.js, fall back to atlas if slow

**4. Sprite Atlas:**
- Load `atlas.webp` into an Image object
- `decodeFromAtlas(z)` — map z to grid coordinates, bilinear blend 4 nearest cells

**5. Rendering:**
- D3 scales: `d3.scaleLinear().domain([-3, 3]).range([0, 500])`
- SVG axes with "time of year" (x) and "time of day" (y) labels
- Render training points as small dots from `latent_coords.json`
- On click: decode the clicked z and draw result in `decoded-image` canvas

**6. Scroll Controller:**
- GSAP ScrollTrigger on the full page
- `onUpdate` callback sets `state.scrollProgress` and updates background via `d3.interpolateRgbBasis`
- ScrollTrigger pinning for the Act II sticky section

**7. Init:**
```javascript
async function init() {
  // 1. Load sprite atlas (fast)
  // 2. Start TF.js model load (parallel)
  // 3. Load latent_coords.json (parallel)
  // 4. Render Act I content immediately
  // 5. Set up scroll observer
  // 6. On model ready: enable real-time decode, run warmup
  // 7. Set up click handler on latent canvas
}
```

### CDN Script Tags

```html
<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4/dist/tf.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12/dist/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/d3-scale@4"></script>
<script src="https://cdn.jsdelivr.net/npm/d3-interpolate@3"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
```

## Acceptance Criteria

1. Page loads without console errors
2. Scrolling through all 5 sections shows smooth background gradient transition
3. Training point dots render on the latent canvas with correct axes
4. Clicking the latent canvas decodes and displays a recognizable sunrise
5. Sprite atlas fallback works (test by blocking model load)
6. Responsive: readable and functional at 320px, 768px, 1024px, 1920px
7. Text color is readable against the background at every scroll position (light on dark for Acts I-II, dark on light for Acts IV-V)
8. `prefers-reduced-motion` disables all transitions

## What NOT to Build Yet

- Hover-to-decode (Agent 5)
- Pinning and interpolation (Agent 5)
- Grid-to-scatter animation (Agent 5)
- Particle animation (Agent 6)
- Progressive disclosure annotations (Agent 6)
- Temperature/beta sliders (Agent 7)
- Game (Agent 7)

Just build the skeleton, the canvas, and click-to-decode. Make it solid.
