"""Full episode: ARE OIL PRICES FINALLY DROPPING? WHAT WILL HAPPEN IN JANUARY? USA IRAN WAR
Timed to voiceover.srt (8:37). News + History Map clips from news_shots/ and maps/ play inside the timeline.
Run from repo root:
  python3 episodes/2026-11-oil-iran-january/full.py info
  python3 episodes/2026-11-oil-iran-january/full.py stills [from to]
  python3 episodes/2026-11-oil-iran-january/full.py render      # out/video.mp4 (no audio)
  python3 episodes/2026-11-oil-iran-january/full.py sfx         # out/sfx.wav (full length)
  python3 episodes/2026-11-oil-iran-january/full.py package     # deliverables
"""
import sys, os, re, math, random, json, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT); sys.path.insert(0, HERE); os.chdir(ROOT)
import numpy as np
import cairo
from toonkit.core import text, rrect, fill_stroke, hexc, ease_io, prog, clamp, W, H, FPS
from toonkit.rig import wline, INK, A_rest, A_talk, A_wave, A_point, A_shrug, A_shock, A_walk, A_run, REST
from toonkit import scene as SC
from toonkit.scene import cam, vgrad, glow, label, stars, suit_figure
from toonkit import kit as K
from toonkit import sfx as SFXK
from props import *

TAU = 2 * math.pi

# ----------------------------------------------------------------------------- captions + timing from SRT
def parse_srt(p):
    out = []
    for b in open(p, encoding="utf-8").read().strip().split("\n\n"):
        ln = b.strip().split("\n")
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", ln[1]); g = [int(x) for x in m.groups()]
        out.append((g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000, g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000, " ".join(ln[2:])))
    return out

SRT = parse_srt(os.path.join(HERE, "voiceover.srt"))
CAPS = SRT
VO_LEN = 516.84
TOTAL = 520.0          # 3.2 s end card after the last word
def C(n): return SRT[n - 1][0]

# ----------------------------------------------------------------------------- chapter timeline bar (top)
CHAPTERS = [(0.0, "THE DROP"), (41.16, "THE FILES"), (109.56, "THE WAR"), (186.24, "THE VOTE"), (228.84, "THE ESCAPE"),
            (272.04, "NOT OVER"), (330.8, "JANUARY"), (424.12, "YOUR WALLET")]
_RAISE = {"on": False}

def timeline(c, t):
    if t >= VO_LEN: return
    x0, x1, y = 40, W - 40, 22
    n = len(CHAPTERS); bounds = [a for a, _ in CHAPTERS] + [VO_LEN]
    cur = max(i for i, (a, _) in enumerate(CHAPTERS) if a <= t)
    c.select_font_face("Patrick Hand"); c.set_font_size(17)
    segw = (x1 - x0) / n
    for i, (a, name) in enumerate(CHAPTERS):
        sx = x0 + i * segw
        rrect(c, sx + 3, y, segw - 6, 22, 7)
        c.set_source_rgba(0, 0, 0, .45); c.fill()
        fr = 1.0 if i < cur else (0.0 if i > cur else clamp((t - a) / (bounds[i + 1] - a)))
        if fr > 0:
            rrect(c, sx + 3, y, max(14, (segw - 6) * fr), 22, 7)
            c.set_source_rgba(.95, .79, .3, .9 if i == cur else .55); c.fill()
        e = c.text_extents(name)
        c.move_to(sx + segw / 2 - e.width / 2 - e.x_bearing, y + 16)
        c.set_source_rgb(.08, .08, .08) if i <= cur else c.set_source_rgba(1, 1, 1, .85)
        c.show_text(name); c.new_path()

_orig_caps = SC.captions
def _captions(c, t, caps):
    timeline(c, t)
    if _RAISE["on"]:
        c.save(); c.translate(0, -70); _orig_caps(c, t, caps); c.restore()
    else:
        _orig_caps(c, t, caps)
    _RAISE["on"] = False
SC.captions = _captions

_orig_fb = SC.frame_bytes
def _frame_bytes(surf, t, fi, gray):   # gray == 2: clip frame, already graded -> pass through untouched
    if gray == 2:
        return np.ndarray((H, W, 4), np.uint8, surf.get_data()).copy()
    return _orig_fb(surf, t, fi, gray)
SC.frame_bytes = _frame_bytes

# ----------------------------------------------------------------------------- shot registry
SHOTS = []; SFX = []; CLIP_SFX = []
def at(t, gray=0, sfx=(), whoosh=True):
    def deco(fn):
        k = len(SHOTS)
        def run(c, u, d, f, fn=fn, k=k): fn(c, u, d, f, k)
        run.__name__ = fn.__name__ if fn.__name__ != "_" else f"shot{k}"
        SHOTS.append((t, run, gray))
        if whoosh: SFX.append((t, "whoosh"))
        for dt, name in sfx: SFX.append((t + dt, name))
        return fn
    return deco

def clip(t, name, offset=0.0, zoom=None, folder="news_shots", sfx=True, hold=True):
    path = os.path.join(HERE, folder, name + ".mp4")
    def _(c, u, d, f, k, path=path, offset=offset, zoom=zoom):
        _RAISE["on"] = True
        paint_clip(c, path, offset + u, zoom)
    _.__name__ = "clip_" + name
    at(t, gray=2, whoosh=(folder == "maps"))(_)
    w = os.path.join(HERE, folder, name + "_sfx.wav")
    if sfx and os.path.exists(w): CLIP_SFX.append((t, w, offset))

def have(name, folder="news_shots"): return os.path.exists(os.path.join(HERE, folder, name + ".mp4"))

PRES = "PRESIDENT TRUMP"
def T(c, x, s, u, f, act=A_rest, ground=600, **kw):
    kw.setdefault("expr", "neutral")
    s = s * 0.82
    K.rob(c, x, ground, s, act(u + kw.pop("ph", 0)), f, u, who="trump", **kw)
def N(c, x, s, u, f, name=None, ground=600, act=A_rest, **kw):
    nt = kw.pop("name_t", prog(u, .2, .5)); kw.pop("talk", None); kw.pop("expr", None)
    K.npc(c, x, ground, s, act(u + kw.pop("ph", 0)), f, u=u, name=name, name_t=nt, **kw)

def road_bg(c, u, f, night=False):
    sky(c, "#9fd0ef", "#eef6fb") if not night else sky(c, "#0d1530", "#2a2f4a")
    c.rectangle(-800, 560, 2900, 400); c.set_source_rgb(.3, .3, .33); c.fill()
    c.rectangle(-800, 540, 2900, 24); c.set_source_rgb(.55, .7, .4); c.fill()
    for x in range(-800, 2100, 160): c.rectangle(x + (u * 60) % 160, 640, 80, 10); c.set_source_rgb(.95, .85, .3); c.fill()

def title_card(c, u, txt, color="#f2c94c", bg=(.05, .05, .06), size=64, speed=1.2, sub=None):
    c.set_source_rgb(*bg); c.paint()
    n = int(len(txt) * clamp(u / max(.2, len(txt) / 26 / speed)))
    text(c, txt[:n], 640, 340, size, color=color)
    if sub and u > .5: text(c, sub, 640, 420, 34, color="#cccccc")

def date_tag(c, s, u, x=1100, y=110, t0=0.1):
    label(c, s, x, y, 34, prog(u, t0, t0 + .3), fill="#f2c94c")

def big_word(c, u, s, color="#1a1a1a", y=360, size=120, t0=0.0, fill=None):
    k = pop(u, t0, .4)
    if k <= 0: return
    c.save(); c.translate(640, y); c.scale(k, k); text(c, s, 0, 0, size, color=color); c.restore()

def lift_cam(u, d, a=(640, 360, 1.0), b=(640, 360, 1.12)):
    k = ease_io(clamp(u / max(d, .01)))
    return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))

def doc_page(c, x, y, s, u, hl_lines=(), tag=None, redacted=False, t0=0.2):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-0.03)
    c.rectangle(-230, -300, 460, 600); fill_stroke(c, "#fbf8f0", 6)
    for i in range(14):
        yy = -250 + i * 36; w = 380 if i % 4 else 300
        c.rectangle(-190, yy, w, 12); c.set_source_rgba(0, 0, 0, .25); c.fill()
        if i in hl_lines:
            kk = ease_io(prog(u, t0 + .3 * hl_lines.index(i), t0 + .3 * hl_lines.index(i) + .3))
            if kk > 0:
                c.rectangle(-196, yy - 8, (w + 12) * kk, 28); c.set_source_rgba(1, .88, .3, .8); c.fill()
                if tag and kk >= 1: label(c, tag, -190 + w + 40, yy + 6, 26, 1.0, rot=0)
            if redacted:
                c.rectangle(-60, yy - 6, 160, 24); c.set_source_rgb(.05, .05, .05); c.fill()
    c.restore()

# ============================================================================= THE DROP  0:00 – 0:41
@at(C(1), sfx=[(0.3, "pop")], whoosh=False)
def _(c, u, d, f, k):
    cam(c, *lift_cam(u, d, (700, 360, 1.0), (760, 330, 1.15)))
    road_bg(c, u, f)
    gas_sign(c, 940, 600, .62, "$3.07")
    N(c, 380, .36, u, f, act=A_walk, hair="#3a2a1a", outfit=("bag",), name_t=0)
    date_tag(c, "NOV 2025", u)

