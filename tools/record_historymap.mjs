// Record this episode's History Map segments to MP4 in Brave/Chrome (WebCodecs H.264, offline 60 fps).
// Copied from naah/projects/america/tools/record_historymap.mjs and pointed at an episode manifest.
//
//   node tools/record_historymap.mjs episodes/2026-11-oil-iran-january [seg or shot ids...]
//
// Needs naah/vendor/historymap served on http://localhost:8743 (python3 -m http.server 8743),
// and Playwright (npm i playwright, or NODE_PATH pointing at a node_modules that has it).
// Output: <episode>/historymap/raw/<seg>.mp4 (1920x1080, 60 fps) and <seg>.proj.json — the screen
// position (CSS px on the 960x540 canvas), occlusion and zoom of every pin / label / arrow tail for
// every rendered frame, so tools/conform_maps.py can draw our Patrick Hand labels exactly on them.
//
// Extra over the America recorder: per-arrow draw times (the app draws all arrows of a shot at once),
// waits for map.areTilesLoaded() + a settle before recording, checks each file's length and retries,
// reloads the page if a segment hangs.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const EP = path.resolve(process.argv[2] || 'episodes/2026-11-oil-iran-january');
const RAW = path.join(EP, 'historymap', 'raw');
const BROWSER = process.env.BRAVE_PATH || [
  `${process.env.HOME}/Desktop/Brave Browser.app/Contents/MacOS/Brave Browser`,
  '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
].find((p) => fs.existsSync(p));
const URL = process.env.HISTORYMAP_URL || 'http://localhost:8743';
const manifest = JSON.parse(fs.readFileSync(path.join(EP, 'historymap', 'manifest.json'), 'utf8'));
const only = process.argv.slice(3);
const todo = manifest.filter((m) => !only.length || only.includes(m.seg) || only.includes(m.shot_id));
fs.mkdirSync(RAW, { recursive: true });
const log = (...a) => console.log(new Date().toISOString().slice(11, 19), ...a);

const browser = await chromium.launch({ executablePath: BROWSER, headless: false, args: ['--window-size=1500,900'] });
const ctx = await browser.newContext({ acceptDownloads: true, viewport: { width: 1440, height: 820 }, deviceScaleFactor: 1 });
let page;
const errors = [];

async function openPage() {
  if (page) await page.close().catch(() => {});
  page = await ctx.newPage();
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(URL, { waitUntil: 'load' });
  await page.waitForSelector('.maplibregl-canvas', { timeout: 60000 });
  await page.waitForTimeout(1500);
  // hooks: per-arrow draw times, and a projection log of our label points for every painted frame
  await page.evaluate(() => {
    const origTL = buildShotTimeline;
    window.buildShotTimeline = function () {
      const r = origTL();
      const t0 = shot && shot.space ? shot.durMs * shot.spaceFrac : 0;
      (window.__arrowTimes || []).forEach((tt, i) => { if (arrows[i]) r.arrowTimes[arrows[i].id] = [t0 + tt[0], t0 + tt[1]]; });
      return r;
    };
    const origPF = paintFrame;
    window.paintFrame = function (tl, tMs) {
      origPF(tl, tMs);
      if (!window.__proj) return;
      const pts = (window.__llpts || []).map(([lng, lat]) => {
        const p = map.project([lng, lat]);
        return [+p.x.toFixed(2), +p.y.toFixed(2), occludedByGlobe(lng, lat) ? 1 : 0];
      });
      window.__proj.push({ t: +tMs.toFixed(3), z: +map.getZoom().toFixed(4), w: map.getCanvas().clientWidth, p: pts });
    };
  });
}

function mp4Seconds(file) {
  // duration from the mvhd box (no ffprobe dependency here)
  const b = fs.readFileSync(file);
  const i = b.indexOf('mvhd');
  if (i < 0) return 0;
  const v = b[i + 4];
  const ts = v === 1 ? b.readUInt32BE(i + 24) : b.readUInt32BE(i + 16);
  const du = v === 1 ? Number(b.readBigUInt64BE(i + 28)) : b.readUInt32BE(i + 20);
  return ts ? du / ts : 0;
}

async function recordOne(m) {
  const pts = [...m.pins.map((p) => p.ll), ...m.labels.map((l) => l.ll), ...m.arrows.map((a) => a.label_ll || a.from)];
  await page.evaluate(([at, ll]) => { window.__arrowTimes = at; window.__llpts = ll; window.__proj = null; }, [m.arrow_times_ms, pts]);
  await page.setInputFiles('#file-route', path.join(EP, m.file));
  // wait until THIS segment's shot is loaded (a stale shot from the previous file must never be recorded)
  await page.waitForFunction((want) => typeof shot !== 'undefined' && shot && Math.abs(shot.durMs - want.durMs) < 0.01
    && shot.from.center[0] === want.from.center[0] && shot.from.qz === want.from.qz && regions.length === want.nreg && arrows.length === want.narr,
    { durMs: m.shot.durMs, from: m.shot.from, nreg: m.regions.length, narr: m.narr }, { timeout: 20000 });
  // 960x540 CSS at pixel ratio 2 → exactly 1920x1080
  await page.evaluate(async () => {
    const box = document.querySelector('#mapbox');
    box.style.width = '960px'; box.style.height = '540px';
    map.resize();
    await regionsReady;
  });
  await page.waitForFunction(() => map.areTilesLoaded() && map.loaded(), null, { timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(1500);
  await page.evaluate(() => { window.__proj = []; });
  await page.click('#btn-record');
  await page.waitForFunction(() => !document.querySelector('#btn-download').classList.contains('hidden'), null, { timeout: 4 * 60e3 });
  const [dl] = await Promise.all([page.waitForEvent('download', { timeout: 60e3 }), page.click('#btn-download')]);
  const out = path.join(RAW, `${m.seg}.mp4`);
  await dl.saveAs(out);
  await page.evaluate(() => document.querySelector('#btn-download').classList.add('hidden'));
  const proj = await page.evaluate(() => window.__proj);
  fs.writeFileSync(path.join(RAW, `${m.seg}.proj.json`), JSON.stringify({ seg: m.seg, points: pts, frames: proj }));
  return mp4Seconds(out);
}

await openPage();
for (const m of todo) {
  const want = m.frames / 30;
  let ok = false;
  for (let attempt = 1; attempt <= 4 && !ok; attempt++) {
    const t0 = Date.now();
    try {
      const secs = await recordOne(m);
      ok = secs >= want - 0.05;
      log(`${m.seg} (${m.frames} f) → ${secs.toFixed(2)} s ${ok ? 'ok' : `TOO SHORT (want ${want.toFixed(2)}), retry`} in ${((Date.now() - t0) / 1000).toFixed(0)} s`);
    } catch (e) {
      log(`${m.seg} attempt ${attempt} failed: ${e.message.split('\n')[0]}; reloading page`);
    }
    if (!ok) await openPage();
  }
  if (!ok) log(`${m.seg} GAVE UP`);
}
log('page errors:', errors.length ? errors : 'none');
await browser.close();
