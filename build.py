#!/usr/bin/env python3
"""Generate the ShipRank site from tools.json, data/compare.json and data/guides.json.

Outputs: / (homepage), /tools/<slug>/, /best/<cat>/, /compare/, /guides/, /weekly/ (+ feed.xml), /featured/,
/stats/, assets/style.css (shared design), sitemap.xml, robots.txt.
Daily routine: edit tools.json -> python3 build.py -> commit + push -> python3 indexnow.py
"""
import json, re, os, html, shutil, hashlib, datetime
from email.utils import format_datetime
BASE = "https://tobychecketts.github.io/shiprank/"  # hosting address only; never shown as text
d = json.load(open("tools.json"))
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
e = html.escape
YEAR = d["lastVerified"][:4]
LV = d["lastVerified"]
def nice(ds):
    try: return datetime.date.fromisoformat(ds).strftime("%-d %b %Y")
    except Exception: return ds
CSS_VER = hashlib.md5(open("assets/style.css", "rb").read()).hexdigest()[:8]
ANALYTICS = """<script>/* Cookie-free anonymous visit counter (Abacus, no cookies, no personal data) */(function(){try{var n="shiprank.tobychecketts",s=location.pathname.split("/")[2]||"home",a="https://abacus.jasoncameron.dev/hit/"+n+"/";["visits","section-"+s.replace(/[^a-z0-9_-]/gi,"")].forEach(function(k){fetch(a+k,{mode:"no-cors",keepalive:true})})}catch(e){}})();</script>"""
MARK = '<svg class="mark" viewBox="0 0 32 32" aria-hidden="true"><defs><linearGradient id="srg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8b6cff"/><stop offset=".5" stop-color="#5b8cff"/><stop offset="1" stop-color="#22d3ee"/></linearGradient></defs><rect width="32" height="32" rx="9" fill="url(#srg)"/><path d="M9 21.5h3.2v-5H9zM14.4 21.5h3.2V10.5h-3.2zM19.8 21.5H23v-8h-3.2z" fill="#fff"/><path d="M8 24h16" stroke="#fff" stroke-width="1.6" stroke-linecap="round" opacity=".7"/></svg>'
FAVICON = "data:image/svg+xml," + re.sub(r"\s+", " ", MARK.replace(' class="mark"', ' xmlns="http://www.w3.org/2000/svg"')).replace("#", "%23").replace('"', "'")
cats = sorted({t["category"] for t in d["tools"]}, key=lambda c: [t["category"] for t in d["tools"]].index(c))
urls = [BASE]

def topbar(active):
    items = [("rankings", f"{BASE}#rankings", "Rankings"), ("compare", f"{BASE}compare/", "Compare"), ("guides", f"{BASE}guides/", "Guides"), ("weekly", f"{BASE}weekly/", "Weekly")]
    links = "".join(f'<a href="{h}"{" class=on" if k == active else ""}>{l}</a>' for k, h, l in items)
    return f'<a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="{BASE}" aria-label="ShipRank home">{MARK}<span>ShipRank</span></a><nav class="nav" aria-label="Main">{links}</nav><a class="btn primary sm topcta" href="{BASE}featured/">Get featured</a></div></header>'

def footer():
    best = "".join(f'<a href="{BASE}best/{slug(c)}/">Best {e(c)}</a>' for c in cats)
    return f"""<footer class="foot"><div class="wrap"><div class="cols"><div><a class="brand" href="{BASE}">{MARK}<span>ShipRank</span></a><p>Independent rankings of AI tools for vibe coders and builders. Prices are checked against official pricing pages, and new launches are added every day.</p><p><small>Last verified {nice(LV)}</small></p></div>
<div><h4>Rankings</h4>{best}</div><div><h4>Read</h4><a href="{BASE}guides/">Guides</a><a href="{BASE}compare/">Comparisons</a><a href="{BASE}weekly/">Weekly roundup</a><a href="{BASE}weekly/feed.xml">RSS feed</a></div><div><h4>ShipRank</h4><a href="{BASE}featured/">Get featured</a><a href="{BASE}#rankings">All tools</a><a href="{BASE}sitemap.xml">Sitemap</a></div></div>
<div class="legal"><p>Disclosure: some links on ShipRank may be affiliate links, and we may earn a commission if you buy through them, at no extra cost to you. Sponsored placements are always labelled. Neither affects our rankings, which are editorial.</p><p>Privacy: we count visits anonymously with a cookie-free counter; no cookies, no tracking across sites, no personal data.</p><p>© {YEAR} ShipRank</p></div></div></footer>"""

