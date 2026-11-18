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
LIVE = DOMAIN
CONTACT = "casbattle19@gmail.com"
LINK_FEATURED = "https://buy.stripe.com/3cI28r4Wm0Z4bnS0T79oc0a"
LINK_PRO = "https://buy.stripe.com/14A00j88yazEajOatH9oc0b"
LINK_SPONSOR = "https://buy.stripe.com/3cI5kD60qazE2Rm8lz9oc0c"
# Lead capture endpoint (api/lead.js → private Vercel Blob store). Every submit and every paid-plan
# click is saved here before the visitor goes to Stripe. Owner view: /api/leads?key=LEADS_ADMIN_KEY.
# Set LEADS_URL="" to fall back to the old mailto-only behaviour.
LEADS_URL = os.environ.get("LEADS_URL", "/api/lead").strip()
TODAY = date.today()
LEGAL_UPDATED = date(2026, 11, 11)

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

MARK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 19 12 5l8 14"/><path d="M8 13h8"/></svg>'
FONTS = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap"

def page(title, desc, body, canonical="", schema=None, noindex=False, og_type="website", crumbs=None):
    robots = '<meta name="robots" content="noindex,nofollow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">'
    if crumbs and not noindex:
        schema = list(schema or []) + [crumbs_schema(crumbs)]
    sc = "".join(jld(s) for s in (schema or []))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}
<link rel="canonical" href="{DOMAIN}{canonical}">
<meta name="theme-color" content="#07080b">
<meta name="color-scheme" content="dark">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{DOMAIN}{canonical}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:locale" content="en_US">
<meta property="og:image" content="{DOMAIN}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{SITE}: the curated directory of AI agents">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{DOMAIN}/og.png">
<script>document.documentElement.classList.add('js')</script>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="/style.css">
<link rel="stylesheet" href="{FONTS}" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="{FONTS}"></noscript>
<link rel="alternate" type="application/rss+xml" title="{SITE}: new AI agents" href="{DOMAIN}/feed.xml">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/og.png">
{sc}{HEAD_EXTRA}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="sponsor-bar"><b>Sponsor slot open.</b> Put your AI product in front of every visitor.<a href="/pricing/#sponsor">Become the sponsor &rarr;</a></div>
<header><div class="wrap nav">
<a class="logo" href="/" aria-label="{SITE} home"><span class="mark">{MARK_SVG}</span>Agent<span>Indexed</span></a>
<nav class="nav-links" aria-label="Main">
<a href="/categories/">Categories</a><a href="/best/">Best of</a><a href="/compare/">Compare</a><a href="/pricing/">Pricing</a>
<a class="btn btn-p btn-sm" href="/submit/">Submit agent</a>
</nav>
</div></header>
<main id="main">
{body}
</main>
<footer><div class="wrap">
<div class="foot">
<div style="max-width:320px"><div class="brand"><span class="logo"><span class="mark">{MARK_SVG}</span></span>{SITE}</div>The curated index of AI agents. Every listing is reviewed by a person, categories describe what a tool does, and search is never pay-to-play.</div>
<div class="cols">
<div><h4>Directory</h4><ul><li><a href="/categories/">All categories</a></li><li><a href="/best/">Best-of lists</a></li><li><a href="/compare/">Comparisons</a></li><li><a href="/alternatives/">Alternatives</a></li><li><a href="/feed.xml">RSS feed</a></li></ul></div>
<div><h4>For builders</h4><ul><li><a href="/submit/">Submit an agent</a></li><li><a href="/pricing/">Get featured</a></li><li><a href="/pricing/#sponsor">Sponsorship</a></li><li><a href="/methodology/">How we review</a></li></ul></div>
<div><h4>Company</h4><ul><li><a href="/about/">About</a></li><li><a href="/terms/">Terms</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="/refunds/">Refund policy</a></li><li><a href="mailto:{CONTACT}">Contact</a></li></ul></div>
</div>
</div>
<div class="foot-bottom"><span>&copy; {TODAY.year} {SITE}. Listings last reviewed {TODAY.strftime('%B %Y')}.</span><span><a href="/llms.txt">llms.txt</a> &middot; <a href="/sitemap.xml">Sitemap</a></span></div>
</div></footer>
<script src="/search.js" defer></script>
</body></html>"""

def avatar(l, cls="card-logo", sz=64):
    ini = esc(l["name"][:1].upper())
    return f"""<div class="{cls}" aria-hidden="true"><img src="{logo(l,sz)}" alt="" loading="lazy" decoding="async" width="24" height="24" onerror="this.parentNode.textContent='{ini}'"></div>"""

def card(l, note=""):
    b = '<span class="badge">Featured</span>' if l["featured"] else ""
    fc = " is-featured" if l["featured"] else ""
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in l["tags"][:3])
    extra = f'<span class="tag" style="color:var(--accent-2);border-color:rgba(52,211,153,.3)">{esc(note)}</span>' if note else ""
    return f"""<a class="card{fc}" href="/agents/{l['slug']}/">{b}
