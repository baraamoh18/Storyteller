/* The Duel: 19 scenes cut from chapters/094 with tools/director/cut_chapter.py,
   directed exactly as in the full chapter. Every setting is explained in site/README.md. */
registerChapter({
  id: "094-demo",
  title: "The Duel",
  number: 94,

  music: [
    { theme: "tension", from: "panel_01", to: "panel_07" },
    { theme: "climax", from: "panel_70", to: "panel_89" },
    { theme: "calm", from: "panel_92" },
  ],

  scenes: [

  { id: "panel_01", w: 787, h: 433, length: 190, enter: "fade", exit: "fade",
    camera: { from: { scale: 1.16, x: 5, y: 4 }, to: { scale: 1.02, x: -3, y: -2 } },
    chars: { from: { x: -2 }, to: { x: 2 } },
    flashes: [{ at: 0.5, color: "#e8f8ff", strength: 0.3 }], sfx: [{ at: 0.5, sound: "glint" }],
    fx: { ambient: "embers", tint: "mana", amount: 0.5 } },

  { id: "panel_02", w: 940, h: 1937, length: 320, fit: "pan", enter: "fade", exit: "fade",
    bg: { from: { scale: 1.04 }, to: { scale: 1 } },
    chars: { from: { scale: 0.98 }, to: { scale: 1.03 } },
    fx: { ambient: "dust", tint: "paper", amount: 0.6 } },

  { id: "panel_04", w: 889, h: 575, length: 190, enter: "fade", exit: "fade", origin: [52, 72],
    camera: { from: { scale: 1 }, to: { scale: 1.2 } },
    chars: { from: { y: 2 }, to: { y: -1 } },
    fx: { ambient: "dust", tint: "paper", amount: 0.4 } },  // Kathyln, Sylvie (fox form), Feyrith

  { id: "panel_06", w: 880, h: 952, length: 240, enter: "fade", exit: "fade",
    camera: { from: { scale: 1.1, y: 5 }, to: { scale: 1, y: -2 } },
    chars: { from: { y: 3 }, to: { y: -2 } },
    bubbles: [
      { src: "bubble_02", x: 8, y: -208, w: 421, h: 367, at: 0.1 },
      { src: "bubble_03", x: 390, y: 764, w: 465, h: 412, at: 0.5 }
    ],
    fx: { ambient: "dust", tint: "paper", amount: 0.5 } },

  { id: "panel_07", w: 940, h: 685, length: 190, enter: "fade", exit: "fade",
    camera: { from: { scale: 1.06 }, to: { scale: 1 } },
    bubbles: [{ src: "bubble_04", x: 53, y: 485, w: 416, h: 382, at: 0.35 }],
    fx: { ambient: "dust", tint: "paper", amount: 0.25 } },

  { id: "panel_70", w: 940, h: 541, length: 200, enter: "fade", exit: "fade",
    camera: { from: { scale: 1.12 }, to: { scale: 1 } },
    chars: { from: { scale: 1.05 }, to: { scale: 1 }, over: [0.1, 0.3] },
    shakes: [0.2], flashes: [{ at: 0.18, color: "#f1ece4", strength: 0.45 }], sfx: [{ at: 0.18, sound: "deflect" }],
    fx: { ambient: "embers", tint: "mana", amount: 0.8, bursts: [{ type: "sparks", at: 0.19, from: [44, 30] }] } },  // TING

  { id: "panel_71", w: 761, h: 406, length: 120, enter: "fade", exit: "fade",
    camera: { from: { x: 7 }, to: { x: -6 } },
    chars: { from: { x: 9 }, to: { x: -9 } },
    sfx: [{ at: 0.2, sound: "whoosh" }],
    fx: { ambient: "speed", tint: "paper", amount: 1.2 } },  // DASH

  { id: "panel_72", w: 940, h: 1765, length: 300, fit: "pan", enter: "fade", exit: "fade",
    bg: { from: { scale: 1.05 }, to: { scale: 1 } },
    chars: { from: { scale: 0.96 }, to: { scale: 1.05 } },
    sfx: [{ at: 0.15, sound: "swish" }, { at: 0.42, sound: "gust" }],
    fx: { ambient: "embers", tint: "wind", amount: 1.3 } },

  { id: "panel_74", w: 940, h: 1044, length: 230, enter: "fade", exit: "fade", origin: [48, 62],
    camera: { from: { scale: 1 }, to: { scale: 1.12 } },
    bubbles: [{ src: "bubble_22", x: 103, y: 240, w: 404, h: 341, at: 0.12 }],
    shakes: [0.14], sfx: [{ at: 0.4, sound: "gust" }],
    fx: { ambient: "embers", tint: "wind", amount: 1.1 } },

  { id: "panel_75", w: 848, h: 485, length: 190, enter: "fade", exit: "fade",
    camera: { from: { scale: 1.08 }, to: { scale: 1 } },
    bubbles: [{ src: "bubble_23", x: 498, y: 376, w: 296, h: 148, at: 0.4 }],
    fx: { ambient: "embers", tint: "wind", amount: 0.5 } },

  { id: "panel_76", w: 940, h: 2805, length: 420, fit: "pan", enter: "fade", exit: "fade",
    chars: { from: { scale: 0.98 }, to: { scale: 1.02 } },
    bubbles: [{ src: "bubble_24", x: 271, y: 2300, w: 428, h: 223, at: 0.76, out: 1 }],
    sfx: [{ at: 0.1, sound: "gust" }, { at: 0.5, sound: "whoosh" }],
    fx: { ambient: "embers", tint: "wind", amount: 1.4 } },  // Arthur flips over Geist

  { id: "panel_78", w: 879, h: 375, length: 170, enter: "fade", exit: "zoom", focus: [72, 50], origin: [70, 50],
    camera: { from: { scale: 1.06 }, to: { scale: 1.18 } },
    flashes: [{ at: 0.7, color: "#c8ffe6", strength: 0.35 }], sfx: [{ at: 0.35, sound: "gust" }],
    fx: { ambient: "embers", tint: "wind", amount: 1.3 } },

  { id: "panel_79", w: 940, h: 1538, length: 330, fit: "pan", enter: "zoom", exit: "fade",
    chars: { from: { scale: 1.06 }, to: { scale: 1 }, over: [0.05, 0.3] },
    shakes: [0.13, 0.3], flashes: [{ at: 0.12, color: "#d9ffee", strength: 0.85, hold: 0.04 }],
    sfx: [{ at: 0.12, sound: "gust" }, { at: 0.3, sound: "whoosh" }],
    fx: { ambient: "embers", tint: "wind", amount: 1.7,
      bursts: [{ type: "flare", tint: "wind", at: 0.13, from: [72, 30] }, { type: "ring", at: 0.14, from: [55, 80] }] } },

  { id: "panel_81", w: 940, h: 1456, length: 300, fit: "pan", enter: "fade", exit: "fade",
    bg: { from: { scale: 1.06 }, to: { scale: 1 } },
    shakes: [0.78], flashes: [{ at: 0.76, color: "#c8ffe6", strength: 0.45 }],
    sfx: [{ at: 0.08, sound: "gust" }, { at: 0.38, sound: "swish" }, { at: 0.58, sound: "swish" }, { at: 0.77, sound: "thud" }],
    fx: { ambient: "embers", tint: "wind", amount: 1.5, bursts: [{ type: "ring", at: 0.78, from: [50, 82] }] } },  // the blades rain down

  { id: "panel_84", w: 709, h: 464, length: 200, enter: "fade", exit: "fade",
    camera: { from: { scale: 1.12 }, to: { scale: 1 } },
    shakes: [0.2], flashes: [{ at: 0.19, color: "#f1ece4", strength: 0.35 }], sfx: [{ at: 0.2, sound: "shatter" }],
    fx: { bursts: [{ type: "shatter", at: 0.2, from: [45, 55] }] } },

  { id: "panel_86", w: 940, h: 1039, length: 220, enter: "fade", exit: "fade",
    camera: { from: { scale: 1.1 }, to: { scale: 1 } },
    bubbles: [{ src: "bubble_25", x: 322, y: -127, w: 548, h: 428, at: 0.1 }],
    shakes: [0.32, 0.46], sfx: [{ at: 0.3, sound: "gust" }],
    fx: { ambient: "embers", tint: "wind", amount: 1.2 } },

  { id: "panel_87", w: 940, h: 3828, length: 460, fit: "pan", enter: "fade", exit: "fade",
    chars: { from: { scale: 0.98 }, to: { scale: 1.02 } },
    shakes: [0.07, 0.25, 0.31], flashes: [{ at: 0.24, color: "#ffffff", strength: 1, rise: 0.01, hold: 0.06, fall: 0.12 }],
    sfx: [{ at: 0.06, sound: "shatter" }, { at: 0.24, sound: "crash" }, { at: 0.6, sound: "gust" }],
    fx: { ambient: "embers", tint: "wind", amount: 1.3,
      bursts: [{ type: "shatter", at: 0.06, from: [30, 6] }, { type: "shatter", at: 0.25, from: [50, 30] }] } },

  { id: "panel_89", w: 777, h: 1006, length: 220, enter: "fade", exit: "fade", origin: [50, 40],
    camera: { from: { scale: 1 }, to: { scale: 1.08 } },
    shakes: [0.2], flashes: [{ at: 0.19, color: "#bfe9ff", strength: 0.4 }], sfx: [{ at: 0.18, sound: "crack" }],
    fx: { ambient: "dust", tint: "paper", amount: 0.5, bursts: [{ type: "sparks", at: 0.2, from: [62, 95] }] } },

  { id: "panel_92", w: 940, h: 1872, length: 360, fit: "pan", enter: "fade", exit: "fade",
    bg: { from: { scale: 1.04 }, to: { scale: 1 } },
    chars: { from: { scale: 1.03 }, to: { scale: 1 } },
    bubbles: [{ src: "bubble_26", x: 161, y: 10, w: 450, h: 282, at: 0.06 }],
    fx: { ambient: "dust", tint: "paper", amount: 1 } },

  ],
});
