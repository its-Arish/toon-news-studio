"""Props for the oil / Iran / January episode (house style: flat colours, ink outlines)."""
import math, random, subprocess, os
import numpy as np
import cairo
from toonkit.core import text, rrect, fill_stroke, hexc, ease_io, prog, clamp, W, H, FPS, ease_out_back
from toonkit.rig import wline, INK
from toonkit.scene import label, glow

TAU = 2 * math.pi
def pop(u, a, dur=0.35): return ease_out_back(prog(u, a, a + dur))


# ------------------------------------------------------------------ gas station price sign
def gas_sign(c, x, ground, s, price, u=0.0, flip_t=None, old=None, color="#c0392b"):
    """Tall roadside sign. If old+flip_t given, the digits flip from old to price at flip_t."""
    c.save(); c.translate(x, ground); c.scale(s, s)
    c.rectangle(-18, -560, 36, 560); fill_stroke(c, "#8a8f99", 6)
    rrect(c, -230, -900, 460, 360, 20); fill_stroke(c, color, 8)
    text(c, "GAS", 0, -840, 70, color="#ffffff")
    rrect(c, -200, -780, 400, 200, 14); fill_stroke(c, "#111111", 6)
    shown = price
    if old is not None and flip_t is not None:
        k = prog(u, flip_t, flip_t + 0.5)
        if k < 1:
            shown = old if k < 0.5 else price
            c.save(); c.translate(0, -680); c.scale(1, abs(math.cos(k * math.pi)) + 0.02)
            text(c, shown, 0, 0, 120, color="#ffcf3a"); c.restore(); c.restore(); return
    glow(c, 0, -680, 160, (1, .8, .2), .18)
    text(c, shown, 0, -680, 120, color="#ffcf3a")
    text(c, "REGULAR", 0, -605, 28, color="#ffffff")
    c.restore()


# ------------------------------------------------------------------ oil barrel
def barrel(c, x, ground, s, lab="OIL", color="#2b2b2b", band="#f2c94c", rot=0.0):
    c.save(); c.translate(x, ground); c.scale(s, s); c.rotate(rot)
    rrect(c, -90, -260, 180, 260, 24); fill_stroke(c, color, 7)
    for yy in (-200, -70):
        c.rectangle(-90, yy, 180, 18); c.set_source_rgb(*hexc(band)[:3]); c.fill()
    c.save(); c.translate(0, -260); c.scale(1, .22); c.arc(0, 0, 90, 0, TAU); c.restore(); fill_stroke(c, "#444444", 6)
    if lab: text(c, lab, 0, -135, 46, color="#ffffff")
    c.restore()


# ------------------------------------------------------------------ oil tanker (side view)
def tanker(c, x, y, s, u, fire=False, dark=False, tracker=None, hull="#b03a2e"):
    bob = math.sin(u * 2 + x * 0.01) * 6
    c.save(); c.translate(x, y + bob); c.scale(s, s); c.rotate(math.sin(u * 1.4 + x) * .015)
    deck = "#3a3f47" if dark else "#d9dde3"
    c.move_to(-420, -60); c.line_to(420, -60); c.line_to(380, 60); c.line_to(-400, 60); c.close_path(); fill_stroke(c, "#20242b" if dark else hull, 7)
    c.rectangle(-420, -60, 840, 22); c.set_source_rgb(.15, .15, .17); c.fill()
    for i in range(5):
        c.arc(-280 + i * 120, -78, 34, math.pi, TAU); c.close_path(); fill_stroke(c, deck, 5)
    rrect(c, 250, -190, 120, 130, 8); fill_stroke(c, "#f2f2f2" if not dark else "#555a62", 6)
    for i in range(3): c.rectangle(266 + i * 34, -170, 22, 18); c.set_source_rgb(.25, .45, .65) if not dark else c.set_source_rgb(.15, .15, .2); c.fill()
    c.rectangle(330, -250, 26, 60); fill_stroke(c, "#d6402f", 5)
    if tracker is not None:   # little beacon on the mast: on = green blinking, off = grey with X
        cx, cy = 300, -230
        if tracker:
            on = (u * 2) % 1 < .5
            c.arc(cx, cy, 16, 0, TAU); c.set_source_rgb(.2, .9, .3) if on else c.set_source_rgb(.1, .4, .15); c.fill()
            if on: glow(c, cx, cy, 60, (.3, 1, .4), .5)
        else:
            c.arc(cx, cy, 16, 0, TAU); c.set_source_rgb(.35, .35, .35); c.fill()
            c.move_to(cx - 14, cy - 14); c.line_to(cx + 14, cy + 14); c.move_to(cx + 14, cy - 14); c.line_to(cx - 14, cy + 14)
            c.set_source_rgb(.9, .2, .2); c.set_line_width(6); c.stroke()
    if fire:
        for i in range(7):
            ph = u * 9 + i * 1.7; fx = -120 + i * 30 + math.sin(ph) * 8; h = 90 + 40 * abs(math.sin(ph * .7))
            c.move_to(fx - 26, -70); c.curve_to(fx - 30, -70 - h * .6, fx + 6, -70 - h * .8, fx, -70 - h)
            c.curve_to(fx + 10, -70 - h * .6, fx + 34, -90, fx + 26, -70); c.close_path()
            c.set_source_rgba(1, .45 + .25 * math.sin(ph), .1, .9); c.fill()
        glow(c, -30, -130, 260, (1, .5, .1), .35)
        for i in range(5):
            sy = -220 - ((u * 60 + i * 50) % 260); sx = -40 + math.sin(u + i) * 40 + i * 10
            c.arc(sx, sy, 40 + i * 6, 0, TAU); c.set_source_rgba(.15, .15, .15, .35); c.fill()
    c.restore()


