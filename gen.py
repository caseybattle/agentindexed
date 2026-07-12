#!/usr/bin/env python3
"""AgentIndexed generator v3 — max optimization build."""
import json, os, html, re, functools
from datetime import date, datetime, timezone
from urllib.parse import urlparse, quote

open = functools.partial(open, encoding="utf-8")  # ponytail: Windows cp1252 default breaks on unicode (✦, →, em-dash) in output

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(BASE, "agentindexed")
SITE = "AgentIndexed"
DOMAIN = "https://agentindexed.com"
LIVE = "https://agentindexed.vercel.app"
CONTACT = "casbattle19@gmail.com"
LINK_FEATURED = "https://buy.stripe.com/3cI28r4Wm0Z4bnS0T79oc0a"
LINK_PRO = "https://buy.stripe.com/14A00j88yazEajOatH9oc0b"
LINK_SPONSOR = "https://buy.stripe.com/3cI5kD60qazE2Rm8lz9oc0c"
TODAY = date.today()

listings = json.load(open(os.path.join(BASE, "listings.json")))
cats = {}
for l in listings: cats.setdefault(l["category"], []).append(l)

ICON_PATHS = {
"Coding Agents": '<polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line>',
"Frameworks & SDKs": '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.73Z"></path><path d="m3.3 7 8.7 5 8.7-5"></path><path d="M12 22V12"></path>',
"Browser & Computer Use": '<path d="m9 9 5 12 1.8-5.2L21 14Z"></path><path d="M7.2 2.2 8 5.1"></path><path d="m5.1 8-2.9-.8"></path><path d="M14 4.1 12 6"></path><path d="m6 12-1.9 2"></path>',
"Voice Agents": '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line>',
"Customer Support & CRM": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z"></path>',
"No-Code Builders": '<path d="m21.64 3.64-1.28-1.28a1.21 1.21 0 0 0-1.72 0L2.36 18.64a1.21 1.21 0 0 0 0 1.72l1.28 1.28a1.2 1.2 0 0 0 1.72 0L21.64 5.36a1.2 1.2 0 0 0 0-1.72Z"></path><path d="m14 7 3 3"></path><path d="M5 6v4"></path><path d="M19 14v4"></path><path d="M10 2v2"></path><path d="M7 8H3"></path><path d="M21 16h-4"></path><path d="M11 3H9"></path>',
"Research Agents": '<path d="M6 18h8"></path><path d="M3 22h18"></path><path d="M14 22a7 7 0 1 0 0-14h-1"></path><path d="M9 14h2"></path><path d="M9 12a2 2 0 0 1-2-2V6h6v4a2 2 0 0 1-2 2Z"></path><path d="M12 6V3a1 1 0 0 0-1-1H9a1 1 0 0 0-1 1v3"></path>',
"Creative Agents": '<circle cx="13.5" cy="6.5" r=".5"></circle><circle cx="17.5" cy="10.5" r=".5"></circle><circle cx="8.5" cy="7.5" r=".5"></circle><circle cx="6.5" cy="12.5" r=".5"></circle><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2Z"></path>',
"Infrastructure & Tooling": '<rect x="2" y="2" width="20" height="8" rx="2"></rect><rect x="2" y="14" width="20" height="8" rx="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line>',
"Memory & Context": '<path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"></path><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"></path>',
"Safety & Observability": '<path d="M20 13c0 5-3.5 7.5-8 9-4.5-1.5-8-4-8-9V6l8-3 8 3Z"></path><path d="m9 12 2 2 4-4"></path>',
"Industry Agents": '<path d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a1 1 0 0 0-1.6-.8L2 8Z"></path><path d="M17 18h1"></path><path d="M12 18h1"></path><path d="M7 18h1"></path>',
"Consumer Platforms": '<rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line>',
}
def _icon(paths): return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="cat-svg" aria-hidden="true">{paths}</svg>'
ICONS = {c: _icon(p) for c,p in ICON_PATHS.items()}

