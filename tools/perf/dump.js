// Dumps what GSAP has written on every animated element at many places along the chapter (forward, backward, jumps),
// to compare two builds of the reader exactly.  node dump.js <port> <out.json>
const { chromium } = require("playwright");
const path = require("path"), fs = require("fs");
const OLD_GSAP = process.env.OLD_GSAP || path.join(__dirname, "../../site/vendor"); // a folder with gsap.min.js + ScrollTrigger.min.js, for a reader from before vendor/
const [port, out] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true })).newPage();
  page.on("pageerror", (e) => console.log("PAGE ERROR", e.message));
  await page.route(/cdnjs\.cloudflare\.com\/.*gsap\/3\.12\.5\/(\w+)\.min\.js/, (r) =>
    r.fulfill({ path: path.join(OLD_GSAP, r.request().url().split("/").pop()), contentType: "text/javascript" }));
  await page.route(/fonts\.(googleapis|gstatic)\.com|cdn\.jsdelivr\.net/, (r) => r.abort());
  await page.goto(`http://localhost:${port}/#094`);
  await page.waitForFunction(() => typeof timeline !== "undefined" && timeline && total > 0);
  await page.waitForTimeout(500);
  const data = await page.evaluate(() => {
    let seed = 7; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
    const times = [];
    for (let t = 0; t <= total; t += 7.3) times.push(t);
    for (let t = total; t >= 0; t -= 11.7) times.push(t);
    for (let k = 0; k < 400; k++) times.push(rnd() * total);
    times.push(0, total, 0);
    const flash = document.querySelector(".flash");
    const snap = () => {
      const o = { flash: flash.style.cssText };
      SCENES.forEach((s) => {
        const p = s.parts, a = [s.el.style.opacity, s.el.style.visibility, p.zoom.style.transform, p.shake.style.transform,
          p.pan.style.getPropertyValue("--pan"), p.rig.style.transform, p.bg.style.transform, p.chars.style.transform,
          ...p.bubbles.map((b) => [b.style.opacity, b.style.visibility, b.style.transform].join("|"))];
        o[s.id] = a.join(";");
      });
      return o;
    };
    const frames = [];
    let prev = snap(); frames.push({ t: -1, d: prev });
    for (const t of times) {
      timeline.time(t);
      const now = snap(), d = {};
      for (const k in now) if (now[k] !== prev[k]) d[k] = now[k];
      frames.push({ t, d }); prev = now;
    }
    return frames;
  });
  fs.writeFileSync(out, JSON.stringify(data));
  console.log(out, data.length, "states");
  await browser.close();
})();