def sea(c, u, y=430, night=False):
    base = (.08, .16, .3) if night else (.16, .38, .62)
    c.rectangle(-800, y, 2900, 1200); c.set_source_rgb(*base); c.fill()
    for i in range(5):
        yy = y + 20 + i * 50
        c.move_to(-800, yy)
        for xx in range(-800, 2100, 40): c.line_to(xx, yy + math.sin(xx / 70 + u * 2 + i) * 6)
        c.set_source_rgba(1, 1, 1, .12 if not night else .06); c.set_line_width(3); c.stroke()


def sky(c, top="#9fd0ef", bot="#e9f4fb"):
    g = cairo.LinearGradient(0, -400, 0, 700); g.add_color_stop_rgb(0, *hexc(top)[:3]); g.add_color_stop_rgb(1, *hexc(bot)[:3])
    c.rectangle(-1000, -1000, 3300, 2700); c.set_source(g); c.fill()


# ------------------------------------------------------------------ aircraft carrier
def carrier(c, x, y, s, u, n_label=None):
    bob = math.sin(u * 1.5 + x * .01) * 4
    c.save(); c.translate(x, y + bob); c.scale(s, s)
    c.move_to(-520, -40); c.line_to(560, -40); c.line_to(470, 80); c.line_to(-470, 80); c.close_path(); fill_stroke(c, "#5f6670", 7)
    c.move_to(-560, -40); c.line_to(600, -40); c.line_to(600, -70); c.line_to(-540, -70); c.close_path(); fill_stroke(c, "#4b5058", 6)
    for i in range(6): c.rectangle(-480 + i * 160, -60, 70, 5); c.set_source_rgb(.95, .95, .95); c.fill()
    rrect(c, 230, -210, 110, 140, 6); fill_stroke(c, "#6b727c", 6)
    c.rectangle(275, -280, 16, 70); fill_stroke(c, "#4b5058", 4)
    for jx in (-380, -180, 40):   # parked jets (simple silhouettes)
        c.save(); c.translate(jx, -88); c.move_to(-60, 0); c.line_to(60, 0); c.line_to(20, -12); c.line_to(-40, -14); c.close_path()
        c.set_source_rgb(.3, .32, .36); c.fill(); c.move_to(-10, -6); c.line_to(-40, -40); c.line_to(-20, -6); c.fill(); c.restore()
    if n_label: label(c, n_label, 0, -150, 44, 1.0)
    c.restore()


