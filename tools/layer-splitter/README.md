# Layer splitter

Turns a manga / webtoon strip into layers for the scroll animations:

| Layer | What it is |
| --- | --- |
| `panel_XX/characters.png` | the characters, with a see-through background |
| `panel_XX/background.png` | the panel with the characters and bubbles painted out |
| `panel_XX/original.png` | the panel as drawn, for comparison |
| `bubbles/bubble_XX.png` | each speech bubble, see-through around it |
| `layers.json` | where every layer sits on the original strip (x, y, width, height) |
| `preview.png` | the strip with panels (green), characters (pink) and bubbles (red) marked |

## Easiest way: Google Colab (nothing to install)

1. Go to <https://colab.research.google.com>, choose **File → Upload notebook** and pick `Split_Manga_Layers.ipynb` from this folder.
2. Choose **Runtime → Run all**.
3. Click **Choose Files** when it appears and select your images.
4. `layers.zip` downloads when it is done.

## On your own computer

Needs Python 3.10 or newer.

```bash
cd tools/layer-splitter
pip install -r requirements.txt
pip install --no-deps simple-lama-inpainting==0.1.2
python split_layers.py path/to/your/images --out layers
```

With an NVIDIA graphics card, swap the processor build for the GPU one to make the cutouts much faster:
`pip uninstall onnxruntime` then `pip install "rembg[gpu]"`.

If your images are slices of one long webtoon strip (panels cut in two between
images), add `--join` to stack them back together, in file-name order, before splitting.

The first run downloads the AI models (about 2.3 GB). Expect a couple of minutes per panel without a graphics card, a few seconds with one.

## How it works

- **Panels** are found by looking for the black or white gaps between them. A "panel" more than 2.5 strip widths tall is
  usually long plain space (black with embers, a fade, a texture) with pictures inside it: the plain stretches (half a
  strip width or longer) are dropped like gutters, and a piece still over 4.5 strip widths tall is cut at its calmest row
  and marked `continues` (the cutout models squash every panel to a square, and WebP cannot store over 16383 px).
- **Speech bubbles** are white shapes with black lettering inside.
- **Characters** are cut out by two BiRefNet models (`birefnet-general` and `birefnet-hrsod`, via `rembg`), each run on the panel and on a mirrored copy, and the results are combined. These two were picked by comparing all of rembg's models on webtoon panels: the others missed parts of characters or grabbed chunks of background. Without a graphics card only `birefnet-general` runs, to save time and memory. Use `--models birefnet-general-lite` for a quicker, rougher run.
- **Edges** are then refined with ViTMatte (for hair and flames, and to drop see-through patches), and the background colour mixed into soft edge pixels is removed so characters carry no fringe.
- **Backgrounds** are filled in with LaMa where the characters and bubbles were.

Sound effects drawn over the art (like "SLASH") usually stay with the characters layer.
The notebook carries its own copy of `split_layers.py`, so update both if you change the script.
