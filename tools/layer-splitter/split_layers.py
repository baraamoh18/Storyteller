"""Split manga / webtoon strips into scroll-ready layers.

For every image you give it, this script:
  1. finds each panel on the strip (the boxes separated by black or white gutters),
  2. finds the speech bubbles and saves each one as a see-through PNG,
  3. cuts the characters out of each panel as a see-through PNG,
  4. paints over the holes the characters and bubbles leave, so the panel
     background looks complete when the layers move apart on scroll.

Usage:
    python split_layers.py input_folder_or_image [more ...] --out output_folder

Everything lands in output_folder/<image name>/ together with a layers.json
that says where each layer sits on the original strip.

If your images are slices of one long webtoon strip (so a panel can be cut in
two between images), add --join to stack them back together first.
"""

import argparse
import json
import re
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".webp"}


# ---------------------------------------------------------------- bubbles

def find_bubbles(rgb):
    """Return one (y, x, mask) per speech bubble: the filled mask of its box and where that box sits.

    A bubble is a near-white area with dark lettering inside it. Large white
    areas without lettering (glows, white skies) are skipped.
    """
    hi = rgb.max(2)
    lo = rgb.min(2)
    white = (lo > 225) & (hi - lo < 25)
    labels, _ = ndi.label(white)
    bubbles = []
    for i, box in enumerate(ndi.find_objects(labels), 1):
        part = labels[box] == i
        area = part.sum()
        if area < 1500:
            continue
        filled = ndi.binary_fill_holes(part)
        filled_area = filled.sum()
        lettering = (filled_area - area) / filled_area
        roundness = filled_area / part.size
        if 0.02 < lettering < 0.45 and roundness > 0.45:
            bubbles.append((box[0].start, box[1].start, filled))
    return bubbles


# ---------------------------------------------------------------- panels

def _runs(flags, min_len):
    out, start = [], None
    for i, on in enumerate(list(flags) + [False]):
        if on and start is None:
            start = i
        if not on and start is not None:
            if i - start >= min_len:
                out.append((start, i))
            start = None
    return out


