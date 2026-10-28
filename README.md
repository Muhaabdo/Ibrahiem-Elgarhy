# VIBE Real Estate — viberealestatre.com

Static site. Every HTML page is generated from two data files, so prices and text are edited in one place.

## Structure

```
index.html, px.html, …        Arabic pages (generated — do not edit by hand)
en/                           English pages (generated)
assets/css/project.css        The one stylesheet
assets/js/project.js          Page behaviour, lead form, tracking events
assets/js/thank-you.js        Thank-you page (conversion event + WhatsApp redirect)
assets/js/countries.js        Country dial codes for the phone field
assets/fonts/                 Almarai + El Messiri
assets/img/brand/             Favicon / logo assets
assets/img/flags/             Country flags for the phone field
assets/img/projects/<slug>/   Images of one project (one folder per project)
assets/img/_future/<slug>/    Source images for projects that have no page yet (not served)
tools/site_data.py            Projects, prices, all UI text (AR + EN)
tools/pages_data.py           About and Privacy page text
tools/build.py                Generator
tools/serve.py                Local preview server
tools/apps-script/Code.gs     Google Sheet lead capture + email
```

## Common tasks

- **Preview locally:** `python tools/serve.py` then open http://localhost:8080/
- **Change a price or text:** edit `tools/site_data.py`, run `python tools/build.py`, commit.
- **Add a project:** add an entry to `PROJECTS` in `tools/site_data.py` (copy an existing one), put its
  images in `assets/img/projects/<slug>/` as `.webp`, set `"ready": True`, run the build. The project then
  appears on its own page (AR + EN), the home cards, the comparison table, the other-projects carousel
  and the sitemap automatically.
- **Image names inside a project folder:** `hero` (page hero), `card` (home / carousel card), anything else
  is referenced by name from the project's `units`, `gallery`, `about_img` and `location.map`.
  Use a `-s` suffix for the small (≈800px) version used on cards.

## Deploy

Hosting is Hostinger with manual upload. Upload everything except `tools/`, `data/`, `README.md` and
`assets/img/_future/`. Vercel is used for previews only.
