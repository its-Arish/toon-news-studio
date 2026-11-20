"""toonkit.face: expressive face for a hand-drawn head.

The head is split by tools/split_face.py into head_blank.png (no eyes/brows/mouth) plus
eye and brow sprites taken from the original drawing. Here they are put back with motion:
eyes squash (blink, squint) or grow (surprise), brows lift and tilt, the mouth is drawn
in matching ink with shapes from closed smile to wide open.
"""
import os, json, math
import cairo
from .core import clamp, ease_io

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Face:
    def __init__(self, folder):
        d = os.path.join(_ROOT, folder)
        self.blank = cairo.ImageSurface.create_from_png(os.path.join(d, "head_blank.png"))
        self.meta = json.load(open(os.path.join(d, "face.json")))
        self.spr = {k: cairo.ImageSurface.create_from_png(os.path.join(d, f"{k}.png")) for k in ("eyeL", "eyeR", "browL", "browR")}
        lip = self.meta["mouth"]["lip"]
        self.lip = tuple(v / 255 for v in lip)
        mp = os.path.join(d, "mouth.png")      # optional: the drawn rest mouth, kept as-is when not talking
        self.mouth_spr = cairo.ImageSurface.create_from_png(mp) if os.path.exists(mp) and "x" in self.meta["mouth"] else None
        self.pivot = tuple(self.meta.get("pivot", (173, 343)))
        self.scale = float(self.meta.get("scale", 1.0))
        self.ink = tuple(v / 255 for v in self.meta["ink"]) if "ink" in self.meta else None
        self.hands = self.meta.get("hands", "fork")

# expression = eye openness, left brow (dy, angle), right brow (dy, angle), mouth (open, width, curve)
# brow angle: positive on L / negative on R = inner ends DOWN (angry); opposite = inner ends UP (worried)
EXPR = {
    "smile":      dict(eye=1.0,  bL=(0, 0),       bR=(0, 0),       mouth=(0.0, 1.0, 0.75)),
    "neutral":    dict(eye=1.0,  bL=(0, 0),       bR=(0, 0),       mouth=(0.0, 0.8, 0.15)),
    "happy":      dict(eye=0.8,  bL=(-3, 0),      bR=(-3, 0),      mouth=(0.45, 1.05, 0.9)),
    "laugh":      dict(eye=0.12, bL=(-4, 0),      bR=(-4, 0),      mouth=(0.8, 1.1, 1.0), closed_happy=True),
    "surprised":  dict(eye=1.3,  bL=(-9, -0.05),  bR=(-9, 0.05),   mouth=(0.7, 0.3, 0.0)),
    "shock":      dict(eye=1.38, bL=(-11, -0.1),  bR=(-11, 0.1),   mouth=(1.0, 0.45, 0.0)),
    "worried":    dict(eye=1.05, bL=(-4, -0.24),  bR=(-4, 0.24),   mouth=(0.12, 0.6, -0.65)),
    "sad":        dict(eye=0.75, bL=(-2, -0.28),  bR=(-2, 0.28),   mouth=(0.0, 0.62, -0.8)),
    "angry":      dict(eye=0.72, bL=(3, 0.3),     bR=(3, -0.3),    mouth=(0.3, 0.8, -0.35)),
    "smug":       dict(eye=0.68, bL=(1, 0.05),    bR=(-8, 0.12),   mouth=(0.0, 0.9, 0.55)),
    "tired":      dict(eye=0.45, bL=(3, -0.12),   bR=(3, 0.12),    mouth=(0.0, 0.6, -0.2)),
    "mad":        dict(eye=1.42, bL=(-11, -0.18), bR=(-1, 0.32),   mouth=(0.55, 1.15, 0.95)),
    "determined": dict(eye=0.82, bL=(2, 0.2),     bR=(2, -0.2),    mouth=(0.0, 0.7, -0.05)),
    "shout":      dict(eye=1.1,  bL=(2, 0.26),    bR=(2, -0.26),   mouth=(1.0, 0.7, -0.6)),
    "dreamy":     dict(eye=0.12, bL=(-5, -0.1),   bR=(-5, 0.1),    mouth=(0.0, 0.9, 0.85), closed_happy=True),
    "dead":       dict(eye=0.08, bL=(2, 0),       bR=(2, 0),       mouth=(0.15, 0.5, -0.3)),
}

def _lerp(a, b, k):
    if isinstance(a, tuple): return tuple(_lerp(x, y, k) for x, y in zip(a, b))
    if isinstance(a, bool) or isinstance(b, bool): return b if k > .5 else a
    return a + (b - a) * k

def resolve(expr, u):
    """expr: name, or list of (time, name) keyframes (blends over 0.18 s)."""
    if isinstance(expr, str): return dict(EXPR[expr])
    cur = expr[0][1]; prev = None; t0 = 0
    for t, name in expr:
        if u >= t: prev, cur, t0 = cur, name, t
    E = dict(EXPR[cur])
    if prev is not None and u - t0 < 0.18:
        A = EXPR[prev]; k = ease_io((u - t0) / 0.18)
        E = {key: _lerp(A.get(key, False), E.get(key, False), k) for key in set(A) | set(E)}
    return E

