#!/usr/bin/env python3
"""news_shots: highlighted news-article screenshots + zoom clips in the house style.

For each shot in a JSON list it opens the article in a real browser, closes cookie /
subscribe pop-ups, finds the exact sentence, paints a yellow marker over it, scrolls it
into view, takes a 2x screenshot, and then makes:

  out/<id>.png   1280x720 still (grain, vignette, outlet + date chip)
  out/<id>.mp4   2.5 s clip that eases from the full page into the highlighted line
  out/report.json  what was found / not found per shot

Usage (on your own machine; needs internet):
  pip install playwright pillow numpy && python3 -m playwright install chromium
  python3 tools/news_shots.py episodes/2026-11-oil-iran-january/news_shots.json
  python3 tools/news_shots.py <json> --only cnbc-brent-90 axios-massie-218
  python3 tools/news_shots.py <json> --profile ~/.toon-news-chrome --headed   # sign in once for paywalled sites
  python3 tools/news_shots.py <json> --dim        # also darken everything except the highlighted line

Shot fields: id, url, highlight (exact words on the page, any case/spacing),
outlet ("CNBC"), date ("10 NOV 2026"), optional: dur (s, default 2.5), fallback
(a shorter phrase to try if the full one is not found), scroll_extra (px).
"""
import argparse, json, math, os, subprocess, sys, tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 30
ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "assets/fonts/PatrickHand.ttf"
HL = "#ffe14d"   # marker yellow

CONSENT_WORDS = ["accept all", "accept", "i accept", "agree", "i agree", "allow all", "got it", "ok",
                 "continue", "no thanks", "not now", "maybe later", "close", "dismiss", "reject all"]

