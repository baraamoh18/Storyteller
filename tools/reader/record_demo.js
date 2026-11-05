// Records the public demo as a portrait video, one frame at a time (see HANDOFF.md, "LinkedIn demo").
// Needs: the demo site unzipped and served on :8803, local GSAP and fonts in the folder given as the first argument
// (gsap/package/dist, fonts/fonts.css + fonts/woff). Frames go to <folder>/video/frames; mix the music with ffmpeg after.
// Renders the demo as 1080x1350 frames at 30 fps: the page clock is stepped one frame at a time,
// so animation and scrubbing are exactly as smooth as in a browser, whatever a screenshot costs.
const { chromium } = require("playwright");
const fs = require("fs");
const S = process.argv[2], OUT = S + "/video/frames", FPS = 30, TEST = process.argv[3] === "test", CUES = process.argv[3] === "cues";
(async () => {
  const browser = await chromium.launch({ args: ["--host-resolver-rules=MAP tbate-scroll-demo.pages.dev 127.0.0.1"] });
  const page = await browser.newPage({ viewport: { width: 540, height: 675 }, deviceScaleFactor: 2 });
  await page.route(/cdnjs\.cloudflare\.com.*gsap\.min\.js/, (r) => r.fulfill({ path: S + "/gsap/package/dist/gsap.min.js" }));
  await page.route(/cdnjs\.cloudflare\.com.*ScrollTrigger\.min\.js/, (r) => r.fulfill({ path: S + "/gsap/package/dist/ScrollTrigger.min.js" }));
  await page.route(/fonts\.googleapis\.com/, (r) => r.fulfill({ path: S + "/fonts/fonts.css", contentType: "text/css" }));
  await page.route("http://fonts.local/**", (r) => r.fulfill({ path: S + "/fonts/woff/" + r.request().url().split("/").pop(), contentType: "font/woff2" }));
  await page.clock.install();
  await page.goto("http://tbate-scroll-demo.pages.dev:8803/");
  await page.addStyleTag({ content: ".hud .sound { display: none !important; }" });
  await page.clock.runFor(500);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);
  const plan = await page.evaluate(() => ({
    top: document.getElementById("story").offsetTop, vh: innerHeight, doc: document.documentElement.scrollHeight,
    scenes: SCENES.map((s, i) => [s.id, starts[i], s.length]), total,
  }));
  // seconds per scene: about 110 units a second, slower on the big moments
  const slow = { panel_79: 1.5, panel_87: 1.35, panel_92: 1.25, panel_84: 1.2, panel_76: 0.85, panel_02: 0.8, panel_71: 0.9 };
  const keys = [[0, 0], [2.6, 0]]; // [seconds, scroll y]: the title card first
  let t = 2.6 + 1.6;
  keys.push([t, plan.top]);
  const marks = {};
  for (const [id, start, L] of plan.scenes) {
    marks[id] = t;
    t += (L / 110) * (slow[id] || 1);
    keys.push([t, plan.top + (start + L) * plan.vh / 100]);
  }
  const endY = plan.doc - plan.vh; // the end card
  t += 1.4; keys.push([t, endY]);
  t += 3.4; keys.push([t, endY]);
  const frames = Math.round(t * FPS);
  fs.writeFileSync(S + "/video/marks.json", JSON.stringify({ marks, length: t }));
  const yAt = (s) => { for (let k = 1; k < keys.length; k++) if (s <= keys[k][0]) {
    const [t0, y0] = keys[k - 1], [t1, y1] = keys[k], f = t1 > t0 ? (s - t0) / (t1 - t0) : 1;
    const e = k === 2 || k === keys.length - 2 ? f * f * (3 - 2 * f) : f; // ease into the chapter and into the end card
    return y0 + (y1 - y0) * e; } return keys[keys.length - 1][1]; };
  console.log(`${frames} frames, ${t.toFixed(1)} s; climax at ${marks.panel_70.toFixed(1)} s, calm at ${marks.panel_92.toFixed(1)} s`);
  const pick = TEST ? new Set([60, 200, Math.round(marks.panel_79 * FPS) + 20, Math.round(marks.panel_87 * FPS) + 25, frames - 30]) : null;
  const times = [];
  for (let n = 0; n < frames; n++) {
    await page.evaluate((y) => window.scrollTo(0, y), yAt(n / FPS));
    await page.clock.runFor(1000 / FPS);
    if (CUES) { times.push(await page.evaluate(() => timeline.time())); continue; }
    if (pick && !pick.has(n)) continue;
    if (n % 30 === 0) await page.waitForTimeout(60); // let the images ahead decode
    await page.screenshot({ path: `${OUT}/f${String(n).padStart(5, "0")}.jpg`, type: "jpeg", quality: 93 });
  }
  if (CUES) {
    // when each sound fires: the first frame whose timeline time passes the cue, as sound.update() does on the site
    const cues = await page.evaluate(() => cues.map((c) => ({ time: c.time, sfx: c.sfx })));
    const fired = cues.map((c) => ({ sfx: c.sfx, at: (times.findIndex((x) => x >= c.time) + 1) / FPS })).filter((c) => c.at > 0);
    fs.writeFileSync(S + "/video/cues.json", JSON.stringify(fired, null, 1));
    console.log(fired.length + " sounds: " + fired.map((c) => c.sfx + "@" + c.at.toFixed(2)).join(", "));
  }
  await browser.close();
})();