@at(C(1) + 2.4, sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    cam(c, 940, 260, 1.5 + .05 * u); road_bg(c, u, f)
    gas_sign(c, 940, 600, .62, "$3.07")
    label(c, "A YEAR AGO", 640, 520, 44, prog(u, .1, .4), fill="#f2c94c")

@at(C(2), sfx=[(0.3, "slam"), (0.5, "boing")])
def _(c, u, d, f, k):
    cam(c, 900, 260, 1.55 + .08 * u); road_bg(c, u, f)
    gas_sign(c, 940, 600, .62, "$4.56", u, flip_t=0.2, old="$3.07", color="#a51d1d")
    glow(c, 940, 250, 400, (1, .2, .1), .2 + .1 * math.sin(u * 8))
    date_tag(c, "SPRING 2026", u, x=640, y=560)

@at(C(2) + 2.35, sfx=[(0.3, "slide"), (0.9, "ding")])
def _(c, u, d, f, k):
    cam(c, 760, 330, 1.2 - .06 * u); road_bg(c, u, f)
    gas_sign(c, 940, 600, .62, "$3.81", u, flip_t=0.6, old="$4.56", color="#2d8a3e")
    k2 = pop(u, 1.4)
    if k2 > 0:
        c.save(); c.translate(560, 230); c.scale(max(1e-3, k2), max(1e-3, k2))
        c.move_to(-50, -80); c.line_to(50, -80); c.line_to(50, 10); c.line_to(90, 10); c.line_to(0, 100); c.line_to(-90, 10); c.line_to(-50, 10); c.close_path()
        fill_stroke(c, "#3fbf5a", 6); c.restore()
        label(c, "UNDER $4 · FIRST TIME SINCE JULY", 560, 380, 30, prog(u, 1.6, 1.9))

@at(C(4), sfx=[(0.2, "pop"), (0.7, "pop"), (1.2, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0 + .05 * u); K.bg_paper(c, u, f)
    text(c, "OIL PRICE", 640, 150, 60)
    for i in range(3):
        kk = pop(u, .2 + i * .5)
        if kk <= 0: continue
        c.save(); c.translate(320 + i * 320, 380); c.scale(kk, kk)
        barrel(c, 0, 120, .55, "")
        c.move_to(-40, -170); c.line_to(40, -170); c.line_to(40, -90); c.line_to(80, -90); c.line_to(0, -10); c.line_to(-80, -90); c.line_to(-40, -90); c.close_path()
        fill_stroke(c, "#d6402f", 6); text(c, f"WEEK {i + 1}", 0, 180, 40)
        c.restore()

@at(C(5), sfx=[(0.4, "ding"), (1.1, "magic")])
def _(c, u, d, f, k):
    cam(c, *lift_cam(u, d, (640, 340, 1.05), (600, 320, 1.2))); road_bg(c, u, f)
    N(c, 520, .4, u, f, act=A_rest, hair="#3a2a1a", expr="happy", name_t=0)
    def inner(c2):
        text(c2, "WAR OVER?", 0, -10, 46, color="#2d8a3e")
    K.bubble(c, 820, 200, 300, 160, u, t0=.3, inner=inner)
    gas_sign(c, 1150, 600, .45, "$3.81")

@at(C(6), sfx=[(0.0, "rewind"), (0.25, "stamp")])
def _(c, u, d, f, k):
    sx, sy = K.shake(u, 9, .6); cam(c, 640 + sx, 340 + sy, 1.2); road_bg(c, u, f)
    N(c, 520, .4, u, f, act=A_shock, hair="#3a2a1a", expr="shock", name_t=0)
    K.stamp(c, 900, 200, .9, u, "NOT EVEN CLOSE", t0=.15)

@at(C(7), sfx=[(0.3, "pop"), (1.6, "boing")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0 + .1 * ease_io(u / d)); K.bg_wall(c, u, f)
    barrel(c, 640, 600, 1.1, "OIL")
    if u > 1.2:
        kk = ease_io(prog(u, 1.2, 1.6))
        c.move_to(560, 420); c.line_to(560 + 160 * kk, 420 - 40 * kk); c.set_source_rgb(.84, .25, .18); c.set_line_width(14); c.stroke()
    K.qmarks(c, 640, 150, u, n=3, color="#d6402f")

@at(C(8), sfx=[(0.3, "click"), (1.4, "stamp")])
def _(c, u, d, f, k):
    cam(c, 640, 330, 1.0 + .06 * u); sky(c, "#cfe4f3", "#f3f1ea")
    capitol(c, 640, 560, .62)
    rrect(c, 900, 120, 300, 170, 14); fill_stroke(c, "#14202e", 6)
    text(c, "WAR VOTE", 1050, 160, 36, color="#ffffff"); text(c, "—", 1050, 230, 80, color="#f2c94c")
    K.stamp(c, 1050, 210, .8, u, "NO VOTE", t0=1.3)

@at(C(9), sfx=[(0.6, "whirr"), (1.6, "thud")])
def _(c, u, d, f, k):
    cam(c, 640, 340, 1.0); sky(c, "#cfe4f3", "#f3f1ea")
    c.save(); c.translate(640, 380); c.rotate(math.pi * ease_io(prog(u, .4, 1.6))); c.translate(-640, -380)
    capitol(c, 640, 560, .6, wash=prog(u, 1.4, 2.4) * .6); c.restore()
    label(c, "ELECTION", 640, 640, 40, prog(u, .2, .5), fill="#f2c94c")

@at(C(9) + 2.45, sfx=[(0.1, "paper"), (0.5, "printer")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.08 - .05 * u); K.bg_paper(c, u, f)
    for i in range(5): paper_stack(c, 200 + i * 220, 640, .8, h=150 + i * 50, seed=i)
    paper_rain(c, u, n=24)
    K.counter(c, 640, 210, 1.0, u, 3000000, t0=.2, dur=1.6, prefix="", suffix=" PAGES", color="#1a1a1a")

@at(C(10), sfx=[(0.4, "click"), (1.4, "ding")])
def _(c, u, d, f, k):
    cam(c, *lift_cam(u, d, (640, 360, 1.0), (640, 330, 1.25))); K.bg_dark(c, u, f)
    doc_page(c, 640, 380, .9, u, hl_lines=(6,), redacted=True, t0=.4)
    K.magnifier(c, 700 + 40 * math.sin(u * 1.5), 360, 1.0)
    label(c, "ONE NAME", 920, 200, 40, prog(u, 1.2, 1.5), fill="#f2c94c")

@at(C(11), sfx=[(0.3, "pop"), (1.0, "marker")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0 + .04 * u); K.bg_paper(c, u, f)
    text(c, "BY THE END YOU'LL KNOW…", 640, 130, 52)
    for i, s in enumerate(("WHY OIL IS FALLING", "WHY THE NEXT 6 WEEKS MATTER", "WHAT GAS HAS TO DO WITH EPSTEIN")):
        kk = pop(u, .3 + i * 1.2)
        if kk <= 0: continue
        c.save(); c.translate(640, 260 + i * 120); c.scale(kk, kk)
        rrect(c, -380, -42, 760, 84, 14); fill_stroke(c, "#ffffff" if i else "#fff3c4", 6)
        text(c, f"{i + 1}. {s}", 0, 0, 40); c.restore()

@at(C(11) + 2.6, sfx=[(0.2, "flip"), (0.6, "flip"), (1.0, "flip"), (1.4, "tick")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_dark(c, u, f, top="#3a1414", bot="#120606")
    wk = min(6, int(u / .3) + 1)
    K.calendar(c, 640, 360, 1.0, "NEXT", f"{wk}", "WEEKS", color="#d6402f", u=u, t0=0)
    glow(c, 640, 360, 420, (1, .2, .1), .15 + .1 * math.sin(u * 6))
    label(c, "MOST DANGEROUS?", 640, 640, 40, prog(u, 1.4, 1.7), fill="#ffd0d0")

@at(C(12) + 2.4, sfx=[(0.3, "pop"), (0.8, "pop"), (1.3, "rip")])
def _(c, u, d, f, k):
    cam(c, *lift_cam(u, d, (640, 360, 1.0), (640, 350, 1.1))); K.bg_wall(c, u, f, top="#5a3d2b", bot="#3d2a1e", floor="#2a1d14")
    c.rectangle(150, 90, 980, 470); fill_stroke(c, "#b78b5b", 8)
    gas_sign(c, 380, 520, .4, "$3.81")
    file_box(c, 900, 470, .9, "EPSTEIN FILES")
    kk = ease_io(prog(u, .9, 1.6))
    if kk > 0:
        c.move_to(450, 230); c.curve_to(600, 160 + 80 * kk, 700, 300, 450 + 400 * kk, 330 - 30 * kk)
        c.set_source_rgb(.8, .1, .1); c.set_line_width(6); c.stroke()
    text(c, "?", 650, 200, 120, color="#d6402f", rot=math.sin(u * 3) * .2)

@at(C(12) + 4.3, sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.1 + .1 * u); K.bg_dark(c, u, f, top="#2a1a12", bot="#0e0806")
    big_word(c, u, "JEFFREY EPSTEIN?", color="#f2c94c", y=330, size=80, t0=.05)

# ============================================================================= THE FILES 0:41 – 1:50
@at(C(14), sfx=[(0.0, "rewind")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_dark(c, u, f, top="#202a3a", bot="#0b0e14")
    K.clock(c, 420, 360, 150, -u * 4)
    K.calendar(c, 860, 360, .9, "JANUARY", "2026", "", color="#2f6fa8", u=u, t0=.3)
    for i in range(6): c.move_to(0, 120 + i * 100); c.line_to(1280, 120 + i * 100 + 20 * math.sin(u * 20 + i)); c.set_source_rgba(1, 1, 1, .05); c.set_line_width(3); c.stroke()

clip(C(15), "01-npr-epstein-3m")

@at(C(15) + 4.0, sfx=[(0.1, "thud"), (0.4, "thud"), (0.7, "thud")])
def _(c, u, d, f, k):
    cam(c, 640, 400, 1.0 + .05 * u); K.bg_wall(c, u, f, top="#d9d2c2", bot="#b8ad94")
    for i in range(6):
        kk = clamp((u - i * .15) / .35)
        x = 300 + (i % 3) * 340; g = 600 - (i // 3) * 175
        c.save(); c.translate(0, -500 * (1 - ease_io(kk))); file_box(c, x, g, 1.1, "EPSTEIN FILES"); c.restore()
    label(c, "JUSTICE DEPARTMENT · 30 JAN", 640, 120, 36, prog(u, .6, .9), fill="#f2c94c")

@at(C(17), sfx=[(0.4 + i * .35, "marker") for i in range(4)])
def _(c, u, d, f, k):
    cam(c, *lift_cam(u, d, (640, 360, 1.0), (620, 340, 1.12))); K.bg_paper(c, u, f)
    doc_page(c, 420, 380, .85, u, hl_lines=(2, 5, 9, 12), tag="THE PRESIDENT", t0=.4)
    T(c, 1000, .36, u, f, expr="neutral", name=PRES, name_t=prog(u, .2, .5))

clip(C(18), "02-npr-not-wrongdoing")

@at(C(18) + 4.0, sfx=[(0.3, "stamp")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_paper(c, u, f)
    doc_page(c, 640, 380, .85, u, hl_lines=(), t0=0)
    K.stamp(c, 640, 360, 1.05, u, "UNTRUE & SENSATIONAL", t0=.25)
    label(c, "SOME CLAIMS · PER JUSTICE DEPT.", 640, 620, 32, prog(u, .9, 1.2))

@at(C(20), sfx=[(0.1, "flip"), (0.9, "news")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_dark(c, u, f, top="#1b2433", bot="#0a0e14")
    K.newspaper(c, 640, 330, 1.25, "EPSTEIN FILES OUT", u, t0=0, spin=True)
    K.breaking_bar(c, u, "THE BIGGEST STORY IN AMERICA", t0=.8)

@at(C(21), sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05 + .1 * u); K.bg_dark(c, u, f)
    K.calendar(c, 640, 360, 1.05, "FEBRUARY", "28", "2026", color="#d6402f", u=u, t0=0.05)

clip(C(21) + 0.893, "map01-strikes", folder="maps")

if have("03-indy-clinton-hours"):
    clip(C(23), "03-indy-clinton-hours")
else:
    @at(C(23), gray=1, sfx=[(0.3, "murmur")])
    def _(c, u, d, f, k):
        cam(c, *lift_cam(u, d, (640, 380, 1.0), (640, 360, 1.12))); K.bg_wall(c, u, f, top="#5b4632", bot="#3a2c20", floor="#2a1f16")
        for i in range(5): suit_figure(c, 220 + i * 210, 330, .55)
        c.rectangle(-200, 330, 1700, 60); fill_stroke(c, "#6b4a2b", 6)
        rrect(c, 470, 480, 340, 40, 8); fill_stroke(c, "#6b4a2b", 5)
        N(c, 640, .36, u, f, act=A_talk, hair="#e6e6e6", name="BILL CLINTON · TESTIFIES ON EPSTEIN", talk=.6, ground=700)
        K.mic(c, 560, 470, .35)
    @at(C(23) + 2.4, sfx=[(0.1, "tick"), (0.6, "tick"), (1.1, "boom")])
    def _(c, u, d, f, k):
        cam(c, 640, 360, 1.0); vgrad(c, "#1a2040", "#05070f")
        K.clock(c, 330, 330, 140, u * 3, txt=None)
        label(c, "HOURS LATER", 330, 540, 40, prog(u, .3, .6), fill="#f2c94c")
        for i in range(3):
            jx = -200 + (u * 520 + i * 140) % 1700
            jet(c, jx, 200 + i * 70, .9)
        label(c, "STRIKES ON IRAN", 900, 560, 40, prog(u, 1.0, 1.3), fill="#ffd0d0")

@at(C(24), sfx=[(0.4, "stamp")])
def _(c, u, d, f, k):
    cam(c, 640, 340, 1.0 + .08 * u); sky(c, "#cfe4f3", "#f3f1ea")
    capitol(c, 640, 600, .65)
    K.stamp(c, 640, 250, .9, u, "NO VOTE IN CONGRESS", t0=.3)

@at(C(24) + 2.8, sfx=[(0.3, "pop"), (0.8, "ping")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); K.bg_wall(c, u, f)
    for i in range(4): N(c, 140 + i * 110, .26, u, f, hair="#6b4a2b", outfit=("suit",), ph=i, name_t=0)
    for i in range(4): N(c, 800 + i * 110, .26, u, f, hair="#3a2a1a", outfit=("suit",), ph=i + 3, name_t=0)
    label(c, "REPUBLICANS", 300, 250, 32, 1, fill="#ffd0d0"); label(c, "DEMOCRATS", 960, 250, 32, 1, fill="#d0e0ff")
    kk = pop(u, .4)
    if kk > 0:
        c.save(); c.translate(640, 170); c.scale(kk, kk); K.bulb(c, 0, 0, 1.0, on=True) if hasattr(K, "bulb") else None; c.restore()
        text(c, "DISTRACTION?", 640, 300, 44, color="#d6402f")

@at(C(26), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, *lift_cam(u, d, (640, 360, 1.0), (600, 330, 1.12))); K.bg_studio_office(c, u, f)
    N(c, 520, .4, u, f, act=A_talk, hair="#8a8a8a", glasses=True, outfit=("suit",), name="REP. THOMAS MASSIE (R-KY)", talk=.5)
    K.mic(c, 700, 420, .4)

@at(C(26) + 2.4, sfx=[(0.3, "slide"), (1.2, "door")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); K.bg_wall(c, u, f)
    K.door(c, 1000, 600, 1.0, u, .9, sign="PUBLIC")
    bx = 300 + 500 * ease_io(prog(u, .2, 1.6))
    file_box(c, bx + 160, 600, .9, "FILES")
    N(c, bx, .34, u, f, act=A_walk, hair="#8a8a8a", glasses=True, outfit=("suit",), name_t=0)
    label(c, "FORCED THE FILES OUT", 640, 130, 40, prog(u, .3, .6), fill="#f2c94c")

clip(C(27), "04-wrap-massie")

@at(C(29), sfx=[(0.3, "pop"), (1.4, "ding")])
def _(c, u, d, f, k):
    cam(c, *lift_cam(u, d, (640, 360, 1.0), (680, 340, 1.12))); K.bg_studio_office(c, u, f)
    N(c, 560, .4, u, f, act=A_talk, hair="#2a1a12", style="long", outfit=("suit",), name="REP. ALEXANDRIA OCASIO-CORTEZ (D-NY)", talk=.5)
    def inner(c2): text(c2, "SAME!", 0, 0, 52, color="#2f6fa8")
    K.bubble(c, 880, 220, 240, 130, u, t0=1.2, inner=inner)

@at(C(30), sfx=[(0.2 + i * .45, "ping") for i in range(4)])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0 + .05 * u); K.bg_dark(c, u, f, top="#20263a", bot="#0c0e16")
    K.phone(c, 640, 370, 1.0, u, [("#OperationEpsteinFury", "#d6402f"), ("Operation Epstein Fury??", "#2f6fa8"), ("#OperationEpsteinFury", "#d6402f"), ("the timing…", "#555555")], t0=.1, step=.5)

@at(C(30) + 2.4, sfx=[(0.3, "murmur")])
def _(c, u, d, f, k):
    cam(c, 640, 400, 1.0); K.bg_city_night(c, u, f)
    K.crowd(c, 60, 1220, 560, rows=2, s=.26, u=u, phones=True)
    label(c, "TRENDING", 640, 140, 44, prog(u, .2, .5), fill="#ffd0d0")

clip(C(31), "05-newsweek-poll")

@at(C(31) + 4.0, sfx=[(0.2, "pop"), (0.9, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.02); K.bg_paper(c, u, f)
    text(c, "WAR = PARTLY A DISTRACTION?", 640, 140, 46)
    poll_bar(c, 260, 300, 600, 52, u, t0=.1, color="#d6402f", lab="YES")
    poll_bar(c, 260, 480, 600, 40, u, t0=.6, color="#555555", lab="NO")
    label(c, "POLL FROM A LEFT-LEANING GROUP · MARCH", 640, 640, 28, prog(u, .9, 1.2))

clip(C(33), "06-wh-true-morons", offset=1.9, zoom=(640, 470, 1.55))

@at(C(33) + 3.6, sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_news(c, u, f)
    N(c, 640, .34, u, f, act=A_talk, hair="#c99a5b", style="long", outfit=("suit",), name="WHITE HOUSE SPOKESPERSON", ground=640)
    podium(c, 640, 700, .62, "WH")
    label(c, "\"RIDICULOUS\"", 1000, 300, 54, prog(u, .3, .6), fill="#ffd0d0")

# ============================================================================= THE WAR 1:50 – 3:06
@at(C(34), sfx=[(0.2, "printer")])
def _(c, u, d, f, k):
    cam(c, 640, 330 + 30 * u, 1.0); K.bg_wall(c, u, f)
    L = 120 + 600 * ease_io(clamp(u / 2.6))
    c.rectangle(500, 100, 280, L); fill_stroke(c, "#fbf8f0", 5)
    text(c, "THE BILL", 640, 140, 44)
    for i in range(int(L / 40) - 2): c.rectangle(530, 190 + i * 40, 160, 10); c.rectangle(720, 190 + i * 40, 40, 10); c.set_source_rgba(0, 0, 0, .3); c.fill()
    label(c, "THE WAR WAS REAL", 980, 300, 38, prog(u, .3, .6), fill="#f2c94c")

@at(C(35), sfx=[(0.3, "pop"), (0.8, "cash")])
def _(c, u, d, f, k):
    cam(c, *lift_cam(u, d, (640, 380, 1.0), (640, 360, 1.12))); K.bg_wall(c, u, f, top="#e9e2d0")
    barrel(c, 500, 600, 1.1, "OIL")
    K.counter(c, 880, 300, 1.2, u, 70, t0=.4, dur=.8, prefix="$")
    label(c, "BEFORE THE WAR", 880, 440, 36, prog(u, 1.0, 1.3))

@at(C(36), sfx=[(0.6, "chain"), (1.6, "slam")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0 + .1 * ease_io(u / d)); sky(c, "#c4dcef", "#eef4f8"); sea(c, u, y=430)
    c.rectangle(-800, 300, 1100, 200); c.set_source_rgb(.85, .72, .5); c.fill()
    c.rectangle(980, 300, 1400, 200); c.set_source_rgb(.85, .72, .5); c.fill()
    hk = ease_io(prog(u, .4, 1.6))
    K.gate(c, 300, 300 + 680 * hk, 560, 200, u, locked=hk > .95)
    label(c, "IRAN'S ONE WEAPON", 640, 150, 44, prog(u, .2, .5), fill="#ffd0d0")

clip(C(37), "map02-hormuz", folder="maps")

@at(C(39), sfx=[(0.3, "pop"), (1.2, "sad")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); sky(c); sea(c, u, y=430)
    n = max(0, 6 - int(u / .3))
    for i in range(n): tanker(c, 120 + i * 210, 500 + (i % 2) * 40, .25, u)
    K.counter(c, 1040, 180, .8, u, 85, t0=0, dur=.01, prefix="", suffix=" SHIPS/DAY") if u < 1.4 else K.counter(c, 1040, 180, .8, 1.6, 0, t0=0, dur=.01, prefix="≈", suffix=" SHIPS")

@at(C(40), sfx=[(0.3, "whirr"), (1.2, "boom")])
def _(c, u, d, f, k):
    sx, sy = K.shake(u, 4, 2.0); cam(c, 640 + sx, 360 + sy, 1.05); K.bg_paper(c, u, f)
    v = clamp(ease_io(prog(u, .2, 1.3)))
    K.gauge(c, 640, 420, 1.6, "SUPPLY DISRUPTION", v, u)
    label(c, "IEA: LARGEST IN HISTORY", 640, 600, 40, prog(u, 1.2, 1.5), fill="#f2c94c")

@at(C(40) + 2.4, sfx=[(0.2, "pop"), (1.1, "boing")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); K.bg_paper(c, u, f)
    line_chart(c, 200, 520, 880, 330, [70, 100, 119, 126], u, t0=.1, dur=1.6, labels=["$70", "", "$119", "$126"], title="OIL, $ PER BARREL")

clip(C(41), "07-abc-oil-126")

@at(C(42), sfx=[(0.3, "slam"), (1.0, "cash")])
def _(c, u, d, f, k):
    cam(c, 900, 280, 1.45); road_bg(c, u, f)
    gas_sign(c, 940, 600, .62, "$3.98", u, flip_t=0.3, old="$2.98", color="#a51d1d")
    label(c, "+$1 IN ONE MONTH", 600, 520, 44, prog(u, .9, 1.2), fill="#ffd0d0")

@at(C(43), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_wall(c, u, f, top="#dce9f2", bot="#bfd3e0")
    c.save(); c.translate(640, 330); c.rotate(math.sin(u * 4) * .1)
    wline(c, [(0, 250), (0, -150)], f); c.move_to(0, -150); c.curve_to(150, -170, 150, -60, 260, -80); c.line_to(260, 30); c.curve_to(150, 50, 150, -60, 0, -40)
    c.close_path(); fill_stroke(c, "#ffffff", 6); c.restore()
    label(c, "CEASEFIRE", 640, 620, 48, prog(u, .2, .5), fill="#f2c94c")

@at(C(43) + 1.45, sfx=[(0.2, "murmur")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.08); K.bg_room(c, u, f, window=False)
    rrect(c, 380, 470, 520, 40, 8); fill_stroke(c, "#6b4a2b", 5)
    N(c, 380, .32, u, f, act=A_talk, hair="#3a2a1a", outfit=("suit",), name_t=0, talk=.4)
    N(c, 900, .32, u, f, act=A_talk, hair="#2a2a2a", beard=True, outfit=("suit",), facing=-1, name_t=0, talk=.4, ph=.7)
    label(c, "TALKS", 640, 140, 48, prog(u, .2, .5), fill="#f2c94c")

@at(C(43) + 2.9, sfx=[(0.2, "paper")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0 + .06 * u); K.bg_paper(c, u, f)
    doc_page(c, 640, 380, .8, u)
    label(c, "DEAL · JUNE", 640, 140, 48, prog(u, .1, .4), fill="#fff3c4")

@at(C(44), sfx=[(0.5, "rip")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_paper(c, u, f)
    sp = 160 * ease_io(prog(u, .5, 1.2))
    c.save(); c.translate(-sp, 0); c.rotate(-.05 * sp / 160); c.rectangle(-1000, -1000, 1640, 3000); c.clip(); doc_page(c, 640, 380, .8, 0); c.restore()
    c.save(); c.translate(sp, 0); c.rotate(.05 * sp / 160); c.rectangle(640, -1000, 2000, 3000); c.clip(); doc_page(c, 640, 380, .8, 0); c.restore()
    label(c, "FELL APART", 640, 640, 44, prog(u, 1.0, 1.3), fill="#ffd0d0")

@at(C(44) + 2.0, sfx=[(0.3, "rope"), (1.2, "rope")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); sky(c); sea(c, u, y=500)
    c.rectangle(-800, 430, 1150, 200); c.set_source_rgb(.85, .72, .5); c.fill(); c.rectangle(930, 430, 1500, 200); c.set_source_rgb(.85, .72, .5); c.fill()
    pull = math.sin(u * 3) * 25
    wline(c, [(220 + pull, 360), (1060 + pull, 360)], f)
    N(c, 180 + pull, .3, u, f, act=A_rest, hair="#3a2a1a", outfit=("suit",), name="USA", ground=430, rot=-.2)
    N(c, 1100 + pull, .3, u, f, act=A_rest, hair="#1a1a1a", beard=True, facing=-1, name="IRAN", ground=430, rot=-.2)
    label(c, "WHO CONTROLS THE STRAIT?", 640, 150, 42, prog(u, .2, .5), fill="#f2c94c")

clip(C(45), "map03-blockade", folder="maps")

@at(C(47), sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_dark(c, u, f)
    K.calendar(c, 640, 360, 1.0, "OCTOBER", "OCT", "2026", color="#7a1f1f", u=u, t0=0.05)

@at(C(47) + 1.6, gray=1, sfx=[(0.1, "boom"), (0.4, "storm")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.08 + .05 * u); sky(c, "#1b2340", "#3b3a4a"); sea(c, u, y=470, night=True)
    tanker(c, 640, 500, .7, u, fire=True)
    label(c, "DEADLIEST MONTH FOR SHIPPING", 640, 130, 40, prog(u, .3, .6), fill="#ffd0d0")

@at(C(48), sfx=[(0.6, "thud")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); sky(c, "#cfe4f3", "#f3f1ea")
    capitol(c, 640, 560, .45)
    kk = clamp((u - .3) / .35); c.save(); c.translate(0, -600 * (1 - ease_io(kk))); file_box(c, 640, 680, 1.4, "EPSTEIN FILES"); c.restore()
    label(c, "STILL HERE", 640, 120, 44, prog(u, 1.0, 1.3), fill="#f2c94c")

clip(C(49), "08-wusf-bondi")

@at(C(49) + 4.0, sfx=[(0.2, "footsteps"), (1.1, "door")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); K.bg_wall(c, u, f, top="#dcd5c4")
    K.door(c, 1040, 600, 1.0, u, .9, sign="EXIT")
    N(c, 600 + 360 * ease_io(clamp(u / 1.6)), .36, u, f, act=A_walk, hair="#e6c27a", style="long", outfit=("suit",), name="PAM BONDI · ATTORNEY GENERAL")

@at(C(51), sfx=[(0.3, "murmur")])
def _(c, u, d, f, k):
    cam(c, *lift_cam(u, d, (640, 380, 1.0), (640, 360, 1.1))); K.bg_wall(c, u, f, top="#5b4632", bot="#3a2c20", floor="#2a1f16")
    rrect(c, 470, 480, 340, 40, 8); fill_stroke(c, "#6b4a2b", 5)
    N(c, 640, .38, u, f, act=A_talk, hair="#4a4a4a", glasses=True, outfit=("suit",), name="HOWARD LUTNICK · COMMERCE SECRETARY", talk=.5, ground=700)
    K.mic(c, 560, 470, .35)

@at(C(51) + 2.4, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); K.bg_wall(c, u, f, top="#5b4632", bot="#3a2c20", floor="#2a1f16")
    for i in range(6): suit_figure(c, 160 + i * 190, 400, .6)
    c.rectangle(-200, 400, 1700, 70); fill_stroke(c, "#6b4a2b", 6)
    label(c, "FIRST SITTING CABINET MEMBER", 640, 560, 40, prog(u, .2, .5), fill="#f2c94c")
    label(c, "QUESTIONED BY CONGRESS", 640, 620, 36, prog(u, .6, .9))

@at(C(52) + .4, sfx=[(0.3, "click")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05 + .06 * u); K.bg_paper(c, u, f)
    file_box(c, 640, 560, 1.4, "EPSTEIN FILES")
    K.magnifier(c, 640 + 60 * math.sin(u * 2), 330, 1.1)
    label(c, "HIS TIES TO EPSTEIN", 640, 120, 40, prog(u, .3, .6), fill="#f2c94c")

@at(C(53), sfx=[(0.2, "cash"), (1.0, "cash"), (1.8, "cash")])
def _(c, u, d, f, k):
    cam(c, 640, 370, 1.05); road_bg(c, u, f)
    rrect(c, 760, 300, 180, 300, 14); fill_stroke(c, "#d6402f", 6)
    rrect(c, 780, 330, 140, 70, 8); fill_stroke(c, "#111111", 4)
    text(c, f"${4.2 * u * 10:,.2f}", 850, 366, 30, color="#ffcf3a")
    N(c, 600, .36, u, f, act=A_rest, hair="#7a5230", expr="worried", name_t=0)
    label(c, "EVERY WEEK, MORE AT THE PUMP", 640, 140, 40, prog(u, .3, .6), fill="#ffd0d0")

@at(C(54), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_paper(c, u, f)
    text(c, "WHO DO AMERICANS BLAME FOR GAS PRICES?", 640, 160, 40)
    poll_bar(c, 260, 360, 600, 63, u, t0=.2, color="#d6402f", lab="THE PRESIDENT")

clip(C(54) + 2.05, "09-pbs-63pct")

# ============================================================================= THE VOTE 3:06 – 3:49
@at(C(55), sfx=[(0.1, "stamp"), (0.6, "bells")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05 + .1 * u); K.bg_dark(c, u, f, top="#132240", bot="#070b16")
    K.calendar(c, 460, 360, .9, "NOVEMBER", "3", "ELECTION DAY", color="#2f6fa8", u=u, t0=0)
    c.save(); c.translate(900, 420); c.scale(max(1e-3, pop(u, .4)), max(1e-3, pop(u, .4)))
    rrect(c, -130, -110, 260, 220, 14); fill_stroke(c, "#ffffff", 6); c.rectangle(-70, -116, 140, 14); c.set_source_rgb(.1, .1, .1); c.fill()
    text(c, "VOTE", 0, 10, 60, color="#2f6fa8"); c.restore()

@at(C(56), sfx=[(0.4, "thud")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_paper(c, u, f)
    K.balance(c, 640, 260, 1.0, "DEM", "GOP", -0.28 * ease_io(prog(u, .2, .9)), u)
    label(c, "NOT CLOSE", 640, 640, 50, prog(u, 1.0, 1.3), fill="#f2c94c")

@at(C(57), sfx=[(0.2, "whoosh"), (0.8, "ding")])
def _(c, u, d, f, k):
    cam(c, 640, 350, 1.0); sky(c, "#cfe4f3", "#f3f1ea")
    capitol(c, 640, 600, .65, wash=prog(u, .1, 1.2) * .35)
    label(c, "HOUSE → DEMOCRATS", 640, 120, 46, prog(u, .3, .6), fill="#d0e0ff")

@at(C(58), sfx=[(0.2 + i * .12, "pop") for i in range(9)])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_paper(c, u, f)
    text(c, "SENATE SEATS FLIPPED", 640, 140, 50)
    for i in range(9):
        kk = pop(u, .2 + i * .12)
        if kk <= 0: continue
        c.save(); c.translate(200 + i * 110, 360); c.scale(kk, kk); c.arc(0, 0, 44, 0, TAU); fill_stroke(c, "#2f6fa8", 6); text(c, str(i + 1), 0, 2, 40, color="#ffffff"); c.restore()
    label(c, "MOST IN NEARLY 70 YEARS", 640, 560, 44, prog(u, 1.3, 1.6), fill="#f2c94c")

clip(C(58) + 1.3, "10-yahoo-senate-9")

@at(C(59), sfx=[(0.2, "pop"), (0.6, "ding")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); K.bg_paper(c, u, f)
    text(c, "SENATE", 640, 120, 54)
    for i in range(100):
        a = math.pi + (i % 25) / 24 * math.pi; r = 160 + (i // 25) * 50
        x = 640 + math.cos(a) * r; y = 520 + math.sin(a) * r
        on = i < int(100 * ease_io(prog(u, .2, 1.4)))
        c.arc(x, y, 14, 0, TAU); c.set_source_rgb(*((.18, .44, .66) if (on and i < 56) else (.75, .22, .2) if on else (.85, .85, .85))); c.fill()
    K.counter(c, 640, 600, .7, u, 56, t0=1.2, dur=.6, prefix="", suffix=" DEM SEATS", color="#2f6fa8")

@at(C(59) + 2.6, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_paper(c, u, f)
    text(c, "HOUSE", 640, 140, 54)
    K.counter(c, 640, 360, 1.3, u, 250, t0=.2, dur=1.2, prefix="", suffix="+", color="#2f6fa8")
    label(c, "DEMOCRATIC SEATS", 640, 520, 40, prog(u, .8, 1.1))

@at(C(60), sfx=[(0.1, "sea"), (0.5, "whoosh")])
def _(c, u, d, f, k):
    cam(c, 640, 350, 1.0 + .06 * u); sky(c, "#cfe4f3", "#f3f1ea")
    capitol(c, 640, 600, .65, wash=prog(u, .1, 2.4) * .9)
    label(c, "BIGGEST BLUE WAVE SINCE WATERGATE", 640, 110, 40, prog(u, .6, .9), fill="#d0e0ff")

@at(C(61), sfx=[(0.3, "thud")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.05); K.bg_wall(c, u, f)
    rrect(c, 510, 360, 260, 240, 14); fill_stroke(c, "#ffffff", 6); c.rectangle(570, 354, 140, 14); c.set_source_rgb(.1, .1, .1); c.fill()
    yy = 60 + 290 * ease_io(prog(u, .1, .7))
    c.save(); c.translate(640, yy); jet(c, 0, 0, 1.0); c.restore()
    label(c, "THE WAR", 640, 130, 44, prog(u, .1, .4), fill="#ffd0d0")

clip(C(62) + .35, "11-reuters-71pct")

@at(C(62) + 4.35, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_paper(c, u, f)
    text(c, "PASS A LAW TO END THE WAR?", 640, 140, 46)
    poll_bar(c, 260, 320, 600, 71, u, t0=.1, color="#2f6fa8", lab="ALL AMERICANS")
    poll_bar(c, 260, 500, 600, 51, u, t0=.5, color="#c0392b", lab="REPUBLICANS")
    label(c, "REUTERS / IPSOS", 640, 640, 28, prog(u, .8, 1.1))

@at(C(63) + 1.0, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 400, 1.0 + .05 * u); K.bg_city_night(c, u, f)
    K.crowd(c, 60, 1220, 560, rows=2, s=.26, u=u)
    label(c, "INCLUDING ABOUT HALF OF REPUBLICANS", 640, 150, 38, prog(u, .2, .5), fill="#ffd0d0")

@at(C(64), sfx=[(0.1, "tick"), (0.6, "tick"), (1.1, "tick")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.1 + .2 * u); K.bg_dark(c, u, f)
    K.clock(c, 640, 330, 170, u * 2)
    label(c, "ONE WEEK LATER", 640, 560, 44, prog(u, .2, .5), fill="#f2c94c")

@at(C(65), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, *lift_cam(u, d, (640, 330, 1.0), (640, 300, 1.12))); K.bg_news(c, u, f)
    podium(c, 640, 660, .75, "")
    T(c, 640, .4, u, f, act=A_talk, expr="determined", talk=.85, ground=520, name=PRES, name_t=prog(u, .2, .5))

@at(C(65) + 2.5, sfx=[(0.1, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_news(c, u, f)
    T(c, 300, .36, u, f, act=A_talk, expr="determined", talk=.6)
    K.quote_card(c, 820, 330, 640, "…militarily… effectively over.", "the President, Nov 2026", u + 1.6, t0=0)

@at(C(66), sfx=[(0.3, "stamp")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); vgrad(c, "#9fc3e0", "#e6eff6")
    for i in range(3): jet(c, 300 + i * 340, 280 + (i % 2) * 60, 1.1)
    c.move_to(160, 160); c.line_to(1120, 480); c.set_source_rgb(.84, .2, .2); c.set_line_width(16); c.stroke()
    label(c, "NEW STRIKES: \"NOT NEEDED\"", 640, 600, 44, prog(u, .3, .6), fill="#f2c94c")

clip(C(67), "12-cnbc-brent-90", offset=0.84)
clip(C(68), "13-aaa-under-4", offset=1.5)

# ============================================================================= THE ESCAPE 3:49 – 4:32
@at(C(69), sfx=[(0.3, "boing")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_paper(c, u, f)
    line_chart(c, 200, 520, 600, 300, [126, 136, 110, 90], 3, labels=["", "", "", "$90"], title="OIL")
    N(c, 1020, .36, u, f, act=A_shrug, hair="#3a2a1a", expr="worried", name_t=0)
    K.qmarks(c, 1020, 120, u, n=2, color="#d6402f")

@at(C(70), sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0 + .08 * u); K.bg_paper(c, u, f)
    kk = ease_io(prog(u, .1, .7))
    c.move_to(640, 360); c.arc(640, 360, 200, -math.pi / 2, -math.pi / 2 + math.pi * kk); c.close_path(); fill_stroke(c, "#f2c94c", 6)
    c.arc(640, 360, 200, 0, TAU); c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
    big_word(c, u, "PARTLY.", y=640, size=70, t0=.2)

@at(C(71), sfx=[(0.3, "click"), (1.6, "ding")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); vgrad(c, "#1d1a24", "#08070b")
    mx = 300 + 700 * ease_io(clamp(u / 2.6))
    c.save(); c.arc(mx, 360, 150, 0, TAU); c.clip()
    K.bg_paper(c, u, f); text(c, "THE REAL REASON", 640, 360, 70, color="#d6402f"); c.restore()
    K.magnifier(c, mx + 40, 380, 1.3)
    label(c, "MOST PEOPLE MISSED THIS", 640, 620, 40, prog(u, .3, .6), fill="#f2c94c")

@at(C(72), sfx=[(0.2, "slide")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); K.bg_wall(c, u, f)
    K.door(c, 960, 600, 1.0, u, .8 * ease_io(prog(u, .1, .6)), sign="EXIT")
    barrel(c, 300 + 600 * ease_io(prog(u, .3, 1.6)), 600, .7, "OIL", rot=math.sin(u * 10) * .08)
    label(c, "ANOTHER WAY OUT", 640, 140, 44, prog(u, .2, .5), fill="#f2c94c")

clip(C(73), "map04-escape", folder="maps")
clip(C(77), "14-cnbc-80pct")

@at(C(78), sfx=[(0.3, "engine")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); road_bg(c, u, f)
    gas_sign(c, 1100, 600, .5, "$4.40")
    N(c, 500, .36, u, f, act=A_walk, hair="#7a5230", name_t=0)
    label(c, "TOO EXPENSIVE → USE LESS", 600, 150, 40, prog(u, .3, .6), fill="#ffd0d0")

@at(C(78) + 2.1, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_paper(c, u, f)
    text(c, "WORLD OIL DEMAND, 2026", 640, 140, 46)
    K.counter(c, 640, 330, 1.2, u, 27, t0=.1, dur=.9, prefix="−", suffix="00,000 BARRELS A DAY", color="#d6402f") if False else None
    k2 = pop(u, .2); c.save(); c.translate(640, 340); c.scale(max(1e-3, k2), max(1e-3, k2))
    rrect(c, -420, -80, 840, 160, 18); fill_stroke(c, "#ffffff", 7); text(c, "−2.7 MILLION BARRELS / DAY", 0, 0, 56, color="#d6402f"); c.restore()
    label(c, "IEA ESTIMATE", 640, 520, 32, prog(u, .7, 1.0))

@at(C(79), sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_dark(c, u, f, top="#1b2a3a", bot="#0a1016")
    K.calendar(c, 640, 360, 1.0, "NOVEMBER", "13", "IEA REPORT", color="#2f6fa8", u=u, t0=0.05)

clip(C(79) + 1.7, "15-spg-surplus")

@at(C(80) + .12, sfx=[(0.3, "thud")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_paper(c, u, f)
    K.balance(c, 640, 260, 1.0, "SUPPLY", "DEMAND", 0.26 * ease_io(prog(u, .2, 1.0)), u)
    label(c, "FIRST TIME SINCE THE WAR BEGAN", 640, 640, 40, prog(u, 1.0, 1.3), fill="#f2c94c")

@at(C(81), sfx=[(0.2, "slide")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_paper(c, u, f)
    line_chart(c, 200, 520, 880, 320, [136, 120, 105, 90], u, t0=0, dur=1.2, labels=["$136", "", "", "$90"], title="OIL FALLING", color="#2d8a3e")

@at(C(82), sfx=[(0.3, "stamp")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_dark(c, u, f)
    big_word(c, u, "WAR ENDED?", color="#ffffff", y=320, size=90, t0=.05)
    if u > .7:
        c.move_to(330, 250); c.line_to(950, 400); c.set_source_rgb(.84, .2, .2); c.set_line_width(18); c.stroke()

@at(C(82) + 1.8, sfx=[(0.3, "whoosh"), (1.0, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_space(c, u, f)
    K.globe(c, 640, 360, 250, u)
    c.arc(700, 330, 50, 0, TAU); c.set_source_rgba(.9, .15, .1, .55 + .2 * math.sin(u * 6)); c.fill()
    kk = ease_io(prog(u, .2, 1.4))
    c.arc(700, 330, 110, math.pi * .9, math.pi * (.9 + 1.2 * kk)); c.set_source_rgb(1, .85, .3); c.set_line_width(8); c.stroke()
    label(c, "LEARNED TO LIVE AROUND IT", 640, 650, 40, prog(u, .6, .9), fill="#f2c94c")

# ============================================================================= NOT OVER 4:32 – 5:31
clip(C(83), "16-gcaptain-65pct", offset=1.0)
clip(C(83) + 2.96, "map06-tankers-hit", folder="maps", offset=1.4)
clip(C(86), "map05-carriers", folder="maps")

@at(C(87), sfx=[(0.3, "murmur")])
def _(c, u, d, f, k):
    cam(c, *lift_cam(u, d, (640, 380, 1.0), (640, 360, 1.1))); K.bg_dark(c, u, f, top="#1d2a20", bot="#0a120c")
    rrect(c, 300, 420, 680, 60, 10); fill_stroke(c, "#3d5a3a", 6)
    N(c, 330, .34, u, f, act=A_point, hair="#3a2a1a", outfit=("suit",), name_t=0, ground=620)
    N(c, 950, .34, u, f, act=A_rest, hair="#5a5a5a", outfit=("suit",), facing=-1, name_t=0, ground=620)
    label(c, "CBS NEWS REPORTS", 640, 120, 36, prog(u, .1, .4), fill="#ffffff")
    label(c, "US + ISRAEL CONSIDERING NEW ASSAULT", 640, 180, 36, prog(u, .5, .8), fill="#ffd0d0")

@at(C(87) + 2.6, gray=1, sfx=[(0.2, "storm")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); vgrad(c, "#0d1020", "#2a2f3f")
    for i in range(4): jet(c, -100 + (u * 380 + i * 300) % 1600, 180 + i * 70, .8)
    label(c, "CONSIDERING", 640, 560, 44, prog(u, .3, .6), fill="#ffd0d0")

@at(C(88), sfx=[(0.2, "paper")] + [(0.6 + i * .25, "pop") for i in range(7)])
def _(c, u, d, f, k):
    cam(c, 640, 330 + 40 * u / d, 1.0); K.bg_wall(c, u, f, top="#e9e2d0")
    L = 120 + 470 * ease_io(clamp(u / .8))
    c.rectangle(440, 60, 400, L); fill_stroke(c, "#f6edd5", 6)
    text(c, "IRAN'S CONDITIONS", 640, 100, 38)
    for i in range(7):
        if u > .6 + i * .25:
            txt = "1. END THE US BLOCKADE" if i == 0 else f"{i + 1}. ……………"
            text(c, txt, 470, 160 + i * 62, 34, align="l", color="#b3201b" if i == 0 else "#1a1a1a")

@at(C(88) + 2.8, sfx=[(0.4, "chain")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); sky(c, "#c4dcef", "#eef4f8"); sea(c, u, y=430)
    c.rectangle(-800, 300, 1100, 200); c.set_source_rgb(.85, .72, .5); c.fill(); c.rectangle(980, 300, 1400, 200); c.set_source_rgb(.85, .72, .5); c.fill()
    K.gate(c, 300, 980, 560, 200, u, locked=True)
    label(c, "STRAIT STAYS SHUT UNTIL THE BLOCKADE ENDS", 640, 150, 34, prog(u, .3, .6), fill="#f2c94c")

@at(C(90), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 340, 1.0 + .06 * u); sky(c, "#cfe4f3", "#f3f1ea")
    capitol(c, 640, 600, .6)
    label(c, "SENATE VOTE: LIMIT WAR POWERS", 640, 130, 40, prog(u, .3, .6), fill="#f2c94c")

@at(C(90) + 2.4, sfx=[(0.3, "pop"), (1.4, "stamp")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_dark(c, u, f)
    scoreboard(c, 640, 330, 1.0, 48, 51, u, t0=0)
    K.stamp(c, 640, 540, .8, u, "REJECTED", t0=1.3)

@at(C(93), sfx=[(0.2, "boom"), (0.4, "paper")])
def _(c, u, d, f, k):
    sx, sy = K.shake(u, 6, 1.0); cam(c, 640 + sx, 380 + sy, 1.0); K.bg_wall(c, u, f)
    for i in range(3): file_box(c, 340 + i * 300, 600, 1.0, "EPSTEIN FILES")
    paper_rain(c, u * 1.5, n=30, seed=4)
    label(c, "ROARING BACK", 640, 120, 50, prog(u, .3, .6), fill="#ffd0d0")

@at(C(93) + 2.2, sfx=[(0.1, "flip"), (0.8, "news")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_dark(c, u, f, top="#1b2433", bot="#0a0e14")
    K.newspaper(c, 640, 330, 1.2, "EPSTEIN FILES: NEW HOUSE PUSH", u, t0=0, spin=True)

@at(C(94), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_studio_office(c, u, f)
    N(c, 460, .38, u, f, act=A_point, hair="#8a8a8a", glasses=True, outfit=("suit",), name="REP. THOMAS MASSIE")
    n = int(218 * ease_io(prog(u, .2, 1.4)))
    rrect(c, 760, 200, 300, 330, 10); fill_stroke(c, "#fbf8f0", 6)
    text(c, "PETITION", 910, 240, 38); text(c, f"{n}/218", 910, 400, 64, color="#2d8a3e" if n >= 218 else "#1a1a1a")

clip(C(94) + 1.6, "18-axios-massie-218")

@at(C(95), sfx=[(0.3, "bells")])
def _(c, u, d, f, k):
    cam(c, 640, 340, 1.0); sky(c, "#cfe4f3", "#f3f1ea")
    capitol(c, 640, 600, .6)
    label(c, "FORCES A NEW HOUSE VOTE", 640, 130, 42, prog(u, .2, .5), fill="#f2c94c")

@at(C(95) + 2.7, sfx=[(0.3, "chain"), (1.2, "lock")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.05); K.bg_wall(c, u, f, top="#cfc8b8")
    rrect(c, 470, 180, 340, 420, 10); fill_stroke(c, "#7d8590", 7)
    for i in range(3): rrect(c, 500, 210 + i * 130, 280, 110, 8); fill_stroke(c, "#9aa2ad", 5); rrect(c, 600, 250 + i * 130, 80, 20, 6); fill_stroke(c, "#555555", 3)
    for i in range(2):
        c.move_to(450, 230 + i * 260); c.line_to(830, 330 + i * 160); c.set_source_rgb(.35, .35, .35); c.set_line_width(14); c.stroke()
    label(c, "RECORDS STILL HELD BACK?", 640, 120, 40, prog(u, .4, .7), fill="#ffd0d0")

@at(C(96), sfx=[(0.3, "murmur")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); K.bg_wall(c, u, f)
    for i in range(5): suit_figure(c, 180 + i * 230, 600, .9, dark=False)
    label(c, "SURVIVORS + LAWMAKERS", 640, 130, 40, prog(u, .2, .5), fill="#f2c94c")

@at(C(97), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, *lift_cam(u, d, (640, 360, 1.0), (600, 340, 1.1))); K.bg_studio_office(c, u, f)
    N(c, 560, .4, u, f, act=A_talk, hair="#e6c27a", style="long", outfit=("suit",), name="MARJORIE TAYLOR GREENE", talk=.5)
    label(c, "ONCE A LOUD ALLY", 900, 220, 36, prog(u, .6, .9), fill="#ffd0d0")

clip(C(97) + 1.8, "19-yahoo-greene")

@at(C(99) - 1.04, sfx=[(0.4, "stamp")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_paper(c, u, f)
    big_word(c, u, "HER CLAIM", y=280, size=90, t0=.05)
    K.stamp(c, 640, 460, .9, u, "NOT PROVEN", t0=.6)

@at(C(99) + 2.2, sfx=[(0.3, "crack"), (0.9, "rip")])
def _(c, u, d, f, k):
    cam(c, 640, 400, 1.0); K.bg_wall(c, u, f, top="#f0dcd6", bot="#d8bdb4")
    sp = 220 * ease_io(prog(u, .3, 1.3))
    for i in range(4): N(c, 200 + i * 100 - sp, .26, u, f, hair="#6b4a2b", outfit=("suit",), ph=i, name_t=0)
    for i in range(4): N(c, 780 + i * 100 + sp, .26, u, f, hair="#c99a5b", outfit=("suit",), ph=i + 2, name_t=0, facing=-1)
    c.move_to(640, 260); c.line_to(620, 380); c.line_to(660, 460); c.line_to(630, 620); c.set_source_rgb(*INK); c.set_line_width(8 * prog(u, .3, .6)); c.stroke()
    label(c, "HIS OWN SIDE, SPLIT", 640, 120, 44, prog(u, .3, .6), fill="#ffd0d0")

# ============================================================================= JANUARY 5:31 – 7:04
@at(C(101), sfx=[(0.3, "thunder")])
def _(c, u, d, f, k):
    cam(c, *lift_cam(u, d, (640, 360, 1.0), (640, 340, 1.08))); K.bg_wall(c, u, f, top="#c9d3dc", bot="#aab5bf")
    T(c, 640, .4, u, f, act=A_rest, expr="worried", name=PRES, name_t=prog(u, .1, .4))
    for i, (lab, x) in enumerate((("WAR", 330), ("FILES", 950))):
        kk = pop(u, .3 + i * .4)
        if kk <= 0: continue
        c.save(); c.translate(x + math.sin(u + i) * 10, 170); c.scale(kk, kk)
        for dx, dy, r in ((-60, 10, 60), (0, -20, 75), (60, 10, 60)): c.arc(dx, dy, r, 0, TAU); c.set_source_rgb(.35, .37, .42); c.fill()
        text(c, lab, 0, 10, 46, color="#ffffff"); c.restore()

@at(C(101) + 2.2, sfx=[(0.2, "flip"), (1.0, "thunder")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_dark(c, u, f)
    K.calendar(c, 640, 400, 1.0, "JANUARY", "2027", "", color="#2f6fa8", u=u, t0=0)
    for i, lab in enumerate(("WAR", "FILES")):
        x = (200 + 300 * ease_io(clamp(u / 1.6))) if i == 0 else (1080 - 300 * ease_io(clamp(u / 1.6)))
        for dx, dy, r in ((-50, 10, 50), (0, -15, 62), (50, 10, 50)): c.arc(x + dx, 150 + dy, r, 0, TAU); c.set_source_rgb(.35, .37, .42); c.fill()
        text(c, lab, x, 158, 40, color="#ffffff")

@at(C(102), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 400, 1.0); K.bg_city_night(c, u, f)
    K.crowd(c, 60, 1220, 560, rows=2, s=.26, u=u)
    poll_bar(c, 300, 180, 540, 71, u, t0=.1, color="#2f6fa8", lab="WANT IT ENDED")

@at(C(103), sfx=[(0.6, "creak")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0 + .06 * u); sky(c, "#cfe4f3", "#f3f1ea")
    capitol(c, 360, 600, .38, wash=.3)
    c.save(); c.translate(860, 600); file_box(c, 0, 0, 1.4, "EPSTEIN FILES")
    a = ease_io(prog(u, .4, 1.4)); c.save(); c.translate(-180, -240); c.rotate(-a * 1.1); c.rectangle(0, 0, 364, 42); fill_stroke(c, "#b89458", 6); c.restore()
    if a > .5: glow(c, 0, -280, 200, (1, .95, .6), .4)
    c.restore()
    label(c, "WANTS THEM OPENED", 640, 120, 42, prog(u, .3, .6), fill="#f2c94c")

@at(C(104), sfx=[(0.2, "stamp")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05 + .1 * u); K.bg_dark(c, u, f, top="#132240", bot="#070b16")
    K.calendar(c, 640, 360, 1.05, "JANUARY", "3", "NEW CONGRESS", color="#2f6fa8", u=u, t0=0.05)

@at(C(104) + 2.0, sfx=[(0.4, "bells")])
def _(c, u, d, f, k):
    cam(c, 640, 340, 1.0); sky(c, "#cfe4f3", "#f3f1ea")
    capitol(c, 640, 600, .65, wash=.25)
    for i in range(6): suit_figure(c, 200 + i * 180, 700, .6, dark=False)
    label(c, "SWORN IN · DEMOCRATS IN CHARGE", 640, 120, 40, prog(u, .2, .5), fill="#d0e0ff")

@at(C(105), sfx=[(0.4, "boom")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_dark(c, u, f, top="#2a1a12", bot="#0e0806")
    big_word(c, u, "THE POWER THAT MATTERS MOST", color="#f2c94c", y=300, size=56, t0=.05)

@at(C(105) + 1.9, sfx=[(0.2, "whoosh"), (0.6, "stamp")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0 + .05 * u); K.bg_paper(c, u, f)
    for i in range(5):
        kk = clamp((u - i * .15) / .5)
        envelope(c, -200 + (840 + i * 30) * ease_io(kk), 200 + i * 70, .7 + .1 * (i == 2), txt="SUBPOENA", rot=(i - 2) * .12)
    label(c, "SUBPOENAS", 640, 640, 50, prog(u, .6, .9), fill="#f2c94c")

clip(C(106), "20-npr-subpoena", offset=0.68)

def _checklist(c, u, n_on, t0=0.0, items=("GOING TO WAR WITHOUT CONGRESS", "HANDLING OF THE EPSTEIN FILES", "THE PRESIDENT'S BUSINESS INTERESTS")):
    K.bg_paper(c, u, 0)
    rrect(c, 260, 100, 760, 520, 18); fill_stroke(c, "#fffdf6", 7)
    text(c, "TO INVESTIGATE", 640, 160, 52, color="#b3201b")
    for i, s in enumerate(items):
        y = 270 + i * 120
        rrect(c, 300, y - 32, 64, 64, 10); fill_stroke(c, "#ffffff", 6)
        if i < n_on:
            kk = ease_io(prog(u, t0, t0 + .4)) if i == n_on - 1 else 1
            c.move_to(312, y); c.line_to(330, y + 20 * kk); c.line_to(330 + 40 * kk, y - 30 * kk); c.set_source_rgb(.18, .55, .25); c.set_line_width(10); c.stroke()
            text(c, s, 390, y, 36, align="l")

@at(C(107), sfx=[(0.3, "paper")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0 + .04 * u); _checklist(c, u, 0)

@at(C(108), sfx=[(0.2, "marker")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); _checklist(c, u, 1, t0=.1)
    jet(c, 980, 270, .8)

@at(C(108) + 2.0, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 340, 1.0); sky(c, "#cfe4f3", "#f3f1ea")
    capitol(c, 640, 600, .6)
    big_word(c, u, "NOT ASKED", color="#d6402f", y=140, size=70, t0=.2)

@at(C(109), sfx=[(0.2, "marker")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); _checklist(c, u, 2, t0=.1)

@at(C(110), sfx=[(0.2, "marker")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); _checklist(c, u, 3, t0=.1)

@at(C(111), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, *lift_cam(u, d, (640, 360, 1.0), (600, 340, 1.1))); K.bg_studio_office(c, u, f)
    N(c, 560, .4, u, f, act=A_talk, hair="#1a1a1a", skin="#8d5a3b", glasses=True, outfit=("suit",), name="REP. GREGORY MEEKS · TOP DEMOCRAT, FOREIGN AFFAIRS", talk=.5)

clip(C(111) + 2.44, "21-cbs-meeks")

@at(C(112) + 1.8, sfx=[(0.3, "creak"), (1.4, "clank")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_wall(c, u, f)
    money_valve(c, 640, 360, 1.0, u, turn=ease_io(prog(u, .3, 1.6)))
    label(c, "CUT OFF MONEY FOR THE WAR", 640, 130, 40, prog(u, .2, .5), fill="#f2c94c")

@at(C(113), sfx=[(0.2, "type")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0 + .05 * u); K.bg_paper(c, u, f)
    c.rectangle(380, 80, 520, 600); fill_stroke(c, "#fbf8f0", 6)
    text(c, "SPENDING BILL", 640, 130, 44)
    for i in range(6): c.rectangle(420, 190 + i * 40, 440, 10); c.set_source_rgba(0, 0, 0, .25); c.fill()
    s = "NO FUNDS FOR WAR WITH IRAN"; n = int(len(s) * clamp((u - .4) / 1.6))
    c.rectangle(410, 450, 460, 60); c.set_source_rgba(1, .88, .3, .7 if n else 0); c.fill()
    text(c, s[:n], 640, 480, 32, color="#b3201b")
    label(c, "MUST-PASS", 1040, 200, 40, prog(u, .3, .6), fill="#f2c94c")

@at(C(113) + 2.6, sfx=[(0.3, "whoosh")])
def _(c, u, d, f, k):
    cam(c, 640, 340, 1.0); sky(c, "#cfe4f3", "#f3f1ea")
    capitol(c, 640, 600, .65, wash=.25 + .05 * math.sin(u * 3))
    label(c, "HOUSE + SENATE", 640, 120, 46, prog(u, .2, .5), fill="#d0e0ff")

@at(C(114), sfx=[(0.3, "stamp")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); K.bg_paper(c, u, f)
    K.bills(c, 640, 380, u, n=12, seed=2, spread=600)
    K.stamp(c, 640, 360, 1.0, u, "NOT FOR IRAN", t0=.4)

@at(C(115), sfx=[(0.2, "thud")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_dark(c, u, f)
    c.save(); c.translate(640, 330); c.scale(max(1e-3, pop(u, .05)), max(1e-3, pop(u, .05)))
    for i in range(8):
        a = i * TAU / 8 + TAU / 16; c.line_to(math.cos(a) * 170, math.sin(a) * 170)
    c.close_path(); fill_stroke(c, "#c0392b", 10, "#ffffff"); text(c, "LIMITS", 0, 0, 64, color="#ffffff"); c.restore()

@at(C(116), sfx=[(0.6, "stamp")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_news(c, u, f)
    T(c, 380, .4, u, f, act=A_point, expr="determined", name=PRES, name_t=prog(u, .1, .4))
    K.stamp(c, 880, 300, 1.1, u, "VETO", t0=.5)

@at(C(116) + 2.2, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_paper(c, u, f)
    text(c, "TO OVERRIDE A VETO", 640, 140, 50)
    poll_bar(c, 230, 330, 640, 67, u, t0=.1, color="#555555", lab="NEEDED: 2/3", big=False)
    poll_bar(c, 230, 520, 640, 56, u, t0=.5, color="#2f6fa8", lab="DEMOCRATS ALONE", big=False)
    c.move_to(230 + 640 * .67, 260); c.line_to(230 + 640 * .67, 580); c.set_dash([12, 10]); c.set_source_rgb(.8, .2, .2); c.set_line_width(5); c.stroke(); c.set_dash([])

@at(C(118), sfx=[(0.3, "cash"), (1.2, "sea")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); sky(c); sea(c, u, y=430)
    for i in range(3): carrier(c, 250 + i * 390, 470 + (i % 2) * 40, .3, u)
    K.bills(c, 640, 200, u, n=8, seed=5, spread=900)
    label(c, "MONEY KEEPS THEM AT SEA", 640, 640, 40, prog(u, .3, .6), fill="#f2c94c")

clip(C(118) + 2.4, "17-aj-third-carrier", offset=1.56)

@at(C(119), sfx=[(0.2, "flip"), (0.7, "flip"), (1.2, "flip"), (1.8, "tick")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_dark(c, u, f, top="#2a1a12", bot="#0e0806")
    days = ["NOV 21", "DEC 1", "DEC 11", "DEC 25", "JAN 3"]
    i = min(4, int(u / .55))
    K.calendar(c, 520, 360, .9, days[i].split()[0], days[i].split()[1], "", color="#d6402f" if i < 4 else "#2f6fa8", u=u, t0=0)
    K.hourglass(c, 930, 360, 1.0, u)

@at(C(120), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); K.bg_studio_office(c, u, f)
    N(c, 400, .36, u, f, act=A_point, hair="#3a2a1a", glasses=True, name="ANALYSTS", talk=.4)
    line_chart(c, 640, 480, 460, 220, [1, 2, 4, 3], u, t0=.2, dur=1.2, color="#d6402f", title="RISK")

@at(C(120) + 2.4, sfx=[(0.3, "slide"), (1.2, "boom")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_paper(c, u, f)
    c.move_to(140, 380); c.line_to(1140, 380); c.set_source_rgb(*INK); c.set_line_width(8); c.stroke()
    for x, s in ((180, "NOW"), (1080, "JAN 3")):
        c.arc(x, 380, 18, 0, TAU); fill_stroke(c, "#ffffff", 6); text(c, s, x, 440, 40)
    kk = pop(u, .6)
    if kk > 0:
        c.save(); c.translate(640, 300); c.scale(kk, kk); jet(c, 0, 0, 1.2); c.restore()
        label(c, "BIG MOVE? BEFORE THIS", 640, 200, 36, prog(u, .9, 1.2), fill="#ffd0d0")
    c.rectangle(1080, 330, 200, 100); c.set_source_rgba(.17, .4, .85, .25); c.fill()
    label(c, "NEW CONGRESS", 1080, 300, 30, 1, fill="#d0e0ff")

@at(C(121), sfx=[(0.3, "flip")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_dark(c, u, f, top="#132240", bot="#070b16")
    K.calendar(c, 640, 360, 1.0, "JANUARY", "3", "NEW CONGRESS", color="#2f6fa8", u=u, t0=.05)
    jet(c, 300 + 200 * u, 180, .8)

@at(C(122), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_tvset(c, u, f)
    T(c, 640, .4, u, f, act=A_talk, expr="neutral", talk=.6, name=PRES, name_t=prog(u, .1, .4))
    label(c, "ISRAELI TV", 1060, 120, 34, prog(u, .2, .5), fill="#f2c94c")

@at(C(122) + 2.0, sfx=[(0.1, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_tvset(c, u, f)
    T(c, 300, .36, u, f, act=A_talk, expr="smug", talk=.6)
    K.quote_card(c, 820, 330, 640, "I'm not rushing to make any decisions on Iran.", "the President", u + 1.8, t0=0)

clip(C(123), "22-cbs-new-year")

@at(C(124), sfx=[(0.3, "pop"), (0.8, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_paper(c, u, f)
    K.calendar(c, 420, 360, .8, "NOVEMBER", "29", "", color="#2d8a3e", u=u, t0=.2)
    K.calendar(c, 860, 360, .8, "DECEMBER", "11", "", color="#d6402f", u=u, t0=.6)

@at(C(125), sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05 + .05 * u); K.bg_dark(c, u, f, top="#1d2a20", bot="#0a120c")
    K.calendar(c, 640, 360, 1.0, "NOVEMBER", "29", "OPEC+ MEETS", color="#2d8a3e", u=u, t0=.05)

@at(C(125) + 2.6, sfx=[(0.2, "whirr"), (1.4, "pour")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); K.bg_desert(c, u, f)
    for i in range(3):
        x = 260 + i * 380; a = math.sin(u * 2.4 + i) * .3
        c.rectangle(x - 10, 400, 20, 200); fill_stroke(c, "#555555", 4)
        c.save(); c.translate(x, 400); c.rotate(a); c.rectangle(-150, -16, 300, 32); fill_stroke(c, "#d6402f", 5)
        c.move_to(150, -30); c.line_to(200, 0); c.line_to(150, 30); c.close_path(); fill_stroke(c, "#d6402f", 5); c.restore()
        wline(c, [(x + 150, 400 + 150 * math.sin(a)), (x + 150, 600)], f)
    label(c, "HOW MUCH TO PUMP IN 2027?", 640, 130, 40, prog(u, .2, .5), fill="#f2c94c")

@at(C(126), sfx=[(0.2, "pour")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0 + .05 * u); K.bg_wall(c, u, f, top="#e9e2d0")
    for i in range(5): barrel(c, 260 + i * 190, 600, .7, "2027" if i == 2 else "")
    label(c, "OUTPUT FOR NEXT YEAR", 640, 140, 40, prog(u, .1, .4), fill="#f2c94c")

if have("23-newsweek-dec11"):
    clip(C(127), "23-newsweek-dec11")
else:
    @at(C(127), sfx=[(0.2, "pop")])
    def _(c, u, d, f, k):
        cam(c, 640, 360, 1.05 + .05 * u); K.bg_dark(c, u, f, top="#3a1414", bot="#120606")
        K.calendar(c, 640, 360, 1.0, "DECEMBER", "11", "FUNDING RUNS OUT", color="#d6402f", u=u, t0=.05)

@at(C(127) + 4.16 if not have("23-newsweek-dec11") else C(127) + 4.0, sfx=[(0.3, "rope"), (1.4, "rope")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); sky(c, "#cfe4f3", "#f3f1ea")
    capitol(c, 980, 600, .4, wash=.25)
    pull = math.sin(u * 3) * 20
    wline(c, [(380 + pull, 380), (820 + pull, 380)], f)
    T(c, 330 + pull, .34, u, f, act=A_rest, expr="determined", rot=-.15, name=PRES, name_t=prog(u, .1, .4))
    label(c, "PRESSURE TO END THE WAR", 640, 130, 40, prog(u, .3, .6), fill="#f2c94c")

if not have("23-newsweek-dec11"):
    @at(C(127) + 2.0, sfx=[(0.3, "creak")])
    def _(c, u, d, f, k):
        cam(c, 640, 360, 1.0); K.bg_wall(c, u, f)
        money_valve(c, 640, 380, .9, u, turn=.3 * math.sin(u * 2))
        label(c, "DEMOCRATS' LEVERAGE", 640, 130, 40, prog(u, .2, .5), fill="#d0e0ff")

# ============================================================================= YOUR WALLET 7:04 – end
clip(C(129), "map07-three-roads", folder="maps")

@at(C(131), sfx=[(0.2, "pop"), (0.45, "pop"), (0.7, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 400, 1.0); sky(c, "#b9dbf2", "#eef6fb"); three_roads(c, u + .5, lit=None)
    label(c, "1. A DEAL", 250, 140, 40, prog(u, 1.0, 1.3), fill="#d6f5dd")

@at(C(131) + 2.24, sfx=[(0.3, "creak"), (1.2, "cash")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); sky(c); sea(c, u, y=430)
    c.rectangle(-800, 300, 1100, 200); c.set_source_rgb(.85, .72, .5); c.fill(); c.rectangle(980, 300, 1400, 200); c.set_source_rgb(.85, .72, .5); c.fill()
    hk = 1 - ease_io(prog(u, .1, .9))
    K.gate(c, 300, 300 + 680 * hk + 1, 560, 200, u, locked=False)
    tanker(c, -300 + 900 * ease_io(prog(u, .5, 2.3)), 500, .35, u, tracker=True)
    label(c, "REOPENS · EVEN WITH A TOLL", 640, 140, 40, prog(u, .3, .6), fill="#f2c94c")

@at(C(132), sfx=[(0.3, "slide")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_paper(c, u, f)
    line_chart(c, 200, 520, 880, 320, [90, 84, 78, 74], u, t0=.1, dur=1.4, labels=["$90", "", "", "$70s"], title="CALMER FORECASTS", color="#2d8a3e", ymin=60, ymax=100)

@at(C(132) + 2.7, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.05); K.bg_wall(c, u, f, top="#e9e2d0")
    barrel(c, 500, 600, 1.1, "OIL")
    K.counter(c, 880, 300, 1.2, u, 70, t0=.2, dur=.6, prefix="≈$")
    label(c, "WHERE IT WAS BEFORE THE WAR", 880, 440, 32, prog(u, .7, 1.0))

@at(C(133), sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 400, 1.0); sky(c, "#b9dbf2", "#eef6fb"); three_roads(c, 3, lit=1)
    label(c, "2. NOTHING CHANGES", 640, 120, 40, prog(u, .1, .4), fill="#fff1cf")

@at(C(133) + 2.0, gray=0, sfx=[(0.3, "sea")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); sky(c, "#0d1530", "#232a45"); sea(c, u, y=440, night=True); K.stars(c, 640, 150, 600, 40, u) if hasattr(K, "stars") else None
    for i in range(3): tanker(c, -300 + (u * 220 + i * 520) % 1900, 500 + i * 30, .3, u, dark=True, tracker=False)
    label(c, "A FROZEN WAR · SHIPS SLIP THROUGH IN THE DARK", 640, 130, 32, prog(u, .3, .6), fill="#f2c94c")

@at(C(134), sfx=[(0.3, "clank")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); K.bg_paper(c, u, f)
    K.gauge(c, 640, 440, 1.6, "OIL PRICE", .55 + .01 * math.sin(u * 20), u)
    label(c, "STUCK AROUND HERE", 640, 600, 40, prog(u, .3, .6), fill="#f2c94c")

@at(C(135), sfx=[(0.2, "thunder")])
def _(c, u, d, f, k):
    cam(c, 640, 400, 1.0); sky(c, "#4a4f63", "#8a8f9f"); three_roads(c, 3, lit=2)
    label(c, "3. THE STRIKES START AGAIN", 640, 120, 40, prog(u, .1, .4), fill="#ffd0d0")

@at(C(135) + 2.3, gray=1, sfx=[(0.2, "storm")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); vgrad(c, "#0d1020", "#2a2f3f")
    for i in range(4): jet(c, -100 + (u * 420 + i * 320) % 1600, 200 + i * 60, .9)
    capitol(c, 1120, 720, .25)
    label(c, "BEFORE THE NEW CONGRESS ARRIVES", 640, 600, 36, prog(u, .3, .6), fill="#ffd0d0")

@at(C(136), sfx=[(0.3, "boing"), (1.2, "boom")])
def _(c, u, d, f, k):
    sx, sy = K.shake(u, 5, 2.0) if u > 1.0 else (0, 0); cam(c, 640 + sx, 360 + sy, 1.0); K.bg_paper(c, u, f)
    line_chart(c, 200, 560, 880, 400, [90, 100, 125, 150], u, t0=.1, dur=1.4, labels=["$90", "", "", "$150?"], title="IF IT ESCALATES", color="#d6402f", ymin=60, ymax=160)

@at(C(137), sfx=[(0.3, "pop"), (0.9, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); K.bg_street(c, u, f)
    K.bg_bank(c, u, f) if False else None
    for x, nm in ((330, "BANK A"), (950, "BANK B")):
        c.rectangle(x - 170, 250, 340, 350); fill_stroke(c, "#e8e1d2", 6)
        c.move_to(x - 200, 250); c.line_to(x, 150); c.line_to(x + 200, 250); c.close_path(); fill_stroke(c, "#e8e1d2", 6)
        for i in range(4): c.rectangle(x - 140 + i * 80, 280, 26, 300); c.set_source_rgba(0, 0, 0, .12); c.fill()
        label(c, nm, x, 210, 30, 1)
    def q(c2): text(c2, "$78!", 0, 0, 44, color="#2d8a3e")
    def q2(c2): text(c2, "$100!", 0, 0, 44, color="#d6402f")
    K.bubble(c, 500, 140, 180, 100, u, t0=.3, inner=q, tail=(-60, 60)); K.bubble(c, 780, 140, 180, 100, u, t0=.9, inner=q2, tail=(60, 60))

@at(C(138), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_paper(c, u, f)
    K.counter(c, 640, 330, 1.3, u, 78, t0=.1, dur=.6, prefix="$", color="#2d8a3e")
    label(c, "BNP PARIBAS · JAN–MAR 2027", 640, 480, 36, prog(u, .3, .6))

clip(C(138) + 1.2, "24-bnp-78")

@at(C(139), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.05); K.bg_paper(c, u, f)
    K.counter(c, 640, 330, 1.3, u, 100, t0=.05, dur=.6, prefix="$", color="#d6402f")
    label(c, "MORGAN STANLEY", 640, 480, 36, prog(u, .2, .5))

@at(C(140), sfx=[(0.3, "pop"), (1.0, "ding")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_paper(c, u, f)
    for x, v, col in ((360, "$78", "#2d8a3e"), (920, "$100", "#d6402f")):
        rrect(c, x - 140, 180, 280, 140, 16); fill_stroke(c, "#ffffff", 6); text(c, v, x, 250, 80, color=col)
    kk = ease_io(prog(u, .4, 1.0))
    c.move_to(500, 400); c.line_to(500 + 280 * kk, 400); c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
    if kk >= 1:
        text(c, "$22 GAP", 640, 450, 60, color="#1a1a1a")
        label(c, "= THE PRICE OF NOT KNOWING", 640, 560, 36, prog(u, 1.2, 1.5), fill="#f2c94c")

@at(C(140) + 2.3, sfx=[(0.3, "wind")])
def _(c, u, d, f, k):
    cam(c, 640, 340, 1.0 + .06 * u); sky(c, "#b8c2cc", "#e2e6ea")
    capitol(c, 640, 600, .6)
    for i in range(8):
        c.arc(-200 + (u * 80 + i * 240) % 1700, 250 + (i % 3) * 120, 140, 0, TAU); c.set_source_rgba(1, 1, 1, .35); c.fill()
    K.qmarks(c, 640, 150, u, n=4, color="#555555")

@at(C(141), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 400, 1.0); sky(c, "#b9dbf2", "#eef6fb"); three_roads(c, 3, lit=None, prices=("DIESEL ↑", "DIESEL ↑", "DIESEL ↑"))
    label(c, "ON EVERY ROAD", 640, 120, 44, prog(u, .3, .6), fill="#f2c94c")

@at(C(141) + 2.1, sfx=[(0.2, "slide")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.2 - .1 * u); road_bg(c, u, f)
    rrect(c, 500, 200, 280, 400, 16); fill_stroke(c, "#1b6b2e", 7)
    rrect(c, 530, 230, 220, 100, 8); fill_stroke(c, "#111111", 4); text(c, "DIESEL", 640, 280, 46, color="#ffcf3a")
    c.move_to(780, 300); c.curve_to(900, 300, 920, 420, 860, 500); c.set_source_rgb(*INK); c.set_line_width(14); c.stroke()

@at(C(142), sfx=[(0.05, "boom")])
def _(c, u, d, f, k):
    title_card(c, u, "DIESEL", color="#ffcf3a", size=130, speed=6)

@at(C(143), sfx=[(0.1, "engine")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); road_bg(c, u * 3, f)
    truck(c, -200 + 1100 * ease_io(clamp(u / 2.4)), 660, .55, u, cargo="GROCERIES")
    label(c, "DIESEL MOVES YOUR FOOD", 640, 130, 40, prog(u, .3, .6), fill="#f2c94c")

@at(C(144), sfx=[(0.3, "boom")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); vgrad(c, "#5a5f6a", "#a8adb5")
    for i in range(4):
        x = 250 + i * 250; c.rectangle(x - 50, 300 - i * 20, 100, 300 + i * 20); fill_stroke(c, "#8a8f99", 6)
        for j in range(4): c.arc(x + math.sin(u + j) * 20, 260 - i * 20 - ((u * 70 + j * 60) % 220), 40 + j * 8, 0, TAU); c.set_source_rgba(.2, .2, .22, .35); c.fill()
    c.rectangle(-500, 600, 2300, 200); c.set_source_rgb(.3, .3, .32); c.fill()
    label(c, "REFINERIES HIT HARDER THAN CRUDE", 640, 120, 38, prog(u, .3, .6), fill="#ffd0d0")

@at(C(144) + 2.0, sfx=[(0.3, "sea")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); sky(c); sea(c, u, y=430)
    tanker(c, 640, 500, .6, u, hull="#2f6fa8")
    label(c, "FUEL SHIPMENTS", 640, 130, 44, prog(u, .3, .6), fill="#f2c94c")

clip(C(145), "25-eia-diesel")
clip(C(146), "26-ap-thanksgiving")

@at(C(147), sfx=[(0.1, "type")], whoosh=False)
def _(c, u, d, f, k):
    title_card(c, u, "ARE OIL PRICES FINALLY DROPPING?", size=56, speed=2.4)

@at(C(148), sfx=[(0.05, "ding")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_paper(c, u, f)
    big_word(c, u, "YES.", color="#2d8a3e", size=180, t0=0)

@at(C(149), sfx=[(0.3, "stamp")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_dark(c, u, f)
    big_word(c, u, "WAR OVER?", color="#ffffff", y=320, size=90, t0=.05)
    if u > .6: c.move_to(330, 250); c.line_to(950, 400); c.set_source_rgb(.84, .2, .2); c.set_line_width(18); c.stroke()

@at(C(150), sfx=[(0.3, "whoosh")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0); K.bg_space(c, u, f)
    K.globe(c, 640, 360, 250, u)
    c.arc(700, 330, 50, 0, TAU); c.set_source_rgba(.9, .15, .1, .6); c.fill()
    kk = ease_io(prog(u, .1, 1.8))
    c.arc(700, 330, 110, math.pi * .9, math.pi * (.9 + 1.3 * kk)); c.set_source_rgb(1, .85, .3); c.set_line_width(8); c.stroke()
    label(c, "THE WORLD FOUND A WAY AROUND IT", 640, 650, 36, prog(u, .4, .7), fill="#f2c94c")

@at(C(151), sfx=[(0.3, "engine")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.05); K.bg_wall(c, u, f, top="#cfe0ee", bot="#aac2d6")
    c.save(); c.translate(640, 360); c.rotate(math.sin(u * 2) * .4 + .6 * ease_io(prog(u, .5, 1.5)))
    c.arc(0, 0, 200, 0, TAU); c.set_source_rgb(*INK); c.set_line_width(36); c.stroke()
    for a in (0, 2.1, 4.2): c.move_to(0, 0); c.line_to(math.cos(a) * 190, math.sin(a) * 190); c.set_line_width(26); c.stroke()
    c.arc(0, 0, 40, 0, TAU); c.fill(); c.restore()
    label(c, "VOTERS TOOK THE WHEEL", 640, 640, 44, prog(u, .3, .6), fill="#d0e0ff")

@at(C(151) + 2.3, sfx=[(0.3, "whoosh")])
def _(c, u, d, f, k):
    cam(c, 640, 340, 1.0); sky(c, "#cfe4f3", "#f3f1ea")
    capitol(c, 640, 600, .65, wash=.3 + .04 * math.sin(u * 3))

@at(C(152), gray=1, sfx=[(0.3, "wind")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0 + .05 * u); vgrad(c, "#9aa2ad", "#d5d9de")
    c.save(); c.translate(640, 640); c.scale(3.2, -.5); file_box(c, 0, 0, 1.0, ""); c.restore()
    c.rectangle(-800, 0, 2900, 720); c.set_source_rgba(0, 0, 0, .0); c.fill()
    for i in range(3): jet(c, 300 + i * 340, 360 + (i % 2) * 40, 1.0)
    c.rectangle(-800, 420, 2900, 400); c.set_source_rgba(0, 0, 0, .35); c.fill()
    label(c, "IN THE SHADOW OF THE FILES", 640, 120, 40, prog(u, .3, .6), fill="#f2c94c")

@at(C(153), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    cam(c, 640, 380, 1.0); sky(c, "#b9dbf2", "#eef6fb")
    c.rectangle(-800, 380, 2900, 900); c.set_source_rgb(.45, .62, .32); c.fill()
    for i, (ex, lab, col) in enumerate(((330, "ENDED", "#3fa86b"), (950, "ESCALATED", "#d6402f"))):
        c.move_to(560 + i * 40, 760); c.line_to(ex - 50, 400); c.line_to(ex + 50, 400); c.line_to(640 + i * 80, 760); c.close_path(); c.set_source_rgb(.33, .33, .36); c.fill()
        label(c, lab, ex, 330, 44, prog(u, .3 + i * .5, .6 + i * .5), fill=col)
    capitol(c, 640, 360, .28)

@at(C(153) + 2.2, sfx=[(0.3, "bells")])
def _(c, u, d, f, k):
    cam(c, 640, 340, 1.0 + .06 * u); sky(c, "#a9c4dc", "#e6eef5")
    capitol(c, 640, 600, .65, wash=.25)
    label(c, "THE NEW CONGRESS · COMING TO OPEN THEM", 640, 120, 36, prog(u, .2, .5), fill="#d0e0ff")

for i, (top, big, col) in enumerate((("NOVEMBER", "29", "#2d8a3e"), ("DECEMBER", "11", "#d6402f"), ("JANUARY", "3", "#2f6fa8"))):
    def _mk(i=i, top=top, big=big, col=col):
        @at(C(154) + i * 1.9, sfx=[(0.1, "stamp")])
        def _(c, u, d, f, k):
            cam(c, 640, 360, 1.0 + .05 * u); K.bg_paper(c, u, f)
            for j, (t2, b2, c2) in enumerate((("NOVEMBER", "29", "#2d8a3e"), ("DECEMBER", "11", "#d6402f"), ("JANUARY", "3", "#2f6fa8"))):
                if j > i: continue
                K.calendar(c, 260 + j * 380, 360, .75 if j == i else .62, t2, b2, "", color=c2, u=u if j == i else 5, t0=.05)
            if i == 2: label(c, "WATCH THESE THREE DATES", 640, 640, 40, prog(u, .5, .8), fill="#f2c94c")
    _mk()

@at(C(155), sfx=[(0.3, "magic")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0 + .05 * u); sky(c, "#f6b26b", "#ffe6c2"); sea(c, u, y=470)
    glow(c, 640, 470, 300, (1, .8, .4), .4)
    c.arc(640, 470, 120, math.pi, TAU); c.set_source_rgb(1, .75, .35); c.fill()
    bx = 300 + 360 * ease_io(clamp(u / 2.6)); by = 260 - 40 * math.sin(u * 2)
    c.save(); c.translate(bx, by); c.scale(1.3, 1.3)
    c.move_to(-80, 6); c.line_to(-110, -14); c.line_to(-104, 14); c.line_to(-112, 30); c.close_path(); fill_stroke(c, "#ffffff", 4)   # tail
    c.save(); c.scale(1.0, .55); c.arc(0, 10, 75, 0, TAU); c.restore(); fill_stroke(c, "#ffffff", 5)                               # body
    c.arc(70, -14, 26, 0, TAU); fill_stroke(c, "#ffffff", 5)                                                                       # head
    c.move_to(94, -16); c.line_to(116, -8); c.line_to(94, -4); c.close_path(); fill_stroke(c, "#f2a33a", 3)                         # beak
    c.arc(76, -20, 4, 0, TAU); c.set_source_rgb(.1, .1, .1); c.fill()
    wa = math.sin(u * 9) * .55
    c.save(); c.translate(-6, -10); c.rotate(-.5 + wa)
    c.move_to(0, 0); c.curve_to(-30, -60, -10, -120, 40, -130); c.curve_to(30, -80, 50, -30, 40, 0); c.close_path(); fill_stroke(c, "#ffffff", 5); c.restore()
    c.move_to(80, 0); c.curve_to(110, 20, 120, 30, 140, 24); c.set_source_rgb(.3, .55, .2); c.set_line_width(5); c.stroke()      # olive twig
    for lx, ly in ((110, 18), (128, 28)): c.save(); c.translate(lx, ly); c.scale(1, .5); c.arc(0, 0, 9, 0, TAU); c.restore(); c.set_source_rgb(.35, .62, .25); c.fill()
    c.restore()

@at(C(156), sfx=[(0.05, "bells")], whoosh=False)
def _(c, u, d, f, k):
    title_card(c, u, "PEACE!", color="#f2c94c", size=110, speed=3,
               sub="WATCH: 29 NOV · 11 DEC · 3 JAN")

SHOTS.sort(key=lambda s: s[0])
SFX.sort()
OUTDIR = os.path.join(HERE, "out", "fshots")

def _work(i): SC.render_shot(i, SHOTS, TOTAL, CAPS, outdir=OUTDIR)

def build_sfx(out_wav):
    SR = SFXK.SR; mix = np.zeros(int(TOTAL * SR) + SR)
    for i, (t, name) in enumerate(SFX):
        fn = SFXK.BANK.get(name, SFXK.pop); SFXK._place(mix, fn(i), t)
    # the clips' own sound (marker strokes, swooshes), trimmed by the offset each clip starts at
    starts = [s[0] for s in SHOTS] + [TOTAL]
    for t, w, off in CLIP_SFX:
        nxt = min(s for s in starts if s > t + 1e-6)
        with wave.open(w) as wf:
            x = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float64) / 32767; sr = wf.getframerate()
        if sr != SR: x = np.interp(np.arange(0, len(x), sr / SR), np.arange(len(x)), x)
        x = x[int(off * SR): int((off + nxt - t) * SR)]
        SFXK._place(mix, x, t)
    mix = mix[: int(TOTAL * SR)]
    mix = np.tanh(mix * 1.2) / 1.2
    pk = np.abs(mix).max()
    if pk > .89: mix *= .89 / pk
    with wave.open(out_wav, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((mix * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "info"
    nxt = [s[0] for s in SHOTS[1:]] + [TOTAL]
    if cmd == "info":
        durs = [e - s[0] for s, e in zip(SHOTS, nxt)]
        print(len(SHOTS), "shots; mean", round(sum(durs) / len(durs), 2), "max", round(max(durs), 2), "min", round(min(durs), 2))
        for s, dd in zip(SHOTS, durs):
            if dd > 3.6 or dd < 0.7: print("  ", round(s[0], 2), s[1].__name__, round(dd, 2))
    elif cmd == "stills":
        a = float(sys.argv[2]) if len(sys.argv) > 2 else 0; b = float(sys.argv[3]) if len(sys.argv) > 3 else TOTAL
        ts = [s[0] + min(1.4, (e - s[0]) * .7) for s, e in zip(SHOTS, nxt) if a <= s[0] < b]
        SC.stills(ts, SHOTS, TOTAL, CAPS, prefix=os.path.join(HERE, "out", "fs"))
        print(len(ts), "stills")
    elif cmd == "sfx":
        build_sfx(os.path.join(HERE, "out", "sfx.wav")); print("sfx ok")
    elif cmd == "render":
        from multiprocessing import get_context
        from concurrent.futures import ProcessPoolExecutor
        os.makedirs(OUTDIR, exist_ok=True)
        todo = [i for i in range(len(SHOTS)) if not os.path.exists(os.path.join(OUTDIR, f"s{i:02d}.mp4"))]
        def _w(i): SC.render_shot(i, SHOTS, TOTAL, CAPS, outdir=OUTDIR)
        with ProcessPoolExecutor(max_workers=2, mp_context=get_context("fork")) as ex:
            for n, _ in enumerate(ex.map(_work, todo)):
                if n % 10 == 0: print("shot", n, "/", len(todo), flush=True)
        with open(os.path.join(OUTDIR, "list.txt"), "w") as fh:
            for i in range(len(SHOTS)): fh.write(f"file s{i:02d}.mp4\n")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-i", os.path.join(OUTDIR, "list.txt"), "-c", "copy",
                        os.path.join(HERE, "out", "video.mp4")], check=True)
        print("done")
