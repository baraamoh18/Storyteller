# Scroll site

The scrollytelling page for the duel scene (panels 1–10), built with GSAP and ScrollTrigger.

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
| `bubbles` | speech bubble file, its position and size in the panel's pixels, when it pops in (0–1), and the `voice` line that plays then |
| `shakes`, `flashes` | moments (0–1) of a camera shake or a flash (with its colour and strength) |
| `sfx` | sound effects at moments (0–1): `crack`, `whoosh`, `grip`, `flame`, `swish`, `clang` |
| `fx` | particles: `ambient` `"dust"`, `"embers"` or `"speed"` in a `tint` (`"paper"`, `"mana"`, `"ember"`) and `amount`, plus impact `bursts` (`"splinters"`, `"sparks"`, `"ring"`, `"flare"`) at a moment, coming `from` a point (% of the panel) |
| `enter`, `exit` | `"cut"`, `"fade"` or `"zoom"`; a zoom exit dives into `focus` (% of the panel) |

People who prefer reduced motion get the panels as a plain column instead.

## Sound

Off until the reader presses **Play with sound** (browsers block sound before a tap).

- **Sound effects** are made in the browser by code, so they need no files. They play as their moment passes while scrolling forward, not when rewinding.
- **Voices**: `assets/audio/voice_<name>.mp3`, made with `tools/voices/make_voices.py` (Kokoro, free). The music dips while a line plays.
- **Music**: `assets/audio/fight.mp3`, looped from the panel named in `MUSIC.from` to the end, fading in and out with the scroll.
  Make one with `tools/music/Make_Fight_Music.ipynb` on Colab, or use any free-to-use track. Until the file is there the page simply has no music.

## Assets

`assets/` holds the layers from the layer splitter, converted to WebP (about 0.8 MB for all ten panels).
The bubbles "GOING EASY, HUH?" (panel 13) and "HE'S NOT USING ANY SPELLS…" (panel 19) and their voice lines are ready
for when those panels are added.