<div class="card-top">{avatar(l)}
<div><h3>{esc(l['name'])}</h3><span class="cat">{esc(l['category'])}</span></div></div>
<p>{esc(l['description'])}</p><div class="tags">{extra}{tags}<span class="go">View &rarr;</span></div></a>"""

def trim(s, n=155):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n-1].rsplit(" ", 1)[0].rstrip(",;:.") + "…"

def links_html(items):  # [(label, href, meta)]
    return '<div class="links">' + "".join(f'<a href="{h}">{esc(t)}<span>{esc(m)}</span></a>' for t, h, m in items) + "</div>"

def app_schema(l):
    dev = l["category"] in ("Coding Agents","Frameworks & SDKs","Infrastructure & Tooling","Safety & Observability","Memory & Context")
    return {"@type":"SoftwareApplication","name":l["name"],"url":l["url"],"description":l["description"],
            "applicationCategory":"DeveloperApplication" if dev else "BusinessApplication","applicationSubCategory":l["category"],
            "keywords":", ".join(l["tags"]),"sameAs":l["url"]}

def write(path, html_):
    d = os.path.join(ROOT, *[p for p in path.strip("/").split("/") if p]); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(html_)

os.makedirs(ROOT, exist_ok=True)
open(os.path.join(ROOT,"style.css"),"w").write(CSS)
open(os.path.join(ROOT,"search.js"),"w").write(JS)
open(os.path.join(ROOT,"favicon.svg"),"w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#f2f3f5"/><path d="M8 24 16 9l8 15M11.5 18h9" fill="none" stroke="#07080b" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
idx = [{"n":l["name"],"s":l["slug"],"c":l["category"],"d":l["description"],"h":dom(l["url"]),"t":" ".join(l["tags"])} for l in listings]
json.dump(idx, open(os.path.join(ROOT,"search-index.json"),"w"), separators=(",",":"))
featured = [l for l in listings if l["featured"]]
cat_names = sorted(cats.keys())
by_slug = {l["slug"]: l for l in listings}

def faq_html(qs): return '<div class="faq">'+ "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q,a in qs) +"</div>"
def faq_schema(qs): return {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qs]}
def crumbs_schema(items): return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":DOMAIN+u} for i,(n,u) in enumerate(items)]}
def crumb_html(items):
    parts = [f'<a href="{u}">{esc(n)}</a>' for n,u in items[:-1]] + [esc(items[-1][0])]
    return '<nav class="wrap crumb" aria-label="Breadcrumb">' + ' <span aria-hidden="true">/</span> '.join(parts) + '</nav>'
def itemlist(name, ls):
    return {"@context":"https://schema.org","@type":"ItemList","name":name,"numberOfItems":len(ls),
            "itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{DOMAIN}/agents/{x['slug']}/","name":x["name"]} for i,x in enumerate(ls)]}
REVIEWED = f'<p class="meta-line">Reviewed by the {SITE} editorial team &middot; Updated {TODAY.strftime("%B %d, %Y")} &middot; <a href="/methodology/">How we review</a></p>'
def rank(x): return (not x["featured"], "overview" not in x, x["name"].lower())

# ---------- programmatic data: comparisons, alternatives, best-of ----------
CMP_PER_CAT = 6
pairs = []
for c in cat_names:
    top = sorted(cats[c], key=rank)[:CMP_PER_CAT]
    for i in range(len(top)):
        for j in range(i+1, len(top)):
            a, b = sorted([top[i], top[j]], key=lambda x: x["slug"])
            pairs.append((a, b))
def pslug(a, b): return f"{a['slug']}-vs-{b['slug']}"
cmp_of = {}
for a, b in pairs:
    cmp_of.setdefault(a["slug"], []).append((b, pslug(a,b))); cmp_of.setdefault(b["slug"], []).append((a, pslug(a,b)))

def alternatives(l, n=8):
    out = []
    for x in listings:
        if x["slug"] == l["slug"]: continue
        shared = [t for t in x["tags"] if t in l["tags"]]
        score = (4 if x["category"] == l["category"] else 0) + len(shared)
        if x["category"] != l["category"] and len(shared) < 2: continue
        if score: out.append((score, not x["featured"], x["name"].lower(), x, shared))
    out.sort(key=lambda t: t[:3])
    return [(t[3], t[4]) for t in out[:n]]

BEST = {
"Python":("best-python-ai-agents","Best Python AI Agents & Frameworks","Python is still the default language of agent engineering. These are the reviewed agents, frameworks and tools in the index that are Python-first or ship a first-class Python SDK."),
"Multi-Agent":("best-multi-agent-frameworks","Best Multi-Agent Frameworks & Platforms","Multi-agent systems split work across specialised agents that plan, delegate and check each other. These tools are built for orchestrating teams of agents rather than a single assistant."),
"Cloud":("best-cloud-ai-agents","Best Cloud-Hosted AI Agents","Cloud-hosted agents run on the vendor's infrastructure, so there is nothing to deploy. Good for teams that want results fast and are comfortable sending data to a managed service."),
"IDE":("best-ai-coding-agents-for-ide","Best AI Coding Agents for Your IDE","Agents that live inside the editor: inline edits, multi-file changes and chat with your codebase without leaving the IDE."),
"TypeScript":("best-typescript-ai-agents","Best TypeScript AI Agents & SDKs","For teams building agents in the JavaScript and TypeScript ecosystem, from coding tools to SDKs that run on Node and the edge."),
"OpenAI":("best-openai-agent-tools","Best Agent Tools in the OpenAI Ecosystem","Agents, SDKs and platforms built by OpenAI or designed around OpenAI models."),
"GitHub":("best-ai-agents-for-github","Best AI Agents for GitHub Workflows","Agents that work where code review happens: issues, pull requests and CI on GitHub."),
"CLI":("best-cli-ai-agents","Best Command-Line (CLI) AI Agents","Terminal-first agents for developers who live in the shell: scriptable, fast and easy to wire into existing tooling."),
"RAG":("best-rag-tools-for-ai-agents","Best RAG Tools for AI Agents","Retrieval-augmented generation grounds agents in your own data. These tools handle indexing, retrieval and context assembly."),
"MCP":("best-mcp-tools","Best MCP-Compatible AI Agent Tools","Tools that speak the Model Context Protocol, the open standard for connecting agents to data sources and tools."),
}
best_lists = []
for tag, (bslug, btitle, bintro) in BEST.items():
    ls = sorted([x for x in listings if tag in x["tags"]], key=rank)
    if len(ls) >= 4: best_lists.append((bslug, btitle, bintro, tag, ls))

# ---------- HOME ----------
HOME_FAQ = [
("What is AgentIndexed?", f"AgentIndexed is a hand-curated directory of {len(listings)} AI agents, frameworks and tools organized into {len(cat_names)} categories, from coding agents to voice platforms. Every listing is reviewed by a person before it goes live."),
("How do I submit my AI agent?", "Use the submit page. Basic listings are free and reviewed within 5–7 days. Featured listings ($49 one-time) are reviewed within 24 hours and placed at the top of their category and on the homepage."),
("What does a Featured listing include?", "Twelve months at the top of your category, placement in the homepage featured section, a Featured badge, a dofollow backlink to your site, and priority 24-hour review."),
("Do listings include a dofollow backlink?", "Yes. Every listing, free or paid, links to your site with a standard dofollow link that search engines and AI assistants can follow."),
("How are agents ranked?", "Categories list featured placements first, then all agents alphabetically. Search results are never pay-to-play: they match on name, description, tags and category only."),
]
strip_domains = ["anthropic.com","openai.com","github.com","google.com","microsoft.com","aws.amazon.com","huggingface.co","langchain.com"]
strip = "".join(f'<img src="https://www.google.com/s2/favicons?domain={d}&sz=64" alt="{d}" loading="lazy" decoding="async" width="22" height="22">' for d in strip_domains)
cat_cards = "".join(f'<a class="cat-card" href="/categories/{cslug(c)}/"><div class="cat-ico">{ICONS.get(c,"")}</div><div><b>{esc(c)}</b><span>{len(cats[c])} agents</span><small>{esc(", ".join(x["name"] for x in sorted(cats[c], key=rank)[:3]))}</small></div></a>' for c in cat_names)
chips = '<span>Popular:</span>' + "".join(f'<a href="{h}">{esc(t)}</a>' for t,h in [("Coding agents","/categories/coding-agents/"),("Multi-agent frameworks","/best/best-multi-agent-frameworks/"),("Browser automation","/categories/browser-computer-use/"),("Voice agents","/categories/voice-agents/"),("MCP tools","/best/best-mcp-tools/")])
pop_pairs = [p for p in pairs if p[0]["featured"] or p[1]["featured"]][:6] + [p for p in pairs if not (p[0]["featured"] or p[1]["featured"])][:6]
pop_cmp = links_html([(f"{a['name']} vs {b['name']}", f"/compare/{pslug(a,b)}/", a["category"]) for a,b in pop_pairs[:12]])
best_links = links_html([(t, f"/best/{s}/", f"{len(ls)} tools") for s,t,_,_,ls in best_lists])
latest = list(reversed(listings[-6:]))
TIERS = f"""<div class="tiers">
<div class="tier"><h3>Basic</h3><div class="amt">$0</div><p>Reviewed listing in your category with a dofollow backlink.</p><a class="btn btn-o btn-sm" href="/submit/">Submit free</a></div>
<div class="tier hot"><h3>Featured</h3><div class="amt">$49 <small>one-time</small></div><p>Top of your category and the homepage for 12 months. Live within 24 hours.</p><a class="btn btn-a btn-sm" href="/submit/?plan=featured">Get Featured</a></div>
<div class="tier"><h3>Pro</h3><div class="amt">$19 <small>/month</small></div><p>Permanent top placement, edits any time, launch re-promotion.</p><a class="btn btn-o btn-sm" href="/submit/?plan=pro">Go Pro</a></div>
<div class="tier"><h3>Homepage Sponsor</h3><div class="amt">$99 <small>/month</small></div><p>The one banner on every page. Exclusive, one sponsor at a time.</p><a class="btn btn-o btn-sm" href="/submit/?plan=sponsor">Claim the slot</a></div>
</div>"""
TRUST = """<div class="trust">
<div><b>Reviewed by a person</b><p>Every submission is checked for a working product, a real website and an accurate description.</p></div>
<div><b>No pay-to-play search</b><p>Paid placements are badged and confined to featured slots. Search and rankings never change for money.</p></div>
<div><b>Honest categories</b><p>Tools are filed by what they actually do, so a category page is a real shortlist.</p></div>
<div><b>Re-checked regularly</b><p>Listings are re-verified and dead tools are removed, so you don't waste an afternoon on a 404.</p></div>
</div>"""

home_schema = [
 {"@context":"https://schema.org","@type":"WebSite","@id":DOMAIN+"/#website","name":SITE,"url":DOMAIN+"/","description":f"Curated directory of {len(listings)} AI agents and tools.",
  "publisher":{"@id":DOMAIN+"/#org"},"potentialAction":{"@type":"SearchAction","target":{"@type":"EntryPoint","urlTemplate":DOMAIN+"/?q={search_term_string}"},"query-input":"required name=search_term_string"}},
 {"@context":"https://schema.org","@type":"Organization","@id":DOMAIN+"/#org","name":SITE,"url":DOMAIN+"/","logo":DOMAIN+"/og.png","email":CONTACT},
 {"@context":"https://schema.org","@type":"CollectionPage","name":f"{SITE}: AI agent directory","url":DOMAIN+"/","isPartOf":{"@id":DOMAIN+"/#website"},"mainEntity":itemlist("Featured AI agents", featured)},
 faq_schema(HOME_FAQ),
]
home_body = f"""
<div class="hero">
<div class="wrap">
<span class="pill"><span class="live"></span><b>{len(listings)} agents</b> &middot; reviewed {TODAY.strftime('%B %Y')}</span>
<h1>Find the right <em>AI agent</em><br>for the job.</h1>
<p class="lead">A hand-curated index of the AI agents, frameworks and tools that actually ship, organized into {len(cat_names)} honest categories. No pay-to-play search.</p>
<form class="search" role="search" action="/" onsubmit="return false"><svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="q" name="q" type="search" aria-label="Search agents" placeholder="Search {len(listings)} agents: coding, voice, browser…" autocomplete="off"><kbd>/</kbd><div id="results" role="listbox"></div></form>
<div class="chips">{chips}</div>
<div class="logostrip"><p>Indexing agents and frameworks from</p><div class="logos">{strip}</div></div>
<div class="stats"><div><b>{len(listings)}</b><span>agents listed</span></div><div><b>{len(cat_names)}</b><span>categories</span></div><div><b>{len(pairs)}</b><span>head-to-head comparisons</span></div><div><b>100%</b><span>human-reviewed</span></div></div>
</div></div>
<section class="wrap"><div class="sec-head"><div><span class="eyebrow">Editor's picks</span><h2 class="sec">Featured <span class="em">agents</span></h2><p class="sub">Placements from teams that want to be found. Clearly badged, never mixed into search.</p></div><a class="sec-link" href="/pricing/">Feature your agent &rarr;</a></div><div class="grid">{"".join(card(l) for l in featured)}</div></section>
<section class="wrap" id="categories"><div class="sec-head"><div><span class="eyebrow">Directory</span><h2 class="sec">Browse by <span class="em">category</span></h2><p class="sub">Every agent, filed by what it actually does, not by who paid.</p></div><a class="sec-link" href="/categories/">All categories &rarr;</a></div><div class="cat-grid">{cat_cards}</div></section>
<section class="wrap"><div class="sec-head"><div><span class="eyebrow">Shortlists</span><h2 class="sec">Best-of <span class="em">lists</span></h2><p class="sub">Cross-category shortlists by language, protocol and workflow.</p></div><a class="sec-link" href="/best/">All lists &rarr;</a></div>{best_links}</section>
<section class="wrap"><div class="sec-head"><div><span class="eyebrow">Head to head</span><h2 class="sec">Popular <span class="em">comparisons</span></h2><p class="sub">Side-by-side breakdowns of tools in the same category.</p></div><a class="sec-link" href="/compare/">All {len(pairs)} comparisons &rarr;</a></div>{pop_cmp}</section>
<section class="wrap"><div class="sec-head"><div><span class="eyebrow">Fresh</span><h2 class="sec">Latest <span class="em">additions</span></h2></div><a class="sec-link" href="/submit/">Add yours &rarr;</a></div><div class="grid">{"".join(card(l) for l in latest)}</div></section>
<section class="wrap"><div class="sec-head"><div><span class="eyebrow">Why trust this index</span><h2 class="sec">Curated, not <span class="em">scraped</span></h2></div><a class="sec-link" href="/methodology/">Our review process &rarr;</a></div>{TRUST}</section>
<section class="wrap"><div class="sec-head"><div><span class="eyebrow">For builders</span><h2 class="sec">Get your agent in front of <span class="em">buyers</span></h2><p class="sub">Every listing gets its own page, a dofollow backlink and a spot in the comparisons and shortlists that AI assistants read.</p></div><a class="sec-link" href="/pricing/">Compare plans &rarr;</a></div>{TIERS}
<div class="upsell"><div class="upsell-in"><h3>Founding Member spots: free Featured placement for the first 20</h3><p>Free listings are always open. For launch, the first 20 agents get Featured placement at no cost in exchange for a short testimonial. Normally $49.</p><a class="btn btn-gold" href="/pricing/">Claim a founding spot &rarr;</a></div></div></section>
<section class="wrap"><div class="sec-head"><div><span class="eyebrow">FAQ</span><h2 class="sec">Frequently asked <span class="em">questions</span></h2></div></div>{faq_html(HOME_FAQ)}</section>
"""
open(os.path.join(ROOT,"index.html"),"w").write(page(
 f"AI Agents Directory: {len(listings)}+ Curated Agents, Frameworks & Tools (2026) | {SITE}",
 f"Compare {len(listings)} hand-reviewed AI agents across coding, voice, browser automation, support and more. Side-by-side comparisons, alternatives and best-of lists.",
 home_body, canonical="/", schema=home_schema))

# ---------- CATEGORY HUB ----------
write("/categories/", page(f"All AI Agent Categories ({len(cat_names)}) | {SITE}",
  f"Browse {len(listings)} curated AI agents across {len(cat_names)} categories: coding, frameworks, browser automation, voice, support, research and more.",
  crumb_html([("Home","/"),("Categories","/categories/")]) + f"""<section class="wrap" style="padding-top:20px"><div class="sec-head"><div><h1 class="sec">All <span class="em">categories</span></h1><p class="sub">{len(listings)} reviewed AI agents and tools, filed by what they do.</p></div></div><div class="cat-grid">{cat_cards}</div>
