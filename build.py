#!/usr/bin/env python3
"""Generate SEO pages from tools.json: /tools/<slug>/, /best/<cat>/, sitemap.xml, robots.txt."""
import json, re, os, html, shutil
BASE = "https://tobychecketts.github.io/shiprank/"
d = json.load(open("tools.json"))
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
e = html.escape
YEAR = d["lastVerified"][:4]
CSS = """body{margin:0;font-family:system-ui,sans-serif;background:#0b0d12;color:#e7e9ee;line-height:1.5}header{padding:28px 24px;background:linear-gradient(135deg,#3b2aff,#00b3a4)}header a{color:#fff;text-decoration:none}main{max-width:900px;margin:auto;padding:24px}.card{background:#161a22;border:1px solid #232835;border-radius:14px;padding:16px;margin:12px 0}a{color:#7fb2ff}small{color:#9aa}table{border-collapse:collapse;width:100%}th,td{border:1px solid #232835;padding:8px;vertical-align:top;text-align:left;font-size:.9em}.rank{color:#00d1bd;font-weight:700}footer{max-width:900px;margin:auto;padding:24px;color:#9aa}"""
ANALYTICS = """<script>/* Cookie-free anonymous visit counter (Abacus, no cookies, no personal data) */(function(){try{var n="shiprank.tobychecketts",s=location.pathname.split("/")[2]||"home",a="https://abacus.jasoncameron.dev/hit/"+n+"/";["visits","section-"+s.replace(/[^a-z0-9_-]/gi,"")].forEach(function(k){fetch(a+k,{mode:"no-cors",keepalive:true})})}catch(e){}})();</script>"""
def page(path, title, desc, body):
    url = BASE + path + ("/" if path else "")
    out = f"""<!doctype html><html lang="en-GB"><head><meta name='impact-site-verification' value='433c0488-f7f6-4a86-9b9a-075a81062f41'><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="ShipRank"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}screenshot.png"><link rel="alternate" type="application/rss+xml" title="ShipRank Weekly" href="{BASE}weekly/feed.xml"><meta name="twitter:card" content="summary_large_image">
<style>{CSS}</style>{ANALYTICS}</head><body><header><a href="{BASE}"><h1 style="margin:0">🚢 ShipRank</h1></a><small style="color:#fff">AI tool rankings for vibe coders and builders · Last verified {d['lastVerified']}</small></header>
<main>{body}</main><footer>{cats_nav}<p><small>Disclosure: some links on ShipRank may be affiliate links, and we may earn a commission if you buy through them, at no extra cost to you. Sponsored placements are always labelled. Neither affects our rankings, which are editorial. Privacy: we count visits anonymously with a cookie-free counter; no cookies, no tracking across sites, no personal data.</small></p></footer></body></html>"""
    os.makedirs(path or ".", exist_ok=True); open(os.path.join(path, "index.html"), "w").write(out); urls.append(url)
cats = sorted({t["category"] for t in d["tools"]}, key=lambda c: [t["category"] for t in d["tools"]].index(c))
cats_nav = f'<a href="{BASE}compare/">Comparisons</a> · <a href="{BASE}guides/">Guides</a> · <a href="{BASE}weekly/">Weekly</a> · <a href="{BASE}weekly/feed.xml">RSS</a> · <a href="{BASE}featured/">Get featured</a> · Browse: ' + " · ".join(f'<a href="{BASE}best/{slug(c)}/">Best {e(c)}</a>' for c in cats)
for p in ("tools", "best"): shutil.rmtree(p, ignore_errors=True)
urls = [BASE]
compare_links = {}
for a in json.load(open("data/compare.json"))["articles"]:
    for n in a["tools"]: compare_links.setdefault(n, []).append(a)
