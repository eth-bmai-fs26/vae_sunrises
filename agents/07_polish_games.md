# Agent 7: Phase 3 — Polish & Games

## Your Task

Add the "wow" layer to `web/index.html`: hero animation, Act IV controls, Find the Sunrise game, and visual polish.

## Prerequisites

- Fully working `web/index.html` from Agent 6 (all P0 features)

## What to Build

### 1. Hero Lissajous Animation (Act I)

On page load, before the user scrolls, a large decoded sunrise image plays a smooth looping animation.

**Implementation:**
- Define a Lissajous curve in latent space: `z₁(t) = 1.5·sin(t), z₂(t) = 1.5·sin(t·φ + π/4)` where φ = golden ratio
- Decode at ~15fps along this curve, displaying each frame in a large hero image (e.g., 384×384 centered)
- The hero image should have a soft glow/shadow
- Loop duration: ~8 seconds per cycle
- Stop the animation when user scrolls past Act I (use ScrollTrigger callback)
- Resume if they scroll back up

### 2. Temperature Slider (Act IV)

**UI:**
```html
<div id="temperature-section">
  <h2>Sampling Temperature</h2>
  <input type="range" id="temp-slider" min="0" max="3" step="0.1" value="1">
  <span id="temp-value">T = 1.0</span>
  <div id="sample-filmstrip"><!-- 8 small canvases --></div>
</div>
```

**Behavior:**
- Pick a point on the canvas (use the most recent pin, or center if no pins)
- At the current temperature T, sample 8 z values: `z_sample = mu + T * sigma * epsilon` where epsilon ~ N(0,1)
- Batch-decode all 8 samples using TF.js batched inference
- Display in a horizontal filmstrip of 8 small images (64×64 each)
- Filmstrip updates every 200ms while the slider is being dragged
- At T=0: all 8 images are identical. At T=3: images vary wildly.
- Show a Gaussian contour on the latent canvas centered on the point, with radius proportional to T. The contour "breathes" (gentle oscillation at 0.5Hz).

**Batched decode:**
```javascript
async function decodeBatch(zArray) {
  return tf.tidy(() => {
    const input = tf.tensor2d(zArray); // shape [8, 2]
    const output = decoder.predict(input); // shape [8, 32, 32, 3]
    return tf.split(output, zArray.length, 0);
  });
}
```

### 3. Beta / KL Divergence Slider (Act IV)

**UI:**
```html
<div id="kl-section">
  <h2>The Balance: Reconstruction vs. Regularization</h2>
  <div id="tug-of-war">
    <span class="tug-label left">Sharp images ←</span>
    <input type="range" id="beta-slider" min="0" max="5" step="0.1" value="1">
    <span class="tug-label right">→ Smooth space</span>
  </div>
  <div id="beta-demo">
    <!-- Side-by-side: reconstruction quality + latent space density -->
  </div>
</div>
```

