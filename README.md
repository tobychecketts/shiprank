# ShipRank

AI tool rankings for vibe coders and builders: tools ranked by use case, with verified pricing and a feed of new releases.

- `index.html` – static site (plain HTML/JS)
- `tools.json` – all tool, pricing and release data (edit this to update the site)

Run locally: `python3 -m http.server` then open http://localhost:8000

## Build (SEO pages)

`python3 build.py` regenerates from `tools.json`:
- `tools/<slug>/index.html` – one page per tool
- `best/<category-slug>/index.html` – one ranking page per category
- `sitemap.xml` and `robots.txt`

Daily routine: update `tools.json` → run `python3 build.py` → commit and push to `main` (GitHub Pages serves the repo root).