def page(path, title, desc, body, head="", hero="", active="", ogtype="website", raw=False):
    url = BASE + path + ("/" if path else "")
    content = body if raw else f'<div class="wrap page">{body}</div>'
    out = f"""<!doctype html><html lang="en-GB"><head><meta name='impact-site-verification' value='433c0488-f7f6-4a86-9b9a-075a81062f41'><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}"><meta name="theme-color" content="#08090d" media="(prefers-color-scheme: dark)"><meta name="theme-color" content="#f6f7fb" media="(prefers-color-scheme: light)"><link rel="icon" href="{FAVICON}">
<meta property="og:type" content="{ogtype}"><meta property="og:site_name" content="ShipRank"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}screenshot.png"><link rel="alternate" type="application/rss+xml" title="ShipRank Weekly" href="{BASE}weekly/feed.xml"><meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{BASE}assets/style.css?v={CSS_VER}">{ANALYTICS}{head}</head><body>{topbar(active)}
<main id="main">{hero}{content}</main>{footer()}</body></html>"""
    os.makedirs(path or ".", exist_ok=True); open(os.path.join(path, "index.html"), "w").write(out)
    if url not in urls: urls.append(url)

def ldjson(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + '</script>'
def faq_ld(faq): return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
def faq_html(faq, esc_answer=True): return "".join(f'<details class="faq"><summary>{e(q)}</summary><div><p>{e(a) if esc_answer else a}</p></div></details>' for q, a in faq)
def crumbs(*parts): return '<nav class="crumbs" aria-label="Breadcrumb">' + ' <span aria-hidden="true">/</span> '.join(f'<a href="{h}">{e(l)}</a>' if h else f'<span>{e(l)}</span>' for l, h in parts) + '</nav>'
def hero(title_html, lead="", crumb="", extra="", home=False):
    return f'<section class="hero{" home" if home else ""}"><div class="wrap">{crumb}<h1>{title_html}</h1>' + (f'<p class="lead">{lead}</p>' if lead else "") + extra + '</div></section>'
def rk(n): return f'<span class="rk{" r"+str(n) if n in (1,2,3) else ""}" title="Rank #{n}">#{n}</span>' if n else '<span class="rk" title="Not ranked">–</span>'
def visit(t, cls="btn sm", label=None):
    aff = t.get("affiliate")
    a = f'<a class="{cls}" href="{t["url"]}" rel="{"sponsored nofollow noopener" if aff else "nofollow noopener"}" target="_blank">{label or "Visit "+e(t["name"])} ↗</a>'
    return a + (' <small class="aff">(affiliate link)</small>' if aff else "")
def price_dl(t, link=True):
    return f'<dl class="price"><dt>Free tier</dt><dd>{e(t["freeTier"])}</dd><dt>Paid from</dt><dd>{e(t["entryPrice"])}</dd><dt>Checked</dt><dd>' + (f'<a href="{t["pricingUrl"]}" rel="nofollow">{nice(t["lastChecked"])}</a>' if link else nice(t["lastChecked"])) + '</dd></dl>'
def tool_card(t, show_cat=True, note=None, num=None):
    n = num if num is not None else t.get("rank")
    internal = any(x["name"] == t["name"] for x in d["tools"])
    name = f'<a href="{BASE}tools/{slug(t["name"])}/">{e(t["name"])}</a>' if internal else f'<a href="{t["url"]}" rel="nofollow">{e(t["name"])}</a>'
    return (f'<article class="card tool" data-cat="{e(t["category"])}"><div class="tool-top">{rk(n)}<div><h3>{name}</h3>' + (f'<span class="chip">{e(t["category"])}</span>' if show_cat else "") + '</div></div>'
            f'<p>{e(t["bestFor"])}</p>' + (f'<p class="why">{e(note)}</p>' if note else (f'<p class="why">{e(t["rankReason"])}</p>' if t.get("rankReason") else "")) + price_dl(t) +
            '<div class="actions">' + (f'<a class="btn sm" href="{BASE}tools/{slug(t["name"])}/">Review</a>' if internal else "") + visit(t, "btn sm", "Visit") + '</div></article>')

compare_links = {}
cmp = json.load(open("data/compare.json"))
for a in cmp["articles"]:
    for n in a["tools"]: compare_links.setdefault(n, []).append(a)
alltools = {t["name"]: t for t in d["tools"]}; alltools.update(cmp["extraTools"])
def tlink(n): return f'<a href="{BASE}tools/{slug(n)}/">{e(n)}</a>' if n in {t["name"] for t in d["tools"]} else f'<a href="{alltools[n]["url"]}" rel="nofollow">{e(n)}</a>'
G = json.load(open("data/guides.json"))["guides"]

# ---- tool pages ----
for p in ("tools", "best"): shutil.rmtree(p, ignore_errors=True)
for t in d["tools"]:
    s = slug(t["name"]); c = t["category"]
    peers = sorted([x for x in d["tools"] if x["category"] == c and x is not t], key=lambda x: x["rank"])
    h = hero(e(t["name"]) + ' <span class="muted" style="font-weight:600">review &amp; pricing</span>', e(t["bestFor"]),
             crumbs(("Home", BASE), (f"Best {c}", f"{BASE}best/{slug(c)}/"), (t["name"], None)),
             f'<div class="meta">{rk(t["rank"])}<span class="pill">#{t["rank"]} in {e(c)}</span><span class="pill"><span class="dot"></span>Pricing checked {nice(t["lastChecked"])}</span></div><div class="cta">{visit(t, "btn primary")}<a class="btn" href="{BASE}best/{slug(c)}/">See all {e(c.lower()) if c != "LLM APIs" else c}</a></div>')
    cmps = "".join(f'<a class="card link" href="{BASE}compare/{a["slug"]}/"><span class="eyebrow">Comparison</span><h3 style="margin-top:.3em">{e(a["title"])}</h3></a>' for a in compare_links.get(t["name"], []))
    body = f"""<div class="layout"><div class="prose"><div class="card callout"><span class="eyebrow">Why #{t['rank']}</span><p style="font-size:1.08rem;margin-top:.4em">{e(t['rankReason'])}</p></div>
<div class="grid tight" style="margin-top:14px"><div class="card"><h3>👍 Pros</h3><ul>{''.join('<li>'+e(x)+'</li>' for x in t['pros'])}</ul></div><div class="card"><h3>👎 Cons</h3><ul>{''.join('<li>'+e(x)+'</li>' for x in t['cons'])}</ul></div></div>
{('<h2>Compare '+e(t['name'])+'</h2>'+cmps) if cmps else ''}<h2>Alternatives to {e(t['name'])}</h2><div class="grid tight">{''.join(f'<a class="card link" href="{BASE}tools/{slug(x["name"])}/"><div class="tool-top">{rk(x["rank"])}<h3>{e(x["name"])}</h3></div><p class="muted" style="font-size:.92rem">{e(x["bestFor"])}</p></a>' for x in peers)}</div></div>
<aside class="aside"><div class="card"><h3>Pricing</h3>{price_dl(t, False)}<p><small>{e(t.get('pricingNote',''))} Checked {nice(t['lastChecked'])} on the <a href="{t['pricingUrl']}" rel="nofollow">official pricing page</a>.</small></p><div class="actions">{visit(t)}</div></div></aside></div>"""
    page(f"tools/{s}", f"{t['name']} Review & Pricing ({YEAR}) – ShipRank", f"{t['name']}: {t['bestFor']}. Free tier: {t['freeTier']}. Entry price: {t['entryPrice']}. Ranked #{t['rank']} in {c}."[:160], body, hero=h, active="rankings")

# ---- best-of category pages ----
FEAT = f'<div class="card dashed tool"><div class="tool-top"><span class="rk">★</span><h3>Your tool here</h3></div><p>Make AI tools for builders? <a href="{BASE}featured/">Get featured on ShipRank</a>. Sponsored slots are always clearly labelled.</p></div>'
for c in cats:
    ts = sorted([x for x in d["tools"] if x["category"] == c], key=lambda x: x["rank"])
    h = hero(f'Best {e(c)} for vibe coders <span class="grad-text">({YEAR})</span>', f"Our ranking of the best {e(c.lower())} for builders, with pricing checked on official pages.", crumbs(("Home", BASE), ("Rankings", f"{BASE}#rankings"), (c, None)),
             f'<div class="meta"><span class="pill"><span class="dot"></span>Updated {nice(LV)}</span><span class="pill">{len(ts)} tools ranked</span></div>')
    others = '<h2>More rankings</h2><div class="cats" style="justify-content:flex-start">' + "".join(f'<a href="{BASE}best/{slug(o)}/">Best {e(o)}</a>' for o in cats if o != c) + '</div>'
    page(f"best/{slug(c)}", f"Best {c} for Vibe Coders {YEAR} – ShipRank", f"The best {c.lower()} for vibe coders and builders in {YEAR}: " + ", ".join(x["name"] for x in ts) + ". Ranked with verified pricing."[:160],
         '<div class="grid">' + "".join(tool_card(x, show_cat=False) for x in ts) + FEAT + '</div>' + others, hero=h, active="rankings")

# ---- comparisons ----
shutil.rmtree("compare", ignore_errors=True)
rows = [("Best for","bestFor"),("Category","category"),("Free tier","freeTier"),("Entry price","entryPrice"),("Pros","pros"),("Cons","cons")]
idx = ""
for a in cmp["articles"]:
    ts = [alltools[n] for n in a["tools"]]
    cell = lambda t,k: "<br>".join(map(e,t[k])) if isinstance(t[k],list) else e(str(t[k]))
    table = '<div class="tbl"><table><thead><tr><th></th>' + "".join(f"<th>{tlink(t['name'])}</th>" for t in ts) + "</tr></thead><tbody>" + "".join(f"<tr><th>{l}</th>" + "".join(f"<td>{cell(t,k)}</td>" for t in ts) + "</tr>" for l,k in rows) + "<tr><th>ShipRank rank</th>" + "".join(f"<td>{'#'+str(t['rank'])+' in '+e(t['category']) if t.get('rank') else 'Not ranked'}</td>" for t in ts) + "</tr></tbody></table></div>"
    h = hero(e(a["title"]), e(a["desc"]), crumbs(("Home", BASE), ("Comparisons", f"{BASE}compare/"), (a["title"], None)), f'<div class="meta"><span class="pill"><span class="dot"></span>Prices checked on official pages</span></div>')
    body = f"""<div class="prose" style="max-width:none"><div class="card callout"><span class="eyebrow">Quick verdict</span><p style="font-size:1.05rem;margin-top:.4em">{a['verdict']}</p></div>
<h2>Side by side</h2>{table}
<h2>Who each is best for</h2><div class="grid tight">{''.join(f'<div class="card"><h3>{tlink(n)}</h3><p class="muted">{e(w)}</p></div>' for n,w in a['who'].items())}</div>
<h2>Pricing</h2><div class="grid tight">{''.join(f'<div class="card"><h3>{e(t["name"])}</h3>{price_dl(t)}</div>' for t in ts)}</div>
<p><small>Prices in USD as shown on official pages. Anything marked unknown/unverified could not be confirmed.</small></p>
<h2>FAQ</h2><div class="prose">{faq_html(a['faq'])}</div></div>"""
    page(f"compare/{a['slug']}", a["title"] + " – ShipRank", a["desc"][:160], body, ldjson(faq_ld(a["faq"])) if a.get("faq") else "", hero=h, active="compare", ogtype="article")
    idx += f'<a class="card link" href="{BASE}compare/{a["slug"]}/"><span class="eyebrow">{len(a["tools"])} tools</span><h3 style="margin-top:.4em">{e(a["title"])}</h3><p class="muted">{e(a["desc"])}</p></a>'
page("compare", f"AI Tool Comparisons for Vibe Coders {YEAR} – ShipRank", "Head-to-head comparisons of AI code editors, app builders, coding agents, backends and hosting for vibe coders.",
     f'<div class="grid">{idx}</div>', hero=hero('AI tool <span class="grad-text">comparisons</span>', "Head-to-head breakdowns of the tools builders argue about most, with prices, pros, cons and a straight verdict.", crumbs(("Home", BASE), ("Comparisons", None))), active="compare")

# ---- guides ----
shutil.rmtree("guides", ignore_errors=True)
gidx = ""
for g in G:
    items = '<div class="grid tight">' + "".join(tool_card(alltools[n], note=g.get("notes", {}).get(n), num=i) for i, n in enumerate(g["tools"], 1)) + '</div>'
    rel = [a for a in cmp["articles"] if set(a["tools"]) & set(g["tools"])]
    secs = lambda key: "".join(f'<h2 id="{slug(x["h"])}">{e(x["h"])}</h2>' + x["html"].replace('href="@/', f'href="{BASE}') for x in g.get(key, []))
    picks_t = g.get("picksTitle", "Our picks")
    picks = f'<h2 id="picks">{e(picks_t)}</h2>' if g.get("sections") or g.get("top") else ""
    srcs = ('<h2 id="sources">Sources</h2><ul>' + "".join(f'<li><a href="{u}" rel="nofollow">{e(l)}</a></li>' for l, u in g["sources"]) + "</ul>") if g.get("sources") else ""
    toc = [(x["h"], slug(x["h"])) for x in g.get("top", [])] + ([(picks_t, "picks")] if picks else []) + [(x["h"], slug(x["h"])) for x in g.get("sections", [])] + [("FAQ", "faq")] + ([("Sources", "sources")] if srcs else [])
    meta = '<div class="meta">' + (f'<span class="pill"><span class="dot"></span>Updated {nice(g["updated"])}</span>' if g.get("updated") else "") + f'<span class="pill">{len(g["tools"])} tools compared</span><span class="pill">By ShipRank</span></div>'
    upd = f'<p><small>Updated {nice(g["updated"])} · prices and plan details checked on official pages.</small></p>' if g.get("updated") else ""
    main_col = secs("top") + picks + items + secs("sections") + '<h2 id="faq">FAQ</h2>' + faq_html(g["faq"]) + srcs + upd + "<p><small>Prices in USD from official pages. Anything marked unverified could not be confirmed.</small></p>"
    aside = '<aside class="aside"><div class="card toc"><h3>On this page</h3>' + "".join(f'<a href="#{i}">{e(t)}</a>' for t, i in toc) + '</div>' + ('<div class="card"><h3>Related comparisons</h3>' + "".join(f'<a href="{BASE}compare/{a["slug"]}/" style="display:block;padding:4px 0">{e(a["title"])}</a>' for a in rel) + '</div>' if rel else "") + f'<div class="card callout"><h3>See every ranking</h3><p class="muted">{len(d["tools"])} tools across {len(cats)} categories, re-checked daily.</p><a class="btn primary sm" href="{BASE}#rankings">Browse rankings</a></div></aside>'
    body = f'<div class="layout"><div class="prose">{main_col}</div>{aside}</div>'
    gurl = f"{BASE}guides/{g['slug']}/"
    art = {"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["desc"], "mainEntityOfPage": gurl, "url": gurl, "image": BASE + "screenshot.png", "author": {"@type": "Organization", "name": "ShipRank", "url": BASE}, "publisher": {"@type": "Organization", "name": "ShipRank", "url": BASE}}
    if g.get("published"): art["datePublished"] = g["published"]
    if g.get("updated"): art["dateModified"] = g["updated"]
    h = hero(e(g["title"]), e(g["intro"]), crumbs(("Home", BASE), ("Guides", f"{BASE}guides/"), (g["title"], None)), meta)
    page(f"guides/{g['slug']}", g.get("metaTitle", g["title"] + " – ShipRank"), g["desc"][:160], body, ldjson(art) + (ldjson(faq_ld(g["faq"])) if g["faq"] else ""), hero=h, active="guides", ogtype="article")
    gidx += f'<a class="card link" href="{BASE}guides/{g["slug"]}/"><span class="eyebrow">Guide' + (f' · {nice(g["updated"])}' if g.get("updated") else "") + f'</span><h3 style="margin-top:.4em">{e(g["title"])}</h3><p class="muted">{e(g["desc"])}</p></a>'
page("guides", f"AI Tool Guides for Vibe Coders {YEAR} – ShipRank", "Guides to the best free, cheapest and beginner-friendly AI tools for vibe coders and solo builders.",
     f'<div class="grid">{gidx}</div>', hero=hero('Guides for <span class="grad-text">AI builders</span>', "Plain-English guides to picking the best free, cheapest and beginner-friendly AI tools to ship your idea.", crumbs(("Home", BASE), ("Guides", None))), active="guides")

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
    return '<div class="timeline">' + "".join(f'<h2 class="day">{datetime.date.fromisoformat(dd).strftime("%A %-d %B %Y")}</h2><div class="grid tight">' + "".join(f'<div class="card rel"><h3>{e(r["name"])}</h3><p style="-webkit-line-clamp:unset;display:block">{e(r["summary"])}</p><small><a href="{r["url"]}" rel="nofollow">Source ↗</a> · verified {r.get("verified","unknown")}</small></div>' for r in lst) + '</div>' for dd, lst in by.items()) + '</div>'
keys = sorted(weeks, reverse=True)
arch = '<h2>Archive</h2><div class="cats" style="justify-content:flex-start">' + "".join(f'<a href="{BASE}weekly/{k}/">Week {k[-2:]}, {k[:4]} · {len(weeks[k])} launches</a>' for k in keys) + "</div>"
RSSCARD = f'<div class="card callout" style="display:flex;gap:14px;align-items:center;justify-content:space-between;flex-wrap:wrap"><div><b>📡 Get every launch in your feed reader</b><p class="muted" style="margin:.2em 0 0">Email signup coming soon.</p></div><a class="btn primary sm" href="{BASE}weekly/feed.xml">Follow via RSS</a></div>'
for k in keys:
    page(f"weekly/{k}", f"AI builder tool launches – week {int(k[-2:])}, {k[:4]} – ShipRank", f"Verified AI tool launches for vibe coders and builders in ISO week {int(k[-2:])} of {k[:4]}, grouped by date with sources."[:160],
         wbody(k, weeks[k]) + arch, hero=hero(f'AI launches: week {int(k[-2:])}, {k[:4]}', f"{len(weeks[k])} launches, each confirmed on its source page.", crumbs(("Home", BASE), ("Weekly", f"{BASE}weekly/"), (f"Week {int(k[-2:])}", None))), active="weekly")
if keys:
    k = keys[0]
    page("weekly", "This Week in AI Builder Tools – ShipRank Weekly Roundup", f"This week's verified AI tool launches for vibe coders (week {int(k[-2:])}, {k[:4]}), grouped by date with sources.",
         RSSCARD + wbody(k, weeks[k]) + arch, hero=hero('This week in <span class="grad-text">AI builder tools</span>', f"Week {int(k[-2:])}, {k[:4]} · only launches confirmed on the source page.", crumbs(("Home", BASE), ("Weekly", None)), f'<div class="meta"><span class="pill"><span class="dot"></span>{len(weeks[k])} launches this week</span></div>'), active="weekly")

# ---- featured (sponsorship) page ----
MAILTO = "mailto:toby211@hotmail.co.uk?subject=" + "Get%20featured%20on%20ShipRank"
opts = [("Featured category slot","£49","per week","A highlighted ‘Featured’ card at the top of one category ranking page (e.g. Best app builders), clearly labelled as sponsored, with your logo, one-line pitch and link."),
        ("Weekly roundup spotlight","£29","per week","A spotlight card at the top of that week’s /weekly/ roundup page and its RSS item, labelled as sponsored."),
        ("Launch listing","£19","per week","Your launch listed on the homepage ‘New releases’ feed and the weekly roundup, labelled as sponsored. Must be a genuine, live launch.")]
fbody = '<div class="card callout"><b>🚀 Launch pricing</b><p class="muted">These are introductory prices for early sponsors and will change as traffic grows. Prices in GBP, per week.</p></div><div class="grid">'
fbody += "".join(f'<div class="card tool"><span class="eyebrow">{e(n)}</span><h2 style="margin:.1em 0" aria-label="{e(n)} — {p} {u}"><span class="price-big">{p}</span> <small>{u} (launch pricing)</small></h2><p class="muted">{e(w)}</p><div class="actions"><a class="btn primary sm" href="{MAILTO}%20-%20{n.replace(" ","%20")}">Enquire about {e(n)} →</a></div></div>' for n,p,u,w in opts) + '</div>'
fbody += '<div class="grid tight" style="margin-top:16px"><div class="card"><h3>Honest traffic note</h3><p class="muted">ShipRank is a new site (launched October 2026). We don’t yet have meaningful traffic numbers to share, which is why prices are low. We’ll publish stats here once we have them.</p></div>'
fbody += f'<div class="card"><h3>Get in touch</h3><p class="muted">Email us with your tool, the option you want and your preferred week.</p><a class="btn sm" href="{MAILTO}">Email ShipRank</a></div></div>'
page("featured", "Get Featured on ShipRank – Sponsor a Slot for Your AI Tool", "Sponsor a clearly labelled slot on ShipRank: featured category, weekly roundup spotlight or launch listing. Introductory launch pricing in GBP.", fbody,
     hero=hero('Get your tool in front of <span class="grad-text">AI builders</span>', "ShipRank helps vibe coders and builders pick AI tools, with verified pricing and honest rankings. Tool makers can sponsor a clearly labelled slot. <b>Sponsorship never changes our rankings or reviews.</b>", crumbs(("Home", BASE), ("Get featured", None))))

# ---- homepage ----
dated = sorted([r for r in d["releases"] if re.match(r"\d{4}-\d{2}-\d{2}$", r["date"])], key=lambda r: r["date"], reverse=True)
latest = dated[:8]
week_ago = (datetime.date.fromisoformat(LV) - datetime.timedelta(days=7)).isoformat()
hh = hero('Find the AI tools that help you <span class="grad-text">ship faster</span>', f"Honest rankings of AI code editors, app builders, coding agents and APIs for vibe coders and builders, with prices checked against official pages.",
          f'<span class="pill"><span class="dot"></span>Updated {nice(LV)} · new launches daily</span>',
          f'<div class="cta"><a class="btn primary" href="#rankings">Browse the rankings</a><a class="btn" href="{BASE}guides/best-ai-coding-tool-for-beginners/">New here? Start with the beginner guide</a></div>'
          f'<div class="stats"><div><b>{len(d["tools"])}</b>tools ranked</div><div><b>{len(cats)}</b>categories</div><div><b>{len([r for r in dated if r["date"] >= week_ago])}</b>launches this week</div><div><b>{len(G)}</b>in-depth guides</div></div>'
          '<div class="cats">' + "".join(f'<a href="{BASE}best/{slug(c)}/">{e(c)}</a>' for c in cats) + '</div>', home=True)
ranked = sorted(d["tools"], key=lambda t: (cats.index(t["category"]), t["rank"]))
filters = '<div class="filters" id="filters" role="toolbar" aria-label="Filter by category"><button class="on" data-f="">All</button>' + "".join(f'<button data-f="{e(c)}">{e(c)}</button>' for c in cats) + '</div>'
FILTER_JS = """<script>(function(){var f=document.getElementById("filters"),cards=document.querySelectorAll("#tools [data-cat]");f.addEventListener("click",function(ev){var b=ev.target.closest("button");if(!b)return;[].forEach.call(f.children,function(x){x.classList.toggle("on",x===b)});var v=b.getAttribute("data-f");[].forEach.call(cards,function(c){c.style.display=!v||c.getAttribute("data-cat")===v?"":"none"})})})();</script>"""
hbody = f"""<section class="section"><div class="wrap"><div class="sec-head"><div><span class="eyebrow">Fresh this week</span><h2>New releases</h2><p>The latest launches for builders, each confirmed on its source page.</p></div><a class="btn sm" href="{BASE}weekly/">Weekly roundup →</a></div>
<div class="grid tight rels">{''.join(f'<div class="card rel"><span class="date">{nice(r["date"])}' + (' <span class="chip new">New</span>' if r["date"] >= week_ago else '') + f'</span><h3>{e(r["name"])}</h3><p>{e(r["summary"])}</p><small><a href="{r["url"]}" rel="nofollow noopener" target="_blank">Source ↗</a></small></div>' for r in latest)}</div></div></section>
<section class="section" id="rankings"><div class="wrap"><div class="sec-head"><div><span class="eyebrow">Rankings</span><h2>The best AI tools, by job</h2><p>Ranked editorially. Sponsorship never changes a rank.</p></div><a class="btn sm" href="{BASE}compare/">Compare head-to-head →</a></div>
{filters}<div class="grid" id="tools">{''.join(tool_card(t) for t in ranked)}</div></div></section>
<section class="section"><div class="wrap"><div class="sec-head"><div><span class="eyebrow">Learn</span><h2>Guides &amp; comparisons</h2></div><a class="btn sm" href="{BASE}guides/">All guides →</a></div>
<div class="grid tight">{''.join(f'<a class="card link" href="{BASE}guides/{g["slug"]}/"><span class="eyebrow">Guide</span><h3 style="margin-top:.4em">{e(g["title"])}</h3></a>' for g in G[::-1][:5])}{''.join(f'<a class="card link" href="{BASE}compare/{a["slug"]}/"><span class="eyebrow">Comparison</span><h3 style="margin-top:.4em">{e(a["title"])}</h3></a>' for a in cmp["articles"][:3])}</div></div></section>
<section class="section"><div class="wrap"><div class="band"><div><h2>Building an AI tool for makers?</h2><p>Put it in front of vibe coders who are actively choosing their stack. Sponsored slots are always clearly labelled.</p></div><div class="cta" style="margin:0"><a class="btn primary" href="{BASE}featured/">Get featured</a><a class="btn" href="{BASE}weekly/feed.xml">📡 RSS</a></div></div></div></section>{FILTER_JS}"""
home_ld = ldjson({"@context": "https://schema.org", "@type": "WebSite", "name": "ShipRank", "url": BASE, "description": "AI tool rankings for vibe coders and builders", "publisher": {"@type": "Organization", "name": "ShipRank", "url": BASE}})
page("", "ShipRank – AI tool rankings for builders", "ShipRank ranks the best AI tools for vibe coders and builders by use case, with verified pricing and new releases.", hbody, home_ld, hero=hh, active="rankings", raw=True)

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
open("stats/index.html","w").write(f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ShipRank visit stats</title><link rel="icon" href="{FAVICON}"><link rel="stylesheet" href="{BASE}assets/style.css?v={CSS_VER}"></head><body>{topbar("")}<main id="main">{hero("Visit stats", "Anonymous, cookie-free page-view counts (all-time totals since 23 Oct 2026).")}<div class="wrap page"><div class="tbl" style="max-width:520px"><table id=t><tr><th>Counter</th><th>Page views</th></tr></table></div><p><small>Counts come from Abacus (abacus.jasoncameron.dev). Viewing this page does not add a visit.</small></p></div></main>
<script>var a="https://abacus.jasoncameron.dev/get/shiprank.tobychecketts/";["visits"].concat({json.dumps(SECTIONS)}.map(function(s){{return "section-"+s}})).forEach(function(k){{var tr=document.createElement("tr");tr.innerHTML="<td>"+(k=="visits"?"<b>All pages</b>":k.slice(8))+"</td><td>…</td>";document.getElementById("t").appendChild(tr);fetch(a+k).then(function(r){{return r.json()}}).then(function(j){{tr.lastChild.textContent=j.value!=null?j.value:0}}).catch(function(){{tr.lastChild.textContent="0"}})}});</script></body></html>""")
open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{u}</loc><lastmod>{LV}</lastmod></url>\n" for u in urls) + "</urlset>\n")
open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
print(f"Built {len(urls)} URLs")
