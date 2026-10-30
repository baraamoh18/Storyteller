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
python split_layers.py path/to/your/images --out layers
```

The first run downloads the two AI models (about 300 MB).

## How it works

- **Panels** are found by looking for the black or white gaps between them.
- **Speech bubbles** are white shapes with lettering inside.
- **Characters** are cut out with BiRefNet (via `rembg`).
- **Backgrounds** are filled in with LaMa where the characters and bubbles were.

Sound effects drawn over the art (like "SLASH") usually stay with the characters layer.
The notebook carries its own copy of `split_layers.py`, so update both if you change the script.
