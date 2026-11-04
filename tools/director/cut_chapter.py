"""Cut a short demo from a directed chapter: the chosen scenes, as they were directed, in a chapter of their own.

    python tools/director/cut_chapter.py site/chapters/094 --id 094-demo --title "The Duel (demo cut)" \
        --panels 01,02,04,06,07,70-72,74-76,78,79,81,84,86,87,89,92 \
        --music "tension:01,climax:70,calm:92"

Writes site/chapters/<id>/chapter.js and copies the chosen panels' images and bubbles next to it (images stay out of git).
--music names the theme that starts at a panel; each plays until the next one starts.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path


def panel_ids(text):
    ids = []
    for part in text.split(","):
        a, _, b = part.strip().partition("-")
        ids += [f"panel_{n:02d}" for n in range(int(a), int(b or a) + 1)]
    return ids


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", help="the directed chapter's folder, e.g. site/chapters/094")
    parser.add_argument("--id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--panels", required=True, help="panel numbers: 01,02,70-72")
    parser.add_argument("--music", required=True, help="theme:first panel, e.g. tension:01,climax:70")
    args = parser.parse_args()

    source = Path(args.source)
    text = (source / "chapter.js").read_text(encoding="utf-8")
    number = re.search(r"\bnumber:\s*([^,\n]+)", text).group(1).strip()
    body = text[text.index("scenes: [") + len("scenes: ["):text.rindex("],")]
    # one block per scene, from its `{ id: "panel_XX"` line up to the next scene (section notes dropped)
    starts = [m.start() for m in re.finditer(r'^  \{ id: "panel_\d+"', body, re.M)] + [len(body)]
    blocks = {}
    for a, z in zip(starts, starts[1:]):
        block = body[a:z].rstrip()
        block = re.sub(r"\n\s*// ----.*$", "", block)  # a section note that belongs to the next scene
        blocks[re.search(r'id: "(panel_\d+)"', block).group(1)] = block.rstrip()

    wanted = panel_ids(args.panels)
    missing = [p for p in wanted if p not in blocks]
    if missing:
        sys.exit(f"Not in {source}/chapter.js: {', '.join(missing)}")
    music = []
    for k, item in enumerate(args.music.split(",")):
        theme, first = item.split(":")
        music.append({"theme": theme.strip(), "from": f"panel_{int(first):02d}"})
    for k in range(len(music) - 1):  # each stretch ends at the panel before the next one starts
        music[k]["to"] = wanted[wanted.index(music[k + 1]["from"]) - 1]

    out = source.parent / args.id
    out.mkdir(exist_ok=True)
    lines = [
        f"/* {args.title}: {len(wanted)} scenes cut from chapters/{source.name} with tools/director/cut_chapter.py,",
        "   directed exactly as in the full chapter. Every setting is explained in site/README.md. */",
        "registerChapter({",
        f'  id: "{args.id}",',
        f'  title: "{args.title}",',
        f"  number: {number},",
        "",
        "  music: [",
    ]
    for z in music:
        lines.append("    { " + ", ".join(f'{k}: "{v}"' for k, v in z.items()) + " },")
    lines += ["  ],", "", "  scenes: [", ""]
    lines += [blocks[p] + "\n" for p in wanted]
    lines += ["  ],", "});", ""]
    (out / "chapter.js").write_text("\n".join(lines), encoding="utf-8")

    copied = 0
    for p in wanted:
        for f in source.glob(f"{p}_*.webp"):
            shutil.copy2(f, out / f.name)
            copied += 1
        for bubble in re.findall(r'src: "(bubble_[^"]+)"', blocks[p]):
            shutil.copy2(source / f"{bubble}.webp", out / f"{bubble}.webp")
            copied += 1
    print(f"Wrote {out}/chapter.js: {len(wanted)} scenes, {copied} images; music " +
          ", ".join(f"{z['theme']} from {z['from']}" for z in music))


if __name__ == "__main__":
    main()
