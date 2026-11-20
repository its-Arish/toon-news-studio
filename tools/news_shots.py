#!/usr/bin/env python3
"""news_shots: news-article clips where the page is shown first, then a marker draws over the line.

For each shot in a JSON list it opens the article in a real browser, closes cookie /
subscribe pop-ups, finds the exact sentence, scrolls it into view and takes a clean 2x
screenshot (no highlight baked in). The highlight is animated afterwards:

  0.0 s   swoosh, the article appears (whole page in view, headline readable)
  ~1.0 s  camera pushes in to the paragraph
  ~1.7 s  marker cap click, then the yellow marker sweeps across the sentence line by line,
          one marker-stroke sound per line; the rest of the page dims
  end     hold on the highlighted line

Outputs per shot (in <json folder>/news_shots/ unless --out):
  <id>.mp4      1280x720 30 fps clip WITH its sound effects
  <id>_sfx.wav  the same sound effects alone (full clip length) for the separate SFX track
  <id>.png      final highlighted frame
  report.json   ok / NOT FOUND / ERROR per shot; raw/<id>.png = the clean screenshot

Usage (on your own machine; needs internet):
  pip install playwright pillow numpy scipy && python3 -m playwright install chromium
  python3 tools/news_shots.py episodes/2026-11-oil-iran-january/news_shots.json
  python3 tools/news_shots.py <json> --only 12-cnbc-brent-90
  python3 tools/news_shots.py <json> --profile ~/.toon-news-chrome --headed --chrome   # paywalls / bot checks
  python3 tools/news_shots.py <json> --no-dim                                           # keep the page bright
  python3 tools/news_shots.py <json> --reuse     # re-animate from saved screenshots, no browser

Shot fields: id, url, highlight (exact words on the page; case, quotes and spacing are ignored),
outlet, date, optional: dur (s, default 4.0), fallback (shorter phrase), scroll_extra (px),
show (s the article is on screen before the push-in, default 1.0).
"""
import argparse, json, os, subprocess, sys, wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 30
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
FONT = ROOT / "assets/fonts/PatrickHand.ttf"
MARKER = np.array([255, 225, 77], np.float32) / 255.0   # marker yellow, applied as multiply

CONSENT_WORDS = ["accept all", "accept", "i accept", "agree", "i agree", "allow all", "got it", "ok",
                 "continue", "no thanks", "not now", "maybe later", "close", "dismiss", "reject all"]

JS_CLEAN = r"""
() => {
  const vw = innerWidth, vh = innerHeight;
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    if (cs.position !== 'fixed' && cs.position !== 'sticky') continue;
    const r = el.getBoundingClientRect();
    const area = (r.width * r.height) / (vw * vh);
    const z = parseInt(cs.zIndex || '0') || 0;
    if (area > 0.25 || (z > 100 && area > 0.04) || r.top > vh * 0.6) el.style.setProperty('display', 'none', 'important');
  }
  for (const el of [document.documentElement, document.body]) {
    el.style.setProperty('overflow', 'auto', 'important');
    el.style.setProperty('position', 'static', 'important');
  }
}
"""

