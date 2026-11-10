// Which kinds of work fill the main thread while scrolling a stretch of the chapter (Chrome trace, CPU slowed 4x).
// node trace.js <port> <label> [fromUnit=0] [units=2500]
const { chromium } = require("playwright");
const path = require("path"), fs = require("fs");
const OLD_GSAP = process.env.OLD_GSAP || path.join(__dirname, "../../site/vendor"); // a folder with gsap.min.js + ScrollTrigger.min.js, for a reader from before vendor/
const [port, label, from = "0", units = "2500"] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  await page.route(/cdnjs\.cloudflare\.com\/.*gsap\/3\.12\.5\/(\w+)\.min\.js/, (r) =>
    r.fulfill({ path: path.join(OLD_GSAP, r.request().url().split("/").pop()), contentType: "text/javascript" }));
  await page.route(/fonts\.(googleapis|gstatic)\.com|cdn\.jsdelivr\.net/, (r) => r.abort());
  const cdp = await ctx.newCDPSession(page);
  await cdp.send("Emulation.setCPUThrottlingRate", { rate: 4 });
  await page.goto(`http://localhost:${port}/#094`);
  await page.waitForFunction(() => typeof timeline !== "undefined" && timeline && total > 0);
  await page.evaluate((from) => scrollTo(0, document.getElementById("story").offsetTop + from * innerHeight / 100), +from);
  if (process.env.CSS) await page.addStyleTag({ content: process.env.CSS });
  await page.waitForTimeout(2500);
  await browser.startTracing(page, { categories: ["devtools.timeline", "disabled-by-default-devtools.timeline", "blink", "cc", "gpu", "viz"] });
  const frames = await page.evaluate(([from, units]) => new Promise((done) => {
    const top = document.getElementById("story").offsetTop, unit = innerHeight / 100, end = top + (from + units) * unit;
    let y = top + from * unit, last = 0, n = 0;
    function step(now) { if (last) y += 240 * unit * Math.min(now - last, 100) / 1000; last = now; n++; scrollTo(0, y); y >= end ? done(n) : requestAnimationFrame(step); }
    requestAnimationFrame(step);
  }), [+from, +units]);
  const buf = await browser.stopTracing();
  const ev = JSON.parse(buf.toString()).traceEvents;
  // the renderer's main thread: the one with the most FunctionCall events
  const count = {}; ev.forEach((e) => { if (e.name === "FunctionCall") count[e.pid + ":" + e.tid] = (count[e.pid + ":" + e.tid] || 0) + 1; });
  const main = Object.entries(count).sort((a, b) => b[1] - a[1])[0][0];
  const byName = {}, perThread = {};
  for (const e of ev) {
    if (e.ph !== "X" || !e.dur) continue;
    const key = e.pid + ":" + e.tid;
    if (key === main) { const b = byName[e.name] || (byName[e.name] = { ms: 0, n: 0 }); b.ms += e.dur / 1000; b.n++; }
    if (["RasterTask", "ImageDecodeTask", "Decode Image", "Draw LazyPixelRef", "GPUTask", "DrawFrame", "Graphics.Pipeline.DrawAndSwap"].includes(e.name)) {
      const b = perThread[e.name] || (perThread[e.name] = { ms: 0, n: 0 }); b.ms += e.dur / 1000; b.n++;
    }
  }
  const top = Object.entries(byName).sort((a, b) => b[1].ms - a[1].ms).filter(([k]) => /^(ProxyMain::BeginMainFrame|Commit|LayerTreeHost::DoUpdateLayers|FunctionCall|LocalFrameView::RunPaintLifecyclePhase|Canvas2DResourceProvider::ProduceCanvasResource|UpdateLayoutTree|Paint|PrePaint|Layerize|CullRectUpdate)$/.test(k)).map(([k, v]) => `${(v.ms / frames).toFixed(2)} ms/frame  x${(v.n / frames).toFixed(1)}  ${k}`);
  console.log(label, "frames", frames, "\nMAIN THREAD (nested events overlap):\n" + top.join("\n"));
  console.log("OTHER THREADS:\n" + Object.entries(perThread).map(([k, v]) => `${(v.ms / frames).toFixed(2)} ms/frame  x${(v.n / frames).toFixed(1)}  ${k}`).join("\n"));
  await browser.close();
})();