# ------------------------------------------------------------------ Capitol
def capitol(c, x, ground, s, wash=0.0, night=False):
    c.save(); c.translate(x, ground); c.scale(s, s)
    body = "#f1ede4" if not night else "#c9c4b8"
    c.rectangle(-460, -170, 920, 170); fill_stroke(c, body, 7)
    for i in range(11): c.rectangle(-420 + i * 80, -150, 22, 150); c.set_source_rgba(0, 0, 0, .12); c.fill()
    c.rectangle(-180, -260, 360, 90); fill_stroke(c, body, 7)
    c.move_to(-210, -260); c.line_to(0, -330); c.line_to(210, -260); c.close_path(); fill_stroke(c, body, 7)
    c.rectangle(-130, -420, 260, 90); fill_stroke(c, body, 7)
    for i in range(9): c.rectangle(-120 + i * 30, -410, 10, 70); c.set_source_rgba(0, 0, 0, .14); c.fill()
    c.move_to(-150, -420); c.curve_to(-150, -600, 150, -600, 150, -420); c.close_path(); fill_stroke(c, body, 7)
    c.rectangle(-14, -620, 28, 70); fill_stroke(c, body, 5)
    c.arc(0, -632, 16, 0, TAU); fill_stroke(c, body, 5)
    if wash > 0:   # blue wave washing over (election)
        h = 700 * ease_io(wash)
        c.move_to(-700, 40)
        for xx in range(-700, 720, 30): c.line_to(xx, 40 - h + math.sin(xx / 60 + wash * 8) * 22)
        c.line_to(700, 40); c.close_path(); c.set_source_rgba(.17, .4, .85, .75); c.fill()
    c.restore()


# ------------------------------------------------------------------ evidence boxes / files
def file_box(c, x, ground, s, lab="FILES", lid=False, color="#c9a56b"):
    c.save(); c.translate(x, ground); c.scale(s, s)
    c.rectangle(-120, -150, 240, 150); fill_stroke(c, color, 6)
    c.rectangle(-130, -170, 260, 30); fill_stroke(c, "#b89458", 6)
    rrect(c, -80, -110, 160, 60, 6); fill_stroke(c, "#ffffff", 4)
    text(c, lab, 0, -80, 30 if len(lab) < 10 else 22)
    c.restore()


def paper_stack(c, x, ground, s, h=300, u=0.0, seed=0):
    rnd = random.Random(seed)
    c.save(); c.translate(x, ground); c.scale(s, s)
    n = int(h / 9)
    for i in range(n):
        dx = rnd.uniform(-10, 10)
        c.rectangle(-110 + dx, -9 * (i + 1), 220, 9); fill_stroke(c, "#fbf8f0" if i % 2 else "#efe9dc", 2)
    c.restore()


def paper_rain(c, u, n=30, seed=1, x0=0, x1=1280):
    rnd = random.Random(seed)
    for i in range(n):
        px = rnd.uniform(x0, x1); sp = rnd.uniform(160, 320); ph = rnd.uniform(0, 4)
        py = -80 + ((u + ph) * sp) % 900
        c.save(); c.translate(px + math.sin(u * 2 + i) * 30, py); c.rotate(math.sin(u * 3 + i) * .6)
        c.rectangle(-30, -40, 60, 80); fill_stroke(c, "#fbf8f0", 3)
        for k in range(4): c.rectangle(-20, -28 + k * 14, 40, 4); c.set_source_rgba(0, 0, 0, .25); c.fill()
        c.restore()


# ------------------------------------------------------------------ simple line chart
def line_chart(c, x, y, w, h, vals, u, t0=0.0, dur=1.6, color="#d6402f", labels=None, ymin=None, ymax=None, title=None, unit="$"):
    ymin = min(vals) * 0.9 if ymin is None else ymin; ymax = max(vals) * 1.05 if ymax is None else ymax
    c.save(); c.translate(x, y)
    rrect(c, -20, -h - 60, w + 40, h + 110, 16); fill_stroke(c, "#ffffff", 6)
    if title: text(c, title, w / 2, -h - 28, 34)
    c.move_to(0, 0); c.line_to(w, 0); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    pts = [(i * w / (len(vals) - 1), -(v - ymin) / (ymax - ymin) * h) for i, v in enumerate(vals)]
    k = ease_io(prog(u, t0, t0 + dur)) * (len(pts) - 1)
    c.move_to(*pts[0])
    for i in range(1, len(pts)):
        if i <= k: c.line_to(*pts[i])
        else:
            fr = k - (i - 1)
            if fr > 0: c.line_to(pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * fr, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * fr)
            break
    c.set_source_rgb(*hexc(color)[:3]); c.set_line_width(9); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
    for i, (px, py) in enumerate(pts):
        if i <= k + 0.01:
            c.arc(px, py, 10, 0, TAU); fill_stroke(c, color, 4)
            if labels and labels[i]:
                text(c, labels[i], px, py - 34, 30)
    c.restore()


