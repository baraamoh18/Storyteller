# Project Handoff: AI-Driven Manhwa Scrollytelling Reader

> **Last updated 2026-11-05 (end of the third session).** Read **Section 0** first, then **Section 13 (next steps)** and
> **Section 14 (how to work)**. `project_handoff_document.md` is the very first, obsolete handoff.

---

## 0. Status at a glance

| Part | State |
|---|---|
| **Reader** (`site/`) | Multi-chapter series reader: chapter menu, scroll-scrubbed parallax scenes, particles, synthesised + recorded sound effects, themed music with crossfades and **ducking under effects**, **auto-scroll** with a speed slider that slows for bubbles and big moments, a **credit line**, and on the PC a "Read on your phone" QR card. |
| **Chapter 94 "The Duel"** | **Directed in full and approved by the user.** `site/chapters/094/chapter.js` (90 scenes). Images are **not in git**: they come from `chapter_094.zip` (user's Drive `Storyteller/chapters/`). The old 60-panel `duel` cut is deleted (commit `cab2a0a`; still in history). |
| **Public demo** | `site/chapters/094-demo/chapter.js`: 19 panels cut from 094 (opening + finale) for LinkedIn. |
| **Websites (Cloudflare Pages, uploaded by the user, both working)** | **tbate-reader.pages.dev**: full chapter for friends, no sign-in (user's choice), kept out of search engines. **tbate-scroll-demo.pages.dev**: the 19-panel demo for LinkedIn, with link-preview tags and cover. The user confirmed both work with the latest zips (auto-scroll, shorter pauses, sound rebalance). |
| **PC reader** | `tools/reader/`: `Read Storyteller.bat` + `reader.py` (Python web server for PC and phone over Wi-Fi). Sent as `Storyteller-Reader.zip` + later `reader-update.zip`. Tested here only (Playwright); **the user has not reported a Windows run yet.** |
| **LinkedIn** | Sent: 56 s portrait video (music + sound effects), the demo site, a post draft (Section 11). Unknown whether the user has posted. |
| **Chapter maker** | Colab, Kaggle (2× T4) and PC kit, proven on real GPUs. **Fixed this session:** very tall "panels" (long black/fade stretches) are split up (they broke WebP and squashed cutouts), and plain black pages are no longer dropped as title/promo pages. |
| **Kaggle** | First run (chapters 1–30) had 10 failures (WebP limit) and squashed cutouts elsewhere. The user got the fixed notebook and was told to rerun with the first run's output as input: **28 chapters remade automatically**, 9 and 21 kept. **Rerun results not reported yet.** Their uploads of chapters 2–4 are superseded. |
| **PC chapter kit** | Sent (`dist/Storyteller-PC-Tools.zip`), not yet run by the user. Untested on Windows. |
| **Music library** | 8 loops in `site/music`. `tools/music/Make_Music.ipynb` (10 more themes) was sent long ago; **not yet run**. |
| **Voices** | **Off** at the user's request. |
| **Repo** | `baraamoh18/Storyteller` is **private** (checked this session). Chapter images are kept out of git. |

---

## 1. The project and the user

* **Goal:** turn the manhwa *The Beginning After the End* (TBATE) into an animated "scrollytelling" reader: scrolling plays each
  chapter like a film (camera moves, 2.5D parallax, zoom-through cuts, particles, sound), scrolling back rewinds it.
* **Use:** a personal fan project. The user now **shares it with friends** (full chapter, link only) and **shows a short demo on
  LinkedIn** as an AI side project. They were told twice about the copyright risk; the demo is an excerpt with credits; the
  friends' site is unlisted. Do not post the full chapter publicly, and do not build a scraper for manhwa sites (CBZ files are
  downloaded by the user).
* **The user (Baraa):**
  * wants plain, non-technical language, one step at a time, exact click paths, and ready-to-run files sent as attachments;
  * wants a **plan before big work** and **approves every chapter** before it joins the reader;
  * wants it **free and budget-friendly** (no paid APIs; the AI in a Claude Code session is the "director");
  * wants **accuracy over speed**: **keep both cutout models** (they rejected a single-model fast mode);
  * works on **Windows** (`D:\Work\StoryTelling website\`), has **Google Colab Pro**, **Kaggle** (phone verified), an **RTX 5050**
    PC, a **Cloudflare** account (their email), Chrome; writes short messages with typos ("chapter 49 approved" meant 94).
  * stores CBZ files in **Google Drive** `Storyteller/cbz/` (~280 files, 2.8 GB) and in the Kaggle dataset `tbate-cbz`.
* **Decisions already made** (do not re-ask): file chapter numbers are series numbers; images stay out of GitHub; title / promo
  pages are dropped automatically; after chapter 94 the series starts from **Episode 1**; music is instrumental, by theme; voices
  off; the friends' website has **no sign-in**; the speed control is a **slider**; auto-scroll also slows at big moments.

## 2. Reference style

Inspired by "The Notturno Experience": neo-noir, ink black (`#0b0a0d`) and paper white (`#f1ece4`) with one flat red (`#e5202e`),
halftone dots, Bangers / Archivo Narrow / IBM Plex Mono. Scroll-scrubbed timelines, zoom-through transitions, parallax.

---

## 3. Where everything lives

* **Repo:** `github.com/baraamoh18/Storyteller`, private. Default branch `claude/project-thread-6clyex` (it has PR #3 merged:
  everything up to `b7cc967`). **This session's branch: `claude/new-session-4xc7k0`** (all work below; **no PR yet**, the user
  has not asked for one). Older branch `claude/new-session-em88ar` (PR [baraamoh18/Storyteller#2](https://github.com/baraamoh18/Storyteller/pull/2)).
* **Claude preview artifact** (private): https://claude.ai/artifact/G6A8f5qCYfSL8KYwcFWKxH — version 11 shows chapter 94 but an
  **older reader** (no credit line, auto-scroll or new mix). The Cloudflare sites replaced it for sharing; republish only if asked
  (copy of `site/index.html` without the doctype/html/head/body lines, `root = site/`, files listed explicitly; ≤ 255 files per
  publish, ≤ 511 per version; it still holds the old duel files).
* **Cloudflare Pages** (the user uploads; Claude cannot reach Cloudflare or `*.pages.dev` from here): projects **`tbate-reader`**
  (← `dist/Storyteller-Site.zip`) and **`tbate-scroll-demo`** (← `dist/Storyteller-Demo.zip`). New version: project → **⋯** →
  **Create deployment** → drag the zip → Deploy. New project: Workers & Pages → Create → Pages → Upload assets.
* **The user's storage:** Drive `Storyteller/cbz`, `Storyteller/chapters` (zips out; `chapter_094.zip` is there),
  `Storyteller/music_takes`; Kaggle dataset `tbate-cbz` + notebook outputs; PC: the reader folder ("Storyteller Reader") and the
  chapter kit folder.

```
HANDOFF.md                            this file
series/cast.md                        the user's cast list (~95 characters: looks, magic colours, first episodes)
site/                                 the reader (details: site/README.md)
  index.html                          engine, chapter menu, auto-scroll, sound; no chapter data inside
  series.js                           title, playlist, credit, chapter list, mix, autoScroll, music themes, recorded sounds
  chapters/094/chapter.js             chapter 94 (90 scenes)      (*.webp from the chapter zip: not in git)
  chapters/094-demo/chapter.js        the 19-panel demo           (*.webp copied by cut_chapter.py, cover.jpg: not in git)
  music/<theme>_<n>.mp3, sfx/*.mp3    loops and the user's two sword recordings
tools/
  build_notebooks.py                  rebuilds the chapter notebooks + PC kit zip from the scripts (run after script changes)
  layer-splitter/split_layers.py      the AI splitter (panels, bubbles, cutouts, fill)
  make-chapter/                       make_chapter.py, gpu_check.py, Make_Chapter.ipynb, Make_Chapters_Kaggle.ipynb, README
  pc/                                 the chapter kit for Windows: Setup.bat, Make Chapters.bat, README.txt (CRLF)
  director/                           draft_chapter.py (first draft, carry-over), cut_chapter.py (demo cuts), README
  reader/                             reader.py + Read Storyteller.bat + README.txt (PC reader, CRLF), build_reader.py (all zips),
                                      record_demo.js + render_demo_audio.js (the demo video), cover.html (link-preview cover)
  music/                              Make_Music.ipynb (MusicGen on Colab), make_loop.py
  voices/                             make_voices.py (Kokoro; voices are off)
dist/                                 built zips and the video (not committed)
```

---

## 4. The pipeline

```
CBZ ─► chapter maker (Colab / Kaggle / PC GPU) ─► chapter_<id>.zip (~5-15 MB)
    ─► user uploads it to a Claude session ─► draft_chapter.py (+ carry-over) ─► Claude directs chapter.js
    ─► Playwright checks ─► preview for the user ─► approval / notes
    ─► series.js line ─► reader pack for the PC (build_reader.py --pack <id>) + rebuilt website zip for Cloudflare
```
Processing only has to stay ahead of directing; directing + approval is the bottleneck.

---

## 5. The splitter (`tools/layer-splitter/split_layers.py`)

Per chapter strip (all pages joined, natural file order):
1. **Panels:** rows of the most common border colour are gutters (`find_panels`).
   **New this session — `split_tall`:** a "panel" over **2.5 strip widths** tall is usually long plain space (black with embers, a
   fade, a texture) with pictures inside. `row_busyness` = share of a row's pixels > 40 away from the row's median colour (in 2048-row
   blocks, every 2nd column). Plain rows (< 0.03) in runs ≥ **0.5 strip widths** are dropped like gutters; segments with fewer than
   120 busy rows are crumbs and dropped; a piece still over **4.5 strip widths** is cut at its calmest row (31-row smoothed
   busyness, slight pull to the middle) and marked `continues: panel_XX` unless the cut fell in a plain band. Chapter 94 is
   unchanged by this (its tall panels are real pictures). Checked by eye on chapters 2, 3, 4.
2. **Bubbles:** near-white area with holes; holes are black ink (> 30% darker than 100), lettering 2–45% of the filled shape,
   roundish, ≥ 2 letter-sized dark shapes, ≤ 5% colourful hole pixels. Saved grown 15 px.
3. **Characters:** `birefnet-general` + `birefnet-hrsod` (rembg), each on the panel and its mirror (averaged), max-combined;
   ViTMatte edges; `pymatting` edge colours. Note: rembg squashes every panel to 1024×1024 — why tall panels must stay ≤ 4.5 widths.
4. **Background:** LaMa (≤ 2048 px on GPU, halving on out-of-memory).
5. Writes `original.png`, `background.png`, `characters.png`, `bubbles/`, `layers.json` (panels may carry `continues`).

**Providers:** CUDA, else DirectML, else CPU; `onnxruntime.preload_dlls()` when present; `Models.timings`, `cutouts_on_gpu`.
**Speed:** ~3.7 s per cutout model per panel on a T4, ~10 s per panel all in; 13–23 min per chapter (Kaggle logs).
**Model comparison, known limits, solved problems:** as before — general most reliable, hrsod the partner, lite/massive/dis/
isnet-anime rejected; sound-effect lettering stays in the character layer; undetected bubbles stay in the art.

| Problem already solved (do not reintroduce) | Fix |
|---|---|
| `simple-lama-inpainting` pins Pillow < 10 | install with `--no-deps` |
| `simple_lama_inpainting.utils` has an empty `__init__` | import from `simple_lama_inpainting.utils.util` |
| joined strips used 6.7 GB for detection | bubbles as small crops, int16 |
| capping numba/Pillow pulled an old rembg | no caps; `sessions_class[name](name, options, providers=...)` |
| ORT GPU on a T4 with CUDA 13 silently used the CPU | start on CPU, `_move_to_gpu` tries `HEURISTIC` then `DEFAULT` |
| ORT memory pools starved LaMa | `kSameAsRequested` + arena shrinkage; LaMa empties torch's cache |
| eyes / white faces taken as bubbles | letter-shape + colour rule |
| **"Image size exceeds WebP limit of 16383 pixels"** (10 Kaggle chapters) and squashed cutouts in tall panels | `split_tall` (above) |

---

## 6. The chapter maker (`tools/make-chapter/`)

`make_chapter.py --cbz-dir … --out … --chapters 1-5,94 [--skip '{"94":[0,69]}'] [--redo] [--shard K/N] [--done-dir D] [--max-hours H]`
1. Finds CBZ files by number (also in subfolders); ids are 3-digit (`094`, `094-5` for 94.5).
2. Drops non-story pages: first two / last two pages compared (16×32 dhash, ≤ 110 of 512 bits) with chapter 94's **series title
   page** and **creators' promo page** fingerprints. **New:** a match also needs `distance < bits set in the page` — a plain page
   (black, a fade, a small picture on black) has almost no bits set and sat near every fingerprint (a blank page was only 72 bits
   from the promo page). Kaggle's chapter 22 dropped page 000 as "promo" before this fix: glance at `sheets/pages.jpg`.
3. Joins pages (other widths scaled to the most common), runs the splitter.
4. WebP (bg q80, chars q85, bubbles q90, method 6). Each bubble gets a panel (inside it, else the nearest, never a tiny one),
   in-panel `x, y, w, h`, `between_panels`, `suspect`. Tiny panels: < 120 px a side or < 40,000 px². Panels carry `continues`.
5. Zip built locally, moved into `--out` whole. Chapters with a zip in `--out` / `--done-dir` are skipped — **except** zips made
   before the tall-panel fix (`made_before_tall_fix`: a panel taller than 4.5 strip widths), which are remade automatically.
   `--shard K/N` (stable across runs), `--max-hours`, per-step timings in `chapter.json` `seconds`.

**The zip** `<id>/`: `panel_XX_background.webp`, `panel_XX_characters.webp`, `bubble_XX.webp`, `chapter.json`,
`sheets/pages.jpg`, `sheets/panels_XX-YY.jpg` (5 per sheet, TINY marked), `sheets/bubbles.jpg`.

| Where | How | Notes |
|---|---|---|
| Colab | `Make_Chapter.ipynb`: T4 + High-RAM, `CHAPTERS`, Run all, allow Drive | Drive in/out; tab must stay open |
| Kaggle | `Make_Chapters_Kaggle.ipynb`: GPU **T4 ×2**, Internet On (verified phone), dataset as Input; **Save Version → Save & Run All** | two processes (`--shard 1/2`, `2/2`), `MAX_HOURS = 11`, logs `log_gpu0/1.txt` in Output; next run: add the previous version's Output as Input (→ `--done-dir`). Update the notebook via **File → Import Notebook**. |
| PC (RTX 5050) | `Storyteller-PC-Tools.zip` → `Setup.bat`, then `Make Chapters.bat` | Python 3.12, torch cu128, models in the kit folder, output `finished/` |

`gpu_check.py` (exit 3 = cutouts on CPU) → Kaggle installs `onnxruntime-gpu==1.22.0`; PC tries that, then DirectML.
Delivery: the user uploads zips into the session, 2–3 per message. (A private `Storyteller-data` repo push was proposed, never approved.)

---

## 7. Directing (`tools/director/`) and the house style

* `draft_chapter.py ZIP --out site/chapters/<id>/chapter.js --title "…" [--carry-over OLD/chapter.js --report]`: first draft
  (every non-tiny panel; `fit: "pan"` when taller than 1.45× its width; length from shape; push-in; dust; bubbles in reading
  order; suspect bubbles as `// check`; music one `calm` stretch). **New:** pieces of one tall picture (`continues`) get plain
  `cut` exits/entries and a `// continues …` note. Carry-over pairs panels by size (±3 px), keeps bubble timings, moves music.
* `cut_chapter.py SOURCE --id --title --panels 01,02,70-72 --music "tension:01,climax:70,calm:92"`: a demo chapter from a directed one.
* **The director playbook skill is still not written** — the house style lives here until then:
  * **Camera:** gentle push-in (1 → 1.06–1.2) or settle-out (1.1–1.16 → 1) per panel; `origin` on the subject; tall panels
    `fit: "pan"` with a slight `chars` scale for depth; wide shots drift sideways (`camera x` ±4–7); never crop lettering (panel 34:
    zoom out instead of in, so "F---!" stays).
  * **Transitions:** `fade` by default; **zoom-through** (`exit: "zoom", focus` → next `enter: "zoom"`) for build-ups into a big
    moment (78 → 79 TEMPEST); `cut` for direct continuations and carried match cuts.
  * **Impacts:** shake + flash + burst + sfx at the same moment. `deflect` for blades turned aside / light TING, `parry` for heavy
    clashes, `crash` + a held white-out (`flashes hold`, strength 1) for the biggest hit, `shatter` sound + `shatter` burst for glass,
    `thud` for bodies hitting the floor, `crack` for a stab, `grip` for anger (GRIT), `glint` for a blade catching light.
  * **Particles:** embers in the fighter's colour (`mana` blue for Arthur's and Geist's sword mana, `ember` orange for Geist's anger,
    **`wind`** green-white for Arthur's TEMPEST), `speed` streaks for dashes/swooshes, `dust`/`paper` for calm scenes; `amount`
    0.25 (quiet) → 1.7 (TEMPEST).
  * **Bubbles:** pop where they sit, `at` after the reader can see the speaker (0.06–0.4), several staggered; lettering drawn on art
    `pop: false`; a bubble the maker placed outside a `pan` panel (y < 0 or y > h) must be moved inside, or it scrolls off / never
    shows (094: bubble_24 → y 2300 with `out: 1`; bubble_26 → y 10); a bubble low on a tall pan panel needs `out` ≥ 0.92.
  * **Music:** one theme per story stretch; climax for the finale, calm after the storm.
  * **Quiet beats:** after a big moment, one still panel with low particles and no sfx (75 "No.", 83 the calm smile).
  * Use `series/cast.md` for speakers and colours; confirm names with the user when unsure.

---

## 8. The reader (`site/`, details in `site/README.md`)

* GSAP 3.12.5 + ScrollTrigger (cdnjs); one pinned stage; one timeline, **1 unit = 1vh**, `scrub: 0.7`.
* `series.js` first; `index.html#<id>` picks the chapter; `chapters/<id>/chapter.js` → `registerChapter(...)` → `boot()`.
  "Chapter not ready" = that chapter.js did not load (on Cloudflare a missing file returns index.html, so it shows as that).
* **Per panel:** `.scene` → `.zoom` → `.shake` → `.pan` → `.rig` → `.frame` (`img.bg`, `canvas.fx-mid`, `img.chars`); bubbles in `.rig`,
  nudged on screen (56 px clear at the top for the buttons).
* **Scene settings:** `length`, `fit`, `camera`/`origin`, `bg`/`chars` (`over`), `bubbles` (`src, x, y, w, h, at, out, pop`), `shakes`,
  `flashes` (`at, color, strength, rise, hold, fall`), `sfx`, `fx` (`ambient`, `tint` paper/mana/ember/**wind**, `amount`, `bursts`
  splinters/sparks/ring/flare/shatter with `at`, `from`, and `tint` for sparks/flare), `enter`/`exit` cut/fade/zoom + `focus`.
* **New this session:**
  * `wind` tint; burst `tint`; bubble `out` (fade moment, default 0.8; ≥ 0.92 stays).
  * **Credit line** from `SERIES.credit` on the title and end cards (`**bold**` for names): "The Beginning After the End: story by
    TurtleMe, art by Fuyuki23, published by Tapas. A non-commercial fan tech demo by Baraa, built with AI. All rights…".
  * **Auto-scroll** (`makeAutoScroll()`): ▶ Auto-scroll on the title card + Auto/Pause next to Sound at the top; **slider 0.5×–2×**
    (`localStorage` key `storyteller.autoSpeed`); base **60 units/s**; holds: bubbles `0.6 + w*h/75000` clamped 1–4 s, big moments
    (crash 1.3, shatter 0.9, parry 0.7, deflect 0.6, thud 0.7, strong flash 0.8, held flash 1.4, shatter burst 0.9), holds closer
    than 8 units merged; actual hold = `0.3 + pauses × hold / √speed` with **`SERIES.autoScroll.pauses = 0.65`** (the user found
    1.0 too long); crawl 4% during a hold; brake τ 0.18 s, set off τ 0.4 s; wheel / touch / scroll keys / manual scroll pause it;
    stops at the end card; keys on the controls work the controls. Measured: first bubble hold 1.9 s at 1×; chapter ≈ 6 min at 1×.
  * **PC-only:** loads `__chapters.js` (chapter menu built from the chapters folder) on http + localhost/IP hosts, and on
    localhost shows "Read on your phone" with the LAN address and a QR code (`qrcode-generator@1.4.4` from jsdelivr).
* **Reduced motion:** plain column, no animation, sound or auto-scroll.
* **Bugs already fixed:** no `invalidateOnRefresh`; the pan lives on `.pan`; `.zoom` centred by hand.

---

## 9. Sound

* Off until **Play with sound**. Effects fire when scrolling forward past their moment (not on jumps > 25 units).
* Synthesised (`makeEffects(ctx, out)`): whoosh, swish, crack, grip, flame, clang, skid, tap, thud, glint, shatter, crash, gust.
  Recorded (`SERIES.sounds`): the user's Sekiro `deflect` and `parry` (trimmed, high shelf down, ~2 semitones lower, ±2% pitch).
* **Chain:** effects bus 0.65 → limiter (−10 dB, ratio 20, 1 ms) → tanh soft clip. **New:** all music goes through a **music bus
  `SERIES.mix.music` = 0.65** that **dips to `mix.dip` = 0.5** under every effect (τ 15 ms down, back after 0.35 s, τ 0.25 s).
  Reason: at the old balance the climax drums buried most effects under the limiter (measured). Tested: the bus dips at TING.
* **Music:** themes per stretch, takes with volumes, crossfades (in 40 / out 60 units), MP3 padding skipped. Library: calm_1 0.5,
  tension_1 0.4, battle_1 0.53, battle_2 0.63, battle_dark_1 0.58, battle_dark_2 0.5, climax_1 0.75, climax_2 0.56.
  **094:** tension 1–14, battle 15–31, battle_dark 32–48, battle 49–57, climax 58–87, calm 88–92. **094-demo:** tension 01–07,
  climax 70–89, calm 92.
* Making music: `Make_Music.ipynb` → `make_loop.py`. The AI cannot listen: measure and say so.
* User's taste: Academy warm/light fantasy or music box; fights cinematic orchestral, choir and drums; Relictombs dark synthwave;
  reading playlist link on the title card (Spotify, cannot be used as audio).
* Voices off (`tools/voices/make_voices.py` works; playback code in commit `77414a1`).

---

## 10. Chapter 94 "The Duel" (approved)

* **Source:** `The Beginning After the End 94 - Chapter 94.cbz`, 70 pages × 940 px (000 title and 069 promo dropped), strip
  940 × 125,394 → **92 panels** (90, 91 tiny, skipped) → **90 scenes**, **26 bubbles**. Panel N = old duel panel N − 9 for 10–69.
* **Cast in it:** Arthur Leywin (red hair, DC uniform; blue mana; green-white wind at the end), Professor Geist (spiky brown hair,
  headband; blue-flame sword; red-orange anger), **Kathyln** (black hair) and **Feyrith** (golden-blonde, two front braids) with
  **Sylvie** (white fox form) in panel 04 — confirmed by the user; panel 03 students unnamed.
* **Opening (1–10):** 01 blade in the sky, fade in, glint, mana embers · 02 pan down Arthur → Geist · 03 sideways drift over the stands
  · 04 push in on Sylvie · 05 Geist's smirk "Quite a nice weapon…" · 06 tilt up, "Since you're an Augmenter / …let you choose…" ·
  07 Arthur "It doesn't matter." (quiet) · 08 Geist trembles (small shakes, grip, orange embers) · 09 pan, "Arrogant brat!", GRIT
  jolt + red flash, "I insist." · 10 Arthur "Please use whatever you're most confident in." (fade in, not the old cut).
* **The duel (11–69):** carried over unchanged from the approved old plan (section notes restored at +9: first exchange 20,
  onslaught 25, leaping slash 32, flame pillar 38, leap and slide 45, stands 49, counterattack 50, "Professor." 58, clash 60,
  "a totally different level" 65). Panel 34 zooms out now.
* **Finale (70–92):** 70 TING (deflect, sparks) · 71 DASH (speed) · 72 the charge (wind embers, swish, gust) · 73 Geist blocks (parry,
  blue flash, flare) · 74 "You think this is enough?!" · 75 "No." (still) · 76 the flip, long pan, "But this might be." (moved into
  the panel, `out: 1`) · 77–78 the hand gathering wind, 78 zooms into 79 · **79 TEMPEST** (green-white flash held 0.04, shakes, gust,
  wind flare + ring) · 80 Geist shields his face · 81 the blades rain down (thud, ring) · 82 SWOOSH · 83 the calm smile (still) ·
  84 CRACK (shatter sound + burst across the screen) · 85 SCRATCH (red flash) · 86 "S-stop!" · **87 CRASH** (shatter at the top,
  crash with a full white-out held 0.06, shakes) · 88 THUD · 89 STAB (crack, blue flash, sparks) · 92 "Thank you for your
  guidance." (moved to y 10, slow pan up, calm music).

---

## 11. Sharing: websites, the demo, LinkedIn

* **Builds** (`tools/reader/build_reader.py`; images must be in `site/chapters/<id>/`):

| Command | Output | Goes to |
|---|---|---|
| `build_reader.py` | `dist/Storyteller-Reader.zip` (PC reader + chapters in series.js) | user's PC (unzip) |
| `build_reader.py --pack 094` | `dist/reader-pack_094.zip` | PC: `new chapters` folder |
| `build_reader.py --reader-update` | `dist/reader-update.zip` (index.html + series.js) | PC: `new chapters` folder |
| `build_reader.py --site` | `dist/Storyteller-Site.zip` (+ `_headers` noindex, `robots.txt` Disallow) | Cloudflare `tbate-reader` |
| `build_reader.py --site --chapters 094-demo --public https://tbate-scroll-demo.pages.dev --cover site/chapters/094-demo/cover.jpg --out Storyteller-Demo.zip` | `dist/Storyteller-Demo.zip` (preview tags, cover, search engines allowed: LinkedIn's crawler obeys robots.txt) | Cloudflare `tbate-scroll-demo` |

* Website zips list **every folder as its own entry** (`add_folder_entries`): Cloudflare's drag-and-drop skipped the chapter folder
  of a zip that only listed files (that was the "Chapter not ready" problem). The first deployment's 404 at the root was never
  explained (likely the same zip issue); a new deployment of the rebuilt zip fixed everything.
* **Demo cut 094-demo:** panels 01, 02, 04, 06, 07, 70–72, 74–76, 78, 79, 81, 84, 86, 87, 89, 92 (19 scenes, 8 bubbles, 4850 units).
* **Cover** (`site/chapters/094-demo/cover.jpg`, not in git): `tools/reader/cover.html` (template, notes inside) + panel 79 crop.
* **Video** `dist/Storyteller-Demo-Video.mp4` (not in git): 56 s, 1080×1350, 30 fps, H.264 CRF 18 + AAC 192k, −14.8 LUFS, peak −1.6.
  How: serve the unzipped demo site on :8803 under the host `tbate-scroll-demo.pages.dev` (`--host-resolver-rules`), then
  `node tools/reader/record_demo.js <dir>` (viewport 540×675 @2x, Playwright fake clock stepped 1/30 s, HUD sound button hidden,
  scroll path ≈110 units/s, slower at 79/87/92/84, title 2.6 s, end card 3.4 s → frames), `record_demo.js <dir> cues` (when each
  sound fires), `render_demo_audio.js <dir>` (music + effects in an OfflineAudioContext with the site's `makeEffects` and chain;
  music bed 0.55 dipping to half under each effect) → ffmpeg `loudnorm=I=-14.5:TP=-3:LRA=11,alimiter=limit=0.84` → mux.
  The music mix for it was made in numpy from the loops (tension 0–14.9 s ×0.4, climax from 12.9 s ×0.75, calm from 46.4 s ×0.5,
  fades 1–2.5 s). **Do not use ffmpeg `-stream_loop` on the MP3 loops** (it clicked); tile the decoded samples.
  `<dir>` needs `gsap/package/dist` (npm pack gsap@3.12.5) and `fonts/fonts.css` + `fonts/woff/` (@fontsource bangers,
  archivo-narrow, ibm-plex-mono 5.1.0, served as `http://fonts.local/…`).
* **LinkedIn post draft** (sent; the user rewrites it): hook "What if a webcomic chapter played like a film while you scroll? 🎬",
  what it is, the 5 phases (cloud-GPU chapter maker → AI panels/bubbles/BiRefNet/LaMa → Claude directs → the user reviews → GSAP +
  Web Audio reader), "I brought the idea, the taste and the decisions; AI made it possible…", demo link, credits, 5 hashtags.
  Advice given: upload the video natively, link in the post or first comment, check the card at linkedin.com/post-inspector.

---

## 12. The PC reader (`tools/reader/`)

* `Read Storyteller.bat` (CRLF): finds `py -3` or `python`, else explains how to install Python (same as the chapter kit), runs
  `reader.py`. `reader.py` (standard library, Python ≥ 3.8): adds every zip in `new chapters/` whose entries are all under
  `chapters/`, `music/`, `sfx/`, `index.html`, `series.js` (others are skipped with a message: a maker zip goes to Claude), moves it
  to `new chapters/added/`; serves `reader/` on port 8000 (or the next free, up to 8010) with ThreadingHTTPServer, explicit MIME
  types, `Cache-Control: no-cache`; answers `/__chapters.js` and `/__phone.json`; opens the browser; prints the phone address.
* First run on Windows: the firewall asks for Python → **Private networks → Allow**. Phone problems: same Wi-Fi, network profile
  **Private**, firewall app list (all in `README.txt`).
* PowerShell could not be tested here (downloading it was refused), hence Python.

---

## 13. Next steps (in order)

1. **Kaggle rerun:** ask whether it finished; get the zips + `log_gpu0/1.txt`. Check dropped pages (`sheets/pages.jpg`) and the new
   tall-panel splits by eye on a couple of chapters, then **direct chapters from Episode 1**, one plan + preview per chapter, user
   approval, then a reader pack and rebuilt website zip.
2. **Write the director playbook** as a repo skill from Section 7 (use the skill-creator / writing-for-agents skills).
3. **PC reader / PC kit:** when the user runs them on Windows, fix what the first run shows (ask for screenshots of the black window).
4. **Music library:** the user runs `Make_Music.ipynb`; loop the takes, add to `SERIES.themes`.
5. Keep the websites in step: after any reader change, rebuild `--site`, the demo and `--reader-update`, send them, remind the
   user of the three upload steps (Section 3) and **Ctrl + F5**.
6. **Optional (ask first):** a PR for `claude/new-session-4xc7k0`; a "How it's made" page with an interactive layer slider (offered,
   the user chose other items first); republishing the Claude preview; automatic delivery via a private data repo.
7. **Later:** voices; light directing mode for dialogue chapters.

---

## 14. Instructions for the next AI session

**Working with the user**
* Plain language, one step at a time, exact click paths; attach files (SendUserFile) instead of describing them.
* Plan before big work and wait for "go"; small fixes and follow-ups can just be done.
* You cannot listen to audio: measure (loudness, peaks, clicks, effect-vs-music level at each cue) and say what you measured.
* Reproduce Colab / Kaggle / Windows / Cloudflare problems here when possible before answering; when it cannot be reached
  (Cloudflare, `*.pages.dev`), give quick test URLs (e.g. `/chapters/094/chapter.js`) and ask for screenshots.

**Keep files in sync**
* After editing `split_layers.py`, `make_chapter.py` or `gpu_check.py`: `python tools/build_notebooks.py`; commit the notebooks.
* After editing `site/index.html` / `series.js`: rebuild the zips (Section 11) for the user.
* `.bat` and `tools/reader/README.txt` keep **CRLF**.

**Recreating the working set in a fresh container**
* Chapter images are not in git: ask for `chapter_094.zip` (Drive `Storyteller/chapters`), unzip its `094/*.webp` into
  `site/chapters/094/` (not the tiny panels 90, 91), then `cut_chapter.py …` (Section 11) for `094-demo`, then rebuild the cover
  (`tools/reader/cover.html`) if a demo zip is needed.

**This cloud environment**
* No GPU. **Blocked:** Hugging Face, cdnjs, Google Fonts, download.pytorch.org, Spotify, Pixabay, freesound, archive.org,
  developers.cloudflare.com, `*.pages.dev`. **Reachable:** GitHub, PyPI, npm (use npm for GSAP, fonts, qrcode-generator).
  Downloading/running external binaries (e.g. PowerShell) was refused by the permission system.
* ffmpeg/ffprobe are installed; `pip install opencv-python-headless scipy` is needed to import `split_layers` (torch is not
  installable: test the maker with stand-in models: `character_alpha`, `character_colours`, `fill_background`, `timings`).
* **Site tests:** serve `site/` with `python3 -m http.server 8765`, drive it with the preinstalled Playwright, route cdnjs GSAP to a
  local copy, abort or route Google Fonts; stop with `pkill -f "http.serve[r] 8765"`. Useful: `--host-resolver-rules=MAP
  <name>.pages.dev 127.0.0.1` to test as the website; `page.clock` for deterministic frames; `--autoplay-policy=no-user-gesture-required`
  and patching `AudioParam.prototype.setTargetAtTime` to check ducking.
* Commit and push to `claude/new-session-4xc7k0` (or the branch the session is given) after each change.
* Do not put model names in commits or files.

---

## 15. Third session's commits (oldest first)

| Commit | What |
|---|---|
| `5ea630f` | merge the second session's last commits (Kaggle notebook, PC kit, handoff) into this branch |
| `b791f39` | split very tall panels, remake old zips that had them, keep plain pages |
| `de41f03` | chapter 94 directed in full; wind tint, burst tint, bubble `out`; images out of git |
| `45b9025` | the PC reader (reader.py, Read Storyteller.bat, build_reader.py, phone QR card) |
| `cab2a0a`, `7a628bb` | retire the old duel cut |
| `13cc51b` | website zip for Cloudflare Pages |
| `5cf0520` | public demo: credit line, cut_chapter.py, 094-demo, link preview, video recorder |
| `e90f634` | website zips list every folder as an entry |
| `78a7294` | sound effects in the demo video's soundtrack |
| `4c15165` | site sound rebalance: music bus with ducking; `--reader-update` |
| `fd4009b` | auto-scroll with a speed slider, slowing for bubbles and big moments |
| `08123e9` | shorter auto-scroll pauses (`SERIES.autoScroll.pauses`) |

Second session's commits: `687ea87` … `e14da16` (see git log: panels 11–60, music, series reader, cast list, Make_Chapter
notebook, music notebook, draft tool, shatter/crash/gust, the Sekiro sounds, subfolders, timers/shards, Kaggle + PC kit).
