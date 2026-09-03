"""Builds the catalogue and the digital business card from their templates.

For each page it writes three files:
  <name>.html               - the hosted page, loads images/ from disk
  <name>-single-file.html   - self contained, images embedded (email / USB)
  <name>-artifact.html      - the same embedded content with no
                              <html>/<head>/<body> wrapper, because the Claude
                              Artifact host supplies those

Every URL on the site derives from SITE_URL below: the QR code, the canonical
links and the absolute og:image address. When the domain changes, change it
here and rerun. Nothing else hardcodes a URL.

The link-preview image itself is built separately by make_og.py, which only
needs rerunning when the photograph or the branding changes.
"""

import base64
import mimetypes
import pathlib
import re

import segno

HERE = pathlib.Path(__file__).parent

SITE_URL = "https://shmulz.github.io/MushroomKingdom"
CATALOG_URL = SITE_URL + "/"          # what the QR code on the card encodes

PAGES = {
    "index": {
        "source": "template.html",
        "url": SITE_URL + "/",
        "title": "ממלכת הפטריות | פטריות שף בגידול אורגני",
        "description": "קטלוג הפטריות של ממלכת הפטריות. פטריות שף בגידול אורגני, ישירות מהמגדל.",
    },
    "card": {
        "source": "card-template.html",
        "url": SITE_URL + "/card.html",
        "title": "ממלכת הפטריות | פרטי קשר והזמנות",
        "description": "כרטיס הביקור הדיגיטלי של ממלכת הפטריות. פרטי קשר, הזמנות וקישור לקטלוג.",
    },
}


def make_qr():
    qr = segno.make(CATALOG_URL, error="q")
    svg = qr.svg_inline(dark="#171512", light=None, border=2)
    size = qr.symbol_size(border=2)[0]
    svg = svg.replace("<svg ", '<svg viewBox="0 0 %d %d" ' % (size, size), 1)
    return re.sub(r'(width|height)="[^"]*"', "", svg, count=2)


def head_meta(page):
    """Description, canonical, and the Open Graph tags that make a shared link
    render as a card with a photograph instead of a bare URL. WhatsApp,
    Facebook and Telegram all read these. og:image must be an absolute URL."""
    return (
        '<meta name="description" content="{description}">\n'
        '<link rel="canonical" href="{url}">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:site_name" content="ממלכת הפטריות">\n'
        '<meta property="og:locale" content="he_IL">\n'
        '<meta property="og:title" content="{title}">\n'
        '<meta property="og:description" content="{description}">\n'
        '<meta property="og:url" content="{url}">\n'
        '<meta property="og:image" content="{site}/images/og.jpg">\n'
        '<meta property="og:image:type" content="image/jpeg">\n'
        '<meta property="og:image:width" content="1200">\n'
        '<meta property="og:image:height" content="630">\n'
        '<meta property="og:image:alt" content="פטריות צדף ורודה טריות עם הסמל של ממלכת הפטריות">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
    ).format(site=SITE_URL, **page)


def wrap(body, page):
    return (
        '<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        + head_meta(page)
        + "</head>\n<body>\n" + body + "\n</body>\n</html>\n"
    )


def inline_images(html):
    def repl(match):
        path = HERE / match.group(1)
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return 'src="data:%s;base64,%s"' % (mime, data)

    return re.sub(r'src="(images/[^"]+)"', repl, html)


qr_svg = make_qr()
(HERE / "images" / "qr.svg").write_text(qr_svg, encoding="utf-8")

for name, page in PAGES.items():
    html = (HERE / page["source"]).read_text(encoding="utf-8").replace("{{QR}}", qr_svg)
    embedded = inline_images(html)
    (HERE / ("%s.html" % name)).write_text(wrap(html, page), encoding="utf-8")
    (HERE / ("%s-single-file.html" % name)).write_text(wrap(embedded, page), encoding="utf-8")
    (HERE / ("%s-artifact.html" % name)).write_text(embedded, encoding="utf-8")

for f in sorted(HERE.glob("*.html")):
    print(f.name, f.stat().st_size // 1024, "KB")
