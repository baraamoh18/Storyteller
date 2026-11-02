# Scroll site

The scrollytelling page for the duel scene (panels 1–60), built with GSAP and ScrollTrigger.

## Look at it

Double-click `index.html`. It needs an internet connection for GSAP and the fonts.
If your browser blocks the images when opened as a file, run `python -m http.server` in this folder and open <http://localhost:8000>.

## Change the choreography

Everything the camera does is in the `SCENES` list near the top of the `<script>` in `index.html`.
Each panel has:

| Setting | What it does |
| --- | --- |
| `length` | how long you scroll through the panel (100 = one screen height) |
| `fit` | `"pan"` fills the width and pans down a tall panel; otherwise the whole panel shows |
| `camera` | moves the whole panel: `scale`, and `x` / `y` in % of the panel |
| `bg`, `chars` | move the background and characters separately for depth; `over: [start, end]` squeezes the move into part of the scroll |
| `bubbles` | speech bubble file, its position and size in the panel's pixels, and when it pops in (0–1); `pop: false` fades it in where it sits (for lettering drawn on the art). Bubbles are nudged back on screen if they hang off it |
| `shakes`, `flashes` | moments (0–1) of a camera shake or a flash (with its colour and strength) |
| `sfx` | sound effects at moments (0–1): `crack`, `whoosh`, `grip`, `flame`, `swish`, `clang`, `skid`, `tap`, `thud`, `glint` |
| `fx` | particles: `ambient` `"dust"`, `"embers"` or `"speed"` in a `tint` (`"paper"`, `"mana"`, `"ember"`) and `amount`, plus impact `bursts` (`"splinters"`, `"sparks"`, `"ring"`, `"flare"`) at a moment, coming `from` a point (% of the panel) |
| `enter`, `exit` | `"cut"`, `"fade"` or `"zoom"`; a zoom exit dives into `focus` (% of the panel) |

People who prefer reduced motion get the panels as a plain column instead.

## Sound

Off until the reader presses **Play with sound** (browsers block sound before a tap).

- **Sound effects** are made in the browser by code, so they need no files. They play as their moment passes while scrolling forward, not when rewinding.
- **Music**: the `MUSIC` list under the scene plan. Each track loops over its stretch of panels (`from` to `to`) and crossfades into the next:
  `academy_dark` (panels 1–5), `fight_orchestral_1` (6–22), `fight_dark` (23–39), `fight_orchestral_2` (40–48), `fight_choir` (49 on),
  all in `assets/audio/`. They were made with `tools/music/Make_Duel_Music.ipynb` and turned into seamless, evenly loud loops with
  `tools/music/make_loop.py`; spare takes are in `tools/music/takes/`. A missing file is skipped quietly.
- **Voices** are switched off for now. `tools/voices/make_voices.py` still makes the lines; the playback code is in the git history
  (commit `77414a1`) for when they come back.

## Assets

`assets/` holds the layers from the layer splitter, converted to WebP (about 6 MB for all sixty panels):
backgrounds at quality 80, characters at 85, bubbles at 90. Each panel's images only load when the reader gets close,
and its particle canvas only exists while it is on screen, so the long page stays light on phones.
`bubble_18.webp` (panel 65) is ready for when the last panels come in.
