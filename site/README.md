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
| `bubbles` | speech bubble file, its position and size in the panel's pixels, and when it pops in (0–1) |
| `shakes`, `flashes` | moments (0–1) of a camera shake or a flash |
| `enter`, `exit` | `"cut"`, `"fade"` or `"zoom"`; a zoom exit dives into `focus` (% of the panel) |

People who prefer reduced motion get the panels as a plain column instead.

## Assets

`assets/` holds the layers from the layer splitter, converted to WebP (about 0.8 MB for all ten panels).
The bubbles "GOING EASY, HUH?" and "HE'S NOT USING ANY SPELLS…" sit between panels, so they are not placed yet:
their positions come from the splitter's `layers.json`.
