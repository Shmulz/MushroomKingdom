"""Builds poster.html, the printable A4 sheet carrying the QR code.

The QR and the printed address both point at the catalogue, not the vcard:
the poster already shows the phone number and the Instagram handle, so the
code should deliver the one thing paper cannot, which is the products.

POSTER_URL is the live address once the domain resolves. Until then the code
on the poster will not open anything, which is why nothing gets printed
before the DNS switch.
"""

import pathlib
import re

import segno

HERE = pathlib.Path(__file__).parent
# Apex, not www, so the code matches the address printed beside it and a
# scan lands directly instead of taking a redirect hop.
POSTER_URL = "https://mushroomkingdom.co.il/catalogue/"
PRINTED_URL = "MushroomKingdom.co.il/catalogue"   # host is case-insensitive; camel case only for legibility


def make_qr(url):
    qr = segno.make(url, error="q")
    svg = qr.svg_inline(dark="#171512", light=None, border=2)
    size = qr.symbol_size(border=2)[0]
    svg = svg.replace("<svg ", '<svg viewBox="0 0 %d %d" ' % (size, size), 1)
    return re.sub(r'(width|height)="[^"]*"', "", svg, count=2)


body = (HERE / "poster-template.html").read_text(encoding="utf-8")
body = body.replace("{{QR}}", make_qr(POSTER_URL)).replace("{{URL}}", PRINTED_URL)

(HERE / "poster.html").write_text(
    '<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n<meta charset="utf-8">\n</head>\n<body>\n'
    + body + "\n</body>\n</html>\n",
    encoding="utf-8",
)
print("poster.html ->", POSTER_URL)