CC = {
"Coding Agents":{"intro":"Coding agents pair-program, review pull requests, and in some cases ship entire features autonomously. The category spans terminal-first tools, IDE-native assistants, and fully autonomous software engineers that take a ticket and return a tested pull request.","choose":["Match the agent to where you actually work — terminal, IDE, or CI pipeline","Check repo-scale context handling if you have a large codebase","Prefer agents with permission gates and reviewable diffs if they can execute code"],"uses":["Automating bug fixes and refactors from issue to pull request","AI pair programming inside the IDE or terminal","Automated code review, testing, and security scanning in CI"]},
"Frameworks & SDKs":{"intro":"Agent frameworks and SDKs are the foundation layer — orchestration, role-based multi-agent collaboration, tool calling, and state management. Most production agent systems in 2026 are built on one of the frameworks listed here.","choose":["Decide between code-first (Python/TypeScript) and declarative orchestration","Check protocol support — MCP, tool calling, agent-to-agent messaging","Weigh community size and production adoption before committing"],"uses":["Building custom single or multi-agent applications","Orchestrating role-based agent teams for complex workflows","Adding tool use, memory, and planning to LLM apps"]},
"Browser & Computer Use":{"intro":"Browser and computer-use agents click, type, scroll, and navigate real interfaces — automating the web and desktop the way a human operator would. They power everything from QA testing to autonomous research and form-filling.","choose":["Verify it handles authentication, iframes, and dynamic pages","Look for permission gates before irreversible actions","Check speed — DOM-native agents beat pixel-based clicking"],"uses":["Automating repetitive web workflows and form-filling","End-to-end QA testing without brittle scripts","Autonomous research and data collection across sites"]},
"Voice Agents":{"intro":"Voice agents hold real-time spoken conversations — answering calls, qualifying leads, and handling support with sub-second latency. The category covers full phone-agent platforms and the speech infrastructure underneath them.","choose":["Test latency and interruption handling first — they make or break the experience","Check telephony integrations (SIP, Twilio) for call-center use","Evaluate voice quality and language coverage for your market"],"uses":["24/7 AI phone answering and appointment booking","Outbound lead qualification calls at scale","Voice interfaces for products and devices"]},
"Customer Support & CRM":{"intro":"Support and CRM agents resolve tickets, draft replies, and keep customer data in sync — deflecting repetitive volume so human teams handle the judgment calls. Leading deployments resolve a large share of inbound conversations autonomously.","choose":["Measure resolution rate on your own tickets, not vendor demos","Check integrations with the helpdesk and CRM you already use","Look for smooth human handoff with full conversation context"],"uses":["Autonomous first-line ticket resolution","Drafting replies for human review","Keeping CRM records updated from conversations automatically"]},
"No-Code Builders":{"intro":"No-code agent builders let non-developers assemble working agents with visual canvases, templates, and drag-and-drop tooling. They are the fastest path from idea to deployed agent — no engineering team required.","choose":["Check export and API options so you are not locked in","Verify connector coverage for the tools you use daily","Test the debugging experience — visual builders vary wildly here"],"uses":["Internal workflow automations built by ops teams","Customer-facing chatbots and intake flows","Prototyping agent ideas before committing engineering time"]},
"Research Agents":{"intro":"Deep research agents plan multi-step investigations, browse dozens of sources, and return cited reports — compressing hours of analyst work into minutes. They are becoming standard kit for analysts, marketers, and founders.","choose":["Demand inline citations — uncited research is unusable","Check source freshness and how paywalled content is handled","Look for structured outputs (tables, briefs), not just prose"],"uses":["Market and competitor research with cited sources","Literature reviews and technical deep-dives","Due-diligence briefs on companies and markets"]},
"Creative Agents":{"intro":"Creative agents generate and edit images, video, music, and design assets — increasingly as autonomous pipelines rather than single prompts. This category covers the tools turning briefs into finished creative work.","choose":["Check commercial licensing on generated output","Evaluate consistency features (characters, brand styles) for series work","Look at editing depth, not just first-generation quality"],"uses":["Producing marketing visuals and video at scale","Automated content pipelines from brief to asset","Design iteration and creative exploration"]},
"Infrastructure & Tooling":{"intro":"Agent infrastructure covers the layer that makes agents production-ready: deployment, hosting, sandboxed execution, tool integration, and scaling. If frameworks are the engine, this is the drivetrain.","choose":["Prioritize sandboxing and isolation for code-executing agents","Check cold-start times and scaling behavior for bursty loads","Verify observability hooks integrate with your existing stack"],"uses":["Deploying and scaling agents in production","Sandboxed code execution for untrusted agent actions","Connecting agents to third-party tools and APIs safely"]},
"Memory & Context":{"intro":"Memory and context tools give agents persistence — long-term recall, user preferences, and knowledge that survives across sessions. The difference between a demo and a product is usually in this layer.","choose":["Decide between managed memory services and self-hosted stores","Check retrieval quality, not just storage features","Look for privacy controls and per-user data isolation"],"uses":["Persistent user memory across agent sessions","RAG pipelines grounding agents in private data","Long-horizon task state for multi-day workflows"]},
"Safety & Observability":{"intro":"Safety and observability tools are how teams ship agents without losing sleep: guardrails, evals, tracing, and monitoring for systems that act autonomously. As agents touch production data, this category moves from optional to mandatory.","choose":["Trace-level debugging is non-negotiable for multi-step agents","Check guardrail latency — slow filters break real-time UX","Prefer eval tooling that runs in CI, not just dashboards"],"uses":["Tracing and debugging multi-step agent runs","Guardrails against prompt injection and unsafe outputs","Continuous evals that catch regressions before users do"]},
"Industry Agents":{"intro":"Industry agents are purpose-built for one vertical — healthcare, security, finance — with the domain knowledge, integrations, and compliance posture that generic agents lack. Specialization is why they win.","choose":["Verify the compliance certifications your industry requires","Check integrations with your vertical's systems of record","Prefer vendors with reference customers in your exact niche"],"uses":["Vertical workflows generic agents cannot handle","Compliance-sensitive automation with audit trails","Domain-specific copilots for professional teams"]},
"Consumer Platforms":{"intro":"Consumer agent platforms bring multi-agent power to everyday users — personal assistants, agent app stores, and interfaces that orchestrate agents behind a simple chat. This is where agents meet the mainstream.","choose":["Look at the ecosystem — more agents means more use cases","Check cross-device support and data portability","Weigh privacy policies carefully for personal data"],"uses":["Personal task automation and daily assistance","Discovering and combining third-party agents","Consumer-grade interfaces over complex agent systems"]},
}

def cslug(c): return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',c.lower())).strip('-')
def esc(s): return html.escape(s, quote=True)
def dom(u):
    try: return urlparse(u).netloc
    except: return ""
def logo(l, sz=64):
    d = dom(l["url"])
    if d == "github.com":
        parts = urlparse(l["url"]).path.strip("/").split("/")
        if parts and parts[0]: return f"https://github.com/{parts[0]}.png?size={sz*2}"
    return f"https://www.google.com/s2/favicons?domain={d}&sz={min(sz*2,128)}"
def jld(obj): return '<script type="application/ld+json">'+json.dumps(obj,separators=(",",":"))+'</script>'

CSS = open(os.path.join(BASE, "assets", "style.css")).read()

JS = open(os.path.join(BASE, "assets", "search.js")).read()

HEAD_EXTRA = '<script defer src="/_vercel/insights/script.js"></script>'

def page(title, desc, body, canonical="", schema=None, noindex=False):
    robots = '<meta name="robots" content="noindex,nofollow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">'
    sc = "".join(jld(s) for s in (schema or []))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}
