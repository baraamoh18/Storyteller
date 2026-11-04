"""Write a first draft of a chapter's scene plan (site/chapters/<id>/chapter.js) from make_chapter.py's chapter.json.

The draft gets everything that follows from the layout: each panel's size, "pan" for tall panels, a scroll length that
fits the panel, every bubble on its panel with staggered pop-in times, and gentle default camera moves. The director
then adds the creative part: camera moves, impacts, particles, sound effects, transitions and music themes.

With --carry-over OLD_CHAPTER_JS it keeps the choreography of an earlier plan for the panels it can match
(same size, in the same order), renaming their bubbles to the new files. That is how a re-split chapter keeps its work.

Usage:
    python tools/director/draft_chapter.py CHAPTER_FOLDER_OR_ZIP --out site/chapters/<id>/chapter.js
                                           [--title "The Duel"] [--carry-over OLD_chapter.js] [--report]
"""

import argparse
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SIZE_TOLERANCE = 3  # px: the same panel can come out a pixel or two different between two splits


# ---------------------------------------------------------------- defaults from the layout

def draft_scene(p, bubbles, first):
    w, h = p["width"], p["height"]
    ratio = h / w
    s = {"id": p["id"], "w": w, "h": h}
    if ratio > 1.45:  # taller than about a screen: pan down it
        s["length"] = min(400, round(140 + 70 * ratio, -1))
        s["fit"] = "pan"
    elif ratio < 0.3:  # a thin strip
        s["length"] = 110
    else:
        s["length"] = round(140 + 60 * min(ratio, 1.2), -1)
    s["enter"] = "cut" if first else "fade"
    s["exit"] = "fade"
    if s.get("fit") != "pan":
        s["camera"] = {"from": {"scale": 1}, "to": {"scale": 1.06}}
    if bubbles:
        # reading order: top to bottom, then left to right; pop-ins spread over the first two thirds of the panel
        order = sorted(bubbles, key=lambda b: (round(b["y"] / 80), b["x"]))
        n = len(order)
        s["bubbles"] = []
        for k, b in enumerate(order):
            at = 0.12 if n == 1 else round(0.1 + k * (0.5 / (n - 1)), 2)
            entry = {"src": b["id"], "x": b["x"], "y": b["y"], "w": b["w"], "h": b["h"], "at": at}
            if b.get("suspect"):
                entry["_suspect"] = True
            s["bubbles"].append(entry)
    s["fx"] = {"ambient": "dust", "tint": "paper", "amount": 0.4}
    return s


# ---------------------------------------------------------------- carrying over an older plan