<div class="sec-head" style="margin-top:48px"><h2 class="sec">Best-of lists</h2></div>{best_links}</section>""",
  canonical="/categories/", crumbs=[("Home","/"),("Categories","/categories/")],
  schema=[{"@context":"https://schema.org","@type":"CollectionPage","name":"AI agent categories","url":DOMAIN+"/categories/"}]))

# ---------- CATEGORY PAGES ----------
for c in cat_names:
    ls = sorted(cats[c], key=lambda x:(not x["featured"],x["name"].lower()))
    cc = CC[c]; cs = cslug(c)
    cat_faq = [
      (f"What are the best {c.lower()} in 2026?", f"AgentIndexed currently lists {len(ls)} {c.lower()}, including "+", ".join(x["name"] for x in ls[:4])+" and more. Featured placements appear first, then all tools alphabetically."),
      (f"How do I choose between {c.lower()}?", " ".join(cc["choose"])+"."),
      ("How do I add my tool to this list?", "Submit it free on the submit page (reviewed in 5–7 days), or go Featured for $49 to be reviewed within 24 hours and placed at the top of this category."),
    ]
    cat_pairs = [(a,b) for a,b in pairs if a["category"] == c]
    rel_best = [(t, f"/best/{s}/", f"{len(bl)} tools") for s,t,_,_,bl in best_lists if any(x["category"]==c for x in bl)][:6]
    schema = [{"@context":"https://schema.org","@type":"CollectionPage","name":f"Best {c} in 2026","url":f"{DOMAIN}/categories/{cs}/","about":c,"dateModified":str(TODAY),"mainEntity":itemlist(f"Best {c} 2026", ls)}, faq_schema(cat_faq)]
    body = crumb_html([("Home","/"),("Categories","/categories/"),(c,f"/categories/{cs}/")]) + f"""