for t in d["tools"]:
    s = slug(t["name"]); c = t["category"]
    peers = [x for x in d["tools"] if x["category"] == c and x is not t]
    body = f"""<p><a href="{BASE}best/{slug(c)}/">← Best {e(c)} {YEAR}</a></p><h1>{e(t['name'])}: review, pricing &amp; ranking</h1>
<div class=card><span class=rank>#{t['rank']} in {e(c)}</span><p><b>Best for:</b> {e(t['bestFor'])}</p><p><b>Why this rank:</b> {e(t['rankReason'])}</p></div>
<div class=card><h2>Pricing</h2><p>Free tier: {e(t['freeTier'])}<br>Entry price: {e(t['entryPrice'])}</p><small>{e(t.get('pricingNote',''))} Checked {t['lastChecked']} on the <a href="{t['pricingUrl']}" rel="nofollow">official pricing page</a>.</small></div>
<div class=card><h2>Pros</h2><ul>{''.join('<li>'+e(x)+'</li>' for x in t['pros'])}</ul><h2>Cons</h2><ul>{''.join('<li>'+e(x)+'</li>' for x in t['cons'])}</ul></div>
<p><a href="{t['url']}" rel="nofollow">Visit {e(t['name'])} →</a></p>
{''.join(f'<p>⚖️ <a href="{BASE}compare/{a["slug"]}/">{e(a["title"])}</a></p>' for a in compare_links.get(t["name"],[]))}<h2>Alternatives to {e(t['name'])}</h2><ul>{''.join(f'<li><a href="{BASE}tools/{slug(x["name"])}/">{e(x["name"])}</a> – {e(x["bestFor"])}</li>' for x in peers)}</ul>"""
    page(f"tools/{s}", f"{t['name']} Review & Pricing ({YEAR}) – ShipRank", f"{t['name']}: {t['bestFor']}. Free tier: {t['freeTier']}. Entry price: {t['entryPrice']}. Ranked #{t['rank']} in {c}."[:160], body)
for c in cats:
    ts = sorted([x for x in d["tools"] if x["category"] == c], key=lambda x: x["rank"])
    body = f"<h1>Best {e(c)} for vibe coders ({YEAR})</h1><p>Our ranking of the best {e(c.lower())} for builders, with verified pricing.</p>" + "".join(
        f'<div class=card><span class=rank>#{x["rank"]}</span> <a href="{BASE}tools/{slug(x["name"])}/"><b>{e(x["name"])}</b></a><p>{e(x["bestFor"])}</p><small>💡 {e(x["rankReason"])}<br>Free tier: {e(x["freeTier"])} · Entry: {e(x["entryPrice"])}</small></div>' for x in ts) + f'<div class=card style="border-style:dashed"><b>🌟 Your tool here</b><p>Make AI tools for builders? <a href="{BASE}featured/">Get featured on ShipRank</a> (sponsored slots are clearly labelled).</p></div>'
    page(f"best/{slug(c)}", f"Best {c} for Vibe Coders {YEAR} – ShipRank", f"The best {c.lower()} for vibe coders and builders in {YEAR}: " + ", ".join(x["name"] for x in ts) + ". Ranked with verified pricing."[:160], body)
cmp = json.load(open("data/compare.json")); shutil.rmtree("compare", ignore_errors=True)
alltools = {t["name"]: t for t in d["tools"]}; alltools.update(cmp["extraTools"])
def tlink(n): return f'<a href="{BASE}tools/{slug(n)}/">{e(n)}</a>' if n in {t["name"] for t in d["tools"]} else f'<a href="{alltools[n]["url"]}" rel="nofollow">{e(n)}</a>'
rows = [("Best for","bestFor"),("Category","category"),("Free tier","freeTier"),("Entry price","entryPrice"),("Pros","pros"),("Cons","cons")]
idx = ""
for a in cmp["articles"]:
    ts = [alltools[n] for n in a["tools"]]
    cell = lambda t,k: "<br>".join(map(e,t[k])) if isinstance(t[k],list) else e(str(t[k]))
    table = "<table><tr><th></th>" + "".join(f"<th>{tlink(t['name'])}</th>" for t in ts) + "</tr>" + "".join(f"<tr><th>{l}</th>" + "".join(f"<td>{cell(t,k)}</td>" for t in ts) + "</tr>" for l,k in rows) + "<tr><th>ShipRank rank</th>" + "".join(f"<td>{'#'+str(t['rank'])+' in '+e(t['category']) if t.get('rank') else 'Not ranked'}</td>" for t in ts) + "</tr></table>"
    body = f"""<p><a href="{BASE}compare/">← All comparisons</a></p><h1>{e(a['title'])}</h1><div class=card><h2>Quick verdict</h2><p>{a['verdict']}</p></div>
<h2>Comparison</h2><div style="overflow-x:auto">{table}</div>
<h2>Who each is best for</h2>{''.join(f'<div class=card><b>{tlink(n)}</b><p>{e(w)}</p></div>' for n,w in a['who'].items())}
<h2>Pricing</h2><ul>{''.join(f'<li><b>{e(t["name"])}</b>: free tier {e(t["freeTier"])}; entry {e(t["entryPrice"])}. <a href="{t["pricingUrl"]}" rel="nofollow">Pricing page</a>, checked {t["lastChecked"]}.</li>' for t in ts)}</ul>
<small>Prices in USD as shown on official pages. Anything marked unknown/unverified could not be confirmed.</small>
<h2>FAQ</h2>{''.join(f'<div class=card><b>{e(q)}</b><p>{e(ans)}</p></div>' for q,ans in a['faq'])}"""
    page(f"compare/{a['slug']}", a["title"] + " – ShipRank", a["desc"][:160], body)
    idx += f'<div class=card><a href="{BASE}compare/{a["slug"]}/"><b>{e(a["title"])}</b></a><p>{e(a["desc"])}</p></div>'