# ------------------------------------------------------------------ poll bar (percent)
def poll_bar(c, x, y, w, pct, u, t0=0.0, color="#2f6fa8", lab="", big=True):
    k = ease_io(prog(u, t0, t0 + 1.0))
    c.save(); c.translate(x, y)
    rrect(c, 0, -40, w, 80, 16); fill_stroke(c, "#ffffff", 6)
    if k > 0:
        rrect(c, 6, -34, (w - 12) * pct / 100 * k, 68, 12); c.set_source_rgb(*hexc(color)[:3]); c.fill()
    if big: text(c, f"{int(pct * k)}%", w + 90, 0, 64, color=color)
    if lab: text(c, lab, w / 2, -76, 36)
    c.restore()


# ------------------------------------------------------------------ truck
def truck(c, x, ground, s, u, cargo="GROCERIES", color="#2f6fa8"):
    c.save(); c.translate(x, ground); c.scale(s, s)
    rrect(c, -420, -300, 560, 240, 10); fill_stroke(c, "#f4f1ea", 7)
    text(c, cargo, -140, -180, 56, color=color)
    rrect(c, 150, -240, 220, 180, 22); fill_stroke(c, color, 7)
    rrect(c, 250, -220, 100, 70, 8); fill_stroke(c, "#bfe3f5", 5)
    c.rectangle(-420, -70, 790, 26); fill_stroke(c, "#333333", 5)
    for wx in (-320, -200, 240):
        c.save(); c.translate(wx, -30); c.rotate(u * 8)
        c.arc(0, 0, 52, 0, TAU); fill_stroke(c, "#222222", 6); c.arc(0, 0, 20, 0, TAU); c.set_source_rgb(.7, .7, .7); c.fill()
        c.move_to(0, 0); c.line_to(0, -48); c.set_source_rgb(.5, .5, .5); c.set_line_width(4); c.stroke()
        c.restore()
    c.restore()


# ------------------------------------------------------------------ pipeline
def pipe(c, pts, w=34, color="#8d939c", flow=None, u=0.0):
    c.move_to(*pts[0])
    for p in pts[1:]: c.line_to(*p)
    c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_source_rgb(*INK); c.set_line_width(w + 12); c.stroke_preserve()
    c.set_source_rgb(*hexc(color)[:3]); c.set_line_width(w); c.stroke()
    if flow is not None:  # dashes moving along the pipe
        c.move_to(*pts[0])
        for p in pts[1:]: c.line_to(*p)
        c.set_dash([18, 26], -u * 120); c.set_source_rgba(.1, .1, .1, .7); c.set_line_width(w * .35); c.stroke(); c.set_dash([])


# ------------------------------------------------------------------ three roads
def three_roads(c, u, lit=None, labels=("DEAL", "FROZEN", "STRIKES"), prices=("$70s", "STUCK", "$150?")):
    c.rectangle(-800, 380, 2900, 900); c.set_source_rgb(.45, .62, .32); c.fill()
    base = (640, 760)
    ends = [(250, 400), (640, 390), (1030, 400)]
    cols = ["#3fa86b", "#e1a33a", "#d6402f"]
    for i, (ex, ey) in enumerate(ends):
        c.move_to(base[0] - 120, base[1]); c.line_to(ex - 50, ey); c.line_to(ex + 50, ey); c.line_to(base[0] + 120, base[1]); c.close_path()
        dim = lit is not None and lit != i
        c.set_source_rgb(.33, .33, .36) if not dim else c.set_source_rgb(.25, .25, .27); c.fill()
    for i, (ex, ey) in enumerate(ends):
        k = pop(u, 0.2 + i * 0.25)
        if k <= 0: continue
        c.save(); c.translate(ex, ey - 40); c.scale(k, k)
        wline(c, [(0, 0), (0, -120)], 0, amp=0)
        dim = lit is not None and lit != i
        rrect(c, -120, -230, 240, 110, 12); fill_stroke(c, "#ffffff" if not dim else "#c8c8c8", 6)
        text(c, labels[i], 0, -195, 40, color=cols[i] if not dim else "#888888")
        text(c, prices[i], 0, -150, 34, color="#1a1a1a" if not dim else "#888888")
        c.restore()


