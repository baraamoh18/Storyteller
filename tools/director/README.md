# Director tools

## draft_chapter.py

Writes a first draft of `site/chapters/<id>/chapter.js` from a chapter zip made by `tools/make-chapter/make_chapter.py`:

```bash
python tools/director/draft_chapter.py chapter_094.zip --out site/chapters/094/chapter.js --title "The Duel"
```

The draft has every non-tiny panel with its size, `fit: "pan"` for panels taller than 1.45× their width, a scroll length that
follows the panel's shape, a gentle push-in, dust, and every bubble on its panel with pop-in times staggered in reading order.
Suspect bubbles (small, maybe an eye) are left out as `// check` comments. Music starts as one `calm` stretch.

`--carry-over OLD/chapter.js --report` keeps an earlier plan's choreography: new and old panels are paired by size (±3 px)
in order (longest common run), then leftover panels in a gap are paired by position and marked `resized … check`.
Bubbles keep their old timing when one sits within 12 px of the old position; others are marked as new.
Old music stretches move to the new panel names.

Tested on chapter 94 against the old 60-panel duel cut (removed in commit `cab2a0a` once 094 was approved; it is still in the git history): all 60 carried over onto panels 10–69 (58 identical, 2 resized), 30 new panels left to direct.

## cut_chapter.py

Cuts a short demo from a directed chapter: the chosen scenes exactly as directed, in a chapter folder of their own, with their
images and bubbles copied next to it (images stay out of git). Used for the public LinkedIn demo:

```
python tools/director/cut_chapter.py site/chapters/094 --id 094-demo --title "The Duel" \
    --panels 01,02,04,06,07,70-72,74-76,78,79,81,84,86,87,89,92 --music "tension:01,climax:70,calm:92"
```

`--music` names the theme that starts at a panel; each plays until the next one starts.
