// How much memory does the browser use while the whole chapter is read at a steady pace?  node memory.js <port> <label>
const { chromium } = require("playwright");
const { execSync } = require("child_process");
const path = require("path");
const OLD_GSAP = process.env.OLD_GSAP || __dirname; // a folder with gsap.min.js + ScrollTrigger.min.js, for a reader from before vendor/
const rss = () => { // MB held by the page's renderer and by the process that draws (GPU process), from the system's own count
  const rows = execSync("ps -eo rss,args").toString().split("\n").filter((l) => /chrom/i.test(l) && /--type=(renderer|gpu-process)/.test(l));
  const mb = (re) => rows.filter((l) => re.test(l)).reduce((a, l) => a + parseInt(l) / 1024, 0);
  return [mb(/--type=renderer/), mb(/--type=gpu-process/)];
};
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  await page.route(/cdnjs\.cloudflare\.com\/.*gsap\/3\.12\.5\/(\w+)\.min\.js/, (r) => r.fulfill({ path: path.join(OLD_GSAP, r.request().url().split("/").pop()), contentType: "text/javascript" }));
  await page.route(/fonts\.(googleapis|gstatic)\.com|cdn\.jsdelivr\.net/, (r) => r.abort());
  await page.goto(`http://localhost:${process.argv[2]}/#094`);
  await page.waitForFunction(() => typeof timeline !== "undefined" && timeline && total > 0);
  await page.waitForTimeout(1500);
  const start = rss(); const seen = [];
  const timer = setInterval(() => seen.push(rss()), 1000);
  await page.evaluate(() => new Promise((done) => {
    const top = document.getElementById("story").offsetTop, unit = innerHeight / 100, end = document.documentElement.scrollHeight - innerHeight;
    let y = top, last = 0;
    (function step(now) { if (last) y += 240 * unit * Math.min((now || 0) - last, 100) / 1000; last = now || 0.001; scrollTo(0, y); y >= end ? done() : requestAnimationFrame(step); })();
  }));
  clearInterval(timer);
  const f = (v) => v.toFixed(0).padStart(5);
  const peak = (k) => Math.max(...seen.map((s) => s[k])), avg = (k) => seen.reduce((a, s) => a + s[k], 0) / seen.length;
  console.log(`${process.argv[3].padEnd(9)} page process: start ${f(start[0])} MB, average ${f(avg(0))} MB, peak ${f(peak(0))} MB | drawing process: average ${f(avg(1))} MB, peak ${f(peak(1))} MB | together at peak ${f(Math.max(...seen.map((s) => s[0] + s[1])))} MB`);
  await browser.close();
})();
