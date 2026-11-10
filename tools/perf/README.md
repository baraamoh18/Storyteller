# Reader checks: speed, and "nothing changed"

Run these after changing `site/index.html`. They need node with Playwright and Chromium, plus numpy and Pillow for the
stand-in pictures. The numbers come from a computer with no graphics card, so they compare one version of the reader
with another; they are not a real phone's numbers.

```bash
python tools/perf/make_test_site.py /tmp/reader-new                      # this project's reader, with stand-in pictures
python3 -m http.server 8772 --directory /tmp/reader-new &
```

To compare with an older reader, check it out somewhere (`git worktree add /tmp/old <commit>`), make a second copy with
`--site /tmp/old/site` and serve it on another port. A reader from before `vendor/` existed asks cdnjs for GSAP: set
`OLD_GSAP` to a folder holding `gsap.min.js` and `ScrollTrigger.min.js` (from `npm pack gsap@3.12.5`).

| Script | What it tells you |
|---|---|
| `node measure.js PORT LABEL [units/s=240] [slowdown=4]` | Plays chapter 094 on a simulated phone (390 x 844 at 3x, processor slowed) at a steady scroll: pictures a second, frame times, main-thread work per frame (script, styles, layout), how many panels are in the drawing, which servers were asked, and the functions that took the most time. |
| `node trace.js PORT LABEL [fromUnit=0] [units=2500]` | The same for a stretch, from Chrome's own trace: paint, layer updates, canvas uploads and redrawn tiles per frame. `CSS='.frame{box-shadow:none}' node trace.js ...` tries a style change without editing the page: this is how the outline that was redrawn on every frame was found. |
| `node dump.js PORT out.json` then `node compare.js a.json b.json` | Every animated element's state (what GSAP wrote on it) at 4,505 places: forward, backward and 400 random jumps. Two readers that animate the same give "identical". Values that sit on a rounding edge can differ by 0.0001. |
| `node func.js PORT` | Pass / fail: only the playing panel and its neighbours are drawn (also after big jumps), auto-scroll runs and a wheel pauses it, turning the phone re-lays the panels out, the music loads the reader's stretch first and dips under effects, reduced motion gives the plain column, a folder without `vendor/` falls back to the web, with `vendor/` no other server is asked, the demo chapter and the end card. Needs a test copy made with `--chapters 094 094-demo`. |
| `node memory.js PORT LABEL` | Memory of the browser's page and drawing processes over a whole read. Run it alone: it adds up every Chromium process on the machine. |
