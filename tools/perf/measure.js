// Plays a chapter on a simulated phone (390x844 @3x, CPU slowed) at a steady scroll and reports where the time goes.
// node measure.js <port> <label> [unitsPerSecond=240] [cpuSlowdown=4] [maxUnits]
const { chromium } = require("playwright");
const path = require("path"), fs = require("fs");
const OLD_GSAP = process.env.OLD_GSAP || __dirname; // a folder with gsap.min.js + ScrollTrigger.min.js, for a reader from before vendor/
const [port, label, ups = "240", slow = "4", maxUnits = "0"] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch({ args: ["--autoplay-policy=no-user-gesture-required"] });
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  const requests = [];
  page.on("request", (r) => requests.push(r.url()));
  page.on("pageerror", (e) => console.log("PAGE ERROR", e.message));
  await page.route(/cdnjs\.cloudflare\.com\/.*gsap\/3\.12\.5\/(\w+)\.min\.js/, (r) =>
    r.fulfill({ path: path.join(OLD_GSAP, r.request().url().split("/").pop()), contentType: "text/javascript" }));
  await page.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
  await page.route(/cdn\.jsdelivr\.net/, (r) => r.abort());
  const cdp = await ctx.newCDPSession(page);
  await cdp.send("Performance.enable");
  await cdp.send("Emulation.setCPUThrottlingRate", { rate: +slow });
  let layers = [];
  cdp.on("LayerTree.layerTreeDidChange", (e) => { if (e.layers) layers = e.layers; });
  await cdp.send("LayerTree.enable");
  const t0 = Date.now();
  await page.goto(`http://localhost:${port}/#094`);
  await page.waitForFunction(() => typeof timeline !== "undefined" && timeline && total > 0);
  const bootMs = Date.now() - t0;
  await page.waitForTimeout(1500);
  const metrics = async () => Object.fromEntries((await cdp.send("Performance.getMetrics")).metrics.map((m) => [m.name, m.value]));
  const before = await metrics();
  await cdp.send("Profiler.enable");
  await cdp.send("Profiler.setSamplingInterval", { interval: 500 });
  await cdp.send("Profiler.start");
  // steady scroll through the story, like auto-scroll without its pauses
  const samples = [];
  const sampler = setInterval(() => {
    const drawn = layers.filter((l) => l.drawsContent);
    samples.push({ n: layers.length, drawn: drawn.length, mpx: drawn.reduce((a, l) => a + l.width * l.height, 0) / 1e6 });
  }, 2000);
  const result = await page.evaluate(([ups, maxUnits]) => new Promise((done) => {
    const story = document.getElementById("story"), top = story.offsetTop, unit = innerHeight / 100;
    const end = maxUnits ? top + maxUnits * unit : document.documentElement.scrollHeight - innerHeight;
    const frames = []; let y = top, last = 0;
    scrollTo(0, y);
    function step(now) {
      if (last) { const dt = now - last; frames.push(dt); y += ups * unit * Math.min(dt, 100) / 1000; }
      last = now;
      scrollTo(0, y);
      if (y >= end) {
        const imgs = [...document.querySelectorAll("#story img")];
        done({ frames, withSrc: imgs.filter((i) => i.getAttribute("src")).length, imgs: imgs.length,
          rendered: [...document.querySelectorAll(".scene")].filter((s) => getComputedStyle(s).display !== "none").length,
          willChange: [...document.querySelectorAll("#story *")].filter((e) => e.offsetParent !== null && getComputedStyle(e).willChange !== "auto").length });
      } else requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }), [+ups, +maxUnits]);
  clearInterval(sampler);
  const { profile } = await cdp.send("Profiler.stop");
  const after = await metrics();
  // self time per function
  const self = {}; const byId = new Map(profile.nodes.map((n) => [n.id, n]));
  const dts = profile.timeDeltas; profile.samples.forEach((id, k) => {
    const n = byId.get(id), f = n.callFrame, name = `${f.functionName || "(anon)"} ${f.url.split("/").pop()}:${f.lineNumber + 1}`;
    self[name] = (self[name] || 0) + (dts[k] || 0) / 1000;
  });
  const top = Object.entries(self).sort((a, b) => b[1] - a[1]).slice(0, 14);
  const f = result.frames.slice().sort((a, b) => a - b), secs = result.frames.reduce((a, b) => a + b, 0) / 1000;
  const d = (k) => after[k] - before[k];
  const out = {
    label, bootMs, seconds: +secs.toFixed(1), frames: f.length, fps: +(f.length / secs).toFixed(1),
    frameMs: { median: +f[f.length >> 1].toFixed(1), p95: +f[Math.floor(f.length * 0.95)].toFixed(1), max: +f[f.length - 1].toFixed(0), over50: f.filter((x) => x > 50).length, over100: f.filter((x) => x > 100).length },
    mainThreadMsPerFrame: { script: +(d("ScriptDuration") * 1000 / f.length).toFixed(2), style: +(d("RecalcStyleDuration") * 1000 / f.length).toFixed(2), layout: +(d("LayoutDuration") * 1000 / f.length).toFixed(2), task: +(d("TaskDuration") * 1000 / f.length).toFixed(2) },
    counts: { layouts: d("LayoutCount"), styleRecalcs: d("RecalcStyleCount"), nodes: after.Nodes, heapMB: +(after.JSHeapUsedSize / 1e6).toFixed(1) },
    atEnd: { imagesHoldingAFile: `${result.withSrc}/${result.imgs}`, scenesInRenderTree: result.rendered, willChangeElementsRendered: result.willChange },
    layers: { count: Math.max(...samples.map((s) => s.n)), drawnMax: Math.max(...samples.map((s) => s.drawn)), megapixelsMax: +Math.max(...samples.map((s) => s.mpx)).toFixed(1), megapixelsAvg: +(samples.reduce((a, s) => a + s.mpx, 0) / samples.length).toFixed(1) },
    requests: { total: requests.length, origins: [...new Set(requests.map((u) => new URL(u).host))] },
    topSelfMs: top.map(([k, v]) => `${v.toFixed(0)} ${k}`),
  };
  fs.writeFileSync(`measure_${label}.json`, JSON.stringify(out, null, 1));
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
})();
