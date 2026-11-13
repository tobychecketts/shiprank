#!/usr/bin/env python3
"""Generate the ShipRank site from tools.json, data/compare.json and data/guides.json.

Outputs: / (homepage), /tools/<slug>/, /best/<cat>/, /compare/, /guides/, /weekly/ (+ feed.xml), /featured/,
/stats/, sitemap.xml, robots.txt. Shared look lives in assets/style.css (+ self-hosted fonts in assets/fonts/).
Daily routine: edit tools.json -> python3 build.py -> commit + push -> python3 indexnow.py
"""
import json, re, os, html, shutil, hashlib, datetime
from urllib.parse import urlparse
from email.utils import format_datetime
BASE = "https://shiprank.co.uk/"  # hosting address only; never shown as text
d = json.load(open("tools.json"))
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
e = html.escape
YEAR = d["lastVerified"][:4]
LV = d["lastVerified"]
def nice(ds):
    try: return datetime.date.fromisoformat(ds).strftime("%-d %b %Y")
    except Exception: return ds
def longdate(ds): return datetime.date.fromisoformat(ds).strftime("%A %-d %B %Y")
CSS_VER = hashlib.md5(open("assets/style.css", "rb").read()).hexdigest()[:8]
CF_BEACON = """<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{"token": "4c16a00aeea24d7db1e4c34321b9796a"}'></script>"""  # Cloudflare Web Analytics (cookie-free)
ANALYTICS = """<script>/* Cookie-free anonymous visit counter (Abacus, no cookies, no personal data) */(function(){try{var n="shiprank.tobychecketts",p=location.pathname.split("/").filter(function(x){return x&&x!="index.html"}),s=p.length?p[0].toLowerCase():"home",a="https://abacus.jasoncameron.dev/hit/"+n+"/";["visits","section-"+s.replace(/[^a-z0-9_-]/gi,"")].forEach(function(k){fetch(a+k,{mode:"no-cors",keepalive:true})})}catch(e){}})();</script>"""
ICONS = '<link rel="icon" href="' + BASE + 'favicon.svg" type="image/svg+xml"><link rel="icon" href="' + BASE + 'favicon-32.png" sizes="32x32" type="image/png"><link rel="apple-touch-icon" href="' + BASE + 'apple-touch-icon.png">'
MARK = '<img class="mark" src="' + BASE + 'assets/brand/mark.svg" alt="" width="34" height="34">'
cats = sorted({t["category"] for t in d["tools"]}, key=lambda c: [t["category"] for t in d["tools"]].index(c))
lc = lambda c: c if c.startswith(("AI", "LLM")) else c[0].lower() + c[1:]
NOUN = {"Design-to-code": "design-to-code tools", "Deployment & backend": "deployment & backend tools", "Voice & video for demos": "voice & video demo tools"}
noun = lambda c: NOUN.get(c, lc(c))
urls = [BASE]

def masthead(active):
    items = [("rankings", f"{BASE}#rankings", "Rankings"), ("compare", f"{BASE}compare/", "Compare"), ("guides", f"{BASE}guides/", "Guides"), ("weekly", f"{BASE}weekly/", "This week"), ("featured", f"{BASE}featured/", "Sponsor")]
    nav = "".join(f'<a href="{h}"{" class=on" if k == active else ""}>{l}</a>' for k, h, l in items)
    return (f'<a class="skip" href="#main">Skip to content</a><header class="mast"><div class="wrap"><a class="logo" href="{BASE}" aria-label="ShipRank home">{MARK}ShipRank<b>.</b></a><nav class="nav" aria-label="Main">{nav}</nav></div></header>'
            f'<div class="strap"><div class="wrap"><span>Last updated {longdate(LV)}</span><span class="r">{len(d["tools"])} tools in {len(cats)} categories · nobody pays to rank</span></div></div>')

def footer():
    best = "".join(f'<li><a href="{BASE}best/{slug(c)}/">{e(c)}</a></li>' for c in cats)
    return f"""<footer class="foot"><div class="wrap"><div class="grid"><div><a class="logo" href="{BASE}">{MARK}ShipRank<b>.</b></a><p>A small, independent site ranking the AI tools people use to build things. We read the changelogs and pricing pages every morning so you don't have to, and we keep the rankings honest: sponsors get a label, not a better spot.</p><p class="xfollow">Follow new releases on X: <a href="https://x.com/ShipRankUK" rel="me">@ShipRankUK</a></p></div>
<div><h4>Rankings</h4><ul>{best}</ul></div><div><h4>Elsewhere</h4><ul><li><a href="{BASE}guides/">Guides</a></li><li><a href="{BASE}compare/">Comparisons</a></li><li><a href="{BASE}weekly/">This week</a></li><li><a href="{BASE}weekly/feed.xml">RSS feed</a></li><li><a href="{BASE}featured/">Sponsor a spot</a></li><li><a href="{BASE}sitemap.xml">Sitemap</a></li></ul></div></div>
<p class="small">Disclosure: some links on ShipRank may be affiliate links, and we may earn a commission if you buy through them, at no extra cost to you. Sponsored placements are always labelled. Neither affects our rankings, which are editorial. Privacy: we count visits anonymously with a cookie-free counter and Cloudflare Web Analytics (also cookie-free); no cookies, no tracking across sites, no personal data. © {YEAR} ShipRank.</p></div></footer>"""

