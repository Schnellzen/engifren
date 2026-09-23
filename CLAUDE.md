# EngiFren website: notes for Claude

Portfolio site for EngiFren ("Teman ngobrolin proyekmu"), a solo engineering-solutions business run by Dulham.
Live at https://schnellzen.github.io/engifren/. Every push to `main` rebuilds and deploys via `.github/workflows/deploy.yml`.

## Rules
- Content only lives in `data/site.json` and `projects/<slug>/project.json`. Do not change `build.py`, `templates/`, or `assets/` unless asked for a design or structure change.
- All text fields are bilingual: `{ "id": "...", "en": "..." }`. Write Indonesian first (casual "kamu" tone), then English.
- Allowed `disciplines`, `services`, and `status` values are defined in `data/site.json`. Use only those.
- Costing is percentages only, and must total 100. Put the engineering fee last. Never publish absolute prices.
- Don't invent results, years, or client names. Leave the field out if unknown.
- Client names are hidden unless the user says otherwise; use a generic `client_type`.
- Photos: run `python tools/compress_images.py projects/<slug>` before committing.

## Workflow for a new project
1. User fills the brief (questions below).
2. Create `projects/<slug>/` from `projects/_TEMPLATE/project.json`, with `"draft": false` only when the user says it is ready.
3. Run `python build.py` and fix every error it reports.
4. Commit with a message like `Add project: <title>` and push.

## Project brief questions
1. Short name  2. One-sentence description  3. Client type; show name? collaboration badge?
4. Year  5. Status (completed / ongoing / prototype)  6. Problem  7. What EngiFren did
8. Key components  9. Results (numbers)  10. Hard or clever part  11. Cost % (show or hide)
12. Confidential?  13. Links  14. Photos + captions

## User preferences
Concise answers, practical ready-to-use output.

## Inbox
New projects arrive as `_inbox/<slug>/` with `brief.md` + raw photos.
Create the project from it, compress photos into `projects/<slug>/`, build, show me a summary, and wait for my OK before committing and pushing.

Don't view photos unless I ask; just compress and copy them. Use captions from brief.md.