<link rel="canonical" href="{DOMAIN}{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{DOMAIN}{canonical}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:image" content="{DOMAIN}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{DOMAIN}/og.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://www.google.com">
<link rel="alternate" type="application/rss+xml" title="{SITE} — new AI agents" href="{DOMAIN}/feed.xml">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='24' fill='%2316a34a'/><text x='50' y='68' font-size='52' text-anchor='middle' fill='white' font-family='sans-serif' font-weight='bold'>A</text></svg>">
{sc}{HEAD_EXTRA}
</head>
<body>
<div class="sponsor-bar">✦ This sponsor slot is available — put your AI product in front of every visitor. <a href="/pricing/">Become the sponsor →</a></div>
<header><div class="wrap nav">
<a class="logo" href="/"><span class="dot">▲</span>Agent<span>Indexed</span></a>
<nav class="nav-links" aria-label="Main">
<a href="/#categories">Categories</a><a href="/#categories">All Agents</a><a href="/pricing/">Pricing</a>
<a class="btn btn-p" href="/submit/">Submit Agent</a>
</nav>
</div></header>
{body}
<footer><div class="wrap foot">
<div style="max-width:300px"><div class="brand">▲ {SITE}</div>The curated index of AI agents. Hand-reviewed listings, honest categories, zero fluff — built for people who ship.<br><br>© {TODAY.year} {SITE}</div>
<div class="cols">
<div><h4>Directory</h4><li><a href="/#categories">Categories</a></li><li><a href="/#categories">All agents</a></li><li><a href="/feed.xml">RSS feed</a></li><li><a href="/sitemap.xml">Sitemap</a></li></div>
<div><h4>For builders</h4><li><a href="/submit/">Submit an agent</a></li><li><a href="/pricing/">Get featured</a></li><li><a href="/pricing/">Sponsorship</a></li></div>
<div><h4>Company</h4><li><a href="/about/">About</a></li><li><a href="/terms/">Terms</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="/refunds/">Refund policy</a></li><li><a href="mailto:{CONTACT}">Contact</a></li></div>
</div>
</div></footer>
<script src="/search.js" defer></script>
</body></html>"""

def card(l):
    b = '<span class="badge">★ Featured</span>' if l["featured"] else ""
    fc = " is-featured" if l["featured"] else ""
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in l["tags"])
    return f"""<a class="card{fc} reveal" href="/agents/{l['slug']}/">{b}
