"""toonkit.kit: actors with outfits, side characters, props, backgrounds and an auto-camera.

Everything draws in a 1280x720 'world'; ground line is usually y=600.
"""
import math, random
import cairo
from .core import text, rrect, fill_stroke, hexc, ease_io, prog, clamp, W, H
from .rig import (wline, limb, hand, HEAD, HEAD_PIVOT, INK, NECK_Y, SHOULDER_Y, UA, FA, TH, SH, FOOT, HIP_H,
                  A_rest, A_talk, A_wave, A_point, A_shrug, A_shock, A_walk, REST)
from . import face as _face
from .scene import cam, vgrad, glow, label, stars, coded_head, suit_figure, main_head, P_, lerpP, ease_out_back

TAU = 2 * math.pi
ROBF = _face.Face("assets/characters/rob")
import numpy as _np

def _dark_here(c, lx, ly):
    """True if the already-drawn background around local point (lx, ly) is dark."""
    tgt = c.get_target(); tgt.flush()
    w, h = tgt.get_width(), tgt.get_height()
    dx, dy = c.user_to_device(lx, ly)
    ix, iy = int(min(max(dx, 12), w - 13)), int(min(max(dy, 12), h - 13))
    a = _np.ndarray((h, w, 4), _np.uint8, tgt.get_data())
    patch = a[iy - 12:iy + 12, ix - 12:ix + 12, :3].astype(_np.float32)
    return patch.mean() < 80

def _halo(c):
    if _dark_here(c, 0, -420):
        glow(c, 0, -380, 760, (1, .93, .8), .32)

def draw_mask(c):
    c.save(); c.translate(18, -137)
    c.new_path(); c.move_to(-95, -8)
    c.curve_to(-70, -40, 100, -42, 118, -6); c.curve_to(110, 24, 40, 30, 12, 14)
    c.curve_to(-10, 30, -80, 26, -95, -8); c.close_path(); fill_stroke(c, "#111111", 4, "#000000")
    for ex in (-40, 42):
        c.save(); c.translate(ex, -4); c.scale(1.6, 0.6); c.arc(0, 0, 11, 0, TAU); c.restore()
        c.set_source_rgb(.95, .95, .95); c.fill()
    c.restore()

def rob_head(c, expr="smile", u=0.0, talk=0.0, mask=False, seed=0.0):
    """Head in neck-pivot coordinates with a live face."""
    c.save(); c.translate(-HEAD_PIVOT[0], -HEAD_PIVOT[1])
    _face.draw(c, ROBF, expr, u, talk, seed)
    c.restore()
    if mask: draw_mask(c)

# =====================================================================================
# camera
# =====================================================================================
MOVES = ("push", "pull", "panL", "panR", "dutch", "rise")

def _move(u, d, mv, cx, cy, z, rot):
    e = ease_io(u / d) if d > 0 else 0
    if mv == "push": z *= 1 + 0.14 * e
    elif mv == "pull": z *= 1.14 - 0.14 * e
    elif mv == "panL": cx += 70 - 140 * e
    elif mv == "panR": cx += -70 + 140 * e
    elif mv == "dutch": rot += 0.04 * (1 - e) - 0.02; z *= 1.05 + 0.06 * e
    elif mv == "rise": cy += 40 - 80 * e
    return cx, cy, z, rot

def autocam(c, u, d, a=(640, 360, 1.0, 0.0), b=None, mv=None, seed=0, split=3.1):
    """Frame A with a move; if the shot is long, hard-cut to framing B halfway (B defaults to a closer A)."""
    rnd = random.Random(seed)
    mv = mv or MOVES[seed % len(MOVES)]
    a = tuple(a) + (0.0,) * (4 - len(a))
    if d > split:
        if b is None: b = (a[0] + rnd.choice((-80, 80)), a[1] - 40, a[2] * 1.45, rnd.choice((0.0, 0.03, -0.03)))
        b = tuple(b) + (0.0,) * (4 - len(b))
        h = d * 0.5
        if u < h: cam(c, *_move(u, h, mv, *a))
        else:
            mv2 = MOVES[(seed + 3) % len(MOVES)]
            cam(c, *_move(u - h, d - h, mv2, *b))
    else:
        cam(c, *_move(u, d, mv, *a))

def shake(u, amp=6, fade=1.0):
    k = max(0.0, 1 - u / fade) if fade else 1
    return math.sin(u * 61) * amp * k, math.cos(u * 47) * amp * k

# =====================================================================================
# actors
# =====================================================================================
def _limbs_legs(c, P, frame):
    for side, (k1, k2) in (("L", ("lL1", "lL2")), ("R", ("lR1", "lR2"))):
        ankle, _ = limb(c, (0, 0), P[k1], P[k2], TH, SH, frame, seed=10 if side == "L" else 20)
        ff = (-1 if side == "L" else 1, 0.3); fs = (1, 0.12)
        fx = (ff[0] * (1 - P["feet"]) + fs[0] * P["feet"], ff[1] * (1 - P["feet"]) + fs[1] * P["feet"])
        n = math.hypot(*fx)
        wline(c, [ankle, (ankle[0] + fx[0] / n * FOOT, ankle[1] + fx[1] / n * FOOT)], frame, seed=30 if side == "L" else 40)

def _torso_outfit(c, outfit):
    if "tux" in outfit or "suit" in outfit:
        col = "#15171c" if "tux" in outfit else "#2f3a4f"
        c.move_to(-78, -300); c.line_to(78, -300); c.line_to(66, 10); c.line_to(-66, 10); c.close_path(); fill_stroke(c, col, 7, "#0a0a0a")
        c.move_to(-30, -300); c.line_to(0, -170); c.line_to(30, -300); c.close_path(); c.set_source_rgb(.96, .96, .96); c.fill()
        if "tux" in outfit:
            c.move_to(-26, -286); c.line_to(0, -272); c.line_to(26, -286); c.line_to(26, -256); c.line_to(0, -272); c.line_to(-26, -256); c.close_path()
            c.set_source_rgb(.04, .04, .04); c.fill()
        else:
            c.move_to(-9, -280); c.line_to(9, -280); c.line_to(12, -190); c.line_to(0, -175); c.line_to(-12, -190); c.close_path(); fill_stroke(c, "#8a1f1f", 3, "#111111")
    if "toga" in outfit:
        c.move_to(-80, -300); c.line_to(60, -310); c.line_to(80, 40); c.line_to(-70, 40); c.close_path(); fill_stroke(c, "#f3efe3", 6, "#1a1a1a")
        c.move_to(-80, -300); c.curve_to(0, -200, 40, -100, 80, 40); c.set_source_rgb(.75, .7, .6); c.set_line_width(5); c.stroke()
    if "scarf" in outfit:
        for i in range(6):
            c.rectangle(-60 + i * 20, -345, 20, 34); c.set_source_rgb(*((.95, .78, .15) if i % 2 == 0 else (.12, .12, .12))); c.fill()
        rrect(c, -60, -345, 120, 34, 10); c.set_source_rgb(*INK); c.set_line_width(5); c.stroke()
        for i in range(4):
            c.rectangle(30, -315 + i * 26, 30, 26); c.set_source_rgb(*((.95, .78, .15) if i % 2 == 0 else (.12, .12, .12))); c.fill()
        c.rectangle(30, -315, 30, 104); c.set_source_rgb(*INK); c.stroke()
    if "explorer" in outfit:
        c.move_to(-70, -300); c.line_to(70, -300); c.line_to(60, 0); c.line_to(-60, 0); c.close_path(); fill_stroke(c, "#b49a6a", 6, "#1a1a1a")
        for x in (-30, 30): c.rectangle(x - 16, -220, 32, 36); fill_stroke(c, "#9c8457", 4, "#1a1a1a")

def _head_back(c, outfit):
    if "wig" in outfit:
        c.move_to(-150, -300); c.curve_to(-190, -150, -170, 0, -120, 40); c.line_to(140, 40)
        c.curve_to(200, 0, 210, -150, 170, -300); c.curve_to(100, -380, -80, -380, -150, -300); c.close_path()
        fill_stroke(c, "#e8c56a", 6, "#1a1a1a")

def _head_front(c, outfit, u=0.0):
    if "explorer" in outfit:
        c.save(); c.translate(12, -250); c.scale(1, .28); c.arc(0, 0, 200, 0, TAU); c.restore(); fill_stroke(c, "#a8875a", 6, "#1a1a1a")
        c.move_to(-110, -255); c.curve_to(-110, -390, 130, -390, 130, -255); c.close_path(); fill_stroke(c, "#b9976a", 6, "#1a1a1a")
        c.rectangle(-110, -290, 240, 26); c.set_source_rgb(.35, .22, .12); c.fill()
    if "crown" in outfit:
        c.move_to(-90, -270); c.line_to(-90, -350); c.line_to(-45, -305); c.line_to(10, -370); c.line_to(60, -305)
        c.line_to(110, -350); c.line_to(110, -270); c.close_path(); fill_stroke(c, "#f2c94c", 6, "#1a1a1a")
        for x in (-45, 10, 60): c.arc(x, -285, 9, 0, TAU); c.set_source_rgb(.8, .15, .2); c.fill()
    if "wig" in outfit:
        c.move_to(-120, -260); c.curve_to(-60, -360, 120, -360, 150, -250); c.curve_to(80, -300, -40, -300, -120, -260); c.close_path()
        fill_stroke(c, "#f0d27e", 5, "#1a1a1a")
    if "sweat" in outfit:
        for i, (x, y) in enumerate(((150, -230), (175, -150), (-110, -200))):
            yy = y + (u * 120 + i * 40) % 80
            c.save(); c.translate(x, yy); c.move_to(0, -18); c.curve_to(14, 0, 14, 14, 0, 14); c.curve_to(-14, 14, -14, 0, 0, -18)
            fill_stroke(c, "#8fd3ff", 3, "#1a1a1a"); c.restore()
    if "eyebags" in outfit:
        for ex in (-25, 58):
            c.arc(ex, -118, 18, 0.15 * math.pi, 0.85 * math.pi); c.set_source_rgba(.35, .2, .35, .7); c.set_line_width(5); c.stroke()
    if "swirl" in outfit:
        for ex in (-25, 58):
            c.save(); c.translate(ex, -135); c.rotate(u * 8)
            c.move_to(0, 0)
            for k in range(40): a = k * 0.45; r = k * 0.55; c.line_to(math.cos(a) * r, math.sin(a) * r)
            c.set_source_rgb(.1, .1, .1); c.set_line_width(3); c.stroke(); c.restore()