# ------------------------------------------------------------------ jets (stylised, no insignia)
def jet(c, x, y, s, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.move_to(80, 0); c.line_to(-60, -14); c.line_to(-80, 0); c.line_to(-60, 14); c.close_path(); fill_stroke(c, "#6b727c", 4)
    c.move_to(10, -6); c.line_to(-30, -50); c.line_to(-40, -6); c.close_path(); fill_stroke(c, "#5a616a", 3)
    c.move_to(10, 6); c.line_to(-30, 50); c.line_to(-40, 6); c.close_path(); fill_stroke(c, "#5a616a", 3)
    c.restore()


# ------------------------------------------------------------------ podium with a seal-like disc (no real seal)
def podium(c, x, ground, s, txt=None, color="#5a3a22"):
    c.save(); c.translate(x, ground); c.scale(s, s)
    c.move_to(-140, 0); c.line_to(-110, -330); c.line_to(110, -330); c.line_to(140, 0); c.close_path(); fill_stroke(c, color, 7)
    c.arc(0, -200, 70, 0, TAU); fill_stroke(c, "#e9d8a6", 5)
    if txt: text(c, txt, 0, -200, 34)
    c.restore()


def envelope(c, x, y, s, txt="SUBPOENA", rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.rectangle(-150, -95, 300, 190); fill_stroke(c, "#f6efdc", 6)
    c.move_to(-150, -95); c.line_to(0, 15); c.line_to(150, -95); c.set_source_rgb(*INK); c.set_line_width(5); c.stroke()
    c.arc(0, 15, 26, 0, TAU); fill_stroke(c, "#b3201b", 4)
    text(c, txt, 0, 62, 34, color="#b3201b")
    c.restore()


def money_valve(c, x, y, s, u, turn=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    pipe(c, [(-500, 0), (500, 0)], w=60, color="#6fa86b")
    c.save(); c.rotate(turn * 4)
    c.arc(0, -10, 110, 0, TAU); c.set_source_rgb(*INK); c.set_line_width(26); c.stroke(); c.arc(0, -10, 110, 0, TAU); c.set_source_rgb(.8, .2, .2); c.set_line_width(16); c.stroke()
    for a in range(4):
        c.move_to(0, -10); c.line_to(math.cos(a * math.pi / 2) * 110, -10 + math.sin(a * math.pi / 2) * 110); c.set_source_rgb(.8, .2, .2); c.set_line_width(14); c.stroke()
    c.restore()
    label(c, "FUNDING", 0, -190, 40, 1.0)
    c.restore()


def scoreboard(c, x, y, s, left, right, u, lt="YES", rt="NO", t0=0.0):
    k = pop(u, t0)
    c.save(); c.translate(x, y); c.scale(s * k, s * k)
    rrect(c, -330, -140, 660, 280, 18); fill_stroke(c, "#14202e", 7)
    for i, (v, t, col) in enumerate(((left, lt, "#3fbf5a"), (right, rt, "#d6402f"))):
        xx = -160 + i * 320
        text(c, t, xx, -80, 40, color="#ffffff"); text(c, str(v), xx, 30, 130, color=col)
    c.restore()


# ------------------------------------------------------------------ video clip player (news + History Map clips)
class _Reader:
    def __init__(self): self.path = None; self.p = None; self.idx = -1; self.last = None
_R = _Reader()

def clip_frame(path, fi):
    """RGB frame number fi of an mp4 (sequential reads are cheap; seeks restart ffmpeg)."""
    R = _R
    if R.path != path or fi < R.idx + 1 or fi > R.idx + 90:
        if R.p: R.p.kill()
        t0 = fi / FPS
        R.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t0:.4f}", "-i", path, "-f", "rawvideo", "-pix_fmt", "bgra",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-"], stdout=subprocess.PIPE)
        R.path = path; R.idx = fi - 1
    while R.idx < fi:
        buf = R.p.stdout.read(W * H * 4)
        if len(buf) < W * H * 4: break
        R.last = np.frombuffer(buf, np.uint8).reshape(H, W, 4).copy(); R.idx += 1
    if R.last is None: R.last = np.zeros((H, W, 4), np.uint8)
    return R.last


def paint_clip(c, path, t, zoom=None):
    arr = clip_frame(path, int(round(t * FPS)))
    surf = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_RGB24, W, H)
    c.save()
    if zoom:  # (cx, cy, z) crop-zoom into the clip
        cx, cy, z = zoom; c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-cx, -cy)
    c.set_source_surface(surf, 0, 0); c.get_source().set_filter(cairo.FILTER_GOOD); c.paint(); c.restore()