<div class="card-top"><div class="card-logo"><img src="{logo(l)}" alt="{esc(l['name'])} logo" loading="lazy" width="26" height="26" onerror="this.replaceWith('🤖')"></div>
<div><span class="cat">{esc(l['category'])}</span><h3>{esc(l['name'])}</h3></div></div>
<p>{esc(l['description'])}</p><div class="tags">{tags}<span class="go">View →</span></div></a>"""

os.makedirs(ROOT, exist_ok=True)
open(os.path.join(ROOT,"style.css"),"w").write(CSS)
open(os.path.join(ROOT,"search.js"),"w").write(JS)
idx = [{"n":l["name"],"s":l["slug"],"c":l["category"],"d":l["description"],"h":dom(l["url"])} for l in listings]
json.dump(idx, open(os.path.join(ROOT,"search-index.json"),"w"))
featured = [l for l in listings if l["featured"]]
cat_names = sorted(cats.keys())

HOME_FAQ = [
("What is AgentIndexed?", f"AgentIndexed is a hand-curated directory of {len(listings)} AI agents, frameworks, and tools organized into {len(cat_names)} categories — from coding agents to voice platforms. Every listing is reviewed before it goes live."),
("How do I submit my AI agent?", "Use the submit page — basic listings are free and reviewed within 5–7 days. Featured listings ($49 one-time) are reviewed within 24 hours and placed at the top of their category and on the homepage."),
("What does a Featured listing include?", "Twelve months at the top of your category, placement in the homepage featured section, a Featured badge, a dofollow backlink to your site, and priority 24-hour review."),
("Do listings include a dofollow backlink?", "Yes. Every listing — free or paid — links to your site with a standard dofollow link that search engines and AI assistants can follow."),
("How are agents ranked?", "Categories list featured placements first, then all agents alphabetically. Search results are never pay-to-play — they match on name, description, and category only."),
]
def faq_html(qs): return '<div class="faq">'+ "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q,a in qs) +"</div>"
def faq_schema(qs): return {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qs]}
def crumbs_schema(items): return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":DOMAIN+u} for i,(n,u) in enumerate(items)]}

# ---------- HOME ----------
strip_domains = ["anthropic.com","openai.com","github.com","google.com","microsoft.com","aws.amazon.com","huggingface.co","langchain.com"]
strip = "".join(f'<img src="https://www.google.com/s2/favicons?domain={d}&sz=64" alt="{d}" loading="lazy" width="26" height="26">' for d in strip_domains)
cat_cards = "".join(f'<a class="cat-card reveal" href="/categories/{cslug(c)}/"><div class="cat-ico">{ICONS.get(c,"")}</div><div><b>{esc(c)}</b><span>{len(cats[c])} agents</span></div></a>' for c in cat_names)
feat_cards = "".join(card(l) for l in featured)

home_schema = [
 {"@context":"https://schema.org","@type":"WebSite","name":SITE,"url":DOMAIN,"description":f"Curated directory of {len(listings)} AI agents and tools."},
 {"@context":"https://schema.org","@type":"Organization","name":SITE,"url":DOMAIN,"email":CONTACT},
 faq_schema(HOME_FAQ),
]
home_body = f"""
<div class="hero">
<div class="orb orb-1"></div><div class="orb orb-2"></div>
<div class="wrap">
<span class="pill"><span class="live"></span> <b>{len(listings)} agents indexed</b> · updated {TODAY.strftime('%B %Y')}</span>
<h1>Find the right <em>AI&nbsp;agent</em><br>for any job</h1>
<p class="lead">The hand-curated index of AI agents, frameworks and tools that actually ship — organized into {len(cat_names)} honest categories, with zero pay-to-play rankings in search.</p>
<div class="cta"><a class="btn btn-p" href="/submit/">Submit your agent</a><a class="btn btn-o" href="#categories">Browse categories ↓</a></div>
<div class="search"><div class="glow"></div><span class="ico">⌕</span><input id="q" type="search" aria-label="Search agents" placeholder="Search {len(listings)} agents — try 'coding', 'voice', 'browser'…" autocomplete="off"><div id="results"></div></div>
<div class="logostrip"><p>Indexing agents &amp; frameworks from</p><div class="logos">{strip}</div></div>
<div class="stats"><div><b>{len(listings)}</b><span>agents listed</span></div><div><b>{len(cat_names)}</b><span>categories</span></div><div><b>24h</b><span>featured review</span></div><div><b>100%</b><span>hand-curated</span></div></div>
</div></div>
<section class="wrap"><div class="sec-head"><div><h2 class="sec">★ <span class="em">Featured</span> Agents</h2><p class="sub">Premium placements from teams that want to be found.</p></div><a class="sec-link" href="/pricing/">Get your agent here →</a></div><div class="grid">{feat_cards}</div></section>
<section class="wrap" id="categories"><div class="sec-head"><div><h2 class="sec">Browse by <span class="em">category</span></h2><p class="sub">Every agent, organized by what it actually does — not by who paid.</p></div></div><div class="cat-grid">{cat_cards}</div></section>
<section class="wrap"><div class="sec-head"><div><h2 class="sec">How it <span class="em">works</span></h2><p class="sub">From submission to discovery in three steps.</p></div></div>
<div class="steps">
<div class="step reveal"><span class="n">01</span><b>Submit your agent</b><p>Two-minute form. Free listings always open; Featured gets 24-hour priority review.</p></div>
<div class="step reveal"><span class="n">02</span><b>We review &amp; publish</b><p>Every listing is checked by a human. No spam, no dead links, no AI-generated junk sites.</p></div>
<div class="step reveal"><span class="n">03</span><b>Get discovered</b><p>Your own SEO page, a dofollow backlink, and visibility in the AI assistants that crawl this index.</p></div>
</div></section>
<section class="wrap"><div class="upsell reveal"><div class="upsell-in"><h3>🎉 Founding Member spots — free Featured placement, first 20 only</h3><p>Free listings are always open. For launch week, the first 20 agents get Featured placement (top of category + homepage) at no cost in exchange for a short testimonial — normally a one-time $49.</p><a class="btn btn-gold" href="/pricing/">Claim a founding spot →</a></div></div></section>
<section class="wrap"><div class="sec-head"><div><h2 class="sec">Frequently asked <span class="em">questions</span></h2></div></div>{faq_html(HOME_FAQ)}</section>
"""
open(os.path.join(ROOT,"index.html"),"w").write(page(
 f"{SITE} — Directory of {len(listings)}+ AI Agents, Frameworks & Tools (2026)",
 f"Discover {len(listings)} curated AI agents across coding, voice, browser automation, customer support and more. Submit your AI agent — free listings, featured placement from $49.",
 home_body, canonical="/", schema=home_schema))

# ---------- CATEGORY PAGES ----------
for c in cat_names:
    ls = sorted(cats[c], key=lambda x:(not x["featured"],x["name"].lower()))
    cc = CC[c]
    cat_faq = [
      (f"What are the best {c.lower()} in 2026?", f"AgentIndexed currently lists {len(ls)} {c.lower()}, including "+", ".join(x["name"] for x in ls[:4])+" and more. Featured placements appear first, then all tools alphabetically."),
      (f"How do I choose between {c.lower()}?", " ".join(cc["choose"])+"."),
      (f"How do I add my tool to this list?", "Submit it free on the submit page (reviewed in 5–7 days), or go Featured for $49 to be reviewed within 24 hours and placed at the top of this category."),
    ]
    schema = [
      {"@context":"https://schema.org","@type":"ItemList","name":f"Best {c} 2026","numberOfItems":len(ls),"itemListElement":[{"@type":"ListItem","position":i+1,"name":x["name"],"url":f"{DOMAIN}/agents/{x['slug']}/"} for i,x in enumerate(ls)]},
      crumbs_schema([("Home","/"),(c,f"/categories/{cslug(c)}/")]),
      faq_schema(cat_faq),
    ]
    body = f"""
