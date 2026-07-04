# AgentIndexed

The curated directory of AI agents — live at [agentindexed.vercel.app](https://agentindexed.vercel.app).

## How it works

- `gen.py` — static site generator. Reads `listings.json`, writes the full site (~138 pages) to `agentindexed/`.
- `listings.json` — the directory data: 116 agents across 13 categories.
- `assets/` — stylesheet and search script consumed by the generator.
- `vercel.json` — tells Vercel to run the generator at build time and serve `agentindexed/`.

## Deploy

Every push to `main` triggers a Vercel build: `pip3 install pillow && python3 gen.py`, output served from `agentindexed/`.

## Adding or upgrading a listing

1. Edit `listings.json` (set `"featured": true` and `"plan": "featured"` for paid placements).
2. Commit and push — Vercel rebuilds automatically.

## Revenue

Stripe payment links (Featured $49 one-time, Pro $19/mo, Homepage Sponsor $99/mo) are configured in `gen.py`.
