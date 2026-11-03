/* The Duel: Arthur against Professor Geist at Xyrus Academy (panels 1-60; 61-65 still to come).
   The scene plan for this chapter. Every setting is explained in site/README.md.
   Images live next to this file: panel_XX_background.webp, panel_XX_characters.webp, bubble_*.webp */
registerChapter({
  id: "duel",
  title: "The Duel",
  number: null, // the chapter's number in the series: to confirm

  // music: one theme from series.js per stretch of story. `from` / `to` are the first and last panel
  // (leave `to` out on the last one). A theme used twice plays its next take the second time.
  music: [
    { theme: "tension", from: "panel_01", to: "panel_05" },     // the build-up
    { theme: "battle", from: "panel_06", to: "panel_22" },      // "BURN": the first exchange
    { theme: "battle_dark", from: "panel_23", to: "panel_39" }, // the leaping slash, the flame pillar
    { theme: "battle", from: "panel_40", to: "panel_48" },      // the stands, the counterattack
    { theme: "climax", from: "panel_49" },                      // "Professor." to the final clash
  ],

  scenes: [
    { id: "panel_01", w: 940, h: 375, length: 120, enter: "cut", exit: "fade",
      camera: { from: { scale: 1.14, y: 3 }, to: { scale: 1 } },
      chars: { from: { y: 6 }, to: { y: -3, scale: 1.04 } },
      fx: { ambient: "dust", tint: "paper", amount: 0.6 } },

    { id: "panel_02", w: 683, h: 1034, length: 230, enter: "fade", exit: "zoom", focus: [81, 90],
      camera: { from: { scale: 1.1 }, to: { scale: 1 } },
      bg: { from: { scale: 1.1 }, to: { scale: 1 } },
      chars: { from: { scale: 0.94, y: 4 }, to: { scale: 1.06, y: -2 } },
      bubbles: [{ src: "bubble_very_well", x: 152, y: -74, w: 362, h: 333, at: 0.16 }],
      fx: { ambient: "dust", tint: "paper", amount: 0.7 } },

    { id: "panel_03", w: 756, h: 480, length: 150, enter: "zoom", exit: "fade",
      camera: { from: { scale: 1 }, to: { scale: 1.1 } },
      chars: { from: { scale: 1.25 }, to: { scale: 1 }, over: [0.12, 0.32] },
      shakes: [0.3], sfx: [{ at: 0.3, sound: "crack" }],
      fx: { ambient: "dust", tint: "paper", amount: 0.5, bursts: [{ type: "splinters", at: 0.3, from: [48, 80] }] } },

    { id: "panel_04", w: 700, h: 994, length: 220, enter: "fade", exit: "zoom", focus: [49, 41],
      camera: { from: { y: -6 }, to: { y: 5 } },
      bg: { from: { scale: 1.08 }, to: { scale: 1 } },
      chars: { from: { y: 9 }, to: { y: -5 } },
      sfx: [{ at: 0.12, sound: "whoosh" }],
      fx: { ambient: "dust", tint: "paper", amount: 0.6 } },

    { id: "panel_05", w: 477, h: 692, length: 140, enter: "zoom", exit: "fade",
      camera: { from: { scale: 1.06 }, to: { scale: 1 } },
      bg: { from: { y: -3 }, to: { y: 3, scale: 1.04 } },
      chars: { from: { scale: 1.14 }, to: { scale: 1 }, over: [0.05, 0.25] },
      shakes: [0.12], flashes: [{ at: 0.1, color: "#f1ece4" }], sfx: [{ at: 0.1, sound: "grip" }],
      fx: { ambient: "dust", tint: "paper", amount: 0.4, bursts: [{ type: "ring", at: 0.1, from: [42, 78] }] } },

    { id: "panel_06", w: 940, h: 1816, length: 280, fit: "pan", enter: "fade", exit: "fade",
      chars: { from: { y: 3 }, to: { y: -3 } },
      bubbles: [{ src: "bubble_go_easy", x: 535, y: 499, w: 389, h: 323, at: 0.38 }],
      sfx: [{ at: 0.08, sound: "flame" }],
      fx: { ambient: "embers", tint: "mana", amount: 1.2, bursts: [{ type: "flare", at: 0.08, from: [30, 60] }] } },

    { id: "panel_07", w: 940, h: 384, length: 120, enter: "fade", exit: "fade",
      camera: { from: { x: 8 }, to: { x: -4 } },
      chars: { from: { x: 8 }, to: { x: -8 } },
      sfx: [{ at: 0.25, sound: "swish" }],
      fx: { ambient: "speed", tint: "paper", amount: 1 } },

    { id: "panel_08", w: 838, h: 747, length: 180, enter: "fade", exit: "fade", origin: [46, 32],
      camera: { from: { scale: 1 }, to: { scale: 1.22 } },
      bg: { from: { scale: 1.06 }, to: { scale: 1 } },
      fx: { ambient: "embers", tint: "mana", amount: 0.45 } },

    { id: "panel_09", w: 940, h: 1648, length: 260, fit: "pan", enter: "fade", exit: "fade",
      chars: { from: { scale: 0.97 }, to: { scale: 1.04 } },
      shakes: [0.46], flashes: [{ at: 0.44, color: "#e5202e", strength: 0.55 }], sfx: [{ at: 0.46, sound: "clang" }],
      fx: { ambient: "embers", tint: "mana", amount: 0.8, bursts: [{ type: "sparks", at: 0.46, from: [42, 36] }] } },

    { id: "panel_10", w: 940, h: 955, length: 240, enter: "fade", exit: "zoom", focus: [80, 45],
      bg: { from: { scale: 1.1 }, to: { scale: 1 } },
      chars: { from: { x: 4, scale: 1.06 }, to: { x: 0, scale: 1 } },
      sfx: [{ at: 0.8, sound: "whoosh" }],
      fx: { ambient: "embers", tint: "mana", amount: 0.7 } },

    // ---- the first exchange: slash, skid, "Going easy, huh?"
    { id: "panel_11", w: 940, h: 686, length: 170, enter: "zoom", exit: "fade",
      camera: { from: { scale: 1.12 }, to: { scale: 1 } },
      chars: { from: { x: -5, scale: 1.08 }, to: { x: 2, scale: 1 }, over: [0.05, 0.3] },
      shakes: [0.22], sfx: [{ at: 0.2, sound: "swish" }, { at: 0.24, sound: "clang" }],
      fx: { ambient: "embers", tint: "mana", amount: 0.9, bursts: [{ type: "sparks", at: 0.24, from: [62, 38] }] } },

    { id: "panel_12", w: 920, h: 541, length: 150, enter: "fade", exit: "fade",
      camera: { from: { x: -5 }, to: { x: 4 } },
      chars: { from: { x: -6 }, to: { x: 3 }, over: [0.05, 0.45] },
      sfx: [{ at: 0.18, sound: "skid" }],
      fx: { ambient: "dust", tint: "paper", amount: 0.7, bursts: [{ type: "ring", at: 0.22, from: [72, 92] }] } },

    { id: "panel_13", w: 860, h: 1098, length: 230, enter: "fade", exit: "fade",
      camera: { from: { scale: 1.3, x: 10, y: 11 }, to: { scale: 1.3, x: -9, y: -10 } },
      bubbles: [{ src: "bubble_going_easy_huh", x: 367, y: 22, w: 274, h: 189, at: 0.12 }],
      fx: { ambient: "embers", tint: "mana", amount: 0.6 } },

    { id: "panel_14", w: 790, h: 991, length: 170, enter: "fade", exit: "zoom", focus: [42, 50],
      camera: { from: { scale: 1 }, to: { scale: 1.12 } },
      chars: { from: { scale: 0.96 }, to: { scale: 1.04 } },
      sfx: [{ at: 0.16, sound: "flame" }],
      fx: { ambient: "embers", tint: "mana", amount: 1.4, bursts: [{ type: "flare", at: 0.16, from: [45, 60] }] } },

    { id: "panel_15", w: 889, h: 836, length: 150, enter: "zoom", exit: "fade",
      chars: { from: { x: 8, scale: 1.14 }, to: { x: 0, scale: 1 }, over: [0.04, 0.3] },
      sfx: [{ at: 0.12, sound: "swish" }],
      fx: { ambient: "speed", tint: "mana", amount: 1 } },

    // ---- the onslaught
    { id: "panel_16", w: 940, h: 1483, length: 250, fit: "pan", enter: "fade", exit: "fade",
      chars: { from: { x: 3, scale: 0.97 }, to: { x: -2, scale: 1.03 } },
      shakes: [0.42], sfx: [{ at: 0.38, sound: "swish" }],
      fx: { ambient: "embers", tint: "mana", amount: 1, bursts: [{ type: "sparks", at: 0.42, from: [55, 50] }] } },

    { id: "panel_17", w: 940, h: 705, length: 160, enter: "fade", exit: "fade",
      camera: { from: { scale: 1 }, to: { scale: 1.1 } },
      chars: { from: { x: 4 }, to: { x: -3 } },
      shakes: [0.28], sfx: [{ at: 0.28, sound: "clang" }],
      fx: { ambient: "embers", tint: "mana", amount: 0.8, bursts: [{ type: "sparks", at: 0.28, from: [66, 42] }] } },

    { id: "panel_18", w: 940, h: 2756, length: 320, fit: "pan", enter: "fade", exit: "fade",
      chars: { from: { rotation: -2 }, to: { rotation: 2 } },
      sfx: [{ at: 0.18, sound: "whoosh" }, { at: 0.66, sound: "whoosh" }],
      fx: { ambient: "embers", tint: "mana", amount: 1.1 } },

    { id: "panel_19", w: 940, h: 730, length: 210, enter: "fade", exit: "fade", origin: [62, 55],
      camera: { from: { scale: 1 }, to: { scale: 1.16 } },
      bg: { from: { x: 3 }, to: { x: -3 } },
      bubbles: [{ src: "bubble_not_using_spells", x: 102, y: -170, w: 485, h: 359, at: 0.12 }],
      fx: { ambient: "speed", tint: "paper", amount: 0.6 } },

    { id: "panel_20", w: 748, h: 364, length: 120, enter: "fade", exit: "fade",
      camera: { from: { x: 5 }, to: { x: -4 } },
      sfx: [{ at: 0.3, sound: "tap" }],
      fx: { ambient: "dust", tint: "paper", amount: 0.6, bursts: [{ type: "ring", at: 0.3, from: [56, 88] }] } },

    { id: "panel_21", w: 890, h: 358, length: 170, enter: "fade", exit: "fade",
      chars: { from: { x: -6 }, to: { x: 4 }, over: [0.3, 0.6] },
      bubbles: [{ src: "bubble_07", x: 503, y: -195, w: 393, h: 256, at: 0.08 }],
      sfx: [{ at: 0.36, sound: "whoosh" }],
      fx: { ambient: "speed", tint: "mana", amount: 0.9 } },

    { id: "panel_22", w: 895, h: 551, length: 200, enter: "fade", exit: "fade", origin: [40, 30],
      camera: { from: { scale: 1 }, to: { scale: 1.12 } },
      bg: { from: { x: 4 }, to: { x: -4 } },
      bubbles: [{ src: "bubble_08", x: 41, y: 320, w: 570, h: 380, at: 0.14 }],
      fx: { ambient: "embers", tint: "mana", amount: 0.4 } },

    // ---- the leaping slash
    { id: "panel_23", w: 830, h: 1302, length: 230, fit: "pan", enter: "fade", exit: "fade",
      chars: { from: { y: -4, scale: 1.04 }, to: { y: 2, scale: 1 } },
      shakes: [0.55], sfx: [{ at: 0.3, sound: "swish" }, { at: 0.55, sound: "thud" }],
      fx: { ambient: "embers", tint: "mana", amount: 1.2, bursts: [{ type: "ring", at: 0.55, from: [55, 82] }] } },

    { id: "panel_24", w: 672, h: 1025, length: 210, enter: "fade", exit: "fade", origin: [42, 30],
      camera: { from: { scale: 1 }, to: { scale: 1.12 } },
      bg: { from: { scale: 1.08 }, to: { scale: 1 } },
      bubbles: [{ src: "bubble_09", x: 279, y: -397, w: 567, h: 553, at: 0.12 }],
      fx: { ambient: "embers", tint: "mana", amount: 0.9 } },

    { id: "panel_25", w: 800, h: 643, length: 170, enter: "cut", exit: "fade", origin: [55, 45],
      camera: { from: { scale: 1.08 }, to: { scale: 1.2 } },
      bubbles: [{ src: "bubble_10", x: 50, y: -148, w: 348, h: 241, at: 0.1 }],
      shakes: [0.06],
      fx: { ambient: "embers", tint: "mana", amount: 0.5 } },

    { id: "panel_26", w: 737, h: 365, length: 130, enter: "fade", exit: "fade",
      camera: { from: { scale: 1.1 }, to: { scale: 1 } },
      chars: { from: { scale: 0.92 }, to: { scale: 1.06 } },
      sfx: [{ at: 0.2, sound: "flame" }],
      fx: { ambient: "embers", tint: "mana", amount: 1.6, bursts: [{ type: "flare", at: 0.2, from: [35, 50] }] } },

    { id: "panel_27", w: 788, h: 671, length: 160, enter: "fade", exit: "zoom", focus: [50, 52],
      camera: { from: { rotation: -3, scale: 1.06 }, to: { rotation: 2, scale: 1 } },
      sfx: [{ at: 0.2, sound: "whoosh" }],
      fx: { ambient: "dust", tint: "paper", amount: 0.6 } },

    { id: "panel_28", w: 778, h: 540, length: 160, enter: "zoom", exit: "fade", origin: [68, 42],
      camera: { from: { scale: 1 }, to: { scale: 1.18 } },
      sfx: [{ at: 0.45, sound: "glint" }],
      fx: { ambient: "embers", tint: "mana", amount: 0.3 } },

    // ---- the flame pillar
    { id: "panel_29", w: 940, h: 1709, length: 270, fit: "pan", enter: "fade", exit: "fade",
      bg: { from: { scale: 1.06 }, to: { scale: 1 } },
      chars: { from: { scale: 1.03 }, to: { scale: 0.98 } },
      shakes: [0.2, 0.6], flashes: [{ at: 0.18, color: "#46beff", strength: 0.45 }], sfx: [{ at: 0.16, sound: "flame" }],
      fx: { ambient: "embers", tint: "mana", amount: 1.8, bursts: [{ type: "flare", at: 0.18, from: [45, 30] }, { type: "ring", at: 0.62, from: [42, 88] }] } },

    { id: "panel_30", w: 940, h: 819, length: 150, enter: "fade", exit: "fade",
      camera: { from: { x: -5 }, to: { x: 4 } },
      chars: { from: { x: -8 }, to: { x: 6 } },
      sfx: [{ at: 0.24, sound: "whoosh" }],
      fx: { ambient: "speed", tint: "paper", amount: 1 } },

    { id: "panel_31", w: 851, h: 386, length: 140, enter: "fade", exit: "fade", origin: [52, 55],
      camera: { from: { scale: 1 }, to: { scale: 1.2 } },
      flashes: [{ at: 0.4, color: "#f1ece4", strength: 0.35 }], sfx: [{ at: 0.4, sound: "glint" }] },

    { id: "panel_32", w: 940, h: 828, length: 170, enter: "fade", exit: "fade",
      camera: { from: { scale: 1.1 }, to: { scale: 1 } },
      chars: { from: { rotation: -3 }, to: { rotation: 1 }, over: [0.1, 0.35] },
      shakes: [0.3], sfx: [{ at: 0.3, sound: "clang" }],
      fx: { ambient: "embers", tint: "mana", amount: 1, bursts: [{ type: "sparks", at: 0.3, from: [58, 40] }] } },

    { id: "panel_33", w: 940, h: 807, length: 180, enter: "fade", exit: "fade", origin: [50, 30],
      camera: { from: { scale: 1 }, to: { scale: 1.16 } },
      bg: { from: { scale: 1.08 }, to: { scale: 1 } },
      sfx: [{ at: 0.2, sound: "flame" }],
      fx: { ambient: "embers", tint: "mana", amount: 0.8 } },

    { id: "panel_34", w: 823, h: 407, length: 130, enter: "fade", exit: "fade",
      camera: { from: { scale: 1.08, x: 3 }, to: { scale: 1, x: -2 } },
      sfx: [{ at: 0.28, sound: "tap" }],
      fx: { ambient: "dust", tint: "paper", amount: 0.5, bursts: [{ type: "ring", at: 0.28, from: [52, 70] }] } },

    { id: "panel_35", w: 940, h: 864, length: 180, enter: "fade", exit: "fade",
      camera: { from: { scale: 1.12 }, to: { scale: 1 } },
      chars: { from: { x: -5 }, to: { x: 3 }, over: [0.1, 0.4] },
      shakes: [0.15], flashes: [{ at: 0.14, color: "#46beff", strength: 0.4 }], sfx: [{ at: 0.12, sound: "flame" }],
      fx: { ambient: "embers", tint: "mana", amount: 1.4, bursts: [{ type: "flare", at: 0.14, from: [48, 30] }] } },

    // ---- the leap and the slide
    { id: "panel_36", w: 940, h: 1813, length: 260, fit: "pan", enter: "fade", exit: "fade",
      chars: { from: { y: -3 }, to: { y: 2 } },
      shakes: [0.86], sfx: [{ at: 0.12, sound: "whoosh" }, { at: 0.86, sound: "thud" }],
      fx: { ambient: "embers", tint: "mana", amount: 1.3, bursts: [{ type: "ring", at: 0.86, from: [30, 92] }] } },

    { id: "panel_37", w: 940, h: 1034, length: 190, enter: "fade", exit: "fade",
      camera: { from: { scale: 1.08 }, to: { scale: 1 } },
      chars: { from: { x: 4 }, to: { x: -4 } },
      shakes: [0.32], sfx: [{ at: 0.28, sound: "swish" }, { at: 0.36, sound: "skid" }],
      fx: { ambient: "embers", tint: "mana", amount: 1, bursts: [{ type: "ring", at: 0.36, from: [70, 88] }] } },

    { id: "panel_38", w: 844, h: 417, length: 140, enter: "fade", exit: "fade", origin: [42, 50],
      camera: { from: { scale: 1 }, to: { scale: 1.16 } },
      fx: { ambient: "embers", tint: "mana", amount: 0.6 } },

    { id: "panel_39", w: 875, h: 445, length: 140, enter: "cut", exit: "fade", origin: [38, 45],
      camera: { from: { scale: 1.04 }, to: { scale: 1.18 } },
      shakes: [0.05],
      fx: { ambient: "embers", tint: "mana", amount: 0.6 } },

    // ---- the stands
    { id: "panel_40", w: 882, h: 968, length: 200, enter: "fade", exit: "fade",
      camera: { from: { scale: 1.06 }, to: { scale: 1 } },
      bg: { from: { scale: 1.06, y: 2 }, to: { scale: 1, y: -2 } },
      bubbles: [{ src: "bubble_11", x: -6, y: -150, w: 894, h: 366, at: 0, pop: false }],
      fx: { ambient: "dust", tint: "paper", amount: 0.5 } },

    // ---- the counterattack
    { id: "panel_41", w: 940, h: 2016, length: 290, fit: "pan", enter: "fade", exit: "fade",
      chars: { from: { x: -2 }, to: { x: 2 } },
      sfx: [{ at: 0.12, sound: "flame" }, { at: 0.28, sound: "whoosh" }, { at: 0.44, sound: "whoosh" }, { at: 0.86, sound: "tap" }],
      fx: { ambient: "embers", tint: "mana", amount: 1.6, bursts: [{ type: "ring", at: 0.86, from: [30, 94] }] } },

    { id: "panel_42", w: 899, h: 710, length: 160, enter: "fade", exit: "fade",
      camera: { from: { scale: 1.1, rotation: -2 }, to: { scale: 1, rotation: 0 } },
      shakes: [0.26], sfx: [{ at: 0.26, sound: "clang" }],
      fx: { ambient: "embers", tint: "mana", amount: 0.9, bursts: [{ type: "sparks", at: 0.26, from: [56, 48] }] } },

    { id: "panel_43", w: 940, h: 907, length: 170, enter: "fade", exit: "cut",
      camera: { from: { scale: 1.06 }, to: { scale: 1 } },
      chars: { from: { scale: 1.06 }, to: { scale: 1 } },
      sfx: [{ at: 0.2, sound: "skid" }],
      fx: { ambient: "embers", tint: "mana", amount: 0.8, bursts: [{ type: "ring", at: 0.22, from: [76, 82] }] } },

    { id: "panel_44", w: 940, h: 912, length: 160, enter: "cut", exit: "fade",
      chars: { from: { x: 4, scale: 1.04 }, to: { x: -2, scale: 1 }, over: [0, 0.35] },
      sfx: [{ at: 0.06, sound: "whoosh" }],
      fx: { ambient: "speed", tint: "mana", amount: 0.8 } },

    { id: "panel_45", w: 940, h: 776, length: 150, enter: "fade", exit: "fade",
      camera: { from: { x: 4 }, to: { x: -4 } },
      chars: { from: { x: 8 }, to: { x: -6 } },
      sfx: [{ at: 0.25, sound: "swish" }],
      fx: { ambient: "speed", tint: "paper", amount: 1 } },

    { id: "panel_46", w: 940, h: 682, length: 150, enter: "cut", exit: "fade",
      camera: { from: { scale: 1.12 }, to: { scale: 1 } },
      shakes: [0.16], flashes: [{ at: 0.14, color: "#e5202e", strength: 0.4 }], sfx: [{ at: 0.14, sound: "clang" }],
      fx: { ambient: "speed", tint: "paper", amount: 0.6, bursts: [{ type: "sparks", at: 0.16, from: [40, 72] }] } },

    { id: "panel_47", w: 940, h: 1965, length: 280, fit: "pan", enter: "fade", exit: "fade",
      sfx: [{ at: 0.1, sound: "swish" }, { at: 0.42, sound: "tap" }, { at: 0.56, sound: "tap" }, { at: 0.68, sound: "tap" }],
      fx: { ambient: "dust", tint: "paper", amount: 0.8, bursts: [{ type: "ring", at: 0.7, from: [50, 80] }] } },

    { id: "panel_48", w: 940, h: 703, length: 170, enter: "fade", exit: "fade", origin: [45, 40],
      camera: { from: { scale: 1 }, to: { scale: 1.12 } },
      bubbles: [{ src: "bubble_12", x: 68, y: 627, w: 423, h: 260, at: 0.3 }],
      shakes: [0.1],
      fx: { ambient: "embers", tint: "mana", amount: 0.7 } },

    // ---- "Professor."
    { id: "panel_49", w: 940, h: 2898, length: 320, fit: "pan", enter: "fade", exit: "fade",
      bg: { from: { scale: 1.04 }, to: { scale: 1 } },
      chars: { from: { scale: 0.98 }, to: { scale: 1.02 } },
      bubbles: [{ src: "bubble_13", x: 243, y: -265, w: 440, h: 378, at: 0.05 },
                { src: "bubble_14", x: 458, y: 1848, w: 454, h: 415, at: 0.6 }],
      fx: { ambient: "dust", tint: "paper", amount: 0.5 } },

    { id: "panel_50", w: 832, h: 613, length: 160, enter: "fade", exit: "fade", origin: [50, 45],
      camera: { from: { scale: 1 }, to: { scale: 1.14 } },
      fx: { ambient: "embers", tint: "ember", amount: 0.7 } },

    // ---- the clash
    { id: "panel_51", w: 716, h: 193, length: 110, enter: "fade", exit: "fade",
      camera: { from: { x: 6 }, to: { x: -6 } },
      sfx: [{ at: 0.25, sound: "swish" }],
      fx: { ambient: "speed", tint: "paper", amount: 1 } },

    { id: "panel_52", w: 940, h: 3569, length: 380, fit: "pan", enter: "fade", exit: "fade",
      chars: { from: { scale: 0.98 }, to: { scale: 1.02 } },
      shakes: [0.74], flashes: [{ at: 0.72, color: "#f1ece4", strength: 0.6 }],
      sfx: [{ at: 0.08, sound: "whoosh" }, { at: 0.36, sound: "swish" }, { at: 0.72, sound: "clang" }],
      fx: { ambient: "embers", tint: "mana", amount: 1.4, bursts: [{ type: "sparks", at: 0.73, from: [50, 70] }] } },

    { id: "panel_53", w: 940, h: 988, length: 190, enter: "fade", exit: "fade",
      camera: { from: { scale: 1.1 }, to: { scale: 1 } },
      chars: { from: { x: 3 }, to: { x: -3 } },
      shakes: [0.16], sfx: [{ at: 0.14, sound: "thud" }],
      fx: { ambient: "embers", tint: "mana", amount: 1, bursts: [{ type: "ring", at: 0.16, from: [40, 78] }] } },

    { id: "panel_54", w: 940, h: 1029, length: 200, enter: "fade", exit: "fade", origin: [62, 30],
      camera: { from: { scale: 1 }, to: { scale: 1.1 } },
      bubbles: [{ src: "bubble_15", x: 39, y: -285, w: 388, h: 414, at: 0.1 }],
      fx: { ambient: "dust", tint: "paper", amount: 0.4 } },

    { id: "panel_55", w: 847, h: 462, length: 140, enter: "fade", exit: "fade", origin: [40, 45],
      camera: { from: { scale: 1 }, to: { scale: 1.14 } },
      fx: { ambient: "speed", tint: "paper", amount: 0.5 } },

    // ---- "a totally different level"
    { id: "panel_56", w: 940, h: 1871, length: 280, fit: "pan", enter: "fade", exit: "fade",
      chars: { from: { scale: 0.97 }, to: { scale: 1.03 } },
      bubbles: [{ src: "bubble_16", x: 82, y: -125, w: 405, h: 298, at: 0.06 }],
      sfx: [{ at: 0.3, sound: "flame" }],
      fx: { ambient: "embers", tint: "mana", amount: 1.4, bursts: [{ type: "flare", at: 0.3, from: [35, 30] }] } },

    { id: "panel_57", w: 782, h: 522, length: 150, enter: "fade", exit: "zoom", focus: [58, 55],
      camera: { from: { scale: 1 }, to: { scale: 1.1 } },
      sfx: [{ at: 0.35, sound: "glint" }],
      flashes: [{ at: 0.35, color: "#f1ece4", strength: 0.3 }] },

    { id: "panel_58", w: 871, h: 732, length: 150, enter: "zoom", exit: "fade",
      camera: { from: { scale: 1.08 }, to: { scale: 1 } },
      fx: { ambient: "embers", tint: "mana", amount: 0.5 } },

    { id: "panel_59", w: 811, h: 531, length: 170, enter: "fade", exit: "fade", origin: [50, 60],
      camera: { from: { scale: 1 }, to: { scale: 1.14 } },
      bubbles: [{ src: "bubble_17", x: 327, y: -211, w: 423, h: 260, at: 0.1 }] },

    { id: "panel_60", w: 940, h: 529, length: 220, enter: "fade", exit: "fade",
      camera: { from: { scale: 1.14 }, to: { scale: 1 }, },
      chars: { from: { scale: 1.06 }, to: { scale: 1 }, over: [0.1, 0.3] },
      shakes: [0.2], flashes: [{ at: 0.18, color: "#f1ece4", strength: 0.55 }], sfx: [{ at: 0.18, sound: "clang" }],
      fx: { ambient: "embers", tint: "mana", amount: 0.9, bursts: [{ type: "sparks", at: 0.2, from: [76, 42] }] } },
  ],
});
