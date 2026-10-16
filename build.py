#!/usr/bin/env python3
"""Generate SEO pages from tools.json: /tools/<slug>/, /best/<cat>/, sitemap.xml, robots.txt."""
import json, re, os, html, shutil
BASE = "https://tobychecketts.github.io/shiprank/"
d = json.load(open("tools.json"))
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
e = html.escape
YEAR = d["lastVerified"][:4]
CSS = """body{margin:0;font-family:system-ui,sans-serif;background:#0b0d12;color:#e7e9ee;line-height:1.5}header{padding:28px 24px;background:linear-gradient(135deg,#3b2aff,#00b3a4)}header a{color:#fff;text-decoration:none}main{max-width:900px;margin:auto;padding:24px}.card{background:#161a22;border:1px solid #232835;border-radius:14px;padding:16px;margin:12px 0}a{color:#7fb2ff}small{color:#9aa}table{border-collapse:collapse;width:100%}th,td{border:1px solid #232835;padding:8px;vertical-align:top;text-align:left;font-size:.9em}.rank{color:#00d1bd;font-weight:700}footer{max-width:900px;margin:auto;padding:24px;color:#9aa}"""
def page(path, title, desc, body):
    url = BASE + path
    out = f"""<!doctype html><html lang="en-GB"><head><meta name='impact-site-verification' value='433c0488-f7f6-4a86-9b9a-075a81062f41'><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="ShipRank"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}screenshot.png"><meta name="twitter:card" content="summary_large_image">
<style>{CSS}</style></head><body><header><a href="{BASE}"><h1 style="margin:0">🚢 ShipRank</h1></a><small style="color:#fff">AI tool rankings for vibe coders and builders · Last verified {d['lastVerified']}</small></header>
<main>{body}</main><footer>{cats_nav}</footer></body></html>"""
    os.makedirs(path or ".", exist_ok=True); open(os.path.join(path, "index.html"), "w").write(out); urls.append(url)
cats = sorted({t["category"] for t in d["tools"]}, key=lambda c: [t["category"] for t in d["tools"]].index(c))
cats_nav = f'<a href="{BASE}compare/">Comparisons</a> · Browse: ' + " · ".join(f'<a href="{BASE}best/{slug(c)}/">Best {e(c)}</a>' for c in cats)
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
        f'<div class=card><span class=rank>#{x["rank"]}</span> <a href="{BASE}tools/{slug(x["name"])}/"><b>{e(x["name"])}</b></a><p>{e(x["bestFor"])}</p><small>💡 {e(x["rankReason"])}<br>Free tier: {e(x["freeTier"])} · Entry: {e(x["entryPrice"])}</small></div>' for x in ts)
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
open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{u}</loc><lastmod>{d['lastVerified']}</lastmod></url>\n" for u in urls) + "</urlset>\n")
open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
print(f"Built {len(urls)} URLs")