def load_chapter_js(path):
    """Evaluate a chapter.js with node and return the object it registers."""
    script = "let c; global.registerChapter = (x) => { c = x; }; require(process.argv[1]); console.log(JSON.stringify(c));"
    out = subprocess.run(["node", "-e", script, str(Path(path).resolve())], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def match_panels(new_panels, old_scenes):
    """Pair new panels with old scenes of the same size, keeping both in order (longest common run of sizes)."""
    same = lambda p, s: abs(p["width"] - s["w"]) <= SIZE_TOLERANCE and abs(p["height"] - s["h"]) <= SIZE_TOLERANCE
    n, m = len(new_panels), len(old_scenes)
    # longest common subsequence on "same size", so a few new panels in between don't break the matching
    best = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            best[i][j] = best[i + 1][j + 1] + 1 if same(new_panels[i], old_scenes[j]) else max(best[i + 1][j], best[i][j + 1])
    pairs, i, j = {}, 0, 0
    while i < n and j < m:
        if same(new_panels[i], old_scenes[j]) and best[i][j] == best[i + 1][j + 1] + 1:
            pairs[i] = j
            i, j = i + 1, j + 1
        elif best[i + 1][j] >= best[i][j + 1]:
            i += 1
        else:
            j += 1
    # gaps: old scenes left between two matched pairs, whose panel the new split cut a little differently.
    # Pair them by position (at the matched edge of the gap) and mark them "resized" for the director.
    resized = set()
    anchors = [(-1, -1)] + sorted(pairs.items()) + [(n, m)]
    for (i0, j0), (i1, j1) in zip(anchors, anchors[1:]):
        new_gap, old_gap = list(range(i0 + 1, i1)), list(range(j0 + 1, j1))
        if not new_gap or not old_gap:
            continue
        if i0 == -1:  # before the first match: line the gap up at its end
            new_gap, old_gap = new_gap[-len(old_gap):], old_gap[-len(new_gap):]
        for i, j in zip(new_gap, old_gap):
            pairs[i] = j
            resized.add(i)
    return pairs, resized


def carry_over(new_scene, old_scene, new_bubbles):
    """The old scene's choreography on the new panel; bubbles matched by position and renamed."""
    s = {}
    for k, v in old_scene.items():  # same order as the old plan, so the two are easy to compare
        s[k] = new_scene[k] if k in ("id", "w", "h") else v
    old_bubbles = old_scene.get("bubbles", [])
    if new_bubbles or old_bubbles:
        s["bubbles"] = []
        for b in sorted(new_bubbles, key=lambda b: (round(b["y"] / 80), b["x"])):
            twin = min(old_bubbles, key=lambda o: abs(o["x"] - b["x"]) + abs(o["y"] - b["y"]), default=None)
            entry = {"src": b["id"], "x": b["x"], "y": b["y"], "w": b["w"], "h": b["h"]}
            if twin and abs(twin["x"] - b["x"]) + abs(twin["y"] - b["y"]) <= 12:
                entry.update({k: v for k, v in twin.items() if k not in ("src", "x", "y", "w", "h")})
            else:
                entry["at"] = 0.12
                entry["_new"] = True
            if b.get("suspect"):
                entry["_suspect"] = True
            s["bubbles"].append(entry)
        if not s["bubbles"]:
            del s["bubbles"]
    return s


# ---------------------------------------------------------------- writing chapter.js

def js(value, indent=0):
    """A JavaScript literal with unquoted keys, short objects on one line."""
    if isinstance(value, dict):
        items = [f"{k}: {js(v, indent + 2)}" for k, v in value.items()]
        flat = "{ " + ", ".join(items) + " }"
        if len(flat) + indent <= 118:
            return flat
        pad = " " * (indent + 2)
        return "{\n" + ",\n".join(pad + i for i in items) + "\n" + " " * indent + "}"
    if isinstance(value, list):
        flat = "[" + ", ".join(js(v, indent + 2) for v in value) + "]"
        if len(flat) + indent <= 118:
            return flat
        pad = " " * (indent + 2)
        return "[\n" + ",\n".join(pad + js(v, indent + 2) for v in value) + "\n" + " " * indent + "]"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return json.dumps(value)


def scene_js(s):
    """One scene: its layout on the first line, then one line per setting, as in the hand-written plans."""
    head = ", ".join(f"{k}: {js(s[k])}" for k in ("id", "w", "h", "length", "fit", "enter", "exit", "focus", "origin") if k in s)
    settings, notes = [], []
    for k, v in s.items():
        if k in ("id", "w", "h", "length", "fit", "enter", "exit", "focus", "origin") or k.startswith("_"):
            continue
        if k == "bubbles":
            entries = []
            for b in v:
                clean = {kk: vv for kk, vv in b.items() if not kk.startswith("_")}
                if b.get("_suspect"):  # left out until the director has looked at it
                    notes.append(f"    // check {clean['src']}: small, may be an eye or a highlight, not a bubble: {js(clean)}")
                else:
                    if b.get("_new"):
                        notes.append(f"    // {clean['src']} is new in this split: check its timing")
                    entries.append(clean)
            if entries:
                settings.append("    bubbles: " + js(entries, 4))
        else:
            settings.append(f"    {k}: " + js(v, 4))
    remark = "; ".join(r for r in (f"from {s['_carried']}" if s.get("_carried") else "", s.get("_note", "")) if r)
    first = "  { " + head + ("," if settings else " },") + (f"  // {remark}" if remark else "")
    if not settings:
        return "\n".join([first] + notes)
    return "\n".join([first] + notes + [",\n".join(settings) + " },"])


def write_chapter(path, info, title, scenes, music):
    out = [
        f"/* {title}: chapter {info['number']} ({len(scenes)} panels).",
        "   The scene plan for this chapter. Every setting is explained in site/README.md.",
        "   Images live next to this file: panel_XX_background.webp, panel_XX_characters.webp, bubble_XX.webp */",
        "registerChapter({",
        f"  id: {json.dumps(info['id'])},",
        f"  title: {json.dumps(title)},",
        f"  number: {info['number']},",
        "",
        "  // music: one theme from series.js per stretch of story (see site/README.md)",
        "  music: [",
    ]
    out += [f"    {js(z)}," for z in music]
    out += ["  ],", "", "  scenes: [", ""]
    out += [scene_js(s) + "\n" for s in scenes]
    out += ["  ],", "});", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out))


