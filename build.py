"""Builds the catalog and the digital business card from their templates.

Outputs, for each of the two pages:
  <name>.html               - normal page, loads images/ from disk (this is what gets hosted)
  <name>-single-file.html   - one self-contained file, images embedded (email / USB)
  <name>-artifact.html      - same embedded content with no <html>/<head>/<body>
                              wrapper, because the Claude Artifact host supplies those

The QR code is regenerated from CATALOG_URL every build and inlined into the
card, so changing the hosting URL only means editing the constant below.
"""

import base64
import mimetypes
import pathlib
import re

import segno

HERE = pathlib.Path(__file__).parent
CATALOG_URL = "https://shmulz.github.io/MashroomKingdom/"

DESCRIPTIONS = {
    "index": "קטלוג הפטריות של ממלכת הפטריות - פטריות שף טריות בגידול מקומי.",
    "card": "כרטיס הביקור הדיגיטלי של ממלכת הפטריות - פרטי קשר וקישור לקטלוג.",
}


def make_qr():
    qr = segno.make(CATALOG_URL, error="q")
    svg = qr.svg_inline(dark="#171512", light=None, border=2)
    # give it a viewBox so CSS can size it freely
    size = qr.symbol_size(border=2)[0]
    svg = svg.replace("<svg ", '<svg viewBox="0 0 %d %d" ' % (size, size), 1)
    return re.sub(r'(width|height)="[^"]*"', "", svg, count=2)


def wrap(body, description):
    return (
        '<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="description" content="%s">\n'
        "</head>\n<body>\n" % description + body + "\n</body>\n</html>\n"
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

for name, source in (("index", "template.html"), ("card", "card-template.html")):
    html = (HERE / source).read_text(encoding="utf-8").replace("{{QR}}", qr_svg)
    embedded = inline_images(html)
    desc = DESCRIPTIONS[name]
    (HERE / ("%s.html" % name)).write_text(wrap(html, desc), encoding="utf-8")
    (HERE / ("%s-single-file.html" % name)).write_text(wrap(embedded, desc), encoding="utf-8")
    (HERE / ("%s-artifact.html" % name)).write_text(embedded, encoding="utf-8")

for f in sorted(HERE.glob("*.html")):
    print(f.name, f.stat().st_size // 1024, "KB")