<section class="wrap" style="padding-top:20px">
<div class="sec-head"><div><h1 class="sec">{ICONS.get(c,"")}Best {esc(c)} <span class="em">in {TODAY.year}</span></h1>
<p class="sub" style="max-width:720px">{esc(cc['intro'])}</p>{REVIEWED}</div>
<a class="btn btn-o btn-sm" href="/submit/?plan=featured">Get the top spot</a></div>
<div class="grid">{"".join(card(l) for l in ls)}</div>
<div class="prose" style="margin-top:44px"><h2>How to choose {esc(c.lower())}</h2><ol>{"".join(f"<li>{esc(x)}</li>" for x in cc["choose"])}</ol>
<h2>Common use cases</h2><ul>{"".join(f"<li>{esc(x)}</li>" for x in cc["uses"])}</ul></div>
{('<div class="sec-head" style="margin-top:44px"><h2 class="sec">Compare '+esc(c)+'</h2></div>'+links_html([(f"{a['name']} vs {b['name']}", f"/compare/{pslug(a,b)}/", "compare") for a,b in cat_pairs])) if cat_pairs else ""}
{('<div class="sec-head" style="margin-top:44px"><h2 class="sec">Related shortlists</h2></div>'+links_html(rel_best)) if rel_best else ""}
<div class="sec-head" style="margin-top:44px"><h2 class="sec">FAQ</h2></div>{faq_html(cat_faq)}
<div class="upsell" style="margin-top:40px"><div class="upsell-in"><h3>Want the #1 spot in {esc(c)}?</h3><p>Featured agents appear first in this category and on the homepage. One-time $49, live within 24 hours.</p><a class="btn btn-a" href="/submit/?plan=featured">Get featured &rarr;</a></div></div>
</section>"""
    write(f"/categories/{cs}/", page(
      f"Best {c} in {TODAY.year}: {len(ls)} Tools Compared | {SITE}",
      trim(f"The best {c.lower()} in {TODAY.year}, hand-reviewed: " + ", ".join(x['name'] for x in ls[:4]) + f" and {max(len(ls)-4,0)} more. How to choose, use cases and head-to-head comparisons."),
      body, canonical=f"/categories/{cs}/", schema=schema, crumbs=[("Home","/"),("Categories","/categories/"),(c,f"/categories/{cs}/")]))

# ---------- AGENT DETAIL PAGES ----------
for l in listings:
    c = l["category"]; cc = CC[c]; cs = cslug(c)
    use_cases = l.get("use_cases", cc["uses"])
    overview = l.get("overview", f"{l['name']} sits in the {c.lower()} category of the agent stack. {cc['intro']}")
    use_case_intro = f"{l['name']} is used for: " if "use_cases" in l else "Tools in this category are commonly used for: "
    alts = alternatives(l)
    alt_names = ", ".join(x["name"] for x,_ in alts[:5])
    cmps = cmp_of.get(l["slug"], [])
    fb = ' <span class="badge" style="position:static;vertical-align:middle;margin-left:8px">Featured</span>' if l["featured"] else ""
    agent_faq = [
      (f"What is {l['name']}?", f"{l['name']} is a tool in the {c.lower()} category. {l['description']}"),
      (f"What is {l['name']} used for?", use_case_intro + "; ".join(use_cases).lower()+"."),
      (f"What are the best alternatives to {l['name']}?", f"Popular alternatives include {alt_names}. See the full list of {l['name']} alternatives or compare them on the {c} category page."),
    ]
    crumbs = [("Home","/"),(c,f"/categories/{cs}/"),(l["name"],f"/agents/{l['slug']}/")]
    schema = [{"@context":"https://schema.org","@type":"WebPage","name":f"{l['name']} review and alternatives","url":f"{DOMAIN}/agents/{l['slug']}/","dateModified":str(TODAY),"isPartOf":{"@id":DOMAIN+"/#website"},"mainEntity":dict(app_schema(l), **{"@context":"https://schema.org"})}, faq_schema(agent_faq)]
    cmp_links = links_html([(f"{l['name']} vs {o['name']}", f"/compare/{ps}/", "compare") for o,ps in cmps[:6]]) if cmps else ""
    body = crumb_html(crumbs) + f"""