def page(path, title, desc, body, head="", active="", ogtype="website"):
    url = BASE + path + ("/" if path else "")
    out = f"""<!doctype html><html lang="en-GB"><head><meta name='impact-site-verification' value='433c0488-f7f6-4a86-9b9a-075a81062f41'><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}"><meta name="theme-color" content="#f7f3ea">{ICONS}
<meta property="og:type" content="{ogtype}"><meta property="og:site_name" content="ShipRank"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}assets/brand/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="ShipRank: a small sailing boat logo beside the ShipRank name"><link rel="alternate" type="application/rss+xml" title="ShipRank Weekly" href="{BASE}weekly/feed.xml"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:site" content="@ShipRankUK">
<link rel="preload" href="{BASE}assets/fonts/fraunces.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="{BASE}assets/style.css?v={CSS_VER}">{ANALYTICS}{head}</head><body>{masthead(active)}
<main id="main" class="wrap page">{body}</main>{footer()}{CF_BEACON}</body></html>"""
    os.makedirs(path or ".", exist_ok=True); open(os.path.join(path, "index.html"), "w").write(out)
    if url not in urls: urls.append(url)

def ldjson(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + '</script>'
def faq_ld(faq): return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
def faq_html(faq): return '<div class="faq">' + "".join(f'<h3>{e(q)}</h3><p>{e(a)}</p>' for q, a in faq) + '</div>'
def kicker(*parts): return '<p class="kicker">' + " / ".join(f'<a href="{h}">{e(l)}</a>' if h else e(l) for l, h in parts) + '</p>'
def visit(t, label=None, cls=""):
    aff = t.get("affiliate")
    a = f'<a{" class=" + chr(34) + cls + chr(34) if cls else ""} href="{t["url"]}" rel="{"sponsored nofollow noopener" if aff else "nofollow noopener"}" target="_blank">{label or "Visit " + e(t["name"])} ↗</a>'
    return a + (' <span class="aff">(affiliate link)</span>' if aff else "")
def cta_label(t):
    n = e(t["name"])
    return f"Try {n} free" if is_free(t) else f"Visit {n}"
def try_btn(t, cls="try"):
    """Clear call-to-action. Free tier -> 'Try X free'. Affiliate links get rel=sponsored and a visible label."""
    aff = t.get("affiliate")
    a = f'<a class="{cls}" href="{t["url"]}" rel="{"sponsored nofollow noopener" if aff else "nofollow noopener"}" target="_blank">{cta_label(t)} →</a>'
    return a + (' <span class="aff tag">Affiliate link</span>' if aff else "")
def internal(n): return n in {t["name"] for t in d["tools"]}
def is_free(t): return str(t.get("freeTier", "")).lower().startswith("yes")
def row(t, n, note=None, big=False):
    name = f'<a class="name" href="{BASE}tools/{slug(t["name"])}/">{e(t["name"])}</a>' if internal(t["name"]) else f'<a class="name" href="{t["url"]}" rel="nofollow">{e(t["name"])}</a>'
    why = note if note is not None else t.get("rankReason", "")
    links = (f'<a href="{BASE}tools/{slug(t["name"])}/">Our notes</a> · ' if internal(t["name"]) else "") + f'<a href="{t["pricingUrl"]}" rel="nofollow">Pricing</a> checked {nice(t["lastChecked"])}'
    pc = (f'<p class="pc"><b>Good:</b> {e("; ".join(t["pros"]))}. <b>Less good:</b> {e("; ".join(t["cons"]))}.</p>' if big and t.get("pros") else "")
    return (f'<li class="row"><span class="n">{n}</span><div>{name}' + 
            f'<p class="for">{e(t["bestFor"])}</p>' + (f'<p class="why">{e(why)}</p>' if why else "") + pc + f'<p class="links">{links}</p><p class="cta">{try_btn(t)}</p></div>'
            f'<div class="cost"><i>Paid from</i><b>{e(t["entryPrice"])}</b><span>Free tier: {e(t["freeTier"])}</span></div></li>')

compare_links = {}
cmp = json.load(open("data/compare.json"))
for a in cmp["articles"]:
    for n in a["tools"]: compare_links.setdefault(n, []).append(a)
alltools = {t["name"]: t for t in d["tools"]}; alltools.update(cmp["extraTools"])
def tlink(n): return f'<a href="{BASE}tools/{slug(n)}/">{e(n)}</a>' if internal(n) else f'<a href="{alltools[n]["url"]}" rel="nofollow">{e(n)}</a>'
G = json.load(open("data/guides.json"))["guides"]
bycat = {c: sorted([x for x in d["tools"] if x["category"] == c], key=lambda x: x["rank"]) for c in cats}

# Releases have no tool field. Map each one to the ranked tool(s) it is actually
# about: official domains, the release name ("Gemini 4 Hydrogen in Cursor"), and
# a few precise phrases in the summary ("available in GitHub Copilot", "plugin
# for Claude Code"). Ignore mentions that are only examples or import sources
# (Hermes v0.23.0 is not v0; Lovable importing from Replit is not a Replit
# release; Microsoft Copilot is not GitHub Copilot).
_ALIAS = {
    "Cursor": ["Cursor"],
    "GitHub Copilot": ["GitHub Copilot"],
    "Windsurf": ["Windsurf"],
    "Lovable": ["Lovable"],
    "Bolt.new": ["Bolt.new"],
    "v0": ["v0"],
    "Replit": ["Replit"],
    "Claude Code": ["Claude Code"],
    "OpenAI Codex": ["OpenAI Codex", "Codex CLI"],
    "Devin": ["Devin"],
    "OpenAI API": ["OpenAI API"],
    "Anthropic API": ["Anthropic API"],
    "Google Gemini API": ["Google Gemini API", "Gemini API"],
    "OpenRouter": ["OpenRouter"],
    "Figma Make": ["Figma Make"],
    "Builder.io": ["Builder.io"],
    "Vercel": ["Vercel"],
    "Supabase": ["Supabase"],
    "Netlify": ["Netlify"],
    "ElevenLabs": ["ElevenLabs", "Eleven Labs"],
    "Descript": ["Descript"],
    "Loom": ["Loom"],
    "LangGraph": ["LangGraph"],
    "CrewAI": ["CrewAI", "Crew AI"],
    "OpenAI Agents SDK": ["OpenAI Agents SDK", "OpenAI Agents API"],
}
_HOST_TOOL = {
    "cursor.com": "Cursor", "lovable.dev": "Lovable", "docs.lovable.dev": "Lovable",
    "v0.app": "v0", "replit.com": "Replit", "docs.replit.com": "Replit",
    "devin.ai": "Devin", "bolt.new": "Bolt.new", "support.bolt.new": "Bolt.new",
    "builder.io": "Builder.io", "vercel.com": "Vercel", "windsurf.com": "Windsurf",
    "code.claude.com": "Claude Code",
}
_INCIDENTAL = re.compile(
    r"(?:import\s+(?:\w+\s+)*from|ZIP export from|use your|unmodified|agents? like|"
    r"built elsewhere|using your existing|login inside)", re.I)
_EXTRA = [
    r"(?:plugin|add-?on|extension)\s+for\s+{a}",
    r"(?:generally\s+)?available\s+in\s+{a}",
    r"(?:now\s+)?(?:the\s+)?(?:default|standard)\b[^.]*?\bin\s+{a}",
    r"now\s+live\s+in\s+{a}",
    r"live\s+in\s+{a}",
]
def _alias_rx(alias):
    if alias == "v0":
        return re.compile(r"(?<![A-Za-z0-9])v0(?![\d.])", re.I)
    return re.compile(r"\b" + re.escape(alias) + r"\b", re.I)
def _starts_with(name, alias):
    if alias == "v0":
        return bool(re.match(r"v0(?![\d.])(\b|:|$)", name, re.I))
    return bool(re.match(re.escape(alias) + r"(\b|:|$)", name, re.I))
def _is_github_copilot_release(r):
    if re.search(r"\bMicrosoft Copilot\b", r["name"]):
        return False
    if re.search(r"\bCopilot\b", r["name"]):
        return True
    return bool(re.search(r"github-copilot|github_copilot", r["url"], re.I))
def tools_for_release(r):
    found, name, url, summary = set(), r["name"], r["url"], r.get("summary", "")
    h = urlparse(url).netloc.lower().removeprefix("www.")
    if h in _HOST_TOOL:
        found.add(_HOST_TOOL[h])
    for tool, aliases in _ALIAS.items():
        if any(_starts_with(name, a) for a in aliases):
            found.add(tool)
        for a in aliases:
            if re.search(r"\bin\s+" + _alias_rx(a).pattern, name, re.I):
                found.add(tool)
    if _starts_with(name, "Bolt"):
        found.add("Bolt.new")
    if re.search(r"\bCodex\b", name):
        found.add("OpenAI Codex")
    if re.search(r"\bOpenAI models\b", name):
        found.add("OpenAI API")
    if re.match(r"Gemini\s+\d", name) and not re.search(r"\bin\b", name):
        found.add("Google Gemini API")
    if _is_github_copilot_release(r):
        found.add("GitHub Copilot")
    blob = name + ". " + summary
    extra = dict(_ALIAS)
    extra["GitHub Copilot"] = ["GitHub Copilot", "Copilot"]
    extra["Bolt.new"] = ["Bolt.new", "Bolt"]
    extra["OpenAI Codex"] = ["OpenAI Codex", "Codex"]
    extra["v0"] = ["v0"]
    for tool, aliases in extra.items():
        for alias in aliases:
            rx = _alias_rx(alias)
            for pat in _EXTRA:
                for m in re.finditer(pat.format(a=rx.pattern), blob, re.I):
                    if _INCIDENTAL.search(blob[max(0, m.start() - 80):m.end() + 80]):
                        continue
                    found.add(tool)
    return found
_cutoff = datetime.date.fromisoformat(LV) - datetime.timedelta(days=30)
releases_by_tool = {t["name"]: [] for t in d["tools"]}
for r in d["releases"]:
    try:
        rd = datetime.date.fromisoformat(r["date"])
    except ValueError:
        continue
    if rd < _cutoff:
        continue
    for name in tools_for_release(r):
        if name in releases_by_tool:
            releases_by_tool[name].append(r)
for _n in releases_by_tool:
    releases_by_tool[_n].sort(key=lambda r: r["date"], reverse=True)

# ---- tool pages ----
for p in ("tools", "best"): shutil.rmtree(p, ignore_errors=True)
for t in d["tools"]:
    s = slug(t["name"]); c = t["category"]; peers = [x for x in bycat[c] if x is not t]
    facts = f'<dl class="facts"><div><dt>Free tier</dt><dd>{e(t["freeTier"])}</dd></div><div><dt>Paid from</dt><dd>{e(t["entryPrice"])}</dd></div>' + (f'<div><dt>Worth knowing</dt><dd>{e(t["pricingNote"])}</dd></div>' if t.get("pricingNote") else "") + f'<div><dt>Checked</dt><dd>{nice(t["lastChecked"])} on the <a href="{t["pricingUrl"]}" rel="nofollow">official pricing page</a></dd></div></dl>'
    cmps = "".join(f'<li><a href="{BASE}compare/{a["slug"]}/">{e(a["title"])}</a></li>' for a in compare_links.get(t["name"], []))
    recents = releases_by_tool[t["name"]]
    if recents:
        rel_html = (f'<div class="sechead"><h2>Recent releases</h2><a href="{BASE}weekly/">This week →</a></div><ul class="log">'
                    + "".join(f'<li><span class="date">{nice(r["date"])}</span><b>{e(r["name"])}</b><p>{e(r["summary"])}</p><small><a href="{r["url"]}" rel="nofollow">Source</a></small></li>' for r in recents)
                    + "</ul>")
    else:
        rel_html = (f'<div class="sechead"><h2>Recent releases</h2><a href="{BASE}weekly/">This week →</a></div>'
                    f'<p class="mute">No new releases in the last 30 days. See the <a href="{BASE}weekly/">weekly roundup</a> for what has shipped across all tools.</p>')
    body = f"""<div class="head">{kicker(("Rankings", f"{BASE}#rankings"), (c, f"{BASE}best/{slug(c)}/"), (t["name"], None))}<h1>{e(t['name'])}</h1><p class="dek">{e(t['bestFor'])}.</p><p class="mute" style="margin-top:12px">No. {t['rank']} of {len(bycat[c])} in <a href="{BASE}best/{slug(c)}/">{e(lc(c))}</a>. Prices checked {nice(t['lastChecked'])}.</p></div>
<div class="cols"><div class="article"><h2>Why it's No. {t['rank']}</h2><p>{e(t['rankReason'])}.</p>
<div class="twocol"><div><h3>What's good</h3><ul>{''.join('<li>'+e(x)+'</li>' for x in t['pros'])}</ul></div><div><h3>What's not</h3><ul>{''.join('<li>'+e(x)+'</li>' for x in t['cons'])}</ul></div></div>
{('<h2>Head-to-heads</h2><ul>'+cmps+'</ul>') if cmps else ''}
{rel_html}
<div class="sechead"><h3>Other {e(noun(c))} we rank</h3><a href="{BASE}best/{slug(c)}/">Full ranking →</a></div><ol class="board">{''.join(row(x, x['rank']) for x in peers)}</ol></div>
<aside class="side"><section><h2>Price</h2>{facts}<p style="margin-top:16px">{try_btn(t, cls="btn solid")}</p>{'<p><small>We may earn a commission if you sign up through this link. It doesn&#39;t affect the ranking.</small></p>' if t.get("affiliate") else ''}</section></aside></div>"""
    page(f"tools/{s}", f"{t['name']} Review & Pricing ({YEAR}) – ShipRank", f"{t['name']}: {t['bestFor']}. Free tier: {t['freeTier']}. Entry price: {t['entryPrice']}. Ranked #{t['rank']} in {c}."[:160], body, active="rankings")

# ---- best-of category pages ----
for c in cats:
    ts = bycat[c]
    body = (f'<div class="head">{kicker(("Rankings", f"{BASE}#rankings"), (c, None))}<h1>The best {e(noun(c))} for vibe coders ({YEAR})</h1><p class="dek">The {len(ts)} we think are worth your time, in order, with what they cost. Prices come from the official pricing pages and were last checked on the dates shown.</p></div>'
            f'<ol class="board big">{"".join(row(x, x["rank"], big=True) for x in ts)}</ol>'
            + ((f'<div class="sechead"><h2>Compare them head to head</h2><a href="{BASE}compare/">All comparisons →</a></div><ul class="plain">' + "".join(f'<li><a href="{BASE}compare/{a["slug"]}/">{e(a["title"])}</a></li>' for a in cmp["articles"] if any(alltools[n].get("category") == c for n in a["tools"])) + '</ul>') if any(any(alltools[n].get("category") == c for n in a["tools"]) for a in cmp["articles"]) else "")
            + f'<p class="note" style="margin-top:24px">Make one of these? You can <a href="{BASE}featured/">sponsor a labelled spot</a> on this page. It won\'t change the order above.</p>'
            '<p class="jump" style="margin-top:24px">Other rankings: ' + " · ".join(f'<a href="{BASE}best/{slug(o)}/">{e(o)}</a>' for o in cats if o != c) + '</p>')
    page(f"best/{slug(c)}", f"Best {c} for Vibe Coders {YEAR} – ShipRank", f"The best {c.lower()} for vibe coders and builders in {YEAR}: " + ", ".join(x["name"] for x in ts) + ". Ranked with verified pricing."[:160], body, active="rankings")

# ---- comparisons ----
shutil.rmtree("compare", ignore_errors=True)
rows = [("Best for","bestFor"),("Category","category"),("Free tier","freeTier"),("Entry price","entryPrice"),("Pros","pros"),("Cons","cons")]
idx = ""
def at(h): return h.replace('href="@/', f'href="{BASE}')
for a in cmp["articles"]:
    ts = [alltools[n] for n in a["tools"]]
    cell = lambda t,k: "<br>".join(map(e,t[k])) if isinstance(t[k],list) else e(str(t[k]))
    table = ('<div class="tbl"><table><thead><tr><th></th>' + "".join(f"<th>{tlink(t['name'])}</th>" for t in ts) + "</tr></thead><tbody>" + "".join(f"<tr><th>{l}</th>" + "".join(f"<td>{cell(t,k)}</td>" for t in ts) + "</tr>" for l,k in rows)
             + "<tr><th>ShipRank rank</th>" + "".join(f"<td>{('<a href=' + chr(34) + BASE + 'best/' + slug(t['category']) + '/' + chr(34) + '>#' + str(t['rank']) + ' in ' + e(t['category']) + '</a>') if t.get('rank') else 'Not ranked'}</td>" for t in ts) + "</tr>"
             + "<tr><th>Try it</th>" + "".join(f"<td>{try_btn(t)}</td>" for t in ts) + "</tr></tbody></table></div>")
    ctas = '<div class="ctas">' + "".join(f'<p>{try_btn(t, cls="btn")}</p>' for t in ts) + '</div>'
    affnote = '<p class="note">Disclosure: ' + ", ".join(e(t["name"]) for t in ts if t.get("affiliate")) + ' links on this page are affiliate links. We may earn a commission if you sign up, at no cost to you. It doesn&#39;t change our ranking or verdict.</p>' if any(t.get("affiliate") for t in ts) else ""
    catl = sorted({t["category"] for t in ts if t.get("rank")})
    related = [x for x in cmp["articles"] if x is not a and set(x["tools"]) & set(a["tools"])]
    gl = [g for g in G if set(g["tools"]) & set(a["tools"])][:4]
    more = ('<h2>Keep reading</h2><ul>' + "".join(f'<li><a href="{BASE}best/{slug(c)}/">The best {e(noun(c))}, ranked</a></li>' for c in catl)
            + "".join(f'<li><a href="{BASE}compare/{x["slug"]}/">{e(x["title"].split(":")[0].split(" (")[0])}</a></li>' for x in related)
            + "".join(f'<li><a href="{BASE}guides/{g["slug"]}/">{e(g["title"])}</a></li>' for g in gl) + '</ul>')
    upd = a.get("updated", cmp.get("checked", LV))
    body = f"""<div class="head">{kicker(("Comparisons", f"{BASE}compare/"), (" vs ".join(a["tools"]), None))}<h1 style="max-width:24ch">{e(a['title'])}</h1><p class="dek">{e(a['desc'])}</p><p class="mute" style="margin-top:12px">Updated {nice(upd)}. Prices from the official pricing pages.</p></div>
<div class="article" style="max-width:none"><div class="verdict" style="max-width:720px"><p class="kicker">The short answer</p><p>{a['verdict']}</p></div>{ctas}{affnote}
<div style="max-width:720px">{at(a.get('body',''))}</div>
<h2>Side by side</h2>{table}
<div style="max-width:720px"><h2>Who should pick what</h2><dl class="who">{''.join(f'<dt>{tlink(n)}</dt><dd>{e(w)}</dd>' for n,w in a['who'].items())}</dl>
<h2>What they cost</h2><ul class="plain">{''.join(f'<li><b>{e(t["name"])}</b>: free tier {e(t["freeTier"])}; paid from {e(t["entryPrice"])}. <small><a href="{t["pricingUrl"]}" rel="nofollow">Pricing page</a>, checked {nice(t["lastChecked"])}.</small></li>' for t in ts)}</ul>
<p><small>Prices in USD as shown on official pages. Anything marked unknown/unverified could not be confirmed.</small></p>
<h2>Questions people ask</h2>{faq_html(a['faq'])}{more}</div></div>"""
    curl = f"{BASE}compare/{a['slug']}/"
    art = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["desc"], "mainEntityOfPage": curl, "url": curl, "image": BASE + "assets/brand/og.png", "dateModified": upd, "author": {"@type": "Organization", "name": "ShipRank", "url": BASE}, "publisher": {"@type": "Organization", "name": "ShipRank", "url": BASE, "sameAs": ["https://x.com/ShipRankUK"], "logo": {"@type": "ImageObject", "url": BASE + "apple-touch-icon.png"}}}
    page(f"compare/{a['slug']}", a.get("metaTitle", a["title"] + " – ShipRank"), a["desc"][:160], body, ldjson(art) + (ldjson(faq_ld(a["faq"])) if a.get("faq") else ""), active="compare", ogtype="article")
    idx += f'<li class="row" style="grid-template-columns:minmax(0,1fr)"><div><a class="name" href="{BASE}compare/{a["slug"]}/">{e(a["title"])}</a><p class="why">{e(a["desc"])}</p></div></li>'
