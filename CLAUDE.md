# AgentIndexed

Static site generator for a directory of AI agents. Live at agentindexed.vercel.app.

## Architecture

- `gen.py` — the whole generator (~460 lines). Reads `listings.json`, writes ~138 finished HTML pages into `agentindexed/`.
- `listings.json` — the data. A flat list of 116 objects, keys: `slug`, `name`, `url`, `category`, `tags`, `description`, `featured`, `plan`. 13 categories.
- `assets/style.css`, `assets/search.js` — the CSS/JS **sources**.
- `agentindexed/` — build output, committed to the repo. Vercel serves it.

## Build

```
python3 gen.py          # from repo root; pillow is optional (OG image only)
```

Vercel runs `pip3 install pillow -q || true; python3 gen.py` on every push to `main` and serves `agentindexed/`.

## Gotchas

- **Never edit anything inside `agentindexed/` by hand.** `gen.py` overwrites it on the next build — that includes `agentindexed/style.css`, which is copied from `assets/style.css`. Edit the source in `assets/`.
- `gen.py` opens every file as UTF-8 via a patched `open` (line 7). The output contains `✦`, `→`, and em-dashes; removing that patch breaks the build on Windows.
- Category names are the join key between `listings.json`, `ICON_PATHS`, and `CC` in `gen.py`. Adding a category means adding an entry to all three or the build raises a `KeyError`.
- Stripe payment links and the contact address are constants at the top of `gen.py`.
- `VISUAL-IMPROVEMENT-PLAN.md` is a historical task list and is partly stale — it describes the accent as indigo, but the palette was since swapped to neon green. Treat the source as truth.

## Adding a listing

Append to `listings.json`, rebuild, commit both the data and the regenerated `agentindexed/` output. Paid placements set `"featured": true` and `"plan": "featured"`.