def draw(c, F, expr="smile", u=0.0, talk=0.0, seed=0.0, blink=True):
    """Draw the face in head.png pixel coordinates (origin = image top-left)."""
    E = resolve(expr, u)
    c.set_source_surface(F.blank, 0, 0); c.get_source().set_filter(cairo.FILTER_BEST); c.paint()
    eye = E["eye"]
    if blink and eye > 0.3 and math.fmod(u + seed * 1.37, 3.3) < 0.13: eye = 0.1
    m = F.meta
    for k in ("eyeL", "eyeR"):
        mm = m[k]
        if eye <= 0.25:
            w = mm.get("w", 26 if k == "eyeL" else 22)
            c.new_path()
            if E.get("closed_happy"):
                c.move_to(mm["cx"] - w, mm["cy"] + 4); c.curve_to(mm["cx"] - w / 2, mm["cy"] - 8, mm["cx"] + w / 2, mm["cy"] - 8, mm["cx"] + w, mm["cy"] + 4)
            else:
                c.move_to(mm["cx"] - w, mm["cy"]); c.curve_to(mm["cx"] - w / 2, mm["cy"] + 7, mm["cx"] + w / 2, mm["cy"] + 7, mm["cx"] + w, mm["cy"])
            c.set_source_rgb(.1, .07, .06); c.set_line_width(3.6); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
        else:
            c.save(); c.translate(mm["cx"], mm["cy"]); c.scale(min(1.2, 0.9 + eye * 0.1) if eye > 1 else 1.0, eye); c.translate(-mm["cx"], -mm["cy"])
            c.set_source_surface(F.spr[k], mm["x"], mm["y"]); c.paint(); c.restore()
    for k, (dy, ang) in (("browL", E["bL"]), ("browR", E["bR"])):
        mm = m[k]
        c.save(); c.translate(mm["cx"], mm["cy"] + dy); c.rotate(ang); c.translate(-mm["cx"], -mm["cy"])
        c.set_source_surface(F.spr[k], mm["x"], mm["y"]); c.paint(); c.restore()
    op, wd, cv = E["mouth"]
    if talk > 0:
        flap = 0.5 + 0.5 * math.sin(u * 17 + seed) * math.sin(u * 7.3 + 1)
        op = max(op, talk * (0.25 + 0.6 * abs(flap)))
    if F.mouth_spr is not None and op < 0.06 and -0.45 < cv < 0.3:
        c.set_source_surface(F.mouth_spr, m["mouth"]["x"], m["mouth"]["y"]); c.get_source().set_filter(cairo.FILTER_BEST); c.paint()
        return
    mouth(c, m["mouth"]["cx"], m["mouth"]["cy"], m["mouth"]["w"] * 0.5 * wd, op, cv, F.lip)

def mouth(c, cx, cy, hw, op, cv, lip):
    ink = (.12, .06, .05)
    lift = cv * 8
    c.new_path()
    if op < 0.06:
        c.move_to(cx - hw, cy - lift); c.curve_to(cx - hw * .4, cy + lift * 1.2, cx + hw * .4, cy + lift * 1.2, cx + hw, cy - lift)
        c.set_source_rgb(*ink); c.set_line_width(3.4); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
        if cv > 0.2:   # lower lip
            c.move_to(cx - hw * .55, cy + lift * .9 + 3); c.curve_to(cx - hw * .2, cy + lift * .9 + 12, cx + hw * .2, cy + lift * .9 + 12, cx + hw * .55, cy + lift * .9 + 3)
            c.set_source_rgba(*lip, .9); c.set_line_width(4); c.stroke()
        return
    depth = 6 + op * 30
    if hw < 24 and abs(cv) < 0.2:      # "O" mouth
        ry = 5 + op * 17; ox = cy + ry * 0.5
        c.save(); c.translate(cx, ox); c.scale(hw, ry); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
        c.set_source_rgb(.36, .1, .1); c.fill_preserve(); c.save()
        c.clip(); c.save(); c.translate(cx, ox + ry * .7); c.scale(hw * .7, ry * .45); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
        c.set_source_rgb(.85, .4, .42); c.fill(); c.restore()
        c.save(); c.translate(cx, ox); c.scale(hw, ry); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
        c.set_source_rgb(*ink); c.set_line_width(3.2); c.stroke()
        return
    def shape():
        c.new_path(); c.move_to(cx - hw, cy - lift)
        c.curve_to(cx - hw * .4, cy + lift * 1.2 - 2, cx + hw * .4, cy + lift * 1.2 - 2, cx + hw, cy - lift)
        c.curve_to(cx + hw * .7, cy + depth + lift * .3, cx - hw * .7, cy + depth + lift * .3, cx - hw, cy - lift); c.close_path()
    shape(); c.set_source_rgb(.36, .1, .1); c.fill()
    c.save(); shape(); c.clip()
    c.rectangle(cx - hw, cy - lift - 10, hw * 2, lift * 1.2 + 14 + min(6, depth * .2)); c.set_source_rgb(.98, .97, .94); c.fill()
    c.save(); c.translate(cx, cy + depth + lift * .3); c.scale(hw * .6, depth * .45); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
    c.set_source_rgb(.85, .4, .42); c.fill()
    c.restore()
    shape(); c.set_source_rgb(*ink); c.set_line_width(3.2); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
