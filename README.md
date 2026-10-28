# Palm Hills Dev — palmhillsdev.com

Marketing site for Palm Hills projects, owned and run by Ibrahim El Garhy (Sales Deputy Manager at Palm Hills).
Not the official Palm Hills website — that is said on the home, About, footer and every project FAQ.

Static site. Every HTML page is generated from two data files, so prices and text are edited in one place.

## Structure

```
index.html, badya.html, …     Arabic pages (generated — do not edit by hand)
en/                           English pages (generated)
assets/css/project.css        The one stylesheet (brand tokens at the top)
assets/js/project.js          Page behaviour, lead form, tracking events
assets/js/thank-you.js        Thank-you page (conversion event + WhatsApp redirect)
assets/js/countries.js        Country dial codes for the phone field
assets/fonts/                 Almarai
assets/img/brand/             Favicon
assets/img/flags/             Country flags for the phone field
assets/img/projects/<slug>/   Images of one project (one folder per project)
tools/site_data.py            Site config, projects, prices, payment plans, all UI text (AR + EN)
tools/pages_data.py           About and Privacy page text
tools/build.py                Generator
tools/serve.py                Local preview server
tools/apps-script/Code.gs     Google Sheet lead capture + email
tools/gtm/gtm-import.json     GTM container import (lead funnel)
docs/RUNBOOK.md               How these sites are built (being reorganised)
```

## Common tasks

- **Preview locally:** `python tools/serve.py` then open http://localhost:8080/
- **Change a price or text:** edit `tools/site_data.py`, run `python tools/build.py`, commit.
- **Payment plans:** each project has `plans`: `steps` (percent + label) and `terms` (years, discount %).
  The hero, cards, comparison table, FAQ and llms.txt all read from it.
- **Add a project:** add an entry to `PROJECTS` in `tools/site_data.py` (copy an existing one), put its
  images in `assets/img/projects/<slug>/` as `.webp`, set `"ready": True`, run the build. The project then
  gets its own page (AR + EN) and appears on the home cards, the comparison table, the other-projects
  carousel and the sitemap automatically.
- **Image names inside a project folder:** `hero` (page hero), `card` (home / carousel card), anything else
  is referenced by name from the project's `units`, `gallery`, `about_img` and `location.map`.
  Use a `-s` suffix for the small (≈640px) version used on cards.

## Deploy

Vercel for testing (`vercel.json` sends `X-Robots-Tag: noindex`). Production is Hostinger pulling `main`
(no build step — the generated HTML is committed). `.htaccess` blocks `tools/`, `data/`, `docs/` and the
`.md` files, and 301s the old WordPress URLs.