# ---------------------------------------------------------------- main

def read_chapter_json(source):
    source = Path(source)
    if source.is_dir():
        hits = list(source.rglob("chapter.json"))
        return json.loads(hits[0].read_text()) if hits else sys.exit(f"No chapter.json in {source}")
    with zipfile.ZipFile(source) as z:
        name = next((n for n in z.namelist() if n.endswith("/chapter.json")), None)
        return json.loads(z.read(name)) if name else sys.exit(f"No chapter.json in {source}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", help="the chapter zip from make_chapter.py, or the folder it unzips to")
    parser.add_argument("--out", required=True, help="where to write chapter.js")
    parser.add_argument("--title", help="the chapter's title (default: Chapter <number>)")
    parser.add_argument("--carry-over", help="an earlier chapter.js whose choreography to keep for matching panels")
    parser.add_argument("--report", action="store_true", help="print which panels were carried over")
    args = parser.parse_args()

    info = read_chapter_json(args.source)
    panels = [p for p in info["panels"] if not p.get("tiny")]
    by_panel = {}
    for b in info["bubbles"]:
        by_panel.setdefault(b["panel"], []).append(b)
    title = args.title or f"Chapter {info['number']}"

    scenes = [draft_scene(p, by_panel.get(p["id"], []), k == 0) for k, p in enumerate(panels)]
    # pieces of one tall picture (the chapter maker cuts those up): a plain cut between them, so it reads as one picture
    for k, p in enumerate(panels):
        if k and p.get("continues") == panels[k - 1]["id"]:
            scenes[k - 1]["exit"] = scenes[k]["enter"] = "cut"
            scenes[k]["_note"] = f"continues {p['continues']} (one tall picture cut in two): keep the camera move going"
    music = [{"theme": "calm", "from": scenes[0]["id"]}]

    if args.carry_over:
        old = load_chapter_js(args.carry_over)
        pairs, resized = match_panels(panels, old["scenes"])
        old_to_new = {}
        for i, j in pairs.items():
            new = carry_over(scenes[i], old["scenes"][j], by_panel.get(panels[i]["id"], []))
            new["_carried"] = old["scenes"][j]["id"] + (f" (resized from {old['scenes'][j]['w']}x{old['scenes'][j]['h']}: check)" if i in resized else "")
            scenes[i] = new
            old_to_new[old["scenes"][j]["id"]] = scenes[i]["id"]
        # the old music stretches, moved to the new panel names; the new panels before and after are left to the director
        music = []
        for z in old.get("music", []):
            moved = {**z, "from": old_to_new.get(z["from"], z["from"])}
            if "to" in z:
                moved["to"] = old_to_new.get(z["to"], z["to"])
            music.append(moved)
        if args.report:
            print(f"Carried over {len(pairs)} of {len(old['scenes'])} old scenes onto {len(panels)} panels:")
            runs, start = [], None
            for i in range(len(panels) + 1):
                if i in pairs and start is None:
                    start = i
                if i not in pairs and start is not None:
                    runs.append((start, i - 1))
                    start = None
            for a, b in runs:
                print(f"  {panels[a]['id']}..{panels[b]['id']}  <-  {old['scenes'][pairs[a]]['id']}..{old['scenes'][pairs[b]]['id']}")
            fresh = [panels[i]["id"] for i in range(len(panels)) if i not in pairs]
            print(f"  new panels to direct ({len(fresh)}): {', '.join(fresh)}")

    skipped = [p["id"] for p in info["panels"] if p.get("tiny")]
    write_chapter(Path(args.out), info, title, scenes, music)
    print(f"Wrote {args.out}: {len(scenes)} scenes" + (f" (skipped tiny {', '.join(skipped)})" if skipped else ""))


if __name__ == "__main__":
    main()