<div class="wrap detail"><div class="detail-grid"><div>
<div class="detail-head">{avatar(l,"detail-logo",128)}
<div><span class="cat">{esc(c)}</span><h1>{esc(l['name'])}{fb}</h1></div></div>
<p class="desc">{esc(l['description'])}</p>
<div class="actions"><a class="btn btn-p" href="{esc(l['url'])}" target="_blank" rel="noopener">Visit {esc(l['name'])} &nearr;</a><a class="btn btn-o" href="/alternatives/{l['slug']}/">{esc(l['name'])} alternatives</a></div>
{REVIEWED}
<div class="prose"><h2>What {esc(l['name'])} is for</h2><p>{esc(overview)}</p>
<h2>Typical use cases</h2><ul>{"".join(f"<li>{esc(x)}</li>" for x in use_cases)}</ul>
<h2>How to evaluate {esc(l['name'])}</h2><ol>{"".join(f"<li>{esc(x)}</li>" for x in cc["choose"])}</ol></div>
{('<div class="sec-head" style="margin-top:40px"><h2 class="sec">Compare '+esc(l['name'])+'</h2></div>'+cmp_links) if cmp_links else ""}
<div class="claim"><b>Is this your agent?</b><p>Claim this listing to update the description and move it to the top of {esc(c)}. <a href="/submit/?plan=featured">Upgrade to Featured</a> or email <a href="mailto:{CONTACT}?subject=Claim listing: {esc(l['name'])}">{CONTACT}</a>.</p></div>
<div class="sec-head" style="margin-top:44px"><h2 class="sec">FAQ</h2></div>{faq_html(agent_faq)}
</div>
<aside class="aside" aria-label="At a glance"><h2>At a glance</h2><dl>
<dt>Category</dt><dd><a href="/categories/{cs}/">{esc(c)}</a></dd>
<dt>Website</dt><dd>{esc(dom(l['url']))}</dd>
<dt>Tags</dt><dd>{esc(", ".join(l['tags']) or "—")}</dd>
<dt>Listing</dt><dd>{"Featured" if l['featured'] else "Standard"}</dd>
<dt>Reviewed</dt><dd>{TODAY.strftime('%b %Y')}</dd></dl><hr>
<a class="btn btn-p" href="{esc(l['url'])}" target="_blank" rel="noopener">Visit website &nearr;</a>
<p class="mini">Listed free. Owners can <a href="/submit/?plan=featured" style="color:var(--accent-2)">feature this tool</a> for $49.</p></aside>
</div>
<div class="sec-head" style="margin-top:56px"><h2 class="sec">Alternatives to {esc(l['name'])}</h2><a class="sec-link" href="/alternatives/{l['slug']}/">See all &rarr;</a></div>
<div class="grid">{"".join(card(x) for x,_ in alts[:6])}</div>
</div>"""
    write(f"/agents/{l['slug']}/", page(
      f"{l['name']}: Features, Use Cases & Alternatives ({TODAY.year}) | {SITE}",
      trim(f"{l['name']}: {l['description']} Compare {l['name']} alternatives in {c.lower()}."),
      body, canonical=f"/agents/{l['slug']}/", schema=schema, crumbs=crumbs, og_type="article"))

# ---------- ALTERNATIVES ----------
for l in listings:
    alts = alternatives(l, 10); c = l["category"]
    if not alts: continue
    crumbs = [("Home","/"),("Alternatives","/alternatives/"),(f"{l['name']} alternatives",f"/alternatives/{l['slug']}/")]
    rows = "".join(f"<tr><th scope=\"row\"><a href=\"/agents/{x['slug']}/\">{esc(x['name'])}</a></th><td>{esc(x['category'])}</td><td>{esc(', '.join(sh) or '—')}</td><td>{esc(trim(x['description'],110))}</td></tr>" for x,sh in alts)
    faq = [(f"What is the best alternative to {l['name']}?", f"It depends on why you are switching. In the {c.lower()} category the closest options in our index are {', '.join(x['name'] for x,_ in alts[:3])}. Each is reviewed and compared on its own page."),
           (f"Why look for {l['name']} alternatives?", "Teams usually switch for pricing, deployment model (cloud vs self-hosted), language or framework fit, or integrations. Use the shared-tags column above to find tools that match your stack."),
           (f"How are these alternatives chosen?", "Alternatives are tools in the same category, plus tools in other categories that share at least two tags. Featured listings are badged and never reorder the list beyond ties.")]
    body = crumb_html(crumbs) + f"""<section class="wrap" style="padding-top:20px">
<div class="sec-head"><div><h1 class="sec">{len(alts)} best <span class="em">{esc(l['name'])}</span> alternatives</h1><p class="sub">{esc(l['name'])} is {esc(l['description'][0].lower()+l['description'][1:])} If it isn't the right fit, these reviewed tools cover similar ground.</p>{REVIEWED}</div><a class="btn btn-o btn-sm" href="/agents/{l['slug']}/">About {esc(l['name'])}</a></div>
<div class="grid">{"".join(card(x, ("Shares "+", ".join(sh[:2])) if sh else "") for x,sh in alts)}</div>
<h2 class="sec" style="margin-top:48px;font-size:1.4rem">At a glance</h2>
<div class="table-wrap"><table class="cmp"><thead><tr><th>Tool</th><th>Category</th><th>Shared tags</th><th>Summary</th></tr></thead><tbody>{rows}</tbody></table></div>
{('<div class="sec-head" style="margin-top:44px"><h2 class="sec">Head-to-head</h2></div>'+links_html([(f"{l['name']} vs {o['name']}", f"/compare/{ps}/", "compare") for o,ps in cmp_of.get(l['slug'],[])])) if cmp_of.get(l['slug']) else ""}
<div class="sec-head" style="margin-top:44px"><h2 class="sec">FAQ</h2></div>{faq_html(faq)}
<div class="upsell" style="margin-top:40px"><div class="upsell-in"><h3>Building a {esc(l['name'])} alternative?</h3><p>Get listed free, or go Featured to appear first in {esc(c)} and on the homepage.</p><a class="btn btn-a" href="/submit/?plan=featured">Get featured &rarr;</a></div></div>
</section>"""
    write(f"/alternatives/{l['slug']}/", page(
      f"{len(alts)} Best {l['name']} Alternatives in {TODAY.year} (Compared) | {SITE}",
      trim(f"Looking for {l['name']} alternatives? Compare {', '.join(x['name'] for x,_ in alts[:3])} and more reviewed {c.lower()} side by side."),
      body, canonical=f"/alternatives/{l['slug']}/", crumbs=crumbs, schema=[itemlist(f"{l['name']} alternatives", [x for x,_ in alts]), faq_schema(faq)]))

# ---------- COMPARISONS ----------
for a, b in pairs:
    c = a["category"]; cc = CC[c]; ps = pslug(a,b)
    shared = [t for t in a["tags"] if t in b["tags"]]
    ua = [t for t in a["tags"] if t not in b["tags"]]; ub = [t for t in b["tags"] if t not in a["tags"]]
    def uc(x): return "; ".join(x.get("use_cases", [])) or "General " + c.lower() + " work"
    rows = [("Category", f'<a href="/categories/{cslug(c)}/">{esc(c)}</a>', f'<a href="/categories/{cslug(c)}/">{esc(c)}</a>'),
            ("What it is", esc(a["description"]), esc(b["description"])),
            ("Tags", esc(", ".join(a["tags"]) or "—"), esc(", ".join(b["tags"]) or "—")),
            ("Use cases", esc(uc(a)), esc(uc(b))),
            ("Website", esc(dom(a["url"])), esc(dom(b["url"]))),
            ("Listing", "Featured" if a["featured"] else "Standard", "Featured" if b["featured"] else "Standard")]
    table = "".join(f'<tr><th scope="row">{k}</th><td>{x}</td><td>{y}</td></tr>' for k,x,y in rows)
    others = [(f"{x['name']} vs {o['name']}", f"/compare/{pslug(x,o)}/", c) for x,o in pairs if x["category"]==c and pslug(x,o)!=ps and (a in (x,o) or b in (x,o))][:8]
    diff = []
    if ua: diff.append(f"{a['name']} is tagged {', '.join(ua)}, which {b['name']} is not.")
    if ub: diff.append(f"{b['name']} is tagged {', '.join(ub)}, which {a['name']} is not.")
    if shared: diff.append(f"Both are tagged {', '.join(shared)}, so they overlap on stack fit.")
    diff.append(f"Both sit in {c.lower()}; the deciding factor is usually how each one fits the workflow you already run.")
    faq = [(f"What is the difference between {a['name']} and {b['name']}?", f"{a['name']}: {a['description']} {b['name']}: {b['description']}"),
           (f"Is {a['name']} or {b['name']} better?", f"Neither is better in every case. "+" ".join(cc["choose"])+". Shortlist both and test them on a real task from your own work."),
           (f"What are alternatives to {a['name']} and {b['name']}?", "Other reviewed "+c.lower()+" include "+", ".join(x["name"] for x in sorted(cats[c], key=rank) if x not in (a,b))[:300]+".")]
    crumbs = [("Home","/"),("Compare","/compare/"),(f"{a['name']} vs {b['name']}",f"/compare/{ps}/")]
    body = crumb_html(crumbs) + f"""<section class="wrap" style="padding-top:20px">