# finds the phrase, scrolls it to ~42% of the viewport, returns one rect per visual line (CSS px)
JS_FIND = r"""
([want, extra]) => {
  const norm = s => s.toLowerCase().replace(/[‘’‛]/g, "'").replace(/[“”]/g, '"')
                    .replace(/[–—]/g, '-').replace(/ /g, ' ');
  const target = norm(want).replace(/\s+/g, ' ').trim();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode: n => {
      const p = n.parentElement; if (!p) return NodeFilter.FILTER_REJECT;
      const cs = getComputedStyle(p);
      if (cs.display === 'none' || cs.visibility === 'hidden' || /SCRIPT|STYLE|NOSCRIPT/.test(p.tagName)) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT; } });
  let flat = '', map = [], lastSpace = true, n;
  while ((n = walker.nextNode())) {
    const t = norm(n.data);
    for (let i = 0; i < t.length; i++) {
      const ch = /\s/.test(t[i]) ? ' ' : t[i];
      if (ch === ' ' && lastSpace) continue;
      flat += ch; map.push([n, i]); lastSpace = ch === ' ';
    }
    if (!lastSpace) { flat += ' '; map.push([n, n.data.length]); lastSpace = true; }
  }
  const at = flat.indexOf(target);
  if (at < 0) return null;
  const [sn, so] = map[at], [en, eo] = map[at + target.length - 1];
  const range = document.createRange();
  range.setStart(sn, so); range.setEnd(en, Math.min(eo + 1, en.data.length));
  const r0 = range.getBoundingClientRect();
  window.scrollBy(0, r0.top - innerHeight * 0.42 + (extra || 0));
  const rects = [...range.getClientRects()].filter(r => r.width > 2 && r.height > 4)
                 .map(r => ({x0: r.left, y0: r.top, x1: r.right, y1: r.bottom}));
  rects.sort((a, b) => a.y0 - b.y0 || a.x0 - b.x0);
  const lines = [];
  for (const r of rects) {               // merge rects that sit on the same visual line
    const L = lines.find(l => Math.abs((l.y0 + l.y1) / 2 - (r.y0 + r.y1) / 2) < Math.min(l.y1 - l.y0, r.y1 - r.y0) * 0.5);
    if (L) { L.x0 = Math.min(L.x0, r.x0); L.x1 = Math.max(L.x1, r.x1); L.y0 = Math.min(L.y0, r.y0); L.y1 = Math.max(L.y1, r.y1); }
    else lines.push({...r});
  }
  lines.sort((a, b) => a.y0 - b.y0);
  return { lines, vw: innerWidth, vh: innerHeight };
}
"""


def dismiss_popups(page):
    for frame in [page.main_frame] + page.frames[1:]:
        for word in CONSENT_WORDS:
            try:
                btn = frame.get_by_role("button", name=word, exact=True)
                if btn.count() and btn.first.is_visible():
                    btn.first.click(timeout=1500)
                    page.wait_for_timeout(500)
            except Exception:
                pass
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass


def font(size):
    return ImageFont.truetype(str(FONT), size) if FONT.exists() else ImageFont.load_default()


def chip_layer(outlet, date):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    txt = f"SOURCE: {outlet}" + (f"  ·  {date}" if date else "")
    f = font(30)
    tw = d.textlength(txt, font=f)
    x, y = 36, H - 82
    d.rounded_rectangle([x, y, x + tw + 32, y + 48], 10, fill=(0, 0, 0, 158))
    d.text((x + 16, y + 6), txt, font=f, fill=(255, 255, 255, 255))
    return im


_yy, _xx = np.mgrid[0:H, 0:W]
_dd = np.sqrt(((_xx - W / 2) / (W / 2)) ** 2 + ((_yy - H / 2) / (H / 2)) ** 2)
VIG = (1 - 0.38 * np.clip(_dd - 0.35, 0, 1) ** 1.6)[..., None].astype(np.float32)
GRAIN = [np.random.default_rng(s).normal(0, 7, (H, W, 1)).astype(np.float32) for s in range(6)]


def grade(rgb, k):
    return np.clip(rgb.astype(np.float32) * VIG + GRAIN[k % 6], 0, 255).astype(np.uint8)


def ease(t):
    t = min(1.0, max(0.0, t)); return t * t * (3 - 2 * t)


