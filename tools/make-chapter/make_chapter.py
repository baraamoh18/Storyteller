"""Turn downloaded chapters (CBZ files) into ready-to-direct chapters for the scroll reader.

For each chapter it:
  1. finds the chapter's CBZ by its number ("..._94_-_Chapter_94.cbz" is chapter 94),
  2. takes out the pages in order and drops the series title page and the creators' promo page
     (recognised by their look; pages can also be dropped by hand with --skip),
  3. joins the pages into one long strip and splits it into panels, characters, bubbles and filled
     backgrounds with split_layers.py,
  4. converts everything to WebP for the web, works out which panel each speech bubble belongs to,
     and draws overview sheets of the pages, panels and bubbles for the director,
  5. saves the result as <out>/chapter_<id>.zip (about 7-10 MB): the only file it writes to <out>.

Chapters already done are skipped, so a batch can be restarted after Colab disconnects.

Usage:
    python make_chapter.py --cbz-dir CBZ_FOLDER --out OUT_FOLDER --chapters 1-5,94 [--skip '{"94": [0, 69]}'] [--redo]
"""

import argparse
import json
import re
import shutil
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None  # a joined chapter is one very tall picture

IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".webp", ".avif"}
WEBP = {"background": 80, "characters": 85, "bubble": 90}

# Fingerprints (difference hashes, 16 x 32) of pages that are not part of the story, taken from chapter 94.
# Only the first two and last two pages of a chapter are compared with them.
NON_STORY = {
    "series title page": "00000000040040000d004ca064a07d70b4647cf82d0c1c003260b4f0347003000f9006800cc00ec0030007000600000000000000000000000000c0000000f634",
    "creators' promo page": "000000000000000000000000000000000000000000000000000000002200000004001900268043404f40d901191c0d634f332a349a9b42780160000000000000",
}
MATCH_BITS = 110  # of 512; the closest story page in chapter 94 differs from these by 156


# ---------------------------------------------------------------- chapters and pages

def chapter_number(path):
    """'The_Beginning_After_the_End_94_-_Chapter_94.cbz' -> '94' (also '94.5'); None if there is no number."""
    m = re.search(r"chapter[\s_-]*(\d+(?:\.\d+)?)", path.stem, re.I) or re.search(r"(\d+(?:\.\d+)?)(?!.*\d)", path.stem)
    if not m:
        return None
    whole, _, part = m.group(1).partition(".")
    return str(int(whole)) + (f".{part}" if part else "")


def chapter_id(number):
    """'94' -> '094', '94.5' -> '094-5': the folder name and the reader's #address."""
    whole, _, part = number.partition(".")
    return whole.zfill(3) + (f"-{part}" if part else "")


def parse_chapters(text):
    """'1-5,94,100.5' -> a test that says whether a chapter number is wanted."""
    ranges = []
    for part in filter(None, (p.strip() for p in text.split(","))):
        a, _, b = part.partition("-")
        ranges.append((float(a), float(b or a)))
    return lambda n: any(a <= float(n) <= b for a, b in ranges)


def natural_key(name):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def extract_pages(cbz, into):
    into.mkdir(parents=True, exist_ok=True)
    pages = []
    with zipfile.ZipFile(cbz) as z:
        names = [n for n in z.namelist()
                 if Path(n).suffix.lower() in IMAGE_TYPES and not n.startswith("__MACOSX") and not n.endswith("/")]
        for k, name in enumerate(sorted(names, key=natural_key)):
            target = into / f"{k:03d}{Path(name).suffix.lower()}"
            target.write_bytes(z.read(name))
            pages.append(target)
    return pages


def dhash(image, w=16, h=32):
    g = np.asarray(image.convert("L").resize((w + 1, h), Image.LANCZOS), dtype=np.int16)
    return (g[:, 1:] > g[:, :-1]).flatten()


REFS = {why: np.unpackbits(np.frombuffer(bytes.fromhex(h), dtype=np.uint8)).astype(bool) for why, h in NON_STORY.items()}


