"""Builds the whole site from the templates.

Site layout:
  /                  landing page, holding the root for the real site later
  /catalogue/        the catalogue in Hebrew
  /catalogue/en/     the catalogue in English
  /vcard/            digital business card, parked; nothing links to it yet

The two catalogue languages are separate pages rather than one page with a
toggle, so a link can be shared in either language and each URL declares one
language to search engines. Both are generated from the same template: the
build strips the other language's spans and turns the toggle into links.

Every URL derives from SITE_URL. Change it here and rerun; the QR code on the
poster comes from make_poster.py, which has its own copy for the same reason.

Run `py build.py` after editing any template. Never hand-edit the output.
"""

import base64
import mimetypes
import pathlib
import datetime
import json
import re

HERE = pathlib.Path(__file__).parent
SITE_URL = "https://mushroomkingdom.co.il"

CATALOGUE = {
    "he": {
        "out": "catalogue/index.html",
        "path": "/catalogue/",
        "dir": "rtl",
        "title": "ממלכת הפטריות | פטריות שף בגידול אורגני",
        "description": "קטלוג הפטריות של ממלכת הפטריות. פטריות שף בגידול אורגני, ישירות מהמגדל.",
    },
    "en": {
        "out": "catalogue/en/index.html",
        "path": "/catalogue/en/",
        "dir": "ltr",
        "title": "Mushrooms Kingdom | Gourmet mushrooms, organically grown",
        "description": "The Mushrooms Kingdom catalogue. Gourmet mushrooms, organically grown, direct from the grower.",
    },
}

LANDING = {
    "out": "index.html",
    "path": "/",
    "dir": "rtl",
    "title": "ממלכת הפטריות",
    "description": "ממלכת הפטריות. פטריות שף בגידול אורגני. האתר המלא יעלה בקרוב.",
}

VCARD = {
    "out": "vcard/index.html",
    "path": "/vcard/",
    "dir": "rtl",
    "title": "ממלכת הפטריות | פרטי קשר והזמנות",
    "description": "כרטיס הביקור הדיגיטלי של ממלכת הפטריות. פרטי קשר, הזמנות וקישור לקטלוג.",
}


ORGANISATION = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "ממלכת הפטריות",
    "alternateName": "Mushrooms Kingdom",
    "description": "חוות פטריות שף בגידול אורגני, בצפון הארץ.",
    "url": SITE_URL + "/",
    "logo": SITE_URL + "/images/favicon-512.png",
    "image": SITE_URL + "/images/og.jpg",
    "foundingDate": "2022",
    "telephone": "+972-52-705-0501",
    "sameAs": ["https://instagram.com/mushrooms.kingdomm"],
    "areaServed": {"@type": "Country", "name": "Israel"},
    "address": {
        "@type": "PostalAddress",
        "addressCountry": "IL",
        "addressRegion": "צפון",
    },
    "contactPoint": {
        "@type": "ContactPoint",
        "contactType": "sales",
        "telephone": "+972-52-705-0501",
        "availableLanguage": ["he", "en"],
    },
}


def structured_data():
    """One Organization block, on every page. Tells search engines who this is,
    which is what a brand-name search needs to resolve to the right site.
    No street address: the location was deliberately kept to a region."""
    return ('<script type="application/ld+json">'
            + json.dumps(ORGANISATION, ensure_ascii=False, separators=(",", ":"))
            + "</script>\n")



def head_meta(page, alternates=()):
    """Description, canonical and the Open Graph tags that make a shared link
    render as a card with a photograph instead of a bare URL. WhatsApp,
    Facebook and Telegram all read these; og:image must be absolute."""
    tags = (
        '<meta name="description" content="{description}">\n'
        '<link rel="canonical" href="{site}{path}">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:site_name" content="ממלכת הפטריות">\n'
        '<meta property="og:title" content="{title}">\n'
        '<meta property="og:description" content="{description}">\n'
        '<meta property="og:url" content="{site}{path}">\n'
        '<meta property="og:image" content="{site}/images/og.jpg">\n'
        '<meta property="og:image:type" content="image/jpeg">\n'
        '<meta property="og:image:width" content="1200">\n'
        '<meta property="og:image:height" content="630">\n'
        '<meta property="og:image:alt" content="פטריות צדף ורודה טריות עם הסמל של ממלכת הפטריות">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
    ).format(site=SITE_URL, **page)
    for lang, path in alternates:
        tags += '<link rel="alternate" hreflang="%s" href="%s%s">\n' % (lang, SITE_URL, path)
    return tags


