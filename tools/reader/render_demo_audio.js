// The demo video's soundtrack: the music mix plus every sound effect at the moment record_demo.js ("cues" mode) found
// it fires, through the site's own chain. Music sits at 0.55 and dips to half under each effect, so the hits read clearly.
// Arguments: the scratch folder (as for record_demo.js) and all | sfx | music. Then: ffmpeg loudnorm I=-14.5 TP=-3 + alimiter.
// Renders the demo's soundtrack in the page: the music mix plus every sound effect at the moment it fires,
// through the site's own chain (effects bus 0.65 -> limiter -> soft clip), with the site's makeEffects().
const { chromium } = require("playwright");
const fs = require("fs");
const S = process.argv[2], PART = process.argv[3] || "all"; // all, sfx (effects alone) or music (music alone)
(async () => {
  const browser = await chromium.launch({ args: ["--host-resolver-rules=MAP tbate-scroll-demo.pages.dev 127.0.0.1", "--autoplay-policy=no-user-gesture-required"] });
  const page = await browser.newPage();
  await page.route(/cdnjs\.cloudflare\.com.*gsap\.min\.js/, (r) => r.fulfill({ path: S + "/gsap/package/dist/gsap.min.js" }));
  await page.route(/cdnjs\.cloudflare\.com.*ScrollTrigger\.min\.js/, (r) => r.fulfill({ path: S + "/gsap/package/dist/ScrollTrigger.min.js" }));
  await page.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
  await page.route("http://tbate-scroll-demo.pages.dev:8803/__music_mix.wav", (r) => r.fulfill({ path: S + "/video/music_mix.wav", contentType: "audio/wav" }));
  await page.goto("http://tbate-scroll-demo.pages.dev:8803/");
  await page.waitForTimeout(1000);
  const cues = JSON.parse(fs.readFileSync(S + "/video/cues.json"));
  const b64 = await page.evaluate(async ([cues, part]) => {
    const SR = 48000, ctx = new OfflineAudioContext(2, Math.round(56 * SR), SR);
    const limiter = ctx.createDynamicsCompressor();
    limiter.threshold.value = -10; limiter.ratio.value = 20; limiter.attack.value = 0.001;
    const softClip = ctx.createWaveShaper();
    softClip.curve = Float32Array.from({ length: 2049 }, (_, i) => Math.tanh(1.2 * (i / 1024 - 1)) / Math.tanh(1.2));
    softClip.oversample = "4x";
    limiter.connect(softClip).connect(ctx.destination);
    const sfxGain = ctx.createGain(); sfxGain.gain.value = 0.65; sfxGain.connect(limiter);
    const effects = makeEffects(ctx, sfxGain);
    const load = async (url) => ctx.decodeAudioData(await (await fetch(url)).arrayBuffer());
    for (const [name, sound] of Object.entries(SERIES.sounds || {})) {
      const buffer = await load(sound.src);
      effects[name] = (t) => { const src = ctx.createBufferSource(), g = ctx.createGain();
        src.buffer = buffer; g.gain.value = sound.volume ?? 1; src.connect(g).connect(sfxGain); src.start(t); };
    }
    // for the video: the music sits lower than on the site, and dips under each effect so the hits read clearly
    const music = ctx.createBufferSource(), bed = ctx.createGain();
    music.buffer = await load("__music_mix.wav"); music.connect(bed).connect(limiter); if (part !== "sfx") music.start(0);
    const BED = 0.55, DIP = 0.5;
    bed.gain.setValueAtTime(BED, 0);
    for (const c of cues) {
      const t = c.at + 0.01;
      bed.gain.setTargetAtTime(BED * DIP, Math.max(0, t - 0.03), 0.015);
      bed.gain.setTargetAtTime(BED, t + 0.35, 0.25);
    }
    const missing = [];
    if (part !== "music") for (const c of cues) effects[c.sfx] ? effects[c.sfx](c.at + 0.01) : missing.push(c.sfx);
    if (missing.length) throw new Error("no effect called " + missing.join(", "));
    const out = await ctx.startRendering();
    const n = out.length, both = new Float32Array(n * 2), L = out.getChannelData(0), R = out.getChannelData(1);
    for (let i = 0; i < n; i++) { both[2 * i] = L[i]; both[2 * i + 1] = R[i]; }
    const bytes = new Uint8Array(both.buffer); let s = "";
    for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return btoa(s);
  }, [cues, PART]);
  fs.writeFileSync(S + `/video/${PART === "all" ? "full" : PART}_mix.raw`, Buffer.from(b64, "base64"));
  console.log("rendered", (Buffer.byteLength(b64, "base64") / 8 / 48000).toFixed(2), "s");
  await browser.close();
})();