def find_panels(rgb, bubble_mask):
    """Return panel boxes as (x, y, w, h), top to bottom.

    Works on vertical webtoon strips where panels are stacked with gutters
    between them. The gutter colour is the most common colour on the image border.
    """
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]]) // 16
    colours, counts = np.unique(border, axis=0, return_counts=True)
    gutter_colour = colours[counts.argmax()].astype(np.int16) * 16 + 8
    # int16 rather than int, so a whole joined chapter fits in memory
    distance = np.abs(rgb.astype(np.int16) - gutter_colour).max(2)
    ignore = cv2.dilate(bubble_mask.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
    content = (distance > 18) & ~ignore

    panels = []
    rows = content.mean(1) > 0.05
    for y0, y1 in _runs(rows, 60):
        cols = content[y0:y1].mean(0) > 0.05
        col_runs = _runs(cols, 30)
        if not col_runs:
            continue
        x0, x1 = col_runs[0][0], col_runs[-1][1]
        panels.append((x0, y0, x1 - x0, y1 - y0))
    if not panels:  # a single picture with no gutters
        h, w = rgb.shape[:2]
        panels.append((0, 0, w, h))
    return panels


# ---------------------------------------------------------------- models

class Models:
    def __init__(self, cutout_models):
        import onnxruntime
        import torch
        from rembg import new_session
        from simple_lama_inpainting.models.model import LAMA_MODEL_URL
        from simple_lama_inpainting.utils.util import download_model

        print(f"Loading cutout model(s) {', '.join(cutout_models)} and background fill model ...")
        # lower-memory settings so the bigger models also fit on an ordinary computer
        options = onnxruntime.SessionOptions()
        options.enable_cpu_mem_arena = False
        options.enable_mem_pattern = False
        self.cutouts = [new_session(name, sess_opts=options) for name in cutout_models]
        # Loaded by hand instead of SimpleLama() so it also works without a GPU.
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.lama = torch.jit.load(download_model(LAMA_MODEL_URL), map_location=self.device).eval()
        self.max_fill_size = 2048 if self.device.type == "cuda" else 800

    def character_alpha(self, rgb):
        from rembg import remove

        # each model misses different bits (a hand here, a sword there),
        # so keep anything that any of them sees as part of a character
        image = Image.fromarray(rgb)
        masks = [np.array(remove(image, session=s, only_mask=True).convert("L")) for s in self.cutouts]
        return np.maximum.reduce(masks)

    def fill_background(self, rgb, hole_mask):
        if not hole_mask.any():
            return rgb
        import torch
        from simple_lama_inpainting.utils.util import prepare_img_and_mask

        h, w = rgb.shape[:2]
        # big panels are filled at a smaller size to save memory, then scaled back
        scale = min(1.0, self.max_fill_size / max(h, w))
        small = (round(w * scale), round(h * scale))
        image = Image.fromarray(rgb).resize(small, Image.LANCZOS)
        mask = Image.fromarray(hole_mask.astype(np.uint8) * 255).resize(small, Image.NEAREST)
        image, mask = prepare_img_and_mask(image, mask, self.device)
        with torch.inference_mode():
            result = self.lama(image, mask)[0].permute(1, 2, 0).cpu().numpy()
        result = np.clip(result * 255, 0, 255).astype(np.uint8)[:small[1], :small[0]]
        result = cv2.resize(result, (w, h), interpolation=cv2.INTER_CUBIC)
        # keep the untouched pixels exactly as drawn
        return np.where(hole_mask[..., None], result, rgb)


# ---------------------------------------------------------------- main work

def save_rgba(path, rgb, alpha):
    Image.fromarray(np.dstack([rgb, alpha]).astype(np.uint8), "RGBA").save(path)


def natural_key(path):
    # so 2.png comes before 10.png
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", path.name)]


def join_slices(files):
    images = [np.array(Image.open(p).convert("RGB")) for p in files]
    widths = sorted({im.shape[1] for im in images})
    if len(widths) > 1:
        raise SystemExit(f"--join needs images that are all the same width, got widths {widths}.")
    return np.vstack(images)


def split_image(name, source, rgb, out_root, models):
    h, w = rgb.shape[:2]
    out = out_root / name
    out.mkdir(parents=True, exist_ok=True)
    grow = lambda m, px: cv2.dilate(m.astype(np.uint8), np.ones((px, px), np.uint8)) > 0

    def grow_bubble(y, x, mask, px):
        # grow within the bubble's box plus a margin, not a full-strip mask per bubble
        pad = px // 2
        y0, x0 = max(y - pad, 0), max(x - pad, 0)
        y1, x1 = min(y + mask.shape[0] + pad, h), min(x + mask.shape[1] + pad, w)
        box = np.zeros((y1 - y0, x1 - x0), bool)
        box[y - y0:y - y0 + mask.shape[0], x - x0:x - x0 + mask.shape[1]] = mask
        return y0, x0, grow(box, px)

    # grow each bubble a little so its black outline comes along with it
    bubbles = [grow_bubble(*b, 15) for b in find_bubbles(rgb)]
    all_bubbles = np.zeros((h, w), bool)
    for y, x, mask in bubbles:
        all_bubbles[y:y + mask.shape[0], x:x + mask.shape[1]] |= mask
    panels = find_panels(rgb, all_bubbles)

    info = {"source": source, "width": w, "height": h, "panels": [], "bubbles": []}
    preview = rgb.copy()

    for n, (x, y, pw, ph) in enumerate(panels, 1):
        name = f"panel_{n:02d}"
        folder = out / name
        folder.mkdir(exist_ok=True)
        crop = rgb[y:y + ph, x:x + pw]
        bubble_here = all_bubbles[y:y + ph, x:x + pw]

        alpha = models.character_alpha(crop)
        alpha[grow(bubble_here, 15)] = 0
        alpha[alpha < 20] = 0
        # grow the holes so glows and outlines around characters get painted over too
        holes = grow(alpha > 40, 31) | grow(bubble_here, 9)
        background = models.fill_background(crop, holes)

        Image.fromarray(crop).save(folder / "original.png")
        Image.fromarray(background).save(folder / "background.png")
        save_rgba(folder / "characters.png", crop, alpha)

        info["panels"].append({
            "id": name, "x": int(x), "y": int(y), "width": int(pw), "height": int(ph),
            "layers": {
                "background": f"{name}/background.png",
                "characters": f"{name}/characters.png",
                "original": f"{name}/original.png",
            },
        })
        cv2.rectangle(preview, (x, y), (x + pw, y + ph), (0, 255, 0), 4)
        cut = (alpha > 40)
        region = preview[y:y + ph, x:x + pw]
        region[cut] = (region[cut] * 0.5 + np.array([255, 0, 255]) * 0.5).astype(np.uint8)
        print(f"  {name}: {pw}x{ph} at ({x}, {y})")

    (out / "bubbles").mkdir(exist_ok=True)
    for n, (by, bx, mask) in enumerate(bubbles, 1):
        ys, xs = np.nonzero(mask)
        mask = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        y0, x0 = by + ys.min(), bx + xs.min()
        y1, x1 = y0 + mask.shape[0], x0 + mask.shape[1]
        file = f"bubbles/bubble_{n:02d}.png"
        save_rgba(out / file, rgb[y0:y1, x0:x1], mask * 255)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        owner = next((p["id"] for p in info["panels"]
                      if p["x"] <= cx <= p["x"] + p["width"] and p["y"] <= cy <= p["y"] + p["height"]), None)
        info["bubbles"].append({"id": f"bubble_{n:02d}", "x": int(x0), "y": int(y0),
                                "width": int(x1 - x0), "height": int(y1 - y0),
                                "panel": owner, "file": file})
        region = preview[y0:y1, x0:x1]
        region[mask] = (region[mask] * 0.4 + np.array([255, 60, 60]) * 0.6).astype(np.uint8)
    print(f"  {len(bubbles)} speech bubble(s)")

    Image.fromarray(preview).save(out / "preview.png")
    (out / "layers.json").write_text(json.dumps(info, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", help="image files or folders of images")
    parser.add_argument("--out", default="layers", help="where to put the results (default: layers)")
    parser.add_argument("--join", action="store_true",
                        help="stack all images into one long strip first (for webtoon slices "
                             "where panels are cut in two between images)")
    parser.add_argument("--models", default="birefnet-general,birefnet-general-lite",
                        help="comma-separated cutout models to combine (default: %(default)s); "
                             "use just birefnet-general-lite for a quick, rougher run")
    args = parser.parse_args()

    files = []
    for item in map(Path, args.inputs):
        if item.is_dir():
            files += sorted((p for p in item.iterdir() if p.suffix.lower() in IMAGE_TYPES), key=natural_key)
        else:
            files.append(item)
    if not files:
        raise SystemExit("No images found.")

    models = Models(args.models.split(","))
    out_root = Path(args.out)
    if args.join:
        name = f"{files[0].stem}-{files[-1].stem}" if len(files) > 1 else files[0].stem
        print(f"{name} (joined {len(files)} images)")
        split_image(name, [p.name for p in files], join_slices(files), out_root, models)
    else:
        for path in files:
            print(f"{path.name}")
            split_image(path.stem, path.name, np.array(Image.open(path).convert("RGB")), out_root, models)
    print(f"Done. Layers are in {out_root.resolve()}")


if __name__ == "__main__":
    main()