page("compare", f"AI Tool Comparisons for Vibe Coders {YEAR} – ShipRank", "Head-to-head comparisons of AI code editors, app builders, coding agents, backends and hosting for vibe coders.", "<h1>AI tool comparisons</h1>" + idx)

# ---- guides ----
import datetime
G = json.load(open("data/guides.json"))["guides"]; shutil.rmtree("guides", ignore_errors=True)
gidx = ""
for g in G:
    items = ""
    for i, n in enumerate(g["tools"], 1):
        t = alltools[n]
        items += f'<div class=card><span class=rank>#{i}</span> {tlink(n)}<p>{e(t["bestFor"])}</p>' + (f'<p class=why>💡 {e(g["notes"][n])}</p>' if n in g.get("notes",{}) else "") + f'<small>Free tier: {e(t["freeTier"])} · Entry: {e(t["entryPrice"])} · <a href="{t["pricingUrl"]}" rel="nofollow">pricing</a> checked {t["lastChecked"]}</small></div>'
    rel = [a for a in cmp["articles"] if set(a["tools"]) & set(g["tools"])]
    body = f'<p><a href="{BASE}guides/">← All guides</a></p><h1>{e(g["title"])}</h1><p>{e(g["intro"])}</p>{items}<h2>FAQ</h2>' + "".join(f'<div class=card><b>{e(q)}</b><p>{e(x)}</p></div>' for q, x in g["faq"]) + "<h2>Related comparisons</h2><ul>" + "".join(f'<li><a href="{BASE}compare/{a["slug"]}/">{e(a["title"])}</a></li>' for a in rel) + "</ul><small>Prices in USD from official pages. Anything marked unverified could not be confirmed.</small>"
    page(f"guides/{g['slug']}", g["title"] + " – ShipRank", g["desc"][:160], body)
    gidx += f'<div class=card><a href="{BASE}guides/{g["slug"]}/"><b>{e(g["title"])}</b></a><p>{e(g["desc"])}</p></div>'
page("guides", f"AI Tool Guides for Vibe Coders {YEAR} – ShipRank", "Guides to the best free, cheapest and beginner-friendly AI tools for vibe coders and solo builders.", "<h1>Guides</h1>" + gidx)

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
    return "".join(f'<h2>{datetime.date.fromisoformat(dd).strftime("%A %-d %B %Y")}</h2>' + "".join(f'<div class=card><b>{e(r["name"])}</b><p>{e(r["summary"])}</p><small><a href="{r["url"]}" rel="nofollow">Source</a> · verified {r.get("verified","unknown")}</small></div>' for r in lst) for dd, lst in by.items())
keys = sorted(weeks, reverse=True)
arch = "<h2>Archive</h2><ul>" + "".join(f'<li><a href="{BASE}weekly/{k}/">Week {k[-2:]}, {k[:4]}</a> ({len(weeks[k])} launches)</li>' for k in keys) + "</ul>"
for k in keys:
    page(f"weekly/{k}", f"AI builder tool launches – week {int(k[-2:])}, {k[:4]} – ShipRank", f"Verified AI tool launches for vibe coders and builders in ISO week {int(k[-2:])} of {k[:4]}, grouped by date with sources."[:160], f'<p><a href="{BASE}weekly/">← Latest roundup</a></p><h1>AI launches: week {int(k[-2:])}, {k[:4]}</h1>' + wbody(k, weeks[k]) + arch)
if keys:
    k = keys[0]
    page("weekly", "This Week in AI Builder Tools – ShipRank Weekly Roundup", f"This week's verified AI tool launches for vibe coders (week {int(k[-2:])}, {k[:4]}), grouped by date with sources.", f'<h1>This week in AI builder tools</h1><p>Week {int(k[-2:])}, {k[:4]} · only launches confirmed on the source page.</p><div class=card>📡 <a href="{BASE}weekly/feed.xml"><b>Follow via RSS</b></a> · Email signup coming soon.</div>' + wbody(k, weeks[k]) + arch)

