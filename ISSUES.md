# GitHub Issues — Create in Order

Use `gh issue create` to create these on the repo, then launch each in Vibe Kanban.

## How to Launch

```bash
# From the repo root, create all issues:
cd /path/to/vae_sunrises

# Issue 1
gh issue create --title "Generate synthetic sunrise dataset" \
  --body "$(cat agents/01_dataset_generator.md)" \
  --label "agent"

# Issue 2
gh issue create --title "Train VAE on synthetic sunrises" \
  --body "$(cat agents/02_vae_training.md)" \
  --label "agent"

# Issue 3
gh issue create --title "Export decoder to TF.js and generate sprite atlas" \
  --body "$(cat agents/03_model_export.md)" \
  --label "agent"

# Issue 4
gh issue create --title "Build scrollytelling skeleton with latent canvas and decode" \
  --body "$(cat agents/04_scroll_shell.md)" \
  --label "agent"

# Issue 5
gh issue create --title "Add hover-to-decode, pin, interpolate, and grid-to-scatter" \
  --body "$(cat agents/05_core_interactions.md)" \
  --label "agent"

# Issue 6
gh issue create --title "Add encoder particle animation and math annotations" \
  --body "$(cat agents/06_encoder_disclosure.md)" \
  --label "agent"

# Issue 7
gh issue create --title "Add hero animation, temperature slider, game, and polish" \
  --body "$(cat agents/07_polish_games.md)" \
  --label "agent"
```

## Launch Order in Vibe Kanban

| Order | Issue | Depends On | Est. Complexity |
|-------|-------|------------|-----------------|
| 1 | Generate synthetic sunrise dataset | — | Medium |
| 2 | Train VAE on synthetic sunrises | #1 | Medium |
| 3 | Export decoder to TF.js and sprite atlas | #2 | Medium-High |
| 4 | Build scrollytelling skeleton | #3 | High |
| 5 | Add core interactions | #4 | High |
| 6 | Add encoder animation + disclosure | #5 | Medium-High |
| 7 | Add polish, games, mobile | #6 | High |

**Important:** Each agent must complete and merge before the next one starts.
Agents 1-3 produce data/model artifacts. Agents 4-7 build the web page incrementally.

## Verification Between Agents

After each agent completes, verify before launching the next:

- **After Agent 1:** Open `dataset/preview.png` — do the sunrises look good?
- **After Agent 2:** Open `checkpoints/latent_space.png` — is the latent space structured?
- **After Agent 3:** Check `web/assets/` — do all files exist? Is the atlas smooth?
- **After Agent 4:** Open `web/index.html` in browser — does it scroll and decode?
- **After Agent 5:** Hover over the canvas — does it morph smoothly?
- **After Agent 6:** Does the particle animation fire? Do annotations expand?
- **After Agent 7:** Play the game. Is it fun? Share the URL.
