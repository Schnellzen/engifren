# EngiFren website

Portfolio site for EngiFren. Layout is built once; everything you change day to day is content in `data/` and `projects/`. Every push to `main` rebuilds and publishes the site automatically.

```
data/site.json               global text, contact, switches (bilingual)
projects/<slug>/project.json one project = one folder (+ its photos)
projects/_TEMPLATE/          copy this to start a new project (never published)
templates/, assets/          layout and styling (edit only for design changes)
build.py                     turns the content into the site (don't edit)
tools/compress_images.py     shrink photos before uploading
```

## One-time setup

1. On github.com, create a new **public** repository named `engifren` (GitHub Pages is free only for public repos).
2. Upload every file and folder from this zip: **Add file > Upload files**, drag everything in, commit.
   The `.github` folder is hidden on macOS (press Cmd+Shift+. in Finder to show it). It must be uploaded, because it contains the auto-deploy.
3. **Settings > Pages > Build and deployment > Source: GitHub Actions**.
4. **Actions** tab > **Build & deploy site** > **Run workflow**. After about a minute the site is live at
   `https://schnellzen.github.io/engifren/`

## Add a project

1. Shrink the photos on your computer first:
   `python tools/compress_images.py path/to/photo-folder`
2. On GitHub: **Add file > Create new file**, type the name `projects/your-project-name/project.json`
   (lowercase, dashes only). Paste the content of `projects/_TEMPLATE/project.json`, fill it in, set `"slug"` to the same folder name and `"draft": false`. Delete any field you don't need.
3. Open the new folder and use **Add file > Upload files** for `cover.jpg` and the `gallery/` photos.
4. Commit. The site updates in about a minute.

If something is wrong (typo in a tag, missing photo, costing not 100%), the build stops, the live site stays unchanged, and the **Actions** tab lists exactly what to fix.

Project page link: `https://schnellzen.github.io/engifren/projects/your-project-name/`
Force a language in a shared link by adding `?lang=en` or `?lang=id`.

## Switches

| Where | Field | Effect |
|---|---|---|
| `data/site.json` | `"show_costing": false` | hides every cost section on the whole site |
| `data/site.json` | `"default_lang"` | `"id"` or `"en"` for first-time visitors |
| `data/site.json` | `"base_url"` | change when you move to a custom domain |
| project | `"draft": true` | not published (preview locally with `--drafts`) |
| project | `"featured": true` | listed first |
| project | `"order": 1` | fine-tune order among featured (lower first) |
| project | `"confidential": true` | shows title, tags, client type only; hides details, photos, costs |
| project | `"costing": {"visible": false}` | hides this project's costs only |

## Project fields

Only `slug`, `title`, and `status` are required. Empty or missing fields simply don't appear.
Text fields are bilingual: `{ "id": "...", "en": "..." }`. If one language is missing, the other is shown.

| Field | Notes |
|---|---|
| `title`, `tagline` | tagline = one sentence, also used as the WhatsApp/social preview text |
| `status` | `completed`, `ongoing`, `prototype` |
| `year` | number, optional |
| `client_type` | e.g. `{"id": "UMKM pangan", "en": "Food SME"}`; avoid real client names unless allowed |
| `affiliations` | list of `{ "name", "logo" (file in the folder), "url" }`, all but name optional |
| `disciplines` | `process`, `mechanical`, `electronics`, `control`, `software`, `fabrication` |
| `services` | `process-engineering`, `mechanical-design`, `automation`, `prototyping`, `troubleshooting` |
| `problem`, `approach` | short paragraphs |
| `scope` | list of bilingual items |
| `results` | list of `{ "label": {...}, "value": "12 kW" }` |
| `costing.items` | list of `{ "label": {...}, "percent": 30 }`, must total 100; put the engineering fee last (it is highlighted) |
| `links` | `{ "type": "youtube" \| "link", "label": {...}, "url": "..." }`; YouTube links are embedded as a player |
| `media.cover` | main photo, also the social preview image (landscape, ~1600 px wide) |
| `media.gallery` | list of `{ "src": "gallery/01.jpg", "caption": {...} }` |

New discipline tag or service: add it in `data/site.json` (`vocab.disciplines` or `services`) and it becomes valid everywhere.

## Preview on your computer (optional)

```
pip install jinja2
python build.py --serve          # http://localhost:8000
python build.py --drafts --serve # include draft projects
```
