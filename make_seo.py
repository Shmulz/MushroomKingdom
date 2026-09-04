"""Writes robots.txt and sitemap.xml.

Kept separate from build.py because these two files change only when a page is
added or removed, not when content is edited. Run it after adding a page.

Only the three pages worth ranking are listed. /vcard/ is deliberately left
out: nothing links to it and nobody searches for it. poster.html is a print
sheet, not a page, and carries its own noindex.
"""

import datetime
import pathlib

HERE = pathlib.Path(__file__).parent
SITE_URL = "https://mushroomkingdom.co.il"

INDEXABLE = ["/", "/catalogue/", "/catalogue/en/"]

robots = "\n".join([
    "User-agent: *",
    "Allow: /",
    "",
    "Sitemap: %s/sitemap.xml" % SITE_URL,
    "",
])
(HERE / "robots.txt").write_text(robots, encoding="utf-8")

today = datetime.date.today().isoformat()
entries = "\n".join(
    '  <url><loc>%s%s</loc><lastmod>%s</lastmod></url>' % (SITE_URL, path, today)
    for path in INDEXABLE
)
sitemap = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + entries + "\n</urlset>\n"
)
(HERE / "sitemap.xml").write_text(sitemap, encoding="utf-8")

print("robots.txt and sitemap.xml written for %d pages" % len(INDEXABLE))