**Behavior:**
- This is a *conceptual* visualization (we can't retrain the model live)
- Show pre-computed or simulated effects:
  - Low beta: show tight, separated clusters on canvas + sharp reconstructions
  - High beta: show overlapping, smooth distribution + blurrier reconstructions
- Simplest approach: pre-compute 3-5 latent space scatter plots at different beta values during training (or fake them by scaling the z coordinates). Interpolate between them as the slider moves.
- The "tug-of-war" metaphor: a horizontal bar with a marker that tilts left (reconstruction) or right (regularization) based on beta value.

### 4. Find the Sunrise Game (Act V)

**Game setup:**
```html
<div id="game-container">
  <h2>Find the Sunrise</h2>
  <div id="game-target">
    <p>Can you find this sunrise in latent space?</p>
    <canvas id="target-image" width="128" height="128"></canvas>
  </div>
  <div id="game-canvas-wrapper">
    <!-- Reuse the latent canvas, but in game mode -->
  </div>
  <div id="game-score">
    <div id="distance-meter"></div>
    <span id="score-text">Score: --</span>
    <span>Guesses: <span id="guess-count">0</span>/3</span>
  </div>
  <div id="game-controls">
    <select id="difficulty">
      <option value="easy">Easy</option>
      <option value="medium">Medium</option>
      <option value="hard">Hard</option>
    </select>
    <button id="play-btn">Play</button>
    <button id="next-btn" style="display:none">Next Round</button>
  </div>
  <div id="game-stats">Best: <span id="high-score">--</span></div>
</div>
```

**Game flow:**
1. **Play:** Generate a random target z within 2σ of training distribution. Decode it to show the target image.
2. **Guess:** User clicks the latent canvas. A numbered pin drops. The decoded image for their guess appears beside the target.
3. **Scoring:** Distance = Euclidean distance between guess z and target z. Score = max(0, 100 - distance * 33). Display as a radial meter (0-100, colored red→yellow→green).
4. **Feedback text:**
   - Score > 80: "Almost perfect!"
   - Score 50-80: "Getting close. Look at the sky color."
   - Score < 50: "Try a different region."
5. **3 guesses per round.** Previous guess pins remain visible.
6. **Reveal:** After 3 guesses, show the true location with a "bullseye" animation (concentric circles at the target z). Draw a line from the closest guess to the true location.
7. **5 rounds per session.** Track cumulative score.
8. **Difficulty:**
   - Easy: show training point dots + a faint halo around the target region
   - Medium: show training point dots, no halo
   - Hard: hide training point dots and axis labels
9. **High scores:** Save to localStorage (wrapped in try/catch for Safari private mode)

**Distance meter (CSS radial gauge):**
```css
#distance-meter {
  width: 80px; height: 80px;
  border-radius: 50%;
  background: conic-gradient(
    var(--meter-color) calc(var(--meter-pct) * 1%),
    #333 0
  );
  position: relative;
}
```
Update `--meter-pct` and `--meter-color` via JS.

### 5. Post-Encoding Drag Verification (Act III enhancement)

After the encoder particle animation lands a pin:
- Make that pin draggable
- As user drags, decode at the new position and show the result
- Display a subtle "ghost ring" at the original mu position
- Show a thin line connecting the ghost ring to the current drag position
- When released, snap the pin back to mu (or let user leave it wherever)
- This viscerally demonstrates the encoder found the right spot

### 6. Film Grain Overlay

```css
.grain-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  pointer-events: none;
  z-index: 9998;
  opacity: 0.04;
  background-image: url('data:image/png;base64,...'); /* tiny 128×128 noise tile */
  background-size: 128px 128px;
  animation: grain 0.5s steps(4) infinite;
}
@keyframes grain {
  0%, 100% { background-position: 0 0; }
  25% { background-position: -32px -32px; }
  50% { background-position: 64px 32px; }
  75% { background-position: -64px 64px; }
}
```

Generate the noise tile as a base64-encoded PNG (small, ~2KB). Subtle, barely visible.

### 7. Mobile "Tap to Explore" Mode

On touch devices (<768px or `pointerType === 'touch'`):

```html
<div id="explore-toggle" class="mobile-only">
  <button id="enter-explore">Tap to explore the sunrise space</button>
</div>
<!-- When active: -->
<div id="exit-explore" class="mobile-only" style="display:none">
  <button>Done exploring ✓</button>
</div>
```

**Behavior:**
- Default: canvas has `touch-action: pan-y` (scrolls normally)
- Tap "Tap to explore": canvas gets `touch-action: none`, single-finger drag decodes
- Tap "Done exploring": canvas returns to `touch-action: pan-y`
- Visual cue: canvas border glows golden when in explore mode

### 8. Ghost Sunrise Souvenir (Act V)

At the bottom of Act V, show the last sunrise the user decoded:

```html
<div id="souvenir">
  <p>Your sunrise:</p>
  <canvas id="souvenir-image" width="256" height="256"></canvas>
  <p class="coord">z = (0.42, -1.31)</p>
  <p class="label">Early autumn morning</p>
</div>
```

- Updates whenever the user decodes a new image
- The "label" is derived from the z coordinates: map z₁ to season name, z₂ to time-of-day name
- Subtle fade-in animation when it updates

## Acceptance Criteria

1. Hero Lissajous animation loops smoothly on page load, stops on scroll
2. Temperature slider produces visible variation — T=0 identical, T=3 diverse/weird
3. Game is playable: scoring works, difficulty changes behavior, localStorage persists
4. Film grain is barely visible — enhances atmosphere without distracting
5. Mobile mode switch works: canvas scrolls by default, explore mode enables decode
6. Post-encoding drag shows reconstruction degrading as you move away from mu
7. All previous features (hover, pin, interpolation, particles, annotations) still work
8. No console errors, no visible jank
9. The overall page feels polished and cohesive — ready to share publicly
