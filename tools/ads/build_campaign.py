"""Builds the Google Ads search campaign for VIBE (one ad group per project and language).

Outputs, next to this file:
  vibe-search-campaign.xlsx      review workbook (settings, keywords, ads with live length checks, negatives, assets)
  vibe-search-campaign-editor.csv   import file for Google Ads Editor (everything is created PAUSED)

Prices and plans come from tools/site_data.py, so re-run after a price update.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from site_data import SITE, PROJECTS  # noqa: E402

D = SITE["domain"]
CAMPAIGN = "VIBE | Search | Palm Hills October"
BUDGET = 500          # EGP/day — PLACEHOLDER, set the real figure before enabling
HUB = "palm-hills-october"
LOCATIONS = ["Egypt", "Saudi Arabia", "United Arab Emirates", "Oman", "Qatar", "Bahrain", "Kuwait"]


def m(n):             # 13144000 -> "13.1"
    return f"{n / 1e6:.1f}"


def full(n):
    return f"{n:,}"


P = PROJECTS
px, pp, ce, ph, bb = P["px"], P["palm-parks"], P["crown-extension"], P["palm-hills-one"], P["bamboo-iii"]
low = min(p["price_from"] for p in P.values() if p.get("ready"))

BRAND_AR = ["VIBE Real Estate", "وسيط عقاري مستقل", "قارن الوحدات والأسعار", "اطلب التفاصيل الآن", "الأسعار وخطط السداد 2026"]
BRAND_EN = ["VIBE Real Estate", "Independent Property Broker", "Compare Units & Prices", "Request Details Today", "Prices & Payment Plans 2026"]
D_BROKER_AR = "VIBE Real Estate وسيط عقاري مستقل. بنعرض أسعار المطوّر زي ما هي ونساعدك تختار."
D_FORM_AR = "سجّل بياناتك وهنتواصل معاك على واتساب بتفاصيل الوحدات والأسعار وخطط السداد."
D_BROKER_EN = "VIBE Real Estate is an independent broker. Developer prices as they are, no pressure."
D_FORM_EN = "Leave your details and we will contact you on WhatsApp with units, prices and plans."

# name, slug, language -> keywords [(text, match)], headlines (first is pinned to position 1), descriptions, paths
GROUPS = [
    dict(name="PX | AR", slug="px", lang="ar", paths=("بالم-هيلز", "PX"),
         kw=[("بي اكس بالم هيلز", "PE"), ("px بالم هيلز", "PE"), ("كمبوند بي اكس", "P"), ("كمبوند px اكتوبر", "P"),
             ("بي اكس اكتوبر", "P"), ("اسعار px بالم هيلز", "P"), ("بالم جاردنز بالم هيلز", "P")],
         h=["PX بالم هيلز أكتوبر", "كمبوند PX من بالم هيلز", f"أسعار PX تبدأ من {m(px['price_from'])} مليون",
            f"مقدم {px['down']}% وتقسيط حتى {px['years']} سنوات", "شقق وتاون هاوس وفيلات", "على أعلى نقطة في بالم هيلز",
            f"استلام يبدأ من {px['delivery']}", "مرحلة Palm Gardens الجديدة", "شقق من غرفة لـ 3 غرف نوم",
            "اعرف الوحدات المتاحة الآن"] + BRAND_AR,
         d=[f"كمبوند PX من بالم هيلز في أكتوبر: شقق وتاون هاوس بمقدم {px['down']}% وتقسيط حتى {px['years']} سنوات.",
            f"الأسعار تبدأ من {full(px['price_from'])} جنيه. اعرف الوحدات المتاحة والمساحات وخطط السداد.",
            D_BROKER_AR, D_FORM_AR]),
    dict(name="PX | EN", slug="px", lang="en", paths=("Palm-Hills", "PX"),
         kw=[("px palm hills", "PE"), ("px compound", "PE"), ("px october", "P"), ("px palm hills prices", "P"),
             ("px compound october", "P"), ("palm gardens px", "P")],
         h=["PX Palm Hills October", "PX Compound by Palm Hills", f"Prices From EGP {m(px['price_from'])}M",
            f"{px['down']}% Down, Up to {px['years']} Years", "Apartments, Towns & Villas", "Highest Point in Palm Hills",
            f"Delivery Starts {px['delivery']}", "New Phase: Palm Gardens", "1 to 3 Bedroom Apartments",
            "See Available Units"] + BRAND_EN,
         d=[f"PX by Palm Hills in 6th of October: apartments and town houses, {px['down']}% down, {px['years']} years.",
            f"Prices start from EGP {full(px['price_from'])}. See available units, sizes and payment plans.",
            D_BROKER_EN, D_FORM_EN]),

    dict(name="Palm Parks | AR", slug="palm-parks", lang="ar", paths=("بالم-هيلز", "Palm-Parks"),
         kw=[("بالم باركس", "PE"), ("بالم باركس اكتوبر", "PE"), ("كمبوند بالم باركس", "P"), ("شقق بالم باركس", "P"),
             ("اسعار بالم باركس", "P"), ("بالم باركس بالم هيلز", "P")],
         h=["Palm Parks بالم هيلز أكتوبر", "شقق بالم باركس أكتوبر", f"الأسعار تبدأ من {m(pp['price_from'])} مليون",
            f"مقدم {pp['down']}% وتقسيط حتى {pp['years']} سنوات", "شقق 2 و3 غرف نوم", "عند وصلة دهشور مباشرة",
            f"استلام {pp['delivery']}", "شقق بجاردن خاصة", "كمبوند هادي بكثافة قليلة",
            "اعرف الوحدات المتاحة الآن"] + BRAND_AR,
         d=[f"شقق Palm Parks من بالم هيلز عند وصلة دهشور: مقدم {pp['down']}% وتقسيط حتى {pp['years']} سنوات.",
            f"الأسعار تبدأ من {full(pp['price_from'])} جنيه. اعرف المساحات والوحدات المتاحة.",
            D_BROKER_AR, D_FORM_AR]),
    dict(name="Palm Parks | EN", slug="palm-parks", lang="en", paths=("Palm-Hills", "Palm-Parks"),
         kw=[("palm parks", "PE"), ("palm parks october", "PE"), ("palm parks palm hills", "P"), ("palm parks compound", "P"),
             ("palm parks apartments", "P"), ("palm parks prices", "P")],
         h=["Palm Parks Palm Hills", "Palm Parks October Apartments", f"Prices From EGP {m(pp['price_from'])}M",
            f"{pp['down']}% Down, Up to {pp['years']} Years", "2 & 3 Bedroom Apartments", "Right off the Dahshur Link",
            f"Delivery {pp['delivery']}", "Garden Apartments Available", "A Quiet Low-Density Community",
            "See Available Units"] + BRAND_EN,
         d=[f"Palm Parks by Palm Hills off the Dahshur Link: apartments, {pp['down']}% down, up to {pp['years']} years.",
            f"Prices start from EGP {full(pp['price_from'])}. See sizes and currently available units.",
            D_BROKER_EN, D_FORM_EN]),

    dict(name="Crown Extension | AR", slug="crown-extension", lang="ar", paths=("بالم-هيلز", "The-Crown"),
         kw=[("ذا كراون بالم هيلز", "PE"), ("كراون اكستنشن", "PE"), ("كمبوند ذا كراون", "P"), ("ذا كراون اكتوبر", "P"),
             ("اسعار ذا كراون", "P"), ("كراون بالم هيلز", "P")],
         h=["Crown Extension بالم هيلز", "ذا كراون بالم هيلز أكتوبر", f"الأسعار تبدأ من {m(ce['price_from'])} مليون",
            f"مقدم {ce['down']}% وتقسيط حتى {ce['years']} سنوات", "Family Homes وتوين هاوس", "في قلب بالم هيلز أكتوبر",
            f"استلام {ce['delivery']}", "مساحات من 217 م²", "بجاردن خاصة أو بنتهاوس",
            "اعرف الوحدات المتاحة الآن"] + BRAND_AR,
         d=[f"Crown Extension من بالم هيلز: Family Homes وتوين هاوس بمقدم {ce['down']}% وتقسيط حتى {ce['years']} سنوات.",
            f"الأسعار تبدأ من {full(ce['price_from'])} جنيه. اعرف المساحات والوحدات المتاحة.",
            D_BROKER_AR, D_FORM_AR]),
    dict(name="Crown Extension | EN", slug="crown-extension", lang="en", paths=("Palm-Hills", "The-Crown"),
         kw=[("the crown palm hills", "PE"), ("crown extension palm hills", "PE"), ("the crown october", "P"),
             ("the crown compound", "P"), ("crown palm hills prices", "P"), ("the crown extension", "P")],
         h=["The Crown Extension", "The Crown Palm Hills October", f"Prices From EGP {m(ce['price_from'])}M",
            f"{ce['down']}% Down, Up to {ce['years']} Years", "Family Homes & Twin Houses", "Heart of Palm Hills October",
            f"Delivery {ce['delivery']}", "Homes From 217 sqm", "Private Garden or Penthouse",
            "See Available Units"] + BRAND_EN,
         d=[f"Crown Extension by Palm Hills: family homes and twin houses, {ce['down']}% down, {ce['years']} years.",
            f"Prices start from EGP {full(ce['price_from'])}. See sizes and currently available units.",
            D_BROKER_EN, D_FORM_EN]),

    dict(name="Palm Hills One | AR", slug="palm-hills-one", lang="ar", paths=("بالم-هيلز", "One"),
         kw=[("بالم هيلز وان", "PE"), ("كمبوند بالم هيلز وان", "P"), ("فيلات بالم هيلز وان", "P"),
             ("اسعار بالم هيلز وان", "P"), ("بالم هيلز وان اكتوبر", "P")],
         h=["Palm Hills One أكتوبر", "فيلات بالم هيلز وان", f"الأسعار تبدأ من {m(ph['price_from'])} مليون",
            f"مقدم {ph['down']}% وتقسيط حتى {ph['years']} سنوات", "تاون وتوين وفيلات مستقلة", "مجتمع فيلات فقط",
            f"استلام {ph['delivery']}", "أراضي حتى 1,500 م²", "امتداد بالم هيلز أكتوبر",
            "اعرف الوحدات المتاحة الآن"] + BRAND_AR,
         d=[f"Palm Hills One: تاون هاوس وتوين هاوس وفيلات مستقلة بمقدم {ph['down']}% وتقسيط حتى {ph['years']} سنوات.",
            f"الأسعار تبدأ من {full(ph['price_from'])} جنيه. اعرف النماذج والمساحات المتاحة.",
            D_BROKER_AR, D_FORM_AR]),
    dict(name="Palm Hills One | EN", slug="palm-hills-one", lang="en", paths=("Palm-Hills", "One"),
         kw=[("palm hills one", "PE"), ("palm hills one villas", "P"), ("palm hills one october", "P"),
             ("palm hills one prices", "P"), ("palm hills one compound", "P")],
         h=["Palm Hills One October", "Palm Hills One Villas", f"Prices From EGP {m(ph['price_from'])}M",
            f"{ph['down']}% Down, Up to {ph['years']} Years", "Town, Twin & Standalone", "A Villas-Only Community",
            f"Delivery {ph['delivery']}", "Plots Up to 1,500 sqm", "Next to Palm Hills October",
            "See Available Units"] + BRAND_EN,
         d=[f"Palm Hills One: town houses, twin houses and villas, {ph['down']}% down, up to {ph['years']} years.",
            f"Prices start from EGP {full(ph['price_from'])}. See villa models and available sizes.",
            D_BROKER_EN, D_FORM_EN]),

    dict(name="Bamboo III | AR", slug="bamboo-iii", lang="ar", paths=("بالم-هيلز", "Bamboo"),
         kw=[("بامبو بالم هيلز", "PE"), ("بامبو 3 بالم هيلز", "PE"), ("كمبوند بامبو اكتوبر", "P"),
             ("بامبو اكستنشن بالم هيلز", "P"), ("اسعار بامبو بالم هيلز", "P"), ("بامبو 3 اكتوبر", "P")],
         h=["Bamboo III بالم هيلز أكتوبر", "بامبو 3 بالم هيلز", f"الأسعار تبدأ من {m(bb['price_from'])} مليون",
            f"مقدم {bb['down']}% وتقسيط حتى {bb['years']} سنوات", "Family Homes وتاون هاوس", "وحدات متشطبة بالكامل",
            f"استلام {bb['delivery']}", "على محور 26 يوليو", "لاجونز ومساحات خضراء",
            "اعرف الوحدات المتاحة الآن"] + BRAND_AR,
         d=[f"Bamboo III من بالم هيلز: Family Homes وتاون هاوس متشطبة، مقدم {bb['down']}% وتقسيط حتى {bb['years']} سنوات.",
            f"الأسعار تبدأ من {full(bb['price_from'])} جنيه. اعرف المساحات والوحدات المتاحة.",
            D_BROKER_AR, D_FORM_AR]),
    dict(name="Bamboo III | EN", slug="bamboo-iii", lang="en", paths=("Palm-Hills", "Bamboo"),
         kw=[("bamboo palm hills", "PE"), ("bamboo 3 palm hills", "PE"), ("bamboo iii palm hills", "P"),
             ("bamboo extension palm hills", "P"), ("bamboo october compound", "P"), ("bamboo palm hills prices", "P")],
         h=["Bamboo III Palm Hills", "Bamboo 3 Palm Hills October", f"Prices From EGP {m(bb['price_from'])}M",
            f"{bb['down']}% Down, Up to {bb['years']} Years", "Family Homes & Town Houses", "Fully Finished Homes",
            f"Delivery {bb['delivery']}", "On the 26th of July Axis", "Lagoons & Green Spaces",
            "See Available Units"] + BRAND_EN,
         d=[f"Bamboo III by Palm Hills: fully finished family homes and towns, {bb['down']}% down, {bb['years']} years.",
            f"Prices start from EGP {full(bb['price_from'])}. See sizes and currently available units.",
            D_BROKER_EN, D_FORM_EN]),

    dict(name="Palm Hills October | AR", slug=HUB, lang="ar", paths=("بالم-هيلز", "أكتوبر"),
         kw=[("بالم هيلز اكتوبر", "PE"), ("كمبوند بالم هيلز اكتوبر", "PE"), ("اسعار بالم هيلز اكتوبر", "P"),
             ("مشاريع بالم هيلز اكتوبر", "P"), ("شقق بالم هيلز اكتوبر", "P"), ("فيلات بالم هيلز اكتوبر", "P"),
             ("بالم هيلز 6 اكتوبر", "P"), ("مشاريع بالم هيلز", "P")],
         h=["مشاريع بالم هيلز أكتوبر", "أسعار بالم هيلز أكتوبر 2026", f"الأسعار تبدأ من {m(low)} مليون",
            "مقدم 5% وتقسيط حتى 10 سنوات", "شقق وتاون هاوس وفيلات", "5 مشاريع في صفحة واحدة",
            "قارن أسعار المشاريع", "PX وPalm Parks وBamboo III", "The Crown وPalm Hills One",
            "اعرف الوحدات المتاحة الآن"] + BRAND_AR,
         d=["كل مشاريع بالم هيلز أكتوبر في صفحة واحدة: الأسعار وخطط السداد ومقارنة بين 5 مشاريع.",
            f"الأسعار تبدأ من {full(low)} جنيه بمقدم 5% وتقسيط حتى 10 سنوات.",
            D_BROKER_AR, D_FORM_AR]),
    dict(name="Palm Hills October | EN", slug=HUB, lang="en", paths=("Palm-Hills", "October"),
         kw=[("palm hills october", "PE"), ("palm hills 6 october", "PE"), ("palm hills october prices", "P"),
             ("palm hills october projects", "P"), ("palm hills october apartments", "P"),
             ("palm hills october villas", "P"), ("palm hills october compound", "P"), ("palm hills projects", "P")],
         h=["Palm Hills October Projects", "Palm Hills October Prices", f"Prices From EGP {m(low)}M",
            "5% Down, Up to 10 Years", "Apartments, Towns & Villas", "5 Projects on One Page",
            "Compare Project Prices", "PX, Palm Parks & Bamboo III", "The Crown & Palm Hills One",
            "See Available Units"] + BRAND_EN,
         d=["All Palm Hills October projects on one page: prices, payment plans and a comparison.",
            f"Prices start from EGP {full(low)} with 5% down payment and up to 10 years.",
            D_BROKER_EN, D_FORM_EN]),
]

# Generic ad groups must not catch searches for one specific project
HUB_NEG = ["px", "بي اكس", "palm parks", "بالم باركس", "crown", "كراون", "bamboo", "بامبو", "palm hills one", "بالم هيلز وان"]

NEGATIVES = {
    "Rent / resale": ["ايجار", "للايجار", "إيجار", "ريسيل", "اعادة بيع", "مستعمل", "rent", "rental", "for rent", "resale", "airbnb"],
    "Jobs": ["وظائف", "وظيفة", "شغل", "توظيف", "تدريب", "jobs", "job", "careers", "career", "hiring", "vacancies", "internship", "salary"],
    "Developer support": ["شكاوى", "شكوى", "خدمة العملاء", "الخط الساخن", "رقم خدمة", "مقر", "complaints", "customer service", "hotline", "head office"],
    "Club / stock / other intent": ["نادي", "عضوية", "اسهم", "سهم", "البورصة", "مدرسة", "مدارس", "club", "membership", "stock", "share price", "school", "gym", "logo"],
    "Commercial units": ["محل", "محلات", "اداري", "مكتب", "عيادة", "تجاري", "shop", "office", "clinic", "retail", "commercial"],
    "Other locations": ["القاهرة الجديدة", "قاهرة جديدة", "التجمع", "الساحل", "هاسيندا", "بادية", "العاصمة", "العلمين", "السخنة", "القطامية",
                        "new cairo", "north coast", "sahel", "hacienda", "badya", "alamein", "sokhna", "katameya", "new capital"],
}

SITELINKS = [("PX Compound", "px", f"من {m(px['price_from'])} مليون جنيه", "شقق وتاون هاوس وفيلات"),
             ("Palm Parks", "palm-parks", f"من {m(pp['price_from'])} مليون جنيه", "شقق عند وصلة دهشور"),
             ("Crown Extension", "crown-extension", f"من {m(ce['price_from'])} مليون جنيه", "Family Homes وتوين هاوس"),
             ("Palm Hills One", "palm-hills-one", f"من {m(ph['price_from'])} مليون جنيه", "تاون وتوين وفيلات"),
             ("Bamboo III", "bamboo-iii", f"من {m(bb['price_from'])} مليون جنيه", "وحدات متشطبة بالكامل"),
             ("مقارنة أسعار المشاريع", HUB, "5 مشاريع في جدول واحد", "الأسعار وخطط السداد")]
CALLOUTS = ["مقدم 5%", "تقسيط حتى 10 سنوات", "وسيط عقاري مستقل", "شقق وتاون هاوس وفيلات", "مقارنة بين 5 مشاريع", "Independent Broker", "5% Down Payment", "Up to 10 Years"]
SNIPPET = ("Types", ["شقق", "Family Homes", "تاون هاوس", "توين هاوس", "فيلات"])


def final_url(g):
    return f"{D}/en/{g['slug']}" if g["lang"] == "en" else f"{D}/{g['slug']}"


def validate():
    bad = []
    for g in GROUPS:
        if not (10 <= len(g["h"]) <= 15):
            bad.append((g["name"], "headline count", len(g["h"])))
        if len(set(g["h"])) != len(g["h"]):
            bad.append((g["name"], "duplicate headline", ""))
        for x in g["h"]:
            if len(x) > 30:
                bad.append((g["name"], f"H {len(x)}", x))
        for x in g["d"]:
            if len(x) > 90:
                bad.append((g["name"], f"D {len(x)}", x))
        for x in g["paths"]:
            if len(x) > 15:
                bad.append((g["name"], f"path {len(x)}", x))
    for t, _, a, b in SITELINKS:
        for x, lim in ((t, 25), (a, 35), (b, 35)):
            if len(x) > lim:
                bad.append(("sitelink", f"{len(x)}>{lim}", x))
    for c in CALLOUTS:
        if len(c) > 25:
            bad.append(("callout", len(c), c))
    return bad


def editor_csv(path):
    cols = (["Campaign", "Campaign Type", "Networks", "Budget", "Budget type", "Bid Strategy Type", "Languages", "Location",
             "Campaign Status", "Ad Group", "Ad Group Status", "Keyword", "Criterion Type", "Status", "Ad type", "Final URL",
             "Path 1", "Path 2"] + [f"Headline {i}" for i in range(1, 16)] + ["Headline 1 position"]
            + [f"Description {i}" for i in range(1, 5)])
    rows = []
    r = lambda **k: rows.append({**{c: "" for c in cols}, "Campaign": CAMPAIGN, **k})
    r(**{"Campaign Type": "Search", "Networks": "Google search", "Budget": BUDGET, "Budget type": "Daily",
         "Bid Strategy Type": "Maximize clicks", "Languages": "ar;en", "Campaign Status": "Paused"})
    for loc in LOCATIONS:
        r(**{"Location": loc})
    for vals in NEGATIVES.values():
        for k in vals:
            r(**{"Keyword": k, "Criterion Type": "Campaign Negative Phrase"})
    MT = {"P": ["Phrase"], "PE": ["Phrase", "Exact"]}
    for g in GROUPS:
        r(**{"Ad Group": g["name"], "Ad Group Status": "Enabled"})
        for k, mt in g["kw"]:
            for t in MT[mt]:
                r(**{"Ad Group": g["name"], "Keyword": k, "Criterion Type": t, "Status": "Enabled"})
        if g["slug"] == HUB:
            for k in HUB_NEG:
                r(**{"Ad Group": g["name"], "Keyword": k, "Criterion Type": "Negative Phrase"})
        ad = {"Ad Group": g["name"], "Ad type": "Responsive search ad", "Status": "Enabled", "Final URL": final_url(g),
              "Path 1": g["paths"][0], "Path 2": g["paths"][1], "Headline 1 position": 1}
        ad.update({f"Headline {i + 1}": x for i, x in enumerate(g["h"])})
        ad.update({f"Description {i + 1}": x for i, x in enumerate(g["d"])})
        r(**ad)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def workbook(path):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.formatting.rule import CellIsRule
    from openpyxl.utils import get_column_letter
    F, B = Font(name="Arial", size=10), Font(name="Arial", size=10, bold=True)
    HEAD = PatternFill("solid", fgColor="0E3B2E")
    HF = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    RED = PatternFill("solid", fgColor="F8D7DA")
    wb = Workbook()

    def sheet(title, headers, widths, rtl=False):
        ws = wb.create_sheet(title)
        ws.append(headers)
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
            c = ws.cell(1, i)
            c.font, c.fill, c.alignment = HF, HEAD, Alignment(vertical="center", wrap_text=True)
        ws.freeze_panes = "A2"
        return ws

    def style(ws):
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.font = F
                c.alignment = Alignment(vertical="top", wrap_text=True)

    ws = wb.active
    ws.title = "Settings"
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width, ws.column_dimensions["C"].width = 26, 44, 70
    data = [("Setting", "Value", "Note"),
            ("Campaign", CAMPAIGN, "Created PAUSED by the Editor import."),
            ("Type / network", "Search — Google search only", "Search partners and Display off."),
            ("Daily budget (EGP)", BUDGET, "PLACEHOLDER. Replace with the real daily budget before enabling."),
            ("Bidding", "Maximize clicks", "Start here with a max CPC limit; switch to Maximize conversions after ~15-20 leads."),
            ("Locations", ", ".join(LOCATIONS), "Presence only (people in the location). One campaign at launch; split Egypt and Gulf later once there is data."),
            ("Languages", "Arabic + English", ""),
            ("Conversion goal", "Submit lead form (account default)", "Fires on thank_you_view, once per lead."),
            ("Ad groups", len(GROUPS), "One per project and language, plus the Palm Hills October hub."),
            ("Match types", "Phrase + Exact", "No broad match at launch, for lead quality."),
            ("Prices in ads", "From tools/site_data.py", "Source: client price sheet 'Sales Availability 1 Oct 2026'. Re-run the script after a price update."),
            ("Discount claims", "None in ad copy", "PX 40% and Crown 30% are left out until confirmed with the developer.")]
    for row in data:
        ws.append(row)
    for c in ws[1]:
        c.font, c.fill = HF, HEAD
    style(ws)

    ws = sheet("Keywords", ["Ad group", "Language", "Keyword", "Match types", "Final URL"], [26, 10, 34, 16, 52])
    for g in GROUPS:
        for k, mt in g["kw"]:
            ws.append([g["name"], g["lang"].upper(), k, "Phrase + Exact" if mt == "PE" else "Phrase", final_url(g)])
    style(ws)

    ws = sheet("Ads", ["Ad group", "Field", "Text", "Length", "Limit", "Final URL"], [26, 16, 78, 9, 8, 52])
    for g in GROUPS:
        for i, x in enumerate(g["h"], 1):
            ws.append([g["name"], f"Headline {i}" + (" (pin 1)" if i == 1 else ""), x, None, 30, final_url(g) if i == 1 else ""])
        for i, x in enumerate(g["d"], 1):
            ws.append([g["name"], f"Description {i}", x, None, 90, ""])
        ws.append([g["name"], "Path", " / ".join(g["paths"]), None, 15, ""])
    for r_ in range(2, ws.max_row + 1):
        if not str(ws.cell(r_, 2).value).startswith("Path"):
            ws.cell(r_, 4).value = f"=LEN(C{r_})"
    style(ws)
    ws.conditional_formatting.add(f"D2:D{ws.max_row}", CellIsRule(operator="greaterThan", formula=["E2"], fill=RED))
    ws["H1"], ws["H2"] = "How to use", "Edit the text in column C. Length updates itself; a red cell means the text is over the limit."
    ws["H1"].font, ws["H2"].font = B, F
    ws.column_dimensions["H"].width = 60

    ws = sheet("Negatives", ["Level", "Group", "Negative keyword", "Match type"], [30, 30, 30, 14])
    for grp, vals in NEGATIVES.items():
        for k in vals:
            ws.append(["Campaign", grp, k, "Phrase"])
    for k in HUB_NEG:
        ws.append(["Ad groups: Palm Hills October AR + EN", "Route project searches to their own ad group", k, "Phrase"])
    style(ws)

    ws = sheet("Assets", ["Asset", "Text", "Line 1", "Line 2", "Final URL"], [18, 30, 30, 30, 52])
    for t, s, a, b in SITELINKS:
        ws.append(["Sitelink", t, a, b, f"{D}/{s}"])
    for c in CALLOUTS:
        ws.append(["Callout", c, "", "", ""])
    ws.append(["Structured snippet", SNIPPET[0], "، ".join(SNIPPET[1]), "", ""])
    ws.append(["Call", SITE["tel_intl"], "Call asset; counts as the secondary 'Phone Call' conversion", "", ""])
    style(ws)
    wb.save(path)


if __name__ == "__main__":
    bad = validate()
    for b in bad:
        print("OVER", b)
    if bad:
        sys.exit(1)
    n = editor_csv(os.path.join(HERE, "vibe-search-campaign-editor.csv"))
    workbook(os.path.join(HERE, "vibe-search-campaign.xlsx"))
    kws = sum(len(g["kw"]) for g in GROUPS)
    print(f"ok: {len(GROUPS)} ad groups, {kws} keywords, {sum(len(v) for v in NEGATIVES.values())} campaign negatives, {n} CSV rows")
