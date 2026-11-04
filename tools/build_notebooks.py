"""Rebuild the Colab notebooks from the scripts they carry, so the two never drift apart.

    python tools/build_notebooks.py

- tools/make-chapter/Make_Chapter.ipynb (Colab) and Make_Chapters_Kaggle.ipynb (Kaggle) are written from scratch
  (they carry split_layers.py, make_chapter.py and gpu_check.py).
- tools/layer-splitter/Split_Manga_Layers.ipynb gets its `%%writefile split_layers.py` cell refreshed.
- dist/Storyteller-PC-Tools.zip is the Windows kit (tools/pc plus the scripts); dist/ is not committed.
Run it after every change to split_layers.py or make_chapter.py, and commit the notebooks with the scripts.
"""

import json
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SPLITTER = TOOLS / "layer-splitter" / "split_layers.py"
MAKER = TOOLS / "make-chapter" / "make_chapter.py"
SPLIT_NB = TOOLS / "layer-splitter" / "Split_Manga_Layers.ipynb"
MAKE_NB = TOOLS / "make-chapter" / "Make_Chapter.ipynb"
KAGGLE_NB = TOOLS / "make-chapter" / "Make_Chapters_Kaggle.ipynb"
CHECK = TOOLS / "make-chapter" / "gpu_check.py"


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
and makes overview sheets. Each chapter ends up as **one zip of about 15 MB** to send to Claude.

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