def write_wav(path, x, sr):
    x = np.clip(x, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def make_outputs(raw_png, geo, shot, out_dir, dim=True):
    from toonkit import sfx
    src = np.asarray(Image.open(raw_png).convert("RGB")).astype(np.float32)
    sh, sw = src.shape[:2]
    sc = sw / geo["vw"]
    lines = [[l["x0"] * sc, l["y0"] * sc, l["x1"] * sc, l["y1"] * sc] for l in geo["lines"]]
    bx0 = min(l[0] for l in lines); by0 = min(l[1] for l in lines)
    bx1 = max(l[2] for l in lines); by1 = max(l[3] for l in lines)

    # end framing: the sentence fills ~78% of the width, 16:9, inside the page
    bw = max(bx1 - bx0, sw * 0.35)
    ew = min(sw, bw / 0.78); eh = ew * 9 / 16
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    ex0 = min(max(cx - ew / 2, 0), sw - ew); ey0 = min(max(cy - eh / 2, 0), sh - eh)

    # timeline (s)
    dur = float(shot.get("dur", 4.0)); show = float(shot.get("show", 1.0))
    push0, push1 = show, show + 0.7
    mark0 = push1 + 0.12
    widths = [l[2] - l[0] for l in lines]
    per_px = 0.85 / max(sum(widths), 1)                       # whole sentence ≈ 0.85 s of marker
    line_t = [max(0.22, w * per_px) for w in widths]
    gap = 0.07
    starts = []; t = mark0
    for lt in line_t:
        starts.append(t); t += lt + gap
    mark1 = t
    dur = max(dur, mark1 + 0.9)                               # always hold ~0.9 s on the finished highlight
    n = int(round(dur * FPS))

    hl = src * MARKER
    box = np.zeros((sh, sw), np.float32)
    pad = 18 * sc / 2
    box[int(max(0, by0 - pad)):int(min(sh, by1 + pad)), int(max(0, bx0 - pad)):int(min(sw, bx1 + pad))] = 1

    def frame(tsec):
        img = src
        prog = [ease((tsec - s0) / lt) for s0, lt in zip(starts, line_t)]
        if any(p > 0 for p in prog):
            m = np.zeros((sh, sw), np.float32)
            for (x0, y0, x1, y1), p in zip(lines, prog):
                if p <= 0: continue
                hgt = y1 - y0
                ya, yb = int(y0 + hgt * 0.12), int(y0 + hgt * 0.98)
                xa = int(x0 - 3 * sc / 2); xb = int(x0 + (x1 - x0 + 6 * sc / 2) * p)
                if xb > xa:
                    m[ya:yb, xa:xb] = 1
                    feather = int(6 * sc / 2)                     # soft wet edge at the moving tip
                    if p < 1 and feather > 0:
                        fa = max(xa, xb - feather)
                        m[ya:yb, fa:xb] *= np.linspace(1, 0.35, xb - fa)[None, :]
            img = img * (1 - m[..., None]) + hl * m[..., None]
        if dim:
            a = 0.45 * ease((tsec - mark0 + 0.1) / 0.35)
            if a > 0:
                img = img * (1 - a * (1 - box[..., None]))
        k = ease((tsec - push0) / (push1 - push0))
        x0 = ex0 * k; y0 = ey0 * k
        w = sw + (ew - sw) * k; h = sh + (eh - sh) * k
        return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))

    chip = chip_layer(shot["outlet"], shot.get("date", ""))
    sid = shot["id"]

    # sound: swoosh as the article lands, cap click, one marker stroke per line
    SR = sfx.SR
    mix = np.zeros(int(dur * SR) + SR, np.float64)
    sfx._place(mix, sfx.swoosh(1), 0.0)
    sfx._place(mix, sfx.marker_cap(2), mark0 - 0.1)
    for i, (s0, lt) in enumerate(zip(starts, line_t)):
        sfx._place(mix, sfx.marker(i + 3, lt + 0.05), s0)
    mix = mix[: int(dur * SR)]
    wav = out_dir / f"{sid}_sfx.wav"
    write_wav(wav, mix, SR)

    tmp = out_dir / f"{sid}.video.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
           "-pix_fmt", "yuv420p", str(tmp)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    last = None
    for i in range(n):
        fr = Image.fromarray(grade(np.asarray(frame(i / FPS)), i // 2)).convert("RGBA")
        fr.alpha_composite(chip)
        last = fr.convert("RGB")
        p.stdin.write(last.tobytes())
    p.stdin.close(); p.wait()
    last.save(out_dir / f"{sid}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-i", str(wav), "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_dir / f"{sid}.mp4")], check=True)
    tmp.unlink()
    return dur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots")
    ap.add_argument("--out", help="output folder (default: <json folder>/news_shots)")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--profile", help="persistent browser profile dir (sign in once, reuse cookies)")
    ap.add_argument("--headed", action="store_true", help="show the browser (helps with bot checks)")
    ap.add_argument("--chrome", action="store_true", help="use installed Google Chrome instead of Playwright Chromium")
    ap.add_argument("--no-dim", action="store_true", help="keep the rest of the page bright")
    ap.add_argument("--reuse", action="store_true", help="skip the browser; re-animate from raw/<id>.png + raw/<id>.json")
    a = ap.parse_args()

    jpath = Path(a.shots)
    shots = json.loads(jpath.read_text())["shots"]
    if a.only:
        shots = [s for s in shots if s["id"] in a.only]
    out = Path(a.out) if a.out else jpath.parent / "news_shots"
    out.mkdir(parents=True, exist_ok=True)
    rawdir = out / "raw"; rawdir.mkdir(exist_ok=True)
    rpath = out / "report.json"
    report = json.loads(rpath.read_text()) if rpath.exists() else {}

    def finish(s, geo, used):
        d = make_outputs(rawdir / f"{s['id']}.png", geo, s, out, dim=not a.no_dim)
        report[s["id"]] = {"status": "ok", "highlighted": used, "seconds": round(d, 2), "lines": len(geo["lines"])}
        print(f"   ok  ({len(geo['lines'])} line(s), {d:.1f} s)")

    if a.reuse:
        for s in shots:
            gp = rawdir / f"{s['id']}.json"
            if gp.exists():
                print(f"[{s['id']}] re-animate"); g = json.loads(gp.read_text()); finish(s, g, g.get("used"))
        rpath.write_text(json.dumps(report, indent=2)); return

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        kw = dict(viewport={"width": 1280, "height": 720}, device_scale_factor=2, locale="en-US",
                  user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")
        launch = dict(headless=not a.headed)
        if a.chrome:
            launch["channel"] = "chrome"
        if a.profile:
            ctx = pw.chromium.launch_persistent_context(os.path.expanduser(a.profile), **launch, **kw)
        else:
            ctx = pw.chromium.launch(**launch).new_context(**kw)
        page = ctx.new_page()
        for s in shots:
            sid = s["id"]
            print(f"[{sid}] {s['url']}")
            try:
                page.goto(s["url"], wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(2500)
                dismiss_popups(page)
                page.evaluate(JS_CLEAN)
                page.wait_for_timeout(400)
                geo, used = None, None
                for phrase in [s["highlight"], s.get("fallback")]:
                    if phrase:
                        geo = page.evaluate(JS_FIND, [phrase, s.get("scroll_extra", 0)])
                        if geo and geo["lines"]:
                            used = phrase; break
                        geo = None
                page.wait_for_timeout(800)            # lazy images settle after the scroll
                page.screenshot(path=str(rawdir / f"{sid}.png"))
                if not geo:
                    report[sid] = {"status": "NOT FOUND", "note": "clean screenshot in raw/; fix 'highlight' to the page's real words"}
                    print("   ! phrase not found (paywall? different wording?)")
                    continue
                geo["used"] = used
                (rawdir / f"{sid}.json").write_text(json.dumps(geo))
                finish(s, geo, used)
            except Exception as e:
                report[sid] = {"status": "ERROR", "note": str(e)[:300]}
                print("   ! error:", e)
        ctx.close()

    rpath.write_text(json.dumps(report, indent=2))
    bad = [k for k, v in report.items() if v["status"] != "ok"]
    print(f"\n{len(report) - len(bad)}/{len(report)} ok → {out}")
    if bad:
        print("needs attention:", ", ".join(bad))


if __name__ == "__main__":
    main()
