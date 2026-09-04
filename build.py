"""Builds the whole site from the templates.

Site layout:
  /                  landing page, holding the root for the real site later
  /catalogue/        the catalogue in Hebrew
  /catalogue/en/     the catalogue in English
  /vcard/            digital business card, parked; nothing links to it yet

The two catalogue languages are separate pages rather than one page with a
toggle, so a link can be shared in either language and each URL declares one
language to search engines. Both come from the same template: the build strips
the other language's spans and turns the toggle into links.

Structured data is generated, not hand-written. The six products are parsed
back out of the template so the markup can never drift from the visible page,
which is the usual way this kind of thing quietly goes stale.

Every URL derives from SITE_URL. robots.txt and sitemap.xml live in
make_seo.py; the poster and its QR in make_poster.py; the favicon set in
make_favicon.py; the link-preview image in make_og.py.

Run `py build.py` after editing any template. Never hand-edit the output.
"""

import base64
import html as html_mod
import json
import mimetypes
import pathlib
import re

HERE = pathlib.Path(__file__).parent
SITE_URL = "https://mushroomkingdom.co.il"

CATALOGUE = {
    "he": {
        "out": "catalogue/index.html",
        "path": "/catalogue/",
        "dir": "rtl",
        "title": "ממלכת הפטריות | פטריות שף וגורמה בגידול אורגני",
        "description": "קטלוג פטריות שף וגורמה בגידול אורגני: רעמת האריה, צדף ורודה, כחולה, צהובה ולבנה ופנינה שחורה. ישירות מהמגדל, בצפון הארץ.",
    },
    "en": {
        "out": "catalogue/en/index.html",
        "path": "/catalogue/en/",
        "dir": "ltr",
        "title": "Mushroom Kingdom | Gourmet & Chef Mushrooms, Organically Grown",
        "description": "A catalogue of organically grown gourmet mushrooms: lion's mane, pink, blue, golden and white oyster, and black pearl oyster. Direct from the grower in northern Israel.",
    },
}

LANDING = {
    "out": "index.html",
    "path": "/",
    "dir": "rtl",
    "title": "ממלכת הפטריות | פטריות שף בגידול אורגני",
    "description": "ממלכת הפטריות. פטריות שף וגורמה בגידול אורגני, ישירות מהמגדל. האתר המלא יעלה בקרוב.",
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
    # LocalBusiness alongside Organization: with a real address this is what
    # feeds local results, and Organization alone does not.
    "@type": ["Organization", "LocalBusiness"],
    "name": "ממלכת הפטריות",
    "alternateName": "Mushroom Kingdom",
    "description": "חוות פטריות שף וגורמה בגידול אורגני, בצפון הארץ.",
    "url": SITE_URL + "/",
    "logo": SITE_URL + "/images/favicon-512.png",
    "image": SITE_URL + "/images/og.jpg",
    "foundingDate": "2022",
    "telephone": "+972-52-705-0501",
    "sameAs": [
        "https://instagram.com/mushrooms.kingdomm",
        "https://www.facebook.com/Mushroomskingdomm/",
    ],
    "areaServed": {"@type": "Country", "name": "Israel"},
    # The full address, matching what the business already publishes on
    # Facebook. Google cross-references name, address and phone across the
    # web, so an address that differs from the Facebook listing would be a
    # weaker signal than either one alone.
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "התורן 22",
        "addressLocality": "מגדים",
        "addressRegion": "צפון",
        "addressCountry": "IL",
    },
    "contactPoint": {
        "@type": "ContactPoint",
        "contactType": "sales",
        "telephone": "+972-52-705-0501",
        "availableLanguage": ["he", "en"],
    },
}

NEWLINE = "\n"


def ld(data):
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            + "</script>" + NEWLINE)


def parse_products(template):
    """Pull the six mushrooms back out of the template.

    Generating the product markup from the same source as the visible page is
    the only way to stop the two drifting apart as copy gets edited.
    """
    products = []
    for block in re.findall(r'<article class="plate">.*?</article>', template, re.S):
        def span(cls, wrapper):
            m = re.search(r'<%s[^>]*>(.*?)</%s>' % (wrapper, wrapper), block, re.S)
            if not m:
                return ""
            m2 = re.search(r'<span class="when-%s[^"]*">(.*?)</span>' % cls, m.group(1), re.S)
            return html_mod.unescape(re.sub(r"\s+", " ", m2.group(1)).strip()) if m2 else ""

        text = re.search(r'<p class="spec-text">(.*?)</p>', block, re.S).group(1)
        def body(cls):
            m = re.search(r'<span class="when-%s[^"]*">(.*?)</span>' % cls, text, re.S)
            return html_mod.unescape(re.sub(r"\s+", " ", m.group(1)).strip()) if m else ""

        products.append({
            "he": span("he", "h2"),
            "en": span("en", "h2"),
            "sci": html_mod.unescape(re.search(r'<p class="spec-sci">(.*?)</p>', block, re.S).group(1).strip()),
            "image": SITE_URL + re.search(r'<img src="(/images/[^"]+)"', block).group(1),
            "desc_he": body("he"),
            "desc_en": body("en"),
        })
    return products


