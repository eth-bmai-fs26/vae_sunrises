# VAE Sunrise Visualization -- Converged Design Document

**Status:** Final Draft
**Date:** 2026-04-01
**Synthesized from:** Visual Designer, Interaction Designer, Technical Architect proposals

---

## 1. Vision & Guiding Principles

An interactive, scrollytelling webpage that teaches Variational Autoencoders through the lens of sunrise photography. The page itself enacts a sunrise -- scrolling from dark indigo to golden light -- so the medium reinforces the message.

**Three principles govern every decision:**

1. **Direct manipulation over explanation.** Every concept the user reads about, they can immediately touch. No "submit" buttons. Linked representations everywhere (Bret Victor style).
2. **Progressive disclosure.** The default layer is intuitive (no equations, plain language). Technical terminology and math are expandable, never forced.
3. **Performance is a feature.** Real-time decoder inference in the browser (~1ms per frame) makes the "magic" feel instant. If it can't be instant, pre-compute it.

---

## 2. Points of Agreement Across All Three Proposals

All three specialists converge on these points, which form the non-negotiable core:

- **Single HTML file deployment** (or minimal file set) on GitHub Pages
- **Scrollytelling narrative arc** with sticky interactive sections
- **Real-time VAE decoder in browser** via TensorFlow.js with pre-computed sprite atlas fallback
- **Latent space as the interactive centerpiece** -- hover to decode, click to pin, drag to explore
- **Particle animation for the encoder** -- image visually compresses to two coordinates
- **Interpolation as the key "aha" moment** -- dragging between points shows smooth morphing
- **Canvas for performance-critical rendering**, SVG overlay for labels/axes
- **KaTeX for math**, shown progressively
- **DM Serif Display / Source Sans 3 / JetBrains Mono** typography stack

---

## 3. Conflicts & Resolutions

### 3.1 Narrative Structure: 7 Sections vs. 5 Acts

**Visual Designer** proposes 7 sections (Hero, Data Grid, Encoder, Latent Space, Decoder, Math, Why It Matters). **Interaction Designer** proposes 5 Acts (Hook, Decoder, Encoder, Variational, Sandbox).

**Resolution:** Adopt the Interaction Designer's 5-Act structure as the backbone -- it has stronger pedagogical logic (showing the decoder BEFORE the encoder is the correct teaching order for VAEs, because understanding "latent space maps to images" must precede "images map to latent space"). Fold the Visual Designer's Hero and Data Grid into Act I, and "Why It Matters" into Act V. The Math section becomes expandable annotations throughout, not a standalone section.

**Final structure:**

