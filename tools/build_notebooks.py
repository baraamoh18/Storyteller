"""Rebuild the Colab notebooks from the scripts they carry, so the two never drift apart.

    python tools/build_notebooks.py

- tools/make-chapter/Make_Chapter.ipynb is written from scratch (it carries split_layers.py and make_chapter.py).
- tools/layer-splitter/Split_Manga_Layers.ipynb gets its `%%writefile split_layers.py` cell refreshed.
Run it after every change to split_layers.py or make_chapter.py, and commit the notebooks with the scripts.
"""

import json
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SPLITTER = TOOLS / "layer-splitter" / "split_layers.py"
MAKER = TOOLS / "make-chapter" / "make_chapter.py"
SPLIT_NB = TOOLS / "layer-splitter" / "Split_Manga_Layers.ipynb"
MAKE_NB = TOOLS / "make-chapter" / "Make_Chapter.ipynb"


def lines(text):
    parts = text.split("\n")
    return [p + "\n" for p in parts[:-1]] + ([parts[-1]] if parts[-1] else [])


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": lines(text)}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": lines(text)}


def writefile(path):
    return code(f"%%writefile {path.name}\n" + path.read_text())


def refresh_split_notebook():
    nb = json.loads(SPLIT_NB.read_text())
    cells = [c for c in nb["cells"] if "".join(c["source"]).startswith("%%writefile split_layers.py")]
    assert len(cells) == 1, "expected one %%writefile split_layers.py cell"
    cells[0]["source"] = writefile(SPLITTER)["source"]
    SPLIT_NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
    # the install cell is shared with the chapter notebook
    return next("".join(c["source"]) for c in nb["cells"] if "pip -q install" in "".join(c["source"]))


def build_make_notebook(install):
    cells = [
        md("""# Make chapters for the scroll reader

Turns your downloaded chapters (CBZ files) into ready-to-direct chapters: it drops the title and promo pages,
splits every panel into a background, a character layer and speech bubbles, converts it all for the web,
and makes overview sheets. Each chapter ends up as **one zip of about 7–10 MB** to send to Claude.

**First time only:** in [Google Drive](https://drive.google.com) make a folder **`Storyteller`**, and inside it a folder **`cbz`**.
Put your CBZ files in `Storyteller/cbz` (you can drag the whole folder of files into the browser).

**Every time**
1. Menu **Runtime → Change runtime type → T4 GPU**, and switch **High-RAM** on.
2. In Step 1 below, type which chapters to make.
3. Menu **Runtime → Run all**. When Google asks, allow access to your Google Drive.
4. The finished zips land in **`Storyteller/chapters`** in your Drive (and download to your computer too). Send them to Claude.

About **15 minutes per chapter**. If Colab disconnects, just **Run all** again: finished chapters are skipped."""),
        md("### Step 1: which chapters"),
        code("""CHAPTERS = "94"        # one chapter "94", a range "1-5", or a list "1-5, 94"
SKIP_PAGES = {}        # pages to drop by hand, e.g. {94: [0, 69]} (the title and promo pages are dropped automatically)
REDO = False           # True: make chapters again even if they are already done
DOWNLOAD = True        # True: also download the zips to this computer when they are done
DRIVE_FOLDER = "Storyteller"   # your folder in Google Drive"""),
        md("### Step 2: connect Google Drive"),
        code("""import os
from google.colab import drive
drive.mount('/content/drive')
ROOT = f'/content/drive/MyDrive/{DRIVE_FOLDER}'
CBZ, OUT = f'{ROOT}/cbz', f'{ROOT}/chapters'
if not os.path.isdir(CBZ):
    raise SystemExit(f'Make a folder "{DRIVE_FOLDER}/cbz" in your Google Drive and put the CBZ files in it, then Run all again.')
os.makedirs(OUT, exist_ok=True)
count = sum(f.lower().endswith('.cbz') for _, _, names in os.walk(CBZ) for f in names)
print(f"{count} CBZ files in {DRIVE_FOLDER}/cbz")
if count == 0:
    raise SystemExit(f'No CBZ files found in "{DRIVE_FOLDER}/cbz" in your Google Drive. Put them there, then Run all again.')"""),
        md("""### Step 3: install the tools (about 1 minute)
If a red pip message about "dependency conflicts" shows up, it is harmless."""),
        code(install),
        md("### Step 4: the two scripts (these cells just save them)"),
        writefile(SPLITTER),
        writefile(MAKER),
        md("""### Step 5: make the chapters
The first lines say whether it runs on the graphics card (`Cutouts run on the graphics card (fast)`). The first run also downloads the AI models (about 2.3 GB)."""),
        code("""import json
skip = json.dumps({str(k): v for k, v in SKIP_PAGES.items()})
!python make_chapter.py --cbz-dir "{CBZ}" --out "{OUT}" --chapters "{CHAPTERS}" --skip '{skip}' --work /content/work {"--redo" if REDO else ""}"""),
        md("""### Step 6: check the pages and download
Each chapter's pages are shown below. Pages crossed out in red were dropped: if a story page was dropped
(or a title or promo page was kept), set `SKIP_PAGES` in Step 1, set `REDO = True` and Run all again."""),
        code("""import io, zipfile
from IPython.display import display
from PIL import Image
from make_chapter import parse_chapters, chapter_number
wanted = parse_chapters(CHAPTERS)
done = sorted(f for f in os.listdir(OUT) if f.startswith('chapter_') and f.endswith('.zip'))
ready = []
for f in done:
    with zipfile.ZipFile(f'{OUT}/{f}') as z:
        info = json.loads(z.read(next(n for n in z.namelist() if n.endswith('/chapter.json'))))
        if not wanted(info['number']):
            continue
        ready.append(f)
        size = os.path.getsize(f'{OUT}/{f}') / 1e6
        print(f"Chapter {info['number']}: {len(info['panels'])} panels, {len(info['bubbles'])} bubbles, "
              f"dropped pages {list(info['dropped_pages']) or 'none'}  ({f}, {size:.1f} MB)")
        sheet = Image.open(io.BytesIO(z.read(next(n for n in z.namelist() if n.endswith('sheets/pages.jpg')))))
        display(sheet.resize((1200, round(sheet.height * 1200 / sheet.width))))
if not ready:
    raise SystemExit('No finished chapters yet: scroll up to Step 5 to see what happened.')
print('Send these to Claude:', ', '.join(ready))
if DOWNLOAD:
    from google.colab import files
    for f in ready:
        files.download(f'{OUT}/{f}')
drive.flush_and_unmount()  # make sure everything is saved in Google Drive
print('Saved in Google Drive:', f'{DRIVE_FOLDER}/chapters')"""),
    ]
    nb = {
        "cells": cells,
        "metadata": {"accelerator": "GPU", "colab": {"provenance": [], "gpuType": "T4"},
                     "kernelspec": {"display_name": "Python 3", "name": "python3"},
                     "language_info": {"name": "python"}},
        "nbformat": 4, "nbformat_minor": 0,
    }
    MAKE_NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    build_make_notebook(refresh_split_notebook())
    print(f"Wrote {MAKE_NB.relative_to(TOOLS.parent)} and refreshed {SPLIT_NB.relative_to(TOOLS.parent)}")