def wrap(body, page, alternates=(), lang="he"):
    return (
        '<!doctype html>\n<html lang="%s" dir="%s">\n<head>\n' % (lang, page["dir"])
        + '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<link rel="icon" href="/favicon.ico" sizes="any">\n'
        '<link rel="icon" type="image/png" sizes="32x32" href="/images/favicon-32.png">\n'
        '<link rel="icon" type="image/png" sizes="192x192" href="/images/favicon-192.png">\n'
        '<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">\n'
        '<meta name="theme-color" content="#171512">\n'
        + head_meta(page, alternates)
        + structured_data()
        + "</head>\n<body>\n" + body + "\n</body>\n</html>\n"
    )


def set_title(html, title):
    return re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, html, count=1, flags=re.S)


def strip_lang(html, drop):
    """Remove the spans belonging to the language this page is not."""
    return re.sub(r'\s*<span class="when-%s[^"]*">.*?</span>' % drop, "", html, flags=re.S)


def language_links(current):
    other = "en" if current == "he" else "he"
    def cell(lang, label):
        mark = ' aria-current="page"' if lang == current else ""
        return '    <a href="%s"%s>%s</a>' % (CATALOGUE[lang]["path"], mark, label)
    return (
        '  <div class="langswitch" role="group" aria-label="Language / שפה">\n'
        + cell("he", "HEB") + "\n" + cell("en", "EN") + "\n  </div>"
    )


def inline_images(html):
    def repl(match):
        path = HERE / match.group(1)
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return 'src="data:%s;base64,%s"' % (mime, base64.b64encode(path.read_bytes()).decode("ascii"))

    return re.sub(r'src="/(images/[^"]+)"', repl, html)


def write(rel, text):
    out = HERE / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return out


# ---------------------------------------------------------------- landing

landing = (HERE / "landing-template.html").read_text(encoding="utf-8")
write(LANDING["out"], wrap(set_title(landing, LANDING["title"]), LANDING))

# -------------------------------------------------------------- catalogue

template = (HERE / "template.html").read_text(encoding="utf-8")
alternates = [("he", CATALOGUE["he"]["path"]), ("en", CATALOGUE["en"]["path"]),
              ("x-default", CATALOGUE["he"]["path"])]

for lang, page in CATALOGUE.items():
    html = strip_lang(template, "en" if lang == "he" else "he")
    html = set_title(html, page["title"])
    # one language per page, so the runtime toggle becomes plain navigation
    html = re.sub(r'  <div class="langswitch".*?</div>', language_links(lang), html, count=1, flags=re.S)
    html = re.sub(r"<script>.*?</script>\s*$", "", html, flags=re.S).rstrip() + "\n"
    html = html.replace(
        '<div class="page" id="page" data-lang="he" dir="rtl" lang="he">',
        '<div class="page" id="page" data-lang="%s" dir="%s" lang="%s">' % (lang, page["dir"], lang),
    )
    write(page["out"], wrap(html, page, alternates, lang))
    if lang == "he":
        write("index-artifact.html", inline_images(html))

# ------------------------------------------------------------------ vcard
# Keeps its runtime toggle: it is a utility page nobody searches for, and a
# reload to translate a phone number is not worth it.

card = (HERE / "card-template.html").read_text(encoding="utf-8")
card = set_title(card, VCARD["title"]).replace('href="michael.vcf"', 'href="/michael.vcf"')
write(VCARD["out"], wrap(card, VCARD))
write("card-artifact.html", inline_images(card))

for f in sorted(HERE.rglob("*.html")):
    if "images" in f.parts:
        continue
    print(str(f.relative_to(HERE)).replace("\\", "/"), f.stat().st_size // 1024, "KB")
