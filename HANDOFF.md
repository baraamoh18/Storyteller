# Project Handoff: AI-Driven Manhwa Scrollytelling Reader

> **Last updated 2026-11-04 (third session: chapter 94 directed, tall-panel fix).** Read **Section 0** first, then **Section 12 (next steps)** and **Section 13 (how to work)**.

---

## 0. Status at a glance

| Part | State |
|---|---|
| **Reader** (`site/`) | A multi-chapter **series reader**: chapter menu, scroll-scrubbed parallax scenes, particles, synthesised + recorded sound effects, themed music that crossfades. One chapter in it: **The Duel** (`chapters/duel`, 60 panels, the old partial cut of chapter 94). |
| **Chapter maker** | Done and **proven on the user's real Colab GPU**: `Make_Chapter.ipynb` (Colab), `Make_Chapters_Kaggle.ipynb` (Kaggle, 2× T4), PC kit for the user's **RTX 5050**. CBZ in → one `chapter_<id>.zip` (~15 MB) per chapter. |
| **Chapter 94, full** | The user's Colab run produced `chapter_094.zip` (70 pages → 92 panels, 2 tiny, 26 bubbles, 14.5 MB). **Not saved in this repo** (images stay out of git): it is in the user's Google Drive at `Storyteller/chapters/chapter_094.zip`. **Ask the user to upload it again** to direct it. |
| **Chapter 94** | **Approved by the user** (third session). `site/chapters/094/chapter.js` (90 scenes; images not in git: they come from `chapter_094.zip`). The old `duel` cut is deleted (in git history up to `45b9025`). The user has it in the PC reader zip. |
| **Kaggle** | First run (chapters 1–30) **failed 10 chapters** (WebP 16383 px limit) and squashed the cutouts of very tall "panels" (long black/fade stretches) in the rest. Fixed in `split_layers.find_panels` → `split_tall` (commit `b791f39`); the user was sent the new notebook and told to rerun with the old output as input: 28 chapters are remade (old zips with panels > 4.5 strip widths count as not done), 9 and 21 are kept. Their uploads of 2–4 are superseded. |
| **PC kit** | Sent (`dist/Storyteller-PC-Tools.zip`), not yet run by the user. Untested on Windows. |
| **Music library** | 8 loops in `site/music` (calm, tension, battle ×2, battle_dark ×2, climax ×2). `tools/music/Make_Music.ipynb` (10 more: calm_2, tension_2, sad, eerie, triumph, warm) was sent; **not yet run** by the user. |
| **Voices** | **Off** at the user's request. |
| **Repo visibility** | `baraamoh18/Storyteller` was found to be **public**; the user was told to make it private. Check before adding more art. |

---

## 1. The project and the user

* **Goal:** turn the manhwa *The Beginning After the End* (TBATE) into an animated "scrollytelling" reader: scrolling plays each
  chapter like a film (camera moves, 2.5D parallax, zoom-through cuts, particles, sound), scrolling back rewinds it.
* **Use:** a **personal project, not going public.** Free tools with non-commercial licences (MusicGen) are fine. Chapter images come
  from CBZ files the user downloaded themselves; **do not build a scraper for manhwa sites**.
