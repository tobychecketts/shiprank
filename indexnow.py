#!/usr/bin/env python3
"""Ping IndexNow (Bing, Yandex, Seznam, Naver...) about new/changed ShipRank URLs. No sign-in needed.

Usage (run AFTER pushing and once GitHub Pages is live):
  python3 indexnow.py            # URLs for HTML files changed in the last commit (HEAD~1..HEAD)
  python3 indexnow.py --since REF  # URLs for HTML files changed since a git ref
  python3 indexnow.py --all      # every URL in sitemap.xml
  python3 indexnow.py URL [URL...] # specific URLs
"""
import json, re, subprocess, sys, urllib.request
BASE = "https://tobychecketts.github.io/shiprank/"
HOST = "tobychecketts.github.io"
KEY = "e5f47d70a4c91ed0ebc65a31f5ba958e"  # public key; key file is /<KEY>.txt at repo root
ENDPOINT = "https://api.indexnow.org/indexnow"

def path_to_url(p):
    if not p.endswith(".html"): return None
    if p.startswith("stats/"): return None
    p = p[:-len("index.html")] if p.endswith("index.html") else p
    return BASE + p

def changed(since):
    out = subprocess.run(["git", "diff", "--name-only", since, "HEAD"], capture_output=True, text=True, check=True).stdout.split()
    return [u for u in map(path_to_url, out) if u]

def main(a):
    if a and a[0] == "--all":
        urls = re.findall(r"<loc>(.*?)</loc>", open("sitemap.xml").read())
    elif a and a[0] == "--since":
        urls = changed(a[1])
    elif a:
        urls = a
    else:
        urls = changed("HEAD~1")
    urls = sorted(set(u for u in urls if u.startswith(BASE)))
    if not urls:
        print("IndexNow: nothing to submit"); return 0
    body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"{BASE}{KEY}.txt", "urlList": urls[:10000]}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: code = r.status
    except urllib.error.HTTPError as e: code = e.code
    print(f"IndexNow: submitted {len(urls)} URLs -> HTTP {code} (200/202 = accepted)")
    return 0 if code in (200, 202) else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
