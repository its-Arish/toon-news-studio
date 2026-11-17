"""toonkit.rig: cut-out stick-body rig (2-bone limbs, boiling ink lines) and reusable actions."""
import os, math
import cairo
from .core import ease_io, clamp, rrect, fill_stroke

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAD = cairo.ImageSurface.create_from_png(os.path.join(_ROOT, "assets/characters/rob/head.png"))
HEAD_PIVOT = (173, 343)          # chin/neck point inside head.png
INK = (0.08, 0.08, 0.08)

# ---- skeleton (reference-image units, origin at hip) ----
NECK_Y, SHOULDER_Y = -347, -312
UA, FA, HAND = 176, 178, 46
TH, SH, FOOT = 214, 266, 70
HIP_H = 500                       # hip height above ground

REST = dict(aL1=-0.69, aL2=-0.18, aR1=0.69, aR2=0.18,
            lL1=-0.20, lL2=-0.08, lR1=0.20, lR2=0.08,
            lean=0.0, tilt=0.0, bob=0.0, feet=0.0)   # feet: 0 front, 1 side

def d(a): return (math.sin(a), math.cos(a))

# ---- hand-drawn "boil": lines jitter a little, re-drawn every 4 frames ----
def nz(i, k, f):
    v = math.sin(i * 12.9898 + k * 78.233 + f * 37.719) * 43758.5453
    return (v - math.floor(v)) * 2 - 1

def wline(c, pts, frame, amp=1.6, seed=0):
    f = frame // 4
    out = []
    for si in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[si], pts[si + 1]
        L = math.hypot(x1 - x0, y1 - y0) or 1
        nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        steps = max(2, int(L / 40))
        for k in range(steps + (si == len(pts) - 2)):
            u = k / steps
            j = nz(seed * 31 + si, k, f) * amp * math.sin(math.pi * u) if 0 < u < 1 else 0
            out.append((x0 + (x1 - x0) * u + nx * j, y0 + (y1 - y0) * u + ny * j))
    c.move_to(*out[0])
    for p in out[1:]: c.line_to(*p)
    c.set_source_rgb(*INK); c.set_line_width(8); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()

def limb(c, base, a1, a2, l1, l2, frame, seed):
    j = (base[0] + d(a1)[0] * l1, base[1] + d(a1)[1] * l1)
    e = (j[0] + d(a2)[0] * l2, j[1] + d(a2)[1] * l2)
    wline(c, [base, j, e], frame, seed=seed)
    return e, a2

def hand(c, wrist, a, frame, seed):
    stem = (wrist[0] + d(a)[0] * 10, wrist[1] + d(a)[1] * 10)
    wline(c, [wrist, stem], frame, seed=seed)
    for k, da in enumerate((-0.42, 0.0, 0.42)):
        tip = (stem[0] + d(a + da)[0] * HAND, stem[1] + d(a + da)[1] * HAND)
        wline(c, [stem, tip], frame, amp=0.8, seed=seed + k + 1)

def character(c, x, ground, s, P, frame, facing=1):
    c.save()
    c.translate(x, ground - (HIP_H - P["bob"]) * s)
    c.scale(s * facing, s)
    # soft shadow
    c.save(); c.translate(0, HIP_H - P["bob"]); c.scale(1, 0.18)
    c.arc(0, 0, 150, 0, 2 * math.pi); c.set_source_rgba(0, 0, 0, 0.18); c.fill(); c.restore()
    # legs
    for side, (k1, k2) in (("L", ("lL1", "lL2")), ("R", ("lR1", "lR2"))):
        ankle, _ = limb(c, (0, 0), P[k1], P[k2], TH, SH, frame, seed=10 if side == "L" else 20)
        fx_front = (-1 if side == "L" else 1, 0.3)
        fx_side = (1, 0.12)
        fx = (fx_front[0] * (1 - P["feet"]) + fx_side[0] * P["feet"], fx_front[1] * (1 - P["feet"]) + fx_side[1] * P["feet"])
        n = math.hypot(*fx)
        wline(c, [ankle, (ankle[0] + fx[0] / n * FOOT, ankle[1] + fx[1] / n * FOOT)], frame, seed=30 if side == "L" else 40)
    # upper body leans from hip
    c.rotate(P["lean"])
    wline(c, [(0, 0), (0, NECK_Y + 6)], frame, seed=50)
    sh = (0, SHOULDER_Y)
    for side, (k1, k2) in (("L", ("aL1", "aL2")), ("R", ("aR1", "aR2"))):
        w, a = limb(c, sh, P[k1], P[k2], UA, FA, frame, seed=60 if side == "L" else 70)
        hand(c, w, a, frame, seed=80 if side == "L" else 90)
    # head
    c.save(); c.translate(0, NECK_Y + 4); c.rotate(P["tilt"])
    hs = 1.0
    c.scale(hs, hs)
    c.set_source_surface(HEAD, -HEAD_PIVOT[0], -HEAD_PIVOT[1])
    c.get_source().set_filter(cairo.FILTER_BEST); c.paint()
    c.restore()
    c.restore()

# ---------------- actions ----------------
def A_rest(u):
    P = dict(REST); b = math.sin(u * 2.4)
    P["aL2"] += 0.04 * b; P["aR2"] -= 0.04 * b; P["tilt"] = 0.03 * math.sin(u * 1.3); P["bob"] = 3 * b
    return P

def A_walk(u):
    P = dict(REST); ph = u * 2 * math.pi * 1.7; s = math.sin(ph)
    P.update(lL1=0.42 * s, lR1=-0.42 * s, feet=1.0)
    P["lL2"] = P["lL1"] - 0.55 * max(0, math.sin(ph + 1.4))
    P["lR2"] = P["lR1"] - 0.55 * max(0, math.sin(ph + 1.4 + math.pi))
    P.update(aL1=-0.35 * s - 0.1, aL2=-0.35 * s + 0.15, aR1=0.35 * s + 0.1, aR2=0.35 * s + 0.35)
    P["bob"] = -10 * abs(math.cos(ph)); P["lean"] = 0.06; P["tilt"] = 0.04 * math.sin(ph * 2)
    return P

def A_wave(u):
    P = A_rest(u); P.update(aR1=2.5, aR2=2.95 + 0.42 * math.sin(u * 13)); P["tilt"] = -0.08
    return P

def A_point(u):
    P = A_rest(u); P.update(aR1=1.5 - 0.03 * math.sin(u * 3), aR2=1.58, lean=0.05, tilt=0.06)
    P.update(aL1=-0.35, aL2=0.55)   # other hand on hip-ish
    return P

def A_shrug(u):
    P = A_rest(u); k = 0.5 + 0.5 * math.sin(u * 5)
    P.update(aL1=-0.95, aL2=-2.25 - 0.1 * k, aR1=0.95, aR2=2.25 + 0.1 * k, tilt=0.16, bob=6 * k)
    return P

def A_shock(u):
    P = A_rest(u); j = math.sin(u * 47) * 0.05
    P.update(aL1=-2.15 + j, aL2=-2.55 - j, aR1=2.15 - j, aR2=2.55 + j, lean=-0.06, tilt=-0.1 + j, bob=12)
    return P

def A_talk(u):
    P = A_rest(u)
    P.update(aR1=0.55, aR2=1.35 + 0.35 * math.sin(u * 4.2), aL1=-0.55, aL2=-1.0 - 0.25 * math.sin(u * 3.1 + 1))
    P["tilt"] = 0.07 * math.sin(u * 3.3); P["bob"] = 4 * abs(math.sin(u * 3.3))
    return P