<div class="wrap crumb"><a href="/">Home</a> <span style="opacity:.4">/</span> {esc(c)}</div>
<section class="wrap" style="padding-top:20px">
<div class="sec-head"><div><h1 class="sec" style="font-size:2.3rem">{ICONS.get(c,"")}<span class="em">{esc(c)}</span></h1>
<p class="sub" style="max-width:720px">{esc(cc['intro'])}</p></div>
<a class="sec-link" href="/pricing/">Get the top spot →</a></div>
<div class="grid">{"".join(card(l) for l in ls)}</div>
<div class="prose" style="margin-top:44px"><h2>How to choose {esc(c.lower())}</h2><ul>{"".join(f"<li>{esc(x)}</li>" for x in cc["choose"])}</ul>
<h2>Common use cases</h2><ul>{"".join(f"<li>{esc(x)}</li>" for x in cc["uses"])}</ul></div>
<div class="sec-head" style="margin-top:40px"><h2 class="sec">FAQ</h2></div>{faq_html(cat_faq)}
<div class="upsell reveal" style="margin-top:40px"><div class="upsell-in"><h3>Want the #1 spot in {esc(c)}?</h3><p>Featured agents appear first in this category and on the homepage. One-time $49, live within 24 hours.</p><a class="btn btn-gold" href="/pricing/">Get featured →</a></div></div>
</section>"""
    d = os.path.join(ROOT,"categories",cslug(c)); os.makedirs(d, exist_ok=True)
    open(os.path.join(d,"index.html"),"w").write(page(
      f"Best {c} in 2026 — {len(ls)} Tools Compared | {SITE}",
      f"{cc['intro'][:150]}",
      body, canonical=f"/categories/{cslug(c)}/", schema=schema))

# ---------- AGENT DETAIL PAGES ----------
for l in listings:
    c = l["category"]; cc = CC[c]
    peers = [x for x in cats[c] if x["slug"] != l["slug"]]
    related = peers[:6]
    rel_html = "".join(card(x) for x in related)
    alt_names = ", ".join(x["name"] for x in peers[:5])
    fb = '<span class="badge" style="position:static;margin-left:12px;vertical-align:middle">★ Featured</span>' if l["featured"] else ""
    agent_faq = [
      (f"What is {l['name']}?", f"{l['name']} is a tool in the {c.lower()} category. {l['description']}"),
      (f"What is {l['name']} used for?", f"Tools in this category are commonly used for: "+ "; ".join(cc["uses"]).lower()+"."),
      (f"What are alternatives to {l['name']}?", f"Popular alternatives in the {c.lower()} category include {alt_names}. Compare them all on the {c} category page."),
    ]
    schema = [
      {"@context":"https://schema.org","@type":"SoftwareApplication","name":l["name"],"url":l["url"],"applicationCategory":c,"description":l["description"],"operatingSystem":"Web"},
      crumbs_schema([("Home","/"),(c,f"/categories/{cslug(c)}/"),(l["name"],f"/agents/{l['slug']}/")]),
      faq_schema(agent_faq),
    ]
    body = f"""
