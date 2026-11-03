# Scroll site: the series reader

A scrollytelling reader for *The Beginning After the End*, built with GSAP and ScrollTrigger.
The page shows a chapter menu on its title card; each chapter plays as one long scroll-scrubbed scene.

## Look at it

Open `index.html` through a local web server: run `python -m http.server` in this folder and open <http://localhost:8000>.
(Double-clicking the file shows the panels, but browsers block the music when a page is opened as a file.)
It needs an internet connection for GSAP and the fonts. `index.html#duel` opens the chapter with the id `duel`.

## Layout

```
index.html                 the reader: chapter menu, stage, particles, sound (no chapter data in here)
series.js                  the series: title, chapter list in reading order, music themes
chapters/<id>/chapter.js   one chapter's scene plan and music
chapters/<id>/*.webp       its layers: panel_XX_background, panel_XX_characters, bubble_*
music/<theme>_<n>.mp3      the shared music library: seamless loops, made with tools/music/
```

## Add a chapter

1. Put its folder in `chapters/<id>/`: the WebP layers plus a `chapter.js` that calls `registerChapter({ id, title, number, music, scenes })`.
2. Add a line to `chapters` in `series.js`: `{ id, title, number, panels }`.

## The scene plan (`scenes` in chapter.js)

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

## Music

A chapter's `music` list names a **theme** for each stretch of panels: `{ theme: "battle", from: "panel_06", to: "panel_22" }`
(leave `to` out on the last one). The themes and their takes live in `series.js` under `themes`; each take is a seamless loop
in `music/` with a `volume` that evens out loudness. When a chapter uses a theme a second time, it plays the theme's next take;
`take: 0` picks one by hand. Neighbouring stretches crossfade.

| Theme | Takes | Sound |
| --- | --- | --- |
| `calm` | 1 | gentle harp and flute |
| `tension` | 1 | music box over a slow beat |
| `battle` | 2 | driving orchestra |
| `battle_dark` | 2 | heavy bass, trap drums |
| `climax` | 2 | war drums and choir |

Planned: `sad`, `eerie`, `triumph`. Make takes with `tools/music/Make_Duel_Music.ipynb`, then loop them with `tools/music/make_loop.py`.

## Sound

Off until the reader presses **Play with sound** (browsers block sound before a tap).
Sound effects are made in the browser by code, so they need no files. They play as their moment passes while scrolling forward, not when rewinding.
Voices are switched off for now; `tools/voices/make_voices.py` still makes the lines, and the playback code is in the git history (commit `77414a1`).

People who prefer reduced motion get the panels as a plain column instead.

## Assets

Backgrounds are WebP at quality 80, characters at 85, bubbles at 90 (`method=6`), about 6 MB per chapter.
Each panel's images only load when the reader gets close, and its particle canvas only exists while it is on screen.
`chapters/duel/bubble_18.webp` (panel 65) is ready for when the last panels of that chapter come in.
