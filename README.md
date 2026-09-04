# Mushroom Kingdom / ממלכת הפטריות

Single-page online catalog and digital business card for Mushroom Kingdom,
a grower of chef and exotic mushrooms. Hebrew by default, with an English toggle.

- `index.html` - the catalog (six mushrooms, photos, descriptions, contact)
- `card.html` - digital business card, including a QR code that opens the catalog
- `*-single-file.html` - the same two pages with every image embedded, so a single
  file can be emailed or copied to a USB stick with nothing else attached

## Editing

Edit `template.html` and `card-template.html` only, then rebuild:

    py build.py

The build regenerates every output, including the QR code, from `CATALOG_URL`
in `build.py`. Do not edit the generated `index.html` or `card.html` by hand.

## Images

`images/` holds 900px square crops, one per mushroom, cropped from the grower's
originals. `logo-cream.png` is the brand seal recoloured for a dark background.
