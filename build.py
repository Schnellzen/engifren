#!/usr/bin/env python3
"""
EngiFren site builder.

    python build.py            build the site into _site/
    python build.py --drafts   also include projects marked "draft": true
    python build.py --serve    build, then preview at http://localhost:8000

Content lives in data/site.json and projects/<slug>/project.json.
You should not need to edit this file to add or change content.
"""
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
LANGS = ("id", "en")

errors, warnings = [], []


# ---------------------------------------------------------------- helpers
def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON at line {e.lineno}, column {e.colno} ({e.msg})")
        return None


def bi(value, where, field, required=False):
    """Normalise a bilingual field to {'id':..., 'en':...} or None."""
    if value in (None, "", {}):
        if required:
            errors.append(f"{where}: '{field}' is required")
        return None
    if isinstance(value, str):
        warnings.append(f"{where}: '{field}' is plain text; shown the same in both languages")
        return {"id": value, "en": value}
    if not isinstance(value, dict):
        errors.append(f"{where}: '{field}' must be {{\"id\": ..., \"en\": ...}}")
        return None
    out = {k: (value.get(k) or "").strip() for k in LANGS}
    missing = [k for k in LANGS if not out[k]]
    if len(missing) == 2:
        if required:
            errors.append(f"{where}: '{field}' is empty")
        return None
    for k in missing:
        other = "en" if k == "id" else "id"
        warnings.append(f"{where}: '{field}' has no '{k}' text; using '{other}'")
        out[k] = out[other]
    return out


def youtube_id(url):
    m = re.search(r"(?:youtube(?:-nocookie)?\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([\w-]{11})", url or "")
    return m.group(1) if m else None


def t(value):
    """Render a bilingual value as two spans; CSS shows the active language."""
    if not value:
        return ""
    if isinstance(value, str):
        return escape(value)
    a, b = value.get("id", ""), value.get("en", "")
    if a == b:
        return escape(a)
    return Markup(f'<span data-l="id">{escape(a)}</span><span data-l="en">{escape(b)}</span>')


# ---------------------------------------------------------------- site
def load_site():
    site = load_json(ROOT / "data" / "site.json")
    if site is None:
        return None
    site.setdefault("default_lang", "id")
    if site["default_lang"] not in LANGS:
        errors.append("data/site.json: default_lang must be 'id' or 'en'")
    site["base_url"] = site.get("base_url", "").rstrip("/")
    site["service_keys"] = {s["key"] for s in site.get("services", [])}
    return site


# ---------------------------------------------------------------- projects
def load_project(folder, site, include_drafts):
    where = f"projects/{folder.name}/project.json"
    raw = load_json(folder / "project.json")
    if raw is None:
        return None
    if raw.get("draft") and not include_drafts:
        print(f"  skip (draft): {folder.name}")
        return None

    p = {"folder": folder, "slug": folder.name}
    if raw.get("slug") and raw["slug"] != folder.name:
        errors.append(f"{where}: slug '{raw['slug']}' must match folder name '{folder.name}'")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", folder.name):
        errors.append(f"{where}: folder name must be lowercase letters, numbers and dashes")

    p["draft"] = bool(raw.get("draft"))
    p["featured"] = bool(raw.get("featured"))
    p["confidential"] = bool(raw.get("confidential"))
    p["year"] = raw.get("year")
    p["order"] = raw.get("order", 0)

    for f, req in [("title", True), ("tagline", False), ("client_type", False),
                   ("problem", False), ("approach", False)]:
        p[f] = bi(raw.get(f), where, f, req)

    status = raw.get("status")
    if status not in site["vocab"]["status"]:
        errors.append(f"{where}: status must be one of {list(site['vocab']['status'])}")
    p["status"] = status

    p["disciplines"] = raw.get("disciplines", [])
    for d in p["disciplines"]:
        if d not in site["vocab"]["disciplines"]:
            errors.append(f"{where}: unknown discipline '{d}' (allowed: {list(site['vocab']['disciplines'])})")
    p["services"] = raw.get("services", [])
    for s in p["services"]:
        if s not in site["service_keys"]:
            errors.append(f"{where}: unknown service '{s}' (allowed: {sorted(site['service_keys'])})")

    def asset(rel, field):
        if not rel:
            return None
        if not (folder / rel).is_file():
            errors.append(f"{where}: {field} file not found: {rel}")
            return None
        return rel

    p["affiliations"] = []
    for a in raw.get("affiliations", []):
        if not a.get("name"):
            errors.append(f"{where}: every affiliation needs a 'name'")
            continue
        p["affiliations"].append({"name": a["name"], "url": a.get("url") or None,
                                  "logo": asset(a.get("logo"), "affiliation logo")})

    p["scope"] = [x for x in (bi(s, where, "scope item") for s in raw.get("scope", [])) if x]

    p["results"] = []
    for r in raw.get("results", []):
        label = bi(r.get("label"), where, "result label", True)
        if label and r.get("value") not in (None, ""):
            p["results"].append({"label": label, "value": str(r["value"])})

    c = raw.get("costing") or {}
    p["costing"] = None
    if c.get("items"):
        items = []
        for it in c["items"]:
            label = bi(it.get("label"), where, "costing label", True)
            pct = it.get("percent")
            if label is None or not isinstance(pct, (int, float)):
                errors.append(f"{where}: each costing item needs a label and a numeric 'percent'")
                continue
            items.append({"label": label, "percent": pct})
        total = sum(i["percent"] for i in items)
        if items and abs(total - 100) > 0.5:
            errors.append(f"{where}: costing percentages add up to {total}, must be 100")
        p["costing"] = {"visible": c.get("visible", True), "items": items}

    p["links"], p["youtube"] = [], []
    for l in raw.get("links", []):
        url = l.get("url")
        if not url or "..." in url or "XXXX" in url:
            warnings.append(f"{where}: skipped a link with no real URL")
            continue
        label = bi(l.get("label"), where, "link label") or {"id": url, "en": url}
        vid = youtube_id(url) if l.get("type") == "youtube" else None
        if l.get("type") == "youtube" and not vid:
            warnings.append(f"{where}: could not read a YouTube video ID from {url}; shown as a plain link")
        (p["youtube"] if vid else p["links"]).append({"label": label, "url": url, "vid": vid})

    media = raw.get("media") or {}
    p["cover"] = asset(media.get("cover"), "cover")
    p["gallery"] = []
    for g in media.get("gallery", []):
        src = asset(g.get("src"), "gallery image")
        if src:
            p["gallery"].append({"src": src, "caption": bi(g.get("caption"), where, "caption")})
    p["videos"] = []
    for v in media.get("videos", []):
        src = asset(v.get("src"), "video")
        if src:
            p["videos"].append({"src": src, "caption": bi(v.get("caption"), where, "caption")})
    return p


