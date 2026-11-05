/* The series: its chapters (in reading order) and the music themes every chapter draws from.
   Add a chapter: put its folder in chapters/<id>/ (images + chapter.js) and add a line to `chapters`. */
window.SERIES = {
  title: "The Beginning After the End",
  playlist: "https://open.spotify.com/playlist/7dbe38KmEgww6qeiyGGWHe", // the fans' reading playlist
  // shown on the title and end cards; **bold** marks names
  credit: "**The Beginning After the End**: story by **TurtleMe**, art by **Fuyuki23**, published by Tapas. " +
    "A non-commercial fan tech demo by **Baraa**, built with AI. All rights to the original work belong to its creators.",

  chapters: [
    { id: "094", title: "The Duel", number: 94, panels: 90 },
  ],

  // music themes: each is a list of takes (seamless loops in music/, made with tools/music/).
  // `volume` evens out the takes' loudness. A missing file is skipped quietly.
  themes: {
    calm:        [{ src: "music/calm_1.mp3", volume: 0.5 }],                                              // gentle harp and flute
    tension:     [{ src: "music/tension_1.mp3", volume: 0.4 }],                                           // music box over a slow beat
    battle:      [{ src: "music/battle_1.mp3", volume: 0.53 }, { src: "music/battle_2.mp3", volume: 0.63 }], // driving orchestra
    battle_dark: [{ src: "music/battle_dark_1.mp3", volume: 0.58 }, { src: "music/battle_dark_2.mp3", volume: 0.5 }], // heavy bass, trap drums
    climax:      [{ src: "music/climax_1.mp3", volume: 0.75 }, { src: "music/climax_2.mp3", volume: 0.56 }], // war drums and choir
    // still to make (step 4): sad, eerie, triumph
  },

  // the balance of music and effects: all music plays at `music`, and dips to `dip` of that under each sound effect
  mix: { music: 0.65, dip: 0.5 },

  // auto-scroll: how long it pauses for bubbles and big moments (1 = longer, 0.5 = brisk)
  autoScroll: { pauses: 0.65 },

  // recorded sound effects (in sfx/), used in scene plans like the synthesised ones: sfx: [{ at: 0.3, sound: "deflect" }]
  sounds: {
    deflect: { src: "sfx/deflect.mp3", volume: 1 }, // a quick, bright deflect: a blade turned aside (pitched about 2 notes down)
    parry: { src: "sfx/parry.mp3", volume: 1 },     // a heavier parry with a longer ring: blades meeting with weight (pitched down too)
  },
};
