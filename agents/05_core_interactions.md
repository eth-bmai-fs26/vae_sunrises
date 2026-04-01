# Agent 5: Phase 2 — Core Interactions

## Your Task

Add the core interactive features to `web/index.html`: hover-to-decode, click-to-pin, interpolation slider, and the Act I grid-to-scatter animation.

## Prerequisites

- Working `web/index.html` from Agent 4 (scrolling, canvas, click-to-decode)
- Assets in `web/assets/`

## What to Build

### 1. Hover-to-Decode (Act II)

Replace the click-to-decode with continuous hover decoding:

**Trigger:** `pointermove` on the latent canvas.

**Implementation:**
```javascript
let scheduled = false;
latentCanvas.addEventListener('pointermove', (e) => {
  state.latentCursor = screenToLatent(e.offsetX, e.offsetY);
  if (!scheduled) {
    scheduled = true;
    requestAnimationFrame(async () => {
      await decodeAndRender(state.latentCursor);
      scheduled = false;
    });
  }
});
```

**Visual feedback (all update simultaneously):**
1. Crosshair: thin lines extending from pointer to axes. Rendered in SVG overlay.
2. Axis ticks: small marks on x and y axes showing current z₁, z₂ values.
3. Decoded image: updates in the side panel at 30fps.
4. Coordinate readout: `z = (0.42, -1.31)` below the decoded image. Use JetBrains Mono. Digits should transition smoothly (CSS `transition: transform 100ms` on individual digit spans).

**Edge behavior:** When cursor approaches |z| > 2.5, show a subtle dashed contour line on the canvas indicating the 2σ boundary. Faint text: "Leaving the learned distribution..."

### 2. Click-to-Pin (Act II)

**Trigger:** `pointerdown` on latent canvas.

**Behavior:**
- Drop a pin at the clicked latent coordinate
- Pin visual: 6px filled circle with 2px white border, color from palette: `['#D4845A', '#F2C94C', '#E17055', '#6C8EBF']` (up to 4 pins)
- Pin number label (1-4) rendered in SVG overlay beside the dot
- Small 48×48 decoded thumbnail attached to the pin via a thin line
- Pin coordinates displayed: `(0.42, -1.31)` in small text
- If 4 pins exist, the 5th click replaces the oldest
- Clicking an existing pin removes it (unpin)

**Animation:** Pin appears with scale 0→8px→6px (elastic ease, 300ms).

### 3. Linear Interpolation Slider (Act II)

**Trigger:** When exactly 2 pins exist (or user clicks 2 pins sequentially to select a pair).

**Implementation:**
- Draw a dashed line between the two selected pins on the canvas (SVG overlay)
- A dot marker moves along this line based on slider position
- An HTML `<input type="range">` slider appears below the canvas
  - min=0, max=1, step=0.01
  - Left endpoint shows Pin A thumbnail, right shows Pin B thumbnail
  - Current `t` value displayed between them
- Slider `input` event computes `z_interp = (1-t)*z_A + t*z_B` and decodes
- Decoded image panel shows the interpolated result

**Pair selection:** If more than 2 pins exist, clicking any 2 sequentially selects them as the interpolation pair (highlighted with a connecting line). Other pins remain but are dimmed.

### 4. Grid-to-Scatter Animation (Act I)

**What it does:** Display ~64 training image thumbnails that animate from a neat grid into their latent space positions.

**Data source:** First 64 entries from `latent_coords.json`. Load their thumbnails from the thumbnails sprite sheet.

**Rendering:** All on Canvas2D (NOT DOM elements):
- Compute grid positions (8×8 grid, centered in Act I section)
- Compute scatter positions (z values mapped to canvas coordinates)
- Use GSAP ScrollTrigger with `scrub: true` to interpolate between the two position sets

```javascript
ScrollTrigger.create({
  trigger: '#act-hook',
  start: 'top center',
  end: 'bottom center',
  scrub: true,
  onUpdate: (self) => {
    const t = self.progress;
    renderTiles(t); // interpolate grid→scatter positions
  }
});

function renderTiles(t) {
  const ctx = gridCanvas.getContext('2d');
  ctx.clearRect(0, 0, w, h);
  for (let i = 0; i < 64; i++) {
    const x = lerp(gridPositions[i].x, scatterPositions[i].x, t);
    const y = lerp(gridPositions[i].y, scatterPositions[i].y, t);
    // Draw thumbnail from sprite sheet
    ctx.drawImage(thumbnailsSheet, sx, sy, 32, 32, x-16, y-16, 32, 32);
  }
}
```

**Ease:** Use GSAP's `scrub: 1` (1 second of smooth catchup) so it feels natural.

**Axis labels:** Fade in during the scatter phase (opacity tied to scroll progress). "Time of Year →" on x, "Time of Day →" on y.

### 5. Adaptive Fallback

```javascript
let slowFrames = 0;
async function decodeAuto(z) {
  if (state.useSpriteFallback) return decodeFromAtlas(z);
  const t0 = performance.now();
  const result = await decode(z);
  if (performance.now() - t0 > 33) {
    if (++slowFrames >= 3) {
      state.useSpriteFallback = true;
      showFallbackBadge(); // small "Lite mode" indicator
    }
  } else {
    slowFrames = 0;
  }
  return result;
}
```

## Acceptance Criteria

1. Moving pointer over the canvas produces smooth, lag-free sunrise morphing
2. Pinned sunrises show correct thumbnails and coordinates
3. Interpolation between 2 pins produces smooth morph — every intermediate frame is a plausible sunrise
4. Grid-to-scatter is scroll-controlled — scrubbing back and forth works smoothly
5. Performance: no visible jank at 30fps on a 2020+ laptop
6. All existing functionality from Agent 4 still works (background gradient, responsive layout, etc.)
7. Mobile: hover features gracefully degrade (no crashes, just less interactive)

## What NOT to Build Yet

- Particle animation (Agent 6)
- Progressive disclosure annotations (Agent 6)
- Temperature/beta sliders (Agent 7)
- Game (Agent 7)
- Mobile "Tap to explore" mode switch (Agent 7)