def _held(c, outfit, P):
    if "guitar" in outfit:
        c.save(); c.translate(10, -150); c.rotate(-0.55)
        c.save(); c.scale(1, .8); c.arc(-60, 0, 62, 0, TAU); c.restore(); fill_stroke(c, "#c46a2a", 6, "#1a1a1a")
        c.save(); c.scale(1, .8); c.arc(20, 0, 46, 0, TAU); c.restore(); fill_stroke(c, "#c46a2a", 6, "#1a1a1a")
        c.arc(-20, 0, 18, 0, TAU); c.set_source_rgb(.15, .08, .03); c.fill()
        c.rectangle(55, -10, 190, 20); fill_stroke(c, "#6b3b1a", 5, "#1a1a1a"); rrect(c, 240, -18, 40, 36, 6); fill_stroke(c, "#4a2a10", 4, "#1a1a1a")
        c.restore()
    if "drink" in outfit:
        c.save(); c.translate(150, -260)
        c.move_to(-26, -30); c.line_to(26, -30); c.line_to(0, 0); c.close_path(); fill_stroke(c, "#e7f3f7", 4, "#1a1a1a")
        c.move_to(0, 0); c.line_to(0, 34); c.set_line_width(4); c.stroke(); c.restore()
    if "bag" in outfit:
        c.save(); c.translate(-170, -60); rrect(c, -50, -40, 100, 80, 14); fill_stroke(c, "#6b5a3a", 5, "#1a1a1a")
        text(c, "$", 0, 0, 50, color="#2d6b2d"); c.restore()

ROB_POSE_FIX = {"guitar": dict(aL1=-0.2, aL2=0.9, aR1=0.4, aR2=-0.9)}

def rob(c, x, ground, s, P, f, u=0.0, outfit=(), mask=False, facing=1, rot=0.0, enter=None, shadow=True, expr="smile", talk=0.0, seed=0.0):
    """Main character. outfit: tux suit toga scarf explorer wig crown sweat eyebags swirl guitar drink bag"""
    P = dict(P)
    for o in outfit:
        if o in ROB_POSE_FIX: P.update(ROB_POSE_FIX[o])
    c.save()
    if enter == "drop": c.translate(0, -600 * (1 - ease_out_back(clamp(u / 0.45), 1.2)))
    elif enter == "left": c.translate(-900 * (1 - ease_io(clamp(u / 0.5))), 0)
    elif enter == "right": c.translate(900 * (1 - ease_io(clamp(u / 0.5))), 0)
    c.translate(x, ground - (HIP_H - P["bob"]) * s); c.scale(s * facing, s)
    if rot: c.translate(0, HIP_H); c.rotate(rot); c.translate(0, -HIP_H)
    elif shadow:
        c.save(); c.translate(0, HIP_H - P["bob"]); c.scale(1, .18); c.arc(0, 0, 150, 0, TAU); c.set_source_rgba(0, 0, 0, .18); c.fill(); c.restore()
    _halo(c)
    _limbs_legs(c, P, f)
    c.rotate(P["lean"])
    wline(c, [(0, 0), (0, NECK_Y + 6)], f, seed=50)
    _torso_outfit(c, outfit)
    for side, (k1, k2) in (("L", ("aL1", "aL2")), ("R", ("aR1", "aR2"))):
        w, a = limb(c, (0, SHOULDER_Y), P[k1], P[k2], UA, FA, f, seed=60 if side == "L" else 70)
        hand(c, w, a, f, seed=80 if side == "L" else 90)
    _held(c, outfit, P)
    c.save(); c.translate(0, NECK_Y + 4); c.rotate(P["tilt"])
    _head_back(c, outfit)
    rob_head(c, expr, u, talk, mask, seed)
    _head_front(c, outfit, u)
    c.restore(); c.restore()

def npc(c, x, ground, s, P, f, u=0.0, hair="#6b4a2b", style="short", skin="#f2d6b3", outfit=(), facing=1,
        glasses=False, shades=False, beard=False, cap=None, name=None, name_t=1.0, seed=0, rot=0.0, enter=None):
    """Side character: coded round head on the same stick body."""
    P = dict(P)
    c.save()
    if enter == "left": c.translate(-900 * (1 - ease_io(clamp(u / 0.5))), 0)
    elif enter == "right": c.translate(900 * (1 - ease_io(clamp(u / 0.5))), 0)
    elif enter == "drop": c.translate(0, -600 * (1 - ease_out_back(clamp(u / 0.45), 1.2)))
    c.translate(x, ground - (HIP_H - P["bob"]) * s); c.scale(s * facing, s)
    if rot: c.translate(0, HIP_H); c.rotate(rot); c.translate(0, -HIP_H)
    else:
        c.save(); c.translate(0, HIP_H - P["bob"]); c.scale(1, .18); c.arc(0, 0, 150, 0, TAU); c.set_source_rgba(0, 0, 0, .18); c.fill(); c.restore()
    _halo(c)
    _limbs_legs(c, P, f)
    c.rotate(P["lean"]); wline(c, [(0, 0), (0, NECK_Y + 6)], f, seed=50)
    _torso_outfit(c, outfit)
    for side, (k1, k2) in (("L", ("aL1", "aL2")), ("R", ("aR1", "aR2"))):
        w, a = limb(c, (0, SHOULDER_Y), P[k1], P[k2], UA, FA, f, seed=60 if side == "L" else 70)
        hand(c, w, a, f, seed=80 if side == "L" else 90)
    _held(c, outfit, P)
    c.save(); c.translate(0, NECK_Y + 4); c.rotate(P["tilt"])
    coded_head(c, f, skin=skin, hair=hair, style=style, t=u, seed=seed)
    sc = 1.4; cy = -96 * sc
    if beard:
        c.move_to(-110, cy + 20); c.curve_to(-100, cy + 170, 100, cy + 170, 110, cy + 20); c.curve_to(60, cy + 90, -60, cy + 90, -110, cy + 20)
        fill_stroke(c, "#d9d9d9", 5, "#1a1a1a")
    if glasses or shades:
        for ex in (-48, 48):
            c.arc(ex, cy + 8, 30, 0, TAU)
            if shades: c.set_source_rgb(.05, .05, .05); c.fill_preserve()
            c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
        c.move_to(-18, cy + 8); c.line_to(18, cy + 8); c.stroke()
    if cap:
        c.move_to(-150, cy - 60); c.curve_to(-150, cy - 210, 150, cy - 210, 150, cy - 60); c.close_path(); fill_stroke(c, cap, 6, "#1a1a1a")
        c.rectangle(80, cy - 75, 120, 24); fill_stroke(c, cap, 5, "#1a1a1a")
    if "crown" in outfit: _head_front(c, ("crown",), u)
    c.restore(); c.restore()
    if name:
        label(c, name, x, ground - (HIP_H + 347 + 380) * s - 30, 26, name_t)