def non_story_reason(image):
    h = dhash(image)
    for why, ref in REFS.items():
        if int((h != ref).sum()) <= MATCH_BITS:
            return why
    return None


# ---------------------------------------------------------------- overview sheets for the director

def label(draw, xy, text):
    x, y = xy
    draw.rectangle([x, y, x + 7 * len(text) + 8, y + 16], fill=(0, 0, 0))
    draw.text((x + 4, y + 2), text, fill=(255, 230, 0))


def pages_sheet(images, dropped, path):
    """Every page side by side, dropped pages crossed out in red."""
    H, cols = 330, 14
    thumbs = [im.convert("RGB").resize((max(1, round(im.width * H / im.height)), H)) for im in images]
    w = max(t.width for t in thumbs)
    sheet = Image.new("RGB", (cols * (w + 4), -(-len(thumbs) // cols) * (H + 20)), (110, 110, 110))
    d = ImageDraw.Draw(sheet)
    for k, t in enumerate(thumbs):
        x, y = (k % cols) * (w + 4), (k // cols) * (H + 20)
        sheet.paste(t, (x, y + 18))
        label(d, (x, y), f"{k:03d}" + (" DROPPED" if k in dropped else ""))
        if k in dropped:
            d.line([x, y + 18, x + t.width, y + 18 + H], fill=(230, 30, 40), width=5)
            d.line([x + t.width, y + 18, x, y + 18 + H], fill=(230, 30, 40), width=5)
    sheet.save(path, quality=80)


def panel_sheets(panel_images, folder, per_sheet=5, height=900):
    """Original panels, five per sheet, labelled with their number and size."""
    paths = []
    for s in range(0, len(panel_images), per_sheet):
        group = panel_images[s:s + per_sheet]
        thumbs = []
        for n, im in group:
            k = min(height / im.height, 420 / im.width)
            thumbs.append((n, im.size, im.convert("RGB").resize((max(1, round(im.width * k)), max(1, round(im.height * k))))))
        sheet = Image.new("RGB", (sum(t.width + 10 for _, _, t in thumbs), height + 24), (110, 110, 110))
        d = ImageDraw.Draw(sheet)
        x = 0
        for n, size, t in thumbs:
            sheet.paste(t, (x, 24))
            label(d, (x, 2), f"panel {n:02d}  {size[0]}x{size[1]}" + ("  TINY" if min(size) < 120 or size[0] * size[1] < 40000 else ""))
            x += t.width + 10
        path = folder / f"panels_{group[0][0]:02d}-{group[-1][0]:02d}.jpg"
        sheet.save(path, quality=82)
        paths.append(path)
    return paths


def bubbles_sheet(bubbles, path, height=240):
    """Every bubble on grey, labelled with its number and the panel it belongs to."""
    if not bubbles:
        return
    thumbs = []
    for b, im in bubbles:
        k = height / im.height
        bg = Image.new("RGBA", im.size, (90, 90, 90, 255))
        bg.alpha_composite(im.convert("RGBA"))
        thumbs.append((b, bg.convert("RGB").resize((max(1, round(im.width * k)), height))))
    rows, row, width = [], [], 0
    for item in thumbs:
        if row and width + item[1].width > 2400:
            rows.append(row)
            row, width = [], 0
        row.append(item)
        width += item[1].width + 8
    rows.append(row)
    sheet = Image.new("RGB", (max(sum(t.width + 8 for _, t in r) for r in rows), len(rows) * (height + 24)), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for r, items in enumerate(rows):
        x = 0
        for b, t in items:
            sheet.paste(t, (x, r * (height + 24) + 22))
            label(d, (x, r * (height + 24) + 2), f"{b['id']} > {b['panel']}" + (" ?" if b["suspect"] else ""))
            x += t.width + 8
    sheet.save(path, quality=85)


# ---------------------------------------------------------------- one chapter

def make_chapter(cbz, number, out_root, work_root, models, skip_by_hand):
    import split_layers  # sits next to this file

    cid = chapter_id(number)
    work = work_root / cid
    shutil.rmtree(work, ignore_errors=True)
    started = time.time()

    # 1-2. pages, minus the non-story ones
    files = extract_pages(cbz, work / "pages")
    if not files:
        raise RuntimeError(f"{cbz.name} has no images in it.")
    images = [Image.open(p) for p in files]
    dropped = {}
    for k in sorted(set(range(min(2, len(images)))) | set(range(max(0, len(images) - 2), len(images)))):
        why = non_story_reason(images[k])
        if why:
            dropped[k] = why
    for k in skip_by_hand:
        dropped[k if k >= 0 else len(images) + k] = "dropped by hand"
    kept = [k for k in range(len(images)) if k not in dropped]
    print(f"  {len(images)} pages; dropped: " + (", ".join(f"{k:03d} ({why})" for k, why in sorted(dropped.items())) or "none"))

    # 3. join and split. Pages of a different width (rare) are scaled to the most common one.
    widths = [images[k].width for k in kept]
    width = max(set(widths), key=widths.count)
    strip = []
    for k in kept:
        im = images[k].convert("RGB")
        if im.width != width:
            print(f"  page {k:03d} is {im.width} px wide, scaled to {width}")
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        strip.append(np.asarray(im))
    rgb = np.vstack(strip)
    del strip
    print(f"  joined strip: {rgb.shape[1]} x {rgb.shape[0]}")
    split_layers.split_image(cid, [files[k].name for k in kept], rgb, work / "layers", models)
    del rgb
    layers = work / "layers" / cid
    info = json.loads((layers / "layers.json").read_text())

    # 4. package for the web (in the scratch folder: only the zip goes to <out>, which may be Google Drive)
    out = work / "package" / cid
    (out / "sheets").mkdir(parents=True)
    panels, panel_images = [], []
    for n, p in enumerate(info["panels"], 1):
        folder = layers / p["id"]
        Image.open(folder / "background.png").convert("RGB").save(
            out / f"{p['id']}_background.webp", quality=WEBP["background"], method=6)
        Image.open(folder / "characters.png").convert("RGBA").save(
            out / f"{p['id']}_characters.webp", quality=WEBP["characters"], method=6)
        panel_images.append((n, Image.open(folder / "original.png")))
        entry = {k: p[k] for k in ("id", "x", "y", "width", "height")}
        # crumbs the panel finder picks up (a flash fragment, the tail of a bubble): the director skips them
        entry["tiny"] = min(p["width"], p["height"]) < 120 or p["width"] * p["height"] < 40000
        panels.append(entry)

    bubbles, bubble_images = [], []
    for b in info["bubbles"]:
        im = Image.open(layers / b["file"]).convert("RGBA")
        im.save(out / f"{b['id']}.webp", quality=WEBP["bubble"], method=6)
        # the panel it belongs to: the one it sits in, or else the nearest one above or below (never a tiny one)
        cx, cy = b["x"] + b["width"] / 2, b["y"] + b["height"] / 2
        real = [p for p in panels if not p["tiny"]] or panels
        owner = next((p for p in real if p["y"] <= cy <= p["y"] + p["height"] and p["x"] <= cx <= p["x"] + p["width"]), None)
        between = owner is None
        if between:
            owner = min(real, key=lambda p: min(abs(cy - p["y"]), abs(cy - (p["y"] + p["height"]))))
        entry = {
            "id": b["id"], "panel": owner["id"],
            "x": b["x"] - owner["x"], "y": b["y"] - owner["y"], "w": b["width"], "h": b["height"],  # in the panel's pixels
            "between_panels": between,
            # small, flat "bubbles" are often eyes or highlights: the director checks these
            "suspect": b["width"] * b["height"] < 12000 or min(b["width"], b["height"]) < 70,
        }
        bubbles.append(entry)
        bubble_images.append((entry, im))

    pages_sheet(images, dropped, out / "sheets" / "pages.jpg")
    panel_sheets(panel_images, out / "sheets")
    bubbles_sheet(bubble_images, out / "sheets" / "bubbles.jpg")

    chapter = {
        "id": cid, "number": number, "source": cbz.name,
        "pages": len(images), "dropped_pages": {f"{k:03d}": why for k, why in sorted(dropped.items())},
        "strip": {"width": info["width"], "height": info["height"]},
        "panels": panels, "bubbles": bubbles,
        "webp_quality": WEBP,
    }
    (out / "chapter.json").write_text(json.dumps(chapter, indent=2))

    # 5. one zip to send to the director. Built locally, then moved into <out> whole, so a disconnect
    # halfway never leaves a broken zip that looks finished.
    local_zip = work / f"chapter_{cid}.zip"
    with zipfile.ZipFile(local_zip, "w", zipfile.ZIP_STORED) as z:  # WebP and JPEG are already compressed
        for f in sorted(out.rglob("*")):
            if f.is_file():
                z.write(f, f"{cid}/{f.relative_to(out)}")
    zip_path = out_root / local_zip.name
    partial = out_root / (local_zip.name + ".part")
    shutil.copyfile(local_zip, partial)
    partial.replace(zip_path)
    shutil.rmtree(work, ignore_errors=True)
    size = zip_path.stat().st_size / 1e6
    minutes = (time.time() - started) / 60
    tiny = sum(p["tiny"] for p in panels)
    print(f"  done: {len(panels)} panels ({tiny} tiny), {len(bubbles)} bubbles -> {zip_path.name} ({size:.1f} MB) in {minutes:.1f} min")
    return zip_path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cbz-dir", required=True, help="the folder with the chapter CBZ files")
    parser.add_argument("--out", required=True, help="where the finished chapters go")
    parser.add_argument("--chapters", required=True, help='which chapters: "94", "1-5", "1-5,94"')
    parser.add_argument("--skip", default="{}", help='pages to drop by hand, per chapter: \'{"94": [0, 69]}\' (-1 is the last page)')
    parser.add_argument("--work", default="work", help="a scratch folder (default: work)")
    parser.add_argument("--redo", action="store_true", help="make chapters again even if their zip already exists")
    parser.add_argument("--models", help="cutout models, as in split_layers.py (default: its choice)")
    args = parser.parse_args()

    wanted = parse_chapters(args.chapters)
    skip = {str(k): v for k, v in json.loads(args.skip).items()}
    cbz_dir, out_root, work_root = Path(args.cbz_dir), Path(args.out), Path(args.work)
    out_root.mkdir(parents=True, exist_ok=True)

    found = {}
    for f in sorted(cbz_dir.iterdir(), key=lambda p: natural_key(p.name)):
        if f.suffix.lower() in {".cbz", ".zip"}:
            n = chapter_number(f)
            if n is not None and wanted(n):
                found.setdefault(n, f)
    if not found:
        raise SystemExit(f"No CBZ files for chapters {args.chapters} in {cbz_dir}.")
    todo = {n: f for n, f in found.items() if args.redo or not (out_root / f"chapter_{chapter_id(n)}.zip").exists()}
    for n in sorted(set(found) - set(todo), key=float):
        print(f"Chapter {n}: already done (chapter_{chapter_id(n)}.zip); use --redo to make it again")
    if not todo:
        return

    import split_layers
    models = split_layers.Models(args.models.split(",") if args.models else None)
    failed = []
    for n in sorted(todo, key=float):
        print(f"Chapter {n}: {todo[n].name}")
        try:
            make_chapter(todo[n], n, out_root, work_root, models, skip.get(n, []))
        except Exception as e:  # keep going with the rest of the batch
            print(f"  FAILED: {e}")
            failed.append(n)
    if failed:
        print(f"Failed: chapters {', '.join(failed)}. The others are done.")
        sys.exit(1)
    print(f"All done. Chapters are in {out_root.resolve()}")


if __name__ == "__main__":
    main()