def sort_key(p):
    return (not p["featured"], p["order"], -(p["year"] or 0), p["title"]["id"] if p["title"] else "")


# ---------------------------------------------------------------- build
def main():
    include_drafts = "--drafts" in sys.argv
    print("Building EngiFren site...")
    site = load_site()
    if site is None:
        return report()

    projects = []
    for folder in sorted((ROOT / "projects").iterdir()):
        if folder.is_dir() and not folder.name.startswith(("_", ".")):
            if not (folder / "project.json").is_file():
                warnings.append(f"projects/{folder.name}: no project.json, folder ignored")
                continue
            p = load_project(folder, site, include_drafts)
            if p:
                projects.append(p)
    projects.sort(key=sort_key)

    if errors:
        return report()

    lang = site["default_lang"]
    used_disciplines = [d for d in site["vocab"]["disciplines"]
                        if any(d in p["disciplines"] for p in projects)]

    def wa_url(message):
        return f"https://wa.me/{site['contact']['whatsapp']}?text={quote(message)}"

    def wa_attrs(msg, title=None):
        """href for the default language + data attributes the JS swaps on language change."""
        urls = {k: wa_url(msg[k].replace("{title}", title[k] if title else "")) for k in LANGS}
        return Markup(f'href="{escape(urls[lang])}" data-wa-id="{escape(urls["id"])}" '
                      f'data-wa-en="{escape(urls["en"])}" target="_blank" rel="noopener"')

    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    env.filters["t"] = t
    env.filters["tx"] = lambda v: (v or {}).get(lang, "") if isinstance(v, dict) else (v or "")
    env.globals.update(site=site, ui=site["ui"], vocab=site["vocab"], lang=lang,
                       wa_attrs=wa_attrs, show_costing=bool(site.get("show_costing")))

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "assets", OUT / "assets")

    # home page
    (OUT / "index.html").write_text(env.get_template("index.html").render(
        root="", page_url=site["base_url"] + "/", projects=projects,
        used_disciplines=used_disciplines), encoding="utf-8")

    # project pages
    for p in projects:
        dest = OUT / "projects" / p["slug"]
        shutil.copytree(p["folder"], dest, ignore=shutil.ignore_patterns("project.json", ".*"))
        others = [o for o in projects if o is not p][:3]
        og_image = (f"{site['base_url']}/projects/{p['slug']}/{p['cover']}"
                    if p["cover"] and not p["confidential"] else None)
        (dest / "index.html").write_text(env.get_template("project.html").render(
            root="../../", p=p, others=others, og_image=og_image,
            page_url=f"{site['base_url']}/projects/{p['slug']}/"), encoding="utf-8")

    (OUT / "404.html").write_text(env.get_template("404.html").render(
        root="/" + site["base_url"].split("/", 3)[3] + "/" if site["base_url"].count("/") > 2 else "/",
        page_url=site["base_url"] + "/"), encoding="utf-8")

    urls = [site["base_url"] + "/"] + [f"{site['base_url']}/projects/{p['slug']}/" for p in projects]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {site['base_url']}/sitemap.xml\n")
    (OUT / ".nojekyll").write_text("")

    print(f"  {len(projects)} project(s): " + ", ".join(p["slug"] for p in projects))
    report()
    if "--serve" in sys.argv:
        serve()


def report():
    for w in warnings:
        print(f"  warning: {w}")
    if errors:
        print("\nBuild failed. Fix these and run again:")
        for e in errors:
            print(f"  error: {e}")
        sys.exit(1)
    print("Done. Output in _site/")


def serve():
    import http.server
    import functools
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    print("Preview at http://localhost:8000  (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer(("", 8000), handler).serve_forever()


if __name__ == "__main__":
    main()
