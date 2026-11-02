"""Split manga / webtoon strips into scroll-ready layers.

For every image you give it, this script:
  1. finds each panel on the strip (the boxes separated by black or white gutters),
  2. finds the speech bubbles and saves each one as a see-through PNG,
  3. cuts the characters out of each panel as a see-through PNG, with clean edges,
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
# Picked by comparing all of rembg's models on real webtoon panels: general is the most
# reliable, hrsod adds missed edges only, while lite and massive grab chunks of background.
CUTOUT_MODELS = ["birefnet-general", "birefnet-hrsod"]


# ---------------------------------------------------------------- bubbles

def find_bubbles(rgb):
    """Return one (y, x, mask) per speech bubble: the filled mask of its box and where that box sits.

    A bubble is a near-white area with dark lettering inside it. Large white
    areas without lettering (glows, white skies) are skipped, and so are white
    slashes and highlights whose "holes" are coloured effects rather than black ink.
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
        if not (0.02 < lettering < 0.45 and roundness > 0.45):
            continue
        # lettering is black ink; real bubbles score about 0.65 here, slashes and glows about 0
        ink = (hi[box][filled & ~part] < 100).mean()
        if ink > 0.3:
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
    def __init__(self, cutout_models=None):
        # torch first: the GPU build of onnxruntime runs on the CUDA libraries torch loads
        import torch
        import onnxruntime
        from rembg.sessions import sessions_class
        from simple_lama_inpainting.models.model import LAMA_MODEL_URL
        from simple_lama_inpainting.utils.util import download_model

        gpu = torch.cuda.is_available() and "CUDAExecutionProvider" in onnxruntime.get_available_providers()
        if cutout_models is None:
            # the second model only adds edge pixels; on the processor it is not worth
            # the time, and both together need more memory than Colab has (about 14 GB)
            cutout_models = CUTOUT_MODELS if gpu else CUTOUT_MODELS[:1]
        print(f"Loading cutout model(s) {', '.join(cutout_models)} and background fill model ...")
        # lower-memory settings so the bigger models also fit on an ordinary computer
        options = onnxruntime.SessionOptions()
        options.enable_cpu_mem_arena = False
        options.enable_mem_pattern = False
        # made directly rather than with rembg's new_session(), which ignores these settings
        # before rembg 2.0.78; without them the two models need about 14 GB and crash Colab
        by_name = {c.name(): c for c in sessions_class}
        unknown = [name for name in cutout_models if name not in by_name]
        if unknown:
            raise SystemExit(f"Unknown cutout model(s): {', '.join(unknown)}")
        # made on the processor, then moved to the graphics card below once they are known to run there
        self.cutouts = [by_name[name](name, options, providers=["CPUExecutionProvider"]) for name in cutout_models]
        # Loaded by hand instead of SimpleLama() so it also works without a GPU.
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.lama = torch.jit.load(download_model(LAMA_MODEL_URL), map_location=self.device).eval()
        self.max_fill_size = 2048 if self.device.type == "cuda" else 800
        try:  # edge refinement arrived in rembg 2.0.8x; older versions just skip it
            from rembg.matting import vitmatte_alpha
            self.refine_edges = vitmatte_alpha
        except ImportError:
            self.refine_edges = None

        noise = Image.fromarray(np.random.default_rng(0).integers(0, 256, (64, 64, 3), np.uint8))
        cutouts_on_gpu = gpu and all([self._move_to_gpu(c.inner_session, lambda c=c: c.predict(noise))
                                      for c in self.cutouts])
        if cutouts_on_gpu and self.refine_edges:
            try:  # rembg keeps its ViTMatte session to itself; it trips over the same problem
                from rembg import matting
                self._move_to_gpu(matting._get_session(matting.DEFAULT_VARIANT),
                                  lambda: self.refine_edges(noise, noise.convert("L")))
            except Exception:
                pass

        where = lambda on_gpu: "graphics card (fast)" if on_gpu else "processor (slow)"
        print(f"Cutouts run on the {where(cutouts_on_gpu)}, background fill on the {where(self.device.type == 'cuda')}.")
        if not torch.cuda.is_available():
            print("No graphics card found. For a much faster run choose Runtime > Change runtime type > T4 GPU.")
        elif not cutouts_on_gpu:
            print("The cutout models could not use this graphics card. Try Runtime > Change runtime type > L4 GPU.")

    @staticmethod
    def _move_to_gpu(session, warm_up):
        """Run an onnxruntime session on the graphics card if it works there; say whether it does.

        onnxruntime's default way of picking convolution algorithms (EXHAUSTIVE) fails on a T4
        with the cuDNN that comes with CUDA 13, and then quietly falls back to the processor.
        So try the other two ways, checking each with a warm-up run.
        """
        import onnxruntime

        session.disable_fallback()  # fail loudly here instead of silently moving to the processor
        for search in ("HEURISTIC", "DEFAULT"):
            try:
                session.set_providers(["CUDAExecutionProvider", "CPUExecutionProvider"],
                                      [{"cudnn_conv_algo_search": search, "arena_extend_strategy": "kSameAsRequested"}, {}])
                warm_up()
                if "CUDAExecutionProvider" in session.get_providers():
                    break
            except Exception:
                pass
        else:
            session.set_providers(["CPUExecutionProvider"])
            return False

        # By default each session keeps all the graphics memory it ever used, and the three of
        # them filled a 15 GB T4 before the background fill got any. Hand it back after every run.
        shrink = onnxruntime.RunOptions()
        shrink.add_run_config_entry("memory.enable_memory_arena_shrinkage", "gpu:0")
        run = session.run
        session.run = lambda output_names, input_feed, run_options=None: run(output_names, input_feed, shrink)
        try:
            warm_up()
        except Exception:  # onnxruntime refuses it when there is no graphics memory pool to shrink
            del session.run
        return True

    def character_alpha(self, rgb):
        image = Image.fromarray(rgb)
        mirrored = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        masks = []
        for session in self.cutouts:
            # averaging with the mirrored panel drops glows and auras only one view mistakes for a character
            plain = np.asarray(session.predict(image)[0], np.float32)
            flipped = np.asarray(session.predict(mirrored)[0], np.float32)[:, ::-1]
            masks.append((plain + flipped) / 2)
        # each model misses different bits (a hand here, an outline there),
        # so keep anything that any of them sees as part of a character
        alpha = np.maximum.reduce(masks).astype(np.uint8)
        if self.refine_edges:
            # ViTMatte redraws the soft edge band: crisper hair, no see-through ghost patches
            refined = np.asarray(self.refine_edges(image, Image.fromarray(alpha)))
            # its output tops out at 254; make the solid inside fully solid again
            refined = np.where(refined >= 250, 255, refined)
            # it also thins fine lines the models were sure of (speed lines, outlines), so those keep their value
            alpha = np.maximum(refined, np.where(alpha >= 200, alpha, 0)).astype(np.uint8)
        return alpha.copy()

    @staticmethod
    def character_colours(rgb, alpha):
        from pymatting import estimate_foreground_ml

        # on soft edges the drawn colour is mixed with the background behind it;
        # unmix it so the character carries no fringe of the old background
        foreground = estimate_foreground_ml(rgb / 255.0, alpha / 255.0)
        foreground = np.clip(foreground * 255 + 0.5, 0, 255).astype(np.uint8)
        return np.where(alpha[..., None] == 255, rgb, foreground)

    def fill_background(self, rgb, hole_mask):
        if not hole_mask.any():
            return rgb
        import torch
        from simple_lama_inpainting.utils.util import prepare_img_and_mask

        h, w = rgb.shape[:2]
        fill_size = min(self.max_fill_size, max(h, w))
        while True:
            # big panels are filled at a smaller size to save memory, then scaled back
            scale = min(1.0, fill_size / max(h, w))
            small = (round(w * scale), round(h * scale))
            image = Image.fromarray(rgb).resize(small, Image.LANCZOS)
            mask = Image.fromarray(hole_mask.astype(np.uint8) * 255).resize(small, Image.NEAREST)
            image, mask = prepare_img_and_mask(image, mask, self.device)
            try:
                with torch.inference_mode():
                    result = self.lama(image, mask)[0].permute(1, 2, 0).cpu().numpy()
                break
            except RuntimeError as error:  # the traced model reports a full graphics card as a plain RuntimeError
                if "out of memory" not in str(error) or fill_size <= 256:
                    raise
                del image, mask
                torch.cuda.empty_cache()
                fill_size //= 2
        if self.device.type == "cuda":
            torch.cuda.empty_cache()  # leave the graphics memory to the cutout models
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
        save_rgba(folder / "characters.png", models.character_colours(crop, alpha), alpha)

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
    parser.add_argument("--models",
                        help="comma-separated cutout models to combine (default: "
                             f"{','.join(CUTOUT_MODELS)} with a graphics card, {CUTOUT_MODELS[0]} without); "
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

    models = Models(args.models.split(",") if args.models else None)
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