def build_kaggle_notebook(install):
    cells = [
        md("""# Make chapters on Kaggle (free, two graphics cards, runs while you're away)

The same as the Colab notebook, but on [Kaggle](https://www.kaggle.com): about **30 free GPU hours a week**, **two T4
graphics cards** (two chapters at once), and it keeps running after you close the browser.
Each chapter becomes one zip (about 15 MB) in this notebook's **Output**.

**First time only**
1. Make a free Kaggle account and **verify your phone number** (Settings → Phone verification): Kaggle only allows the
   graphics cards and internet access after that.
2. **Upload your chapters:** *Datasets → New Dataset*, drag in your CBZ files (or the folder), name it for example
   `tbate-cbz`, keep it **Private**, and *Create*. Uploading 2.8 GB takes a while; it only happens once.
3. **Make the notebook:** *Code → New Notebook*, then *File → Import Notebook* and pick this file.
4. In the right-hand panel: **Session options → Accelerator → GPU T4 x2**, **Internet → On**, and under **Input**
   click *Add Input* and add your `tbate-cbz` dataset.

**Every run**
1. In Step 1 below, type which chapters to make (a big range is fine: it stops in time and the next run carries on).
2. Click **Save Version** (top right) → **Save & Run All (Commit)** → **Save**. You can close the browser now.
3. When it has finished, open the notebook's version → **Output** → download the zips, and send them to Claude.
4. **Next run:** in the right-hand panel, *Add Input → Your Work → Notebook Output Files* → this notebook. Chapters
   already in that output are skipped, so every run picks up where the last one stopped."""),
        md("### Step 1: which chapters"),
        code("""import time
START = time.time()
CHAPTERS = "1-30"      # a range "1-30", a list "1-5, 94", or one chapter "94"
SKIP_PAGES = {}        # pages to drop by hand, e.g. {94: [0, 69]} (the title and promo pages are dropped automatically)
MAX_HOURS = 11         # Kaggle stops a run at 12 hours; no new chapter is started after this"""),
        md("### Step 2: find the chapters and the graphics cards"),
        code("""import glob, os, torch
cbz = sorted(glob.glob('/kaggle/input/**/*.cbz', recursive=True))
if not cbz:
    raise SystemExit('No CBZ files found. In the right-hand panel, Add Input and add your dataset of CBZ files.')
CBZ_DIR = os.path.commonpath([os.path.dirname(p) for p in cbz])
DONE = sorted({os.path.dirname(p) for p in glob.glob('/kaggle/input/**/chapter_*.zip', recursive=True)})
OUT = '/kaggle/working/chapters'
GPUS = torch.cuda.device_count()
print(f'{len(cbz)} CBZ files; {sum(len(glob.glob(d + "/chapter_*.zip")) for d in DONE)} chapters already done in earlier runs')
print(f'{GPUS} graphics card(s): ' + ', '.join(torch.cuda.get_device_name(g) for g in range(GPUS)))
if GPUS == 0:
    print('No graphics card: in the right-hand panel set Accelerator to GPU T4 x2 (this needs a verified phone number).')"""),
        md("""### Step 3: install the tools (a few minutes)
Red pip messages about "dependency conflicts" are harmless."""),
        code(install),
        md("### Step 4: the scripts (these cells just save them)"),
        writefile(SPLITTER),
        writefile(MAKER),
        writefile(CHECK),
        md("""### Step 5: load the AI models once and check the graphics card
The first time it downloads the models (about 2.3 GB). If the newest cutout runtime cannot use these graphics cards,
it switches to the build for CUDA 12 by itself."""),
        code("""import subprocess, sys
check = subprocess.run([sys.executable, 'gpu_check.py'])
if check.returncode == 3 and GPUS:
    print('Switching to the cutout runtime built for CUDA 12 ...')
    !pip -q install "onnxruntime-gpu==1.22.0"
    check = subprocess.run([sys.executable, 'gpu_check.py'])
if check.returncode != 0:
    print('WARNING: the cutouts will run on the processor, which is many times slower.')"""),
        md("""### Step 6: make the chapters, one per graphics card at a time
Progress shows every 5 minutes; each graphics card's full log is saved as `log_gpu0.txt` / `log_gpu1.txt` in the Output."""),
        code("""import json
skip = json.dumps({str(k): v for k, v in SKIP_PAGES.items()})
hours_left = MAX_HOURS - (time.time() - START) / 3600
shares = max(1, GPUS)
procs = []
for g in range(shares):
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(g)) if GPUS else dict(os.environ)
    cmd = [sys.executable, 'make_chapter.py', '--cbz-dir', CBZ_DIR, '--out', OUT, '--chapters', CHAPTERS,
           '--skip', skip, '--work', f'/tmp/work{g}', '--shard', f'{g + 1}/{shares}', '--max-hours', f'{hours_left:.2f}']
    for d in DONE:
        cmd += ['--done-dir', d]
    log = open(f'/kaggle/working/log_gpu{g}.txt', 'w')
    procs.append((subprocess.Popen(cmd, env=env, stdout=log, stderr=subprocess.STDOUT), log))
while any(p.poll() is None for p, _ in procs):
    time.sleep(300)
    finished = len(glob.glob(f'{OUT}/chapter_*.zip'))
    print(f'{time.strftime("%H:%M")}  {finished} chapters finished in this run', flush=True)
for g, (p, log) in enumerate(procs):
    log.close()
    print(f'--- graphics card {g} (exit code {p.returncode}), last lines of its log:')
    print(''.join(open(f'/kaggle/working/log_gpu{g}.txt').readlines()[-12:]))"""),
        md("### Step 7: what this run made"),
        code("""zips = sorted(glob.glob(f'{OUT}/chapter_*.zip'))
total = sum(os.path.getsize(z) for z in zips) / 1e6
print(f'{len(zips)} chapters in this run ({total:.0f} MB):', ', '.join(os.path.basename(z)[8:-4] for z in zips))
print("Download them from this version's Output tab and send them to Claude.")"""),
    ]
    nb = {
        "cells": cells,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                     "language_info": {"name": "python"},
                     "kaggle": {"accelerator": "nvidiaTeslaT4", "isInternetEnabled": True, "isGpuEnabled": True}},
        "nbformat": 4, "nbformat_minor": 4,
    }
    KAGGLE_NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")


def build_pc_kit():
    """dist/Storyteller-PC-Tools.zip: the Windows double-click kit plus the scripts it runs (not committed)."""
    import zipfile
    dist = TOOLS.parent / "dist"
    dist.mkdir(exist_ok=True)
    kit = dist / "Storyteller-PC-Tools.zip"
    with zipfile.ZipFile(kit, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted((TOOLS / "pc").iterdir()):
            z.write(f, f"Storyteller-PC-Tools/{f.name}")
        for f in (SPLITTER, MAKER, CHECK):
            z.write(f, f"Storyteller-PC-Tools/{f.name}")
    return kit


if __name__ == "__main__":
    print(f"Wrote {build_pc_kit().relative_to(TOOLS.parent)}")
    install = refresh_split_notebook()
    build_make_notebook(install)
    build_kaggle_notebook(install)
    print(f"Wrote {MAKE_NB.relative_to(TOOLS.parent)} and {KAGGLE_NB.relative_to(TOOLS.parent)}, "
          f"and refreshed {SPLIT_NB.relative_to(TOOLS.parent)}")
