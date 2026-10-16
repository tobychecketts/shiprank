#!/usr/bin/env python3
"""Generate SEO pages from tools.json: /tools/<slug>/, /best/<cat>/, sitemap.xml, robots.txt."""
import json, re, os, html, shutil
BASE = "https://tobychecketts.github.io/shiprank/"
d = json.load(open("tools.json"))
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
e = html.escape
YEAR = d["lastVerified"][:4]
CSS = """body{margin:0;font-family:system-ui,sans-serif;background:#0b0d12;color:#e7e9ee;line-height:1.5}header{padding:28px 24px;background:linear-gradient(135deg,#3b2aff,#00b3a4)}header a{color:#fff;text-decoration:none}main{max-width:900px;margin:auto;padding:24px}.card{background:#161a22;border:1px solid #232835;border-radius:14px;padding:16px;margin:12px 0}a{color:#7fb2ff}small{color:#9aa}.rank{color:#00d1bd;font-weight:700}footer{max-width:900px;margin:auto;padding:24px;color:#9aa}"""
def page(path, title, desc, body):
    url = BASE + path
    out = f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="ShipRank"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}screenshot.png"><meta name="twitter:card" content="summary_large_image">
<style>{CSS}</style></head><body><header><a href="{BASE}"><h1 style="margin:0">🚢 ShipRank</h1></a><small style="color:#fff">AI tool rankings for vibe coders and builders · Last verified {d['lastVerified']}</small></header>
<main>{body}</main><footer>{cats_nav}</footer></body></html>"""
    os.makedirs(path or ".", exist_ok=True); open(os.path.join(path, "index.html"), "w").write(out); urls.append(url)
cats = sorted({t["category"] for t in d["tools"]}, key=lambda c: [t["category"] for t in d["tools"]].index(c))
cats_nav = "Browse: " + " · ".join(f'<a href="{BASE}best/{slug(c)}/">Best {e(c)}</a>' for c in cats)
for p in ("tools", "best"): shutil.rmtree(p, ignore_errors=True)
urls = [BASE]
for t in d["tools"]:
    s = slug(t["name"]); c = t["category"]
    peers = [x for x in d["tools"] if x["category"] == c and x is not t]
    body = f"""<p><a href="{BASE}best/{slug(c)}/">← Best {e(c)} {YEAR}</a></p><h1>{e(t['name'])}: review, pricing &amp; ranking</h1>
<div class=card><span class=rank>#{t['rank']} in {e(c)}</span><p><b>Best for:</b> {e(t['bestFor'])}</p><p><b>Why this rank:</b> {e(t['rankReason'])}</p></div>
<div class=card><h2>Pricing</h2><p>Free tier: {e(t['freeTier'])}<br>Entry price: {e(t['entryPrice'])}</p><small>{e(t.get('pricingNote',''))} Checked {t['lastChecked']} on the <a href="{t['pricingUrl']}" rel="nofollow">official pricing page</a>.</small></div>
<div class=card><h2>Pros</h2><ul>{''.join('<li>'+e(x)+'</li>' for x in t['pros'])}</ul><h2>Cons</h2><ul>{''.join('<li>'+e(x)+'</li>' for x in t['cons'])}</ul></div>
<p><a href="{t['url']}" rel="nofollow">Visit {e(t['name'])} →</a></p>
<h2>Alternatives to {e(t['name'])}</h2><ul>{''.join(f'<li><a href="{BASE}tools/{slug(x["name"])}/">{e(x["name"])}</a> – {e(x["bestFor"])}</li>' for x in peers)}</ul>"""
    page(f"tools/{s}", f"{t['name']} Review & Pricing ({YEAR}) – ShipRank", f"{t['name']}: {t['bestFor']}. Free tier: {t['freeTier']}. Entry price: {t['entryPrice']}. Ranked #{t['rank']} in {c}."[:160], body)
for c in cats:
    ts = sorted([x for x in d["tools"] if x["category"] == c], key=lambda x: x["rank"])
    body = f"<h1>Best {e(c)} for vibe coders ({YEAR})</h1><p>Our ranking of the best {e(c.lower())} for builders, with verified pricing.</p>" + "".join(
        f'<div class=card><span class=rank>#{x["rank"]}</span> <a href="{BASE}tools/{slug(x["name"])}/"><b>{e(x["name"])}</b></a><p>{e(x["bestFor"])}</p><small>💡 {e(x["rankReason"])}<br>Free tier: {e(x["freeTier"])} · Entry: {e(x["entryPrice"])}</small></div>' for x in ts)
    page(f"best/{slug(c)}", f"Best {c} for Vibe Coders {YEAR} – ShipRank", f"The best {c.lower()} for vibe coders and builders in {YEAR}: " + ", ".join(x["name"] for x in ts) + ". Ranked with verified pricing."[:160], body)
open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{u}</loc><lastmod>{d['lastVerified']}</lastmod></url>\n" for u in urls) + "</urlset>\n")
open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
print(f"Built {len(urls)} URLs")
