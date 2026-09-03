"""Builds images/og.jpg, the link-preview image shown when the site is shared
on WhatsApp, Facebook, Telegram and the like.

1200x630 is the size those services crop to. Run this only when the photo or
the branding changes; build.py does not regenerate it.

Layout: the photograph keeps its full colour in the upper band and the type
sits on solid ground below it, with the seal straddling the join. Darkening
the whole photograph to make the text readable was tried first and it turned
the pink oysters brown, which is the one thing this image exists to show.

Hebrew is drawn right to left by reversing the string, which is correct for
plain Hebrew with no embedded Latin text or digits. If you ever add either,
this needs a real bidi library instead.
"""

import pathlib

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

HERE = pathlib.Path(__file__).parent
W, H = 1200, 630
PHOTO_H = 250          # where the photograph gives way to solid ground
FADE = 42              # soft join, so the edge is not a hard line

SOURCE_PHOTO = HERE / "images" / "card_hero.jpg"
LOGO = HERE / "images" / "logo-cream.png"
OUT = HERE / "images" / "og.jpg"

GROUND = (23, 21, 18)
CREAM = (242, 237, 227)
OCHRE = (200, 151, 63)

HEB_BOLD = r"C:\Windows\Fonts\FrankRuehlCLM-Bold.otf"
LATIN = r"C:\Windows\Fonts\arialbd.ttf"


def heb(s):
    """Reverse for right-to-left drawing. Plain Hebrew only."""
    return s[::-1]


canvas = Image.new("RGB", (W, H), GROUND)

photo = ImageOps.exif_transpose(Image.open(SOURCE_PHOTO)).convert("RGB")
photo = ImageOps.fit(photo, (W, PHOTO_H), Image.LANCZOS, centering=(0.5, 0.42))
photo = ImageEnhance.Color(photo).enhance(1.12)
canvas.paste(photo, (0, 0))

# fade the bottom of the photograph into the ground
fade = Image.new("L", (1, FADE))
for y in range(FADE):
    fade.putpixel((0, y), int(255 * (y / FADE) ** 0.85))
region = (0, PHOTO_H - FADE, W, PHOTO_H)
canvas.paste(
    Image.composite(
        Image.new("RGB", (W, FADE), GROUND),
        canvas.crop(region),
        fade.resize((W, FADE)),
    ),
    region,
)

draw = ImageDraw.Draw(canvas)

logo = Image.open(LOGO).convert("RGBA")
logo.thumbnail((232, 232), Image.LANCZOS)
# sit the seal mostly on the solid ground, only its top edge on the photo
canvas.paste(logo, ((W - logo.width) // 2, PHOTO_H - logo.height // 3), logo)

f_brand = ImageFont.truetype(HEB_BOLD, 92)
f_latin = ImageFont.truetype(LATIN, 25)


def centred(text, font, y, fill, spacing=0):
    if spacing:
        widths = [draw.textlength(c, font=font) for c in text]
        total = sum(widths) + spacing * (len(text) - 1)
        x = (W - total) / 2
        for c, cw in zip(text, widths):
            draw.text((x, y), c, font=font, fill=fill)
            x += cw + spacing
    else:
        draw.text(((W - draw.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)


centred(heb("ממלכת הפטריות"), f_brand, 424, CREAM)
centred("MUSHROOMS KINGDOM", f_latin, 550, OCHRE, spacing=7)

canvas.save(OUT, quality=88, optimize=True, progressive=True)
print("og.jpg", OUT.stat().st_size // 1024, "KB", canvas.size)