<h1 class="sec">{esc(a['name'])} <span class="em">vs</span> {esc(b['name'])}</h1>
<p class="sub">Two {esc(c.lower())} side by side: what each one is, where they differ, and how to pick. Built from {SITE}'s reviewed listings.</p>{REVIEWED}
<div class="vs-head">
<a class="vs-side" href="/agents/{a['slug']}/">{avatar(a)}<div><h2>{esc(a['name'])}</h2><span>{esc(dom(a['url']))}</span></div></a>
<div class="vs-x" aria-hidden="true">vs</div>
<a class="vs-side" href="/agents/{b['slug']}/">{avatar(b)}<div><h2>{esc(b['name'])}</h2><span>{esc(dom(b['url']))}</span></div></a></div>
<div class="table-wrap"><table class="cmp"><thead><tr><th></th><th>{esc(a['name'])}</th><th>{esc(b['name'])}</th></tr></thead><tbody>{table}</tbody></table></div>
<div class="prose"><h2>Key differences</h2><ul>{"".join(f"<li>{esc(x)}</li>" for x in diff)}</ul>
<h2>Which should you choose?</h2>
<p><strong>Pick {esc(a['name'])}</strong> if this matches what you need: {esc(a['description'])}</p>
<p><strong>Pick {esc(b['name'])}</strong> if this matches what you need: {esc(b['description'])}</p>
<h3>Questions to settle before you commit</h3><ol>{"".join(f"<li>{esc(x)}</li>" for x in cc["choose"])}</ol></div>
<div class="actions" style="display:flex;gap:10px;flex-wrap:wrap;margin-top:26px"><a class="btn btn-o" href="/alternatives/{a['slug']}/">{esc(a['name'])} alternatives</a><a class="btn btn-o" href="/alternatives/{b['slug']}/">{esc(b['name'])} alternatives</a><a class="btn btn-o" href="/categories/{cslug(c)}/">All {esc(c)}</a></div>
{('<div class="sec-head" style="margin-top:44px"><h2 class="sec">Related comparisons</h2></div>'+links_html(others)) if others else ""}
<div class="sec-head" style="margin-top:44px"><h2 class="sec">FAQ</h2></div>{faq_html(faq)}
<div class="upsell" style="margin-top:40px"><div class="upsell-in"><h3>Building in {esc(c)}?</h3><p>Featured tools appear first in the category and on the homepage, and get added to comparisons like this one.</p><a class="btn btn-a" href="/submit/?plan=featured">Get featured &rarr;</a></div></div>
</section>"""
    write(f"/compare/{ps}/", page(
      f"{a['name']} vs {b['name']} ({TODAY.year}): Side-by-Side Comparison | {SITE}",
      trim(f"{a['name']} vs {b['name']}: compare features, tags and use cases of these two {c.lower()}, and see which one fits your workflow."),
      body, canonical=f"/compare/{ps}/", crumbs=crumbs, og_type="article",
      schema=[{"@context":"https://schema.org","@type":"WebPage","name":f"{a['name']} vs {b['name']}","url":f"{DOMAIN}/compare/{ps}/","dateModified":str(TODAY),"about":[app_schema(a),app_schema(b)]}, faq_schema(faq)]))

# ---------- BEST-OF LISTS ----------
for bslug, btitle, bintro, tag, ls in best_lists:
    crumbs = [("Home","/"),("Best of","/best/"),(btitle,f"/best/{bslug}/")]
    cats_in = sorted({x["category"] for x in ls})
    faq = [(f"What is the {btitle.lower().replace('best ','best ',1)}?", f"There is no single winner. Top picks in our index include {', '.join(x['name'] for x in ls[:4])}. Start from the category that matches your job: {', '.join(cats_in[:4])}."),
           ("How is this list ordered?", "Featured placements first (clearly badged), then tools with full editorial overviews, then alphabetically. Inclusion is never paid: every tool here passed the same human review.")]
    body = crumb_html(crumbs) + f"""<section class="wrap" style="padding-top:20px">
<div class="sec-head"><div><h1 class="sec">{esc(btitle)} <span class="em">({TODAY.year})</span></h1><p class="sub" style="max-width:720px">{esc(bintro)}</p>{REVIEWED}</div></div>
<div class="grid">{"".join(card(x) for x in ls)}</div>
<div class="prose" style="margin-top:44px"><h2>The shortlist at a glance</h2><ol>{"".join(f'<li><span><a href="/agents/{x["slug"]}/">{esc(x["name"])}</a> ({esc(x["category"])}): {esc(x["description"])}</span></li>' for x in ls[:10])}</ol>
<h2>Browse by category</h2><ul>{"".join(f'<li><a href="/categories/{cslug(k)}/">{esc(k)}</a></li>' for k in cats_in)}</ul></div>
<div class="sec-head" style="margin-top:44px"><h2 class="sec">FAQ</h2></div>{faq_html(faq)}
<div class="upsell" style="margin-top:40px"><div class="upsell-in"><h3>Belong on this list?</h3><p>Submit your tool free. Featured tools are reviewed within 24 hours and shown first.</p><a class="btn btn-a" href="/submit/?plan=featured">Get featured &rarr;</a></div></div>
</section>"""
    write(f"/best/{bslug}/", page(f"{btitle} ({TODAY.year}): {len(ls)} Reviewed Picks | {SITE}", trim(f"{bintro} {len(ls)} reviewed picks including {', '.join(x['name'] for x in ls[:3])}."),
      body, canonical=f"/best/{bslug}/", crumbs=crumbs, og_type="article", schema=[itemlist(btitle, ls), faq_schema(faq)]))

# ---------- HUBS ----------
best_hub = [(t, f"/best/{s}/", f"{len(ls)} tools") for s,t,_,_,ls in best_lists] + [(f"Best {c}", f"/categories/{cslug(c)}/", f"{len(cats[c])} tools") for c in cat_names]
write("/best/", page(f"Best AI Agents & Tools: {len(best_hub)} Curated Lists ({TODAY.year}) | {SITE}", "Curated best-of lists of AI agents by language, protocol, workflow and category. Every tool is human-reviewed.",
  crumb_html([("Home","/"),("Best of","/best/")]) + f'<section class="wrap" style="padding-top:20px"><div class="sec-head"><div><h1 class="sec">Best-of <span class="em">lists</span></h1><p class="sub">Shortlists of reviewed AI agents and tools, by stack and by job.</p></div></div>{links_html(best_hub)}</section>',
  canonical="/best/", crumbs=[("Home","/"),("Best of","/best/")]))
cmp_hub = ""
for c in cat_names:
    cp = [(f"{a['name']} vs {b['name']}", f"/compare/{pslug(a,b)}/", "compare") for a,b in pairs if a["category"]==c]
    if cp: cmp_hub += f'<div class="sec-head" style="margin-top:36px"><h2 class="sec" style="font-size:1.3rem">{esc(c)}</h2></div>' + links_html(cp)
write("/compare/", page(f"AI Agent Comparisons: {len(pairs)} Head-to-Head Matchups | {SITE}", f"Side-by-side comparisons of {len(pairs)} pairs of AI agents, frameworks and tools in the same category.",
  crumb_html([("Home","/"),("Compare","/compare/")]) + f'<section class="wrap" style="padding-top:20px"><h1 class="sec">AI agent <span class="em">comparisons</span></h1><p class="sub">{len(pairs)} head-to-head breakdowns of tools in the same category.</p>{cmp_hub}</section>',
  canonical="/compare/", crumbs=[("Home","/"),("Compare","/compare/")]))
alt_hub = ""
for c in cat_names:
    alt_hub += f'<div class="sec-head" style="margin-top:36px"><h2 class="sec" style="font-size:1.3rem">{esc(c)}</h2></div>' + links_html([(f"{x['name']} alternatives", f"/alternatives/{x['slug']}/", "") for x in sorted(cats[c], key=lambda x:x["name"].lower())])
write("/alternatives/", page(f"Alternatives to {len(listings)} AI Agents & Tools | {SITE}", "Find alternatives to any AI agent, framework or tool in the index, ranked by category and stack overlap.",
  crumb_html([("Home","/"),("Alternatives","/alternatives/")]) + f'<section class="wrap" style="padding-top:20px"><h1 class="sec">Find an <span class="em">alternative</span></h1><p class="sub">Pick the tool you are replacing. We rank alternatives by category and shared stack.</p>{alt_hub}</section>',
  canonical="/alternatives/", crumbs=[("Home","/"),("Alternatives","/alternatives/")]))

# ---------- METHODOLOGY ----------
write("/methodology/", page(f"How We Review AI Agents: Methodology | {SITE}", "How AgentIndexed reviews, categorizes, ranks and re-checks AI agent listings, and how paid placements are kept separate from search.",
  crumb_html([("Home","/"),("Methodology","/methodology/")]) + f"""<section class="wrap prose" style="padding-top:20px">
