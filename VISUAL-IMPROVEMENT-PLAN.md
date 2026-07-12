# AgentIndexed — Visual Improvement Plan

For: implementation agent (Sonnet). Scope: visual/UX only. No content, pricing, or SEO changes.

## Architecture (read first)

- **Static site generator**: `gen.py` (457 lines) reads `listings.json` (116 agents, 13 categories) and writes finished HTML into `agentindexed/` (the deploy dir).
- **CSS source**: `assets/style.css` (215 lines) — inlined/copied into output by gen.py. **Never edit `agentindexed/style.css` directly; it gets overwritten.**
- **JS source**: `assets/search.js`.
- **Build**: `python gen.py` from repo root. Output goes to `agentindexed/`.
- **Deploy**: Vercel serves the `agentindexed/` dir (see `vercel.json`). Live at agentindexed.com + agentindexed.vercel.app.
- Design tokens already in use: bg `#04060C`, body Inter 15px, headings Space Grotesk, accent indigo (`rgb(165,180,252)`), cards `rgba(255,255,255,.027)` + 1px `rgba(255,255,255,.08)` border, 18px radius, gold `rgba(251,191,36,…)` for Featured/sponsor.

**Important**: the live site may be behind local source — gen.py already renders card logos (`logo()` helper, line ~48, used at line ~119) and `.card.is-featured` gold styling exists (style.css lines 111–112). After ANY change, rebuild and diff against live before assuming a task is unfinished. If a task below is already done in source, skip it and note that.

## Tasks (in order)

### 1. Cut the homepage index (biggest win)
The homepage currently renders all 116 agent cards ("The full index" section), making it ~16,000px tall.
- In `gen.py`, find the homepage builder and remove the full-index section.
- Homepage becomes: hero → stats bar → Featured agents → 13 category tiles → How it works → Founding member CTA → FAQ → footer.
- The category tiles and "All Agents" nav link already route users to full listings — no replacement needed.
- Keep `/agents/` (all-agents page) and category pages untouched.

### 2. Clamp card descriptions to 2 lines
Cards have uneven heights because descriptions run 1–4 lines.
- In `assets/style.css`, add to the card description class:
  `display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden`
- Full description still shows on the agent detail page, so nothing is lost.

### 3. Replace emoji category icons with inline SVG
Emoji (🖱️⌨️📱 etc., `ICONS` dict in gen.py ~line 23) render inconsistently per OS.
- Replace the `ICONS` dict values with inline SVG strings — Lucide icons (https://lucide.dev), 24px, `stroke="currentColor"`, colored via CSS with the indigo accent.
- Suggested mapping: Coding→`terminal`, Frameworks→`boxes`, Browser→`mouse-pointer-click`, Voice→`mic`, Support/CRM→`messages-square`, No-Code→`wand-2`, Research→`microscope`, Creative→`palette`, Infrastructure→`server-cog`, Memory→`brain`, Safety→`shield-check`, Industry→`factory`, Consumer→`smartphone`.
- No external requests, no icon font — paste the SVG paths inline (self-contained, zero deps).
- Update wherever ICONS is interpolated (category tiles, category page headers, card kicker labels) so the SVG renders instead of a text glyph.

### 4. Strengthen the Featured tier
`.card.is-featured` exists but is subtle (gold border at 35% alpha).
- Raise resting border to ~55% alpha and add a faint resting glow: `box-shadow:0 0 24px rgba(251,191,36,.10)`.
- Make the ★ FEATURED kicker gold, not gray.
- Keep the "paid = gold" rule consistent: gold appears ONLY on Featured cards, the sponsor bar, and the Founding Member CTA. If indigo is used anywhere in those, switch to gold; if gold leaks anywhere else, remove it.

### 5. Card hierarchy pass
- Card title: Space Grotesk (var(--display)), white.
- Description: 13px, muted gray (`rgb(152,162,184)`), the 2-line clamp from task 2.
- Tags row pinned to card bottom (`margin-top:auto` on the tag container with the card as flex column) so all cards align.

### 6. Verify logos render on live
gen.py already renders favicons via Google s2 + GitHub avatars with a 🤖 `onerror` fallback.
- After rebuild, spot-check ~10 cards in output HTML for `<img src="https://www.google.com/s2/favicons...` or `github.com/....png`.
- If live site lacks them, the fix is simply rebuild + redeploy — do not re-implement.

## Verification (required before done)

1. `python gen.py` runs clean, no tracebacks.
2. Open `agentindexed/index.html` locally in a browser:
   - homepage no longer contains the 116-card full index (search page source for a non-featured agent name, e.g. "Skyvern" — should NOT appear on the homepage)
   - all cards in a row are equal height
   - no emoji glyphs remain in category UI (grep output HTML for 🖱️)
   - Featured cards visibly distinct at a glance
3. Check one category page + one agent detail page still render correctly (they share the same CSS).
4. Mobile check at 375px width — category tile grid and cards must not overflow.
5. Do NOT deploy. Leave rebuilt output committed/staged for Casey to review and push to Vercel himself.

## Out of scope

- listings.json content, copy, pricing links, Stripe URLs
- SEO/meta/schema markup (gen.py has extensive JSON-LD — don't touch)
- search.js behavior
- New pages or nav items
