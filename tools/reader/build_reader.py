"""Build the PC reader for the user, or a reader pack with one or more chapters to add to it.

    python tools/reader/build_reader.py                 # dist/Storyteller-Reader.zip: the reader, with the chapters in series.js
    python tools/reader/build_reader.py --pack 094      # dist/reader-pack_094.zip: chapters to drop into "new chapters"
    python tools/reader/build_reader.py --pack 094 --with-reader   # the same, plus the newest reader page (index.html, series.js)
    python tools/reader/build_reader.py --site          # dist/Storyteller-Site.zip: the reader as a website, for Cloudflare Pages
    python tools/reader/build_reader.py --site --chapters 094-demo --public https://tbate-scroll-demo.pages.dev \
        --cover site/chapters/094-demo/cover.jpg --out Storyteller-Demo.zip   # the public demo, with a link preview

The chapter images are not in git: they come from the chapter zips (put them in site/chapters/<id>/ first).
"""

import argparse
import html
import json
import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SITE = REPO / "site"
HERE = Path(__file__).resolve().parent
DIST = REPO / "dist"


def series_chapters():
    text = (SITE / "series.js").read_text(encoding="utf-8")
    block = text[text.index("chapters:"):text.index("],", text.index("chapters:"))]
    return re.findall(r'\bid:\s*"([^"]+)"', block)


def chapter_files(cid):
    folder = SITE / "chapters" / cid
    files = sorted(p for p in folder.iterdir() if p.suffix in (".js", ".webp")) if folder.is_dir() else []
    if not any(p.name == "chapter.js" for p in files) or not any(p.suffix == ".webp" for p in files):
        sys.exit(f"site/chapters/{cid} needs its chapter.js and images (unzip the chapter zip's WebP files into it).")
    return files


def reader_files():
    yield SITE / "index.html", "index.html"
    yield SITE / "series.js", "series.js"
    for folder in ("music", "sfx"):
        for p in sorted((SITE / folder).glob("*.mp3")):
            yield p, f"{folder}/{p.name}"


# for the website: open to anyone with the address, but kept out of search engines
SITE_HEADERS = """/*
  X-Robots-Tag: noindex, nofollow, noimageindex
"""
ROBOTS = "User-agent: *\nDisallow: /\n"


def chapter_entry(cid):
    """The series.js line for a chapter, from its chapter.js."""
    text = (SITE / "chapters" / cid / "chapter.js").read_text(encoding="utf-8")
    head = text[text.index("registerChapter("):text.index("scenes:")]
    title = re.search(r'\btitle:\s*"((?:[^"\\]|\\.)*)"', head).group(1)
    number = re.search(r"\bnumber:\s*([0-9.]+|null)", head).group(1)
    panels = len(re.findall(r'\{\s*id:\s*"panel_', text))
    return f'    {{ id: {json.dumps(cid)}, title: "{title}", number: {number}, panels: {panels} }},'


def site_series(chapters):
    """series.js with its chapter list set to these chapters."""
    text = (SITE / "series.js").read_text(encoding="utf-8")
    a = text.index("chapters: [") + len("chapters: [")
    z = text.index("],", a)
    return text[:a] + "\n" + "\n".join(chapter_entry(c) for c in chapters) + "\n  " + text[z:]


def site_page(url, cover, description):
    """index.html with a page title and the tags LinkedIn (and others) read for the link preview."""
    page = (SITE / "index.html").read_text(encoding="utf-8")
    title = "The Duel | Storyteller, a scroll-driven manhwa reader"
    tags = [f'<meta name="description" content="{html.escape(description)}">',
            f'<meta property="og:type" content="website">',
            f'<meta property="og:title" content="{html.escape(title)}">',
            f'<meta property="og:description" content="{html.escape(description)}">',
            f'<meta property="og:url" content="{url}/">']
    if cover:
        tags += [f'<meta property="og:image" content="{url}/cover.jpg">', '<meta property="og:image:width" content="1200">',
                 '<meta property="og:image:height" content="627">', '<meta name="twitter:card" content="summary_large_image">']
    page = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>\n" + "\n".join(tags), page, count=1)
    return page


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pack", nargs="+", metavar="ID", help="make a reader pack with these chapters")
    parser.add_argument("--with-reader", action="store_true", help="put the reader page and series.js in the pack too")
    parser.add_argument("--site", action="store_true", help="make the website zip (reader files at the top, no PC tools)")
    parser.add_argument("--chapters", nargs="+", metavar="ID", help="the website's chapters (default: those in series.js)")
    parser.add_argument("--public", metavar="URL", help="a public site at this address: link-preview tags, search engines allowed")
    parser.add_argument("--cover", help="the link-preview image (1200 x 627 JPEG)")
    parser.add_argument("--out", help="the zip's name in dist/")
    args = parser.parse_args()
    DIST.mkdir(exist_ok=True)

    if args.site:
        out = DIST / (args.out or "Storyteller-Site.zip")
        chapters = args.chapters or series_chapters()
        url = args.public.rstrip("/") if args.public else None
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for p, name in reader_files():
                if name == "index.html" and url:
                    z.writestr(name, site_page(url, args.cover, "A webcomic chapter that plays like a film as you scroll: "
                                              "panels split into layers by AI, then directed scene by scene. A fan tech demo."))
                elif name == "series.js":
                    z.writestr(name, site_series(chapters))
                else:
                    z.write(p, name)
            for cid in chapters:
                for p in chapter_files(cid):
                    z.write(p, f"chapters/{cid}/{p.name}", zipfile.ZIP_STORED)
            if args.cover:
                z.write(args.cover, "cover.jpg", zipfile.ZIP_STORED)
            if not url:  # the friends' site: kept out of search engines (LinkedIn's preview reads robots.txt too)
                z.writestr("_headers", SITE_HEADERS)
                z.writestr("robots.txt", ROBOTS)
    elif args.pack:
        out = DIST / f"reader-pack_{'_'.join(args.pack)}.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as z:  # WebP and MP3 are already compressed
            for cid in args.pack:
                for p in chapter_files(cid):
                    z.write(p, f"chapters/{cid}/{p.name}")
            if args.with_reader:
                for p, name in reader_files():
                    if name.endswith((".html", ".js")):
                        z.write(p, name)
    else:
        out = DIST / "Storyteller-Reader.zip"
        top = "Storyteller Reader"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for name in ("Read Storyteller.bat", "README.txt", "reader.py"):
                z.write(HERE / name, f"{top}/{name}")
            z.writestr(f"{top}/new chapters/", "")
            for p, name in reader_files():
                z.write(p, f"{top}/reader/{name}")
            for cid in series_chapters():
                for p in chapter_files(cid):
                    z.write(p, f"{top}/reader/chapters/{cid}/{p.name}", zipfile.ZIP_STORED)
    print(f"Wrote {out.relative_to(REPO)} ({out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