<h1 class="sec">How we <span class="em">review</span></h1>{REVIEWED}
<p>{SITE} is a curated index, not a scraped one. This page explains exactly what happens between a submission and a published listing, and what money can and cannot buy.</p>
<h2>1. Submission</h2><p>Anyone can submit a tool through the <a href="/submit/">submit form</a>. Free and paid submissions go through the same checks.</p>
<h2>2. Human review</h2><ol><li>The product works and is publicly available or has a real waitlist.</li><li>The website is the vendor's own, not an affiliate or reseller page.</li><li>The description is accurate. We rewrite marketing claims we cannot verify.</li><li>The tool fits a category by what it does.</li></ol>
<h2>3. Categorization and tags</h2><p>Each tool gets one category and a small set of tags (language, protocol, deployment). Tags drive the best-of lists, alternatives and comparisons, so they are kept factual.</p>
<h2>4. Ordering</h2><p>Category pages and lists show Featured placements first, clearly badged, then tools with full editorial overviews, then alphabetical order. Search never takes payment into account.</p>
<h2>5. Re-checks and removals</h2><p>Listings are re-checked periodically. Tools that shut down, change category or stop matching their description are updated or removed. Spot something out of date? Email <a href="mailto:{CONTACT}">{CONTACT}</a>.</p>
<h2>What paid plans buy</h2><p>Featured, Pro and Sponsor plans buy position and visibility. They never buy a listing that would not be accepted for free, and they never change search results. See <a href="/pricing/">pricing</a>.</p>
</section>""", canonical="/methodology/", crumbs=[("Home","/"),("Methodology","/methodology/")]))
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
<a class="btn btn-p" href="/submit/?plan=featured" style="justify-content:center">Get Featured — $49</a></div>
<div class="price"><h3>Pro Listing</h3><div class="amt">$19 <small>/month</small></div>
<ul><li>Everything in Featured</li><li>Permanent top placement</li><li>Listing updates any time</li><li>Launch &amp; update re-promotion</li><li>Cancel anytime</li></ul>
<a class="btn btn-o" href="/submit/?plan=pro" style="justify-content:center">Go Pro — $19/mo</a></div>
<div class="price"><h3>Homepage Sponsor</h3><div class="amt">$99 <small>/month</small></div>
<ul><li>Exclusive banner on every page</li><li>Your logo, tagline &amp; link</li><li>Only one sponsor at a time</li><li>Cancel anytime</li></ul>
<a class="btn btn-gold" href="/submit/?plan=sponsor" style="justify-content:center">Claim sponsor slot</a></div>
</div>
<div class="sec-head" style="margin-top:44px"><h2 class="sec">Pricing FAQ</h2></div>{faq_html(pricing_faq)}
</section>"""
d=os.path.join(ROOT,"pricing");os.makedirs(d,exist_ok=True)
open(os.path.join(d,"index.html"),"w").write(page(f"Pricing — Feature Your AI Agent | {SITE}","List your AI agent free, or get featured placement with a dofollow backlink from $49. 24-hour review, 7-day money-back guarantee.",pricing_body,canonical="/pricing/",schema=[faq_schema(pricing_faq),crumbs_schema([("Home","/"),("Pricing","/pricing/")])]))