def product_list(products, lang, page):
    """The catalogue is a list of products, so say so. Deliberately no offers:
    there are no prices, and inventing availability would be a lie."""
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": page["title"],
        "numberOfItems": len(products),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "item": {
                    "@type": "Product",
                    "name": p["he"] if lang == "he" else p["en"],
                    "alternateName": p["en"] if lang == "he" else p["he"],
                    "description": p["desc_he"] if lang == "he" else p["desc_en"],
                    "image": p["image"],
                    "category": "פטריות שף" if lang == "he" else "Gourmet mushrooms",
                    "additionalProperty": {
                        "@type": "PropertyValue",
                        "name": "Scientific name",
                        "value": p["sci"],
                    },
                    "brand": {"@type": "Brand", "name": ORGANISATION["name"]},
                },
            }
            for i, p in enumerate(products)
        ],
    }


def head_meta(page, alternates=()):
    """Description, canonical and the Open Graph tags that make a shared link
    render as a card with a photograph instead of a bare URL. WhatsApp,
    Facebook and Telegram all read these; og:image must be absolute."""
    tags = (
        '<meta name="description" content="{description}">' + NEWLINE
        + '<link rel="canonical" href="{site}{path}">' + NEWLINE
        + '<meta property="og:type" content="website">' + NEWLINE
        + '<meta property="og:site_name" content="ממלכת הפטריות">' + NEWLINE
        + '<meta property="og:title" content="{title}">' + NEWLINE
        + '<meta property="og:description" content="{description}">' + NEWLINE
        + '<meta property="og:url" content="{site}{path}">' + NEWLINE
        + '<meta property="og:image" content="{site}/images/og.jpg">' + NEWLINE
        + '<meta property="og:image:type" content="image/jpeg">' + NEWLINE
        + '<meta property="og:image:width" content="1200">' + NEWLINE
        + '<meta property="og:image:height" content="630">' + NEWLINE
        + '<meta property="og:image:alt" content="פטריות צדף ורודה טריות עם הסמל של ממלכת הפטריות">' + NEWLINE
        + '<meta name="twitter:card" content="summary_large_image">' + NEWLINE
    ).format(site=SITE_URL, **page)
    for lang, path in alternates:
        tags += '<link rel="alternate" hreflang="%s" href="%s%s">%s' % (lang, SITE_URL, path, NEWLINE)
    return tags


ICONS = (
    '<link rel="icon" href="/favicon.ico" sizes="any">' + NEWLINE
    + '<link rel="icon" type="image/png" sizes="32x32" href="/images/favicon-32.png">' + NEWLINE
    + '<link rel="icon" type="image/png" sizes="192x192" href="/images/favicon-192.png">' + NEWLINE
    + '<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">' + NEWLINE
    + '<meta name="theme-color" content="#171512">' + NEWLINE
)


def wrap(body, page, alternates=(), lang="he", extra_ld=None):
    schema = ld(ORGANISATION) + (ld(extra_ld) if extra_ld else "")
    return (
        "<!doctype html>" + NEWLINE
        + '<html lang="%s" dir="%s">' % (lang, page["dir"]) + NEWLINE
        + "<head>" + NEWLINE
        + '<meta charset="utf-8">' + NEWLINE
        + '<meta name="viewport" content="width=device-width, initial-scale=1">' + NEWLINE
        + ICONS
        + head_meta(page, alternates)
        + schema
        + "</head>" + NEWLINE + "<body>" + NEWLINE
        + body
        + NEWLINE + "</body>" + NEWLINE + "</html>" + NEWLINE
    )


def set_title(html, title):
    return re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, html, count=1, flags=re.S)


def strip_lang(html, drop):
    return re.sub(r'\s*<span class="when-%s[^"]*">.*?</span>' % drop, "", html, flags=re.S)


def language_links(current):
    def cell(lang, label):
        mark = ' aria-current="page"' if lang == current else ""
        return '    <a href="%s"%s>%s</a>' % (CATALOGUE[lang]["path"], mark, label)
    return ('  <div class="langswitch" role="group" aria-label="Language / שפה">' + NEWLINE
            + cell("he", "HEB") + NEWLINE + cell("en", "EN") + NEWLINE + "  </div>")


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
products = parse_products(template)
alternates = [("he", CATALOGUE["he"]["path"]), ("en", CATALOGUE["en"]["path"]),
              ("x-default", CATALOGUE["he"]["path"])]

for lang, page in CATALOGUE.items():
    html = strip_lang(template, "en" if lang == "he" else "he")
    html = set_title(html, page["title"])
    html = re.sub(r'  <div class="langswitch".*?</div>', language_links(lang), html, count=1, flags=re.S)
    html = re.sub(r"<script>.*?</script>\s*$", "", html, flags=re.S).rstrip() + NEWLINE
    html = html.replace(
        '<div class="page" id="page" data-lang="he" dir="rtl" lang="he">',
        '<div class="page" id="page" data-lang="%s" dir="%s" lang="%s">' % (lang, page["dir"], lang),
    )
    write(page["out"], wrap(html, page, alternates, lang, product_list(products, lang, page)))
    if lang == "he":
        write("index-artifact.html", inline_images(html))

# ------------------------------------------------------------------ vcard

card = (HERE / "card-template.html").read_text(encoding="utf-8")
card = set_title(card, VCARD["title"]).replace('href="michael.vcf"', 'href="/michael.vcf"')
write(VCARD["out"], wrap(card, VCARD))
write("card-artifact.html", inline_images(card))

print("parsed %d products from the template" % len(products))
for f in sorted(HERE.rglob("*.html")):
    if "images" in f.parts:
        continue
    print(" ", str(f.relative_to(HERE)).replace("\\", "/"), f.stat().st_size // 1024, "KB")