<div class="wrap crumb"><a href="/">Home</a> <span style="opacity:.4">/</span> <a href="/categories/{cslug(c)}/">{esc(c)}</a> <span style="opacity:.4">/</span> {esc(l['name'])}</div>
<div class="wrap detail">
<div class="detail-head">
<div class="detail-logo"><img src="{logo(l,128)}" alt="{esc(l['name'])} logo" width="46" height="46" onerror="this.replaceWith('🤖')"></div>
<div><span class="cat">{esc(c)}</span><h1>{esc(l['name'])}{fb}</h1></div>
</div>
<p class="desc">{esc(l['description'])}</p>
<div class="kv">
<div><span>Category</span><b>{esc(c)}</b></div>
<div><span>Website</span><b>{esc(dom(l['url']))}</b></div>
<div><span>Tags</span><b>{esc(", ".join(l['tags']) or "—")}</b></div>
<div><span>Listing</span><b>{"★ Featured" if l['featured'] else "Standard"}</b></div>
</div>
<div class="actions">
<a class="btn btn-p" href="{esc(l['url'])}" target="_blank" rel="noopener">Visit {esc(l['name'])} ↗</a>
<a class="btn btn-o" href="/categories/{cslug(c)}/">More {esc(c)}</a>
</div>
<div class="prose"><h2>What {esc(l['name'])} is for</h2><p>{esc(l['name'])} sits in the {esc(c.lower())} category of the agent stack. {esc(cc['intro'])}</p>
<h2>Typical use cases</h2><ul>{"".join(f"<li>{esc(x)}</li>" for x in cc["uses"])}</ul></div>
<div class="claim"><b>Is this your agent?</b><p>Claim this listing to update the description and upgrade to Featured or Pro placement. Email <a href="mailto:{CONTACT}?subject=Claim listing: {esc(l['name'])}">{CONTACT}</a> or <a href="/pricing/">see upgrade options</a>.</p></div>
<div class="sec-head" style="margin-top:48px"><h2 class="sec">FAQ</h2></div>{faq_html(agent_faq)}
<div class="sec-head" style="margin-top:48px"><h2 class="sec">Alternatives &amp; related in {esc(c)}</h2></div>
<div class="grid">{rel_html}</div>
</div>"""
    d = os.path.join(ROOT,"agents",l["slug"]); os.makedirs(d, exist_ok=True)
    open(os.path.join(d,"index.html"),"w").write(page(
      f"{l['name']} — {c}: Features, Use Cases & Alternatives | {SITE}",
      f"{l['name']}: {l['description'][:120]} Compare alternatives in {c.lower()}.",
      body, canonical=f"/agents/{l['slug']}/", schema=schema))
print("core pages done")

# ---------- PRICING ----------
pricing_faq = [
 ("How fast does a paid listing go live?","Featured and Pro listings are reviewed and published within 24 hours of receiving your details. If we miss that window, you get a full refund."),
 ("Is there a refund policy?","Yes — Featured listings carry a 7-day money-back guarantee, and subscriptions can be cancelled anytime. See the refund policy page for details."),
 ("What details do I send after paying?","Your agent's name, website URL, category, and a one-sentence description — email them to "+CONTACT+" or reply to your Stripe receipt. You'll be redirected to instructions right after checkout."),
]
pricing_body = f"""
<div class="wrap crumb"><a href="/">Home</a> <span style="opacity:.4">/</span> Pricing</div>
<section class="wrap" style="padding-top:20px">
<div style="text-align:center;max-width:640px;margin:0 auto 34px">
<h1 class="sec" style="font-size:2.5rem">Get your agent <span class="em">discovered</span></h1>
<p class="sub" style="margin:14px auto 0">Every listing includes a dofollow backlink. Payments are secured by Stripe. Featured &amp; Pro listings go live within 24 hours — or your money back.</p>
</div>
<div class="upsell reveal" style="margin-bottom:34px"><div class="upsell-in"><h3>🎉 Founding Member spots — free Featured placement, first 20 only</h3><p>We just launched. In exchange for a short testimonial and permission to use your logo, we'll give the first 20 agents top-of-category + homepage Featured placement at no cost — normally $49. Once 20 are claimed, this offer closes and Featured reverts to paid.</p><a class="btn btn-gold" href="mailto:{CONTACT}?subject=Founding Member spot&body=Agent name:%0AWebsite URL:%0ACategory:%0AOne-line testimonial about AgentIndexed (or why you'd want to be listed):" style="justify-content:center">Claim a founding spot →</a></div></div>
<div class="price-grid">
<div class="price"><h3>Basic Listing</h3><div class="amt">$0</div>
<ul><li>Standard listing in your category</li><li>Dofollow backlink to your site</li><li>Reviewed within 5–7 days</li></ul>
<a class="btn btn-o" href="/submit/" style="justify-content:center">Submit free →</a></div>
<div class="price hot"><span class="pop">Most popular</span><h3>Featured Listing</h3><div class="amt">$49 <small>one-time</small></div>
<ul><li>Top of your category for 12 months</li><li>Homepage featured section</li><li>★ Featured badge</li><li>Dofollow backlink</li><li>Priority 24-hour review</li></ul>
<a class="btn btn-p" href="{LINK_FEATURED}" style="justify-content:center">Get Featured — $49</a></div>
<div class="price"><h3>Pro Listing</h3><div class="amt">$19 <small>/month</small></div>
<ul><li>Everything in Featured</li><li>Permanent top placement</li><li>Listing updates any time</li><li>Launch &amp; update re-promotion</li><li>Cancel anytime</li></ul>
<a class="btn btn-o" href="{LINK_PRO}" style="justify-content:center">Go Pro — $19/mo</a></div>
<div class="price"><h3>Homepage Sponsor</h3><div class="amt">$99 <small>/month</small></div>
<ul><li>Exclusive banner on every page</li><li>Your logo, tagline &amp; link</li><li>Only one sponsor at a time</li><li>Cancel anytime</li></ul>
<a class="btn btn-gold" href="{LINK_SPONSOR}" style="justify-content:center">Claim sponsor slot</a></div>
</div>
<div class="sec-head" style="margin-top:44px"><h2 class="sec">Pricing FAQ</h2></div>{faq_html(pricing_faq)}
</section>"""
d=os.path.join(ROOT,"pricing");os.makedirs(d,exist_ok=True)
open(os.path.join(d,"index.html"),"w").write(page(f"Pricing — Feature Your AI Agent | {SITE}","List your AI agent free, or get featured placement with a dofollow backlink from $49. 24-hour review, 7-day money-back guarantee.",pricing_body,canonical="/pricing/",schema=[faq_schema(pricing_faq),crumbs_schema([("Home","/"),("Pricing","/pricing/")])]))

# ---------- SUBMIT ----------
cat_opts="".join(f'<option>{esc(c)}</option>' for c in sorted(cats.keys()))
submit_body = f"""
<div class="wrap crumb"><a href="/">Home</a> <span style="opacity:.4">/</span> Submit</div>
<section class="wrap" style="padding-top:20px;max-width:700px">
<h1 class="sec" style="font-size:2.3rem">Submit your <span class="em">AI agent</span></h1>
<p class="sub" style="margin-top:12px">Free listings are reviewed in 5–7 days. Want it live tomorrow at the top of the category? <a href="/pricing/" style="color:#86efac;font-weight:600">Go Featured for $49 →</a></p>
<form id="subform" style="margin-top:10px">
<label for="f-name">Agent name *</label><input required id="f-name" placeholder="e.g. AcmeAgent">
<label for="f-url">Website URL *</label><input required id="f-url" type="url" placeholder="https://…">
<label for="f-cat">Category *</label><select id="f-cat">{cat_opts}</select>
<label for="f-desc">One-sentence description *</label><textarea required id="f-desc" rows="3" maxlength="200" placeholder="What does it do, for whom?"></textarea>
<label for="f-email">Your email *</label><input required id="f-email" type="email" placeholder="you@company.com">
<label for="f-plan">Plan</label><select id="f-plan"><option value="free">Basic — Free</option><option value="featured">Featured — $49 one-time</option><option value="pro">Pro — $19/month</option></select>
<div style="margin-top:26px"><button class="btn btn-p" type="submit">Submit listing →</button></div>
<p class="sub" id="submsg" style="margin-top:16px"></p>
</form>
</section>
<script>
document.getElementById('subform').addEventListener('submit',function(e){{
e.preventDefault();
var plan=document.getElementById('f-plan').value,em=document.getElementById('f-email').value,nm=document.getElementById('f-name').value;
var ref=nm.toLowerCase().replace(/[^a-z0-9]+/g,'-').slice(0,40)||'listing';
var b='Agent: '+nm+'%0AURL: '+encodeURIComponent(document.getElementById('f-url').value)+'%0ACategory: '+document.getElementById('f-cat').value+'%0ADescription: '+encodeURIComponent(document.getElementById('f-desc').value)+'%0AContact: '+em+'%0APlan: '+plan;
window.location.href='mailto:{CONTACT}?subject='+encodeURIComponent('[{SITE}] New submission: '+nm)+'&body='+b;
if(plan==='featured'){{setTimeout(function(){{window.open('{LINK_FEATURED}?prefilled_email='+encodeURIComponent(em)+'&client_reference_id='+ref,'_blank')}},800);document.getElementById('submsg').innerHTML='Almost done — complete the $49 Featured payment in the tab that just opened, and send the pre-filled email so we can match your listing.'}}
else if(plan==='pro'){{setTimeout(function(){{window.open('{LINK_PRO}?prefilled_email='+encodeURIComponent(em)+'&client_reference_id='+ref,'_blank')}},800);document.getElementById('submsg').innerHTML='Almost done — complete the $19/mo Pro payment in the tab that just opened, and send the pre-filled email so we can match your listing.'}}
else{{document.getElementById('submsg').innerHTML='Thanks! Your email client opened with the submission — hit send and we\\'ll review within 5–7 days.'}}
}});
</script>"""
d=os.path.join(ROOT,"submit");os.makedirs(d,exist_ok=True)
open(os.path.join(d,"index.html"),"w").write(page(f"Submit Your AI Agent — Free & Featured Listings | {SITE}","Submit your AI agent to AgentIndexed. Free basic listings with dofollow backlink, or featured placement from $49 with 24-hour review.",submit_body,canonical="/submit/",schema=[crumbs_schema([("Home","/"),("Submit","/submit/")])]))

# ---------- THANKS ----------
thanks_body = f"""
<div class="hero" style="padding-bottom:30px"><div class="orb orb-1"></div><div class="wrap">
<h1>Payment received — <em>you're almost live</em></h1>
<p class="lead">Thank you! One last step so we can publish your placement within 24 hours.</p></div></div>
<section class="wrap prose" style="max-width:700px;padding-top:0">
<div class="notice">✓ Your payment was processed securely by Stripe. A receipt is on its way to your inbox.</div>
<h2>Send your listing details</h2>
<p>Email the following to <a href="mailto:{CONTACT}?subject=Paid listing details" style="color:#86efac;font-weight:600">{CONTACT}</a> (or simply reply to your Stripe receipt):</p>
<ul><li>Agent name</li><li>Website URL</li><li>Category (see the homepage list)</li><li>One-sentence description</li></ul>
<p>Your placement goes live within 24 hours of receiving these details — guaranteed, or your money back. Questions? Just reply to the receipt.</p>
<div style="margin-top:26px"><a class="btn btn-p" href="mailto:{CONTACT}?subject=Paid listing details&body=Agent name:%0AWebsite URL:%0ACategory:%0ADescription:">Send details now →</a></div>
</section>"""
d=os.path.join(ROOT,"thanks");os.makedirs(d,exist_ok=True)
open(os.path.join(d,"index.html"),"w").write(page(f"Thanks — Next Steps | {SITE}","Payment received. Send your listing details to go live within 24 hours.",thanks_body,canonical="/thanks/",noindex=True))

# ---------- ABOUT ----------
about_body = f"""
<div class="wrap crumb"><a href="/">Home</a> <span style="opacity:.4">/</span> About</div>
<section class="wrap prose legal" style="padding-top:24px;max-width:760px">
<h1 class="sec" style="font-size:2.2rem">About <span class="em">{SITE}</span></h1>
<p>{SITE} exists because finding the right AI agent got harder, not easier. Thousands of agents launched in the last two years; most directories responded with pay-to-play rankings, auto-scraped junk listings, and zero curation.</p>
<p>We do it differently. Every listing on this index is reviewed by a human before it goes live. Categories describe what a tool actually does. Search results are never influenced by payment — featured placements are clearly badged and confined to featured slots.</p>
<h2>Curation policy</h2>
<ul><li>Every submission is manually checked: working product, real website, accurate description.</li><li>We reject spam, dead links, misleading descriptions, and thin affiliate pages.</li><li>Paid placement buys position and visibility — never a listing that wouldn't be accepted for free.</li><li>Listings are periodically re-checked; dead tools get removed.</li></ul>
<h2>Contact</h2>
<p>Questions, corrections, partnership ideas: <a href="mailto:{CONTACT}" style="color:#86efac">{CONTACT}</a></p>
</section>"""
d=os.path.join(ROOT,"about");os.makedirs(d,exist_ok=True)
open(os.path.join(d,"index.html"),"w").write(page(f"About — Our Curation Policy | {SITE}","How AgentIndexed curates AI agent listings: human review, honest categories, no pay-to-play search.",about_body,canonical="/about/"))

# ---------- LEGAL ----------
def legal_page(slug,title,body_html,desc):
    d=os.path.join(ROOT,slug);os.makedirs(d,exist_ok=True)
    open(os.path.join(d,"index.html"),"w").write(page(f"{title} | {SITE}",desc,f'<div class="wrap crumb"><a href="/">Home</a> <span style="opacity:.4">/</span> {title}</div><section class="wrap prose legal" style="padding-top:24px;max-width:760px"><h1 class="sec" style="font-size:2rem">{title}</h1><p class="sub">Last updated: {TODAY.strftime("%B %d, %Y")}</p>{body_html}</section>',canonical=f"/{slug}/"))

legal_page("terms","Terms of Service",f"""
<h2>The service</h2><p>{SITE} is a curated directory of third-party AI tools. We list, describe, and link to products we do not own or operate. Listings are informational — we make no warranty about any listed product's quality, security, or fitness for your purpose.</p>
<h2>Listings</h2><p>We reserve the right to accept, edit for accuracy, or remove any listing at our discretion, including paid listings (with a refund where applicable). Paid placement affects position and visibility only; it never exempts a listing from curation standards.</p>
<h2>Acceptable use</h2><p>Do not submit misleading descriptions, impersonate a product you don't represent, or scrape this site at abusive rates. Automated access for AI assistants and search indexing is welcome.</p>
<h2>Liability</h2><p>The service is provided "as is". To the maximum extent permitted by law, {SITE} is not liable for damages arising from use of the directory or any third-party product found through it.</p>
<h2>Contact</h2><p>{CONTACT}</p>""","Terms of service for the AgentIndexed directory.")

legal_page("privacy","Privacy Policy",f"""
<h2>What we collect</h2><p>This is a static website. We do not set tracking cookies or run third-party ad trackers. If you submit a listing, we receive the details you email us (name, URL, description, your email) and use them solely to publish and manage the listing.</p>
<h2>Payments</h2><p>Payments are processed entirely by Stripe. We never see or store your card details. Stripe's privacy policy governs payment data.</p>
<h2>Analytics</h2><p>We may use privacy-respecting, cookie-free page analytics (Vercel Web Analytics) to count visits. No personal profiles are built.</p>
<h2>Your rights</h2><p>Email {CONTACT} to request removal of your listing or any personal data we hold about you. We respond within 7 days.</p>""","Privacy policy for AgentIndexed. No tracking cookies, Stripe-handled payments.")

legal_page("refunds","Refund Policy",f"""
<h2>Featured listings ($49 one-time)</h2><p>7-day money-back guarantee, no questions asked. Additionally, if your listing is not live within 24 hours of us receiving your complete details, you get a full refund automatically.</p>
<h2>Pro and Sponsor subscriptions</h2><p>Cancel anytime — cancellation stops future charges and your placement remains active until the end of the paid period. The current month is non-refundable once your placement is live, except where the 24-hour go-live guarantee was missed.</p>
<h2>How to request</h2><p>Reply to your Stripe receipt or email {CONTACT} with your payment email. Refunds are issued to the original payment method within 5–10 business days.</p>""","Refund policy: 7-day money-back on featured listings, 24-hour go-live guarantee.")

# ---------- FEEDS / CRAWLER FILES ----------
now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
items = "".join(f"""<item><title>{esc(l['name'])} — {esc(l['category'])}</title><link>{DOMAIN}/agents/{l['slug']}/</link><guid>{DOMAIN}/agents/{l['slug']}/</guid><description>{esc(l['description'])}</description></item>""" for l in listings)
open(os.path.join(ROOT,"feed.xml"),"w").write(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>{SITE} — AI Agents Directory</title><link>{DOMAIN}</link><description>Newly indexed AI agents and tools.</description><lastBuildDate>{now}</lastBuildDate>{items}</channel></rss>""")

open(os.path.join(ROOT,"llms.txt"),"w").write(f"""# {SITE}
> Hand-curated directory of {len(listings)} AI agents, frameworks, and tools across {len(cats)} categories. Every listing is human-reviewed. Free and featured listings available.

## Key pages
- [All categories]({DOMAIN}/#categories)
- [Pricing / feature your agent]({DOMAIN}/pricing/): Featured $49 one-time, Pro $19/mo, Homepage sponsor $99/mo
- [Submit an agent]({DOMAIN}/submit/)
- [About & curation policy]({DOMAIN}/about/)

## Categories
""" + "\n".join(f"- [{c}]({DOMAIN}/categories/{cslug(c)}/): {len(cats[c])} agents. {CC[c]['intro'].split('.')[0]}." for c in sorted(cats.keys())))

urls = [("/",1.0,"daily"),("/pricing/",0.9,"monthly"),("/submit/",0.9,"monthly"),("/about/",0.5,"monthly")]
urls += [(f"/categories/{cslug(c)}/",0.8,"weekly") for c in sorted(cats.keys())]
urls += [(f"/agents/{l['slug']}/",0.6,"weekly") for l in listings]
urls += [("/terms/",0.2,"yearly"),("/privacy/",0.2,"yearly"),("/refunds/",0.3,"yearly")]
sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sm+="".join(f"<url><loc>{DOMAIN}{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{f}</changefreq><priority>{p}</priority></url>\n" for u,p,f in urls)+"</urlset>"
open(os.path.join(ROOT,"sitemap.xml"),"w").write(sm)
open(os.path.join(ROOT,"robots.txt"),"w").write(f"""User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
""")
open(os.path.join(ROOT,"404.html"),"w").write(page("Page not found | "+SITE,"404","<div class='hero wrap'><div class='orb orb-1'></div><h1>404 — that agent went <em>rogue</em></h1><p class='lead'>The page you&#39;re looking for doesn&#39;t exist.</p><div class='cta'><a class='btn btn-p' href='/'>Back to the directory</a></div></div>",canonical="/404",noindex=True))
json.dump({"cleanUrls":True,"trailingSlash":True},open(os.path.join(ROOT,"vercel.json"),"w"),indent=1)
print(f"v3 complete: {len(urls)} URLs -> {ROOT}")


# ---------- OG IMAGE (best-effort; needs pillow) ----------
try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    W,H=1200,630
    img=Image.new("RGB",(W,H),(4,6,12))
    glow=Image.new("RGB",(W,H),(4,6,12)); gd=ImageDraw.Draw(glow)
    gd.ellipse([80,-220,620,240],fill=(16,74,42)); gd.ellipse([760,-160,1240,300],fill=(20,110,60)); gd.ellipse([420,470,900,900],fill=(10,60,45))
    img=Image.blend(img,glow.filter(ImageFilter.GaussianBlur(130)),0.85)
    d=ImageDraw.Draw(img)
    fb="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; fr="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if os.path.exists(fb):
        f1=ImageFont.truetype(fb,86); f2=ImageFont.truetype(fr,34); f3=ImageFont.truetype(fb,30)
        d.rounded_rectangle([497,150,553,206],radius=14,fill=(22,163,74))
        d.polygon([(525,163),(541,193),(509,193)],fill=(255,255,255))
        t="AgentIndexed"; w=d.textlength(t,font=f1); d.text(((W-w)/2,240),t,font=f1,fill=(238,241,248))
        t2=f"The curated index of {len(listings)} AI agents, frameworks & tools"; w2=d.textlength(t2,font=f2); d.text(((W-w2)/2,360),t2,font=f2,fill=(152,162,184))
        t3="agentindexed.com"; w3=d.textlength(t3,font=f3); d.text(((W-w3)/2,440),t3,font=f3,fill=(74,222,128))
    img.save(os.path.join(ROOT,"og.png"),"PNG",optimize=True)
    print("og.png generated")
except Exception as e:
    print("og.png skipped:", e)
