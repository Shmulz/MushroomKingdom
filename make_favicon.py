"""Builds the favicon set.

The brand seal cannot be the favicon. At 16px its ring of text and fine
engraving collapse into a smudge, and cropping to just the mushroom cluster
is only marginally better; both were rendered and compared before this was
drawn instead.

So the icon is a drawn mushroom in the brand cream on the brand ground. Two
details do the work: the stem is thick, because a dome on a thin stem reads
as an umbrella, and a sliver of ground under the cap stands in for the gills,
which stops the cap and stem merging into one shape.

Run only when the branding changes. Outputs favicon.ico plus PNGs, all wired
into every page by build.py.
"""

import pathlib

from PIL import Image, ImageDraw

S = 1024                      # drawn large, downscaled, so the edges stay clean
GROUND = (23, 21, 18)
CREAM = (242, 237, 227)
HERE = pathlib.Path(__file__).parent


def mark(size, rounded=True):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if rounded:
        d.rounded_rectangle((0, 0, S - 1, S - 1), radius=196, fill=GROUND + (255,))
    else:
        d.rectangle((0, 0, S - 1, S - 1), fill=GROUND + (255,))

    d.chord((132, 268, 892, 720), 180, 360, fill=CREAM)               # cap dome
    d.rounded_rectangle((132, 468, 892, 560), radius=44, fill=CREAM)  # cap rim
    d.rounded_rectangle((176, 536, 848, 576), radius=20,
                        fill=GROUND + (255,))                          # gills
    d.rounded_rectangle((386, 520, 638, 842), radius=54, fill=CREAM)   # stem

    return im.resize((size, size), Image.LANCZOS)


images = HERE / "images"
for size in (16, 32, 48, 192, 512):
    mark(size).save(images / ("favicon-%d.png" % size), optimize=True)

# iOS applies its own rounded mask, so this one is square and opaque
mark(180, rounded=False).convert("RGB").save(images / "apple-touch-icon.png", optimize=True)

mark(48).save(HERE / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

print("favicon set rebuilt")
