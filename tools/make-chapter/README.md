# Make chapters

Three ways to run the same chapter maker; all three take a range of chapters, skip the ones already done, and make
one `chapter_<id>.zip` (about 15 MB) per chapter:

| Where | File | Notes |
|---|---|---|
| Colab | `Make_Chapter.ipynb` | CBZ from Drive `Storyteller/cbz`, zips to `Storyteller/chapters`; the tab must stay open |
| Kaggle | `Make_Chapters_Kaggle.ipynb` | free ~30 GPU h/week, **2× T4 = two chapters at once** (`--shard 1/2`, `2/2`), runs after the browser closes (Save & Run All), stops starting chapters after `MAX_HOURS` (default 11; Kaggle's limit is 12); add the previous version's output as an input to resume |
| The user's PC (RTX 5050) | `../pc/` → `dist/Storyteller-PC-Tools.zip` | `Setup.bat` once (Python 3.12, torch cu128, models in the kit folder), then `Make Chapters.bat` |

`gpu_check.py` loads the models and exits 3 if the cutouts would run on the processor; the Kaggle notebook then installs
`onnxruntime-gpu==1.22.0` (the CUDA 12 build), the PC setup tries that and then `onnxruntime-directml`.
`split_layers.Models` picks CUDA, else DirectML, else the processor, and times every step; each chapter prints its
time per panel and stores it in `chapter.json` under `seconds`. Both cutout models always run (the user wants the accuracy).

`Make_Chapter.ipynb` (Colab, T4 GPU + High-RAM) turns chapter CBZ files into ready-to-direct chapters.
It carries `make_chapter.py` and `../layer-splitter/split_layers.py`; rebuild it with `python tools/build_notebooks.py`
after changing either script.

**Drive layout:** `MyDrive/Storyteller/cbz/*.cbz` in, `MyDrive/Storyteller/chapters/chapter_<id>.zip` out.

**Per chapter** (`make_chapter.py --cbz-dir … --out … --chapters 1-5,94`):

1. finds the CBZ by its number (`..._94_-_Chapter_94.cbz` → chapter `94`, id `094`; `94.5` → `094-5`);
2. drops the series title page and the creators' promo page: the first two and last two pages are compared with
   fingerprints taken from chapter 94 (`NON_STORY`); `--skip '{"94": [0, 69]}'` drops pages by hand;
3. joins the pages and runs `split_layers.split_image`;
4. converts to WebP (backgrounds q80, characters q85, bubbles q90, `method=6`), assigns each bubble to a panel
   (never a tiny one), and draws overview sheets;
5. writes `chapter_<id>.zip` (built locally, then moved into place whole). Chapters with a zip are skipped unless `--redo`.

**The zip** holds `<id>/`:

| File | What |
|---|---|
| `panel_XX_background.webp`, `panel_XX_characters.webp` | the layers |
| `bubble_XX.webp` | the speech bubbles |
| `chapter.json` | number, source file, dropped pages, strip size, panels (`x, y, width, height, tiny`, and `continues: panel_XX` for a piece cut from the same tall picture as the panel before), bubbles (`panel`, `x, y, w, h` in that panel's pixels, `between_panels`, `suspect`) |
| `sheets/pages.jpg` | every page, dropped ones crossed out |
| `sheets/panels_XX-YY.jpg` | the original panels, five per sheet, numbered |
| `sheets/bubbles.jpg` | every bubble with the panel it belongs to |

A chapter zip in `--out` or a `--done-dir` whose panels are over 4.5 strip widths tall was made before tall panels were
split up (its cutouts are squashed): it is made again automatically. Title and promo pages are recognised by fingerprint,
but a plain page (black, a fade) is never dropped, as it sits near every fingerprint.

`tiny` panels (under 120 px on a side or 40,000 px²) are crumbs the panel finder picks up, such as a flash fragment
or the tail of a bubble; the director skips them. `suspect` bubbles are small ones worth a second look.

Tested here on chapter 94 with stand-in models (no GPU): 70 pages, title and promo dropped, 92 panels (2 tiny), 26 bubbles,
all real, about 3.5 minutes without the AI models.
The user's real Colab run of chapter 94 (T4) gave exactly the same: 92 panels (2 tiny), 26 bubbles, zip 14.5 MB.
