"""Builds the four printable posters from one template.

    poster-A4-press.html    dark, full-bleed photograph, A4
    poster-A4-home.html     light, photo reduced to a band, A4
    poster-A5-press.html    the A4 press sheet scaled to A5
    poster-A5-home.html     the A4 home sheet scaled to A5

Press versus home is not a size difference, it is an ink difference. The press
sheet covers the page in a dark photograph, which looks excellent from a real
printer and terrible from an office inkjet: large flat dark areas band, and the
edges of the white QR panel smear, which is the one element that has to stay
sharp enough to scan. The home sheet keeps the photograph as a band at the top
and sets everything else as dark ink on white, so it costs little to print and
the code stays crisp.

No bleed and no crop marks. The print shop handles trim, and the sheet has
square corners.

A5 is the A4 sheet scaled rather than a separate layout, so the two can never
drift apart. The scale is width-exact; the fraction of a millimetre left at
the foot is filled with the sheet's own background colour.

The QR and the printed address both point at the catalogue, not the vcard: the
poster already carries the phone number and the handle, so the code should
deliver the thing paper cannot.
"""

import pathlib
import re

import segno

HERE = pathlib.Path(__file__).parent
POSTER_URL = "https://mushroomkingdom.co.il/catalogue/"
PRINTED_URL = "MushroomKingdom.co.il/catalogue"   # host is case-insensitive; camel case for legibility

A5_SCALE = 148 / 210      # width-exact, so nothing is cropped at the sides

# Ink colours for the home sheet. The ochre is darkened: the screen value is
# too pale to hold as small text on white paper.
HOME_CSS = """
  /* ---- home print: light ground, photograph reduced to a band ---- */
  html, body { background: #FFFFFF; }

  .poster {
    background: #FFFFFF;
    color: #171512;
    justify-content: flex-start;
    padding: 40mm 12mm 12mm;
    gap: 6mm;
  }

  .poster::before { bottom: auto; height: 64mm; filter: saturate(1.12) contrast(1.02); }

  .poster::after {
    bottom: auto;
    height: 64mm;
    background: linear-gradient(to bottom,
      rgba(255, 255, 255, 0) 52%,
      rgba(255, 255, 255, 0.75) 84%,
      #FFFFFF 100%);
  }

  .seal { filter: none; }

  .brand, .claim, .qr-caption, .phone, .social { color: #171512; text-shadow: none; }
  .brand-latin, .qr-url { color: #8A6420; text-shadow: none; }

  .qr-panel { background: transparent; box-shadow: none; padding: 0; }

  .divider { background: rgba(23, 21, 18, 0.3); }

  .phone svg { color: #8A6420; }
  .ig-mark { background: #8A6420; }
  .ig-mark svg { color: #FFFFFF; }
"""


def make_qr(url):
    qr = segno.make(url, error="q")
    svg = qr.svg_inline(dark="#171512", light=None, border=2)
    size = qr.symbol_size(border=2)[0]
    svg = svg.replace("<svg ", '<svg viewBox="0 0 %d %d" ' % (size, size), 1)
    return re.sub(r'(width|height)="[^"]*"', "", svg, count=2)


def build(paper, ink):
    body = (HERE / "poster-template.html").read_text(encoding="utf-8")
    body = body.replace("{{QR}}", make_qr(POSTER_URL)).replace("{{URL}}", PRINTED_URL)

    css = ""
    if ink == "home":
        # logo.png is black line art on an opaque white disc, which is exactly
        # right on a white sheet; logo-cream.png would vanish.
        body = body.replace("/images/logo-cream.png", "/images/logo.png")
        css += HOME_CSS

    if paper == "A5":
        css += """
  /* ---- A5: the A4 sheet scaled, not a second layout ---- */
  @page { size: A5 portrait; margin: 0; }
  html, body { width: 148mm; height: 210mm; overflow: hidden; }
  .sheet { position: relative; width: 148mm; height: 210mm; overflow: hidden; }
  /* Absolute placement, because the document is right-to-left: a 210mm block
     inside a 148mm sheet would otherwise be laid out from the right edge and
     hang off the left, and the transform would then scale from a point that
     is already off the page. That cut a third off the earlier A5. */
  .poster {
    position: absolute;
    top: 0;
    left: 0;
    width: 210mm;
    height: 297mm;
    transform: scale(%.5f);
    transform-origin: top left;
  }
""" % A5_SCALE
        body = body.replace('<div class="poster">', '<div class="sheet"><div class="poster">')
        body = body.rstrip()
        assert body.endswith("</div>")
        body = body + "</div>"

    if css:
        body = body.replace("</style>", css + "</style>", 1)

    out = HERE / ("poster-%s-%s.html" % (paper, ink))
    out.write_text(
        '<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="robots" content="noindex">\n</head>\n<body>\n'
        + body + "\n</body>\n</html>\n",
        encoding="utf-8",
    )
    return out


for paper in ("A4", "A5"):
    for ink in ("press", "home"):
        f = build(paper, ink)
        print(f.name, f.stat().st_size // 1024, "KB")

print("QR ->", POSTER_URL)