# ---- featured (sponsorship) page ----
MAILTO = "mailto:toby211@hotmail.co.uk?subject=" + "Get%20featured%20on%20ShipRank"
opts = [("Featured category slot","£49","per week","A highlighted ‘Featured’ card at the top of one category ranking page (e.g. Best app builders), clearly labelled as sponsored, with your logo, one-line pitch and link."),
        ("Weekly roundup spotlight","£29","per week","A spotlight card at the top of that week’s /weekly/ roundup page and its RSS item, labelled as sponsored."),
        ("Launch listing","£19","per week","Your launch listed on the homepage ‘New releases’ feed and the weekly roundup, labelled as sponsored. Must be a genuine, live launch.")]
fbody = "<h1>Get featured on ShipRank</h1><p>ShipRank helps vibe coders and builders pick AI tools, with verified pricing and honest rankings. Tool makers can sponsor a clearly labelled slot. <b>Sponsorship never changes our rankings or reviews.</b></p>"
fbody += "<div class=card><b>🚀 Launch pricing</b><p>These are introductory prices for early sponsors and will change as traffic grows. Prices in GBP, per week.</p></div>"
fbody += "".join(f'<div class=card><h2>{e(n)} — {p} <small>{u} (launch pricing)</small></h2><p>{e(w)}</p><p><a href="{MAILTO}%20-%20{n.replace(" ","%20")}">Enquire about {e(n)} →</a></p></div>' for n,p,u,w in opts)
fbody += "<div class=card><h2>Honest traffic note</h2><p>ShipRank is a new site (launched October 2026). We don’t yet have meaningful traffic numbers to share, which is why prices are low. We’ll publish stats here once we have them.</p></div>"
fbody += f'<div class=card><h2>Get in touch</h2><p>Email <a href="{MAILTO}">toby211@hotmail.co.uk</a> with your tool, the option you want and your preferred week.</p></div>'
page("featured", "Get Featured on ShipRank – Sponsor a Slot for Your AI Tool", "Sponsor a clearly labelled slot on ShipRank: featured category, weekly roundup spotlight or launch listing. Introductory launch pricing in GBP.", fbody)

# ---- RSS feed of releases ----
from email.utils import format_datetime
items = ""
for r in sorted([r for r in d["releases"] if re.match(r"\d{4}-\d{2}-\d{2}$", r["date"])], key=lambda r: r["date"], reverse=True):
    dt = datetime.datetime.fromisoformat(r["date"] + "T09:00:00+00:00")
    y, w, _ = dt.date().isocalendar()
    items += f"<item><title>{e(r['name'])}</title><link>{e(r['url'])}</link><guid isPermaLink=\"false\">{e(r['date']+'-'+slug(r['name']))}</guid><pubDate>{format_datetime(dt)}</pubDate><description>{e(r['summary'])} (ShipRank weekly roundup: {BASE}weekly/{y}-w{w:02d}/)</description></item>\n"
open("weekly/feed.xml", "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>ShipRank Weekly – AI builder tool launches</title><link>{BASE}weekly/</link><atom:link href="{BASE}weekly/feed.xml" rel="self" type="application/rss+xml"/><description>Verified AI tool launches for vibe coders and builders.</description><language>en-gb</language><lastBuildDate>{format_datetime(datetime.datetime.now(datetime.timezone.utc))}</lastBuildDate>\n{items}</channel></rss>\n')
# ---- private-ish stats page (not in sitemap, noindex) ----
os.makedirs("stats", exist_ok=True)
SECTIONS = ["home","tools","best","compare","guides","weekly","featured"]
open("stats/index.html","w").write(f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ShipRank visit stats</title><style>{CSS}</style></head><body><header><a href="{BASE}"><h1 style="margin:0">🚢 ShipRank stats</h1></a><small style="color:#fff">Anonymous, cookie-free page-view counts (all-time totals since 23 Oct 2026)</small></header><main><table id=t><tr><th>Counter</th><th>Page views</th></tr></table><p><small>Counts come from Abacus (abacus.jasoncameron.dev). Viewing this page does not add a visit.</small></p></main>
<script>var a="https://abacus.jasoncameron.dev/get/shiprank.tobychecketts/";["visits"].concat({json.dumps(SECTIONS)}.map(function(s){{return "section-"+s}})).forEach(function(k){{var tr=document.createElement("tr");tr.innerHTML="<td>"+(k=="visits"?"<b>All pages</b>":k.slice(8))+"</td><td>…</td>";document.getElementById("t").appendChild(tr);fetch(a+k).then(function(r){{return r.json()}}).then(function(j){{tr.lastChild.textContent=j.value!=null?j.value:0}}).catch(function(){{tr.lastChild.textContent="0"}})}});</script></body></html>""")
open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{u}</loc><lastmod>{d['lastVerified']}</lastmod></url>\n" for u in urls) + "</urlset>\n")
open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
print(f"Built {len(urls)} URLs")
