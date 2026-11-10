// Functional checks of the new reader on a simulated phone.  node func.js <port>
const { chromium } = require("playwright");
const path = require("path");
const OLD_GSAP = process.env.OLD_GSAP || __dirname; // a folder with gsap.min.js + ScrollTrigger.min.js, for a reader from before vendor/
const port = process.argv[2];
const ok = (c, m) => console.log((c ? "PASS  " : "FAIL  ") + m);
async function open(browser, opts = {}, hash = "#094", prep) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, ...opts });
  const page = await ctx.newPage();
  page.errors = []; page.reqs = [];
  page.on("pageerror", (e) => page.errors.push(e.message));
  page.on("request", (r) => page.reqs.push(r.url()));
  if (prep) await prep(page);
  await page.goto(`http://localhost:${port}/${hash}`);
  return page;
}
const ready = (page) => page.waitForFunction(() => typeof timeline !== "undefined" && timeline && total > 0);
(async () => {
  const browser = await chromium.launch({ args: ["--autoplay-policy=no-user-gesture-required"] });

  // 1. the window of panels: only the playing one and its neighbours are drawn, and every showing panel is among them
  let page = await open(browser); await ready(page);
  const windowCheck = () => page.evaluate(() => {
    const now = timeline.time(), i = starts.findLastIndex((s) => s <= now);
    const shown = SCENES.map((s, j) => (getComputedStyle(s.el).display !== "none" ? j : -1)).filter((j) => j >= 0);
    const visible = SCENES.map((s, j) => (+s.el.style.opacity > 0.001 ? j : -1)).filter((j) => j >= 0);
    return { i, shown, visible, good: shown.every((j) => Math.abs(j - i) <= 1) && visible.every((j) => shown.includes(j)) && shown.includes(i) };
  });
  let all = true, detail = "";
  for (const u of [0, 300, 2210, 9000, 18300, 12000, 40, 15480, 0]) {
    await page.evaluate((u) => scrollTo(0, document.getElementById("story").offsetTop + u * innerHeight / 100), u);
    for (let k = 0; k < 6; k++) { await page.waitForTimeout(250); const r = await windowCheck(); if (!r.good) { all = false; detail = JSON.stringify(r); } }
  }
  ok(all, "only the playing panel and its neighbours are drawn, at 9 places incl. big jumps back and forth " + detail);
  const mem = await page.evaluate(() => ({ drawn: document.querySelectorAll(".scene:not(.away)").length, total: SCENES.length }));
  ok(mem.drawn <= 3, `panels in the drawing: ${mem.drawn} of ${mem.total}`);

  // 2. auto-scroll: it moves, pauses at a bubble, and its idea of the place matches the timeline's
  await page.evaluate(() => { const i = SCENES.findIndex((s) => (s.bubbles || []).length); scrollTo(0, scroller.start + (starts[i] - 150) * (scroller.end - scroller.start) / total); });
  await page.waitForTimeout(1200);
  await page.click(".hud .auto-toggle");
  const samples = [];
  for (let k = 0; k < 110; k++) { await page.waitForTimeout(100); samples.push(await page.evaluate(() => [scrollY, timeline.time(), (scrollY - scroller.start) / ((scroller.end - scroller.start) / total)])); }
  const speeds = samples.slice(1).map((s, k) => (s[0] - samples[k][0]) / 0.1);
  const moving = speeds.filter((v) => v > 300).length, crawling = speeds.filter((v) => v >= 0 && v < 60).length;
  ok(moving > 20 && crawling > 5, `auto-scroll moves (${moving} samples) and pauses (${crawling} samples) in 11 s from just before the first bubble`);
  const lag = samples.slice(-20).map((s) => s[2] - s[1]);
  ok(lag.every((d) => d > -2 && d < 60), `auto-scroll's place stays just ahead of the picture (by ${Math.min(...lag).toFixed(0)} to ${Math.max(...lag).toFixed(0)} units; the picture trails the scroll by design)`);
  ok(await page.evaluate(() => document.querySelector(".auto-toggle").getAttribute("aria-pressed")) === "true", "auto-scroll still playing after 11 s");
  await page.mouse.wheel(0, 50); await page.waitForTimeout(200);
  ok(await page.evaluate(() => document.querySelector(".auto-toggle").getAttribute("aria-pressed")) === "false", "a wheel pauses auto-scroll");

  // 3. rotation re-lays the stage out; a height-only change of the window (address bar) does not
  const before = await page.evaluate(() => SCENES[1].boxW);
  await page.evaluate(() => { window.__refreshes = 0; ScrollTrigger.addEventListener("refresh", () => window.__refreshes++); });
  await page.setViewportSize({ width: 844, height: 390 }); await page.waitForTimeout(700);
  const after = await page.evaluate(() => [SCENES[1].boxW, window.__refreshes]);
  ok(after[0] !== before && after[1] >= 1, `turning the phone re-lays the panels out (panel 2: ${before.toFixed(0)} px -> ${after[0].toFixed(0)} px wide)`);
  ok(page.errors.length === 0, "no script errors so far " + page.errors.join(" | "));
  await page.context().close();

  // 4. sound: effects ready first, music one track at a time starting with the reader's place; music dips under an effect
  page = await open(browser, {}, "#094", async (p) => p.addInitScript(() => {
    window.__dips = []; const orig = AudioParam.prototype.setTargetAtTime;
    AudioParam.prototype.setTargetAtTime = function (v, t, c) { window.__dips.push([+v.toFixed(3), +c.toFixed(3)]); return orig.call(this, v, t, c); };
  }));
  await ready(page);
  await page.evaluate(() => scrollTo(0, document.getElementById("story").offsetTop + 9000 * innerHeight / 100)); await page.waitForTimeout(1200);
  page.reqs.length = 0;
  await page.click(".hud [data-sound]");
  await page.waitForTimeout(4000);
  const music = page.reqs.filter((u) => /music\//.test(u)).map((u) => u.split("/").pop());
  const expectFirst = await page.evaluate(() => { const now = timeline.time(); const k = MUSIC.findIndex((m) => { const a = SCENES.findIndex((s) => s.id === m.from), z = m.to ? SCENES.findIndex((s) => s.id === m.to) : SCENES.length - 1; return starts[a] <= now && now < (starts[z + 1] ?? total); }); return MUSIC[k].src.split("/").pop(); });
  ok(music[0] === expectFirst && music.length === 6, `music loads the reader's stretch first (${music[0]}), then the rest in turn: ${music.join(", ")}`);
  await page.evaluate(() => { window.__dips.length = 0; });
  await page.evaluate(() => new Promise((done) => { const top = document.getElementById("story").offsetTop, unit = innerHeight / 100; let y = scrollY, n = 0; (function step() { y += 3 * unit; scrollTo(0, y); ++n < 240 ? requestAnimationFrame(step) : done(); })(); }));
  await page.waitForTimeout(500);
  const dips = await page.evaluate(() => window.__dips);
  ok(dips.some((d) => Math.abs(d[0] - 0.325) < 0.001 && d[1] === 0.015) && dips.some((d) => d[0] === 0.65 && d[1] === 0.25), `effects fire while scrolling and the music dips under them (${dips.filter((d) => d[1] === 0.015).length} dips)`);
  ok(page.errors.length === 0, "no script errors with sound " + page.errors.join(" | "));
  await page.context().close();

  // 5. reduced motion: the plain column, every panel there, none switched off
  page = await open(browser, { reducedMotion: "reduce" });
  await page.waitForFunction(() => document.documentElement.classList.contains("static"));
  const st = await page.evaluate(() => ({ away: document.querySelectorAll(".scene.away").length, imgs: document.querySelectorAll("#story img[src]").length, scenes: document.querySelectorAll(".scene").length }));
  ok(st.away === 0 && st.scenes === 90 && st.imgs === 206, `reduced motion: ${st.scenes} panels in a column, ${st.imgs} pictures, none switched off`);
  await page.context().close();

  // 6. a reader folder with no vendor/ (only the page updated): library and fonts come from the web instead
  page = await open(browser, {}, "#094", async (p) => {
    await p.route(/\/vendor\//, (r) => r.fulfill({ status: 404, body: "" }));
    await p.route(/cdnjs\.cloudflare\.com\/.*gsap\/3\.12\.5\/(\w+)\.min\.js/, (r) => r.fulfill({ path: path.join(OLD_GSAP, r.request().url().split("/").pop()), contentType: "text/javascript" }));
    await p.route(/fonts\.googleapis\.com/, (r) => r.fulfill({ contentType: "text/css", body: "/* stand-in */" }));
  });
  await ready(page); await page.waitForTimeout(600);
  ok(page.reqs.some((u) => u.includes("cdnjs.cloudflare.com")) && page.reqs.some((u) => u.includes("fonts.googleapis.com")) && page.errors.length === 0,
    "without vendor/: GSAP is taken from cdnjs and the fonts from Google Fonts, and the chapter still builds");
  await page.context().close();

  // 7. with vendor/: nothing is asked of any other server, and the real fonts are in use
  page = await open(browser); await ready(page); await page.waitForTimeout(800);
  const hosts = [...new Set(page.reqs.map((u) => new URL(u).host))];
  const fonts = await page.evaluate(() => ["Bangers", "Archivo Narrow", "IBM Plex Mono"].map((f) => document.fonts.check(`16px "${f}"`)));
  ok(hosts.length === 1 && fonts.every(Boolean), `with vendor/: every request goes to ${hosts.join(", ")}; fonts loaded: ${fonts.join(", ")}`);
  await page.context().close();

  // 8. the demo chapter, and the end card buttons
  page = await open(browser, {}, "#094-demo"); await ready(page);
  const demo = await page.evaluate(() => ({ n: SCENES.length, total }));
  await page.evaluate(() => scrollTo(0, document.documentElement.scrollHeight)); await page.waitForTimeout(1200);
  await page.click(".to-menu"); await page.waitForTimeout(1500);
  const back = await page.evaluate(() => ({ y: scrollY, first: !SCENES[0].away, t: timeline.time() }));
  ok(demo.n === 19 && back.y === 0 && back.first && back.t < 1 && page.errors.length === 0, `demo chapter: ${demo.n} scenes, ${demo.total} units; "All chapters" returns to the top with panel 1 ready`);
  await browser.close();
})();
