"""Build the PC reader for the user, or a reader pack with one or more chapters to add to it.

    python tools/reader/build_reader.py                 # dist/Storyteller-Reader.zip: the reader, with the chapters in series.js
    python tools/reader/build_reader.py --pack 094      # dist/reader-pack_094.zip: chapters to drop into "new chapters"
    python tools/reader/build_reader.py --pack 094 --with-reader   # the same, plus the newest reader page (index.html, series.js)

The chapter images are not in git: they come from the chapter zips (put them in site/chapters/<id>/ first).
"""

import argparse
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


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pack", nargs="+", metavar="ID", help="make a reader pack with these chapters")
    parser.add_argument("--with-reader", action="store_true", help="put the reader page and series.js in the pack too")
    args = parser.parse_args()
    DIST.mkdir(exist_ok=True)

    if args.pack:
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
