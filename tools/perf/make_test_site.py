"""A test copy of the reader with stand-in pictures, for the checks in this folder.

    python tools/perf/make_test_site.py OUT_FOLDER [--site SITE_FOLDER] [--chapters 094 094-demo]

Chapter pictures are not in git, and the checks do not need the real ones: this copies the reader (index.html,
series.js, vendor, music, sfx, each chapter.js) into OUT_FOLDER and draws stand-in pictures of exactly the sizes each
chapter.js names, with picture-like detail so that unpacking them costs about what the real ones cost.
--site can point at an older copy of the reader (to compare a change against it). Needs node, numpy and Pillow.
"""

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

REPO = Path(__file__).resolve().parents[2]


def scenes_of(chapter_js):
    script = "let c; global.registerChapter = (x) => { c = x; }; require(process.argv[1]); console.log(JSON.stringify(c));"
    out = subprocess.run(["node", "-e", script, str(chapter_js.resolve())], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def draw(scene, folder, rng):
    w, h, name = scene["w"], scene["h"], scene["id"]
    # background: a smooth colour field with soft grain, like painted art
    field = Image.fromarray(rng.integers(0, 255, (max(2, h // 40), max(2, w // 40), 3), np.uint8)).resize((w, h), Image.BICUBIC)
    grain = Image.fromarray(rng.integers(0, 40, (max(1, h // 2), max(1, w // 2), 3), np.uint8)).resize((w, h), Image.BILINEAR)
    bg = Image.fromarray(np.clip(np.asarray(field).astype(np.int16) // 2 + np.asarray(grain) + 20, 0, 255).astype(np.uint8))
    ImageDraw.Draw(bg).text((20, 20), name, fill=(255, 255, 255))
    bg.save(folder / f"{name}_background.webp", quality=80, method=2)
    # characters: a soft-edged figure on a see-through background
    alpha = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(alpha)
    d.ellipse([w * 0.3, h * 0.15, w * 0.7, h * 0.45], fill=255)
    d.rectangle([w * 0.35, h * 0.4, w * 0.65, h * 0.95], fill=255)
    figure = Image.fromarray(rng.integers(60, 255, (max(2, h // 25), max(2, w // 25), 3), np.uint8)).resize((w, h), Image.BICUBIC)
    figure.putalpha(alpha.filter(ImageFilter.GaussianBlur(3)))
    figure.save(folder / f"{name}_characters.webp", quality=85, method=2)
    for b in scene.get("bubbles", []):
        im = Image.new("RGBA", (b["w"], b["h"]), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse([4, 4, b["w"] - 4, b["h"] - 4], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=4)
        d.text((b["w"] // 3, b["h"] // 2), b["src"], fill=(0, 0, 0, 255))
        im.save(folder / f"{b['src']}.webp", quality=90)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("out")
    parser.add_argument("--site", default=str(REPO / "site"), help="the reader to copy (default: this project's site folder)")
    parser.add_argument("--chapters", nargs="+", help="chapter ids (default: every chapter folder with a chapter.js)")
    args = parser.parse_args()
    site, out = Path(args.site), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "series.js"):
        shutil.copy2(site / name, out / name)
    for folder in ("vendor", "music", "sfx"):
        if (site / folder).is_dir():
            shutil.copytree(site / folder, out / folder, dirs_exist_ok=True)
    chapters = args.chapters or sorted(p.parent.name for p in (site / "chapters").glob("*/chapter.js"))
    lines = []
    for cid in chapters:
        target = out / "chapters" / cid
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(site / "chapters" / cid / "chapter.js", target / "chapter.js")
        chapter = scenes_of(target / "chapter.js")
        rng = np.random.default_rng(1)
        made = 0
        for scene in chapter["scenes"]:
            if not (target / f"{scene['id']}_background.webp").exists():
                draw(scene, target, rng)
                made += 1
        lines.append(f'    {{ id: {json.dumps(cid)}, title: {json.dumps(chapter["title"])}, number: {json.dumps(chapter.get("number"))}, panels: {len(chapter["scenes"])} }},')
        print(f"{cid}: {len(chapter['scenes'])} scenes, {made} drawn")
    # the test copy's menu lists exactly these chapters
    text = (out / "series.js").read_text(encoding="utf-8")
    a = text.index("chapters: [") + len("chapters: [")
    z = text.index("],", a)
    (out / "series.js").write_text(text[:a] + "\n" + "\n".join(lines) + "\n  " + text[z:], encoding="utf-8")
    print(f"Serve it:  python3 -m http.server 8772 --directory {out}")


if __name__ == "__main__":
    main()