| Act | Visual Theme | Content |
|-----|-------------|---------|
| **I: The Hook** | Deep indigo (#0B0E2D), star-field feel | Hero sunrise animation, grid of sunrise thumbnails that rearranges by similarity then collapses into 2D scatter |
| **II: The Decoder** | Indigo to violet transition | Latent space becomes sticky. Hover-to-preview activates. Click to pin. Path drawing. "Every point is a sunrise." |
| **III: The Encoder** | Violet to rose | Pick a sunrise from gallery, watch particle compression animation, point appears in latent space, drag to verify |
| **IV: The Variational Part** | Rose to gold | Temperature slider, KL divergence "breathing" visualization, beta slider tug-of-war between reconstruction and regularization |
| **V: The Full Picture** | Gold to warm cream (#FFF8F0) | Reconstruction game, sandbox mode combining all tools, "Why It Matters" outro |

### 3.2 Scope of Gamification

**Interaction Designer** proposes 4 games (Find the Sunrise, Latent Space Cartographer, Blind Encoder, Interpolation Challenge). This is too much for launch.

**Resolution:** Keep "Find the Sunrise" (P0) as it directly teaches the core concept. Move Latent Space Cartographer to P1. Cut Blind Encoder and Interpolation Challenge entirely (P2 at best) -- they add complexity without proportional pedagogical value.

### 3.3 Path Drawing Complexity

**Interaction Designer** proposes Catmull-Rom splines with preset paths. **Technical Architect** does not mention path drawing but the performance budget supports it.

**Resolution:** P1 feature. For P0, support only linear interpolation between two pinned points (a slider). Path drawing with splines is a clear P1 -- it is high-impact but not required to teach the core concept.

### 3.4 Pinch-to-Zoom and Minimap

**Interaction Designer** proposes pinch-to-zoom with minimap and density overlays. This adds significant interaction complexity.

**Resolution:** P2. The latent space for this VAE is 2D with ~1000 training images -- it does not need multi-scale navigation. A fixed viewport with slight zoom (scroll-wheel or pinch, 0.5x to 3x range) is P1. Full minimap and density overlays are P2.

### 3.5 Model Format: TF.js vs. ONNX Runtime Web

**Technical Architect** suggests TF.js as primary with ONNX as alternative.

**Resolution:** Use TF.js. It has better browser support, a smaller bundle when cherry-picked, and the model is tiny enough that optimization differences are irrelevant. The sprite atlas fallback eliminates the need for a second runtime.

### 3.6 Truly Single HTML File vs. Separate Assets

**Technical Architect** mentions both options. **Visual Designer** implies separate assets (images, fonts).

**Resolution:** Primary deployment is a small set of files (index.html + model files + sprite atlas + font files). A single-HTML build target with base64-encoded weights is a P2 convenience feature. Fonts load from Google Fonts CDN, not self-hosted (saves ~200KB).

---

## 4. Final Feature List with Priorities

### P0 -- Launch Requirements

These are the features without which the page does not accomplish its teaching goal.

| # | Feature | Owner Domain |
|---|---------|-------------|
| P0.1 | **Scrollytelling skeleton** -- 5-act structure with scroll-triggered transitions via Intersection Observer | Visual + Tech |
| P0.2 | **Background gradient** -- page background shifts indigo to gold to cream as user scrolls | Visual |
| P0.3 | **Sunrise data grid** -- display ~200 sunrise thumbnails in a grid that animates into the 2D latent scatter | Visual + Interaction |
| P0.4 | **Latent space canvas** -- 2D interactive canvas with axes, labeled regions, and training point dots | Tech + Interaction |
| P0.5 | **Hover-to-decode** -- move pointer over latent canvas, see decoded sunrise image at ~30fps in a panel beside/above the canvas | Interaction + Tech |
| P0.6 | **Click-to-pin** -- click to pin up to 4 sunrises on the canvas with thumbnail + coordinates | Interaction |
| P0.7 | **Linear interpolation slider** -- select two pinned points, drag slider to see morph between them | Interaction |
| P0.8 | **Encoder particle animation** -- select a sunrise, watch it decompose into particles that converge to its (mu, sigma) point in latent space | Visual + Tech |
| P0.9 | **TF.js decoder inference** -- real-time decoding of arbitrary latent coordinates in browser | Tech |
| P0.10 | **Sprite atlas fallback** -- 20x20 grid of pre-computed decoded images, bilinear interpolation for points between grid cells | Tech |
| P0.11 | **Progressive disclosure** -- expandable "Learn more" annotations for technical terms and math (KaTeX) | Interaction + Visual |
| P0.12 | **Responsive layout** -- works on desktop (768-1920px) and does not break on mobile (graceful degradation, not full mobile optimization) | Tech |
| P0.13 | **Typography and color system** -- DM Serif Display, Source Sans 3, JetBrains Mono. Encoder=violet/indigo, Decoder=rose/gold palette. | Visual |

### P1 -- Should Have (implement after P0 is solid)

| # | Feature | Notes |
|---|---------|-------|
| P1.1 | **Hero sunrise animation** | Lissajous curve decoded through VAE, looping. Establishes the "wow" on page load. |
| P1.2 | **Temperature / sampling slider** | In Act IV. Shows effect of sigma scaling on decoded output variety. |
| P1.3 | **KL divergence visualization** | "Breathing" gaussian blobs. Beta slider shows regularization vs. reconstruction trade-off. |
| P1.4 | **Path drawing mode** | Draw a freeform path on latent space, see decoded animation along it. Catmull-Rom interpolation. Preset paths (season arc, color gradient). |
| P1.5 | **Find the Sunrise game** | Show a target sunrise, user clicks in latent space to find it. Distance-based scoring. 3 difficulty levels. |
| P1.6 | **Scroll-wheel zoom** | 0.5x-3x zoom on latent canvas. Recenter on pointer. |
| P1.7 | **Animated grain texture overlay** | Subtle film-grain across the page. Pure CSS or tiny canvas. |
| P1.8 | **Scrubbable numeric values** | All displayed numbers (coordinates, loss values, temperature) are click-and-drag adjustable. |
| P1.9 | **Mobile-optimized interactions** | Touch-friendly latent canvas, swipe between pinned sunrises, responsive sticky sections. |
| P1.10 | **Encode mode verification** | After encoding, user can drag the encoded point and see how decoded output diverges from original. |

### P2 -- Nice to Have

| # | Feature | Notes |
|---|---------|-------|
| P2.1 | Latent Space Cartographer game | Explore 25 regions, collect stamps. |
| P2.2 | Pinch-to-zoom with minimap | Full multi-scale navigation. |
| P2.3 | Density visualization overlays | Prior, aggregate posterior, clean modes. |
| P2.4 | Semantic region labels | Auto-detected clusters labeled ("winter dawn", "tropical sunset", etc.). |
| P2.5 | Slerp interpolation toggle | Alternative to linear interp. |
| P2.6 | Single-HTML build target | Base64-encode all assets into one file. |
| P2.7 | Auto-playing filmstrip time-lapses | For seasonal variation demonstration. |
| P2.8 | Projector mode (>1920px) | Large-screen layout for presentations. |

---

## 5. Technical Specification

### 5.1 File Structure

```
index.html              -- Main (and only) HTML file. All CSS is inlined in <style>. All JS is inlined in <script>.
assets/
  model/
    decoder.json        -- TF.js model topology
    decoder.bin         -- Quantized int8 weights (~200KB)
  sprites/
    atlas.png           -- 20x20 pre-computed decoded grid (~300KB)
  data/
    latent_coords.json  -- (mu, logvar) for all training images (~50KB)
    thumbnails.png       -- Sprite sheet of training image thumbnails (~500KB)
```

**Total first-load budget: ~1.2MB** (excluding CDN-hosted libraries and fonts).

### 5.2 CDN Dependencies

```html
<!-- TensorFlow.js -- WebGL backend only, no WASM -->
<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.x/dist/tf.min.js"></script>

<!-- D3.js -- cherry-picked modules only -->
<script src="https://cdn.jsdelivr.net/npm/d3-scale@4"></script>
<script src="https://cdn.jsdelivr.net/npm/d3-axis@3"></script>
<script src="https://cdn.jsdelivr.net/npm/d3-selection@3"></script>
<script src="https://cdn.jsdelivr.net/npm/d3-transition@3"></script>
<script src="https://cdn.jsdelivr.net/npm/d3-interpolate@3"></script>
<script src="https://cdn.jsdelivr.net/npm/d3-ease@3"></script>

<!-- KaTeX for math rendering -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.js"></script>

<!-- Fonts -->
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
```

### 5.3 Core Architecture (in index.html)

The JS is organized into these modules (all in one `<script>` block, separated by comments):

```
// ═══════════════════════════════════════
// MODULE: Config & Constants
// ═══════════════════════════════════════
// Color palette, breakpoints, timing constants, latent space bounds

// ═══════════════════════════════════════
// MODULE: State Management
// ═══════════════════════════════════════
// Single state object. No framework. Event emitter pattern for reactivity.
//
// state = {
//   scrollProgress: 0-1,
//   currentAct: 1-5,
//   latentCursor: {x, y},
//   pinnedPoints: [],        // max 4
//   interpolationT: 0-1,
//   temperature: 1.0,
//   beta: 1.0,
//   decodedImage: ImageData,
//   modelReady: false,
//   useSpriteFallback: false,
// }

// ═══════════════════════════════════════
// MODULE: Model & Inference
// ═══════════════════════════════════════
// loadDecoder()        -- loads TF.js model, runs warmup inference
// decode(z)            -- returns ImageData from latent vector [z1, z2]
// decodeFromAtlas(z)   -- bilinear interpolation from sprite atlas
// decodeAuto(z)        -- tries TF.js, falls back to atlas
// encode(imageData)    -- if encoder is loaded (P1), returns {mu, logvar}
// Wraps all TF calls in tf.tidy(). Uses double-buffer pattern for canvas.

// ═══════════════════════════════════════
// MODULE: Rendering -- Canvas
// ═══════════════════════════════════════
// Two canvases layered:
//   1. imageCanvas  -- decoded sunrise images, particle effects, thumbnails
//   2. uiCanvas (SVG overlay) -- axes, labels, pinned point markers, paths
//
// renderLatentSpace()  -- draws training points as dots, pinned points, cursor
// renderDecodedPanel() -- draws the large decoded image beside the latent canvas
// renderParticles()    -- encoder particle animation (requestAnimationFrame loop)
// renderGrid()         -- Act I sunrise thumbnail grid

// ═══════════════════════════════════════
// MODULE: Scroll Controller
// ═══════════════════════════════════════
// Intersection Observer on each <section data-act="N">
// Updates state.scrollProgress and state.currentAct
// Triggers background gradient transition via CSS custom property:
//   document.documentElement.style.setProperty('--scroll-progress', progress)
// Background gradient defined in CSS using the custom property.

// ═══════════════════════════════════════
// MODULE: Interaction Handlers
// ═══════════════════════════════════════
// Uses PointerEvents (unified mouse + touch) throughout.
// pointerMove on latent canvas -> update state.latentCursor -> decode -> render
// pointerDown on latent canvas -> pin point
// Slider for interpolation -> update state.interpolationT -> decode lerp -> render
// All interactions throttled to 33ms (30fps) via requestAnimationFrame gate.

// ═══════════════════════════════════════
// MODULE: Animations
// ═══════════════════════════════════════
// heroAnimation()      -- Lissajous loop through latent space (P1)
// gridToScatter()      -- FLIP animation: thumbnails morph from grid to scatter
// encoderParticles()   -- image -> particles -> convergence to (mu) point
// klBreathing()        -- gaussian contours pulsing (P1)
// All animations use requestAnimationFrame. No GSAP (unnecessary dependency).

// ═══════════════════════════════════════
// MODULE: Progressive Disclosure
// ═══════════════════════════════════════
// <details> elements with custom styling for expandable annotations.
// KaTeX renders on-demand (when annotation is opened) to avoid upfront cost.
// Three layers: data-depth="intuitive|technical|deep"

// ═══════════════════════════════════════
// MODULE: Init
// ═══════════════════════════════════════
// 1. Load sprite atlas (fast, ~300KB)
// 2. Begin TF.js model load in parallel
// 3. Render Act I immediately using sprite data
// 4. On model ready, enable real-time decode, run warmup
// 5. Set up scroll observer, pointer handlers
```

### 5.4 Key Code Patterns

**Double-buffered decode (avoids flicker):**
```javascript
const bufferA = new OffscreenCanvas(64, 64);
const bufferB = new OffscreenCanvas(64, 64);
let activeBuffer = bufferA;

async function decode(z) {
  const inactive = activeBuffer === bufferA ? bufferB : bufferA;
  const ctx = inactive.getContext('2d');
  const tensor = tf.tidy(() => {
    const input = tf.tensor2d([[z[0], z[1]]]);
    return decoder.predict(input);
  });
  const data = await tensor.data();
  tensor.dispose();
  const imageData = new ImageData(new Uint8ClampedArray(data), 64, 64);
  ctx.putImageData(imageData, 0, 0);
  activeBuffer = inactive;
  return activeBuffer;
}
```

**Throttled pointer handler:**
```javascript
let frameRequested = false;
latentCanvas.addEventListener('pointermove', (e) => {
  state.latentCursor = screenToLatent(e.offsetX, e.offsetY);
  if (!frameRequested) {
    frameRequested = true;
    requestAnimationFrame(() => {
      decodeAndRender(state.latentCursor);
      frameRequested = false;
    });
  }
});
```

**Scroll-driven background gradient (CSS):**
```css
:root {
  --scroll-progress: 0;
}
body {
  background: color-mix(
    in oklch,
    color-mix(in oklch, #0B0E2D calc((1 - var(--scroll-progress) * 2) * 100%), #F5A623),
    #FFF8F0 calc(max(0, var(--scroll-progress) * 2 - 1) * 100%)
  );
  transition: background 0.3s ease-out;
}
```
Note: If `color-mix` browser support is insufficient, fall back to a JS-computed `background` style using d3-interpolate on the three color stops.

**Sprite atlas bilinear interpolation:**
```javascript
function decodeFromAtlas(z, atlas, ctx) {
  // z in [-3, 3] mapped to atlas grid [0, 19]
  const gx = (z[0] + 3) / 6 * 19;
  const gy = (z[1] + 3) / 6 * 19;
  const x0 = Math.floor(gx), y0 = Math.floor(gy);
  const x1 = Math.min(x0 + 1, 19), y1 = Math.min(y0 + 1, 19);
  const fx = gx - x0, fy = gy - y0;
  // Draw 4 nearest cells with appropriate opacity for bilinear blend
  ctx.globalAlpha = (1 - fx) * (1 - fy); ctx.drawImage(atlas, x0*64, y0*64, 64, 64, 0, 0, 64, 64);
  ctx.globalAlpha = fx * (1 - fy);       ctx.drawImage(atlas, x1*64, y0*64, 64, 64, 0, 0, 64, 64);
  ctx.globalAlpha = (1 - fx) * fy;       ctx.drawImage(atlas, x0*64, y1*64, 64, 64, 0, 0, 64, 64);
  ctx.globalAlpha = fx * fy;             ctx.drawImage(atlas, x1*64, y1*64, 64, 64, 0, 0, 64, 64);
  ctx.globalAlpha = 1;
}
```

### 5.5 VAE Model Pipeline

```
Training (offline, not part of this repo):
  PyTorch VAE (2-dim latent, 64x64 RGB output)
    -> torch.onnx.export()
    -> onnx-tf convert
    -> tensorflowjs_converter --quantize_uint8
    -> decoder.json + decoder.bin

Sprite atlas generation (offline script):
  Grid of 20x20 evenly spaced z values in [-3, 3]
  Decode each, stitch into single 1280x1280 PNG

Latent coordinates export:
  Run encoder on full training set
  Save as JSON: [{id, mu: [z1, z2], logvar: [z1, z2], thumb_idx}]
```

### 5.6 Responsive Strategy

Three tiers:

| Tier | Width | Latent canvas | Decoded panel | Layout |
|------|-------|--------------|---------------|--------|
| Mobile | <768px | 300x300 | 128x128 above canvas | Single column, no sticky sections, sprite-only fallback |
| Desktop | 768-1920px | 500x500 | 256x256 side panel | Two-column sticky layout for Acts II-IV |
| Projector | >1920px (P2) | 700x700 | 384x384 | Scaled desktop layout |

Use CSS `clamp()` for fluid intermediate sizes. PointerEvents for unified input handling.

### 5.7 Performance Budgets

| Metric | Target |
|--------|--------|
| First contentful paint | < 1.5s |
| Time to interactive (Act I visible) | < 3s |
| Decode latency (TF.js) | < 5ms at p95 |
| Decode latency (sprite fallback) | < 1ms |
| Hover-to-image update | < 33ms (30fps) |
| Total transfer size | < 1.5MB |
| Particle animation | 60fps with up to 200 particles |

### 5.8 Accessibility

- All interactive canvases have `role="img"` with descriptive `aria-label`
- Pinned points announced via `aria-live="polite"` region
- Expandable annotations use native `<details>/<summary>`
- Color contrast ratios meet WCAG AA against the current background gradient position
- Keyboard: Tab to latent canvas, arrow keys to move cursor, Enter to pin, Escape to unpin last

---

## 6. Implementation Phases

### Phase 1: Foundation (P0.1, P0.2, P0.4, P0.9, P0.10, P0.12, P0.13)

**Goal:** A scrollable page with a working latent space canvas that decodes sunrises.

**Deliverables:**
- index.html with 5 `<section>` elements, scroll observer, background gradient
- Typography and color system applied
- Latent space canvas renders with axes (D3 SVG overlay)
- TF.js decoder loads and decodes on click
- Sprite atlas loads and serves as fallback
- Responsive: does not break at any width

**Exit criteria:** User can open the page, scroll through 5 sections with gradient shift, click anywhere on the latent canvas in Act II, and see a decoded sunrise image.

### Phase 2: Core Interactions (P0.3, P0.5, P0.6, P0.7, P0.8, P0.11)

**Goal:** All the interactive teaching moments work.

**Deliverables:**
- Act I: Grid of thumbnails with FLIP animation to scatter plot
- Act II: Hover-to-decode at 30fps, click-to-pin (up to 4), linear interpolation slider
- Act III: Encoder particle animation (select image, particles converge to latent point)
- Progressive disclosure annotations with KaTeX math on at least 5 key concepts (latent space, encoder, decoder, reconstruction loss, KL divergence)

**Exit criteria:** A user with no ML background can scroll through the page and correctly explain what a VAE does afterward.

### Phase 3: Polish & P1 Features (P1.1-P1.10)

**Goal:** The "wow" factor. The page feels like a sunrise.

**Deliverables:**
- Hero Lissajous animation
- Temperature and beta sliders with live visualization
- KL divergence breathing animation
- Path drawing with Catmull-Rom splines
- Find the Sunrise game
- Film grain overlay
- Scrubbable numbers
- Mobile touch optimization
- Encode-and-verify mode

**Exit criteria:** The page is something you would share on Twitter / Hacker News and feel proud of.

### Phase 4: Extras (P2)

Implement based on user feedback and interest. No formal specification needed until Phase 3 is complete.

---

## 7. Color Reference

```
Background gradient stops:
  0%   scroll: #0B0E2D  (deep indigo night sky)
  50%  scroll: #F5A623  (golden sunrise)
  100% scroll: #FFF8F0  (warm cream daylight)

Encoder palette (cool):
  Primary:    #6C5CE7  (violet)
  Secondary:  #341F97  (deep indigo)
  Accent:     #A29BFE  (light violet)

Decoder palette (warm):
  Primary:    #E17055  (rose)
  Secondary:  #F5A623  (gold)
  Accent:     #FFEAA7  (pale gold)

Interactive elements:
  Glow:       #F5A623 with 0.4 opacity box-shadow
  Hover:      #FDCB6E
  Active:     #E17055

Neutral text:
  On dark BG:  #E8E8F0
  On light BG: #2D3436
  Muted:       #636E72

Code/coordinates:
  #00CEC9 (cyan, on dark backgrounds)
  #6C5CE7 (violet, on light backgrounds)
```

---

## 8. Typography Reference

```
Headlines (Act titles, hero text):
  font-family: 'DM Serif Display', serif
  Sizes: clamp(2rem, 5vw, 4rem) for h1, clamp(1.5rem, 3vw, 2.5rem) for h2

Body text (explanations, annotations):
  font-family: 'Source Sans 3', sans-serif
  Size: clamp(1rem, 1.5vw, 1.25rem)
  Line-height: 1.65
  Max-width: 65ch

Coordinates, code, numeric values:
  font-family: 'JetBrains Mono', monospace
  Size: 0.875em (relative to context)

Math (KaTeX):
  Rendered inline or display-block as appropriate
  Inherits surrounding font size
```

---

## 9. Open Questions (to resolve during implementation)

1. **Training data source:** Where are the sunrise images from? How many? What license? This affects the thumbnail sprite sheet and the model quality. Need to finalize before Phase 1.
2. **Encoder in browser:** The Interaction Designer wants an encode mode (Act III). Running the encoder in TF.js is feasible but doubles the model weight download. Alternative: pre-compute all encodings and animate a "fake" encode using the known (mu, logvar) from latent_coords.json. **Recommendation:** Fake it for P0/P1. Real encoder is P2.
3. **Image resolution:** 64x64 is the practical limit for real-time decode. Is this sufficient visual quality for the "wow" factor? If not, consider 128x128 with a slightly larger model (~800K params, still <5ms inference). Decide after seeing 64x64 results.
4. **Scroll library:** Raw Intersection Observer vs. a lightweight scroll library (e.g., scrollama, ~2KB). Scrollama handles resize/orientation edge cases. **Recommendation:** Use scrollama for robustness, it is tiny.

---

## 10. Summary: What Makes This Design Work

The three proposals are remarkably aligned. The core insight they share is that **the VAE's own decoder is the rendering engine for the visualization**. Instead of showing static diagrams of what a VAE does, the page IS a VAE doing its thing in real time. The user's pointer becomes the latent vector. Their scroll becomes the sunrise. Their curiosity becomes the exploration of latent space.

The main risk is scope creep -- all three proposals are ambitious. The phasing above is designed so that Phase 1 produces a working (if minimal) teaching tool, Phase 2 makes it genuinely good, and Phase 3 makes it remarkable. Each phase is independently shippable.