* **The user (Baraa):**
  * wants plain, non-technical language, one step at a time, exact click paths, and ready-to-run files sent as attachments;
  * wants a **plan before big work**, and **approves every chapter** before it joins the reader;
  * wants it **free and budget-friendly** (no paid APIs; the AI in a Claude Code session is the "director");
  * wants **accuracy over speed**: **keep both cutout models** (they explicitly rejected a single-model fast mode);
  * works on **Windows**, local folder `D:\Work\StoryTelling website\`; has **Google Colab Pro**, a **Kaggle** account (phone
    verified now) and a PC with an **NVIDIA RTX 5050** (8 GB, Blackwell);
  * stores chapters in **Google Drive** `Storyteller/cbz/` (all ~280 CBZ files, 2.8 GB; ~10 MB each) and on their PC.
* **Decisions already made** (do not re-ask): file chapter numbers are the series numbers (`..._94_-_Chapter_94.cbz` = chapter 94);
  chapter images stay **out of the GitHub project**; title / credits / promo pages are dropped automatically and shown to the user;
  after chapter 94 the series starts from **Episode 1**; music is **instrumental only**, by theme; voices stay off for now.

## 2. Reference style

Inspired by "The Notturno Experience" interactive graphic novel: neo-noir, ink black and paper white with one flat red accent,
halftone dots, bold comic type (Bangers, Archivo Narrow, IBM Plex Mono). Scroll-scrubbed timelines (no autoplay), zoom-through
transitions into a focal point, parallax between layers.

---

## 3. Where everything lives

* **Repo:** `github.com/baraamoh18/Storyteller` (private now; default branch `claude/project-thread-6clyex`). **Third session's branch:** `claude/new-session-4xc7k0` (no PR yet). Older branch: `claude/new-session-em88ar` →
  **pull request [baraamoh18/Storyteller#2](https://github.com/baraamoh18/Storyteller/pull/2)** (created by the user from the UI;
  pushing to the branch updates it). The PR is not being watched (the user was asked, no answer).
* **Live preview** (private artifact): https://claude.ai/artifact/G6A8f5qCYfSL8KYwcFWKxH. Published from a copy of `site/index.html`
  with the `<!doctype>`, `<html>`, `<head>`, `<body>` lines stripped (the host adds its own), `root = site/`, and the other files
  passed in `files` (`series.js`, `chapters/duel/*`, `music/*`, `sfx/*`). An artifact version holds **at most 511 files, 255 per
  publish**; one chapter is ~140 files, so the preview fits ~3 chapters. Plan: per-chapter previews for approval; the full series
  reader runs on the user's PC (Section 12).
* **The user's storage:** Google Drive `Storyteller/cbz` (CBZ in), `Storyteller/chapters` (zips out), `Storyteller/music_takes`
  (music notebook output); Kaggle dataset `tbate-cbz` (some or all CBZ files) and notebook outputs; PC kit folder with a `finished/`
  folder.

```
HANDOFF.md                            this file (project_handoff_document.md is the very first, obsolete handoff)
series/cast.md                        the user's cast list: ~95 characters with looks, magic colours, first episodes
site/                                 the reader (see site/README.md)
  index.html                          engine + chapter menu; no chapter data inside
  series.js                           title, playlist link, chapter list, music themes (takes + volumes), recorded sounds
  chapters/duel/chapter.js, *.webp    The Duel: 60 panels (old numbering), its layers and bubbles
  music/<theme>_<n>.mp3               seamless loops: calm_1, tension_1, battle_1-2, battle_dark_1-2, climax_1-2
  sfx/deflect.mp3, sfx/parry.mp3      the user's Sekiro recordings, processed (Section 9)
tools/
  build_notebooks.py                  rebuilds the notebooks + the PC kit zip from the scripts (run after every script change)
  layer-splitter/                     split_layers.py (the AI splitter) + Split_Manga_Layers.ipynb (older one-off notebook)
  make-chapter/                       make_chapter.py, gpu_check.py, Make_Chapter.ipynb (Colab), Make_Chapters_Kaggle.ipynb, README
  pc/                                 Setup.bat, Make Chapters.bat, README.txt (Windows kit; CRLF line endings matter)
  director/                           draft_chapter.py (first-draft chapter.js, carry-over), README
  music/                              Make_Music.ipynb (MusicGen on Colab), make_loop.py (seamless loops)
  voices/                             make_voices.py (Kokoro; voices are off)
dist/Storyteller-PC-Tools.zip         built by build_notebooks.py; not committed (.gitignore)
```

---

## 4. The pipeline

```
CBZ (user's downloader) ─► chapter maker (Colab / Kaggle / PC GPU) ─► chapter_<id>.zip (~15 MB)
     ─► user uploads it to a Claude session ─► draft_chapter.py ─► AI directs chapter.js (+ music themes)
     ─► preview artifact ─► user approves / notes ─► chapter added to series.js
```
Processing only has to stay **ahead of directing**; directing (AI + user approval) is the real bottleneck.

---

## 5. The splitter (`tools/layer-splitter/split_layers.py`)

Per chapter strip (all pages joined, natural file order):
1. **Panels:** rows of the most common border colour are gutters.
2. **Bubbles:** a near-white area with holes; holes must be **black ink** (> 30% of hole pixels darker than 100), lettering 2–45% of
   the filled shape, roundish, **at least 2 letter-sized dark shapes** inside and **≤ 5% colourful hole pixels** (added this session:
   on chapter 94 it removed 4 eyes and Sylvie's white fox face, kept all 26 real bubbles, even "NO."). Saved grown 15 px.
3. **Characters:** `birefnet-general` + `birefnet-hrsod` (rembg), each on the panel and its mirror (averaged), combined with max;
   **ViTMatte** refines edges (≥ 250 → 255; pixels the models scored ≥ 200 keep their value); `pymatting` unmixes edge colours.
4. **Background:** LaMa fills where characters and bubbles were (up to 2048 px on the GPU, halving on out-of-memory).
5. Writes `original.png`, `background.png`, `characters.png` per panel, `bubbles/`, `layers.json`.

**Providers:** `Models` picks **CUDA**, else **DirectML** (Windows), else the CPU; `onnxruntime.preload_dlls()` is called when present
(finds torch's CUDA DLLs on Windows). `Models.timings` records seconds per step (each cutout model, edge refinement, edge colours,
background fill); `Models.cutouts_on_gpu` says where the cutouts run.

**Speed:** about 8–9 s per panel on a T4 (6 AI passes); a ~90-panel chapter ≈ 15 min. The whole series (~280 chapters) ≈ 70 T4-hours.

**Model comparison** (5 panels): `birefnet-general` most reliable; `birefnet-hrsod` clean, adds 0.1–0.3% edge pixels (the partner);
`birefnet-general-lite` added 5–7% wrong background (dropped); `birefnet-massive`, `birefnet-dis`, `isnet-anime` miss characters;
`bria-rmbg` not tried (licence). Flip averaging removes wrongly included glows (up to 2.5%); ViTMatte removes ghost patches.

**Known limits:** sound-effect lettering stays in the character layer (often useful); fills are a bit smudgy behind characters;
undetected bubbles (e.g. chapter 94's "HE'S…") stay in the character layer; very unusual layouts without gutters are untested.

**Problems already solved (do not reintroduce):**
| Problem | Fix |
|---|---|
| `simple-lama-inpainting` pins Pillow < 10 (fails on Python 3.13) | install with `--no-deps` |
| `simple_lama_inpainting.utils` has an empty `__init__` | import from `simple_lama_inpainting.utils.util` |
| joined strips used 6.7 GB for detection | bubbles as small crops, int16 |
| capping numba/Pillow pulled an old rembg whose `new_session()` rejects options (14 GB, Colab killed) | no caps; sessions built with `sessions_class[name](name, options, providers=...)` |
| ORT GPU on a **T4** with CUDA 13 fails the default cuDNN search and silently used the CPU | start on CPU, `_move_to_gpu` tries `HEURISTIC` then `DEFAULT` with a warm-up |
| three ORT sessions kept their GPU memory pools, LaMa ran out | `kSameAsRequested` + `memory.enable_memory_arena_shrinkage`; LaMa empties torch's cache |
| eyes / white faces cut out as "bubbles" | the letter-shape + colour rule above |

---

## 6. The chapter maker (`tools/make-chapter/`)

`make_chapter.py --cbz-dir … --out … --chapters 1-5,94 [--skip '{"94":[0,69]}'] [--redo] [--shard K/N] [--done-dir D] [--max-hours H]`
1. Finds CBZ files by number (also in subfolders): `chapter[ _-]*N` or the last number; ids are 3-digit (`094`, `094-5` for 94.5).
2. Drops non-story pages: the first two and last two pages are compared (16×32 difference hash, ≤ 110 of 512 bits) with fingerprints
   of chapter 94's **series title page** (000) and **creators' promo page** (069); the closest story page differs by 156 bits.
3. Joins pages (other widths are scaled to the most common), runs the splitter.
4. WebP: backgrounds q80, characters q85, bubbles q90, `method=6`. Each bubble gets a panel (the one it sits in, else the nearest,
   **never a tiny one**) and in-panel `x, y, w, h`; `between_panels`, `suspect` (small) flags. Panels under 120 px on a side or
   40,000 px² are **tiny** (crumbs; the director skips them).
5. Zip built locally, moved into `--out` whole (`.part` → final), so a disconnect never leaves a "finished" broken zip.
   Chapters with a zip in `--out` or any `--done-dir` are skipped. `--shard K/N` takes every Nth chapter **of the whole batch**
   (stable across runs). `--max-hours` stops starting chapters after that long (and if the slowest chapter so far would not fit).
   Prints the time per panel per step and stores it in `chapter.json` under `seconds`.

**The zip** `<id>/`: `panel_XX_background.webp`, `panel_XX_characters.webp`, `bubble_XX.webp`, `chapter.json`
(number, source, pages, dropped pages, strip size, panels, bubbles, seconds), `sheets/pages.jpg` (dropped pages crossed out),
`sheets/panels_XX-YY.jpg` (five original panels per sheet, numbered, TINY marked), `sheets/bubbles.jpg`.

**Where it runs**
| | How | Notes |
|---|---|---|
| Colab | `Make_Chapter.ipynb`: T4 + High-RAM, `CHAPTERS` in Step 1, Run all, allow Drive | reads Drive `Storyteller/cbz`, writes `Storyteller/chapters`, downloads the zips; tab must stay open |
| Kaggle | `Make_Chapters_Kaggle.ipynb`: GPU **T4 ×2**, Internet **On** (needs a verified phone; the error `kernelSessions.enableInternet was denied` means not verified), dataset as Input; **Save Version → Save & Run All** | two `make_chapter.py` processes (`CUDA_VISIBLE_DEVICES=0/1`, `--shard 1/2`, `2/2`), `MAX_HOURS = 11` (Kaggle stops at 12 h), progress every 5 min, logs `log_gpu0/1.txt`; outputs download from the **version's Output tab after the run finishes**; next run: add the previous version's output as an input (→ `--done-dir`) |
| PC (RTX 5050) | `dist/Storyteller-PC-Tools.zip` → `Setup.bat` once, then `Make Chapters.bat` | Python **3.12**, torch from the **cu128** index (Blackwell needs CUDA 12.8+), `rembg[gpu]`; models in the kit folder (`U2NET_HOME`, `TORCH_HOME`, `HF_HOME`); remembers the CBZ folder; output `finished/` |

**Self-fixing GPU check** (`gpu_check.py`, exit 3 = cutouts on the CPU): Kaggle then installs `onnxruntime-gpu==1.22.0`
(the CUDA 12 build); the PC setup tries that, then swaps to `onnxruntime-directml`.

**Delivery to the AI:** the user uploads zips into the session, 2–3 per message. Proposed but **not approved yet**: Colab/Kaggle push
bundles (~25 MB) to a private `Storyteller-data` repo with a fine-grained token in Colab/Kaggle Secrets, so the AI fetches them.

---

## 7. Directing (`tools/director/`)

* `draft_chapter.py ZIP --out site/chapters/<id>/chapter.js --title "…" [--carry-over OLD/chapter.js --report]` writes the
  first draft: every non-tiny panel, `fit: "pan"` when taller than 1.45× its width, scroll length from the shape, a gentle push-in,
  dust, bubbles in reading order with staggered `at`, suspect bubbles as `// check` comments, music one `calm` stretch.
* `--carry-over` pairs new and old panels by size (±3 px, longest common run), pairs leftovers in gaps by position (marked
  `resized … check`), keeps bubble timings within 12 px, renames bubbles, and moves music stretches to the new panel ids.
* The AI then directs: camera, layers, impacts, particles, sfx, transitions and music themes, using the cast list for speakers and
  magic colours. Then checks in Playwright (Section 13) and publishes a preview for approval.
* **To write:** the director playbook (a repo skill) capturing the house style below, so every session directs the same way.
  House style so far: zoom-through on match cuts and big focal moments; `pan` for tall panels; shakes + flash + burst + sfx on
  impacts; `deflect` for blades turned aside, `parry` for heavy clashes; mana embers in the fighter's colour; bubbles pop where they
  sit, lettering drawn on art uses `pop: false`; music theme per story stretch; light mode for dialogue chapters.

---

## 8. The reader (`site/`, details in `site/README.md`)

* GSAP 3.12.5 + ScrollTrigger from cdnjs; one pinned stage; one timeline, **1 unit = 1vh of scroll**, `scrub: 0.7`.
* `series.js` (`window.SERIES`) is loaded first; the address `index.html#<id>` picks the chapter (else the first); its
  `chapters/<id>/chapter.js` calls `registerChapter({ id, title, number, music, scenes })`, then `boot()` builds it.
  A hash change reloads the page. A missing chapter shows "Chapter not ready"; the end card links to the next chapter.
* **Per panel:** `.scene` → `.zoom` (enter/exit zoom; centred by hand) → `.shake` → `.pan` (tall-panel pan, CSS `translate`) →
  `.rig` (camera) → `.frame` (clip) → `img.bg`, `canvas.fx-mid`, `img.chars`; bubbles in `.rig` (may overflow), nudged on screen
  (56 px clear at the top for the Sound button).
* **Loading:** images use `data-src`, loaded 1 panel behind / 3 ahead; particle canvases are sized only while visible.
* **Scene settings:** `length`, `fit: "pan"`, `camera`/`origin`, `bg`/`chars` (`over: [a, b]`), `bubbles` (`src, x, y, w, h, at`,
  `pop: false`), `shakes`, `flashes` (`at, color, strength`, `rise`, `hold`, `fall` — `hold` gives a white-out), `sfx` (`at, sound`),
  `fx` (`ambient` dust/embers/speed, `tint` paper/mana/ember, `amount`, `bursts` splinters/sparks/ring/flare/**shatter** with `at`,
  `from`), `enter`/`exit` cut/fade/zoom with `focus`.
* **Bursts** are deterministic functions of scroll time (seeded), so they rewind; `shatter` grows jagged glass cracks from a point,
  with branches and shards, and lets them linger.
* **Reduced motion:** a plain column, no animation or sound (the playlist link stays).
* **Bugs already fixed (do not reintroduce):** no `invalidateOnRefresh: true` (it showed bubbles early); GSAP writes `translate: none`
  on transformed elements, so the pan lives on its own `.pan` wrapper; a centring grid pinned tall panels to the top, so `.zoom` is
  centred with absolute position and negative margins.

---

## 9. Sound

* Off until **Play with sound**. Effects fire only when scrolling forward past their moment (not on jumps of > 25 units).
* **Synthesised effects** (`makeEffects(ctx, out)`, also usable with an `OfflineAudioContext` for listening tests): `whoosh`,
  `swish`, `crack`, `grip`, `flame`, `clang`, `skid`, `tap`, `thud`, `glint`, `shatter`, `crash`, `gust`.
* **Recorded effects** (`SERIES.sounds`, `site/sfx/`): the user's **Sekiro** `deflect` and `parry` recordings replaced the CLANK
  (the user rejected the synthesised parry/block/tink, now removed). They were far too loud (−4 to −6 LUFS, peaks +3 dBFS) and
  started late: trimmed (0.21 / 0.47 s of silence), high shelf −5 / −3 dB above ~4.5 kHz, about 4 dB under the other sword effects,
  **pitched ~2 semitones down** (`asetrate` ×0.89, the user's choice). Played with ±2% pitch variation; a missing file falls back to
  `clang`. Duel: `deflect` on panels 11, 32, 42, 46; `parry` on 9, 17, 52, 60.
* **Chain:** effects bus 0.65 → limiter (threshold −10, ratio 20, attack 1 ms) → tanh soft clip; music tracks into the limiter.
  (Chrome's compressor is not a brick wall: the old `clang` measurably clipped.)
* **Music:** a chapter names a **theme** per stretch (`music: [{ theme, from, to, take? }]`); `SERIES.themes` lists takes with
  volumes; a reused theme plays its next take; neighbours crossfade (in over 40 units, out over 60); the MP3 encoder padding is
  skipped (`loopStart`/`loopEnd`). Library: `calm_1` (harp, 0.5), `tension_1` (music box + slow beat, 0.4), `battle_1` (0.53),
  `battle_2` (0.63), `battle_dark_1` (0.58), `battle_dark_2` (0.5), `climax_1` (0.75), `climax_2` (0.56).
  Duel: tension 1–5, battle 6–22, battle_dark 23–39, battle 40–48, climax 49–60.
* **Making music:** `Make_Music.ipynb` (MusicGen large on Colab, 30 s, fixed gain — the old `loudnorm` broke loop seams) →
  `make_loop.py in.mp3 out.mp3 TAIL_SECONDS` (skips the first 1.6 s, drops a dead tail, beat-aligned 1 s equal-power crossfade,
  fixed gain to ~−16 LUFS). The AI cannot listen: choose takes by measurement (steady loudness and beat, no dropouts) and say so.
* **The user's taste:** Academy = warm/light fantasy or music box; fights = cinematic orchestral, choir and drums for desperate
  turns; Relictombs = dark synthwave/post-rock; plus the fans' **reading playlist** (Spotify
  https://open.spotify.com/playlist/7dbe38KmEgww6qeiyGGWHe: dark electronic / trap alt-pop — Egzod, Silent Child, UNDREAM, PatrickReza,
  NUVILICES…). Spotify audio cannot be used; the title card has a "Reading playlist ↗" link.
* **Voices: off.** `tools/voices/make_voices.py` (kokoro-onnx, CPU) still works; old playback code is in commit `77414a1`. Arthur
  should sound deep and calm (onyx-based blends); the user wants adjustments before voices return.

---

## 10. Chapter 94 (the Geist duel)

* **CBZ:** `The_Beginning_After_the_End_94_-_Chapter_94.cbz`, 70 pages × 940 px (page 000 = series title, 069 = promo; both dropped).
  Strip 940 × 125,394 → **92 panels** (90 and 91 tiny), **26 bubbles**, all real.
* **The old "duel" chapter** (`site/chapters/duel`) came from slices 8–53 of a different download: it started mid-panel and stopped
  before the finale. **New panel N = old panel N − 9 for 10–69** (old 1 was cut in half; new 10 is complete, 940×721). New 1–9 are the
  opening, 70–92 the finale.
* **Beats:** opening — Arthur enters the arena, the stands (students, a black-haired and a blonde girl with Sylvie in her white fox form beside them; names to confirm against the cast list), Geist offers a choice of
  fighting method. Duel (old plan). Finale — "You think this is enough?!", "No." "But this might be.", the green-white **TEMPEST** wind
  blade, the floor **cracking like glass** (drawn cracks are in the character layer), "S-stop!", **CRASH** (tall 940×3828 panel 87),
  **THUD**, the blade stabbed into the floor beside Geist's neck, "Thank you for your guidance." (final panel 92).
* **Bubbles** (new ids; speakers to confirm by eye):

| Bubble | Panel | Text | | Bubble | Panel | Text |
|---|---|---|---|---|---|---|
| 01 | 05 | QUITE A NICE WEAPON YOU'VE GOT THERE. | | 14 | 33 | IS THERE REALLY A NEED FOR ME TO ATTACK… |
| 02 | 06 | SINCE YOU'RE AN AUGMENTER | | 15 | 49 | THAT DOESN'T LOOK LIKE A DEMONSTRATION. / SHOULD WE GET THE STUDENT COUNCIL? (wall art: `pop: false`) |
| 03 | 06 | I SUPPOSE IT'S ONLY FAIR TO LET YOU CHOOSE WHICH METHOD YOU'D LIKE ME TO USE TO FIGHT. | | 16 | 57 | THIS BRAT GOT FASTER! |
| 04 | 07 | IT DOESN'T MATTER. | | 17 | 58 | EVEN RATS BECOME DEADLY WHEN CORNERED, |
| 05 | 09 | ARROGANT BRAT! | | 18 | 58 | PROFESSOR. |
| 06 | 09 | I INSIST. | | 19 | 63 | ARTHUR IS PUSHING PROFESSOR GEIST BACK. |
| 07 | 10 | PLEASE USE WHATEVER YOU'RE MOST CONFIDENT IN. | | 20 | 65 | ON A TOTALLY DIFFERENT LEVEL. |
| 08 | 11 | VERY WELL. | | 21 | 68 | IT'S TIME TO END THIS. |
| 09 | 15 | I'LL BE SURE TO GO EASY ON YOU. | | 22 | 74 | YOU THINK THIS IS ENOUGH?! |
| 10 | 22 | GOING EASY, HUH? | | 23 | 75 | NO. |
| 11 | 28 | HE'S NOT USING ANY SPELLS—JUST STRENGTHENING HIS BODY AND SWORD WITH MANA. | | 24 | 76 | BUT THIS MIGHT BE. |
| 12 | 30 | WHO DOES HE TAKE ME FOR?! | | 25 | 86 | S-STOP! |
| 13 | 31 | I'M SURE THE DISCIPLINARY COMMITTEE ISN'T MADE ONLY OF RATS WHO KEEP DODGING AND RUNNING AWAY! | | 26 | 92 | THANK YOU FOR YOUR GUIDANCE. |

* **Draft test (done here on identical data):** `draft_chapter.py … --carry-over site/chapters/duel/chapter.js --report` carries all
  60 old scenes onto 10–69 (58 identical, 2 resized: new 10 (from old 1, now includes bubble 07) and new 34 (from old 25, "F---!"
  sits at a new height)). 30 new panels to direct: 1–9, 70–89, 92. New panel 10 inherits `enter: "cut"` from the old first scene:
  change it.
* **Plan for the finale:** TEMPEST with `gust` and green-white wind tint; `shatter` burst + `shatter` sound on the glass-crack panels;
  CRASH with `crash`, a held white-out flash (`hold`), shake; THUD with `thud`; the final stab and "Thank you for your guidance." calm
  after the storm (music: climax fading toward tension/calm). The effects were tested on panel 87 in a scratch copy.
* When approved: chapter id `094`, title "The Duel", number 94 → `site/chapters/094/` and one line in `series.js`; then retire `duel`.

---

## 11. Cast and story

`series/cast.md` (the user's): ~95 characters across the series with "also called", look, magic and colour, role, personality and
first episode — use it to name speakers and pick particle/flash colours. In chapter 94: **Arthur Leywin** (long red hair, Disciplinary
Committee uniform, blue mana, green-white wind at the end) and **Professor Geist** (spiky brown hair, white headband, glasses, scar;
blue-flame sword, red-orange aura), plus Sylvie (white fox form) and students in the stands (who exactly: confirm with the cast list or the user).

---

## 12. Next steps (in order)

1. ~~**Direct chapter 94**~~ (done, see Section 0; next: the user's notes, then retire `duel`). Was: ask for `chapter_094.zip` (Drive `Storyteller/chapters`), unpack it in the scratchpad, run the draft tool
   with `--carry-over site/chapters/duel/chapter.js`, direct the 30 new panels, check panels 10 and 34, test in Playwright, publish
   the preview, get the user's approval or notes. Copy the images into `site/chapters/094/` for previews but **do not commit them**
   (add `site/chapters/*/*.webp` to `.gitignore`, keeping the tracked duel files until `duel` is retired).
2. **Write the director playbook** (a repo skill) while doing step 1, so later sessions direct consistently.
3. **Kaggle results:** ask whether the first run finished; if it failed, get a screenshot of the log's last lines. Then the user
   uploads chapters 1–5 for the first series batch.
4. **PC kit:** when the user runs `Setup.bat`, fix whatever the first Windows run shows (screenshots).
5. **Music library:** the user runs `Make_Music.ipynb`; loop the takes with `make_loop.py`, add them to `SERIES.themes`.
6. ~~**Reading on the PC**~~ done in the third session: `tools/reader/` (see `site/README.md`, "On the user's PC"). Sent the user
   `dist/Storyteller-Reader.zip` with chapter 94; tested here with Playwright (PC + phone address, pack import), not yet on
   Windows. Each approved chapter: `build_reader.py --pack <id>` and send the pack (the user drops it into `new chapters`).
6b. **Website for friends:** the user chose Cloudflare Pages, public, **no sign-in** (they declined Cloudflare Access; they were
   told about the copyright risk). `build_reader.py --site` → `dist/Storyteller-Site.zip`, uploaded by the user (drag and drop);
   noindex headers + robots.txt. The Cloudflare docs host is blocked here, so the click path given was from memory.
6c. **LinkedIn demo** (third session): public demo cut `site/chapters/094-demo` (19 panels, made with
   `tools/director/cut_chapter.py`), credit line in `SERIES.credit`, `build_reader.py --site --chapters 094-demo --public
   https://tbate-scroll-demo.pages.dev --cover site/chapters/094-demo/cover.jpg --out Storyteller-Demo.zip` (preview tags; no
   robots block, LinkedIn's crawler obeys robots.txt). Video: `tools/reader/record_demo.js` (Playwright, fake clock, 30 fps,
   1080x1350) + music mixed in numpy from the site loops (tension 0-14.9 s, climax from 12.9 s, calm from 46.4 s), loudnorm
   -14 LUFS. ffmpeg's `-stream_loop` on the MP3 loops made a click: loop the decoded samples instead.
   Sound effects (the user asked for them): `record_demo.js <dir> cues` logs when each fires, `render_demo_audio.js` renders
   music + effects in an OfflineAudioContext with the site's makeEffects and chain; music bed 0.55, dipping to half under each
   effect (at the site's own balance the climax music buried most effects under the limiter: worth checking on the site too).
7. **Optional, needs the user's yes:** automatic delivery through a private `Storyteller-data` repo.
8. **Later:** voices; dialogue chapters in "light" directing mode.

---

## 13. Instructions for the next AI session

**Working with the user**
* Plain language, one step at a time, exact click paths; send notebooks/kits as attachments.
* Before a big piece of work, give a plan and wait for approval.
* Ask the user to check which notebook copy they run (they sometimes reopen old copies from Drive).
* You cannot listen to audio: measure (loudness, spectrum, clipping) and send short MP3s for the user to judge.
* When the user reports an error from Colab/Kaggle/Windows, reproduce or simulate it here first and test the fix.

**Keep files in sync**
* After editing `split_layers.py`, `make_chapter.py` or `gpu_check.py`: `python tools/build_notebooks.py` (rebuilds both
  chapter notebooks, refreshes the old splitter notebook's cell, rebuilds `dist/Storyteller-PC-Tools.zip`). Commit the notebooks.
* `.bat` files must keep **CRLF** line endings, carets inside quotes print literally, and `%~dp0` ends with a backslash.

**This cloud environment**
* No GPU; **blocked:** Hugging Face, cdnjs, download.pytorch.org, Spotify, Pixabay, freesound, archive.org. **Reachable:** GitHub,
  PyPI, npm. torch is not installable here, so test the chapter maker with **stand-in models** (a class with `character_alpha`,
  `character_colours`, `fill_background`, `timings`) — scripts for this were in the scratchpad (`stub_run.py`, `opt_run.py`).
* **Site tests:** serve `site/` with `python3 -m http.server`, drive it with the preinstalled Playwright, route the cdnjs GSAP URLs to
  a local copy (`npm pack gsap@3.12.5`), abort Google Fonts. To stop the server use `pkill -f "http.serve[r] 8765"` (a plain pattern
  kills the shell running it).
* **Sound tests:** `makeEffects(new OfflineAudioContext(...), node)` in the page renders effects to WAV for analysis.
* Never `rm` with a relative glob after `cd` in the same command (the safety check blocks it); write tests into fresh folders.
* Commit and push to `claude/new-session-em88ar` after each change (it updates PR #2). Republish the preview by publishing the same
  scratch file path, or by passing the artifact `url` from a new session (read it first).

---

## 13b. Third session (notes)

* Reader: `wind` particle tint (green-white, Arthur's TEMPEST), `tint` on `sparks`/`flare` bursts, per-bubble `out` (fade moment; ≥ 0.92 keeps it): a bubble low on a tall `pan` panel otherwise fades at 0.8 before the camera reaches it.
* Bubbles the maker places outside their panel (`between_panels`, y < 0 or y > h) on `pan` panels need moving into the panel by hand (094: bubble_24, bubble_26).
* Chapter maker: a plain page (all black, a fade) is no longer taken for the title/promo page (it is near every fingerprint); dropped pages still need a glance on `sheets/pages.jpg` (Kaggle's chapter 22 dropped page 000 as "promo": check when it comes in).
* Test helpers for tall panels lived in the scratchpad (rebuild a strip from a zip's background + characters layers, run `find_panels`).
* Still to do from step 2: the director playbook skill.

## 14. Second session's commits (oldest first)

| Commit | What |
|---|---|
| `687ea87` | merge the earlier work into `claude/new-session-em88ar` |
| `df47df6` | panels 11–60, all bubbles, voices off, music zones, pan fixes |
| `5d53137` | reading playlist button, playlist-style music prompts |
| `8f3742f` | duel music: five loops crossfading by story section |
| `1547282` | multi-chapter series reader, music themes |
| `6534e1d` | the user's cast list |
| `200d2c2` | Make_Chapter notebook; bubble rule against eyes and faces |
| `74e35f3` | music notebook for the theme library |
| `27cfbec` | draft tool with carry-over |
| `bb528c7` | shatter burst, held flashes, shatter/crash/gust sounds |
| `f3db37f`, `66e88b3`, `a1848e0` | Sekiro-style parry → the user's recordings → lower pitch |
| `b7cc967` | find CBZ files in subfolders |
| `43d26c6` | timers, `--shard`, `--done-dir`, `--max-hours`, DirectML |
| `e14da16` | Kaggle notebook and PC kit |