JS_CLEAN = r"""
() => {
  // hide fixed/sticky overlays that cover the page (cookie walls, sign-up modals, sticky ads)
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

JS_HIGHLIGHT = r"""
([want, color, dim, extra]) => {
  const norm = s => s.toLowerCase().replace(/[‘’‛]/g, "'").replace(/[“”]/g, '"')
                    .replace(/[–—]/g, '-').replace(/ /g, ' ');
  const target = norm(want).replace(/\s+/g, ' ').trim();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode: n => {
      const p = n.parentElement; if (!p) return NodeFilter.FILTER_REJECT;
      const cs = getComputedStyle(p);
      if (cs.display === 'none' || cs.visibility === 'hidden' || /SCRIPT|STYLE|NOSCRIPT/.test(p.tagName)) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT; } });
  // build one string of all visible text with whitespace collapsed, keeping a map back to (node, offset)
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
  const rects = [...range.getClientRects()].filter(r => r.width > 2 && r.height > 2);
  const layer = document.createElement('div');
  layer.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:2147483647;mix-blend-mode:multiply';
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  for (const r of rects) {
    const m = document.createElement('div');
    m.style.cssText = `position:absolute;left:${r.left - 3}px;top:${r.top + r.height * 0.12}px;width:${r.width + 6}px;` +
      `height:${r.height * 0.86}px;background:${color};border-radius:4px;transform:rotate(-0.4deg)`;
    layer.appendChild(m);
    x0 = Math.min(x0, r.left); y0 = Math.min(y0, r.top); x1 = Math.max(x1, r.right); y1 = Math.max(y1, r.bottom);
  }
  if (dim) {
    const pad = 18, box = [x0 - pad, y0 - pad, x1 + pad, y1 + pad];
    const sh = (l, t, w, h) => { const d = document.createElement('div');
      d.style.cssText = `position:absolute;left:${l}px;top:${t}px;width:${w}px;height:${h}px;background:rgba(0,0,0,.45)`; layer.appendChild(d); };
    sh(0, 0, innerWidth, box[1]); sh(0, box[3], innerWidth, innerHeight - box[3]);
    sh(0, box[1], box[0], box[3] - box[1]); sh(box[2], box[1], innerWidth - box[2], box[3] - box[1]);
  }
  document.body.appendChild(layer);
  return { x0, y0, x1, y1, vw: innerWidth, vh: innerHeight };
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
    """Transparent 1280x720 overlay: dark rounded source chip, bottom-left (house caption look)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    txt = f"SOURCE: {outlet}" + (f"  ·  {date}" if date else "")
    f = font(30)
    tw = d.textlength(txt, font=f)
    x, y = 36, H - 82
    d.rounded_rectangle([x, y, x + tw + 32, y + 48], 10, fill=(0, 0, 0, 158))
    d.text((x + 16, y + 6), txt, font=f, fill=(255, 255, 255, 255))
    return im


def grade(rgb, seed):
    """grain + vignette, same values as toonkit.core."""
    a = rgb.astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    dd = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    vig = (1 - 0.38 * np.clip(dd - 0.35, 0, 1) ** 1.6)[..., None]
    g = np.random.default_rng(seed).normal(0, 7, (H, W, 1))
    return np.clip(a * vig + g, 0, 255).astype(np.uint8)


def make_outputs(raw_png, box, shot, out_dir):
    """raw_png: 2x viewport screenshot (2560x1440). box: highlight rect in CSS px."""
    src = Image.open(raw_png).convert("RGB")
    sw, sh = src.size
    sc = sw / box["vw"]                      # CSS px → screenshot px
    bx0, by0, bx1, by1 = (box["x0"] * sc, box["y0"] * sc, box["x1"] * sc, box["y1"] * sc)
    # end framing: the highlighted line fills ~78% of the width, kept 16:9 and inside the page
    bw = max(bx1 - bx0, sw * 0.35)
    ew = min(sw, bw / 0.78); eh = ew * 9 / 16
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    ex0 = min(max(cx - ew / 2, 0), sw - ew); ey0 = min(max(cy - eh / 2, 0), sh - eh)
    chip = chip_layer(shot["outlet"], shot.get("date", ""))
    sid = shot["id"]

    def frame_at(t):
        k = t * t * (3 - 2 * t)              # ease in-out
        x0 = ex0 * k; y0 = ey0 * k
        w = sw + (ew - sw) * k; h = sh + (eh - sh) * k
        fr = src.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))
        return fr

    still = Image.fromarray(grade(np.asarray(frame_at(1.0)), 1)).convert("RGBA")
    still.alpha_composite(chip)
    still.convert("RGB").save(out_dir / f"{sid}.png")

    dur = float(shot.get("dur", 2.5)); n = int(round(dur * FPS))
    hold = int(0.35 * FPS)                   # hold on the full page first, then push in
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
           "-pix_fmt", "yuv420p", str(out_dir / f"{sid}.mp4")]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        t = 0 if i < hold else min(1, (i - hold) / max(1, n - hold - int(0.3 * FPS)))
        fr = Image.fromarray(grade(np.asarray(frame_at(t)), i // 2 % 6)).convert("RGBA")
        fr.alpha_composite(chip)
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots")
    ap.add_argument("--out", help="output folder (default: <json folder>/news_shots)")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--profile", help="persistent browser profile dir (sign in once, reuse cookies)")
    ap.add_argument("--headed", action="store_true", help="show the browser (helps with bot checks)")
    ap.add_argument("--chrome", action="store_true", help="use installed Google Chrome instead of Playwright Chromium")
    ap.add_argument("--dim", action="store_true", help="darken everything except the highlighted line")
    a = ap.parse_args()

    from playwright.sync_api import sync_playwright

    jpath = Path(a.shots)
    shots = json.loads(jpath.read_text())["shots"]
    if a.only:
        shots = [s for s in shots if s["id"] in a.only]
    out = Path(a.out) if a.out else jpath.parent / "news_shots"
    out.mkdir(parents=True, exist_ok=True)
    rawdir = out / "raw"; rawdir.mkdir(exist_ok=True)
    report = {}

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
                box = None
                for phrase in [s["highlight"], s.get("fallback")]:
                    if phrase:
                        box = page.evaluate(JS_HIGHLIGHT, [phrase, HL, a.dim, s.get("scroll_extra", 0)])
                        if box:
                            used = phrase; break
                page.wait_for_timeout(700)       # let lazy images settle after the scroll
                raw = rawdir / f"{sid}.png"
                page.screenshot(path=str(raw))
                if not box:
                    report[sid] = {"status": "NOT FOUND", "note": "screenshot saved without highlight; check raw/ and fix the phrase"}
                    print("   ! phrase not found (paywall? different wording?)")
                    continue
                make_outputs(raw, box, s, out)
                report[sid] = {"status": "ok", "highlighted": used}
                print("   ok")
            except Exception as e:
                report[sid] = {"status": "ERROR", "note": str(e)[:300]}
                print("   ! error:", e)
        ctx.close()

    (out / "report.json").write_text(json.dumps(report, indent=2))
    bad = [k for k, v in report.items() if v["status"] != "ok"]
    print(f"\n{len(report) - len(bad)}/{len(report)} ok → {out}")
    if bad:
        print("needs attention:", ", ".join(bad))


if __name__ == "__main__":
    main()
