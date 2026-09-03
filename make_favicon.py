"""Builds the favicon set.

The brand seal cannot be the favicon. At 16px its ring of text and fine
engraving collapse into a smudge, and cropping to just the mushroom cluster is
only marginally better; both were rendered and compared before this was drawn
instead.

So the icon is a drawn mushroom in the brand cream on the brand ground. Three
details carry it, each added because the version without it failed:

  thick stem   a dome on a thin stem reads as an umbrella
  gill line    a sliver of ground under the cap, so cap and stem read as two
               parts rather than one continuous shaft
  flared foot  the skirt at the base is the silhouette cue that says mushroom
               rather than lamp or tree

Run only when the branding changes. build.py wires the output into every page.
"""

import math
import pathlib

from PIL import Image, ImageDraw

S = 1024                      # drawn large, downscaled, so the edges stay clean
GROUND = (23, 21, 18)
CREAM = (242, 237, 227)
HERE = pathlib.Path(__file__).parent

STEM_TOP, STEM_BOTTOM = 520, 826
HALF_TOP, HALF_BOTTOM = 118, 210      # the flare
FLARE_POWER = 2.4                     # most of the widening happens near the foot


def stem_outline():
    right, left = [], []
    steps = 60
    for i in range(steps + 1):
        t = i / steps
        y = STEM_TOP + (STEM_BOTTOM - STEM_TOP) * t
        half = HALF_TOP + (HALF_BOTTOM - HALF_TOP) * (t ** FLARE_POWER)
        right.append((512 + half, y))
        left.append((512 - half, y))
    foot = [
        (512 + HALF_BOTTOM * math.cos(math.pi * i / 24), STEM_BOTTOM + 26 * math.sin(math.pi * i / 24))
        for i in range(1, 24)
    ]
    return right + foot + left[::-1]


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
    d.polygon(stem_outline(), fill=CREAM)                              # flared stem

    return im.resize((size, size), Image.LANCZOS)


images = HERE / "images"
for size in (16, 32, 48, 192, 512):
    mark(size).save(images / ("favicon-%d.png" % size), optimize=True)

# iOS applies its own rounded mask, so this one is square and opaque
mark(180, rounded=False).convert("RGB").save(images / "apple-touch-icon.png", optimize=True)

mark(48).save(HERE / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

print("favicon set rebuilt")