def crowd(c, x0, x1, ground, rows=2, s=0.22, u=0.0, seed=0, phones=False, signs=None, jump=False, dark=False):
    rnd = random.Random(seed)
    hairs = ["#3a2a1a", "#6b4a2b", "#c99a5b", "#1a1a1a", "#a57a4a", "#7a5230", "#d9d9d9"]
    shirts = ["#c0392b", "#2f6fa8", "#3fa86b", "#e1a33a", "#7d4ea8", "#555555", "#d65a8a"]
    for r in range(rows):
        n = int((x1 - x0) / (95 * s / 0.22))
        for i in range(n):
            x = x0 + (i + rnd.random() * 0.6) * (x1 - x0) / n
            g = ground + r * 40 * s / 0.22
            ph = rnd.random() * 6
            b = abs(math.sin(u * (6 if jump else 2.5) + ph)) * (24 if jump else 6) * s / 0.22
            c.save(); c.translate(x, g - b); c.scale(s / 0.22 * 0.5, s / 0.22 * 0.5)
            rrect(c, -60, -200, 120, 220, 55); fill_stroke(c, "#202020" if dark else rnd.choice(shirts), 5, "#141414")
            c.translate(0, -175)
            coded_head(c, 0, hair=rnd.choice(hairs), style=rnd.choice(("short", "long")), t=u, seed=i, face=not dark, scale=0.9)
            if phones:
                c.save(); c.translate(60 if i % 2 else -60, -260); c.rotate(0.15)
                rrect(c, -22, -38, 44, 76, 8); fill_stroke(c, "#222222", 4, "#000000")
                if math.sin(u * 7 + ph * 3) > 0.85: glow(c, 0, 0, 90, (1, 1, 1), .8)
                c.restore()
            if signs and i % 3 == 0:
                c.save(); c.translate(0, -330); wline(c, [(0, 60), (0, 200)], 0, amp=0)
                rrect(c, -95, -30, 190, 90, 8); fill_stroke(c, "#ffffff", 5, "#1a1a1a"); text(c, signs[(i // 3) % len(signs)], 0, 15, 40, color="#c0392b")
                c.restore()
            c.restore()

def tiny_head(c, x, y, s, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.set_source_surface(HEAD, -HEAD_PIVOT[0] + 0, -HEAD_PIVOT[1] + 170); c.get_source().set_filter(cairo.FILTER_BEST); c.paint()
    c.restore()

# =====================================================================================
# props
# =====================================================================================
def pop(u, a, dur=0.35): return ease_out_back(prog(u, a, a + dur))

def calendar(c, x, y, s, top, big, bottom, color="#d6402f", circle=None, u=0.0, t0=0.0):
    k = pop(u, t0)
    c.save(); c.translate(x, y); c.scale(s * k, s * k); c.rotate(-0.04)
    rrect(c, -170, -190, 340, 380, 14); fill_stroke(c, "#ffffff", 7, "#1a1a1a")
    c.rectangle(-170, -190, 340, 90); c.set_source_rgb(*hexc(color)[:3]); c.fill()
    rrect(c, -170, -190, 340, 380, 14); c.set_source_rgb(*INK); c.set_line_width(7); c.stroke()
    text(c, top, 0, -146, 46, color="#ffffff"); text(c, big, 0, 30, 150 if len(big) <= 3 else 110); text(c, bottom, 0, 140, 34)
    for rx in (-90, 90): rrect(c, rx - 10, -210, 20, 44, 8); fill_stroke(c, "#888888", 4, "#1a1a1a")
    c.restore()

def counter(c, x, y, s, u, target, t0=0.0, dur=1.3, prefix="$", suffix="", color="#2d8a3e"):
    k = ease_io(prog(u, t0, t0 + dur)); val = int(target * k)
    sc = pop(u, t0 - 0.2)
    c.save(); c.translate(x, y); c.scale(s * sc, s * sc)
    txt = f"{prefix}{val:,}{suffix}"
    c.select_font_face("Patrick Hand"); c.set_font_size(84); e = c.text_extents(txt)
    rrect(c, -e.width / 2 - 40, -70, e.width + 80, 140, 18); fill_stroke(c, "#ffffff", 7, "#1a1a1a")
    text(c, txt, 0, 4, 84, color=color); c.restore()

def bills(c, x, y, u, n=10, seed=0, spread=500):
    rnd = random.Random(seed)
    for i in range(n):
        ph = rnd.random(); t = (u * 0.6 + ph) % 1.0
        bx = x + (rnd.random() - .5) * spread; by = y - 300 + t * 700
        c.save(); c.translate(bx + math.sin(u * 3 + i) * 30, by); c.rotate(math.sin(u * 4 + i) * .6)
        rrect(c, -36, -18, 72, 36, 4); fill_stroke(c, "#8fd18a", 3, "#1a5a1a"); text(c, "$", 0, 0, 26, color="#1a5a1a"); c.restore()

def clapboard(c, x, y, s, u, title, year="", t0=0.0):
    k = pop(u, t0); snap = clamp((u - t0 - 0.35) / 0.15)
    c.save(); c.translate(x, y); c.scale(s * k, s * k); c.rotate(-0.05)
    rrect(c, -190, -60, 380, 230, 10); fill_stroke(c, "#222222", 7, "#0a0a0a")
    text(c, title, 0, 30, 48 if len(title) < 14 else 36, color="#ffffff"); text(c, year, 0, 110, 40, color="#f2c94c")
    c.save(); c.translate(-190, -60); c.rotate(-0.45 * (1 - snap))
    c.rectangle(0, -50, 380, 50); fill_stroke(c, "#ffffff", 6, "#0a0a0a")
    for i in range(6): c.move_to(20 + i * 64, -50); c.line_to(50 + i * 64, 0); c.line_to(80 + i * 64, 0); c.line_to(50 + i * 64, -50); c.close_path(); c.set_source_rgb(.1, .1, .1); c.fill()
    c.restore(); c.restore()

def chair(c, x, ground, s, name, u=0.0, t0=0.0):
    k = pop(u, t0)
    c.save(); c.translate(x, ground); c.scale(s * k, s * k)
    for lx in (-80, 80): wline(c, [(lx, 0), (-lx * .8, -180)], 0, amp=0, seed=lx)
    c.rectangle(-100, -190, 200, 26); fill_stroke(c, "#6b3b1a", 5, "#1a1a1a")
    c.rectangle(-100, -360, 200, 100); fill_stroke(c, "#1b1b1b", 6, "#000000")
    for lx in (-100, 100): c.rectangle(lx - 8, -370, 16, 190); fill_stroke(c, "#6b3b1a", 4, "#1a1a1a")
    text(c, "DIRECTOR", 0, -335, 30, color="#bbbbbb"); text(c, name, 0, -295, 40 if len(name) < 13 else 30, color="#ffffff")
    c.restore()

def film_strip(c, x, y, s, u, n=5, cut=None, heads=True, scroll=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    w = n * 170
    c.translate(-w / 2 - (u * scroll) % 170, 0)
    for i in range(n + 1):
        if cut is not None and i in cut[0] and u > cut[1]:
            k = ease_io(prog(u, cut[1], cut[1] + 0.6)); c.save(); c.translate(i * 170 + 85, 300 * k * k); c.rotate(k * (1 if i % 2 else -1))
            c.translate(-(i * 170 + 85), 0)
        else: c.save()
        c.rectangle(i * 170, -100, 170, 200); c.set_source_rgb(.1, .1, .1); c.fill()
        c.rectangle(i * 170 + 15, -70, 140, 140); c.set_source_rgb(.95, .9, .78); c.fill()
        for hy in (-88, 78):
            for hx in range(5): c.rectangle(i * 170 + 10 + hx * 33, hy, 16, 10); c.set_source_rgb(.95, .95, .95); c.fill()
        if heads and i % 2 == 0: tiny_head(c, i * 170 + 85, -25, 0.28)
        c.restore()
    c.restore()

def scissors(c, x, y, s, u):
    a = 0.35 * abs(math.sin(u * 8))
    c.save(); c.translate(x, y); c.scale(s, s)
    for sgn in (1, -1):
        c.save(); c.rotate(sgn * a)
        c.move_to(0, 0); c.line_to(220, -12 * sgn); c.line_to(220, 6 * sgn); c.close_path(); fill_stroke(c, "#cfd6de", 5, "#1a1a1a")
        c.arc(-60, 30 * sgn, 34, 0, TAU); fill_stroke(c, "#d6402f", 8, "#1a1a1a"); c.arc(-60, 30 * sgn, 18, 0, TAU); c.set_source_rgb(.95, .93, .88); c.fill()
        c.restore()
    c.restore()

def tv(c, x, y, s, inner=None, u=0.0, label_text=None):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -230, -160, 460, 320, 26); fill_stroke(c, "#6b4a2b", 8, "#1a1a1a")
    rrect(c, -200, -130, 340, 260, 18); fill_stroke(c, "#1d2c3a", 5, "#0a0a0a")
    for i, yy in enumerate((-60, 0)): c.arc(180, yy, 16, 0, TAU); fill_stroke(c, "#cccccc", 4, "#1a1a1a")
    for lx in (-120, 120): wline(c, [(lx, 160), (lx * 1.2, 220)], 0, amp=0)
    c.save(); rrect(c, -200, -130, 340, 260, 18); c.clip(); c.translate(-30, 0)
    if inner: inner(c, u)
    c.restore()
    c.restore()

def book(c, x, y, s, title, u=0.0, t0=0.0, color="#1b2433"):
    k = pop(u, t0)
    c.save(); c.translate(x, y); c.scale(s * k, s * k); c.rotate(0.05)
    rrect(c, -130, -180, 260, 360, 10); fill_stroke(c, color, 7, "#0a0a0a")
    c.rectangle(-130, -180, 26, 360); c.set_source_rgba(0, 0, 0, .3); c.fill()
    text(c, title, 10, -60, 48, color="#f3f3f3"); text(c, "a novel", 10, 120, 28, color="#9aa5b5")
    c.restore()

def poster(c, x, y, s, title, kind="rob", u=0.0, t0=0.0, bg="#d6402f", torn=0.0, rot=-0.04):
    k = pop(u, t0)
    if k <= 0.002: return
    c.save(); c.translate(x, y); c.scale(s * k, s * k); c.rotate(rot)
    if torn > 0: c.rotate(torn * 0.4); c.translate(0, torn * 200)
    rrect(c, -150, -220, 300, 440, 6); fill_stroke(c, bg, 7, "#141414")
    if kind == "rob": tiny_head(c, 0, -40, 0.5)
    elif kind == "elephant":
        c.save(); c.translate(0, -30); c.scale(1.3, 1); c.arc(0, 0, 70, 0, TAU); c.restore(); c.set_source_rgb(.55, .55, .6); c.fill()
        c.arc(-90, -60, 40, 0, TAU); c.fill(); c.rectangle(-130, -60, 24, 120); c.fill()
        for lx in (-50, 0, 50, 80): c.rectangle(lx - 12, 20, 24, 70); c.fill()
    elif kind == "rain":
        c.set_source_rgba(1, 1, 1, .6); c.set_line_width(3)
        for i in range(30): xx = -130 + (i * 37) % 260; yy = -200 + (i * 53) % 300; c.move_to(xx, yy); c.line_to(xx - 8, yy + 30); c.stroke()
        c.arc(0, -10, 60, math.pi, TAU); c.close_path(); c.set_source_rgb(.15, .15, .2); c.fill()
    elif kind == "hat":
        c.rectangle(-60, -120, 120, 110); c.set_source_rgb(.08, .08, .08); c.fill(); c.rectangle(-100, -14, 200, 20); c.fill()
    elif kind == "desert":
        c.arc(40, -80, 50, 0, TAU); c.set_source_rgb(1, .85, .4); c.fill()
        c.move_to(-150, 60); c.curve_to(-50, -20, 50, 20, 150, -10); c.line_to(150, 120); c.line_to(-150, 120); c.close_path(); c.set_source_rgb(.85, .6, .3); c.fill()
    elif kind == "space":
        rnd = random.Random(3)
        for i in range(40): c.arc(rnd.uniform(-140, 140), rnd.uniform(-210, 120), rnd.uniform(1, 3), 0, TAU); c.set_source_rgb(1, 1, 1); c.fill()
        c.arc(30, -40, 50, 0, TAU); c.set_source_rgb(.85, .5, .3); c.fill()
    text(c, title, 0, 160, 38 if len(title) < 13 else 28, color="#ffffff")
    c.restore()

def magazine(c, x, y, s, title, u=0.0, t0=0.0, bg="#f2c94c", rot=0.06):
    k = pop(u, t0)
    if k <= 0.002: return
    c.save(); c.translate(x, y); c.scale(s * k, s * k); c.rotate(rot)
    rrect(c, -140, -190, 280, 380, 6); fill_stroke(c, bg, 7, "#141414")
    text(c, title, 0, -150, 52, color="#c0392b"); tiny_head(c, 0, 10, 0.55)
    c.restore()

def lunchbox(c, x, y, s, u=0.0, t0=0.0):
    k = pop(u, t0)
    if k <= 0.002: return
    c.save(); c.translate(x, y); c.scale(s * k, s * k); c.rotate(-0.05)
    c.move_to(-60, -130); c.curve_to(-60, -190, 60, -190, 60, -130); c.set_source_rgb(*INK); c.set_line_width(10); c.stroke()
    rrect(c, -170, -130, 340, 250, 22); fill_stroke(c, "#3f7fd6", 7, "#141414")
    tiny_head(c, 0, -10, 0.45); c.restore()

def phone(c, x, y, s, u, posts, t0=0.0, step=0.45):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -170, -300, 340, 600, 40); fill_stroke(c, "#1a1a1a", 7, "#000000")
    rrect(c, -150, -270, 300, 540, 20); c.set_source_rgb(.97, .97, .99); c.fill()
    c.save(); rrect(c, -150, -270, 300, 540, 20); c.clip()
    for i, (txt, col) in enumerate(posts):
        k = pop(u, t0 + i * step)
        if k <= 0.002: continue
        yy = -220 + i * 110
        c.save(); c.translate(0, yy); c.scale(k, k)
        rrect(c, -135, -45, 270, 90, 14); fill_stroke(c, col, 4, "#1a1a1a")
        c.arc(-100, 0, 24, 0, TAU); fill_stroke(c, "#f2d6b3", 3, "#1a1a1a")
        text(c, txt, 20, 0, 30 if len(txt) < 14 else 24)
        c.restore()
    c.restore(); c.restore()

def stamp(c, x, y, s, u, txt, color="#d6402f", t0=0.0, rot=-0.15):
    if u < t0: return
    k = clamp((u - t0) / 0.12); sc = 2.2 - 1.2 * ease_io(k)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s * sc, s * sc)
    c.select_font_face("Patrick Hand"); c.set_font_size(90); e = c.text_extents(txt)
    rrect(c, -e.width / 2 - 30, -70, e.width + 60, 140, 12); c.set_source_rgba(*hexc(color)[:3], .9 * k); c.set_line_width(10); c.stroke()
    c.new_path(); c.move_to(-e.width / 2 - e.x_bearing, 32); c.text_path(txt); c.set_source_rgba(*hexc(color)[:3], .9 * k); c.fill()
    c.restore()

def door(c, x, ground, s, u, open_k, light=(1, .95, .7), sign=None, color="#7a4a2a"):
    c.save(); c.translate(x, ground); c.scale(s, s)
    c.rectangle(-120, -400, 240, 400); fill_stroke(c, "#2a2a2a", 8, "#111111")
    if open_k > 0:
        glow(c, 0, -200, 420 * open_k + 10, light, .55 * open_k)
        c.rectangle(-112, -392, 224, 392); c.set_source_rgba(*light, .9 * open_k); c.fill()
    w = 224 * (1 - open_k * 0.85)
    c.rectangle(-112, -392, w, 392); fill_stroke(c, color, 6, "#111111")
    if w > 60: c.arc(-112 + w - 30, -190, 12, 0, TAU); c.set_source_rgb(.9, .75, .3); c.fill()
    if sign:
        rrect(c, -150, -480, 300, 64, 8); fill_stroke(c, "#ffffff", 5, "#111111"); text(c, sign, 0, -448, 36 if len(sign) < 14 else 28)
    c.restore()

def goblet(c, x, y, s, u):
    c.save(); c.translate(x, y); c.scale(s, s)
    glow(c, 0, -160, 260, (.4, .65, 1), .55 + .15 * math.sin(u * 7))
    for i in range(7):
        a = i / 7 * TAU + u * 3; r = 40 + 15 * math.sin(u * 9 + i)
        c.move_to(-60, -100); c.curve_to(-60 + math.cos(a) * 30, -180, math.sin(a) * r, -260 - 30 * math.sin(u * 5 + i), 0, -300 - 20 * math.sin(u * 6 + i))
        c.curve_to(math.sin(a) * r * .5, -200, 60, -180, 60, -100); c.close_path(); c.set_source_rgba(.45, .75, 1, .35); c.fill()
    c.move_to(-110, -100); c.line_to(110, -100); c.curve_to(110, 20, -110, 20, -110, -100); c.close_path(); fill_stroke(c, "#8a6a3a", 7, "#1a1a1a")
    c.rectangle(-20, 0, 40, 90); fill_stroke(c, "#7a5a2a", 6, "#1a1a1a"); rrect(c, -80, 80, 160, 30, 8); fill_stroke(c, "#7a5a2a", 6, "#1a1a1a")
    c.restore()

def trophy(c, x, y, s, u=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    glow(c, 0, -20, 160, (1, .9, .4), .5 + .15 * math.sin(u * 6))
    c.move_to(-40, -50); c.line_to(40, -50); c.curve_to(40, 15, -40, 15, -40, -50); c.close_path(); fill_stroke(c, "#f2c94c", 5, "#1a1a1a")
    c.rectangle(-8, 8, 16, 24); c.set_source_rgb(.9, .7, .2); c.fill(); rrect(c, -28, 30, 56, 14, 4); fill_stroke(c, "#f2c94c", 4, "#1a1a1a")
    c.restore()

def box_trap(c, x, ground, w, h, txt, u, brk=None):
    k = ease_io(prog(u, brk, brk + 0.5)) if brk is not None else 0
    for i, (dx, dy, rr) in enumerate(((-1, 0, -1), (1, 0, 1), (0, -1, 0))):
        c.save()
        c.translate(dx * 500 * k, dy * 400 * k); c.rotate(rr * k * .8)
        if i == 0: c.rectangle(x - w / 2, ground - h, 18, h)
        elif i == 1: c.rectangle(x + w / 2 - 18, ground - h, 18, h)
        else: c.rectangle(x - w / 2, ground - h - 18, w, 18)
        fill_stroke(c, "#6b4a2b", 5, "#1a1a1a"); c.restore()
    if k < 0.3:
        c.set_source_rgba(.2, .1, .1, .5); c.set_line_width(5)
        for i in range(1, 6): bx = x - w / 2 + i * w / 6; c.move_to(bx, ground - h); c.line_to(bx, ground); c.stroke()
        label(c, txt, x, ground - h - 50, 34, 1.0, fill="#ffd0d0")

def signpost(c, x, ground, s, left, right, u=0.0):
    c.save(); c.translate(x, ground); c.scale(s, s)
    c.rectangle(-12, -420, 24, 420); fill_stroke(c, "#7a5a3a", 5, "#1a1a1a")
    for i, (txt, d) in enumerate(((left, -1), (right, 1))):
        y = -380 + i * 110 + math.sin(u * 2 + i) * 3
        c.move_to(0, y - 38); c.line_to(d * 300, y - 38); c.line_to(d * 340, y); c.line_to(d * 300, y + 38); c.line_to(0, y + 38); c.close_path()
        fill_stroke(c, "#f2e2c0", 5, "#1a1a1a"); text(c, txt, d * 165, y, 34 if len(txt) < 16 else 26)
    c.restore()

def limo(c, x, ground, s, u, rob_in=True):
    c.save(); c.translate(x, ground); c.scale(s, s)
    c.move_to(-420, -20); c.curve_to(-420, -90, -380, -100, -330, -100); c.line_to(-260, -170); c.line_to(300, -170); c.line_to(360, -100)
    c.curve_to(420, -100, 440, -70, 440, -20); c.close_path(); fill_stroke(c, "#121418", 7, "#000000")
    for i, wx in enumerate((-230, -90, 50, 190)):
        rrect(c, wx, -158, 120, 52, 8); fill_stroke(c, "#3a4a5e", 4, "#000000")
    if rob_in:
        c.save(); rrect(c, 190, -158, 120, 52, 8); c.clip(); tiny_head(c, 250, -95, 0.32); c.restore()
    for wx in (-300, 320): c.arc(wx, -10, 46, 0, TAU); fill_stroke(c, "#1a1a1a", 5); c.arc(wx, -10, 18, 0, TAU); c.set_source_rgb(.6, .6, .6); c.fill()
    c.restore()

def globe(c, x, y, r, u):
    c.save(); c.translate(x, y)
    c.arc(0, 0, r, 0, TAU); fill_stroke(c, "#3a7fc4", 7, "#1a1a1a")
    c.save(); c.arc(0, 0, r, 0, TAU); c.clip()
    rnd = random.Random(1)
    for i in range(9):
        cx = ((rnd.uniform(-1.6, 1.6) + u * 0.25) % 3.2 - 1.6) * r; cy = rnd.uniform(-.7, .7) * r
        c.save(); c.translate(cx, cy); c.scale(1.4, 1); c.arc(0, 0, rnd.uniform(.15, .3) * r, 0, TAU); c.restore(); c.set_source_rgb(.38, .7, .38); c.fill()
    c.restore(); c.arc(0, 0, r, 0, TAU); c.set_source_rgb(*INK); c.set_line_width(7); c.stroke(); c.restore()

def flashes(c, u, x0, y0, x1, y1, seed=0, rate=6):
    rnd = random.Random(seed + int(u * rate))
    for i in range(3):
        if rnd.random() < .5:
            x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1); glow(c, x, y, 110, (1, 1, 1), .85)
            c.move_to(x - 40, y); c.line_to(x + 40, y); c.move_to(x, y - 40); c.line_to(x, y + 40); c.set_source_rgba(1, 1, 1, .9); c.set_line_width(4); c.stroke()

def newspaper(c, x, y, s, head, u=0.0, t0=0.0, rot=-0.06, spin=False):
    k = pop(u, t0, 0.5)
    if k <= 0.002: return
    c.save(); c.translate(x, y); c.rotate(rot + (1 - k) * (6 if spin else 0)); c.scale(s * k, s * k)
    c.rectangle(-220, -150, 440, 300); fill_stroke(c, "#f3efe6", 6, "#1a1a1a")
    text(c, "THE DAILY", 0, -118, 30, color="#555555")
    c.select_font_face("Patrick Hand"); c.set_font_size(46)
    words = head.split(); lines = [""]
    for wd in words:
        tr = (lines[-1] + " " + wd).strip()
        if c.text_extents(tr).width > 400: lines.append(wd)
        else: lines[-1] = tr
    for i, ln in enumerate(lines[:2]): text(c, ln, 0, -60 + i * 50, 46)
    for i in range(4): c.rectangle(-200, 50 + i * 22, 180, 8); c.rectangle(20, 50 + i * 22, 180, 8); c.set_source_rgb(.7, .7, .7); c.fill()
    c.restore()

def laptop(c, x, y, s, u, lines, t0=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -240, -300, 480, 320, 16); fill_stroke(c, "#2a2a2a", 7, "#0a0a0a")
    rrect(c, -220, -280, 440, 280, 8); c.set_source_rgb(.96, .97, 1); c.fill()
    c.move_to(-300, 20); c.line_to(300, 20); c.line_to(260, 60); c.line_to(-260, 60); c.close_path(); fill_stroke(c, "#bbbbbb", 6, "#0a0a0a")
    total = sum(len(l) for l in lines); shown = int(total * clamp((u - t0) / 1.6)); acc = 0
    for i, ln in enumerate(lines):
        n = clamp(shown - acc, 0, len(ln)); acc += len(ln)
        text(c, ln[:int(n)], -200, -240 + i * 46, 32, align="l")
    c.restore()

def spaceship(c, x, y, s, u, flame=True):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(math.sin(u * 1.5) * .04)
    if flame:
        for i in range(3):
            c.move_to(-200, -30 + i * 30); c.line_to(-260 - 60 * abs(math.sin(u * 20 + i)), -15 + i * 30); c.line_to(-200, 0 + i * 30); c.close_path(); c.set_source_rgba(1, .6, .2, .8); c.fill()
    c.move_to(-200, -60); c.line_to(150, -60); c.curve_to(260, -60, 280, 0, 280, 20); c.curve_to(280, 40, 260, 100, 150, 100); c.line_to(-200, 100); c.close_path()
    fill_stroke(c, "#d9dde3", 7, "#1a1a1a")
    for wx in (-120, -20, 80): c.arc(wx, 20, 26, 0, TAU); fill_stroke(c, "#7fb6e0", 5, "#1a1a1a")
    c.move_to(-180, -60); c.line_to(-240, -150); c.line_to(-100, -60); c.close_path(); fill_stroke(c, "#d6402f", 5, "#1a1a1a")
    c.move_to(-180, 100); c.line_to(-240, 190); c.line_to(-100, 100); c.close_path(); fill_stroke(c, "#d6402f", 5, "#1a1a1a")
    c.restore()

def printer(c, x, ground, s, u, k, count=None):
    c.save(); c.translate(x, ground); c.scale(s, s)
    rrect(c, -260, -330, 520, 330, 20); fill_stroke(c, "#cfd6de", 7, "#1a1a1a")
    c.rectangle(-180, -300, 360, 40); c.set_source_rgb(.1, .1, .1); c.fill()
    for i in range(3): c.arc(180 + i * 0, -200 + i * 40, 14, 0, TAU); c.set_source_rgb(*((.3, .9, .4) if (int(u * 4) + i) % 3 == 0 else (.4, .4, .4))); c.fill()
    c.save(); c.rectangle(-170, -900, 340, 610); c.clip()
    tiny_head(c, 0, -300 - 360 * k + 170 * 0, 0.9)
    c.restore()
    if count: label(c, count, 0, -380 - 360 * k, 34, 1.0, fill="#f2c94c")
    c.restore()

def balance(c, x, y, s, left, right, tilt, u=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.rectangle(-14, -20, 28, 300); fill_stroke(c, "#8a6a3a", 5, "#1a1a1a"); c.rectangle(-120, 270, 240, 30); fill_stroke(c, "#8a6a3a", 5, "#1a1a1a")
    a = tilt + math.sin(u * 3) * .02
    c.save(); c.rotate(a); c.rectangle(-320, -14, 640, 28); fill_stroke(c, "#a07a4a", 5, "#1a1a1a")
    for sx, txt in ((-300, left), (300, right)):
        c.save(); c.translate(sx, 0); c.rotate(-a)
        wline(c, [(0, 0), (-80, 140)], 0, amp=0); wline(c, [(0, 0), (80, 140)], 0, amp=0)
        c.move_to(-110, 140); c.line_to(110, 140); c.curve_to(90, 190, -90, 190, -110, 140); fill_stroke(c, "#f2c94c", 5, "#1a1a1a")
        label(c, txt, 0, 100, 30, 1.0); c.restore()
    c.restore(); c.restore()

def gauge(c, x, y, s, title, val, u=0.0, colors=("#3fbf5a", "#f2c94c", "#d6402f")):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.arc(0, 0, 150, math.pi, TAU); c.close_path(); fill_stroke(c, "#ffffff", 6, "#1a1a1a")
    for i, col in enumerate(colors):
        c.move_to(0, 0); c.arc(0, 0, 130, math.pi + i * math.pi / 3, math.pi + (i + 1) * math.pi / 3); c.close_path(); c.set_source_rgba(*hexc(col)[:3], .85); c.fill()
    na = math.pi + val * math.pi + 0.04 * math.sin(u * 9)
    c.move_to(0, 0); c.line_to(math.cos(na) * 120, math.sin(na) * 120); c.set_source_rgb(*INK); c.set_line_width(8); c.stroke()
    c.arc(0, 0, 12, 0, TAU); c.fill()
    text(c, title, 0, 40, 32)
    c.restore()

def vinyl(c, x, y, r, u, lab="", color="#d6402f"):
    c.save(); c.translate(x, y); c.rotate(u * 4)
    c.arc(0, 0, r, 0, TAU); fill_stroke(c, "#111111", 6, "#000000")
    for rr in (0.85, 0.7, 0.55): c.arc(0, 0, r * rr, 0, TAU); c.set_source_rgba(1, 1, 1, .12); c.set_line_width(3); c.stroke()
    c.arc(0, 0, r * .35, 0, TAU); c.set_source_rgb(*hexc(color)[:3]); c.fill(); c.arc(0, 0, 8, 0, TAU); c.set_source_rgb(0, 0, 0); c.fill()
    c.restore()
    if lab: label(c, lab, x, y + r + 40, 30, 1.0)

def piano(c, x, ground, s):
    c.save(); c.translate(x, ground); c.scale(s, s)
    c.rectangle(-260, -330, 520, 220); fill_stroke(c, "#2a1a10", 7, "#0a0a0a")
    c.rectangle(-260, -110, 520, 50); fill_stroke(c, "#ffffff", 5, "#0a0a0a")
    for i in range(1, 20): c.move_to(-260 + i * 26, -110); c.line_to(-260 + i * 26, -60); c.set_source_rgb(*INK); c.set_line_width(2); c.stroke()
    for i in range(19):
        if i % 7 not in (2, 6): c.rectangle(-246 + i * 26, -110, 14, 30); c.set_source_rgb(0, 0, 0); c.fill()
    for lx in (-230, 230): c.rectangle(lx - 12, -60, 24, 60); c.set_source_rgb(.15, .1, .05); c.fill()
    c.restore()

def notes(c, x, y, u, n=5, seed=0, color=(0.1, 0.1, 0.1)):
    rnd = random.Random(seed)
    for i in range(n):
        ph = rnd.random(); t = (u * 0.5 + ph) % 1
        nx = x + rnd.uniform(-120, 120) + math.sin(u * 2 + i) * 20; ny = y - t * 260
        c.save(); c.translate(nx, ny); c.rotate(.2)
        c.save(); c.scale(1.3, 1); c.arc(0, 0, 11, 0, TAU); c.restore(); c.set_source_rgba(*color, 1 - t); c.fill()
        c.rectangle(11, -50, 5, 50); c.fill(); c.restore()

def cake(c, x, ground, s, crack=0.0):
    c.save(); c.translate(x, ground); c.scale(s, s)
    for i, (w, h) in enumerate(((300, 120), (220, 100), (140, 90))):
        y = -sum(hh for _, hh in ((300, 120), (220, 100), (140, 90))[:i + 1])
        c.save(); c.translate((crack * 30) * (1 if i % 2 else -1), 0)
        rrect(c, -w / 2, y, w, h, 14); fill_stroke(c, "#fdf6ea", 6, "#1a1a1a")
        c.move_to(-w / 2, y + 22)
        for k in range(9): c.line_to(-w / 2 + (k + .5) * w / 9, y + (36 if k % 2 == 0 else 22))
        c.set_source_rgb(.95, .75, .8); c.set_line_width(6); c.stroke(); c.restore()
    if crack > 0:
        c.move_to(0, -310); c.line_to(-15, -240); c.line_to(12, -170); c.line_to(-10, -90); c.line_to(8, 0)
        c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
    c.restore()

def rings(c, x, y, s, u):
    c.save(); c.translate(x, y); c.scale(s, s)
    for dx in (-26, 26): c.arc(dx, 0, 40, 0, TAU); c.set_source_rgb(.95, .78, .2); c.set_line_width(12); c.stroke()
    stars(c, 0, -20, 50, 4, u, seed=3, color=(1, 1, .8)); c.restore()

def ship(c, x, y, s, u):
    c.save(); c.translate(x, y + math.sin(u * 2) * 8); c.scale(s, s); c.rotate(math.sin(u * 1.6) * .05)
    c.move_to(-300, 0); c.line_to(300, 0); c.line_to(220, 90); c.line_to(-220, 90); c.close_path(); fill_stroke(c, "#7a4a2a", 7, "#1a1a1a")
    for i in range(7): c.arc(-180 + i * 60, 45, 10, 0, TAU); c.set_source_rgb(.2, .1, .05); c.fill()
    wline(c, [(0, 0), (0, -380)], 0, amp=0)
    c.move_to(0, -360); c.curve_to(160, -300, 160, -100, 0, -60); c.close_path(); fill_stroke(c, "#f3e7cf", 6, "#1a1a1a")
    c.move_to(-280, 0); c.curve_to(-340, -40, -330, -80, -300, -90); c.set_source_rgb(*INK); c.set_line_width(7); c.stroke()
    c.restore()

def waves(c, y, u, n=5, base=(.2, .4, .65), x0=-600, x1=2000):
    for i in range(n):
        yy = y + i * 40; ph = u * 2.5 + i
        c.move_to(x0, yy)
        for x in range(int(x0), int(x1), 40): c.line_to(x, yy + math.sin(x / 60 + ph) * 12)
        c.line_to(x1, 1200); c.line_to(x0, 1200); c.close_path()
        c.set_source_rgb(base[0] + i * .03, base[1] + i * .03, base[2] + i * .03); c.fill()

def columns(c, x0, x1, ground, top, n=5):
    for i in range(n):
        x = x0 + i * (x1 - x0) / (n - 1)
        c.rectangle(x - 40, top, 80, ground - top); fill_stroke(c, "#efe8d8", 6, "#1a1a1a")
        for k in range(1, 4): c.move_to(x - 40 + k * 20, top + 20); c.line_to(x - 40 + k * 20, ground - 20); c.set_source_rgba(0, 0, 0, .15); c.set_line_width(3); c.stroke()
        c.rectangle(x - 55, top - 30, 110, 30); fill_stroke(c, "#e3dccb", 5, "#1a1a1a")
    c.move_to(x0 - 80, top - 30); c.line_to((x0 + x1) / 2, top - 160); c.line_to(x1 + 80, top - 30); c.close_path(); fill_stroke(c, "#e8e0cc", 6, "#1a1a1a")

def clock(c, x, y, r, u, speed=1.0, txt=None):
    c.save(); c.translate(x, y)
    c.arc(0, 0, r, 0, TAU); fill_stroke(c, "#ffffff", 6, "#1a1a1a")
    for i in range(12):
        a = i / 12 * TAU; c.move_to(math.sin(a) * r * .8, -math.cos(a) * r * .8); c.line_to(math.sin(a) * r * .92, -math.cos(a) * r * .92); c.set_line_width(4); c.set_source_rgb(*INK); c.stroke()
    hm = -math.pi / 2 + u * speed * TAU * .5; hh = -math.pi / 2 + u * speed * TAU * .04 + 1
    c.move_to(0, 0); c.line_to(math.cos(hh) * r * .5, math.sin(hh) * r * .5); c.set_line_width(7); c.stroke()
    c.move_to(0, 0); c.line_to(math.cos(hm) * r * .78, math.sin(hm) * r * .78); c.set_line_width(5); c.set_source_rgb(.8, .15, .1); c.stroke()
    c.arc(0, 0, 8, 0, TAU); c.set_source_rgb(*INK); c.fill()
    if txt: text(c, txt, 0, r + 36, 32)
    c.restore()

def test_kit(c, x, y, s, u, t0=0.6):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(0.1)
    rrect(c, -70, -220, 140, 440, 30); fill_stroke(c, "#ffffff", 7, "#1a1a1a")
    rrect(c, -30, -120, 60, 160, 8); fill_stroke(c, "#f3efe6", 4, "#1a1a1a")
    text(c, "C", -50, -90, 26); text(c, "T", -50, 0, 26)
    c.rectangle(-26, -94, 52, 8); c.set_source_rgb(.8, .1, .3); c.fill()
    k = clamp((u - t0) / 0.6)
    if k > 0: c.rectangle(-26, -4, 52, 8); c.set_source_rgba(.8, .1, .3, k); c.fill()
    c.arc(0, 140, 30, 0, TAU); fill_stroke(c, "#f3efe6", 4, "#1a1a1a")
    c.restore()

def hourglass(c, x, y, s, u):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(math.sin(u * 2) * .05)
    for yy in (-170, 150): rrect(c, -110, yy, 220, 22, 6); fill_stroke(c, "#7a5a3a", 5, "#1a1a1a")
    c.move_to(-90, -150); c.line_to(90, -150); c.line_to(10, 0); c.line_to(90, 150); c.line_to(-90, 150); c.line_to(-10, 0); c.close_path()
    fill_stroke(c, "#e7f3f7", 6, "#1a1a1a")
    k = (u * 0.3) % 1
    c.move_to(-70 * (1 - k), -150 + 140 * k); c.line_to(70 * (1 - k), -150 + 140 * k); c.line_to(0, -10); c.close_path(); c.set_source_rgb(.9, .75, .4); c.fill()
    c.move_to(-80 * k, 150 - 120 * k); c.line_to(80 * k, 150 - 120 * k); c.line_to(85, 150); c.line_to(-85, 150); c.close_path(); c.fill()
    c.rectangle(-3, -10, 6, 160); c.fill()
    c.restore()

def magnifier(c, x, y, s, rot=-0.6):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.rectangle(-16, 90, 32, 170); fill_stroke(c, "#6b3b1a", 5, "#1a1a1a")
    c.arc(0, 0, 100, 0, TAU); c.set_source_rgba(.8, .9, 1, .35); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(14); c.stroke()
    c.restore()

def bulb(c, x, y, s, on=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    if on > 0: glow(c, 0, 0, 200, (1, .95, .5), .6 * on)
    c.arc(0, 0, 70, 0, TAU); fill_stroke(c, "#fff3a8" if on > .5 else "#dddddd", 6, "#1a1a1a")
    c.rectangle(-36, 60, 72, 50); fill_stroke(c, "#aaaaaa", 5, "#1a1a1a")
    c.restore()

def rating(c, x, y, s, n, u, t0=0.0):
    for i in range(5):
        k = pop(u, t0 + i * 0.12)
        if k <= 0.002: continue
        c.save(); c.translate(x + (i - 2) * 90 * s, y); c.scale(s * k, s * k)
        for j in range(10):
            a = -math.pi / 2 + j * math.pi / 5; r = 40 if j % 2 == 0 else 17
            (c.move_to if j == 0 else c.line_to)(math.cos(a) * r, math.sin(a) * r)
        c.close_path(); fill_stroke(c, "#f2c94c" if i < n else "#dddddd", 4, "#1a1a1a"); c.restore()

def quote_card(c, x, y, w, txt, who, u, t0=0.0):
    k = pop(u, t0, 0.4)
    if k <= 0.002: return
    c.select_font_face("Patrick Hand"); c.set_font_size(46)
    words = txt.split(); lines = [""]
    for wd in words:
        tr = (lines[-1] + " " + wd).strip()
        if c.text_extents(tr).width > w - 80: lines.append(wd)
        else: lines[-1] = tr
    h = 70 + len(lines) * 56 + 60
    c.save(); c.translate(x, y); c.scale(k, k); c.rotate(-0.02)
    rrect(c, -w / 2, -h / 2, w, h, 18); fill_stroke(c, "#fffaf0", 7, "#1a1a1a")
    text(c, "“", -w / 2 + 40, -h / 2 + 40, 90, color="#c0392b")
    nshow = len(" ".join(lines)) * clamp((u - t0 - 0.3) / 2.0); acc = 0
    for i, ln in enumerate(lines):
        m = int(clamp(nshow - acc, 0, len(ln))); acc += len(ln) + 1
        text(c, ln[:m], -w / 2 + 50, -h / 2 + 80 + i * 56, 46, align="l")
    text(c, "— " + who, w / 2 - 40, h / 2 - 40, 34, color="#555555", align="r")
    c.restore()

def mic(c, x, y, s, txt=None):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -40, -120, 80, 140, 40); fill_stroke(c, "#555555", 6, "#1a1a1a")
    for i in range(4): c.move_to(-36, -90 + i * 25); c.line_to(36, -90 + i * 25); c.set_source_rgba(1, 1, 1, .3); c.set_line_width(3); c.stroke()
    c.rectangle(-10, 20, 20, 260); fill_stroke(c, "#333333", 5, "#1a1a1a")
    if txt: label(c, txt, 0, -190, 34, 1.0, fill="#ffd0d0")
    c.restore()

def gate(c, x0, x1, ground, h, u=0.0, locked=True):
    for x in range(int(x0), int(x1), 40):
        c.rectangle(x, ground - h, 14, h); fill_stroke(c, "#2a2a2a", 3, "#000000")
        c.move_to(x - 6, ground - h); c.line_to(x + 7, ground - h - 30); c.line_to(x + 20, ground - h); c.close_path(); c.set_source_rgb(.15, .15, .15); c.fill()
    for yy in (ground - h + 30, ground - 40): c.rectangle(x0, yy, x1 - x0, 12); c.set_source_rgb(.15, .15, .15); c.fill()
    if locked:
        mx = (x0 + x1) / 2; my = ground - h / 2
        c.arc(mx, my - 40, 34, math.pi, TAU); c.set_source_rgb(*INK); c.set_line_width(12); c.stroke()
        rrect(c, mx - 50, my - 40, 100, 90, 12); fill_stroke(c, "#f2c94c", 6, "#1a1a1a")

def qmarks(c, x, y, u, n=4, seed=0, color="#1a1a1a", size=70):
    rnd = random.Random(seed)
    for i in range(n):
        ph = rnd.random() * 6
        text(c, "?", x + (i - n / 2) * 70 + math.sin(u * 3 + ph) * 10, y + math.cos(u * 2.5 + ph) * 14, size, color=color, rot=math.sin(u * 2 + ph) * .3)

def bubble(c, x, y, w, h, u, t0=0.0, inner=None, tail=(-60, 120)):
    k = pop(u, t0)
    if k <= 0.002: return
    c.save(); c.translate(x, y); c.scale(k, k)
    for i, rr in enumerate((10, 16, 24)):
        c.arc(tail[0] * (1 - i * .3), tail[1] * (1 - i * .3) + h / 2 - 20, rr, 0, TAU); fill_stroke(c, "#ffffff", 4, "#1a1a1a")
    c.save(); c.scale(w / 2, h / 2); c.arc(0, 0, 1, 0, TAU); c.restore(); fill_stroke(c, "#ffffff", 6, "#1a1a1a")
    if inner: inner(c)
    c.restore()

def speedo(c, x, y, s, u, val):
    gauge(c, x, y, s, "SPEED", val, u, colors=("#3fbf5a", "#f2c94c", "#d6402f"))

def marquee(c, x, y, s, txt, u, color="#d6402f"):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -330, -110, 660, 220, 14); fill_stroke(c, color, 8, "#1a1a1a")
    rrect(c, -290, -70, 580, 140, 8); fill_stroke(c, "#fff6d8", 5, "#1a1a1a")
    text(c, txt, 0, 0, 58 if len(txt) < 15 else 40)
    for i in range(22):
        a = i / 22
        bx = -330 + a * 660 if i < 11 else -330 + (a - .5) * 2 * 660
        by = -110 if i < 11 else 110
        on = (i + int(u * 8)) % 3 == 0
        c.arc(bx, by, 9, 0, TAU); c.set_source_rgb(*((1, .95, .5) if on else (.6, .5, .3))); c.fill()
    c.restore()

def reel(c, x, y, r, u, color="#333333"):
    c.save(); c.translate(x, y); c.rotate(u * 3)
    c.arc(0, 0, r, 0, TAU); fill_stroke(c, color, 6, "#0a0a0a")
    for i in range(5):
        a = i / 5 * TAU; c.arc(math.cos(a) * r * .55, math.sin(a) * r * .55, r * .2, 0, TAU); c.set_source_rgb(.9, .9, .9); c.fill()
    c.arc(0, 0, r * .12, 0, TAU); c.set_source_rgb(.9, .9, .9); c.fill(); c.restore()

def heart(c, x, y, s, color="#e0405a", a=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(0, 30); c.curve_to(-60, -10, -30, -60, 0, -26); c.curve_to(30, -60, 60, -10, 0, 30); c.close_path()
    c.set_source_rgba(*hexc(color)[:3], a); c.fill_preserve(); c.set_source_rgba(*INK, a); c.set_line_width(4); c.stroke(); c.restore()

def hearts_up(c, x, y, u, n=6, seed=0, color="#e0405a"):
    rnd = random.Random(seed)
    for i in range(n):
        ph = rnd.random(); t = (u * .6 + ph) % 1
        heart(c, x + rnd.uniform(-150, 150) + math.sin(u * 3 + i) * 20, y - t * 300, 0.8 + rnd.random() * .5, color, 1 - t)

def thumbs(c, x, y, s, up=True):
    c.save(); c.translate(x, y); c.scale(s, -s if not up else s)
    rrect(c, -50, -20, 100, 110, 20); fill_stroke(c, "#f2d6b3", 6, "#1a1a1a")
    rrect(c, -20, -110, 40, 110, 18); fill_stroke(c, "#f2d6b3", 6, "#1a1a1a")
    c.restore()

def headshot(c, x, y, s, rot=0.0, gray=False):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.rectangle(-110, -140, 220, 280); fill_stroke(c, "#ffffff", 6, "#1a1a1a")
    c.rectangle(-95, -125, 190, 200); c.set_source_rgb(.85, .88, .92); c.fill()
    tiny_head(c, 0, -30, 0.45)
    c.restore()

def dumbbell(c, x, y, s, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.rectangle(-120, -10, 240, 20); fill_stroke(c, "#888888", 4, "#1a1a1a")
    for dx in (-130, 100): rrect(c, dx, -50, 30, 100, 6); fill_stroke(c, "#333333", 5, "#1a1a1a")
    c.restore()

def lightning(c, x, y, s, u, every=1.3, seed=0):
    ph = (u + seed) % every
    if ph < 0.12:
        c.save(); c.translate(x, y); c.scale(s, s)
        c.move_to(0, 0); c.line_to(-40, 120); c.line_to(10, 120); c.line_to(-30, 260); c.line_to(60, 90); c.line_to(10, 90); c.line_to(40, 0); c.close_path()
        c.set_source_rgb(1, 1, .8); c.fill(); c.restore()
        return True
    return False

def rain(c, f, n=140, alpha=.45, seed=0):
    rnd = random.Random(int(f) + seed * 1000)
    c.set_source_rgba(.85, .85, .95, alpha); c.set_line_width(2)
    for i in range(n):
        x = rnd.uniform(-300, 1600); y = rnd.uniform(-200, 800); c.move_to(x, y); c.line_to(x - 8, y + 34); c.stroke()

def dust(c, u, n=40, seed=0, color=(.85, .65, .4)):
    rnd = random.Random(seed)
    for i in range(n):
        x = (rnd.uniform(-200, 1500) + u * 160 * (0.5 + rnd.random())) % 1700 - 200; y = rnd.uniform(100, 700) + math.sin(u + i) * 10
        c.arc(x, y, rnd.uniform(8, 30), 0, TAU); c.set_source_rgba(*color, .15); c.fill()

def map_pin(c, x, y, s, u, t0, name):
    k = pop(u, t0)
    if k <= 0.002: return
    c.save(); c.translate(x, y - 30 * (1 - k)); c.scale(s * k, s * k)
    c.move_to(0, 0); c.curve_to(-24, -30, -24, -56, 0, -56); c.curve_to(24, -56, 24, -30, 0, 0); fill_stroke(c, "#d6402f", 4, "#1a1a1a")
    c.arc(0, -38, 8, 0, TAU); c.set_source_rgb(1, 1, 1); c.fill(); c.restore()
    label(c, name, x, y + 34, 28, prog(u, t0 + .1, t0 + .4))

def tv_frame_text(c, txt, color="#ffffff", bg=(.1, .1, .15)):
    def inner(c2, u):
        c2.rectangle(-300, -200, 600, 400); c2.set_source_rgb(*bg); c2.fill()
        text(c2, txt, 0, 0, 44, color=color)
    return inner

def breaking_bar(c, u, txt, t0=0.0):
    k = ease_io(prog(u, t0, t0 + 0.4))
    c.save(); c.translate(-1280 * (1 - k), 0)
    c.rectangle(0, 560, 1280, 70); c.set_source_rgb(.75, .1, .1); c.fill()
    c.rectangle(0, 560, 230, 70); c.set_source_rgb(1, 1, 1); c.fill()
    text(c, "BREAKING", 115, 595, 38, color="#b01515"); text(c, txt, 250, 595, 38, color="#ffffff", align="l")
    c.restore()

# =====================================================================================
# backgrounds  (each: fn(c, u, f))
# =====================================================================================
def bg_paper(c, u, f):
    vgrad(c, "#efe7d4", "#ddd2b8")
    c.set_source_rgba(0, 0, 0, .05); c.set_line_width(1)
    for gx in range(-400, 1800, 50): c.move_to(gx, -400); c.line_to(gx, 1200); c.stroke()
    for gy in range(-400, 1200, 50): c.move_to(-400, gy); c.line_to(1800, gy); c.stroke()

def bg_wall(c, u, f, top="#e9e2d0", bot="#cfc4ab", floor="#a58a6a", fy=600):
    vgrad(c, top, bot)
    c.rectangle(-600, fy, 2600, 800); c.set_source_rgb(*hexc(floor)[:3]); c.fill()
    wline(c, [(-600, fy), (2000, fy)], f, amp=1.0, seed=5)

def bg_dark(c, u, f, top="#1d1a24", bot="#08070b", floor="#120f16"):
    vgrad(c, top, bot); c.rectangle(-600, 600, 2600, 800); c.set_source_rgb(*hexc(floor)[:3]); c.fill()

def spot(c, x, top=-100, ground=600, w=140, a=.18, col=(1, .95, .75)):
    glow(c, x, ground - 200, 280, col, a * 1.6)
    c.move_to(x - w / 2, top); c.line_to(x + w / 2, top); c.line_to(x + w * 1.7, ground); c.line_to(x - w * 1.7, ground); c.close_path()
    c.set_source_rgba(*col, a); c.fill()

def bg_street(c, u, f, river=False, night=False):
    vgrad(c, "#1b2440" if night else "#bfe0f2", "#33405e" if night else "#e8f3f8")
    from_ = ["#d9b38c", "#c98f6a", "#e3cfa6", "#b98466", "#d6c2a0", "#c7a27a"]
    c.rectangle(-600, 560, 2800, 60); c.set_source_rgb(.62, .62, .62); c.fill()
    c.rectangle(-600, 620, 2800, 400); c.set_source_rgb(*((.25, .45, .65) if river else (.42, .42, .44))); c.fill()
    for i in range(10):
        x = -300 + i * 190; h = 200 + (i % 3) * 30
        c.rectangle(x, 560 - h, 160, h); fill_stroke(c, from_[i % 6], 5, "#1a1a1a")
        c.move_to(x - 12, 560 - h); c.line_to(x + 80, 560 - h - 70); c.line_to(x + 172, 560 - h); c.close_path(); fill_stroke(c, "#6b3b2a", 5, "#1a1a1a")
        for wx in (x + 24, x + 96): c.rectangle(wx, 560 - h + 30, 40, 50); fill_stroke(c, "#ffe28a" if night else "#fff3c4", 4, "#1a1a1a")
        c.rectangle(x + 60, 480, 40, 80); fill_stroke(c, "#2f4f6f", 4, "#1a1a1a")

def bg_city_night(c, u, f, sky=("#3a0f12", "#0e0607"), wet=True):
    vgrad(c, *sky)
    rnd = random.Random(3)
    for i in range(22):
        x = -400 + i * 95; h = rnd.uniform(200, 440)
        c.rectangle(x, 600 - h, 88, h); c.set_source_rgb(.09, .05, .06); c.fill()
        for wy in range(int(600 - h + 20), 580, 40):
            if rnd.random() < .3: c.rectangle(x + 15, wy, 14, 18); c.set_source_rgba(1, .7, .3, .5); c.fill()
    c.rectangle(-600, 600, 2800, 400); c.set_source_rgb(.08, .06, .07); c.fill()

def bg_nyc(c, u, f):
    vgrad(c, "#120a2a", "#05030c")
    rnd = random.Random(8)
    for i in range(24):
        x = -400 + i * 92; h = rnd.uniform(250, 520)
        c.rectangle(x, 600 - h, 86, h); c.set_source_rgb(.08, .06, .14); c.fill()
        for wy in range(int(600 - h + 20), 580, 34):
            if rnd.random() < .35: c.rectangle(x + 12, wy, 12, 16); c.set_source_rgba(.4, .9, 1, .5); c.fill()
    for i, (x, col) in enumerate(((150, (1, .2, .6)), (700, (.3, 1, .9)), (1150, (1, .8, .2)))):
        glow(c, x, 420, 180, col, .25 + .1 * math.sin(u * 9 + i))
    c.rectangle(-600, 600, 2800, 400); c.set_source_rgb(.06, .05, .09); c.fill()

def bg_forest(c, u, f):
    vgrad(c, "#0f1d33", "#06101c")
    c.arc(980, 120, 60, 0, TAU); c.set_source_rgba(.92, .95, 1, .95); c.fill(); glow(c, 980, 120, 200, (.7, .8, 1), .25)
    for i, x in enumerate(range(-300, 1700, 140)):
        h = 520 + (i * 53) % 120
        c.rectangle(x - 26, 600 - h * .55, 52, h * .55); c.set_source_rgb(.16, .11, .08); c.fill()
        c.move_to(x, 600 - h); c.line_to(x + 110, 600 - h * .35); c.line_to(x - 110, 600 - h * .35); c.close_path(); c.set_source_rgb(.07, .16, .16); c.fill()
    c.rectangle(-600, 580, 2600, 400); c.set_source_rgb(.06, .12, .12); c.fill()

def bg_stage(c, u, f, curtain="#8a1f2a", lit=True):
    vgrad(c, "#2a1218", "#120709")
    c.rectangle(-600, 560, 2600, 600); c.set_source_rgb(.45, .3, .18); c.fill()
    for i in range(0, 2000, 60): c.move_to(i - 600, 560); c.line_to(i - 620, 1000); c.set_source_rgba(0, 0, 0, .15); c.set_line_width(3); c.stroke()
    for side in (-1, 1):
        x = 640 + side * 640
        for k in range(6):
            c.rectangle(x - side * k * 40 - 40, -200, 46, 780); c.set_source_rgb(*hexc(curtain)[:3]); c.fill()
            c.move_to(x - side * k * 40 - 40, -200); c.line_to(x - side * k * 40 - 40, 580); c.set_source_rgba(0, 0, 0, .35); c.set_line_width(4); c.stroke()
    c.rectangle(-600, -200, 2600, 90); c.set_source_rgb(*hexc(curtain)[:3]); c.fill()

def bg_cinema(c, u, f, screen=None, glowc=(.8, .85, 1)):
    vgrad(c, "#141118", "#07060a")
    rrect(c, 140, 30, 1000, 400, 8); fill_stroke(c, "#e8ecf2", 6, "#000000")
    glow(c, 640, 230, 700, glowc, .12)
    if screen:
        c.save(); rrect(c, 140, 30, 1000, 400, 8); c.clip(); screen(c, u); c.restore()

def seats(c, n=3, y0=520, dark=True, u=0.0, heads=True, seed=0, sparse=False):
    rnd = random.Random(seed)
    for r in range(n):
        y = y0 + r * 70
        for i in range(-2, 16):
            x = i * 100 + (r % 2) * 50
            if heads and (not sparse or rnd.random() < .08):
                c.arc(x, y - 30, 34, 0, TAU); c.set_source_rgb(.05, .05, .07); c.fill()
            rrect(c, x - 45, y - 10, 90, 90, 12); c.set_source_rgb(.35, .08, .1); c.fill()

def bg_room(c, u, f, wall="#e8dcc6", floor="#9a7a5a", window=True, night=False):
    vgrad(c, wall, hexc_dark(wall))
    if window:
        rrect(c, 860, 120, 260, 220, 8); fill_stroke(c, "#1b2440" if night else "#bfe0f2", 7, "#1a1a1a")
        if night:
            c.arc(1040, 180, 26, 0, TAU); c.set_source_rgb(.95, .95, .85); c.fill()
        c.move_to(990, 120); c.line_to(990, 340); c.move_to(860, 230); c.line_to(1120, 230); c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
    c.rectangle(-600, 600, 2600, 600); c.set_source_rgb(*hexc(floor)[:3]); c.fill()
    wline(c, [(-600, 600), (2000, 600)], f, amp=1.0, seed=6)
    if night: c.rectangle(-600, -600, 2600, 2000); c.set_source_rgba(0.05, 0.05, 0.2, .45); c.fill()

def hexc_dark(h, k=0.82):
    r, g, b, _ = hexc(h); return "#%02x%02x%02x" % (int(r * 255 * k), int(g * 255 * k), int(b * 255 * k))

def bg_school(c, u, f):
    vgrad(c, "#bfe0f2", "#e8f3f8")
    c.rectangle(-600, 580, 2600, 600); c.set_source_rgb(.45, .65, .35); c.fill()
    c.rectangle(240, 200, 800, 380); fill_stroke(c, "#b7564a", 7, "#1a1a1a")
    c.move_to(200, 200); c.line_to(640, 60); c.line_to(1080, 200); c.close_path(); fill_stroke(c, "#5a3a2a", 7, "#1a1a1a")
    for r in range(2):
        for i in range(6): c.rectangle(290 + i * 120, 250 + r * 120, 60, 80); fill_stroke(c, "#fff3c4", 4, "#1a1a1a")
    rrect(c, 590, 470, 100, 110, 10); fill_stroke(c, "#2f4f6f", 5, "#1a1a1a")

def bg_classroom(c, u, f):
    bg_wall(c, u, f, "#e6e0cc", "#cfc6ac", "#8a6a4a")
    rrect(c, 240, 90, 800, 330, 10); fill_stroke(c, "#2e4a3a", 10, "#6b4a2b")
    for i, ln in enumerate(("2 + 2 = 4", "a² + b² = c²")): text(c, ln, 640, 190 + i * 90, 56, color="#f3f3f3")

def bg_pub(c, u, f):
    bg_wall(c, u, f, "#4a2a18", "#2a160a", "#3a2412")
    for x in range(-200, 1600, 260):
        glow(c, x, 120, 140, (1, .75, .4), .35)
        wline(c, [(x, -100), (x, 90)], f, amp=0); c.arc(x, 110, 22, 0, TAU); c.set_source_rgb(1, .85, .5); c.fill()
    rrect(c, 760, 140, 360, 110, 10); fill_stroke(c, "#1a0e06", 6, "#000000"); text(c, "OPEN MIC", 940, 195, 64, color="#ffb347")

def bg_desert(c, u, f):
    vgrad(c, "#f0b46a", "#f7dca4")
    c.arc(1000, 160, 80, 0, TAU); c.set_source_rgb(1, .92, .6); c.fill(); glow(c, 1000, 160, 260, (1, .9, .5), .35)
    c.move_to(-600, 520); c.curve_to(-100, 440, 300, 540, 700, 470); c.curve_to(1000, 420, 1400, 500, 2000, 460); c.line_to(2000, 1200); c.line_to(-600, 1200); c.close_path()
    c.set_source_rgb(.85, .55, .3); c.fill()
    c.rectangle(-600, 600, 2600, 600); c.set_source_rgb(.78, .5, .28); c.fill()

def bg_jungle(c, u, f):
    vgrad(c, "#2f5a2a", "#173018")
    rnd = random.Random(4)
    for i in range(30):
        x = rnd.uniform(-300, 1600); y = rnd.uniform(-100, 500)
        c.save(); c.translate(x, y); c.rotate(rnd.uniform(-1, 1)); c.scale(2.2, .7); c.arc(0, 0, 60, 0, TAU); c.restore()
        c.set_source_rgb(.2 + rnd.random() * .15, .45 + rnd.random() * .2, .2); c.fill()
    for x in range(-200, 1600, 230):
        c.move_to(x, -200); c.curve_to(x + 40 + math.sin(u + x) * 20, 100, x - 30, 300, x + 10, 450); c.set_source_rgb(.15, .35, .12); c.set_line_width(8); c.stroke()
    c.rectangle(-600, 600, 2600, 600); c.set_source_rgb(.22, .3, .12); c.fill()

def bg_space(c, u, f):
    vgrad(c, "#05061a", "#0d0a24")
    rnd = random.Random(2)
    for i in range(160):
        x = (rnd.uniform(-400, 1700) - u * 20 * rnd.random()) % 2100 - 400; y = rnd.uniform(-300, 1000)
        c.arc(x, y, rnd.uniform(.8, 2.6), 0, TAU); c.set_source_rgba(1, 1, 1, .5 + .5 * abs(math.sin(u * 2 + i))); c.fill()
    c.arc(1100, 560, 180, 0, TAU); c.set_source_rgb(.55, .35, .6); c.fill(); glow(c, 1100, 560, 320, (.6, .4, .8), .25)

def bg_redcarpet(c, u, f):
    vgrad(c, "#1c1c28", "#0a0a12")
    c.move_to(520, 260); c.line_to(760, 260); c.line_to(1100, 760); c.line_to(180, 760); c.close_path(); c.set_source_rgb(.72, .1, .12); c.fill()
    for i in range(6): y = 260 + i * 55; c.move_to(520 - i * 57, y); c.line_to(760 + i * 57, y); c.set_source_rgba(0, 0, 0, .2); c.set_line_width(4); c.stroke()
    for side in (-1, 1):
        for i in range(5):
            x = 640 + side * (200 + i * 90); y = 300 + i * 80
            wline(c, [(x, y), (x, y + 80)], f, amp=0); c.arc(x, y, 12, 0, TAU); c.set_source_rgb(.85, .7, .3); c.fill()

def bg_throne(c, u, f):
    bg_wall(c, u, f, "#5a4a3a", "#3a2e24", "#6a5034")
    for x in (180, 1100):
        c.move_to(x - 70, 60); c.line_to(x + 70, 60); c.line_to(x + 70, 380); c.line_to(x, 330); c.line_to(x - 70, 380); c.close_path(); fill_stroke(c, "#1f3f8a", 6, "#1a1a1a")
        for k in range(3):
            c.save(); c.translate(x, 140 + k * 70); c.scale(.5, .5)
            c.move_to(0, -40); c.curve_to(30, -10, 20, 30, 0, 40); c.curve_to(-20, 30, -30, -10, 0, -40); c.set_source_rgb(.95, .8, .2); c.fill(); c.restore()
    c.rectangle(560, 260, 160, 340); fill_stroke(c, "#8a1f2a", 6, "#1a1a1a"); c.rectangle(540, 420, 200, 60); fill_stroke(c, "#c9a24a", 6, "#1a1a1a")

def bg_gray_room(c, u, f):
    vgrad(c, "#5a5a5a", "#2a2a2a")
    for x in range(-200, 1600, 120): c.rectangle(x, -200, 8, 800); c.set_source_rgba(0, 0, 0, .25); c.fill()
    rrect(c, 860, 120, 240, 220, 6); fill_stroke(c, "#8a8a8a", 7, "#111111")
    c.rectangle(-600, 600, 2600, 600); c.set_source_rgb(.25, .25, .25); c.fill()

def bg_mansion(c, u, f):
    vgrad(c, "#141a2a", "#05070c")
    c.rectangle(260, 120, 760, 480); fill_stroke(c, "#1c1f28", 7, "#000000")
    for r in range(2):
        for i in range(5):
            on = (r == 1 and i == 2)
            c.rectangle(310 + i * 140, 170 + r * 170, 80, 110); c.set_source_rgb(*((1, .85, .5) if on else (.12, .14, .2))); c.fill_preserve(); c.set_source_rgb(0, 0, 0); c.set_line_width(5); c.stroke()
    c.move_to(220, 120); c.line_to(640, -20); c.line_to(1060, 120); c.close_path(); fill_stroke(c, "#14161d", 7, "#000000")
    c.rectangle(-600, 600, 2600, 600); c.set_source_rgb(.06, .07, .1); c.fill()

def bg_palace(c, u, f):
    vgrad(c, "#e8c98a", "#f5e6c4")
    c.rectangle(-600, 600, 2600, 600); c.set_source_rgb(.82, .76, .66); c.fill()
    columns(c, 120, 1160, 600, 220, 6)

def bg_sea(c, u, f, storm=False):
    vgrad(c, "#5a5f66" if storm else "#8fc6e8", "#202326" if storm else "#e2f1f8")
    if not storm: c.arc(1050, 140, 60, 0, TAU); c.set_source_rgb(1, .92, .6); c.fill()
    waves(c, 520, u, 6, (.25, .3, .35) if storm else (.2, .45, .7))

def bg_dunes(c, u, f):
    vgrad(c, "#e9a25a", "#f6d6a0")
    for i, col in enumerate(((.88, .62, .34), (.82, .55, .3), (.76, .48, .26))):
        y = 380 + i * 90
        c.move_to(-600, y)
        for x in range(-600, 2000, 80): c.line_to(x, y + math.sin(x / 200 + i * 2) * 40)
        c.line_to(2000, 1200); c.line_to(-600, 1200); c.close_path(); c.set_source_rgb(*col); c.fill()

def bg_news(c, u, f):
    vgrad(c, "#123a6a", "#0a1a33")
    for x in range(-400, 1800, 80): c.move_to(x, -200); c.line_to(x + 400, 800); c.set_source_rgba(1, 1, 1, .04); c.set_line_width(20); c.stroke()
    rrect(c, 300, 470, 680, 160, 10); fill_stroke(c, "#e8ecf2", 7, "#1a1a1a")
    c.rectangle(300, 470, 680, 30); c.set_source_rgb(.75, .1, .1); c.fill()

def bg_hills(c, u, f):
    vgrad(c, "#0d1030", "#2a1a40")
    rnd = random.Random(5)
    for i in range(80): c.arc(rnd.uniform(-400, 1700), rnd.uniform(-200, 360), rnd.uniform(1, 2.5), 0, TAU); c.set_source_rgba(1, 1, 1, .5 + .5 * abs(math.sin(u * 2 + i))); c.fill()
    c.move_to(-600, 520); c.curve_to(0, 300, 500, 460, 800, 380); c.curve_to(1100, 310, 1500, 420, 2000, 380); c.line_to(2000, 1200); c.line_to(-600, 1200); c.close_path()
    c.set_source_rgb(.1, .08, .14); c.fill()
    for x in range(-200, 1600, 18):
        y = 560 + (x * 13) % 90
        c.arc(x, y, 2.4, 0, TAU); c.set_source_rgba(1, .85, .4, .7); c.fill()

def bg_bank(c, u, f, alarm=False):
    bg_wall(c, u, f, "#d8d2c4", "#bdb5a2", "#7a7a7a")
    columns(c, 260, 1020, 600, 220, 4)
    text(c, "BANK", 640, 120, 70)
    if alarm:
        a = .35 * (0.5 + 0.5 * math.sin(u * 14)); c.rectangle(-600, -600, 2600, 2000); c.set_source_rgba(1, 0, 0, a); c.fill()

def bg_studio_office(c, u, f):
    bg_wall(c, u, f, "#dfe6ee", "#c3ccd8", "#5a6270")
    rrect(c, 80, 120, 300, 200, 6); fill_stroke(c, "#ffffff", 6, "#1a1a1a")
    c.move_to(110, 290); c.line_to(170, 230); c.line_to(230, 260); c.line_to(350, 150); c.set_source_rgb(.2, .6, .3); c.set_line_width(6); c.stroke()
    c.rectangle(380, 470, 520, 40); fill_stroke(c, "#6b4a2b", 6, "#1a1a1a")

def bg_tvset(c, u, f):
    vgrad(c, "#2a3a6a", "#141c36")
    for i in range(8): glow(c, 100 + i * 160, 80, 90, (.6, .7, 1), .25)
    c.rectangle(-600, 600, 2600, 600); c.set_source_rgb(.16, .14, .2); c.fill()
    rrect(c, 140, 470, 420, 120, 30); fill_stroke(c, "#c0392b", 6, "#1a1a1a"); rrect(c, 760, 470, 300, 120, 30); fill_stroke(c, "#2f6fa8", 6, "#1a1a1a")

def bg_black(c, u, f):
    c.set_source_rgb(0, 0, 0); c.rectangle(-2000, -2000, 6000, 6000); c.fill()