page("compare", f"AI Tool Comparisons for Vibe Coders {YEAR} – ShipRank", "Head-to-head comparisons of AI code editors, app builders, coding agents, backends and hosting for vibe coders.",
     f'<div class="head">{kicker(("Comparisons", None))}<h1>Head-to-heads</h1><p class="dek">When two or three tools do roughly the same job, we put them side by side and tell you which one we\'d pick and why.</p></div><ol class="board">{idx}</ol>', active="compare")

# ---- guides ----
shutil.rmtree("guides", ignore_errors=True)
gidx = ""
for g in G:
    items = '<ol class="board">' + "".join(row(alltools[n], i, note=g.get("notes", {}).get(n, "")) for i, n in enumerate(g["tools"], 1)) + '</ol>'
    rel = [a for a in cmp["articles"] if set(a["tools"]) & set(g["tools"])]
    secs = lambda key: "".join(f'<h2 id="{slug(x["h"])}">{e(x["h"])}</h2>' + x["html"].replace('href="@/', f'href="{BASE}') for x in g.get(key, []))
    picks_t = g.get("picksTitle", "Our picks")
    picks = f'<h2 id="picks">{e(picks_t)}</h2>' if g.get("sections") or g.get("top") else ""
    srcs = ('<h2 id="sources">Sources</h2><ul>' + "".join(f'<li><a href="{u}" rel="nofollow">{e(l)}</a></li>' for l, u in g["sources"]) + "</ul>") if g.get("sources") else ""
    toc = [(x["h"], slug(x["h"])) for x in g.get("top", [])] + ([(picks_t, "picks")] if picks else []) + [(x["h"], slug(x["h"])) for x in g.get("sections", [])] + [("FAQ", "faq")] + ([("Sources", "sources")] if srcs else [])
    upd = f'Updated {nice(g["updated"])}' if g.get("updated") else "Guide"
    relh = ('<h2>Related comparisons</h2><ul>' + "".join(f'<li><a href="{BASE}compare/{a["slug"]}/">{e(a["title"])}</a></li>' for a in rel) + '</ul>') if rel else ""
    body = (f'<div class="article c"><p class="kicker"><a href="{BASE}guides/">Guides</a> / <span class="red">{upd}</span> / prices checked on official pages</p><h1>{e(g["title"])}</h1><p class="dek">{e(g["intro"])}</p>'
            '<p class="toc">In this guide: ' + " · ".join(f'<a href="#{i}">{e(t)}</a>' for t, i in toc) + '</p>'
            + secs("top") + picks + items + secs("sections") + '<h2 id="faq">FAQ</h2>' + faq_html(g["faq"]) + srcs + relh +
            '<hr><p><small>Prices in USD from official pages. Anything marked unverified could not be confirmed.</small></p></div>')
    gurl = f"{BASE}guides/{g['slug']}/"
    art = {"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["desc"], "mainEntityOfPage": gurl, "url": gurl, "image": BASE + "assets/brand/og.png", "author": {"@type": "Organization", "name": "ShipRank", "url": BASE}, "publisher": {"@type": "Organization", "name": "ShipRank", "url": BASE, "sameAs": ["https://x.com/ShipRankUK"], "logo": {"@type": "ImageObject", "url": BASE + "apple-touch-icon.png"}}}
    if g.get("published"): art["datePublished"] = g["published"]
    if g.get("updated"): art["dateModified"] = g["updated"]
    page(f"guides/{g['slug']}", g.get("metaTitle", g["title"] + " – ShipRank"), g["desc"][:160], body, ldjson(art) + (ldjson(faq_ld(g["faq"])) if g["faq"] else ""), active="guides", ogtype="article")
    gidx += f'<li class="row" style="grid-template-columns:minmax(0,1fr) 110px"><div><a class="name" href="{BASE}guides/{g["slug"]}/">{e(g["title"])}</a><p class="why">{e(g["desc"])}</p></div><div class="cost">{nice(g.get("updated",""))}</div></li>'
page("guides", f"AI Tool Guides for Vibe Coders {YEAR} – ShipRank", "Guides to the best free, cheapest and beginner-friendly AI tools for vibe coders and solo builders.",
     f'<div class="head">{kicker(("Guides", None))}<h1>Guides</h1><p class="dek">Longer write-ups for when a ranking isn\'t enough: where to start, what\'s free, what\'s cheap, and how to get from a design to working code.</p></div><ol class="board">{gidx}</ol>', active="guides")

# ---- weekly roundups ----
shutil.rmtree("weekly", ignore_errors=True)
weeks = {}
for r in d["releases"]:
    try: dt = datetime.date.fromisoformat(r["date"])
    except ValueError: continue
    y, w, _ = dt.isocalendar(); weeks.setdefault(f"{y}-w{w:02d}", []).append(r)
def wbody(k, rs):
    by = {}
    for r in sorted(rs, key=lambda r: r["date"], reverse=True): by.setdefault(r["date"], []).append(r)
    return "".join(f'<section class="day"><h2>{datetime.date.fromisoformat(dd).strftime("%a %-d %b")}</h2><ul class="log">' + "".join(f'<li><b>{e(r["name"])}</b><p>{e(r["summary"])}</p><small><a href="{r["url"]}" rel="nofollow">Source</a> · checked {nice(r.get("verified","unknown"))}</small></li>' for r in lst) + '</ul></section>' for dd, lst in by.items())
keys = sorted(weeks, reverse=True)
arch = '<p class="jump" style="margin-top:36px">Earlier weeks: ' + " · ".join(f'<a href="{BASE}weekly/{k}/">week {int(k[-2:])}</a> ({len(weeks[k])})' for k in keys) + "</p>"
for k in keys:
    page(f"weekly/{k}", f"AI builder tool launches – week {int(k[-2:])}, {k[:4]} – ShipRank", f"Verified AI tool launches for vibe coders and builders in ISO week {int(k[-2:])} of {k[:4]}, grouped by date with sources."[:160],
         f'<div class="head">{kicker(("This week", f"{BASE}weekly/"), (f"Week {int(k[-2:])}, {k[:4]}", None))}<h1>What shipped in week {int(k[-2:])}</h1><p class="dek">{len(weeks[k])} releases for people building with AI. We only list something once we\'ve seen it on the company\'s own page.</p></div>' + wbody(k, weeks[k]) + arch, active="weekly")
if keys:
    k = keys[0]
    page("weekly", "This Week in AI Builder Tools – ShipRank Weekly Roundup", f"This week's verified AI tool launches for vibe coders (week {int(k[-2:])}, {k[:4]}), grouped by date with sources.",
         f'<div class="head">{kicker(("This week", None))}<h1>What shipped this week</h1><p class="dek">New releases from the AI tools builders actually use, newest first. Week {int(k[-2:])}, {k[:4]}. We only list something once we\'ve seen it on the company\'s own page.</p><p class="mute" style="margin-top:12px">Follow along in your reader with the <a href="{BASE}weekly/feed.xml">RSS feed</a>. An email version is on the way.</p></div>' + wbody(k, weeks[k]) + arch, active="weekly")

# ---- featured (sponsorship) page ----
MAILTO = "mailto:hello@shiprank.co.uk?subject=" + "Get%20featured%20on%20ShipRank"
opts = [("Featured category slot","£49","per week","A highlighted ‘Featured’ card at the top of one category ranking page (e.g. Best app builders), clearly labelled as sponsored, with your logo, one-line pitch and link."),
        ("Weekly roundup spotlight","£29","per week","A spotlight card at the top of that week’s /weekly/ roundup page and its RSS item, labelled as sponsored."),
        ("Launch listing","£19","per week","Your launch listed on the homepage ‘New releases’ feed and the weekly roundup, labelled as sponsored. Must be a genuine, live launch.")]
fbody = f'<div class="article c" style="max-width:760px"><p class="kicker">Sponsor</p><h1>Sponsor a spot on ShipRank</h1><p class="dek">If you make a tool for people building with AI, you can pay to put it in front of them. Every paid spot is labelled as sponsored, and paying never changes where anything ranks.</p>'
fbody += '<h2>What you can buy</h2><p>These are launch prices for early sponsors, in GBP per week. They\'ll go up as traffic does.</p><div class="prices">'
fbody += "".join(f'<div class="opt"><div><h3>{e(n)}</h3><p>{e(w)}</p><p><a href="{MAILTO}%20-%20{n.replace(" ","%20")}">Enquire about {e(n)} →</a></p></div><div class="amt">{p}<small>{u} (launch pricing)</small></div></div>' for n,p,u,w in opts) + '</div>'
fbody += '<h2>A straight answer on traffic</h2><p>ShipRank is a new site (launched October 2026). We don’t yet have meaningful traffic numbers to share, which is why prices are low. We’ll publish stats here once we have them.</p>'
fbody += f'<h2>Get in touch</h2><p>Email us with your tool, which option you want and the week you\'d like.</p><p><a class="btn solid" href="{MAILTO}">Email ShipRank</a></p></div>'
page("featured", "Get Featured on ShipRank – Sponsor a Slot for Your AI Tool", "Sponsor a clearly labelled slot on ShipRank: featured category, weekly roundup spotlight or launch listing. Introductory launch pricing in GBP.", fbody, active="featured")

# ---- homepage ----
dated = sorted([r for r in d["releases"] if re.match(r"\d{4}-\d{2}-\d{2}$", r["date"])], key=lambda r: r["date"], reverse=True)
beginner = next((g for g in G if g["slug"] == "best-ai-coding-tool-for-beginners"), G[0])
intro = (f'<section class="intro"><h1>We rank AI coding tools by what they’re <em>actually</em> good for.</h1>'
         f'<p>Pick the job you need doing, like writing code, building an app without code, or putting it online, and we’ll tell you which tool we’d use and roughly what it costs. We check prices on the official pages and add new releases every morning. Nobody can pay to move up.</p>'
         f'<p>New to all this? Start with <a href="{BASE}guides/{beginner["slug"]}/">the best AI coding tool for beginners</a>. Can’t code at all? Read <a href="{BASE}guides/best-ai-coding-tool-for-non-developers/">the best AI tools for non-developers</a>, or see <a href="{BASE}compare/lovable-vs-bolt/">Lovable vs Bolt.new</a> and <a href="{BASE}compare/cursor-vs-github-copilot/">Cursor vs GitHub Copilot</a>.</p></section>')
boards = "".join(f'<div class="sechead" id="{slug(c)}"><h2>{e(c)}</h2><a href="{BASE}best/{slug(c)}/">Full ranking →</a></div><ol class="board">{"".join(row(t, t["rank"]) for t in bycat[c])}</ol>' for c in cats)
jump = '<p class="jump">Jump to: ' + " · ".join(f'<a href="#{slug(c)}">{e(c)}</a>' for c in cats) + '</p>'
side = (f'<aside class="side"><section><h2>Shipped lately</h2><ul class="log">' + "".join(f'<li><span class="date">{nice(r["date"])}</span><b>{e(r["name"])}</b><p>{e(r["summary"])}</p></li>' for r in dated[:8]) + f'</ul><p><a href="{BASE}weekly/">Everything from this week →</a></p></section>'
        f'<section><h2>Worth reading</h2><ol class="reads">' + "".join(f'<li><a href="{BASE}guides/{g["slug"]}/">{e(g["title"])}</a></li>' for g in G[::-1][:6]) + '</ol></section>'
        f'<section><h2>Head-to-heads</h2><ul class="plain">' + "".join(f'<li><a href="{BASE}compare/{a["slug"]}/">{e(a["title"].split(":")[0].split(" (")[0])}</a></li>' for a in cmp["articles"][::-1]) + f'</ul><p><a href="{BASE}compare/">All comparisons →</a></p></section>'
        f'<section class="note">Make a tool for builders? You can <a href="{BASE}featured/">pay for a labelled spot</a>. It won’t change where you rank, and we’ll say so on the page.</section></aside>')
hbody = intro + f'<div class="cols" style="margin-top:8px"><div id="rankings"><div class="sechead" style="margin-top:28px;border:0;padding:0"><h2 style="font-size:1.1rem;font-family:var(--mono);font-weight:400;color:var(--mute)">The rankings</h2></div>{jump}{boards}</div>{side}</div>'
home_ld = ldjson({"@context": "https://schema.org", "@type": "WebSite", "name": "ShipRank", "url": BASE, "description": "AI tool rankings for vibe coders and builders", "publisher": {"@type": "Organization", "name": "ShipRank", "url": BASE, "sameAs": ["https://x.com/ShipRankUK"], "logo": {"@type": "ImageObject", "url": BASE + "apple-touch-icon.png"}}})
page("", "ShipRank – AI tool rankings for builders", "ShipRank ranks the best AI tools for vibe coders and builders by use case, with verified pricing and new releases.", hbody, home_ld, active="")

# ---- RSS feed of releases ----
items = ""
for r in dated:
    dt = datetime.datetime.fromisoformat(r["date"] + "T09:00:00+00:00")
    y, w, _ = dt.date().isocalendar()
    items += f"<item><title>{e(r['name'])}</title><link>{e(r['url'])}</link><guid isPermaLink=\"false\">{e(r['date']+'-'+slug(r['name']))}</guid><pubDate>{format_datetime(dt)}</pubDate><description>{e(r['summary'])} (ShipRank weekly roundup: {BASE}weekly/{y}-w{w:02d}/)</description></item>\n"
open("weekly/feed.xml", "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>ShipRank Weekly – AI builder tool launches</title><link>{BASE}weekly/</link><atom:link href="{BASE}weekly/feed.xml" rel="self" type="application/rss+xml"/><description>Verified AI tool launches for vibe coders and builders.</description><language>en-gb</language><lastBuildDate>{format_datetime(datetime.datetime.now(datetime.timezone.utc))}</lastBuildDate>\n{items}</channel></rss>\n')
# ---- private-ish stats page (not in sitemap, noindex) ----
os.makedirs("stats", exist_ok=True)
SECTIONS = ["home","tools","best","compare","guides","weekly","featured"]
open("stats/index.html","w").write(f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ShipRank visit stats</title>{ICONS}<link rel="stylesheet" href="{BASE}assets/style.css?v={CSS_VER}"></head><body>{masthead("")}<main id="main" class="wrap page"><div class="head"><h1>Visit stats</h1><p class="dek">Anonymous, cookie-free page-view counts (all-time totals since 23 Oct 2026).</p></div><div class="tbl" style="max-width:520px"><table id=t><tr><th>Counter</th><th>Page views</th></tr></table></div><p><small>Counts come from Abacus (abacus.jasoncameron.dev). Viewing this page does not add a visit.</small></p></main>
<script>var a="https://abacus.jasoncameron.dev/get/shiprank.tobychecketts/";["visits"].concat({json.dumps(SECTIONS)}.map(function(s){{return "section-"+s}})).forEach(function(k){{var tr=document.createElement("tr");tr.innerHTML="<td>"+(k=="visits"?"<b>All pages</b>":k.slice(8))+"</td><td>…</td>";document.getElementById("t").appendChild(tr);fetch(a+k).then(function(r){{return r.json()}}).then(function(j){{tr.lastChild.textContent=j.value!=null?j.value:0}}).catch(function(){{tr.lastChild.textContent="0"}})}});</script>{CF_BEACON}</body></html>""")
open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{u}</loc><lastmod>{LV}</lastmod></url>\n" for u in urls) + "</urlset>\n")
open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
print(f"Built {len(urls)} URLs")

# ---- short-link redirects (fix links that got cut off when shared; not in sitemap) ----
REDIRECTS = {"compare/cu": "compare/cursor-vs-github-copilot/"}
for src, dst in REDIRECTS.items():
    os.makedirs(src, exist_ok=True)
    u = BASE + dst
    with open(os.path.join(src, "index.html"), "w") as f:
        f.write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Redirecting…</title><link rel="canonical" href="{u}"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={u}"><script>location.replace("{u}")</script></head><body><p><a href="{u}">Continue to the page</a></p></body></html>')
