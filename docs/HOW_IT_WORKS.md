# How Storyteller works: every step, every script

This file explains the whole project from start to finish: how a chapter's CBZ file becomes layers, how a chapter is
directed, how the music is made, how the reader (the frontend) plays it all, and how the result is given out (the
desktop reader, the websites and the demo video). Every script is covered: what it does, how it does it, the
numbers it uses, and how to run it.

The short version is in [`README.md`](../README.md). The project diary for working sessions is [`HANDOFF.md`](../HANDOFF.md).

---

## Contents

1. [The whole process at a glance](#1-the-whole-process-at-a-glance)
2. [Step 1: the chapter files (CBZ)](#2-step-1-the-chapter-files-cbz)
3. [Step 2: the chapter maker (`make_chapter.py`)](#3-step-2-the-chapter-maker-make_chapterpy)
4. [Step 3: the layer splitter, the AI part (`split_layers.py`)](#4-step-3-the-layer-splitter-the-ai-part-split_layerspy)
5. [Where the chapter maker runs: Colab, Kaggle, the PC](#5-where-the-chapter-maker-runs-colab-kaggle-the-pc)
6. [Step 4: directing a chapter](#6-step-4-directing-a-chapter)
7. [Step 5: music, sound effects and voices](#7-step-5-music-sound-effects-and-voices)
8. [Step 6: the frontend, the reader (`site/`)](#8-step-6-the-frontend-the-reader-site)
9. [Step 7: giving out the result](#9-step-7-giving-out-the-result)
10. [Reference: every setting of a scene](#10-reference-every-setting-of-a-scene)
11. [Reference: every script and command](#11-reference-every-script-and-command)
12. [Problems already solved, and the rules that keep them solved](#12-problems-already-solved-and-the-rules-that-keep-them-solved)

---

## 1. The whole process at a glance

```
 ┌──────────────┐   ┌────────────────────────┐   ┌──────────────────┐   ┌────────────────────┐
 │ 1. CBZ files │──►│ 2-3. Chapter maker     │──►│ chapter_<id>.zip │──►│ 4. Directing       │
 │ (the pages)  │   │ + layer splitter (AI)  │   │ layers, bubbles, │   │ draft_chapter.py + │
 │ Drive/Kaggle │   │ on Colab, Kaggle or PC │   │ chapter.json,    │   │ the AI director →  │
 └──────────────┘   └────────────────────────┘   │ overview sheets  │   │ chapter.js         │
                                                 └──────────────────┘   └─────────┬──────────┘
                                                                                  │ preview → your approval
 ┌──────────────┐   ┌────────────────────────┐   ┌──────────────────┐   ┌─────────▼──────────┐
 │ 5. Music     │──►│ site/music/*.mp3       │──►│ 6. The reader    │──►│ 7. Given out:      │
 │ MusicGen +   │   │ themes in series.js    │   │ site/index.html  │   │ desktop reader,    │
 │ make_loop.py │   └────────────────────────┘   │ GSAP + Web Audio │   │ websites, video    │
 └──────────────┘                                └──────────────────┘   └────────────────────┘
```

| Step | What goes in | What comes out | Script(s) | Runs on |
|---|---|---|---|---|
| 1. Chapter files | your licensed downloads | `*.cbz` in Drive `Storyteller/cbz` and the Kaggle dataset `tbate-cbz` | (by hand) | your PC |
| 2. Chapter maker | a CBZ | `chapter_<id>.zip` (~5–15 MB) | `tools/make-chapter/make_chapter.py` | a GPU: Colab, Kaggle or your PC |
| 3. Layer splitter | one long strip of pages | panels, characters, backgrounds, bubbles | `tools/layer-splitter/split_layers.py` | (called by step 2) |
| 4. Directing | the chapter zip | `site/chapters/<id>/chapter.js` | `tools/director/draft_chapter.py`, then an AI director in a Claude Code session; `cut_chapter.py` for demos | the cloud session |
| 5. Music | text descriptions | seamless loops `site/music/<theme>_<n>.mp3` | `tools/music/Make_Music.ipynb`, `tools/music/make_loop.py` | Colab (GPU), then any computer |
| 6. The reader | `chapter.js` + images + music | the animated chapter in a browser | `site/index.html`, `site/series.js` | any browser |
| 7. Giving out | the `site/` folder | desktop reader, reader packs, website zips, demo video | `tools/reader/*` | any computer |

**Two rules hold everywhere:**
- **Chapter images are never stored on GitHub** (`.gitignore` keeps out `site/chapters/*/*.webp` and `*.jpg`). They live
  in the chapter zips, your Drive, and the zips sent to you.
- **You approve every chapter** before it goes into the reader.

---

## 2. Step 1: the chapter files (CBZ)

A CBZ is an ordinary zip file holding a chapter's pages as images (JPG, PNG, WebP or AVIF), named in reading order.

- They are downloaded by you, from a source you are allowed to use. The project never scrapes manhwa websites.
- They are kept in **Google Drive `Storyteller/cbz/`** (about 280 files, 2.8 GB) and in the private **Kaggle dataset
  `tbate-cbz`**.
- The file name must contain the chapter number. `The_Beginning_After_the_End_94_-_Chapter_94.cbz` is chapter 94.
  The maker looks for "chapter" followed by a number first; failing that, it takes the last number in the name.
  Half chapters work too: `94.5`.
- Files can sit in subfolders: the maker searches the whole folder.

**Chapter ids.** Every chapter gets a 3-digit id used for folder names and the reader's address: chapter 94 → `094`,
chapter 94.5 → `094-5`, chapter 1 → `001`. Chapter numbers are always the series' own numbers.

---

## 3. Step 2: the chapter maker (`make_chapter.py`)

`tools/make-chapter/make_chapter.py` turns CBZ files into ready-to-direct chapter zips, one chapter after another.

```bash
python make_chapter.py --cbz-dir CBZ_FOLDER --out OUT_FOLDER --chapters 1-5,94
```

| Option | What it does |
|---|---|
| `--cbz-dir` | the folder with the CBZ files (subfolders are searched too) |
| `--out` | where finished zips go. **Only** the zips are written here (it may be Google Drive) |
| `--chapters` | `94`, `1-5`, `1-5,94`, `100.5`: ranges and lists, half chapters allowed |
| `--skip '{"94":[0,69]}'` | drop pages by hand, per chapter (page numbers from 0; `-1` is the last page) |
| `--work` | a scratch folder for the work in progress (default `work`) |
| `--redo` | make chapters again even if their zip exists |
| `--models` | which cutout models (default: both, see section 4) |
| `--shard K/N` | take every Nth chapter of the batch, starting at the Kth, so N graphics cards share a batch |
| `--done-dir DIR` | skip chapters whose zip is already in another folder (an earlier run's output); can be repeated |
| `--max-hours H` | don't start another chapter after H hours |

### What it does for each chapter

**1. Find the pages.** It opens the CBZ, takes every image (ignoring `__MACOSX` junk), sorts them in natural order
(`2.jpg` before `10.jpg`) and saves them as `000.jpg`, `001.jpg`, …

**2. Drop the pages that aren't story.** Chapters start with the series title page and end with the creators' promo
page. The maker recognises these by their look, using a **difference hash** ("dhash"):
- the page is shrunk to 17 × 32 grey pixels, and each pixel is compared with its right-hand neighbour, giving 512
  yes/no bits: a fingerprint of the page's shapes;
- two reference fingerprints, taken from chapter 94's title page and promo page, are stored in the script (`NON_STORY`);
- **only the first two and last two pages** are checked. A page counts as non-story when its fingerprint differs from a
  reference by **at most 110 of 512 bits** (the closest real story page in chapter 94 differs by 156) **and** by
  fewer bits than the page itself has set. That second test matters because a plain page (all black, a fade, a small
  picture on black) has almost no bits set, so it sits close to *every* fingerprint. Without it, a black page was taken
  for the promo page (Kaggle's chapter 22);
- pages can also be dropped by hand with `--skip`.

**3. Join the pages into one strip.** Webtoon panels often run across page breaks, so all kept pages are stacked into
one very tall picture. Pages of a different width (rare) are scaled to the most common width. Chapter 94's strip is
940 × 125,394 pixels.

**4. Split the strip** with the layer splitter (section 4). It finds the panels, cuts out the characters, fills in
the backgrounds and saves the speech bubbles.

**5. Convert for the web (WebP).** For each panel:
- `panel_XX_background.webp`: quality 80;
- `panel_XX_characters.webp` (see-through): quality 85;
- `bubble_XX.webp`: quality 90.

All use WebP `method=6`, the slowest and smallest. A whole chapter comes to about 10 MB.

**6. Mark tiny panels.** A "panel" under 120 px on a side, or under 40,000 px² in area, is a crumb the panel finder
picked up (a flash fragment, the tail of a bubble). It's marked `tiny: true` and the director skips it.

**7. Give every bubble a panel.** A bubble belongs to the panel its centre sits in. If it sits between panels, it goes
to the nearest one above or below and is marked `between_panels: true`. It never goes to a tiny panel. Its position
is stored **in that panel's own pixels** (`x, y, w, h`). Small or flat bubbles (under 12,000 px², or under 70 px on a
side) are marked `suspect: true`: they may be an eye or a highlight, so the director checks them.

**8. Draw overview sheets** for checking by eye:
- `sheets/pages.jpg`: every page in rows of 14, numbered, with dropped pages crossed out in red and labelled DROPPED;
- `sheets/panels_XX-YY.jpg`: the original panels, five per sheet, labelled with number and size (TINY marked);
- `sheets/bubbles.jpg`: every bubble on grey, labelled `bubble_07 > panel_12` (`?` for suspect ones).

**9. Write `chapter.json`:**

```json
{
  "id": "094", "number": "94", "source": "The Beginning After the End 94 - Chapter 94.cbz",
  "pages": 70, "dropped_pages": {"000": "series title page", "069": "creators' promo page"},
  "strip": {"width": 940, "height": 125394},
  "panels": [{"id": "panel_01", "x": 0, "y": 0, "width": 940, "height": 1210, "tiny": false}, "..."],
  "bubbles": [{"id": "bubble_01", "panel": "panel_05", "x": 412, "y": 96, "w": 310, "h": 188,
               "between_panels": false, "suspect": false}, "..."],
  "webp_quality": {"background": 80, "characters": 85, "bubble": 90},
  "seconds": {"split": 812.4, "cutout birefnet-general": 340.1, "...": 0}
}
```

A panel cut from the same tall picture as the panel before it carries `"continues": "panel_XX"` (see `split_tall` in
section 4). The example values above are for illustration only.

**10. Make the zip safely.** The zip (`chapter_<id>.zip`, files inside `<id>/`, stored without extra compression because
WebP and JPEG are already compressed) is built in the scratch folder, copied to `<out>` as `chapter_<id>.zip.part`,
then renamed. A disconnect halfway never leaves a broken zip that looks finished. The scratch folder is then deleted.

### Batches, restarts and the time limit

- **Done chapters are skipped.** A chapter is done when its zip is in `--out` or any `--done-dir`. So a batch can simply
  be started again after Colab disconnects or Kaggle stops.
- **Old zips are remade by themselves.** A zip made before the tall-panel fix (it has a panel taller than 4.5 strip
  widths, `made_before_tall_fix`) counts as not done.
- **Shards:** with `--shard 1/2` and `--shard 2/2`, two processes split the batch by position in the sorted chapter
  list. The split is the same on every run, whatever is already done.
- **Time limit:** with `--max-hours`, no chapter is started once the time left is under 1.2 × the slowest chapter so
  far. The rest are listed as "left for the next run".
- A failing chapter doesn't stop the batch. Failures are listed at the end, and the exit code is 1.
- Each chapter prints how long each AI step took per panel (stored in `chapter.json` → `seconds`).

**Speed:** about 3.7 s per cutout model per panel on a T4 and about 10 s per panel in all, so **13–23 minutes per
chapter**.

---

## 4. Step 3: the layer splitter, the AI part (`split_layers.py`)

`tools/layer-splitter/split_layers.py` does the real work on the strip. It can also be used on its own:

```bash
python split_layers.py path/to/images --out layers [--join] [--models birefnet-general]
```

`--join` stacks all the images into one strip first (pages of the same width). The output per strip is
`panel_XX/original.png`, `panel_XX/background.png`, `panel_XX/characters.png`, `bubbles/bubble_XX.png`, a
`preview.png` (panels outlined green, characters tinted pink, bubbles red) and `layers.json` (where everything sits).

The order is: **bubbles first** (so they don't confuse the panel finder), then **panels**, then for each panel the
**characters**, the **background fill** and the **edge colours**.

### 4.1 Speech bubbles (`find_bubbles`)

No AI here, just rules that were tuned on real chapters:

1. **Near-white areas:** pixels whose darkest channel is above 225 and whose channels differ by under 25 (white, not
   pale yellow). Connected areas under 1,500 px are ignored.
2. **Fill the holes** of each area. The holes are where the lettering is.
3. **Lettering share:** holes must be 2–45% of the filled shape (a big white sky has none; a white slash has too
   much). **Roundness:** the filled shape must cover over 45% of its box.
4. **Black ink:** over 30% of the hole pixels must be dark (brightest channel under 100). Real bubbles score about 0.65;
   white slashes and glows score about 0.
5. **Several letters:** at least **2 separate dark shapes** 5–70 px tall and at least 6 px in area. An eye's white has
   one dark shape (the pupil), so eyes are left in the art.
6. **Neutral ink:** at most 5% of the hole pixels may be colourful (channel spread over 60). Sylvie's white fox face has
   coloured eyes, so it's left in the art.

Each bubble found is **grown by 15 px**, so its black outline comes with it. It is then saved as a see-through PNG.

### 4.2 Panels (`find_panels` and `split_tall`)

1. **The gutter colour** is the most common colour on the strip's border (black or white, usually).
2. A pixel is "content" when it's more than 18 levels away from the gutter colour (bubbles, grown by 15 px, are ignored).
3. **Rows** with over 5% content are panel rows. Runs of at least 60 such rows make a panel band. Inside a band, the
   **columns** with over 5% content give the left and right edges (runs of at least 30).
4. A strip with no gutters at all is one panel.

**`split_tall`, for very tall "panels":** webtoons pace scenes with long stretches of plain space (black with a few
embers, a fade, a faint texture) that aren't the gutter colour. To the gutter test, that's one "panel" many screens
tall. That caused two bugs: the cutout models squash every panel into a square (ruining the cutout), and WebP can't
store pictures over 16,383 px tall (10 Kaggle chapters failed). So:

- a panel taller than **2.5 strip widths** is examined row by row. **Row busyness** is the share of a row's pixels that
  differ by more than 40 from that row's median colour (computed in 2,048-row blocks, every 2nd column, to save memory);
- **plain rows** (busyness under 0.03) in runs of at least **0.5 strip widths** are dropped, like gutters;
- what's left between them are the pictures. A piece with fewer than **120 busy rows** is a crumb and is dropped;
- a piece still taller than **4.5 strip widths** is cut at its **calmest row**: busyness smoothed over 31 rows, with a
  slight pull toward the middle and never within one strip width of either end. This repeats until every piece fits;
- a cut that didn't fall in a plain band marks the lower piece `continues: panel_XX`, so the director keeps the camera
  move going across the cut.

Chapter 94 is unchanged by this: its tall panels are real pictures.

### 4.3 Characters: the cutout models (`Models.character_alpha`)

- **Two AI models** from the `rembg` library: **`birefnet-general`** (the most reliable) and **`birefnet-hrsod`** (adds
  edges the first one misses). All of rembg's models were compared on real webtoon panels. `lite`, `massive`, `dis` and
  `isnet-anime` grabbed chunks of background or missed parts of characters. **Both models always run** (you chose
  accuracy over speed). Without a graphics card, only `birefnet-general` runs.
- **Each model sees the panel twice**, as drawn and mirrored. The two masks are averaged, which drops glows and auras
  that only one view mistakes for a character.
- **The two models' masks are combined by taking the maximum**: anything either model sees as character is kept (each
  misses different bits, a hand here, an outline there).
- **Edge refinement with ViTMatte** (`rembg.matting.vitmatte_alpha`, when the installed rembg has it) redraws the soft
  edge band: crisper hair and flames, no see-through ghost patches. Its output tops out at 254, so values ≥ 250 are set
  back to fully solid. Fine lines the models were sure of (≥ 200: speed lines, outlines) keep their value.
- Inside the bubbles the mask is cleared, and values under 20 become fully see-through.

**Edge colours (`character_colours`):** on soft edges, the drawn colour is mixed with the background behind it.
`pymatting`'s `estimate_foreground_ml` unmixes it, so a character moved over a new background has no fringe of the
old one. Fully solid pixels keep their exact drawn colour.

Note: rembg resizes every panel to 1024 × 1024 for the model, which is why tall panels must stay under 4.5 strip widths.

### 4.4 Backgrounds: filling the holes (`Models.fill_background`)

When the characters move separately from the background, the background needs something where they used to be.

- **The holes:** the character mask (values over 40) grown by 31 px, plus the bubbles grown by 9 px. Glows and outlines
  around characters are painted over too.
- **LaMa** (an AI inpainting model, loaded from `simple-lama-inpainting`) paints the holes in. It works at up to
  **2,048 px** on a graphics card (800 px on the processor): bigger panels are shrunk, filled and scaled back up.
  If the graphics card runs out of memory, it tries again at half the size (down to 256 px).
- Pixels outside the holes are kept **exactly** as drawn: only the holes take LaMa's paint.

### 4.5 Making it run on the graphics card (`Models.__init__`, `_move_to_gpu`)

This part makes the same code fast on Colab, Kaggle and your PC:

- **Which hardware:** NVIDIA CUDA if PyTorch sees a card and ONNX Runtime has the CUDA provider; else **DirectML**
  (Windows, any graphics card); else the processor. On Windows, `onnxruntime.preload_dlls()` finds the CUDA libraries
  that came with PyTorch.
- **The models are made on the processor first**, then moved to the graphics card only after a warm-up run proves they
  work there. ONNX Runtime normally falls back to the processor *silently* when the graphics card fails (that happened
  on Kaggle's T4 with CUDA 13), so fallback is switched off during the test. Two ways of picking algorithms are
  tried: `HEURISTIC` (newer cards) and `DEFAULT` (the only one that works on a T4).
- **Memory:** each model hands its graphics memory back after every run ("arena shrinkage", `kSameAsRequested`).
  Without this, the three models filled a 15 GB T4 before LaMa got any. LaMa empties PyTorch's cache after each fill.
- **Low-memory settings** (`enable_cpu_mem_arena = False`, `enable_mem_pattern = False`) let both models fit in
  Colab's memory. Without them they needed about 14 GB and crashed it.
- It prints where each step runs ("graphics card (fast)" or "processor (slow)"), and `Models.timings` adds up the
  seconds per step.

**`gpu_check.py`** loads the models once (downloading about 2.3 GB the first time) and exits with code **0** if the
cutouts run on the graphics card, or **3** if they run on the processor. The Kaggle notebook and the PC setup use that
code to try another build of ONNX Runtime.

---

## 5. Where the chapter maker runs: Colab, Kaggle, the PC

The same two scripts run in three places. The notebooks **carry copies of the scripts** inside them (`%%writefile`
cells), written by `tools/build_notebooks.py`. **Run `python tools/build_notebooks.py` after every change** to
`split_layers.py`, `make_chapter.py` or `gpu_check.py`, and commit the notebooks with the scripts.

### Install line (Colab and Kaggle)

```
pip uninstall -y onnxruntime            # the plain build must go first: it can't sit next to the GPU build
pip install "rembg[gpu]" opencv-python-headless scipy
pip install --no-deps simple-lama-inpainting==0.1.2   # --no-deps: it pins an old Pillow that no longer installs
```

### Google Colab: `tools/make-chapter/Make_Chapter.ipynb`

1. Upload the notebook to Colab. **Runtime → Change runtime type → T4 GPU**, plus **High-RAM**.
2. Set `CHAPTERS` (and if needed `SKIP_PAGES`, `REDO`, `DOWNLOAD`, `DRIVE_FOLDER = "Storyteller"`).
3. **Runtime → Run all**, and allow Google Drive access.
4. It reads `MyDrive/Storyteller/cbz`, writes zips to `MyDrive/Storyteller/chapters`, shows each chapter's page sheet,
   and (with `DOWNLOAD = True`) downloads the zips too.

The browser tab must stay open.

### Kaggle: `tools/make-chapter/Make_Chapters_Kaggle.ipynb` (big batches)

- About **30 free GPU hours a week**, **two T4 cards** (two chapters at once), and it keeps running after the browser is
  closed. Needs a verified phone number.
- Set up: dataset `tbate-cbz` as **Input**, **Accelerator: GPU T4 ×2**, **Internet: On**, and import the notebook via
  **File → Import Notebook**.
- Run: set `CHAPTERS` (a big range is fine) and `MAX_HOURS = 11` (Kaggle stops a run at 12 hours), then **Save Version →
  Save & Run All (Commit)**.
- Inside, it starts **one `make_chapter.py` process per graphics card** (`CUDA_VISIBLE_DEVICES=0` with `--shard 1/2`,
  `CUDA_VISIBLE_DEVICES=1` with `--shard 2/2`). Each writes its log to `log_gpu0.txt` / `log_gpu1.txt` in the Output,
  progress prints every 5 minutes, and the end shows the last lines of each log.
- If the cutouts land on the processor, it installs `onnxruntime-gpu==1.22.0` (the CUDA 12 build) and checks again.
- **Next run:** add the previous version's **Output** as an Input. Its zips are found and passed as `--done-dir`, so the run
  continues where the last one stopped.

### Your PC (NVIDIA card, Windows): `tools/pc/` → `Storyteller-PC-Tools.zip`

`python tools/build_notebooks.py` also writes `dist/Storyteller-PC-Tools.zip`: `Setup.bat`, `Make Chapters.bat`,
`README.txt` and the three scripts. The `.bat` files and `README.txt` use Windows line endings (CRLF) and must keep them.

- **`Setup.bat` (once, 10–20 minutes, about 6–8 GB):** needs Python 3.12. It keeps the models in the kit folder
  (`U2NET_HOME`, `TORCH_HOME`, `HF_HOME` = `models\`, not on drive C:), then:
  1. makes a private Python folder `.venv`;
  2. installs PyTorch for RTX 50-series cards (`--index-url https://download.pytorch.org/whl/cu128`), `rembg[gpu]`,
     OpenCV, SciPy and `simple-lama-inpainting` (`--no-deps`);
  3. runs `gpu_check.py`. If the cutouts are on the processor, it tries `onnxruntime-gpu==1.22.0`, then
     `onnxruntime-directml`;
  4. ends with "All set" or "Send Claude a screenshot".
- **`Make Chapters.bat`:** asks for the CBZ folder (remembered in `cbz-folder.txt`) and which chapters. It runs
  `make_chapter.py` into the `finished\` folder and opens that folder when done. Closing the window stops it;
  starting it again carries on.

---

## 6. Step 4: directing a chapter

Directing turns a chapter zip into a **scene plan**, `site/chapters/<id>/chapter.js`: how each panel moves, when each
bubble pops, which impacts, particles, sounds and music. An AI director does this in a Claude Code session, then you
review a preview and approve or send notes.

### 6.1 The first draft: `tools/director/draft_chapter.py`

```bash
python tools/director/draft_chapter.py chapter_094.zip --out site/chapters/094/chapter.js --title "The Duel"
```

From `chapter.json`, for every non-tiny panel:

| Panel shape (height ÷ width) | Draft |
|---|---|
| over 1.45 (taller than a screen) | `fit: "pan"` (pans down it), `length` = 140 + 70 × ratio, rounded to 10, at most 400 |
| under 0.3 (a thin strip) | `length: 110` |
| otherwise | `length` = 140 + 60 × min(ratio, 1.2), rounded to 10, plus a gentle push-in: `camera` scale 1 → 1.06 |

- The first panel enters with a `cut`, the rest `fade` in, and all `fade` out.
- Every panel gets dust particles (`ambient: "dust", tint: "paper", amount: 0.4`).
- **Bubbles** go in reading order (top to bottom in 80 px rows, then left to right). Their pop-in times are spread over
  the first part of the panel: one bubble at 0.12, several from 0.1 to 0.6. Suspect bubbles are left out as
  `// check bubble_XX: small, may be an eye…` comments.
- **Pieces of one tall picture** (`continues`) get plain `cut` exits and entries, with a note to keep the camera move going.
- Music starts as one `calm` stretch.

**`--carry-over OLD/chapter.js --report`** keeps the choreography of an earlier plan when a chapter is split again:
- `node` loads the old plan (`registerChapter` is caught);
- new panels and old scenes are paired by **size (±3 px), in order**, using a longest-common-sequence match, so a few
  new panels in between don't break the pairing;
- old scenes left over in a gap are paired by position and marked `resized … check`;
- bubbles keep their old timing when one sits within 12 px of an old bubble; others are marked new (`at: 0.12`);
- music stretches are moved to the new panel names.

This is how chapter 94's 60 approved duel scenes moved onto panels 10–69 of the full split (58 identical, 2 resized).

### 6.2 Directing (the creative part)

The director goes through the panel sheets and the draft, panel by panel, and follows the **house style**:

- **Camera:** a gentle push-in (scale 1 → 1.06–1.2) or settle-out (1.1–1.16 → 1) per panel, with `origin` on the subject.
  Tall panels `fit: "pan"` with a slight `chars` scale for depth. Wide shots drift sideways (`camera x` ±4–7). Never
  crop lettering (chapter 94, panel 34 zooms *out* so "F---!" stays).
- **Transitions:** `fade` by default. **Zoom-through** (`exit: "zoom"` with a `focus`, then the next `enter: "zoom"`)
  for build-ups into a big moment (78 → 79 TEMPEST). `cut` for direct continuations and match cuts.
- **Impacts:** shake + flash + burst + sound at the same moment. `deflect` for blades turned aside, `parry` for heavy
  clashes, `crash` with a held white-out for the biggest hit, `shatter` sound + `shatter` burst for glass, `thud` for
  bodies hitting the floor, `crack` for a stab, `grip` for anger, `glint` for a blade catching light.
- **Particles:** embers in each fighter's colour (`mana` blue for sword mana, `ember` orange for anger, `wind`
  green-white for Arthur's TEMPEST), `speed` streaks for dashes, `dust` for calm scenes. `amount` from 0.25 (quiet)
  to 1.7 (TEMPEST).
- **Bubbles:** pop once the reader can see the speaker (`at` 0.06–0.4), staggered when there are several. Lettering
  drawn on the art uses `pop: false`. A bubble placed outside a `pan` panel must be moved inside it. A bubble low on a
  tall panel needs `out` ≥ 0.92.
- **Music:** one theme per story stretch. Climax for the finale, calm after the storm.
- **Quiet beats:** after a big moment, one still panel with few particles and no sound.
- **Cast and colours** come from `series/cast.md` (about 95 characters: looks, magic colours, first episodes).

**Checks before review:** the chapter is played in a headless browser (Playwright). Every image loads, no bubble falls
off screen, the effects fire at their moments, and screenshots of key moments are taken. Then a preview goes to
you. **Only an approved chapter is added** to `site/series.js` and given out.

### 6.3 Demo cuts: `tools/director/cut_chapter.py`

Makes a short chapter from chosen scenes of a directed one, **exactly as directed**, and copies their images and bubbles:

```bash
python tools/director/cut_chapter.py site/chapters/094 --id 094-demo --title "The Duel" \
    --panels 01,02,04,06,07,70-72,74-76,78,79,81,84,86,87,89,92 --music "tension:01,climax:70,calm:92"
```

`--music theme:panel` starts a theme at that panel, and each theme plays until the next one starts. This made the
19-scene public demo (8 bubbles, 4,850 units long).

---

## 7. Step 5: music, sound effects and voices

### 7.1 Making music: `tools/music/Make_Music.ipynb` (Colab)

- Uses **MusicGen large** (`facebook/musicgen-large`, Meta's free music model, non-commercial use), on a T4 GPU.
- One track per **text description**, named `<theme>_<take>`, for example `"sad_1": "sad emotional piano melody with
  soft strings, grief and loss, slow and tender, cinematic anime drama, 70 bpm, instrumental, no vocals"`. Every
  description says *instrumental, no vocals*: lyrics distract from reading.
- 30 seconds each (`SECONDS = 30`, MusicGen's limit), sampling with `guidance_scale=3.0` and a fixed seed per track.
- A first rough loop: the last 1.5 s are blended into the start, then one fixed gain sets the peak to 0.89. The file is
  saved as 128 kbps MP3.
- The tracks go into `music_takes.zip` (downloaded and saved to Drive `Storyteller/music_takes`), which you send to Claude.
- The current notebook makes the missing themes: `calm_2`, `tension_2`, `sad_1–2`, `eerie_1–2`, `triumph_1–2`,
  `warm_1–2`. **Not run yet.**

### 7.2 Making seamless loops: `tools/music/make_loop.py`

```bash
python make_loop.py in.mp3 out.mp3 TAIL_SECONDS
```

`TAIL_SECONDS` is how much of a fade-out or silent ending to drop. Then:

1. Skip the first 1.6 s (the old blended start) and drop the tail.
2. **Find the beat:** an onset envelope (spectral flux, 100 frames a second) is computed. The script then picks the
   longest loop length whose rhythm best lines up with the start (3 s of onsets compared), searching the last 20% of
   possible lengths.
3. **Equal-power crossfade** of 1 s: the end runs into the beginning with sine/cosine curves, so the loudness never dips.
4. **One fixed gain** to about **−16 LUFS** (measured with ffmpeg's EBU R128 meter), with the peak kept under −1 dBFS.
   A gain that changes over time would break the loop seam.
5. Save as 128 kbps mono MP3, and print the loop length, the rhythm match, the loudness and the "edge step" (the
   jump at the seam).

The AI can't listen to music, so loops are judged by these measurements. Then the loop goes in `site/music/` and gets a
line in `SERIES.themes` with a `volume` that evens out its loudness.

### 7.3 The music library now (`site/music/`, 2.7 MB)

| Theme | Takes (volume) | Sound | Used in chapter 94 |
|---|---|---|---|
| `calm` | `calm_1` (0.5) | gentle harp and flute | panels 88–92 |
| `tension` | `tension_1` (0.4) | music box over a slow beat | 1–14 |
| `battle` | `battle_1` (0.53), `battle_2` (0.63) | driving orchestra | 15–31, 49–57 |
| `battle_dark` | `battle_dark_1` (0.58), `battle_dark_2` (0.5) | heavy bass, trap drums | 32–48 |
| `climax` | `climax_1` (0.75), `climax_2` (0.56) | war drums and choir | 58–87 |

When a chapter uses a theme a second time, it plays the theme's next take (`take: 0` picks one by hand).

### 7.4 Sound effects

- **13 made by code in the browser** (no files): `whoosh`, `swish`, `crack`, `grip`, `flame`, `clang`, `skid`, `tap`,
  `thud`, `glint`, `shatter`, `crash`, `gust`. Each recipe is filtered noise and/or tones with sharp envelopes. For
  example, `clang` is six inharmonic partials (622–5,210 Hz) ringing for different lengths, on a sharp high-noise
  attack and a low thump. Section 8.8 has the details.
- **2 recordings** (`site/sfx/`, listed under `SERIES.sounds`): your Sekiro **`deflect`** and **`parry`**, trimmed, with
  the highs eased and pitched about 2 semitones lower. They play at a random speed between 0.98 and 1.02, so no two
  strikes sound alike. A missing recording falls back to `clang`.

### 7.5 Voices (switched off)

`tools/voices/make_voices.py` makes voice lines with **Kokoro** (free, no graphics card). Each character's voice is a
weighted blend of Kokoro's preset voices plus a pitch shift and speed: Arthur is built on `am_onyx`, the deepest, taken
lower still. It writes several takes per line to `out/candidates/`. ffmpeg shifts the pitch, adds a touch of room
(`aecho`) and evens the loudness (`loudnorm I=-16`). Voices are **off at your request**. The playback code is in git
history (commit `77414a1`).

---

## 8. Step 6: the frontend, the reader (`site/`)

The reader is **one HTML page with no build step**: plain HTML, CSS and JavaScript, plus two libraries loaded from
CDNs. It runs in any modern browser, on a PC or a phone.

### 8.1 Files

| File | What it holds |
|---|---|
| `site/index.html` (~1,200 lines) | everything: styles, page structure, the engine (scenes, timeline, particles, sound, auto-scroll, chapter menu). No chapter data inside |
| `site/series.js` | the series: `title`, `playlist` link, `credit` line, `chapters` list (in reading order), music `themes`, `mix`, `autoScroll`, recorded `sounds` |
| `site/chapters/<id>/chapter.js` | one chapter: `registerChapter({ id, title, number, music, scenes })` |
| `site/chapters/<id>/*.webp` | its images (not in git) |
| `site/music/*.mp3`, `site/sfx/*.mp3` | the music loops and the recorded sword sounds |
| `site/README.md` | the developer reference for the reader |

**Libraries:** GSAP 3.12.5 and its ScrollTrigger plugin (from cdnjs), the Google Fonts Bangers, Archivo Narrow and
IBM Plex Mono, and, only on the desktop reader, `qrcode-generator@1.4.4` (from jsdelivr) for the phone QR code. That's
why the reader needs an internet connection.

### 8.2 The look

- **Neo-noir comic**, inspired by "The Notturno Experience": ink black `#0b0a0d` (`--ink`), a second ink `#17151b`,
  paper white `#f1ece4` (`--paper`), muted `#a39d96`, and **one flat red** `#e5202e` (`--red`), with halftone dots.
- **Fonts:** **Bangers** for headlines (skewed, with a red offset shadow), **Archivo Narrow** for text, **IBM Plex Mono**
  for labels, buttons and numbers. Each has system fallbacks (Impact, Arial Narrow, Menlo).
- One dark look on purpose (`color-scheme: dark`).

### 8.3 The page, top to bottom

1. **Title card:** eyebrow "STORYTELLER / series title", the chapter title in Bangers, a short explanation, the
   **credit line** (from `SERIES.credit`, `**bold**` names), the buttons **▶ Auto-scroll**, **Play with sound** and
   **Reading playlist ↗** (Spotify, a link only), the **auto-scroll speed** slider, the **Read on your phone** box
   (desktop reader only), and the **Chapters** menu (number, title, panel count; the current one is marked red).
2. **The stage (`#story`):** a very tall block (`total length in vh + one screen`) with a **pinned viewport** inside it.
   As you scroll through the block, the viewport stays put and the chapter plays in it.
3. **The HUD** over the stage: a thin red **progress bar**, the **panel counter** ("Panel 07 / 90") and the **Auto** /
   **Sound** buttons.
4. **End card:** "End of Ch. 94 · The Duel", "To be continued" or "Next: <title>", the credit line, **Next chapter →**
   and **All chapters ↑**.

### 8.4 How a chapter starts (boot)

1. `series.js` loads first. On the desktop reader (an `http:` address that is `localhost` or a number like
   `192.168.1.23`), the page also loads `__chapters.js`, which reader.py builds from the chapters folder. That list
   replaces `SERIES.chapters`, so new reader packs show up without a new `series.js`.
2. The address picks the chapter: `index.html#094`. No address or an unknown one → the first chapter. Switching chapters
   reloads the page, so nothing carries over.
3. The page adds `<script src="chapters/<id>/chapter.js">`, which calls `registerChapter(...)`. If it fails, the
   page shows **"Chapter not ready"** (on Cloudflare a missing file returns the main page, which shows up the same way).
4. `boot()` fills in the titles, the counter and the next-chapter link, works out the music (`resolveMusic`), builds
   the scenes, and calls `start()`.
5. `start()` makes the particles and the sound. Then either the **static mode** runs (reduced motion, or GSAP failed to
   load: all images in a plain column, lazy-loaded) or the animated mode: `preload(0)`, `layout()`,
   `buildTimeline()`, `makeAutoScroll()`. A GSAP **ticker** then drives the particles and the sound every frame from the
   timeline's current time.

### 8.5 One panel on the stage (the nested layers, and why)

```
section.scene                     fades in and out (autoAlpha)
 └ .zoom                          enter/exit moves, zoom-through (scale up to 7)
    └ .shake                      impact shakes
       └ .pan                     the pan down a tall panel (CSS translate driven by --pan 0→1)
          └ .rig                  the camera: scale, x / y, around `origin`
             ├ .frame
             │  ├ img.bg          the filled background         (own parallax move: `bg`)
             │  ├ canvas.fx-mid   ambient particles, between background and characters
             │  └ img.chars       the see-through characters    (own parallax move: `chars`)
             └ img.bubble ×n      speech bubbles, over the frame
```

Each kind of movement has its own wrapper, so moves never fight each other. GSAP resets any `translate` on an element
whose transform it animates, so the pan has its own `.pan` wrapper driven by a CSS variable. `.zoom` is centred by hand
(`left: 50%`, `top: 50%`, negative margins), because a grid would pin a panel taller than the screen to the top.

Over all panels: one `canvas.fx-front` (impact bursts, above the flash so sparks fly through it) and one `.flash` layer
(a full-screen colour for flashes and white-outs).

### 8.6 Sizing (`layout()`)

- A normal panel fits **90% of the screen width and 82% of its height**, whichever is smaller.
- A `pan` panel fills **92% of the width, up to 620 px**, keeping its full height. It travels
  `panel height − 86% of the screen` from top to bottom.
- **Bubbles are kept on screen:** at least 8 px from the sides and **56 px clear at the top** (for the buttons). On a
  `pan` panel, a bubble is only kept below the top of the screen at the start.
- Everything is recomputed when the window resizes.

**Loading:** images get their file only when the reader comes near: the current panel, one before and three ahead
(`preload`). A 90-panel chapter never loads all at once.

### 8.7 The timeline (`buildTimeline()`)

The whole chapter is **one GSAP timeline**, with time measured in **units: 1 unit = 1% of the screen height (1vh)**. A
scene with `length: 200` takes two screens of scrolling. **ScrollTrigger** ties the timeline to the scroll position of
`#story` with `scrub: 0.7` (the picture follows the scroll with a 0.7 s smoothing). Scrolling back plays it backwards
exactly. No `invalidateOnRefresh`: it broke the scenes.

For each scene, at its start time `t`, with its length `L` (and `at(f)` = `t + f × L`):

| Part | What the timeline does |
|---|---|
| **Enter** | `cut`: appears at once. `fade`: fades in over 0.12 L while the zoom settles from 0.92 and 4% lower. `zoom`: fades in over 0.1 L while the zoom comes down from **1.7 → 1** (power2.out), starting 4 units early. |
| **Camera** | `.rig` moves from `camera.from` to `camera.to` over the whole scene (linear). `x`/`y` are % of the panel. |
| **Pan** | `--pan` runs 0 → 1 over the whole scene for `fit: "pan"`. |
| **Parallax** | `bg` and `chars` move separately (`from` → `to`). With `over: [a, b]` the move is squeezed into that part of the scene, eased (power2.out). |
| **Bubbles** | pop in at `at(b.at)`: from scale 0.2, tilted −8°, see-through, to full size with an overshoot (`back.out(2.2)`), over 0.08 L. They drift up 12% and fade at `out` (default 0.8; 0.92 or more: they stay). `pop: false`: a plain fade. |
| **Shakes** | at each moment, five quick offsets (−14,6 → 12,−8 → −8,4 → 5,−2 → 0,0) over 0.06 L. |
| **Flashes** | the flash layer takes the `color`, rises to `strength` (default 0.85) over `rise` (0.02 L), **holds** for `hold`, and falls over `fall` (0.07 L). |
| **Sounds** | each `sfx` becomes a cue at `at(f.at)` in timeline time. |
| **Exit** | `fade` (and `cut`, which the engine treats the same way): lifts 6% with a slight zoom and fades over the last 0.1–0.12 L. A hard cut comes from the *next* scene's `enter: "cut"`, which shows it at once. `zoom`: dives in to **scale 7** around `focus` over the last 0.24 L (power2.in), fading out at the very end. |

While scrolling, `onUpdate` moves the progress bar, sets the panel counter, and preloads images around the current panel.

### 8.8 Particles (`makeParticles()`)

- **Ambient particles** live **inside each panel**, on its own canvas between the background and the characters, so the
  characters stand in front of the embers. Kinds:
  - `dust`: slow, drifting up a little;
  - `embers`: rising from the lower half, swaying, glowing;
  - `speed`: long streaks rushing from right to left.

  Base counts are 46, 70 and 22, times `amount`, times 0.55 on narrow screens (under 600 px).
- **Tints** (colour, and a brighter core for the glow): `paper` (warm white), `mana` (blue `70,190,255`), `ember` (orange
  `255,138,42`), `spark`, `wood`, `wind` (green-white `120,255,200`). Glows are pre-drawn radial gradients.
- **Impact bursts** (`fx.bursts`) are drawn on the front canvas over the whole stage, from a point (`from`, % of the
  panel):
  - `splinters`: 30 wood chips and dust puffs;
  - `sparks`: 80 streaks in `spark` and the burst's `tint`;
  - `ring`: 26 puffs in a flat ring;
  - `flare`: 60 rising glows;
  - `shatter`: jagged glass cracks growing out with branches, staying a while, plus flying shards.
- **Bursts rewind:** every particle's path is fixed when the page loads (seeded random numbers), and its position is
  worked out from the scroll position (22 units of scroll = 1 second of burst). Any scroll position can be drawn,
  backwards too.
- **Memory:** a panel's canvas has pixels only while the panel is on screen, its size is capped at 4,096 px, and the
  pixel density is capped at 1.5×.

### 8.9 Sound (`makeSound()` and `makeEffects()`)

- **Off until a tap** on **Play with sound** (browsers block sound before a tap). Sound pauses when the tab is hidden.
- **The chain:**

  ```
  effects ─► effects bus (0.65) ──────────────┐
                                              ├─► limiter (−10 dB, ratio 20, 1 ms) ─► soft clip (tanh, 4× oversampled) ─► speakers
  music takes ─► each take's gain ─► music bus (0.65) ┘
  ```

  The soft clip rounds off any click that is too short for the limiter, so nothing ever distorts.
- **Ducking:** at every effect, the music bus dips to **0.65 × 0.5** (`SERIES.mix.dip`) within about 15 ms, then
  comes back after 0.35 s (smoothing 0.25 s). Without it, the climax drums buried most hits under the limiter (measured).
- **Music:** every take is decoded and plays in a loop from the start, silent, and its level follows the scroll. Each
  stretch fades in over 40 units around its start and out over 60 units around its end, so neighbouring stretches
  **crossfade**. The first one is already playing at the top, and the last has faded out by the end card. The loop
  points skip the few milliseconds of silence MP3 encoders add, so there is no click at the loop.
- **Effects fire going forward only,** as their moment passes, and not on jumps of more than 25 units (a click on the
  chapter menu doesn't fire 40 sounds at once).
- **`makeEffects(ctx, out)`** builds the 13 synthesised effects on any audio context. The same recipes play live and in
  an `OfflineAudioContext` (used to render the demo video's soundtrack). Building blocks:
  - `noiseHit`: white noise through a sweeping filter with an envelope;
  - `tone`: an oscillator with a pitch sweep and an envelope.

  For example, `crash` = a deep 80 → 30 Hz boom + a crackling low-passed burst + a mid crack, and `gust` = two swelling
  band-passed noise rushes.

### 8.10 Auto-scroll (`makeAutoScroll()`)

- **Speed:** 60 units a second at 1× (about 3–4 s per panel). The slider goes from **0.5× to 2×** and is remembered on that
  device (`localStorage` key `storyteller.autoSpeed`).
- **Holds:** it eases almost to a stop (4% speed, the "crawl") at:
  - **every bubble:** `0.6 + w × h / 75,000` seconds, between 1 and 4 (bigger bubbles hold more words);
  - **big moments:** `crash` 1.3 s, `shatter` 0.9, `parry` 0.7, `thud` 0.7, `deflect` 0.6, a strong flash 0.8, a held
    flash 1.4, a `shatter` burst 0.9.

  Moments closer than 8 units share one hold, the longest. The actual hold is `0.3 + pauses × hold ÷ √speed` seconds, with
  **`SERIES.autoScroll.pauses = 0.65`** (1.0 felt too long).
- **Smooth:** it brakes quickly (0.18 s) and sets off gently (0.4 s).
- **You always win:** a wheel, a touch, a mouse press, a scroll key or a scrollbar drag pauses it. Keys and taps on the
  controls themselves work the controls. It stops at the end card, and at the end ▶ starts over from the top.
- Measured: the first bubble holds 1.9 s at 1×, and chapter 94 takes about 6 minutes at 1×.

### 8.11 Desktop-only extras

- **The chapter menu from the folder** (`__chapters.js`, see 8.4).
- **"Read on your phone"** (only when opened as `localhost`): the page asks `__phone.json` for the computer's Wi-Fi
  address and shows it with a **QR code**. Offline, it shows the address alone.

### 8.12 Accessibility

- **Reduced motion** (the system setting): no animation, sound or auto-scroll, just the panels in a plain column.
- Buttons show their state with `aria-pressed` and have visible red focus outlines.
- Each panel is a labelled section ("Panel 7"), and the story is labelled "The Duel, 90 animated panels".

### 8.13 Adding a chapter to the reader

1. Put its folder in `site/chapters/<id>/`: the WebP images plus `chapter.js`.
2. Add a line to `chapters` in `site/series.js`: `{ id: "094", title: "The Duel", number: 94, panels: 90 }`.

The desktop reader doesn't even need step 2: its menu comes from the folder.

---

## 9. Step 7: giving out the result

### 9.1 The desktop reader (`tools/reader/`)

**`Read Storyteller.bat`** (Windows, CRLF) finds Python (`py -3`, else `python`). If neither is installed, it explains
how to install Python. Otherwise it runs `reader.py` and keeps the window open on an error.

**`reader.py`** (standard library only, Python 3.8+):

1. **Finds the reader files:** a `reader/` folder next to it (the ready-made zip). If that's missing but it sits in
   `tools/reader/` of the project, it uses the project's `site/` folder (a GitHub download).
2. **Adds reader packs** from the `new chapters/` folder. A zip is accepted only if **every** entry sits under
   `chapters/`, `music/`, `sfx/`, `index.html` or `series.js`, with no `..`, no absolute paths and no drive letters. It is
   unpacked into the reader, and the zip moves to `new chapters/added/`. Anything else (for example a chapter-maker zip)
   is skipped with a message.
3. **Serves the reader** on port 8000, or the next free one up to 8010, to this computer and the home network
   (`ThreadingHTTPServer`). It sends the right file types, `Cache-Control: no-cache` (so a new chapter shows on the next
   reload), and ignores phones that drop the connection mid-image.
4. **Answers two special addresses:**
   - `/__chapters.js`: every `chapters/*/chapter.js`, read for id, title, number and panel count, sorted by number;
   - `/__phone.json`: the computer's addresses on the home network, skipping `127.*`, `169.254.*` and `0.*`.
5. **Prints** the chapters, any chapters with no pictures yet, the address for this computer and the address for the
   phone, then **opens the browser**.

Options: `--port 8000`, `--no-browser`.

**`build_reader.py`** makes every zip you receive (images must be in `site/chapters/<id>/` first):

| Command | Zip in `dist/` | What's inside | Goes to |
|---|---|---|---|
| `build_reader.py` | `Storyteller-Reader.zip` | `Storyteller Reader/`: the .bat, README.txt, reader.py, an empty `new chapters/`, and `reader/` (index.html, series.js, music, sfx, every chapter in series.js) | your PC (unzip) |
| `build_reader.py --pack 094` | `reader-pack_094.zip` | `chapters/094/*` (`--with-reader` adds index.html and series.js) | PC: `new chapters` folder |
| `build_reader.py --reader-update` | `reader-update.zip` | index.html + series.js | PC: `new chapters` folder |
| `build_reader.py --site` | `Storyteller-Site.zip` | the reader files at the top level, the chapters, and `_headers` (`X-Robots-Tag: noindex, nofollow, noimageindex`) + `robots.txt` (`Disallow: /`), which keep it out of search engines | Cloudflare `tbate-reader` |
| `build_reader.py --site --chapters 094-demo --public URL --cover cover.jpg --out Storyteller-Demo.zip` | `Storyteller-Demo.zip` | the same for chosen chapters, plus link-preview tags (`og:title`, `og:description`, `og:image` 1200 × 627, `twitter:card`) and `cover.jpg`. Search engines are allowed (LinkedIn's preview reads robots.txt) | Cloudflare `tbate-scroll-demo` |

Details:
- For a website, `series.js` is rewritten with only the chosen chapters (each line built from its `chapter.js`).
- **Every folder gets its own entry in the zip.** Cloudflare's drag and drop skipped the chapter folder of a zip that only
  listed files, which caused "Chapter not ready".
- Images and MP3s are stored without extra compression.

### 9.2 The websites (Cloudflare Pages, free)

- **tbate-reader.pages.dev**: the full chapter for friends. No sign-in (your choice), and kept out of search engines.
- **tbate-scroll-demo.pages.dev**: the 19-panel demo for LinkedIn, with link-preview tags and a cover.
- **New project:** Workers & Pages → Create → Pages → **Upload assets** → drag the zip → Deploy.
- **New version:** open the project → **⋯** → **Create deployment** → drag the zip → Deploy. Then **Ctrl + F5** on the site.

### 9.3 The demo video and the cover

- **Cover** (`site/chapters/094-demo/cover.jpg`, 1200 × 627, not in git): `tools/reader/cover.html` is a template.
  Panel 79's background and characters are combined and cropped to (0, 0, 940, 1180) as `tempest.jpg`, then the page is
  rendered with Playwright and saved as JPEG at quality 90.
- **Video** (`dist/Storyteller-Demo-Video.mp4`: 56 s, 1080 × 1350, 30 fps, H.264 CRF 18 + AAC 192k, −14.8 LUFS, peak
  −1.6 dB):
  1. Serve the unzipped demo site on port 8803 under the name `tbate-scroll-demo.pages.dev` (Chromium's
     `--host-resolver-rules`). GSAP and the fonts are served from local copies.
  2. `node tools/reader/record_demo.js <dir>`: a 540 × 675 window at 2× density. Playwright's **fake clock** is stepped
     exactly 1/30 s per frame, so the animation is perfectly smooth however slow a screenshot is. The scroll path:
     the title card for 2.6 s, then about 110 units a second (slower on panels 79, 87, 92, 84), and the end card for 3.4 s.
     The HUD's sound button is hidden.
  3. `record_demo.js <dir> cues` notes the time each sound fires.
  4. `node tools/reader/render_demo_audio.js <dir>` renders the soundtrack: the music mix plus every effect at its
     moment, through the site's own `makeEffects` and chain, in an `OfflineAudioContext`. The music bed sits at 0.55 and
     dips to half under each effect.
  5. ffmpeg: `loudnorm=I=-14.5:TP=-3:LRA=11,alimiter=limit=0.84`, then the frames and the sound are put together.

  The music mix was built in NumPy from the loops (tension, climax, calm, with 1–2.5 s fades). **Never use ffmpeg
  `-stream_loop` on the MP3 loops**: it clicked. Join the decoded samples instead.

---

## 10. Reference: every setting of a scene

A scene in `chapter.js`:

```js
{ id: "panel_79", w: 940, h: 1538, length: 330, fit: "pan", enter: "zoom", exit: "fade",
  chars: { from: { scale: 1.06 }, to: { scale: 1 }, over: [0.05, 0.3] },
  shakes: [0.13, 0.3], flashes: [{ at: 0.12, color: "#d9ffee", strength: 0.85, hold: 0.04 }],
  sfx: [{ at: 0.12, sound: "gust" }, { at: 0.3, sound: "whoosh" }],
  fx: { ambient: "embers", tint: "wind", amount: 1.7,
    bursts: [{ type: "flare", tint: "wind", at: 0.13, from: [72, 30] }, { type: "ring", at: 0.14, from: [55, 80] }] } },
```

All moments (`at`, `shakes`, `over`, `out`, `hold`…) are **fractions of the scene, 0 to 1**.

| Setting | Values | Meaning |
|---|---|---|
| `id`, `w`, `h` | `"panel_79"`, pixels | the panel and its size (from chapter.json) |
| `length` | units (100 = one screen of scrolling) | how long the scene lasts |
| `fit` | `"pan"` or left out | `pan`: fill the width and pan down; otherwise the whole panel shows |
| `camera` | `{ from: {scale, x, y}, to: {…} }` | moves the whole panel; `x`/`y` in % of the panel |
| `origin` | `[x%, y%]` | the point the camera scales around |
| `bg`, `chars` | `{ from, to, over: [a, b] }` | move the background / characters separately (parallax); `over` squeezes it into part of the scene |
| `bubbles` | `[{ src, x, y, w, h, at, out, pop }]` | `src` = file name without `.webp`; position and size in panel pixels; `at` pop-in; `out` fade (default 0.8, ≥ 0.92 stays); `pop: false` plain fade-in for lettering on the art |
| `shakes` | `[0.13, 0.3]` | moments of a camera shake |
| `flashes` | `[{ at, color, strength, rise, hold, fall }]` | a full-screen flash; `hold` > 0 = a white-out |
| `sfx` | `[{ at, sound }]` | `whoosh` `swish` `crack` `grip` `flame` `clang` `skid` `tap` `thud` `glint` `shatter` `crash` `gust` + recorded `deflect` `parry` |
| `fx.ambient` | `"dust"`, `"embers"`, `"speed"` | ambient particles |
| `fx.tint` | `"paper"`, `"mana"`, `"ember"`, `"wind"` | their colour |
| `fx.amount` | 0.25 – 1.7 | how many |
| `fx.bursts` | `[{ type, at, from: [x%, y%], tint }]` | `splinters`, `sparks`, `ring`, `flare`, `shatter`; `sparks`/`flare` take a `tint` |
| `enter`, `exit` | `"cut"`, `"fade"`, `"zoom"` | transitions |
| `focus` | `[x%, y%]` | where a zoom exit dives in |

A chapter's `music`: `[{ theme: "tension", from: "panel_01", to: "panel_14" }, …, { theme: "calm", from: "panel_88" }]`
(the last stretch has no `to`; `take: 0` picks a take by hand).

`series.js` keys: `title`, `playlist`, `credit`, `chapters`, `themes`, `mix: { music: 0.65, dip: 0.5 }`,
`autoScroll: { pauses: 0.65 }`, `sounds: { deflect: { src, volume }, parry: { … } }`.

---

## 11. Reference: every script and command

| Script | What it's for | Run it like this |
|---|---|---|
| `tools/make-chapter/make_chapter.py` | CBZ → chapter zip | `python make_chapter.py --cbz-dir cbz --out chapters --chapters 1-5,94` |
| `tools/layer-splitter/split_layers.py` | images → layers (used by the maker) | `python split_layers.py images --out layers --join` |
| `tools/make-chapter/gpu_check.py` | is the graphics card used? (exit 0 / 3) | `python gpu_check.py` |
| `tools/make-chapter/Make_Chapter.ipynb` | the maker on Colab | Colab: Run all |
| `tools/make-chapter/Make_Chapters_Kaggle.ipynb` | the maker on Kaggle, 2 GPUs | Kaggle: Save & Run All |
| `tools/layer-splitter/Split_Manga_Layers.ipynb` | the splitter alone on Colab | Colab: Run all, upload images |
| `tools/pc/Setup.bat`, `Make Chapters.bat` | the maker on your Windows PC | double-click |
| `tools/build_notebooks.py` | rebuild the notebooks + the PC kit from the scripts | `python tools/build_notebooks.py` |
| `tools/director/draft_chapter.py` | chapter zip → first scene plan | `python tools/director/draft_chapter.py chapter_001.zip --out site/chapters/001/chapter.js --title "…"` |
| `tools/director/cut_chapter.py` | a demo cut of a directed chapter | see 6.3 |
| `tools/music/Make_Music.ipynb` | new music with MusicGen | Colab: Run all |
| `tools/music/make_loop.py` | a take → a seamless loop | `python make_loop.py in.mp3 out.mp3 2` |
| `tools/voices/make_voices.py` | voice lines with Kokoro (voices off) | `python make_voices.py` |
| `tools/reader/reader.py`, `Read Storyteller.bat` | the desktop reader | double-click, or `python3 tools/reader/reader.py` |
| `tools/reader/build_reader.py` | every zip to give out | see 9.1 |
| `tools/reader/record_demo.js`, `render_demo_audio.js` | the demo video and its sound | see 9.3 |
| `tools/reader/cover.html` | the link-preview cover | see 9.3 |
| `docs/images/banner.html` | the README banner | render with Playwright at 1280 × 400, 2× |

**What to run after changing something:**
- `split_layers.py`, `make_chapter.py` or `gpu_check.py` changed → `python tools/build_notebooks.py`, then commit the
  notebooks too.
- `site/index.html` or `series.js` changed → rebuild `--site`, the demo zip and `--reader-update`, and upload/send them.
- Keep Windows line endings (CRLF) in the `.bat` files and in `tools/reader/README.txt` and `tools/pc/README.txt`.

**What each part needs:**

| Part | Needs |
|---|---|
| The reader | a modern browser and internet (GSAP, fonts) |
| The desktop reader | Python 3.8+ (nothing else to install) |
| The chapter maker | Python 3.10+ (3.12 on the PC kit), PyTorch, `rembg[gpu]`, ONNX Runtime (GPU or DirectML), OpenCV, SciPy, NumPy, Pillow, pymatting, `simple-lama-inpainting` 0.1.2 (`--no-deps`), an NVIDIA graphics card for speed; models about 2.3 GB |
| The draft tool | Python 3; `node` for `--carry-over` |
| Music | a Colab T4 for MusicGen; NumPy + ffmpeg for `make_loop.py` |
| The demo video | Node, Playwright with Chromium, ffmpeg |

---

## 12. Problems already solved, and the rules that keep them solved

| Problem | Fix (do not undo) |
|---|---|
| `simple-lama-inpainting` pins Pillow < 10 | install it with `--no-deps` |
| its `utils` package has an empty `__init__` | import from `simple_lama_inpainting.utils.util` |
| joining a whole chapter used 6.7 GB in bubble detection | bubbles handled as small crops; `int16` maths |
| capping numba/Pillow versions pulled in an old rembg | no version caps; models made with `sessions_class[name](name, options, providers=…)` |
| ONNX Runtime on a T4 with CUDA 13 silently used the processor | start on the processor; `_move_to_gpu` tries `HEURISTIC` then `DEFAULT`, with fallback switched off |
| ONNX Runtime's memory pools starved LaMa | `kSameAsRequested` + arena shrinkage after every run; LaMa empties PyTorch's cache |
| eyes and white faces taken for bubbles | the letter-shape and neutral-ink rules (4.1) |
| "Image size exceeds WebP limit of 16383 pixels" and squashed cutouts in tall panels | `split_tall` (4.2); old zips remade automatically |
| a black page dropped as a "promo page" | the "closer than an empty page" rule (3, step 2) |
| Cloudflare showed "Chapter not ready" | website zips list every folder as its own entry |
| ScrollTrigger scenes broke on refresh | no `invalidateOnRefresh` |
| the pan fought GSAP's transforms | the pan lives on its own `.pan` wrapper |
| tall panels pinned to the top | `.zoom` centred by hand |
| music clicked at the loop point | loop points skip the MP3 encoder's silence; never `-stream_loop` in ffmpeg |
| climax drums buried the hits | the music bus that ducks under every effect |
