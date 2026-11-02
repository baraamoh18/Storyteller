# Project Handoff: AI-Driven Manhwa Scrollytelling Website

> **Status (last updated 2026-11-02, second session):** Stage 1 (splitting the chapter into layers) is done and runs fast on Colab's T4 GPU.
> Stages 2 and 3 are working for **panels 1–60**: a scroll site with parallax, zoom-through cuts, particles, sword sound effects and all speech bubbles.
> **Voices are switched off** at the user's request ("needs more adjustments").
> **Waiting on the user:** run `tools/music/Make_Duel_Music.ipynb` (or send free tracks) and pick an academy and a fight track; send panels 61–65.
> Read **Section 9: Next steps** and **Section 10: Instructions for the next AI session** first.

---

## 1. The project and the user

* **Goal:** turn a static manhwa chapter into an interactive, animated "scrollytelling" web page. Scrolling plays the scene; scrolling back rewinds it.
* **Comic:** *The Beginning After the End* (TBATE) manhwa. The chapter used is a sword duel.
* **Use:** a **personal project for fun, not going public.** That is why copyrighted art is fine to use here, and why free tools with non-commercial licences (MusicGen) are acceptable.
* **The user (Baraa):** prefers an AI-first workflow with minimal manual coding or design. Wants plain-language explanations, one step at a time, and ready-to-run files.
  * Runs notebooks on **Google Colab Pro**: **T4 GPU + High-RAM** runtime.
  * Works on **Windows**. The local files live in `D:\Work\StoryTelling website\`.
  * Prefers **free** options. Voices in **English**.

## 2. Reference style

Inspired by "The Notturno Experience" interactive graphic novel.
* **Look:** neo-noir. High-contrast black and white with bold flat accents (red), halftone dots, rough ink lines, bold retro comic type.
* **Mechanics:**
  * scroll-scrubbed timelines, not autoplay;
  * zoom-through transitions into a focal point;
  * 2.5D parallax between layers;
  * sequential frame motion.

## 3. Where everything lives

* **Repo:** `github.com/baraamoh18/Storyteller`
  * **Branch with all the work:** `claude/new-session-em88ar` (it contains everything from the older `claude/tender-planck-n2lbxf`). No pull request has been opened.
  * The older branch `claude/project-thread-6clyex` has the original layer splitter only.
* **Live preview** (private artifact, only the user can open it): https://claude.ai/artifact/G6A8f5qCYfSL8KYwcFWKxH. It is published from `site/index.html`, with the `<!doctype>`, `<html>`, `<head>` and `<body>` wrappers stripped (the artifact host adds its own) and every `site/assets/...` file passed through the publish `files` map.

```
HANDOFF.md                         this file
tools/layer-splitter/
  Split_Manga_Layers.ipynb         the Colab notebook the user runs (it carries its own copy of split_layers.py)
  split_layers.py                  the splitter script (keep the notebook's copy in sync when editing!)
  README.md, requirements.txt
tools/voices/
  make_voices.py                   makes the voice lines with Kokoro (kokoro-onnx), runs on a normal CPU
  .gitignore                       model files and out/ are not committed
tools/music/
  Make_Duel_Music.ipynb            Colab notebook: 2 academy + 3 fight looping 30 s tracks with MusicGen -> duel_music.zip
site/
  index.html                       the whole scroll site (CSS + JS in one file; GSAP from cdnjs)
  README.md                        how to edit the scene plan, sound, assets
  assets/panel_XX_background.webp, panel_XX_characters.webp   panels 1-60 (WebP, ~6 MB total)
  assets/bubble_*.webp             very_well, go_easy, going_easy_huh, not_using_spells (bubbles 01-04), bubble_07 ... bubble_18
  assets/audio/academy.mp3, fight.mp3   NOT THERE YET: the page plays no music until they exist (the folder does not exist either)
```

Commits on the branch, oldest first:

| Commit | What |
|---|---|
| `a417406` | Add the layer splitter |
| `76594ac` | Combine two cutout models |
| `5dd8fc8` | Fix the install on Colab (Pillow pin) |
| `580c33b` | Fix the inpainting imports |
| `9073d08` | Option to join webtoon slices |
| `6af869f` | Cut memory use |
| `5e859aa` | Pin numba and Pillow (later reverted) |
| `f389d59` | Bubbles need black ink |
| `310a6b1` | Support old rembg |
| `5203d97` | Low-memory model loading |
| `9dd21dc` | GPU support |
| `45631a1` | Model pair, flip averaging, edge refinement |
| `d4c6665` | Keep confident lines solid; one model on CPU |
| `805f35f` | T4 cuDNN fix |
| `8ee6c9f` | GPU memory fix |
| `733d326` | Quiet the expected cuDNN errors |
| `a6a9a74` | Scroll site, panels 1–10 |
| `77414a1` | Particles, sound effects, voices, music slot |
| `ab1bc52` | Handoff document |
| (this session) | Merge into `claude/new-session-em88ar`; panels 11–60, all bubbles, voices off, music zones, pan fix |

---

## 4. Stage 1: the layer splitter (done)

### What it does
For the uploaded images (with `JOIN_SLICES = True` they are first stacked into one long strip, in natural file-name order, so panels cut between slices come out whole):

1. **Finds the panels.** It looks for gutter rows in the most common border colour.
2. **Finds the speech bubbles.** A bubble is a near-white area with holes; the holes must be **black ink** (more than 30% of hole pixels darker than 100), the lettering must be 2–45% of the filled shape, and the shape must be roundish. It saves each bubble as a see-through PNG, grown 15 px to include the outline.
3. **Cuts out the characters** (`characters.png`):
   * Uses `birefnet-general` + `birefnet-hrsod` via rembg. Each model also runs on the mirrored panel and the two results are averaged; the two models are then combined with a maximum.
   * **ViTMatte** (rembg's `vitmatte_alpha`) refines the edges, with two corrections: its output tops out at 254, so values of 250 and up are snapped to 255; and pixels the models scored 200 or more keep the models' value, because ViTMatte thins speed lines.
   * Edge colours are unmixed from the background with `pymatting.estimate_foreground_ml`. Fully solid pixels keep the exact drawn colours.
   * Without a GPU only `birefnet-general` runs, for memory reasons.
4. **Fills the background** where characters and bubbles were, using LaMa (`simple-lama-inpainting` weights, loaded by hand). It fills at up to 2048 px on the GPU (800 px on the CPU) and retries at half size if the GPU runs out of memory.
5. **Writes per panel:** `original.png`, `background.png` and `characters.png`; plus the `bubbles/` folder, `layers.json` (positions) and `preview.png`.

### How the user runs it
1. Upload `Split_Manga_Layers.ipynb` to Colab (**File → Upload notebook**).
2. Set **Runtime → Change runtime type → T4 GPU + High-RAM**.
3. Click **Runtime → Disconnect and delete runtime** (to clear old installs), then **Run all**.
4. At **Choose Files**, select **all original slices at once** (e.g. `8.webp` … `53.webp`), never the output files.
5. `layers.zip` downloads at the end.

* **Speed:** about **8–9 s per panel** on the T4 (6 AI passes per panel). The first run downloads about 2.3 GB of models.
* **Expected noise** in the output, all harmless:
  * a red pip "dependency conflicts" message in Step 1 (gradio, cudf, cuml and pytensor complain about the Pillow and numba versions);
  * the line `Cutouts run on the graphics card (fast), background fill on the graphics card (fast).` is the one to check.

### Results for this chapter
* Slices `8.webp`–`53.webp` (940 px wide), joined into one strip of 940×84793 → **65 panels, 18 bubbles**.
* `bubble_05` and `bubble_06` (in panel 19) are **two eyes misdetected as bubbles**: ignore them.
* The full `layers.json` zip is about **195 MB**, too big to upload in one go. The user sends subsets (e.g. `layers.json`, `bubbles/` and `panel_01`–`panel_10`). They have twice forgotten `layers.json` and `bubbles/`, so remind them.

### Model comparison (done on 5 of the user's panels, 2026-11-02)
| Model | Verdict |
|---|---|
| `birefnet-general` | Most reliable. Keep as the main model. |
| `birefnet-hrsod` | Clean. Adds only 0.1–0.3% missed edge pixels: the partner model. |
| `birefnet-general-lite` (the old partner) | Added **5–7% wrong background** (auras, gaps between legs, sound effects). Dropped. |
| `birefnet-massive` | Missed both characters in a face-off panel. |
| `birefnet-dis` | Missed spiky hair and half a face. |
| `isnet-anime` | Missed most of the fighters. |
| `bria-rmbg` | Not tried: non-commercial licence. |

* Flip averaging removed wrongly included glows (up to 2.5% of a panel).
* ViTMatte removed see-through ghost patches.

### Known limits
* Sound-effect lettering ("PRY", "CLENCH") stays in the characters layer, often half-transparent.
* Background fills are a little smudgy where characters were.
* Small eye-shaped false bubbles are possible. A possible fix: require at least 3 separate letter shapes inside a bubble.
* Without a GPU, a joined chapter peaks around 12.7 GB of RAM, so keep High-RAM on.

### Problems already solved (do not reintroduce)
| Problem | Fix |
|---|---|
| `simple-lama-inpainting` pins Pillow < 10, which fails on Colab's Python 3.13 | Installed with `--no-deps` |
| `simple_lama_inpainting.utils` has an empty `__init__` | Import from `simple_lama_inpainting.utils.util` |
| Joined strips used 6.7 GB just for detection | Bubbles are kept as small crops and int16 is used: now 1.4 GB, byte-identical output |
| Capping numba and Pillow made Colab install an old rembg (< 2.0.78), whose `new_session()` rejects `sess_opts`; without low-memory options the models needed 14 GB and Colab killed the run (`^C`) | Caps removed. Sessions are built directly with `sessions_class[name](name, options, providers=...)` |
| ONNX Runtime GPU 1.31.1 (CUDA 13, as on Colab) fails on the **T4** with its default cuDNN search (`HEURISTIC_QUERY_FAILED`, `CUDNN_STATUS_NOT_SUPPORTED`) and silently fell back to the CPU | Sessions start on the CPU, then `_move_to_gpu` tries `cudnn_conv_algo_search` `HEURISTIC` and then `DEFAULT` (on the T4 only `DEFAULT` works), each checked with a warm-up run. ORT logging is muted during the tries. |
| On the GPU, the three ORT sessions kept their memory pools and LaMa ran out of CUDA memory | Each session uses `arena_extend_strategy: kSameAsRequested` and the run option `memory.enable_memory_arena_shrinkage = gpu:0`; LaMa empties torch's cache after each fill |
| The notebook's Step 4 zipped an empty folder when Step 3 failed | Step 4 now stops with a clear message |

---

## 5. Stage 2: the choreography for panels 1–10 (done, in `SCENES`)

Focus points are percentages of the panel.

| # | Panel | What happens |
|---|---|---|
| 1 | an onlooker's torso | slow push-in, dust |
| 2 | **"VERY WELL."** (the armoured swordsman) | character comes forward; bubble pops at 0.16 with its voice; **zoom-through into the sword hilt (81%, 90%)** |
| 3 | sword stuck in wood, **"PRY"** | arrives from the zoom; shake, crack sound and wood-splinter burst at 0.30 |
| 4 | the throw, **"WOOSH"** | camera tilts up, whoosh sound; **zoom-through into the raised hand (49%, 41%)** |
| 5 | fist catches the sword, **"CLENCH"** | white flash, shake, grip sound, dust ring |
| 6 | **"BURN"**, tall panel | pans down; blue mana embers, flame sound and flare; bubble "I'LL BE SURE TO GO EASY ON YOU." at 0.38 with its voice; **music starts here** |
| 7 | the dash | sideways sweep, speed streaks, swish sound |
| 8 | **Arthur** (long red hair) | push-in on his face (46%, 32%); blue embers |
| 9 | **"CLANK"**, tall panel | pans down; red flash (strength 0.55), hard shake, clang sound, spark burst with a shockwave ring at 0.46 |
| 10 | the face-off | settles in; **final zoom into the swordsman's eye (80%, 45%)**, then the "To be continued" card |

### Panels 11–60 (added in the second session)
Story beats, so later choreography stays consistent. The swordsman is **Professor Geist** (bubble 15 says so).
| Panels | Beat | Main effects |
|---|---|---|
| 11–15 | first exchange: SLASH, SKIDD, "Going easy, huh?", FIRM grip, DASH | sparks, skid, flame flare; zoom-through 14 → 15 |
| 16–22 | the onslaught, top-down VWOOSH (18, pan), "not using any spells", "Who does he take me for?!", "disciplinary committee… rats" | clangs, speed lines |
| 23–28 | leaping SLASH, Arthur: "Is there really a need for me to attack…", "F---!", flame hand, zoom-through 27 → 28 (Arthur's eye) | thud, flare, glint |
| 29–35 | FLAME PILLAR (pan, blue flash), WOOSH, eye glint, SHHING parry, aura, TAP, WOOM | flame, clang, tap |
| 36–39 | leap and slide, close-ups | thud, skid |
| 40 | the stands: "That doesn't look like a demonstration" / "Should we get the student council?" | bubble 11 is a strip of the wall art, so `pop: false` |
| 41–48 | counterattack: FWOOM ×3, SLING, SKIDD/RUSH match cut (43 → 44, `cut`), SHH, ING (red flash), TAP TAP, "This brat got faster!" | |
| 49–50 | "Even rats become deadly when cornered," … "Professor." (pan) | |
| 51–55 | DASH, the 3569 px CLASH (pan, white flash), STAGGER, "Arthur is pushing Professor Geist back." | |
| 56–60 | "On a totally different level.", eye, OPEN (zoom-through 57 → 58), "It's time to end this.", CLANG | |

---

## 6. Stage 3: the scroll site (`site/index.html`)

* **GSAP 3.12.5 + ScrollTrigger** from cdnjs. One pinned (sticky) stage. One master timeline, in which **1 time unit = 1vh of scroll**, scrubbed with `scrub: 0.7`.
* **Layer nesting per panel:** `.scene` (opacity) → `.zoom` (enter/exit zoom, origin = `focus`; centred with absolute position + negative margins) → `.shake` → `.pan` (the tall-panel pan: CSS `translate` from the `--pan` and `--travel` variables) → `.rig` (camera) → `.frame` (clip) → `img.bg`, `canvas.fx-mid`, `img.chars`. Bubbles sit in `.rig`, outside the clip, so they can overflow the panel border; `layout()` nudges them back on screen (56 px clear at the top for the Sound button).
* **Loading:** images carry `data-src` and get their file when the reader is within 1 panel behind / 3 ahead (`preload`). Particle canvases get their size only while their panel is visible.
* **Scene plan schema:**

  | Setting | What it does |
  |---|---|
  | `length` | scroll length, in vh |
  | `fit` | `"pan"` for tall panels |
  | `camera`, `origin`, `bg`, `chars` | camera and layer moves; `over: [a, b]` limits a move to part of the scroll |
  | `bubbles` | `{src, x, y, w, h}` in the panel's pixels, `at`, and `voice` |
  | `shakes`, `flashes` | `{at, color, strength}` |
  | `sfx` | `{at, sound}` |
  | `fx` | `{ambient, tint, amount, bursts: [{type, at, from}]}` |
  | `enter`, `exit` | `cut`, `fade` or `zoom`, plus `focus` |

* **Particles:** ambient particles (`dust`, `embers`, `speed`) are clock-driven, drawn in each panel's `fx-mid` canvas, with a few big soft ones on the front canvas. Impact bursts (`splinters`, `sparks`, `ring`, `flare`) are **deterministic functions of scroll time** (seeded random), drawn on `fx-front` (z-index above the flash), so they rewind correctly.
* **Sound** (`makeSound`): off until a **Play with sound** button is pressed.
  * **Effects** are synthesised with Web Audio (`crack`, `whoosh`, `grip`, `flame`, `swish`, `clang`). Effects and voices fire only when the timeline passes their moment going forward, and not after jumps of more than 25 units.
  * **Music:** `MUSIC = { src: "audio/fight.mp3", from: "panel_06", volume: 0.5 }`. It loops, with the volume following the scroll (fades in over 40 units, out over the last 60) and dipping to 40% while a voice plays.
  * Missing audio files are skipped quietly.
* **Reduced motion:** the panels show as a plain column, with no animation, particles or sound.
* **Important bugs already fixed:**
  * do **not** use `invalidateOnRefresh: true`. It wiped the hidden starting state of later `fromTo` tweens, so bubbles showed before their moment.
  * GSAP writes `translate: none` on any element whose transform it animates, which silently killed the tall-panel pan (panels 6 and 9 never panned). The pan now lives on its own `.pan` wrapper that GSAP never transforms.
  * A grid with `place-items: center` pins an item taller than the screen to the top, so tall panels started half-way down their pan. `.zoom` is now centred by hand.
* **Placing bubbles for later panels:** position in the panel = bubble x,y minus panel x,y (from `layers.json`; see the tables in Section 11). Bubbles listed as "between panels" need to be attached to the nearest panel, possibly at negative coordinates.

---

## 7. Audio

### Music zones (site)
`MUSIC` in `index.html` is a list: `{ src, from, to, volume }`. Each loaded track loops all the time; its gain follows the scroll,
fading in over 40 units around the start of its stretch and out over 60 around the end, so neighbouring tracks crossfade.
The first track is already up at the top of the page; the last fades out by the end card. Now: `academy.mp3` panels 1–5 (0.4), `fight.mp3` panel 6 on (0.5).
The user's taste in music for TBATE (their notes): Academy arc = warm acoustic / light fantasy / gentle piano; fights = heavy cinematic orchestral
(Attack on Titan / Solo Leveling style), percussion and choir for desperate turns; Relictombs = dark synthwave / post-rock. **Instrumental only.**
A long fight on one 30 s loop repeats a lot: a second fight zone (e.g. panels 40–60, starting at the stands) is an easy upgrade once there are two good fight takes.

### Voices (OFF for now: the user wants more adjustments first)
The site no longer loads or plays voices and `site/assets/audio/voice_*.mp3` were removed. The old playback code (with music ducking) is in commit `77414a1`.
`tools/voices/make_voices.py` uses **kokoro-onnx**:
* The regular `kokoro` package needs Python below 3.13, so it won't install on Colab now.
* kokoro-onnx runs on a CPU. Its model files come from GitHub: `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/` (`kokoro-v1.0.onnx` and `voices-v1.0.bin`).
* Each voice is a blend of preset voices plus a pitch shift via ffmpeg (`asetrate`/`atempo`), a light room echo and `loudnorm`, saved as 96 kbps mono MP3.

**Measured pitch of the presets** on the same sentence: `am_onyx` 86 Hz (deepest), `bm_lewis` 94, `am_puck` 107, `am_echo` 107, `am_michael` 118, `am_adam` 119, `bm_fable` 119, `am_liam` 123, `bm_daniel` 125, `am_fenrir` 130, `bm_george` 143, `am_eric` 154, `am_santa` 183.

| Character | Description | Options (A is the default) | Measured |
|---|---|---|---|
| **Arthur Leywin** (main character, long red hair) | the user wants a **deep voice**; calm and controlled (a reincarnated king) | A: onyx 0.7 + lewis 0.3, −1 st · B: onyx, −1.5 st · C: onyx 0.6 + fable 0.4, −2 st | ~89–98 Hz |
| **The armoured swordsman** (headband, scar, blue-flame sword) | younger, confident, a bit smug. **Name not confirmed**: web searches failed, so ask the user if needed. | A: michael 0.7 + liam 0.3 · B: puck 0.6 + liam 0.4, +0.5 st · C: bm_daniel | ~112–141 Hz |
| **Onlooker** (a student watching) | impressed, the lightest voice | A: eric 0.6 + adam 0.4, speed 1.08 | ~143 Hz |

Lines so far (only 4 bubbles have known text):

| Line file | Speaker | Text | Panel |
|---|---|---|---|
| `very_well` | swordsman | "Very well." | 2 |
| `go_easy` | swordsman | "I'll be sure to go easy on you." | 6 |
| `going_easy_huh` | Arthur | "Going easy, huh?" | 13 |
| `not_using_spells` | onlooker | "He's not using any spells... just strengthening his body and sword with mana." | 19 |

The user was sent the candidate takes (`<line>__<who>_<A|B|C>.mp3`) and has **not picked yet**. To swap the default: reorder the options in `CAST`, re-run the script, and copy `out/voice_*.mp3` to `site/assets/audio/`.

### Music (not done)
The user wants **both**:
1. **AI-generated:** `tools/music/Make_Duel_Music.ipynb` on Colab (T4). It uses `transformers` `MusicgenForConditionalGeneration` with `facebook/musicgen-large`, `dtype=float16`, 1500 tokens (about 30 s), `guidance_scale` 3. It makes five tracks (`academy_strings`, `academy_harp`, `fight_orchestral`, `fight_choir`, `fight_hybrid`), each blended 1.5 s end-into-start so it loops, normalised with loudnorm and saved as MP3; the zip is `duel_music.zip`. **Not yet run by the user, and untested here** (Hugging Face is blocked in the AI's environment).
2. **Free to use:** the user downloads a track, e.g. from Pixabay Music ("epic battle", "anime fight") or the YouTube Audio Library (Cinematic, dramatic). The AI then trims or loops it into `site/assets/audio/fight.mp3`.

There is no official per-chapter soundtrack for this webtoon.

---

## 8. Characters and story notes
* **Arthur Leywin:** the TBATE protagonist, a reincarnated king (Grey). In these panels: long red/auburn hair, Xyrus-style black uniform, a sword glowing blue. Appears in panels 8, 10 and 13.
* **The swordsman:** spiky brown hair, white headband, armoured shoulder, a cloak with an emblem, a blue-flame sword ("BURN"). Says "Very well." and "I'll be sure to go easy on you."
* An onlooker comments on Arthur strengthening his body and sword with mana (panel 19).

---

## 9. Next steps
1. **Music:** the user runs `Make_Duel_Music.ipynb` and/or sends free tracks. Pick one academy and one fight take, convert to `site/assets/audio/academy.mp3` and `fight.mp3` (mono or stereo MP3, ~128 kbps), check the loop point, adjust the volumes in `MUSIC`, then republish.
2. **Panels 61–65:** not sent yet. Convert (backgrounds q80, characters q85, `method=6`) and extend `SCENES`; `bubble_18` ("You think this is enough?!", panel 65 at 103,240) is already in `assets/`. Then end on a final beat and update the footer card.
3. **Voices (later):** the user wants adjustments before they come back. All bubble texts are now known (Section 11), so more lines can be made.
4. **Nice-to-haves:**
   * recorded free sound effects (e.g. CC0 from freesound) in place of the synthesised ones;
   * a letter-count rule against eye false bubbles;
   * Segment Anything for any missed cutouts;
   * outpainting or depth maps (original handoff, Stage 1 steps 3–4).
5. **Publishing:** this is a personal project, so the preview artifact is enough. A local run is also possible: double-click `site/index.html`, or run `python -m http.server` in `site/`.

---

## 10. Instructions for the next AI session

**Working with the user**
* Plain, non-technical language. One step at a time. Give exact click paths for Colab.
* Send notebooks and files as attachments. The user downloads them and uploads them to Colab.
* The user often reopens an **old notebook copy from Google Drive**: ask them to check the version, e.g. search for a known string or look at the Step 1 install line.

**When the user reports a Colab error**
* Reproduce it locally first: install the same package versions, simulate the failure, and test the fix before sending a new notebook.
* The user's Colab currently runs **Python 3.13, CUDA 13** (PyPI torch is `+cu132`), `onnxruntime-gpu` 1.31.1 and rembg 2.0.86.

**Keep files in sync**
* After editing `split_layers.py`, regenerate the notebook cell that starts with `%%writefile split_layers.py` from the file.
* The voice script reads model files from its own folder.

**The AI's cloud environment** (for an AI in Claude Code on the web)
* **No GPU.**
* **Blocked:** Hugging Face and cdnjs.
* **Reachable:** GitHub releases, PyPI and npm.
* **Testing the site:** serve `site/` with `python3 -m http.server` and drive it with the preinstalled Playwright. Route the cdnjs GSAP URLs to a local copy from `npm pack gsap@3.12.5` and abort the Google Fonts requests.
* Running code cloned from third-party GitHub repos was blocked by the safety classifier, so prefer published packages.
* rembg's models download from GitHub releases into `~/.u2net` / `~/.rembg`. `birefnet-general` takes about 40 s per panel on the CPU here.

**Where the user's work lives**
* Commit and push to `claude/new-session-em88ar` after each change (or the branch the session names).
* Republish the preview artifact to the same URL by publishing the same scratch file path, or by passing `url`.

---

## 11. Chapter layout from `layers.json` (slices 8–53)

Panels: `number: x,y widthxheight` on the joined 940×84793 strip.

| | | | | |
|---|---|---|---|---|
| 01: 0,0 940x375 | 02: 236,1114 683x1034 | 03: 86,2689 756x480 | 04: 198,3695 700x994 | 05: 90,5482 477x692 |
| 06: 0,6321 940x1816 | 07: 0,8422 940x384 | 08: 87,9126 838x747 | 09: 0,10453 940x1648 | 10: 0,12384 940x955 |
| 11: 0,14095 940x686 | 12: 10,15178 920x541 | 13: 41,16048 860x1098 | 14: 45,17647 790x991 | 15: 31,18810 889x836 |
| 16: 0,19843 940x1483 | 17: 0,21560 940x705 | 18: 0,22341 940x2756 | 19: 0,25349 940x730 | 20: 192,26168 748x364 |
| 21: 0,26715 890x358 | 22: 45,27178 895x551 | 23: 53,27981 830x1302 | 24: 59,29707 672x1025 | 25: 108,31206 800x643 |
| 26: 20,32080 737x365 | 27: 121,32603 788x671 | 28: 40,33616 778x540 | 29: 0,34779 940x1709 | 30: 0,36713 940x819 |
| 31: 0,37644 851x386 | 32: 0,38108 940x828 | 33: 0,39285 940x807 | 34: 46,40514 823x407 | 35: 0,41121 940x864 |
| 36: 0,42122 940x1813 | 37: 0,44509 940x1034 | 38: 96,45888 844x417 | 39: 0,46562 875x445 | 40: 27,47627 882x968 |
| 41: 0,49093 940x2016 | 42: 23,51490 899x710 | 43: 0,52608 940x907 | 44: 0,53884 940x912 | 45: 0,55288 940x776 |
| 46: 0,56197 940x682 | 47: 0,57314 940x1965 | 48: 0,59663 940x703 | 49: 0,61002 940x2898 | 50: 57,64306 832x613 |
| 51: 0,65170 716x193 | 52: 0,65406 940x3569 | 53: 0,69313 940x988 | 54: 0,70784 940x1029 | 55: 50,72237 847x462 |
| 56: 0,72982 940x1871 | 57: 119,75446 782x522 | 58: 0,76212 871x732 | 59: 52,77428 811x531 | 60: 0,78287 940x529 |
| 61: 0,79186 940x541 | 62: 137,79991 761x406 | 63: 0,80670 940x1769 | 64: 121,82826 471x794 | 65: 0,83740 940x1044 |

Bubbles ("in panel" = position relative to that panel's top-left corner, the numbers the site's `bubbles` entries use):

| Bubble | Panel | On strip | Size | In panel | Notes |
|---|---|---|---|---|---|
| bubble_01 | panel_02 | 388,1040 | 362x333 | 152,−74 | "VERY WELL." (in the site) |
| bubble_02 | panel_06 | 535,6820 | 389x323 | 535,499 | "I'LL BE SURE TO GO EASY ON YOU." (in the site) |
| bubble_03 | panel_13 | 408,16070 | 274x189 | 367,22 | "GOING EASY, HUH?" (Arthur) |
| bubble_04 | panel_19 | 102,25179 | 485x359 | 102,−170 | "HE'S NOT USING ANY SPELLS…" (onlooker) |
| bubble_05 | panel_19 | 587,25612 | 83x56 | 587,263 | **an eye: ignore** |
| bubble_06 | panel_19 | 767,25669 | 95x47 | 767,320 | **an eye: ignore** |
| bubble_07 | (attached to panel_21) | 503,26520 | 393x256 | 503,−195 | "WHO DOES HE TAKE ME FOR?!" (Geist) |
| bubble_08 | panel_22 | 86,27498 | 570x380 | 41,320 | "I'M SURE THE DISCIPLINARY COMMITTEE ISN'T MADE ONLY OF RATS WHO KEEP DODGING AND RUNNING AWAY!" (Geist) |
| bubble_09 | (panel_24) | 338,29310 | 567x553 | 279,−397 | "IS THERE REALLY A NEED FOR ME TO ATTACK WHEN OUR ESTEEMED PROFESSOR CAN'T EVEN LAND A SINGLE BLOW ON A FIRST-YEAR STUDENT?" (Arthur) |
| bubble_10 | (panel_25) | 158,31058 | 348x241 | 50,−148 | "F---!" (Geist) |
| bubble_11 | panel_40 | 21,47477 | 894x366 | −6,−150 | "THAT DOESN'T LOOK LIKE A DEMONSTRATION." / "SHOULD WE GET THE STUDENT COUNCIL?" (students; a strip of the wall art) |
| bubble_12 | (panel_48) | 68,60290 | 423x260 | 68,627 | "THIS BRAT GOT FASTER!" (Geist) |
| bubble_13 | (panel_49) | 243,60737 | 440x378 | 243,−265 | "EVEN RATS BECOME DEADLY WHEN CORNERED," (Arthur) |
| bubble_14 | panel_49 | 458,62850 | 454x415 | 458,1848 | "PROFESSOR." (Arthur) |
| bubble_15 | (panel_54) | 39,70499 | 388x414 | 39,−285 | "ARTHUR IS PUSHING PROFESSOR GEIST BACK." (spectator) |
| bubble_16 | panel_56 | 82,72857 | 405x298 | 82,−125 | "ON A TOTALLY DIFFERENT LEVEL." (spectator) |
| bubble_17 | (panel_59) | 379,77217 | 423x260 | 327,−211 | "IT'S TIME TO END THIS." (Arthur) |
| bubble_18 | panel_65 | 103,83980 | 404x341 | 103,240 | "YOU THINK THIS IS ENOUGH?!" (Geist) |

Panel 54's "HE'S…" bubble was not detected, so it stays in that panel's character layer.