# ---------- SUBMIT ----------
# Every submission (free or paid) is saved to LEADS_URL (/api/lead) *before* anything else happens, so the email is
# captured even if the visitor abandons Stripe checkout. Paid plans then go to Stripe in the same tab
# (no pop-up to block) with the email pre-filled.
SUBMIT_JS = """
(function(){
var CFG=__CFG__;
var f=document.getElementById('subform'),sel=document.getElementById('f-plan'),btn=document.getElementById('subbtn'),msg=document.getElementById('submsg');
var p=new URLSearchParams(location.search).get('plan');
if(p&&CFG.links.hasOwnProperty(p)||p==='free'){sel.value=p;}
function label(){btn.textContent=sel.value==='free'?'Submit listing \\u2192':'Continue to secure payment \\u2192';}
sel.addEventListener('change',label);label();
function v(id){return document.getElementById(id).value.trim();}
f.addEventListener('submit',function(e){
e.preventDefault();
var plan=sel.value,em=v('f-email'),nm=v('f-name');
var ref=(nm.toLowerCase().replace(/[^a-z0-9]+/g,'-').slice(0,40))||'listing';
var data={plan:plan,name:nm,url:v('f-url'),category:v('f-cat'),description:v('f-desc'),email:em,page:location.pathname+location.search,ref:ref,company_website:v('f-hp')};
btn.disabled=true;btn.textContent='Saving\\u2026';
function next(saved){
if(CFG.links[plan]){location.href=CFG.links[plan]+'?prefilled_email='+encodeURIComponent(em)+'&client_reference_id='+encodeURIComponent(ref);return;}
if(saved){msg.innerHTML='Thanks! Your submission is in. We review free listings within 5\\u20137 days and will email you when it\\'s live.';btn.textContent='Submitted \\u2713';return;}
var b='Agent: '+nm+'%0AURL: '+encodeURIComponent(data.url)+'%0ACategory: '+encodeURIComponent(data.category)+'%0ADescription: '+encodeURIComponent(data.description)+'%0AContact: '+encodeURIComponent(em)+'%0APlan: '+plan;
location.href='mailto:'+CFG.contact+'?subject='+encodeURIComponent('['+CFG.site+'] New submission: '+nm)+'&body='+b;
msg.innerHTML='Your email app opened with the submission \\u2014 hit send and we\\'ll review within 5\\u20137 days.';btn.disabled=false;label();
}
if(!CFG.leads){next(false);return;}
var done=false;function finish(ok){if(!done){done=true;next(ok);}}
try{
fetch(CFG.leads,{method:'POST',keepalive:true,headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})
.then(function(r){finish(r.ok);},function(){finish(false);});
setTimeout(function(){finish(false);},5000);
}catch(err){finish(false);}
});
})();
""".replace("__CFG__", json.dumps({"leads": LEADS_URL, "contact": CONTACT, "site": SITE,
    "links": {"featured": LINK_FEATURED, "pro": LINK_PRO, "sponsor": LINK_SPONSOR}}))
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
<div aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden"><label for="f-hp">Company website</label><input id="f-hp" tabindex="-1" autocomplete="off"></div>
<label for="f-plan">Plan</label><select id="f-plan"><option value="free">Basic — Free</option><option value="featured">Featured — $49 one-time</option><option value="pro">Pro — $19/month</option><option value="sponsor">Homepage Sponsor — $99/month</option></select>
<div style="margin-top:26px"><button class="btn btn-p" id="subbtn" type="submit">Submit listing →</button></div>
<p class="sub" id="submsg" style="margin-top:16px"></p>
</form>
</section>
<script>{SUBMIT_JS}</script>"""
d=os.path.join(ROOT,"submit");os.makedirs(d,exist_ok=True)
open(os.path.join(d,"index.html"),"w").write(page(f"Submit Your AI Agent — Free & Featured Listings | {SITE}","Submit your AI agent to AgentIndexed. Free basic listings with dofollow backlink, or featured placement from $49 with 24-hour review.",submit_body,canonical="/submit/",schema=[crumbs_schema([("Home","/"),("Submit","/submit/")])]))

# ---------- THANKS ----------
thanks_body = f"""
<div class="hero" style="padding-bottom:30px"><div class="orb orb-1"></div><div class="wrap">
<h1>Next steps for <em>your listing</em></h1>
<p class="lead">Completed checkout? Send your listing details so we can match your payment and review your placement.</p></div></div>
<section class="wrap prose" style="max-width:700px;padding-top:0">
<div class="notice">Check your Stripe confirmation or receipt to confirm checkout completed. Visiting this page alone does not confirm payment. We verify successful payment in Stripe before publishing.</div>
<h2>Send your listing details</h2>
<p>Email the following to <a href="mailto:{CONTACT}?subject=Paid listing details" style="color:#86efac;font-weight:600">{CONTACT}</a>:</p>
<ul><li>Agent name</li><li>Website URL</li><li>Category (see the homepage list)</li><li>One-sentence description</li><li>Email used at checkout and your Stripe receipt reference</li></ul>
<p>Do not send card details, passwords, or verification codes.</p>
<p>Publication is manual: we match your details to the successful Stripe payment, review the listing, and publish it. Once payment is confirmed and complete eligible listing details are received, your paid placement goes live within 24 hours under our published money-back guarantee. We will email your listing link when it is live.</p>
<div style="margin-top:26px"><a class="btn btn-p" href="mailto:{CONTACT}?subject=Paid listing details&body=Agent name:%0AWebsite URL:%0ACategory:%0ADescription:%0ACheckout email:%0AStripe receipt reference:">Send details now →</a></div>
</section>"""
d=os.path.join(ROOT,"thanks");os.makedirs(d,exist_ok=True)
open(os.path.join(d,"index.html"),"w").write(page(f"Thanks — Next Steps | {SITE}","Complete your listing details for manual payment verification, review, and publication.",thanks_body,canonical="/thanks/",noindex=True))

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
    open(os.path.join(d,"index.html"),"w").write(page(f"{title} | {SITE}",desc,f'<div class="wrap crumb"><a href="/">Home</a> <span style="opacity:.4">/</span> {title}</div><section class="wrap prose legal" style="padding-top:24px;max-width:760px"><h1 class="sec" style="font-size:2rem">{title}</h1><p class="sub">Last updated: {LEGAL_UPDATED.strftime("%B %d, %Y")}</p>{body_html}</section>',canonical=f"/{slug}/"))

legal_page("terms","Terms of Service",f"""
<h2>The service</h2><p>{SITE} is a curated directory of third-party AI tools. We list, describe, and link to products we do not own or operate. Listings are informational — we make no warranty about any listed product's quality, security, or fitness for your purpose.</p>
<h2>Listings</h2><p>We reserve the right to accept, edit for accuracy, or remove any listing at our discretion, including paid listings (with a refund where applicable). Paid placement affects position and visibility only; it never exempts a listing from curation standards.</p>
<h2>Acceptable use</h2><p>Do not submit misleading descriptions, impersonate a product you don't represent, or scrape this site at abusive rates. Automated access for AI assistants and search indexing is welcome.</p>
<h2>Liability</h2><p>The service is provided "as is". To the maximum extent permitted by law, {SITE} is not liable for damages arising from use of the directory or any third-party product found through it.</p>
<h2>Contact</h2><p>{CONTACT}</p>""","Terms of service for the AgentIndexed directory.")

legal_page("privacy","Privacy Policy",f"""
<h2>What we collect</h2><p>This is a static website. We do not set tracking cookies or run third-party ad trackers. If you submit a listing or start a paid checkout, we store the details you enter in our form (agent name, URL, category, description, chosen plan, your email) in private storage and use them solely to publish and manage the listing and to follow up about your submission or an unfinished checkout.</p>
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
- [Best-of lists]({DOMAIN}/best/)
- [Alternatives]({DOMAIN}/alternatives/)
- [Comparisons]({DOMAIN}/compare/)
- [Methodology]({DOMAIN}/methodology/)

## Categories
""" + "\n".join(f"- [{c}]({DOMAIN}/categories/{cslug(c)}/): {len(cats[c])} agents. {CC[c]['intro'].split('.')[0]}." for c in sorted(cats.keys())))

urls = [("/",1.0,"daily"),("/pricing/",0.9,"monthly"),("/submit/",0.9,"monthly"),("/about/",0.5,"monthly")]
urls += [(f"/categories/{cslug(c)}/",0.8,"weekly") for c in sorted(cats.keys())]
urls += [(f"/agents/{l['slug']}/",0.6,"weekly") for l in listings]
have = {u for u,_,_ in urls}
for sec,pr in (('compare',0.5),('alternatives',0.6),('best',0.7)):
    base = os.path.join(ROOT, sec)
    if os.path.isdir(base):
        urls += [(f'/{sec}/',pr+0.1,'weekly')] + [(f'/{sec}/{d}/',pr,'monthly') for d in sorted(os.listdir(base)) if os.path.isdir(os.path.join(base,d))]
urls += [('/methodology/',0.4,'monthly')]
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
