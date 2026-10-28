#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builds the project landing pages (AR at the root, EN under /en/) and the thank-you pages.

    python3 tools/build.py

Content lives in tools/site_data.py; markup lives here. Output files are committed, so the
host only ever serves static HTML.
"""
import json
import os
import sys
from html import escape as esc

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from site_data import SITE, PROJECTS, T  # noqa: E402
from pages_data import ABOUT, PRIVACY, PRIVACY_EMAIL, MISC, HUB, HUB_SLUG  # noqa: E402

LANGS = ("ar", "en")
ASSET_V = "20261011c"


def ic(name):
    return f'<svg class="ic" aria-hidden="true"><use href="/assets/img/icons.svg#i-{name}"></use></svg>'


def money(n):
    return f"{n:,}"


def price_html(n, t):
    num = f'<b>{money(n)}</b>'
    return f'<span>{t["from"]}</span>{num}<span>{t["egp"]}</span>' if t["dir"] == "rtl" else f'<span>{t["from"]} {t["egp"]}</span>{num}'


def url(slug, lang, absolute=False):
    path = ("/en/" if lang == "en" else "/") + slug
    if slug == "":
        path = "/en/" if lang == "en" else "/"
    return (SITE["domain"] + path) if absolute else path


def img(project_img, name):
    return f"/assets/img/projects/{project_img}/{name}.webp"


def build_sprite():
    icons = json.load(open(os.path.join(HERE, "icons.json"), encoding="utf-8"))
    out = ['<svg xmlns="http://www.w3.org/2000/svg" style="display:none">']
    for name, d in icons.items():
        paths = "".join(f'<path d="{p}"/>' for p in d["d"])
        out.append(f'<symbol id="i-{name}" viewBox="{d["vb"]}">{paths}</symbol>')
    out.append("</svg>")
    with open(os.path.join(ROOT, "assets/img/icons.svg"), "w", encoding="utf-8") as f:
        f.write("".join(out))


def gtm_head():
    return ("<!-- Google Tag Manager -->\n"
            "<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':\n"
            "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],\n"
            "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=\n"
            "'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);\n"
            f"}})(window,document,'script','dataLayer','{SITE['gtm']}');</script>\n"
            "<!-- End Google Tag Manager -->")


def gtm_body():
    return ("<!-- Google Tag Manager (noscript) -->\n"
            f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={SITE["gtm"]}"\n'
            'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n'
            "<!-- End Google Tag Manager (noscript) -->")


def lang_toggle(slug, lang):
    """Compact language switch shown inside the nav bar on phones (the top bar is hidden there)."""
    other = "en" if lang == "ar" else "ar"
    label = "English" if other == "en" else "العربية"
    return (f'<a class="nav-lang" href="{url(slug, other)}" lang="{other}" hreflang="{other}" aria-label="{label}">'
            f'{ic("globe")}<span>{"EN" if other == "en" else "عربي"}</span></a>')


def lang_bar(slug, lang, t, keep=False):
    cur = ' aria-current="true"'
    return f'''<div class="lang{" lang-keep" if keep else ""}">
 <div class="wrap">
  <nav class="lang-switch" aria-label="Language">
   <a href="{url(slug, "ar")}" lang="ar" hreflang="ar"{cur if lang == "ar" else ""}>العربية</a>
   <a href="{url(slug, "en")}" lang="en" hreflang="en"{cur if lang == "en" else ""}>English</a>
  </nav>
 </div>
</div>'''


def unit_card(p, u, lang, t, title, launch=None):
    """One unit card. `launch` is the new-phase dict when the unit belongs to it."""
    value = f'{launch["name"]} - {u["name"]}' if launch else u["name"]
    imgs = "".join(f'<img src="{img(p["img"], i)}" alt="{esc(title)} — {esc(u["name"])}" loading="lazy">' for i in u.get("imgs", []))
    mini = (f'''<div class="mini">{imgs}</div>
     <button class="mini-nav prev" type="button" aria-label="prev">{ic("chev-r" if t["dir"] == "rtl" else "chev-l")}</button>
     <button class="mini-nav next" type="button" aria-label="next">{ic("chev-l" if t["dir"] == "rtl" else "chev-r")}</button>
     <div class="mini-dots"></div>''' if imgs else "")
    badges = [esc(b) for b in u.get("badges", [])]
    if u.get("finish"):
        badges.append(esc(t["fin_" + u["finish"]]))
    badges = "".join(f'<span class="badge">{b}</span>' for b in badges)
    if "land" in u:
        specs = [(t["u_bua"], u["bua"]), (t["u_land"], u["land"])]
        spec_html = "".join(f'<div class="spec"><span>{esc(k)}</span><b><span class="ltr">{esc(v)}</span> {esc(t["sqm"])}</b></div>' for k, v in specs)
    else:
        spec_html = (f'<div class="spec"><span>{esc(t["u_area"])}</span><b><span class="ltr">{esc(u["area"])}</span> {esc(t["sqm"])}</b></div>'
                     f'<div class="spec"><span>{esc(t["u_deliv"])}</span><b>{p["delivery"]}</b></div>')
    price = price_html(u["price"], t) if u["price"] else f'<b class="price-req">{esc(t["price_req"])}</b>'
    off = f'<span class="card-off">{esc(t["new_launch"])}</span>' if launch else ""
    return f'''<article class="card">
    <div class="card-media">
     {mini}
     {off}<span class="card-tag">{ic("pin")} {esc(launch["name"] if launch else p["area"][lang])}</span>
    </div>
    <div class="card-body">
     <h3 class="card-name">{esc(u["name"])}</h3>
     <div class="card-sub">{esc(u["sub"][lang])}</div>
     <div class="badges">{badges}</div>
     <div class="specs">{spec_html}</div>
     <div class="price">{price}</div>
     <button class="btn btn-dark" type="button" data-cta="{"launch_card" if launch else "unit_card"}" data-unit="{esc(value)}">{ic("whatsapp")} {esc(t["cta_card"])}</button>
    </div>
   </article>'''


def footer(lang, t):
    return f'''<footer class="ft">
 <div class="wrap">
  <div class="ft-top">
   <div>
    <div class="ft-logo">VIBE <span>Real Estate</span></div>
    <div class="ft-acr">Vision · Investment · Brokerage · Excellence</div>
    <p class="ft-tag">{esc(t["ft_tag"])}</p>
   </div>
   <div class="ft-disc">{ic("info")}<p>{t["ft_disc"]}</p></div>
  </div>
  <div class="ft-bot">
   <div>© <span id="year">2026</span> VIBE Real Estate — {esc(t["ft_rights"])}</div>
   <ul class="ft-links">
    <li><a href="{url(HUB_SLUG, lang)}">{esc(HUB[lang]["crumb"])}</a></li>
    <li><a href="{url("about-us", lang)}">{esc(t["ft_about"])}</a></li>
    <li><a href="{url("privacy-policy", lang)}">{esc(t["ft_priv"])}</a></li>
   </ul>
  </div>
 </div>
</footer>'''


def cookie(t):
    return f'''<div class="ck hide" id="ck" role="region" aria-label="{esc(t["ck_aria"])}">
 <button class="ck-x" type="button" data-ck-close aria-label="{esc(t["close"])}">{ic("x")}</button>
 <div class="ck-top">
  <div class="ck-ic">{ic("cookie")}</div>
  <div><div class="ck-title">{t["ck_title"]}</div><div class="ck-text"><span class="ck-long">{t["ck_text"]}</span><span class="ck-short">{t["ck_short"]}</span></div></div>
 </div>
 <button class="btn ck-ok" type="button" data-ck-close>{ic("check")} <span class="ck-long">{esc(t["ck_ok"])}</span><span class="ck-short">{esc(t["ck_ok_short"])}</span></button>
</div>'''


def lead_form(p, t, loc, inline=False, uid="m"):
    """`p` is a project dict, or None on the home page where the select picks the project."""
    lab = {"l": t["f_unit"], "ph": t["f_unit_ph"], "err": t["f_unit_err"]}
    if p is None:
        lab = {"l": t["f_project"], "ph": t["f_project_ph"], "err": t["f_project_err"]}
        opts = "".join(f'<option value="{esc(o["name"])}">{esc(o["title"])}</option>' for o in PROJECTS.values() if o.get("ready"))
    else:
        opts = "".join(f'<option value="{esc(u["name"])}">{esc(u["name"])}</option>' for u in p["units"])
        if p.get("launch"):
            L = p["launch"]
            opts += f'<optgroup label="{esc(L["name"])}">' + "".join(
                f'<option value="{esc(L["name"])} - {esc(u["name"])}">{esc(u["name"])}</option>' for u in L["units"]) + "</optgroup>"
    return f'''<form class="lf" novalidate data-loc="{loc}"{" data-inline" if inline else ""}>
 <div class="lf-f">
  <label for="{uid}-name">{esc(t["f_name"])}</label>
  <input type="text" id="{uid}-name" name="name" autocomplete="name" placeholder="{esc(t["f_name_ph"])}" maxlength="60" required>
  <div class="lf-err">{esc(t["f_name_err"])}</div>
 </div>
 <div class="lf-f">
  <label for="{uid}-phone">{esc(t["f_phone"])}</label>
  <div class="ph">
   <button type="button" class="ph-cc" aria-haspopup="listbox" aria-expanded="false" aria-label="{esc(t["f_cc"])}">
    <img src="/assets/img/flags/EG.svg" width="24" height="16" alt=""><b>+20</b>{ic("chev-d")}
   </button>
   <input type="tel" id="{uid}-phone" name="phone" inputmode="tel" autocomplete="tel-national" maxlength="20" required>
   <div class="cc-pop">
    <div class="cc-search"><input type="text" placeholder="{esc(t["f_cc_search"])}" aria-label="{esc(t["f_cc_search"])}" autocomplete="off"></div>
    <div class="cc-list" role="listbox"></div>
   </div>
  </div>
  <div class="lf-err">{esc(t["f_phone_err"])}</div>
 </div>
 <div class="lf-f">
  <label for="{uid}-unit">{esc(lab["l"])}</label>
  <select id="{uid}-unit" name="unit">
   <option value="">{esc(lab["ph"])}</option>{opts}
   <option value="Not sure">{esc(t["f_unit_any"])}</option>
  </select>
  <div class="lf-err">{esc(lab["err"])}</div>
 </div>
 <input class="lf-hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
 <button class="btn lf-submit" type="submit">{ic("whatsapp")}<span>{esc(t["f_submit"])}</span></button>
 <p class="lf-priv">{t["f_priv"]}</p>
</form>'''


def other_cards(slug, lang, t):
    out = []
    for s, o in PROJECTS.items():
        if s == slug:
            continue
        media = (f'<img src="{img(o["img"], o["card"])}" alt="{esc(o["title"])}" loading="lazy" '
                 f'style="width:100%;height:100%;object-fit:cover">') if o.get("card") else ""
        off = f'<span class="card-off">{esc(t["more_off"].format(p=o["discount"]["pct"]))}</span>' if o["discount"] else ""
        badges = "".join(f'<span class="badge">{esc(b)}</span>' for b in o["types"][lang])
        out.append(f'''<a class="card" href="{url(s, lang)}" data-track="project_switch" data-loc="other_projects" data-target="{esc(o["name"])}">
    <div class="card-media">{media}{off}<span class="card-tag">{ic("pin")} {esc(o["area"][lang])}</span></div>
    <div class="card-body">
     <h3 class="card-name">{esc(o["title"])}</h3>
     <div class="badges">{badges}</div>
     <div class="specs">
      <div class="spec"><span>{esc(t["down"])}</span><b>{o["down"]}%</b></div>
      <div class="spec"><span>{esc(t["years"])}</span><b>{o["years"]}</b></div>
      <div class="spec"><span>{esc(t["u_deliv"])}</span><b>{o["delivery"]}</b></div>
     </div>
     <div class="price">{price_html(o["price_from"], t)}</div>
     <span class="card-more">{esc(t["more_link"])} {ic("arrow-l" if t["dir"] == "rtl" else "arrow-r")}</span>
    </div>
   </a>''')
    return "\n   ".join(out)


def unit_size(u, t):
    """Plain-text size of a unit: built-up area, plus land when the unit has it."""
    if u.get("area"):
        return f'{u["area"]} {t["sqm"]}'
    out = f'{t["u_bua"]} {u["bua"]} {t["sqm"]}'
    if u.get("land"):
        out += f'، {t["u_land"]} {u["land"]} {t["sqm"]}' if t["dir"] == "rtl" else f', {t["u_land"].lower()} {u["land"]} {t["sqm"]}'
    return out


def project_faq(p, lang, t):
    """Question/answer pairs built from the project data, so they always match the prices on the page.
    Shown on the page and repeated in the FAQPage schema and in llms.txt."""
    ar = lang == "ar"
    name, units, disc, launch = p["title"], p["units"], p["discount"], p.get("launch")
    egp = t["egp"]
    sep = "؛ " if ar else "; "
    price_list = sep.join((f'{u["name"]} {"من" if ar else "from"} {money(u["price"])} {egp}' if ar
                           else f'{u["name"]} from {egp} {money(u["price"])}') for u in units if u.get("price"))
    size_list = sep.join(f'{u["name"]} ({unit_size(u, t)})' for u in units)
    qa = []
    if ar:
        qa.append((f"فين مكان {name}؟", f'{p["location"]["text"]["ar"]} المشروع من تطوير Palm Hills Developments.'))
        qa.append((f"أسعار {name} بتبدأ من كام؟",
                   f'الأسعار بتبدأ من {money(p["price_from"])} جنيه. أسعار الوحدات المتاحة: {price_list}.'))
        pay = f'مقدم {p["down"]}% وتقسيط حتى {p["years"]} سنوات.'
        if disc:
            pay += f' وفيه خصم يصل إلى {disc["pct"]}% على نظام تقسيط {disc["years"]} سنوات.'
        if launch:
            pay += f' مرحلة {launch["name"]}: مقدم {launch["down"]}% وتقسيط حتى {launch["years"]} سنوات.'
        qa.append((f"إيه أنظمة السداد في {name}؟", pay))
        qa.append((f"إيه أنواع الوحدات والمساحات في {name}؟", f"{size_list}."))
        qa.append((f"إمتى استلام {name}؟", f'الاستلام {"يبدأ من " if p["name"] == "PX" else "في "}{p["delivery"]} حسب المطوّر.'))
    else:
        qa.append((f"Where is {name} located?", f'{p["location"]["text"]["en"]} It is developed by Palm Hills Developments.'))
        qa.append((f"What are the starting prices in {name}?",
                   f'Prices start from EGP {money(p["price_from"])}. Available units: {price_list}.'))
        pay = f'{p["down"]}% down payment with installments over up to {p["years"]} years.'
        if disc:
            pay += f' A discount of up to {disc["pct"]}% is available on the {disc["years"]}-year plan.'
        if launch:
            pay += f' The {launch["name"]} phase: {launch["down"]}% down payment over up to {launch["years"]} years.'
        qa.append((f"What payment plans are available in {name}?", pay))
        qa.append((f"What unit types and sizes are available in {name}?", f"{size_list}."))
        qa.append((f"When is {name} delivered?", f'Delivery {"starts in" if p["name"] == "PX" else "is in"} {p["delivery"]}, according to the developer.'))
    all_units = units + (launch["units"] if launch else [])
    fin = {u.get("finish") for u in all_units}
    if fin == {"ff"}:
        qa.append((f"هل وحدات {name} متشطبة؟", "أيوه، كل الوحدات المعروضة متشطبة بالكامل.") if ar else
                  (f"Are {name} homes finished?", "Yes, all the units shown are delivered fully finished."))
    elif launch and {"ff", "cs"} <= {u.get("finish") for u in launch["units"]}:
        qa.append((f"هل وحدات {launch['name']} متشطبة؟",
                   f"التاون هاوس في {launch['name']} متشطب بالكامل، والفيلات Core & Shell.") if ar else
                  (f"Are {launch['name']} homes finished?",
                   f"Town houses in {launch['name']} are fully finished; villas are delivered Core & Shell."))
    qa.append((f"هل VIBE Real Estate هي المطوّر بتاع {name}؟",
               "لا. المطوّر هو Palm Hills Developments. VIBE Real Estate وسيط عقاري مستقل بيعرض المشروع وبيساعدك تختار الوحدة، والتعاقد بيتم مع المطوّر مباشرة.") if ar else
              (f"Is VIBE Real Estate the developer of {name}?",
               "No. The developer is Palm Hills Developments. VIBE Real Estate is an independent broker that presents the project and helps you choose a unit; contracts are signed directly with the developer."))
    qa.append(("هل الأسعار المعروضة نهائية؟",
               "الأسعار استرشادية وقابلة للتغيير من المطوّر دون إشعار مسبق، والمرجع النهائي هو المطوّر وقت التعاقد.") if ar else
              ("Are the prices shown final?",
               "Prices are indicative and may be changed by the developer without notice. The developer is the final reference at the time of contracting."))
    return qa


def jsonld(slug, p, lang, t):
    page = url(slug, lang, True)
    org = SITE["domain"] + "/#organization"
    hero = SITE["domain"] + img(p["img"], p["hero"]) if p.get("hero") else SITE["domain"] + img("px", "lagoon")
    graph = [
        {"@type": "RealEstateAgent", "@id": org, "name": SITE["brand"], "url": SITE["domain"] + "/",
         "telephone": SITE["tel_intl"], "image": hero,
         "address": {"@type": "PostalAddress", "addressLocality": "Cairo", "addressCountry": "EG"}},
        {"@type": "WebPage", "@id": page + "#webpage", "url": page, "name": p["seo"][lang]["title"],
         "description": p["seo"][lang]["desc"], "inLanguage": lang,
         "primaryImageOfPage": hero,
         "publisher": {"@id": org}, "breadcrumb": {"@id": page + "#breadcrumb"}},
        {"@type": "BreadcrumbList", "@id": page + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t["crumb_home"], "item": url("", lang, True)},
            {"@type": "ListItem", "position": 2, "name": HUB[lang]["crumb"], "item": url(HUB_SLUG, lang, True)},
            {"@type": "ListItem", "position": 3, "name": p["title"], "item": page}]},
        {"@type": "ApartmentComplex", "@id": page + "#project", "name": p["title"], "url": page,
         "description": p["about"][lang][0], "image": hero,
         "address": {"@type": "PostalAddress", "addressLocality": p["area"]["en"], "addressRegion": "Giza", "addressCountry": "EG"}},
        {"@type": "FAQPage", "@id": page + "#faq", "inLanguage": lang, "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in project_faq(p, lang, t)]},
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)


OG_DEFAULT = "/assets/img/projects/palm-parks/og.jpg"   # share image for the home page and pages without a hero


def og_path(p):
    return f'/assets/img/projects/{p["img"]}/og.jpg' if p.get("hero") else OG_DEFAULT


def build_og():
    """1200x630 JPG share images (WhatsApp / Facebook / X previews) cropped from each project's hero.
    Needs Pillow; skipped quietly when it is not installed (the committed files are then reused)."""
    try:
        from PIL import Image
    except ImportError:
        print("og images: Pillow not installed, keeping existing files")
        return
    for slug, p in PROJECTS.items():
        if not p.get("hero"):
            continue
        src = os.path.join(ROOT, "assets", "img", "projects", p["img"], p["hero"] + ".webp")
        dst = os.path.join(ROOT, "assets", "img", "projects", p["img"], "og.jpg")
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            continue
        im = Image.open(src).convert("RGB")
        w, h = im.size
        scale = max(1200 / w, 630 / h)
        im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
        w, h = im.size
        left, top = (w - 1200) // 2, (h - 630) // 2
        im.crop((left, top, left + 1200, top + 630)).save(dst, "JPEG", quality=84, optimize=True, progressive=True)
        print("built og image for", slug)


def head(title, desc, canonical, alternates, lang, t, og_img=None, robots="max-image-preview:large", preload=None, ld=None):
    alt = "".join(f'<link rel="alternate" hreflang="{h}" href="{u}">\n' for h, u in alternates)
    og_img = og_img or SITE["domain"] + OG_DEFAULT
    og = (f'<meta property="og:image" content="{og_img}">\n<meta property="og:image:type" content="image/jpeg">\n'
          f'<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
          f'<meta property="og:image:alt" content="{esc(title)}">\n<meta name="twitter:card" content="summary_large_image">\n'
          f'<meta name="twitter:image" content="{og_img}">\n')
    pre = f'<link rel="preload" as="image" href="{preload}" fetchpriority="high">\n' if preload else ""
    ldtag = f'<script type="application/ld+json">\n{ld}\n</script>\n' if ld else ""
    return f'''<!DOCTYPE html>
<html lang="{lang}" dir="{t["dir"]}">
<head>
{gtm_head()}
<meta charset="UTF-8">
<title>{esc(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#092A21">
<link rel="canonical" href="{canonical}">
{alt}<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE["brand"]}">
<meta property="og:locale" content="{t["locale"]}">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
{og}<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/assets/img/brand/favicon.svg" type="image/svg+xml">
<link rel="preload" as="font" type="font/woff2" crossorigin href="/assets/fonts/almarai-700-{"ar" if lang == "ar" else "latin"}.woff2">
{pre}<link rel="stylesheet" href="/assets/css/project.css?v={ASSET_V}">
{ldtag}</head>
<body>
{gtm_body()}
'''


def project_page(slug, lang):
    p, t = PROJECTS[slug], T[lang]
    title = p["title"]
    alternates = [("ar", url(slug, "ar", True)), ("en", url(slug, "en", True)), ("x-default", url(slug, "ar", True))]
    hero_img = img(p["img"], p["hero"]) if p.get("hero") else None
    has_gallery = len(p.get("gallery", [])) >= 2
    cfg = {
        "lang": lang, "project": p["name"], "projectName": title, "endpoint": SITE["endpoint"],
        "thankYou": url("thank-you", lang),
        "wa": SITE["wa"],
           "t": {"submit": t["f_submit"], "sending": t["f_sending"], "noCountry": t["no_country"], "close": t["close"],
                 "waMsg": t["wa_msg"], "waMsgGeneric": t["wa_msg_generic"]},
    }
    nav_links = "".join(f'<a href="{h}">{esc(x)}</a>' for h, x in t["nav"] if has_gallery or h != "#gallery")
    disc = p["discount"]
    offer_badge = (f'<div class="hero-offer">{ic("tag")} {esc(t["offer_badge"].format(p=disc["pct"], y=disc["years"]))}</div>' if disc else "")
    millions = f'{p["price_from"] / 1e6:.1f}'

    feats = "".join(
        f'<div class="feat"><div class="feat-ic">{ic(f["ic"])}</div><div><h3>{esc(f[lang][0])}</h3><p>{esc(f[lang][1])}</p></div></div>'
        for f in p["features"])
    facts = "".join(f'<div class="fact"><b class="num">{esc(f["v"])}</b><span>{esc(f[lang])}</span></div>' for f in p["facts"])
    about_ps = "".join(f"<p>{esc(x)}</p>" for x in p["about"][lang])
    faq_html = "".join(f'<details class="faq"><summary>{esc(q)}{ic("chev-d")}</summary><p>{esc(a_)}</p></details>'
                       for q, a_ in project_faq(p, lang, t))

    unit_cards = [unit_card(p, u, lang, t, title) for u in p["units"]]
    launch_html = ""
    if p.get("launch"):
        L = p["launch"]
        launch_cards = "".join(unit_card(p, u, lang, t, title, launch=L) for u in L["units"])
        launch_html = f'''
  <div class="launch" id="launch">
   <div class="launch-head">
    <div class="eyebrow">{esc(t["launch_eyebrow"])}</div>
    <h3>{esc(t["launch_h"].format(n=L["name"]))}</h3>
    <p>{esc(L["intro"][lang])}</p>
    <span class="launch-pay">{ic("tag")} {esc(t["launch_pay"].format(d=L["down"], y=L["years"]))}</span>
   </div>
   <div class="cards cards-3">{launch_cards}</div>
  </div>'''

    if disc:
        offer_h = t["offer_h"].format(p=disc["pct"], y=disc["years"])
        offer_p = t["offer_p"].format(d=p["down"], yy=p["years"])
    else:
        offer_h = t["plan_h"].format(d=p["down"], yy=p["years"])
        offer_p = t["plan_p"]

    loc = p["location"]
    loc_items = "".join(f'<div class="loc-item"><b>{esc(x["b"][lang])}</b><span>{esc(x["s"][lang])}</span></div>' for x in loc["points"])
    gallery = "".join(
        f'<figure data-lb="{img(p["img"], g["img"])}" data-lb-group="gallery" data-cap="{esc(g["cap"][lang])}">'
        f'<img src="{img(p["img"], g["img"])}" alt="{esc(g["cap"][lang])}" loading="lazy"><figcaption>{esc(g["cap"][lang])}</figcaption></figure>'
        for g in p.get("gallery", []))
    points = "".join(f"<li>{ic('check')} {esc(x)}</li>" for x in t["final_points"])
    prev_i, next_i = ("chev-r", "chev-l") if t["dir"] == "rtl" else ("chev-l", "chev-r")

    gallery_sec = f'''<section class="sec" id="gallery">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(t["gal_eyebrow"])}</div><h2>{esc(t["gal_h"])}</h2><p>{esc(t["gal_p"].format(t=title))}</p></div>
  <div class="car gal">
   <button class="car-btn prev" type="button" aria-label="prev">{ic(prev_i)}</button>
   <div class="car-track">{gallery}</div>
   <button class="car-btn next" type="button" aria-label="next">{ic(next_i)}</button>
   <div class="car-dots"></div>
  </div>
 </div>
</section>''' if has_gallery else ""
    loc_map = (f'''<div>
    <div class="loc-map" data-lb="{img(p["img"], loc["map"])}" data-lb-group="map" data-cap="{esc(loc["map_cap"][lang])}"><img src="{img(p["img"], loc["map"])}" alt="{esc(title)} master plan" loading="lazy"></div>
    <p class="loc-cap">{esc(loc["map_cap"][lang])}</p>
   </div>''' if loc.get("map") else "")

    html = head(p["seo"][lang]["title"], p["seo"][lang]["desc"], url(slug, lang, True), alternates, lang, t,
                og_img=SITE["domain"] + og_path(p), preload=hero_img, ld=jsonld(slug, p, lang, t))
    html += f'''{lang_bar(slug, lang, t)}
<header class="nav">
 <div class="wrap">
  <a class="logo" href="{url("", lang)}" aria-label="VIBE Real Estate"><strong>VIBE <span>Real Estate</span></strong><small>Luxury Properties</small></a>
  <nav class="nav-links" aria-label="{esc(t["menu"])}">{nav_links}</nav>
  <button class="btn btn-cta" type="button" data-cta="nav">{ic("whatsapp")} {esc(t["nav_cta"])}</button>
  {lang_toggle(slug, lang)}
  <button class="nav-burger" type="button" aria-label="{esc(t["menu"])}" aria-expanded="false">{ic("bars")}</button>
 </div>
</header>

<main>
<section class="hero{"" if hero_img else " hero-plain"}">
 {f'<img class="hero-bg" src="{hero_img}" alt="{esc(title)}" fetchpriority="high">' if hero_img else ""}
 <div class="hero-in">
  <div class="eyebrow">VIBE Real Estate</div>
  <h1><span class="ltr">{esc(title)}</span></h1>
  <p class="hero-sub">{esc(p["hero_sub"][lang])}</p>
  {offer_badge}
  <div class="hero-stats">
   <div class="hero-stat"><b>{p["down"]}%</b><span>{esc(t["down"])}</span></div>
   <div class="hero-stat"><b>{p["years"]}</b><span>{esc(t["years"])}</span></div>
   <div class="hero-stat"><b>{millions}</b><span>{esc(t["from_m"])}</span></div>
  </div>
  <button class="btn btn-cta btn-lg" type="button" data-cta="hero">{ic("whatsapp")} {esc(t["cta_main"])}</button>
  <p class="hero-note">{esc(t["hero_note"])}</p>
 </div>
</section>

<section class="sec" id="units">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(t["units_eyebrow"])}</div><h2>{esc(t["units_h"].format(t=title))}</h2><p>{esc(t["units_p"])}</p></div>
  <div class="cards{" cards-3" if len(unit_cards) == 3 else ""}">
   {"".join(unit_cards)}
  </div>
  {launch_html}
  <div class="offer">
   <div><h3>{offer_h}</h3><p>{esc(offer_p)}</p></div>
   <div><button class="btn btn-cta btn-lg" type="button" data-cta="offer">{ic("whatsapp")} {esc(t["offer_cta"])}</button></div>
  </div>
  <p class="disclaimer">{ic("info")}<span>{esc(t["units_disc"])}</span></p>
 </div>
</section>

<section class="sec sec-white" id="about">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(t["about_eyebrow"])}</div><h2>{esc(t["about_h"].format(t=title))}</h2><p>{esc(t["about_p"])}</p></div>
  <div class="about{"" if p.get("about_img") else " about-solo"}">
   <div class="about-text">{about_ps}<div class="about-facts">{facts}</div></div>
   {f'<div class="about-img"><img src="{img(p["img"], p["about_img"])}" alt="{esc(title)}" loading="lazy"></div>' if p.get("about_img") else ""}
  </div>
  <div class="feats">{feats}</div>
 </div>
</section>

<section class="sec sec-dark" id="location">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(t["loc_eyebrow"])}</div><h2>{esc(t["loc_h"].format(t=title))}</h2><p>{esc(t["loc_p"])}</p></div>
  <div class="loc{"" if loc.get("map") else " loc-solo"}">
   <div><p class="loc-text">{esc(loc["text"][lang])}</p><div class="loc-list">{loc_items}</div></div>
   {loc_map}
  </div>
 </div>
</section>

{gallery_sec}
<section class="sec sec-white" id="more">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(t["more_eyebrow"])}</div><h2>{esc(t["more_h"])}</h2><p>{esc(t["more_p"].format(t=title))}</p></div>
  <div class="car others">
   <button class="car-btn prev" type="button" aria-label="prev">{ic(prev_i)}</button>
   <div class="car-track">
   {other_cards(slug, lang, t)}
   </div>
   <button class="car-btn next" type="button" aria-label="next">{ic(next_i)}</button>
   <div class="car-dots"></div>
  </div>
  <p style="text-align:center;margin-top:22px"><a class="hub-link" href="{url(HUB_SLUG, lang)}">{esc(HUB[lang]["link"])} {ic("arrow-l" if t["dir"] == "rtl" else "arrow-r")}</a></p>
 </div>
</section>

<section class="sec" id="faq">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(t["faq_eyebrow"])}</div><h2>{esc(t["faq_h_project"].format(t=title))}</h2></div>
  <div class="faqs">{faq_html}</div>
 </div>
</section>

<section class="sec sec-dark" id="contact">
 <div class="wrap">
  <div class="final">
   <div>
    <div class="eyebrow">VIBE Real Estate</div>
    <h2>{t["final_h"].format(t='<span class="ltr">' + esc(title) + '</span>')}</h2>
    <p class="final-lead">{esc(t["final_lead"])}</p>
    <ul class="final-points">{points}</ul>
    <a class="final-call" href="tel:{SITE["tel"]}" data-track="call_click" data-loc="final">{ic("phone")} {esc(t["final_call"])}<span class="ltr">{SITE["tel"]}</span></a>
   </div>
   <div class="final-card">
    <h3>{esc(t["final_form_h"])}</h3>
    {lead_form(p, t, "final_form", inline=True, uid="f")}
   </div>
  </div>
 </div>
</section>
</main>

{footer(lang, t)}

<div class="stick" role="region" aria-label="{esc(t["stick_cta"])}">
 <div class="stick-txt"><small>{esc(title)} — {esc(t["stick_from"])}</small><b>{money(p["price_from"])}</b> <small style="display:inline">{esc(t["egp"])}</small></div>
 <button class="btn btn-cta" type="button" data-cta="sticky_bar">{ic("whatsapp")} {esc(t["stick_cta"])}</button>
</div>

<div class="modal" id="leadModal" role="dialog" aria-modal="true" aria-labelledby="leadTitle">
 <div class="modal-box">
  <button class="modal-x" type="button" data-modal-close aria-label="{esc(t["close"])}">{ic("x")}</button>
  <div class="modal-head">
   <div class="modal-wa">{ic("whatsapp")}</div>
   <h2 id="leadTitle">{esc(t["f_title"])}</h2>
   <p>{esc(t["f_sub"])}</p>
   <span class="modal-ctx"></span>
  </div>
  <div class="modal-body">{lead_form(p, t, "modal", uid="m")}</div>
 </div>
</div>

{cookie(t)}

<script>window.VIBE={json.dumps(cfg, ensure_ascii=False)};</script>
<script src="/assets/js/countries.js?v={ASSET_V}" defer></script>
<script src="/assets/js/project.js?v={ASSET_V}" defer></script>
</body>
</html>
'''
    return html


def compare_table(lang, t):
    """Side-by-side table of every ready project: unit types, starting price, payment plan, delivery, offer."""
    rows = ""
    for sl, o in PROJECTS.items():
        if not o.get("ready"):
            continue
        offer = t["cmp_off"].format(p=o["discount"]["pct"]) if o["discount"] else t["cmp_none"]
        c = t["cmp_cols"]
        rows += (f'<tr><th scope="row"><a href="{url(sl, lang)}">{esc(o["title"])}</a></th>'
                 f'<td data-l="{esc(c[1])}">{esc(" · ".join(o["types"][lang]))}</td>'
                 f'<td data-l="{esc(c[2])}"><span><b class="num">{money(o["price_from"])}</b> {esc(t["egp"])}</span></td>'
                 f'<td data-l="{esc(c[3])}">{o["down"]}%</td><td data-l="{esc(c[4])}">{esc(t["cmp_years"].format(y=o["years"]))}</td>'
                 f'<td data-l="{esc(c[5])}">{o["delivery"]}</td><td data-l="{esc(c[6])}">{esc(offer)}</td></tr>')
    cmp_head = "".join(f'<th scope="col">{esc(x)}</th>' for x in t["cmp_cols"])
    return f'<div class="cmp"><table><thead><tr>{cmp_head}</tr></thead><tbody>{rows}</tbody></table></div>'


def home_page(lang):
    t = T[lang]
    alternates = [("ar", url("", "ar", True)), ("en", url("", "en", True)), ("x-default", url("", "ar", True))]
    hero_img = img("palm-parks", "hero")
    cfg = {"lang": lang, "project": "", "projectName": SITE["brand"], "pickProject": True, "backTitle": t["home_back"],
           "endpoint": SITE["endpoint"], "thankYou": url("thank-you", lang),
           "wa": SITE["wa"],
           "t": {"submit": t["f_submit"], "sending": t["f_sending"], "noCountry": t["no_country"], "close": t["close"],
                 "waMsg": t["wa_msg"], "waMsgGeneric": t["wa_msg_generic"]}}
    nav_links = "".join(f'<a href="{url(HUB_SLUG, lang) if h == "#compare" else h}">{esc(x)}</a>' for h, x in t["home_nav"])
    stats = "".join(f'<div class="hero-stat"><b>{esc(v)}</b><span>{esc(k)}</span></div>' for v, k in t["home_stats"])
    arrow = ic("arrow-l" if t["dir"] == "rtl" else "arrow-r")
    more = "".join(f'''<a class="card" href="{m["href"]}" data-track="project_switch" data-loc="home_more" data-target="{esc(m["title"])}">
    <div class="card-media"><img src="{img("home", m["img"])}" alt="{esc(m["title"])}" loading="lazy" style="width:100%;height:100%;object-fit:cover"><span class="card-tag">{ic("pin")} {esc(m["tag"])}</span></div>
    <div class="card-body"><h3 class="card-name">{esc(m["title"])}</h3><p class="card-sub" style="margin:6px 0 14px">{esc(m["text"])}</p>
     <span class="card-more" style="margin-top:auto">{esc(t["home_explore"])} {arrow}</span></div>
   </a>''' for m in t["home_more"])
    vibe = "".join(f'<div class="vibe"><b>{l}</b><h3>{esc(n)}</h3><p>{esc(d)}</p></div>' for l, n, d in t["home_vibe"])
    about_ps = "".join(f"<p>{esc(x)}</p>" for x in t["home_about"])
    dev_stats = "".join(f'<div class="dstat"><b>{esc(v)}</b><span>{esc(k)}</span></div>' for v, k in t["dev_stats"])
    why = "".join(f'<div class="feat"><div class="feat-ic">{ic(i)}</div><div><h3>{esc(h)}</h3><p>{esc(d)}</p></div></div>' for i, h, d in t["why"])
    faq = "".join(f'<details class="faq"><summary>{esc(q)}{ic("chev-d")}</summary><p>{esc(a_)}</p></details>' for q, a_ in t["faq"])
    faq_ld = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a_}} for q, a_ in t["faq"]]}
    items = [{"@type": "ListItem", "position": i + 1, "name": o["title"], "url": url(s, lang, True)}
             for i, (s, o) in enumerate(PROJECTS.items()) if o.get("ready")]
    org = SITE["domain"] + "/#organization"
    ld = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "RealEstateAgent", "@id": org, "name": SITE["brand"], "url": SITE["domain"] + "/", "telephone": SITE["tel_intl"],
         "image": SITE["domain"] + hero_img, "address": {"@type": "PostalAddress", "addressLocality": "Cairo", "addressCountry": "EG"}},
        {"@type": "WebSite", "@id": SITE["domain"] + "/#website", "url": SITE["domain"] + "/", "name": SITE["brand"], "inLanguage": ["ar", "en"], "publisher": {"@id": org}},
        {"@type": "ItemList", "name": t["home_h1"], "itemListElement": items}, faq_ld]}, ensure_ascii=False, indent=1)
    html = head(t["home_seo_title"], t["home_seo_desc"], url("", lang, True), alternates, lang, t,
                preload=hero_img, ld=ld)
    html += f'''{lang_bar("", lang, t)}
<header class="nav">
 <div class="wrap">
  <a class="logo" href="{url("", lang)}" aria-label="VIBE Real Estate"><strong>VIBE <span>Real Estate</span></strong><small>Luxury Properties</small></a>
  <nav class="nav-links" aria-label="{esc(t["menu"])}">{nav_links}</nav>
  <button class="btn btn-cta" type="button" data-cta="nav">{ic("whatsapp")} {esc(t["home_nav_cta"])}</button>
  {lang_toggle("", lang)}
  <button class="nav-burger" type="button" aria-label="{esc(t["menu"])}" aria-expanded="false">{ic("bars")}</button>
 </div>
</header>

<main>
<section class="hero">
 <img class="hero-bg" src="{hero_img}" alt="Palm Hills" fetchpriority="high">
 <div class="hero-in">
  <div class="eyebrow">{esc(t["home_eyebrow"])}</div>
  <h1 class="hero-h1-ar">{esc(t["home_h1"])}</h1>
  <p class="hero-sub">{esc(t["home_sub"])}</p>
  <div class="hero-stats">{stats}</div>
  <div class="hero-btns">
   <a class="btn btn-cta btn-lg" href="#projects">{esc(t["home_cta2"])}</a>
   <a class="btn btn-ghost" href="#about">{esc(t["home_nav"][0][1])}</a>
  </div>
 </div>
</section>

<section class="sec sec-white" id="about">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(t["home_about_eyebrow"])}</div><h2>{esc(t["home_about_h"])}</h2></div>
  <div class="home-about">{about_ps}</div>
  <div class="vibes">{vibe}</div>
  <p style="text-align:center;margin-top:26px"><a class="btn btn-dark" style="width:auto;padding:12px 26px;border-radius:100px" href="{url("about-us", lang)}">{esc(t["home_about_link"])} {arrow}</a></p>
 </div>
</section>

<section class="sec" id="projects">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(t["home_proj_eyebrow"])}</div><h2>{esc(t["home_proj_h"])}</h2><p>{esc(t["home_proj_p"])}</p></div>
  <div class="cards cards-3 others">
   {other_cards(None, lang, t)}
  </div>
  <p style="text-align:center;margin-top:26px"><a class="btn btn-dark" style="width:auto;padding:12px 26px;border-radius:100px" href="{url(HUB_SLUG, lang)}">{esc(HUB[lang]["link"])} {arrow}</a></p>
  <p class="disclaimer">{ic("info")}<span>{esc(t["units_disc"])}</span></p>
 </div>
</section>

<section class="sec sec-dark" id="developer">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(t["dev_eyebrow"])}</div><h2>{esc(t["dev_h"])}</h2><p>{esc(t["dev_p"])}</p></div>
  <div class="dstats">{dev_stats}</div>
  <h3 class="sub-h">{esc(t["why_h"])}</h3>
  <div class="feats feats-2">{why}</div>
 </div>
</section>

<section class="sec" id="faq">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(t["faq_eyebrow"])}</div><h2>{esc(t["faq_h"])}</h2></div>
  <div class="faqs">{faq}</div>
  <div class="soft">
   <div><h3>{esc(t["soft_h"])}</h3><p>{esc(t["soft_p"])}</p></div>
   <button class="btn btn-cta" type="button" data-cta="contact_strip">{ic("whatsapp")} {esc(t["soft_cta"])}</button>
  </div>
 </div>
</section>
</main>

{footer(lang, t)}

<div class="modal" id="leadModal" role="dialog" aria-modal="true" aria-labelledby="leadTitle">
 <div class="modal-box">
  <button class="modal-x" type="button" data-modal-close aria-label="{esc(t["close"])}">{ic("x")}</button>
  <div class="modal-head">
   <div class="modal-wa">{ic("whatsapp")}</div>
   <h2 id="leadTitle">{esc(t["f_title"])}</h2>
   <p>{esc(t["f_sub"])}</p>
   <span class="modal-ctx"></span>
  </div>
  <div class="modal-body">{lead_form(None, t, "modal", uid="m")}</div>
 </div>
</div>

{cookie(t)}

<script>window.VIBE={json.dumps(cfg, ensure_ascii=False)};</script>
<script src="/assets/js/countries.js?v={ASSET_V}" defer></script>
<script src="/assets/js/project.js?v={ASSET_V}" defer></script>
</body>
</html>
'''
    return html


GROUP_KEYS = (("Apartment",), ("Family Home", "Town"), ("Twin", "Villa"))


def hub_groups(lang):
    """For each home-type group: the projects that have it and their lowest price for that type."""
    out = []
    for keys in GROUP_KEYS:
        rows = []
        for slug, p in PROJECTS.items():
            if not p.get("ready"):
                continue
            units = p["units"] + (p["launch"]["units"] if p.get("launch") else [])
            prices = [u["price"] for u in units if u.get("price") and any(k.lower() in u["name"].lower() for k in keys)]
            if prices:
                rows.append((slug, p, min(prices)))
        out.append(sorted(rows, key=lambda r: r[2]))
    return out


def hub_faq(lang, t):
    ar = lang == "ar"
    ps = [(s, p) for s, p in PROJECTS.items() if p.get("ready")]
    low_s, low = min(ps, key=lambda x: x[1]["price_from"])
    sep = "؛ " if ar else "; "
    groups = hub_groups(lang)
    names = lambda g: ("، " if ar else ", ").join(r[1]["title"] for r in g)
    if ar:
        return [
            ("إيه مشاريع بالم هيلز أكتوبر المتاحة؟",
             sep.join(f'{p["title"]} ({"، ".join(p["types"]["ar"])})' for _, p in ps) + ". كلها من تطوير Palm Hills Developments."),
            ("أسعار بالم هيلز أكتوبر بتبدأ من كام؟",
             f'الأسعار بتبدأ من {money(low["price_from"])} جنيه في {low["title"]}. بداية كل مشروع: '
             + sep.join(f'{p["title"]} من {money(p["price_from"])} جنيه' for _, p in ps) + "."),
            ("إيه أنظمة السداد في مشاريع بالم هيلز أكتوبر؟",
             "المقدم 5% في كل المشاريع المعروضة. التقسيط: " + sep.join(f'{p["title"]} حتى {p["years"]} سنوات' for _, p in ps) + "."),
            ("إمتى الاستلام؟", sep.join(f'{p["title"]} {p["delivery"]}' for _, p in ps) + "، حسب المطوّر."),
            ("فين ألاقي شقق وفين ألاقي فيلات؟",
             f"الشقق في {names(groups[0])}. الـFamily Homes والتاون هاوس في {names(groups[1])}. التوين هاوس والفيلات في {names(groups[2])}."),
            ("هل VIBE Real Estate هي المطوّر؟",
             "لا. المطوّر هو Palm Hills Developments. VIBE Real Estate وسيط عقاري مستقل بيعرض المشاريع وبيساعدك تقارن وتختار، والتعاقد بيتم مع المطوّر مباشرة."),
            ("هل الأسعار المعروضة نهائية؟",
             "الأسعار استرشادية وقابلة للتغيير من المطوّر دون إشعار مسبق، والمرجع النهائي هو المطوّر وقت التعاقد."),
        ]
    return [
        ("Which Palm Hills October projects are available?",
         sep.join(f'{p["title"]} ({", ".join(p["types"]["en"]).lower()})' for _, p in ps) + ". All are developed by Palm Hills Developments."),
        ("What are the starting prices in Palm Hills October?",
         f'Prices start from EGP {money(low["price_from"])} in {low["title"]}. By project: '
         + sep.join(f'{p["title"]} from EGP {money(p["price_from"])}' for _, p in ps) + "."),
        ("What payment plans are available?",
         "The down payment is 5% in every project shown. Installments: " + sep.join(f'{p["title"]} up to {p["years"]} years' for _, p in ps) + "."),
        ("When is delivery?", sep.join(f'{p["title"]} {p["delivery"]}' for _, p in ps) + ", according to the developer."),
        ("Where can I find apartments, and where villas?",
         f"Apartments are in {names(groups[0])}. Family homes and town houses are in {names(groups[1])}. Twin houses and villas are in {names(groups[2])}."),
        ("Is VIBE Real Estate the developer?",
         "No. The developer is Palm Hills Developments. VIBE Real Estate is an independent broker that presents the projects and helps you compare and choose; contracts are signed directly with the developer."),
        ("Are the prices shown final?",
         "Prices are indicative and may be changed by the developer without notice. The developer is the final reference at the time of contracting."),
    ]


def hub_page(lang):
    """Palm Hills October hub: every project, a comparison, a by-type guide, the area and an FAQ."""
    t, h = T[lang], HUB[lang]
    ps = [(s, p) for s, p in PROJECTS.items() if p.get("ready")]
    n, low = len(ps), min(p["price_from"] for _, p in ps)
    alternates = [("ar", url(HUB_SLUG, "ar", True)), ("en", url(HUB_SLUG, "en", True)), ("x-default", url(HUB_SLUG, "ar", True))]
    hero_img = img("crown-extension", "hero")
    page = url(HUB_SLUG, lang, True)
    cfg = {"lang": lang, "project": "", "projectName": h["final_name"], "pickProject": True, "backTitle": h["back"],
           "endpoint": SITE["endpoint"], "thankYou": url("thank-you", lang), "wa": SITE["wa"],
           "t": {"submit": t["f_submit"], "sending": t["f_sending"], "noCountry": t["no_country"], "close": t["close"],
                 "waMsg": t["wa_msg"], "waMsgGeneric": t["wa_msg_generic"]}}
    nav_links = "".join(f'<a href="{hh}">{esc(x)}</a>' for hh, x in h["nav"])
    stats = "".join(f'<div class="hero-stat"><b>{esc(v.format(n=n))}</b><span>{esc(k)}</span></div>' for v, k in h["stats"])
    arrow = ic("arrow-l" if t["dir"] == "rtl" else "arrow-r")
    guide = ""
    for (icon, name, text), rows in zip(h["groups"], hub_groups(lang)):
        items = "".join(
            f'<li><a href="{url(s, lang)}" data-track="project_switch" data-loc="hub_guide" data-target="{esc(p["name"])}">'
            f'<span>{esc(p["title"])}</span><small>{esc(h["from"])} <b class="num">{money(pr)}</b> {esc(t["egp"])}</small></a></li>'
            for s, p, pr in rows)
        guide += (f'<div class="guide"><div class="feat-ic">{ic(icon)}</div><h3>{esc(name)}</h3><p>{esc(text)}</p>'
                  f'<ul>{items}</ul></div>')
    area = "".join(f'<div class="feat"><div class="feat-ic">{ic(i)}</div><div><h3>{esc(a)}</h3><p>{esc(d)}</p></div></div>' for i, a, d in h["area"])
    qa = hub_faq(lang, t)
    faq = "".join(f'<details class="faq"><summary>{esc(q)}{ic("chev-d")}</summary><p>{esc(a_)}</p></details>' for q, a_ in qa)
    points = "".join(f"<li>{ic('check')} {esc(x)}</li>" for x in t["final_points"])
    org = SITE["domain"] + "/#organization"
    desc = h["seo_desc"].format(price=money(low))
    ld = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "RealEstateAgent", "@id": org, "name": SITE["brand"], "url": SITE["domain"] + "/", "telephone": SITE["tel_intl"],
         "image": SITE["domain"] + hero_img, "address": {"@type": "PostalAddress", "addressLocality": "Cairo", "addressCountry": "EG"}},
        {"@type": "CollectionPage", "@id": page + "#webpage", "url": page, "name": h["seo_title"], "description": desc,
         "inLanguage": lang, "publisher": {"@id": org}, "breadcrumb": {"@id": page + "#breadcrumb"}},
        {"@type": "BreadcrumbList", "@id": page + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t["crumb_home"], "item": url("", lang, True)},
            {"@type": "ListItem", "position": 2, "name": h["crumb"], "item": page}]},
        {"@type": "ItemList", "name": h["h1"], "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": p["title"], "url": url(s, lang, True)} for i, (s, p) in enumerate(ps)]},
        {"@type": "FAQPage", "@id": page + "#faq", "inLanguage": lang, "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a_}} for q, a_ in qa]},
    ]}, ensure_ascii=False, indent=1)
    html = head(h["seo_title"], desc, page, alternates, lang, t,
                og_img=SITE["domain"] + og_path(PROJECTS["crown-extension"]), preload=hero_img, ld=ld)
    html += f'''{lang_bar(HUB_SLUG, lang, t)}
<header class="nav">
 <div class="wrap">
  <a class="logo" href="{url("", lang)}" aria-label="VIBE Real Estate"><strong>VIBE <span>Real Estate</span></strong><small>Luxury Properties</small></a>
  <nav class="nav-links" aria-label="{esc(t["menu"])}">{nav_links}</nav>
  <button class="btn btn-cta" type="button" data-cta="nav">{ic("whatsapp")} {esc(h["nav_cta"])}</button>
  {lang_toggle(HUB_SLUG, lang)}
  <button class="nav-burger" type="button" aria-label="{esc(t["menu"])}" aria-expanded="false">{ic("bars")}</button>
 </div>
</header>

<main>
<section class="hero">
 <img class="hero-bg" src="{hero_img}" alt="{esc(h["h1"])}" fetchpriority="high">
 <div class="hero-in">
  <div class="eyebrow">{esc(h["eyebrow"])}</div>
  <h1 class="hero-h1-ar">{esc(h["h1"])}</h1>
  <p class="hero-sub">{esc(h["sub"].format(n=n, price=money(low)))}</p>
  <div class="hero-stats">{stats}</div>
  <div class="hero-btns">
   <button class="btn btn-cta btn-lg" type="button" data-cta="hero">{ic("whatsapp")} {esc(t["cta_main"])}</button>
   <a class="btn btn-ghost" href="#projects">{esc(h["cta"])}</a>
  </div>
 </div>
</section>

<section class="sec" id="projects">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(h["proj_eyebrow"])}</div><h2>{esc(h["proj_h"])}</h2><p>{esc(h["proj_p"])}</p></div>
  <div class="cards cards-3 others">
   {other_cards(None, lang, t)}
  </div>
  <p class="disclaimer">{ic("info")}<span>{esc(t["units_disc"])}</span></p>
 </div>
</section>

<section class="sec sec-white" id="compare">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(t["cmp_eyebrow"])}</div><h2>{esc(t["cmp_h"])}</h2><p>{esc(t["cmp_p"])}</p></div>
  {compare_table(lang, t)}
 </div>
</section>

<section class="sec" id="guide">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(h["guide_eyebrow"])}</div><h2>{esc(h["guide_h"])}</h2><p>{esc(h["guide_p"])}</p></div>
  <div class="guides">{guide}</div>
 </div>
</section>

<section class="sec sec-dark" id="area">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(h["area_eyebrow"])}</div><h2>{esc(h["area_h"])}</h2><p>{esc(h["area_p"])}</p></div>
  <div class="feats feats-2">{area}</div>
 </div>
</section>

<section class="sec" id="faq">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(t["faq_eyebrow"])}</div><h2>{esc(h["faq_h"])}</h2></div>
  <div class="faqs">{faq}</div>
 </div>
</section>

<section class="sec sec-dark" id="contact">
 <div class="wrap">
  <div class="final">
   <div>
    <div class="eyebrow">VIBE Real Estate</div>
    <h2>{t["final_h"].format(t=esc(h["final_name"]))}</h2>
    <p class="final-lead">{esc(t["final_lead"])}</p>
    <ul class="final-points">{points}</ul>
    <a class="final-call" href="tel:{SITE["tel"]}" data-track="call_click" data-loc="final">{ic("phone")} {esc(t["final_call"])}<span class="ltr">{SITE["tel"]}</span></a>
   </div>
   <div class="final-card">
    <h3>{esc(t["final_form_h"])}</h3>
    {lead_form(None, t, "final_form", inline=True, uid="f")}
   </div>
  </div>
 </div>
</section>
</main>

{footer(lang, t)}

<div class="modal" id="leadModal" role="dialog" aria-modal="true" aria-labelledby="leadTitle">
 <div class="modal-box">
  <button class="modal-x" type="button" data-modal-close aria-label="{esc(t["close"])}">{ic("x")}</button>
  <div class="modal-head">
   <div class="modal-wa">{ic("whatsapp")}</div>
   <h2 id="leadTitle">{esc(t["f_title"])}</h2>
   <p>{esc(t["f_sub"])}</p>
   <span class="modal-ctx"></span>
  </div>
  <div class="modal-body">{lead_form(None, t, "modal", uid="m")}</div>
 </div>
</div>

{cookie(t)}

<script>window.VIBE={json.dumps(cfg, ensure_ascii=False)};</script>
<script src="/assets/js/countries.js?v={ASSET_V}" defer></script>
<script src="/assets/js/project.js?v={ASSET_V}" defer></script>
</body>
</html>
'''
    return html


def simple_shell(lang, t, slug, title, desc, body, robots="max-image-preview:large", ld=None, alternates=True):
    """Shared chrome for the About / Privacy / 404 pages: nav, footer, contact modal, cookie notice."""
    m = MISC[lang]
    alts = [("ar", url(slug, "ar", True)), ("en", url(slug, "en", True)), ("x-default", url(slug, "ar", True))] if alternates else []
    cfg = {"lang": lang, "project": "", "projectName": SITE["brand"], "pickProject": True, "backTitle": t["home_back"],
           "endpoint": SITE["endpoint"], "thankYou": url("thank-you", lang),
           "wa": SITE["wa"],
           "t": {"submit": t["f_submit"], "sending": t["f_sending"], "noCountry": t["no_country"], "close": t["close"],
                 "waMsg": t["wa_msg"], "waMsgGeneric": t["wa_msg_generic"]}}
    nav_links = "".join(f'<a href="{h}">{esc(x)}</a>' for h, x in m["nav"])
    html = head(title, desc, url(slug, lang, True), alts, lang, t, robots=robots, ld=ld)
    html += f'''{lang_bar(slug, lang, t) if alternates else ""}
<header class="nav">
 <div class="wrap">
  <a class="logo" href="{url("", lang)}" aria-label="VIBE Real Estate"><strong>VIBE <span>Real Estate</span></strong><small>Luxury Properties</small></a>
  <nav class="nav-links" aria-label="{esc(t["menu"])}">{nav_links}</nav>
  <button class="btn btn-cta" type="button" data-cta="nav">{ic("whatsapp")} {esc(t["home_nav_cta"])}</button>
  {lang_toggle(slug, lang) if alternates else ""}
  <button class="nav-burger" type="button" aria-label="{esc(t["menu"])}" aria-expanded="false">{ic("bars")}</button>
 </div>
</header>

<main>
{body}
</main>

{footer(lang, t)}

<div class="modal" id="leadModal" role="dialog" aria-modal="true" aria-labelledby="leadTitle">
 <div class="modal-box">
  <button class="modal-x" type="button" data-modal-close aria-label="{esc(t["close"])}">{ic("x")}</button>
  <div class="modal-head">
   <div class="modal-wa">{ic("whatsapp")}</div>
   <h2 id="leadTitle">{esc(t["f_title"])}</h2>
   <p>{esc(t["f_sub"])}</p>
   <span class="modal-ctx"></span>
  </div>
  <div class="modal-body">{lead_form(None, t, "modal", uid="m")}</div>
 </div>
</div>

{cookie(t)}

<script>window.VIBE={json.dumps(cfg, ensure_ascii=False)};</script>
<script src="/assets/js/countries.js?v={ASSET_V}" defer></script>
<script src="/assets/js/project.js?v={ASSET_V}" defer></script>
</body>
</html>
'''
    return html


def page_hero(eyebrow, h1, sub):
    return f'''<section class="hero hero-plain hero-sm">
 <div class="hero-in">
  <div class="eyebrow">{esc(eyebrow)}</div>
  <h1 class="hero-h1-ar">{esc(h1)}</h1>
  <p class="hero-sub">{esc(sub)}</p>
 </div>
</section>'''


def about_page(lang):
    t, a = T[lang], ABOUT[lang]
    arrow = ic("arrow-l" if t["dir"] == "rtl" else "arrow-r")
    intro = "".join(f"<p>{esc(x)}</p>" for x in a["intro"])
    letters = "".join(f'<div class="vibe"><b>{l}</b><h3>{esc(n)}</h3><p>{esc(d)}</p></div>' for l, n, d in a["letters"])
    values = "".join(f'<div class="feat"><div class="feat-ic">{ic(i)}</div><div><h3>{esc(h)}</h3><p>{esc(d)}</p></div></div>' for i, h, d in a["values"])
    body = f'''{page_hero(a["eyebrow"], a["h1"], a["sub"])}
<section class="sec sec-white">
 <div class="wrap"><div class="prose prose-center">{intro}</div></div>
</section>
<section class="sec sec-dark">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(a["name_eyebrow"])}</div><h2>{esc(a["name_h"])}</h2><p>{esc(a["name_p"])}</p></div>
  <div class="vibes">{letters}</div>
 </div>
</section>
<section class="sec">
 <div class="wrap">
  <div class="sec-head"><div class="eyebrow">{esc(a["values_eyebrow"])}</div><h2>{esc(a["values_h"])}</h2></div>
  <div class="feats" style="margin-top:0">{values}</div>
  <div class="mv">
   <div class="mv-card mv-dark"><h3>{esc(a["mission_h"])}</h3><p>{esc(a["mission"])}</p></div>
   <div class="mv-card"><h3>{esc(a["vision_h"])}</h3><p>{esc(a["vision"])}</p></div>
  </div>
  <p class="disclaimer">{ic("info")}<span>{esc(a["note"])}</span></p>
  <p style="text-align:center;margin-top:30px"><a class="btn btn-cta btn-lg" href="{url("", lang)}#projects">{esc(t["home_cta2"])} {arrow}</a></p>
 </div>
</section>'''
    org = SITE["domain"] + "/#organization"
    ld = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "RealEstateAgent", "@id": org, "name": SITE["brand"], "url": SITE["domain"] + "/", "telephone": SITE["tel_intl"],
         "description": a["seo_desc"], "address": {"@type": "PostalAddress", "addressLocality": "Cairo", "addressCountry": "EG"}},
        {"@type": "AboutPage", "url": url("about-us", lang, True), "name": a["seo_title"], "inLanguage": lang, "about": {"@id": org}}]},
        ensure_ascii=False, indent=1)
    return simple_shell(lang, t, "about-us", a["seo_title"], a["seo_desc"], body, ld=ld)


def privacy_page(lang):
    t, d = T[lang], PRIVACY[lang]
    out = [f"<p>{esc(d['intro'])}</p>"]
    for title, blocks in d["sections"]:
        out.append(f"<h2>{esc(title)}</h2>")
        for kind, val in blocks:
            if kind == "p":
                out.append(f"<p>{esc(val)}</p>")
            elif kind == "html":
                out.append(f"<p>{val}</p>")
            else:
                out.append("<ul>" + "".join(f"<li>{esc(x)}</li>" for x in val) + "</ul>")
    body = f'''{page_hero(d["eyebrow"], d["h1"], d["sub"])}
<section class="sec sec-white">
 <div class="wrap">
  <div class="prose">
   {"".join(out)}
   <div class="prose-box"><h3>{esc(d["contact_h"])}</h3><p>{esc(d["contact_p"])}</p><p><a class="ltr" href="mailto:{PRIVACY_EMAIL}">{PRIVACY_EMAIL}</a></p></div>
   <p class="prose-date">{esc(d["updated"])}</p>
  </div>
 </div>
</section>'''
    return simple_shell(lang, t, "privacy-policy", d["seo_title"], d["seo_desc"], body)


def not_found_page():
    """Single bilingual-agnostic 404 (Arabic, the site default)."""
    lang = "ar"
    t, m = T[lang], MISC[lang]
    body = f'''<section class="hero hero-plain">
 <div class="hero-in">
  <div class="eyebrow">404</div>
  <h1 class="hero-h1-ar">{esc(m["nf_h"])}</h1>
  <p class="hero-sub">{esc(m["nf_p"])}</p>
  <div class="hero-btns" style="margin-top:26px">
   <a class="btn btn-cta btn-lg" href="/">{esc(m["nf_cta"])}</a>
   <a class="btn btn-ghost" href="/#projects">{esc(m["nf_cta2"])}</a>
  </div>
 </div>
</section>'''
    return simple_shell(lang, t, "404", m["nf_title"], m["nf_p"], body, robots="noindex", alternates=False)


def thank_you(lang):
    t = T[lang]
    alternates = [("ar", url("thank-you", "ar", True)), ("en", url("thank-you", "en", True))]
    cfg = {"lang": lang, "wa": SITE["wa"], "t": {
        "waMsg": t["wa_msg"], "waMsgGeneric": t["wa_msg_generic"], "backTo": t["ty_back"],
        "redirecting": t["ty_redirecting"], "notOpened": t["ty_not_opened"], "openedNewTab": t["ty_new_tab"], "clickToOpen": t["ty_click"],
        "titleGeneric": t["ty_title_generic"], "textGeneric": t["ty_text_generic"], "titleProject": t["ty_title_p"]}}
    html = head(t["ty_seo_title"], t["ty_text_generic"], url("thank-you", lang, True), alternates, lang, t,
                robots="noindex, nofollow")
    html += f'''{lang_bar("thank-you", lang, t, keep=True)}
<main class="ty">
 <div class="ty-box">
  <div class="ty-ok">{ic("check")}</div>
  <h1 id="tyTitle">{esc(t["ty_title"])}</h1>
  <p id="tyText">{esc(t["ty_text"])}</p>
  <span class="ty-ctx" id="tyCtx" hidden></span>
  <ul class="ty-points" id="tyPoints">{"".join(f"<li>{ic('check')} {esc(x)}</li>" for x in t["ty_points"])}</ul>
  <a class="btn ty-wa" id="tyWa" href="https://wa.me/{SITE["wa"]}" rel="noopener">{ic("whatsapp")} {esc(t["ty_btn"])}</a>
  <div class="ty-bar" id="tyBar"><i></i></div>
  <p class="ty-count" id="tyCount" aria-live="polite"></p>
  <a class="ty-back" id="tyBack" href="{url("", lang)}">{ic("arrow-r" if t["dir"] == "rtl" else "arrow-l")} <span id="tyBackText">{esc(t["ty_back_generic"])}</span></a>
 </div>
</main>
<script>window.VIBE={json.dumps(cfg, ensure_ascii=False)};</script>
<script src="/assets/js/thank-you.js?v={ASSET_V}" defer></script>
</body>
</html>
'''
    return html


def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("built", rel, f"({len(content.encode('utf-8')) // 1024} KB)")


def sitemap():
    """Plain urlset (hreflang lives in each page's <head>, so it is not repeated here).
    Written twice: sitemap.xml and pages-sitemap.xml (a fresh name for Search Console)."""
    import datetime
    today = datetime.date.today().isoformat()
    slugs = [""] + [HUB_SLUG] + [s for s, p in PROJECTS.items() if p.get("ready")] + ["about-us", "privacy-policy"]
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for slug in slugs:
        for l in LANGS:
            out.append(f"  <url><loc>{url(slug, l, True)}</loc><lastmod>{today}</lastmod></url>")
    out.append("</urlset>")
    xml = "\n".join(out) + "\n"
    write("sitemap.xml", xml)
    write("pages-sitemap.xml", xml)
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /thank-you\nDisallow: /en/thank-you\nDisallow: /tools/\n\n"
                        f"Sitemap: {SITE['domain']}/sitemap.xml\nSitemap: {SITE['domain']}/pages-sitemap.xml\n")

def llms_txt():
    """/llms.txt — a plain-markdown summary of the site for AI assistants and answer engines."""
    t = T["en"]
    d = SITE["domain"]
    out = [f'# {SITE["brand"]}', "",
           "> VIBE Real Estate is an independent real-estate broker in Egypt. It presents residential projects from "
           "Egypt's leading developers, helps buyers compare units, prices and payment plans, and connects them with "
           "the developer. VIBE is not a developer: contracts are signed directly with the developer.", "",
           "Prices are in Egyptian pounds (EGP), are indicative, and may be changed by the developer without notice.",
           f'Contact: phone / WhatsApp {SITE["tel_intl"]}. The site is available in Arabic ({d}/) and English ({d}/en/).', "",
           "## Projects (Palm Hills Developments, West Cairo)", ""]
    for slug, p in PROJECTS.items():
        if not p.get("ready"):
            continue
        out.append(f'- [{p["title"]}]({url(slug, "en", True)}): {p["about"]["en"][0]} From EGP {money(p["price_from"])}, '
                   f'{p["down"]}% down payment, up to {p["years"]} years installments, delivery {p["delivery"]}.')
    out += ["", "## Company", "",
            f'- [About VIBE Real Estate]({url("about-us", "en", True)}): who we are and how we work as an independent broker.',
            f'- [Privacy policy]({url("privacy-policy", "en", True)}): how enquiry data is collected and used.',
            f'- [Palm Hills October projects]({url(HUB_SLUG, "en", True)}): all five projects, a side-by-side price comparison and a guide by home type.',
            f'- [Home]({url("", "en", True)}): who VIBE is, the projects and general questions.', ""]
    for slug, p in PROJECTS.items():
        if not p.get("ready"):
            continue
        out += [f'## {p["title"]}', "", f'Page: {url(slug, "en", True)} (Arabic: {url(slug, "ar", True)})', ""]
        out += [" ".join(p["about"]["en"]), ""]
        out.append("| Unit | Size | Price from (EGP) |")
        out.append("|---|---|---|")
        for u in p["units"] + (p["launch"]["units"] if p.get("launch") else []):
            out.append(f'| {u["name"]} | {unit_size(u, t)} | {money(u["price"]) if u.get("price") else "On request"} |')
        out.append("")
        for q, a in project_faq(p, "en", t):
            out += [f"**{q}** {a}", ""]
    write("llms.txt", "\n".join(out).rstrip() + "\n")


def main():
    build_sprite()
    build_og()
    sitemap()
    llms_txt()
    for slug, p in PROJECTS.items():
        if not p.get("ready"):
            continue
        for lang in LANGS:
            write((f"en/{slug}.html" if lang == "en" else f"{slug}.html"), project_page(slug, lang))
    for lang in LANGS:
        write("en/thank-you.html" if lang == "en" else "thank-you.html", thank_you(lang))
        write("en/index.html" if lang == "en" else "index.html", home_page(lang))
        write(f"en/{HUB_SLUG}.html" if lang == "en" else f"{HUB_SLUG}.html", hub_page(lang))
        write("en/about-us.html" if lang == "en" else "about-us.html", about_page(lang))
        write("en/privacy-policy.html" if lang == "en" else "privacy-policy.html", privacy_page(lang))
    write("404.html", not_found_page())


if __name__ == "__main__":
    main()
