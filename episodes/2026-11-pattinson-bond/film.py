"""Episode: The Entire History of Robert Pattinson, the seventh James Bond (first minute).
Run from repo root:  python3 episodes/2026-11-pattinson-bond/film.py stills   (or: render)
"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import cairo
from toonkit.core import text, rrect, fill_stroke, hexc, ease_io, prog, clamp, W, H, FPS
from toonkit.rig import wline, INK, A_rest, A_talk, A_wave, A_point, A_shrug, A_shock, A_walk
from toonkit.scene import *
from toonkit import scene as _scene

SCRIPT = [
    "You know the gun barrel, the shaken martini, the tuxedo and the Aston Martin.",
    "Only six men have ever worn that suit.",
    "And on Monday the seventh was named.",
    "He is the same man who once died in a maze at the end of a wizard tournament,",
    "sparkled in a forest as a vampire,",
    "stood in the rain in a black cowl,",
    "and went mad in a lighthouse beside a seagull.",
    "The studio did not pick him in spite of that strange road.",
    "It picked him because of it.",
    "This is the entire history of Robert Pattinson, the seventh James Bond.",
    "Robert Douglas Thomas Pattinson was born on the 13th of May, 1986,",
    "in Barnes, a leafy corner of southwest London beside the Thames.",
    "His mother, Clare, worked for a modelling agency.",
    "His father, Richard, imported vintage cars from America.",
    "He grew up with two older sisters, Elizabeth and Victoria,",
    "and the family was comfortable but not famous, not even close.",
]

CAPS, TOTAL = caps_from_lines(SCRIPT, pauses={8: 0.9, 9: 0.9})
def T(i): return CAPS[i][0]

# ------------------------------------------------------------------ shots
def sh_martini(c, u, d, f):
    cam(c, 640, 380, 1.0 + 0.15 * ease_io(u / d))
    vgrad(c, "#3b2416", "#1b0f08")
    for x in range(80, 1280, 110):   # back bar bottles
        h = 120 + (x * 37) % 70
        rrect(c, x, 260 - h, 46, h, 10); c.set_source_rgba(.6, .35, .15, .35); c.fill()
        rrect(c, x + 14, 230 - h, 18, 40, 4); c.fill()
    c.rectangle(0, 262, 1280, 14); c.set_source_rgb(.25, .14, .07); c.fill()
    c.rectangle(-500, 520, 2300, 400); c.set_source_rgb(.36, .2, .1); c.fill()
    wline(c, [(-500, 520), (1800, 520)], f)
    glow(c, 640, 400, 380, (1, .8, .5), .18)
    pour = u > 1.7
    sx, sy = (560, 300) if not pour else (560 + 60 * ease_io(prog(u, 1.7, 2.0)), 300 - 20 * ease_io(prog(u, 1.7, 2.0)))
    shake = 0 if pour else math.sin(u * 40) * 14
    c.save(); c.translate(sx + shake, sy); c.rotate(math.sin(u * 40) * .12 if not pour else 1.9 * ease_io(prog(u, 1.7, 2.0)))
    rrect(c, -48, -90, 96, 170, 18); fill_stroke(c, "#c9ced6", 5, "#1a1a1a")
    rrect(c, -30, -132, 60, 46, 12); fill_stroke(c, "#aeb4bd", 5, "#1a1a1a")
    c.rectangle(-30, -50, 18, 100); c.set_source_rgba(1, 1, 1, .45); c.fill()
    c.restore()
    if not pour:
        for k in range(3):
            c.move_to(sx - 90 - k * 16, sy - 40 + k * 30); c.line_to(sx - 130 - k * 16, sy - 40 + k * 30)
            c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    gx, gy = 760, 420
    lvl = ease_io(prog(u, 1.9, 2.5))
    c.move_to(gx - 70, gy - 90); c.line_to(gx + 70, gy - 90); c.line_to(gx, gy); c.close_path(); fill_stroke(c, "#e7f3f7", 5, "#1a1a1a")
    if lvl > 0:
        k = 1 - lvl * 0.85; c.move_to(gx - 70 * (1 - k), gy - 90 * (1 - k)); c.line_to(gx + 70 * (1 - k), gy - 90 * (1 - k)); c.line_to(gx, gy); c.close_path()
        c.set_source_rgba(.85, .92, .7, .9); c.fill()
    if pour and u < 2.6:
        c.move_to(sx + 90, sy - 20); c.curve_to(sx + 140, sy, gx - 10, gy - 140, gx, gy - 40)
        c.set_source_rgba(.85, .92, .7, .9); c.set_line_width(8); c.stroke()
    wline(c, [(gx, gy), (gx, gy + 90)], f, seed=3); wline(c, [(gx - 45, gy + 92), (gx + 45, gy + 92)], f, seed=4)
    if lvl > .6:
        c.arc(gx + 10, gy - 40, 12, 0, TAU); fill_stroke(c, "#6f8f2a", 3)
        wline(c, [(gx + 10, gy - 40), (gx + 44, gy - 110)], f, amp=.6, seed=5)

def sh_tux(c, u, d, f):
    cam(c, 660 - 60 * ease_io(u / d), 360, 1.05)
    vgrad(c, "#20242c", "#0d0f13")
    glow(c, 640, 330, 330, (1, .95, .8), .22)
    c.move_to(560, -40); c.line_to(720, -40); c.line_to(900, 600); c.line_to(380, 600); c.close_path()
    g = cairo.LinearGradient(0, 0, 0, 600); g.add_color_stop_rgba(0, 1, .95, .8, .25); g.add_color_stop_rgba(1, 1, .95, .8, 0)
    c.set_source(g); c.fill()
    wline(c, [(640, 40), (640, 90)], f)
    c.move_to(540, 130); c.curve_to(560, 95, 720, 95, 740, 130); c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
    c.move_to(540, 130); c.line_to(520, 400); c.line_to(760, 400); c.line_to(740, 130); c.close_path(); fill_stroke(c, "#14161b", 5, "#000000")
    c.move_to(610, 128); c.line_to(640, 260); c.line_to(670, 128); c.close_path(); c.set_source_rgb(.96, .96, .96); c.fill()
    c.move_to(600, 128); c.line_to(640, 300); c.line_to(560, 160); c.close_path(); c.set_source_rgb(.18, .19, .23); c.fill()
    c.move_to(680, 128); c.line_to(640, 300); c.line_to(720, 160); c.close_path(); c.fill()
    c.move_to(622, 140); c.line_to(640, 150); c.line_to(658, 140); c.line_to(658, 160); c.line_to(640, 150); c.line_to(622, 160); c.close_path()
    c.set_source_rgb(.05, .05, .05); c.fill()
    for by in (310, 350): c.arc(640, by, 5, 0, TAU); c.set_source_rgb(.8, .8, .8); c.fill()
    k = ease_io(prog(u, 0.8, 1.6)); carx = 1500 - 1000 * k
    c.rectangle(-400, 560, 2200, 300); c.set_source_rgb(.1, .11, .13); c.fill()
    c.save(); c.translate(carx, 560)
    c.move_to(-200, -10); c.curve_to(-200, -60, -150, -70, -90, -75); c.curve_to(-40, -120, 70, -120, 110, -78)
    c.curve_to(180, -72, 210, -50, 210, -10); c.close_path(); fill_stroke(c, "#a8b0b8", 5, "#141414")
    c.move_to(-60, -78); c.curve_to(-30, -108, 60, -108, 90, -78); c.close_path(); c.set_source_rgb(.25, .35, .45); c.fill()
    for wx in (-120, 130): c.arc(wx, -8, 32, 0, TAU); fill_stroke(c, "#1a1a1a", 4); c.arc(wx, -8, 13, 0, TAU); c.set_source_rgb(.7, .7, .7); c.fill()
    if k < 1:
        for s in range(4):
            c.move_to(230 + s * 10, -60 + s * 16); c.line_to(330 + s * 30, -60 + s * 16); c.set_source_rgba(1, 1, 1, .6); c.set_line_width(4); c.stroke()
    c.restore()

def sh_six(c, u, d, f):
    cam(c, 560 + 140 * ease_io(u / d), 340, 1.1)
    vgrad(c, "#1d1a24", "#08070b")
    c.rectangle(-500, 560, 2500, 300); c.set_source_rgb(.12, .1, .14); c.fill()
    for i in range(6):
        x = 170 + i * 165; k = prog(u, 0.1 + i * 0.3, 0.45 + i * 0.3)
        if k <= 0: continue
        glow(c, x, 380, 160, (1, .9, .6), .14 * k)
        c.save(); c.translate(0, 40 * (1 - ease_out_back(k))); suit_figure(c, x, 560, 0.95); c.restore()
        c.save(); c.translate(x, 210); c.scale(ease_out_back(k), ease_out_back(k))
        c.arc(0, 0, 26, 0, TAU); fill_stroke(c, "#f2c94c", 4, "#1a1a1a"); text(c, str(i + 1), 0, 2, 32); c.restore()
    label(c, "ONLY SIX MEN", 640, 100, 40, prog(u, 2.0, 2.4), fill="#f2c94c")

def sh_calendar(c, u, d, f):
    cam(c, 640, 360, 1.15 + 0.25 * ease_io(u / d), 0.02)
    vgrad(c, "#e9e2d0", "#cfc4ab")
    k = ease_out_back(prog(u, 0.0, 0.35))
    c.save(); c.translate(640, 360); c.scale(k, k); c.rotate(-0.04)
    rrect(c, -170, -190, 340, 380, 14); fill_stroke(c, "#ffffff", 7, "#1a1a1a")
    c.rectangle(-170, -190, 340, 90); c.set_source_rgb(.82, .2, .18); c.fill()
    rrect(c, -170, -190, 340, 380, 14); c.set_source_rgb(*INK); c.set_line_width(7); c.stroke()
    text(c, "MONDAY", 0, -146, 48, color="#ffffff"); text(c, "16", 0, 30, 170); text(c, "NOVEMBER 2026", 0, 140, 34)
    for rx in (-90, 90): rrect(c, rx - 10, -210, 20, 44, 8); fill_stroke(c, "#888888", 4, "#1a1a1a")
    c.restore()

def sh_seventh(c, u, d, f):
    z = 1.0 + 0.6 * ease_io(prog(u, 1.0, d))
    cam(c, 870, 330 - 40 * ease_io(prog(u, 1.0, d)), z)
    vgrad(c, "#1d1a24", "#08070b")
    c.rectangle(-500, 560, 2500, 300); c.set_source_rgb(.12, .1, .14); c.fill()
    for i in range(6): suit_figure(c, 100 + i * 120, 560, 0.75)
    k = prog(u, 0.15, 0.55)
    glow(c, 960, 360, 260, (1, .92, .65), .35 * k)
    c.move_to(900, -100); c.line_to(1020, -100); c.line_to(1160, 600); c.line_to(760, 600); c.close_path()
    c.set_source_rgba(1, .95, .75, .18 * k); c.fill()
    drop = 1 - ease_out_back(k, 1.2)
    person(c, 960, 560 - 500 * drop, 0.38, P_(A_rest, u, tilt=0.05), f)
    c.save(); c.translate(1090, 180); s = ease_out_back(prog(u, 0.6, 0.9)); c.scale(s, s)
    c.arc(0, 0, 34, 0, TAU); fill_stroke(c, "#f2c94c", 5, "#1a1a1a"); text(c, "7", 0, 2, 46); c.restore()

def maze_walls(n=9, seed=4):
    rnd = random.Random(seed); vis = set(); walls = set()
    for x in range(n):
        for y in range(n):
            walls.add(((x, y), (x + 1, y))); walls.add(((x, y), (x, y + 1)))
            walls.add(((x + 1, y), (x + 1, y + 1))); walls.add(((x, y + 1), (x + 1, y + 1)))
    stack = [(0, 0)]; vis.add((0, 0))
    while stack:
        x, y = stack[-1]
        nb = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + dx < n and 0 <= y + dy < n and (x + dx, y + dy) not in vis]
        if not nb: stack.pop(); continue
        nx, ny = rnd.choice(nb)
        if nx != x: w = ((max(x, nx), y), (max(x, nx), y + 1))
        else: w = ((x, max(y, ny)), (x + 1, max(y, ny)))
        walls.discard(w); vis.add((nx, ny)); stack.append((nx, ny))
    return walls
MAZE = maze_walls()

def sh_maze_top(c, u, d, f):
    cam(c, 640, 360, 1.0 + 0.5 * ease_io(u / d), 0.15 * ease_io(u / d))
    vgrad(c, "#6d8f4e", "#4c6c35")
    cell = 62; ox, oy = 640 - 4.5 * cell, 360 - 4.5 * cell
    for (a, b) in MAZE:
        x0, y0 = ox + a[0] * cell, oy + a[1] * cell; x1, y1 = ox + b[0] * cell, oy + b[1] * cell
        c.move_to(x0, y0); c.line_to(x1, y1); c.set_source_rgb(.12, .2, .08); c.set_line_width(26); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
        c.move_to(x0, y0 - 3); c.line_to(x1, y1 - 3); c.set_source_rgb(.33, .55, .22); c.set_line_width(18); c.stroke()
    glow(c, 640, 360, 120, (1, .9, .4), .5 + .2 * math.sin(u * 6))
    c.save(); c.translate(640, 360)
    c.move_to(-22, -24); c.line_to(22, -24); c.curve_to(22, 10, -22, 10, -22, -24); c.close_path(); fill_stroke(c, "#f2c94c", 4, "#1a1a1a")
    c.rectangle(-5, 4, 10, 12); c.set_source_rgb(.9, .7, .2); c.fill(); rrect(c, -16, 14, 32, 9, 3); fill_stroke(c, "#f2c94c", 3, "#1a1a1a")
    c.restore()
    p = ease_io(prog(u, 0.2, 2.2)); pts = [(ox + 0.5 * cell, oy + 9 * cell + 30), (ox + 0.5 * cell, oy + 7.5 * cell), (ox + 2.5 * cell, oy + 7.5 * cell),
                                          (ox + 2.5 * cell, oy + 5.5 * cell), (ox + 4.5 * cell, oy + 5.5 * cell), (640, 360)]
    c.set_dash([10, 12]); c.set_source_rgb(.85, .15, .1); c.set_line_width(6)
    L = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)); acc = 0
    c.move_to(*pts[0])
    for i in range(len(pts) - 1):
        seg = math.dist(pts[i], pts[i + 1])
        if acc + seg >= p * L:
            k = (p * L - acc) / seg; c.line_to(pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k); break
        c.line_to(*pts[i + 1]); acc += seg
    c.stroke(); c.set_dash([])
    label(c, "2005", 330, 110, 36, prog(u, 0.3, 0.7), fill="#f2c94c")

def hedge_wall(c, x0, x1, top, ground):
    c.rectangle(x0, top, x1 - x0, ground - top); fill_stroke(c, "#3f6b2b", 6, "#16240f")
    rnd = random.Random(int(x0))
    for i in range(40):
        c.arc(rnd.uniform(x0, x1), rnd.uniform(top, ground), rnd.uniform(10, 26), 0, TAU); c.set_source_rgba(.25, .45, .15, .5); c.fill()

def sh_maze_side(c, u, d, f):
    if u < 1.7: cam(c, 560 + 60 * u, 360, 1.1)
    else: cam(c, 720, 470, 1.6, -0.04)
    vgrad(c, "#2b3346", "#151a25")
    c.arc(1050, 120, 50, 0, TAU); c.set_source_rgba(.95, .95, .85, .9); c.fill()
    c.rectangle(-500, 560, 2500, 400); c.set_source_rgb(.2, .26, .14); c.fill()
    hedge_wall(c, -300, 260, 140, 560); hedge_wall(c, 1050, 1600, 140, 560)
    glow(c, 900, 470, 140, (1, .9, .4), .55)
    c.save(); c.translate(900, 500)
    c.move_to(-40, -50); c.line_to(40, -50); c.curve_to(40, 15, -40, 15, -40, -50); c.close_path(); fill_stroke(c, "#f2c94c", 5, "#1a1a1a")
    c.rectangle(-8, 8, 16, 24); c.set_source_rgb(.9, .7, .2); c.fill(); rrect(c, -28, 30, 56, 14, 4); fill_stroke(c, "#f2c94c", 4, "#1a1a1a")
    c.restore()
    stars(c, 900, 470, 70, 8, u, seed=2, color=(1, .95, .6))
    if u < 1.6:
        x = 300 + 450 * ease_io(u / 1.6); person(c, x, 560, 0.36, A_walk(u), f)
    else:
        k = ease_io(prog(u, 1.9, 2.5))
        P = lerpP(P_(A_point, u), P_(A_rest, u), 0)
        person(c, 750 + 20 * k, 560, 0.36, P_(A_shock, u) if k < 0.05 else P_(A_rest, u), f, rot=-1.5 * k)
        if k > 0.95:
            label(c, "...", 760, 380, 40, prog(u, 2.7, 3.0))

def tree(c, x, ground, h, w, col, trunk="#2a1d14"):
    c.rectangle(x - w * .12, ground - h * .55, w * .24, h * .55); c.set_source_rgb(*hexc(trunk)[:3]); c.fill()
    c.move_to(x, ground - h); c.line_to(x + w / 2, ground - h * .35); c.line_to(x - w / 2, ground - h * .35); c.close_path()
    c.set_source_rgb(*hexc(col)[:3]); c.fill()

def sh_forest(c, u, d, f):
    cam(c, 600 + 80 * ease_io(u / d), 360, 1.15)
    vgrad(c, "#0f1d33", "#06101c")
    c.arc(980, 120, 60, 0, TAU); c.set_source_rgba(.92, .95, 1, .95); c.fill(); glow(c, 980, 120, 200, (.7, .8, 1), .25)
    for i, x in enumerate(range(-300, 1700, 140)): tree(c, x, 600, 520 + (i * 53) % 120, 220, "#132a2a")
    c.rectangle(-500, 580, 2500, 400); c.set_source_rgb(.06, .12, .12); c.fill()
    for i, x in enumerate(range(-200, 1700, 260)):
        if abs(x - 640) > 160: tree(c, x + 60, 640, 640, 300, "#0b1d1c", "#140d09")
    glow(c, 640, 380, 320, (.75, .85, 1), .42)
    person(c, 640, 600, 0.4, P_(A_rest, u, tilt=-0.06), f)
    c.save(); c.translate(0, 0)
    stars(c, 640, 330, 140, 26, u, seed=7)
    c.restore()
    label(c, "2008", 330, 120, 36, prog(u, 0.2, 0.6), fill="#cfe3ff")

def sh_rain(c, u, d, f):
    cam(c, 640, 330 - 20 * ease_io(u / d), 1.05 + 0.2 * ease_io(u / d), -0.03)
    vgrad(c, "#3a0f12", "#0e0607")
    rnd = random.Random(3)
    for i in range(18):
        x = -100 + i * 85; h = rnd.uniform(200, 420)
        c.rectangle(x, 560 - h, 80, h); c.set_source_rgb(.09, .05, .06); c.fill()
        for wy in range(int(560 - h + 20), 540, 40):
            if rnd.random() < .3: c.rectangle(x + 15, wy, 14, 18); c.set_source_rgba(1, .7, .3, .5); c.fill()
    c.rectangle(-500, 560, 2500, 400); c.set_source_rgb(.08, .06, .07); c.fill()
    c.save(); c.translate(640, 590); c.scale(1, .2); c.arc(0, 0, 200, 0, TAU); c.set_source_rgba(.6, .2, .2, .25); c.fill(); c.restore()
    wline(c, [(820, 590), (820, 150)], f, seed=11); rrect(c, 790, 120, 60, 36, 8); fill_stroke(c, "#ffe9a8", 4, "#111111")
    glow(c, 700, 330, 380, (1, .85, .6), .45)
    person(c, 640, 590, 0.42, P_(A_rest, u, tilt=0.02), f, mask=True)
    rnd = random.Random(int(f))
    c.set_source_rgba(.85, .85, .95, .45); c.set_line_width(2)
    for i in range(140):
        x = rnd.uniform(-200, 1500); y = rnd.uniform(-100, 760)
        c.move_to(x, y); c.line_to(x - 8, y + 34); c.stroke()
    label(c, "2022", 330, 130, 36, prog(u, 0.2, 0.6), fill="#ffb3b3")

def sh_lighthouse(c, u, d, f):
    cam(c, 640, 360, 1.0 + 0.2 * ease_io(u / d))
    vgrad(c, "#5a5f66", "#202326")
    flash = 1 if 0.6 < u < 0.7 or 0.78 < u < 0.84 else 0
    if flash: c.rectangle(-500, -500, 2500, 2000); c.set_source_rgba(1, 1, 1, .5); c.fill()
    c.move_to(760, 600); c.line_to(1060, 600); c.line_to(1000, 520); c.line_to(820, 520); c.close_path(); fill_stroke(c, "#3a3a3a", 5, "#111111")
    c.move_to(860, 520); c.line_to(960, 520); c.line_to(940, 220); c.line_to(880, 220); c.close_path(); fill_stroke(c, "#e8e8e8", 5, "#111111")
    for yy in (300, 400): c.rectangle(866, yy, 88, 34); c.set_source_rgb(.25, .25, .25); c.fill()
    rrect(c, 868, 168, 84, 54, 6); fill_stroke(c, "#fff6c8", 5, "#111111")
    c.move_to(860, 170); c.line_to(910, 130); c.line_to(960, 170); c.close_path(); fill_stroke(c, "#333333", 5, "#111111")
    a = u * 2.2
    c.move_to(910, 195); c.line_to(910 + math.cos(a) * 900, 195 + math.sin(a) * 120 - 60); c.line_to(910 + math.cos(a) * 900, 195 + math.sin(a) * 120 + 60); c.close_path()
    c.set_source_rgba(1, 1, .85, .25); c.fill()
    for i in range(6):
        y = 560 + i * 40; ph = u * 3 + i
        c.move_to(-200, y)
        for x in range(-200, 1600, 40): c.line_to(x, y + math.sin(x / 60 + ph) * 14)
        c.line_to(1600, 900); c.line_to(-200, 900); c.close_path(); c.set_source_rgba(.15 + i * .03, .17 + i * .03, .19 + i * .03, 1); c.fill()

def gull(c, x, y, s, u):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.save(); c.scale(1.4, 1); c.arc(0, 0, 40, 0, TAU); c.restore(); fill_stroke(c, "#f2f2f2", 5, "#111111")
    c.arc(-46, -38, 26, 0, TAU); fill_stroke(c, "#f2f2f2", 5, "#111111")
    c.arc(-52, -42, 5, 0, TAU); c.set_source_rgb(0, 0, 0); c.fill()
    op = abs(math.sin(u * 9)) * 10
    c.move_to(-70, -38); c.line_to(-102, -34 - op / 2); c.line_to(-70, -28); c.close_path(); fill_stroke(c, "#f2b233", 3, "#111111")
    c.move_to(-70, -30); c.line_to(-98, -26 + op); c.line_to(-70, -26); c.close_path(); fill_stroke(c, "#f2b233", 3, "#111111")
    c.move_to(-10, -10); c.curve_to(30, -40, 60, -20, 50, 10); c.close_path(); fill_stroke(c, "#bfbfbf", 4, "#111111")
    for lx in (-10, 10): wline(c, [(lx, 36), (lx, 70)], 0, amp=0, seed=lx)
    c.restore()

def sh_gull(c, u, d, f):
    sh = math.sin(u * 50) * 4
    cam(c, 640 + sh, 330, 1.2, 0.05)
    vgrad(c, "#6b6f75", "#2a2d31")
    c.rectangle(-500, 560, 2500, 400); c.set_source_rgb(.3, .3, .3); c.fill()
    c.rectangle(300, 470, 900, 14); c.set_source_rgb(.15, .15, .15); c.fill()
    for x in range(320, 1200, 90): c.rectangle(x, 470, 10, 90); c.fill()
    person(c, 560, 580, 0.42, A_shock(u), f)
    gull(c, 830, 425, 0.9, u)
    label(c, "SQUAWK!", 900, 290, 40, prog(u, 0.4, 0.7), rot=0.08)
    label(c, "2019", 330, 130, 36, prog(u, 0.2, 0.6))
    rnd = random.Random(int(f))
    c.set_source_rgba(.9, .9, .9, .35); c.set_line_width(2)
    for i in range(90):
        x = rnd.uniform(-200, 1500); y = rnd.uniform(-100, 760); c.move_to(x, y); c.line_to(x - 14, y + 30); c.stroke()

ROAD = [(80, 560), (260, 330), (480, 520), (700, 260), (920, 470), (1140, 240), (1360, 420), (1560, 300)]
def road_pts(n=200):
    pts = []
    for i in range(n + 1):
        t = i / n * (len(ROAD) - 1); k = min(int(t), len(ROAD) - 2); f = t - k
        p0 = ROAD[max(k - 1, 0)]; p1 = ROAD[k]; p2 = ROAD[k + 1]; p3 = ROAD[min(k + 2, len(ROAD) - 1)]
        def cr(a, b, c_, d_): return 0.5 * ((2 * b) + (-a + c_) * f + (2 * a - 5 * b + 4 * c_ - d_) * f * f + (-a + 3 * b - 3 * c_ + d_) * f ** 3)
        pts.append((cr(p0[0], p1[0], p2[0], p3[0]), cr(p0[1], p1[1], p2[1], p3[1])))
    return pts
RP = road_pts()

def icon(c, kind, x, y):
    c.save(); c.translate(x, y)
    c.arc(0, 0, 42, 0, TAU); fill_stroke(c, "#ffffff", 5, "#1a1a1a")
    if kind == "maze":
        for r in (28, 18, 8): c.rectangle(-r, -r, 2 * r, 2 * r); c.set_source_rgb(.25, .5, .2); c.set_line_width(4); c.stroke()
    elif kind == "fang":
        c.move_to(-20, -14); c.line_to(20, -14); c.line_to(10, -14); c.line_to(6, 20); c.line_to(2, -14); c.line_to(-2, -14); c.line_to(-6, 20); c.line_to(-10, -14); c.close_path()
        fill_stroke(c, "#ffffff", 3, "#1a1a1a"); c.rectangle(-24, -22, 48, 10); c.set_source_rgb(.7, .1, .15); c.fill()
    elif kind == "mask":
        c.move_to(-30, -4); c.curve_to(-20, -20, 20, -20, 30, -4); c.curve_to(20, 14, -20, 14, -30, -4); c.close_path(); c.set_source_rgb(.08, .08, .08); c.fill()
        for ex in (-12, 12): c.arc(ex, -3, 5, 0, TAU); c.set_source_rgb(1, 1, 1); c.fill()
    elif kind == "light":
        c.move_to(-10, 26); c.line_to(10, 26); c.line_to(6, -14); c.line_to(-6, -14); c.close_path(); fill_stroke(c, "#e8e8e8", 3, "#1a1a1a")
        c.rectangle(-8, -26, 16, 12); c.set_source_rgb(1, .85, .3); c.fill()
    elif kind == "star":
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5; r = 30 if i % 2 == 0 else 13
            (c.move_to if i == 0 else c.line_to)(math.cos(a) * r, math.sin(a) * r)
        c.close_path(); fill_stroke(c, "#f2c94c", 3, "#1a1a1a")
    c.restore()

STOPS = [(0.14, "maze"), (0.32, "fang"), (0.52, "mask"), (0.72, "light"), (0.98, "star")]
def sh_road(c, u, d, f):
    p = 0.02 + 0.7 * ease_io(u / d)
    i = int(p * (len(RP) - 1)); car = RP[i]
    if u < 2.4: cam(c, car[0] + 120, 380, 1.35, 0)
    else: cam(c, 820, 400, 0.72 + 0.05 * ease_io(prog(u, 2.4, d)), -0.02)
    vgrad(c, "#efe7d4", "#ddd2b8")
    c.set_source_rgba(0, 0, 0, .05); c.set_line_width(1)
    for gx in range(-200, 1800, 50): c.move_to(gx, -200); c.line_to(gx, 900); c.stroke()
    c.move_to(*RP[0])
    for q in RP[1:]: c.line_to(*q)
    c.set_source_rgb(*INK); c.set_line_width(46); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
    c.set_source_rgb(.45, .42, .4); c.set_line_width(36); c.stroke()
    c.move_to(*RP[0])
    for q in RP[1:]: c.line_to(*q)
    c.set_dash([18, 16]); c.set_source_rgb(.98, .9, .5); c.set_line_width(4); c.stroke(); c.set_dash([])
    for sp, kind in STOPS:
        q = RP[int(sp * (len(RP) - 1))]; icon(c, kind, q[0], q[1] - 70)
    c.save(); c.translate(*car)
    rrect(c, -26, -16, 52, 32, 10); fill_stroke(c, "#d6402f", 4, "#1a1a1a"); c.restore()
    label(c, "A STRANGE ROAD", car[0] + 120, 150, 38, prog(u, 0.3, 0.7), fill="#f2c94c")

def sh_because(c, u, d, f):
    cam(c, 1380 - 60 * ease_io(u / d), 330, 1.3)
    vgrad(c, "#efe7d4", "#ddd2b8")
    c.move_to(*RP[120])
    for q in RP[121:]: c.line_to(*q)
    c.set_source_rgb(*INK); c.set_line_width(46); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke_preserve()
    c.set_source_rgb(.45, .42, .4); c.set_line_width(36); c.stroke()
    q = RP[-4]; glow(c, q[0], q[1] - 90, 160, (1, .85, .3), .45 + .15 * math.sin(u * 5))
    s = 1 + 0.15 * ease_out_back(prog(u, 0.1, 0.5)); c.save(); c.translate(q[0], q[1] - 90); c.scale(s * 1.4, s * 1.4); icon(c, "star", 0, 0); c.restore()
    person(c, 1300, 520, 0.34, P_(A_point, u), f)
    label(c, "BECAUSE OF IT", 1380, 130, 42, prog(u, 0.6, 1.0), fill="#f2c94c")

def sh_title(c, u, d, f):
    c.set_source_rgb(0, 0, 0); c.paint()
    cam(c, 640, 360, 1.0 + 0.06 * u / d)
    l1 = "The Entire History of"; l2 = "Robert Pattinson"; l3 = "the seventh James Bond"
    n1 = int(len(l1) * clamp(u / 0.8)); n2 = int(len(l2) * clamp((u - 0.8) / 0.9)); n3 = int(len(l3) * clamp((u - 2.6) / 1.0))
    text(c, l1[:n1], 640, 270, 46, color="#bdbdbd")
    if n2: text(c, l2[:n2], 640, 350, 92, color="#ffffff")
    if n3: text(c, l3[:n3], 640, 440, 44, color="#f2c94c")

def sh_1986(c, u, d, f):
    cam(c, 640, 360, 1.1 + 0.2 * ease_io(u / d))
    vgrad(c, "#e9e2d0", "#cfc4ab")
    yr = int(2026 - 40 * ease_io(clamp(u / 1.2)))
    c.save(); c.translate(640, 350); c.rotate(-0.03)
    rrect(c, -190, -210, 380, 420, 14); fill_stroke(c, "#ffffff", 7, "#1a1a1a")
    c.rectangle(-190, -210, 380, 90); c.set_source_rgb(.2, .4, .7); c.fill()
    rrect(c, -190, -210, 380, 420, 14); c.set_source_rgb(*INK); c.set_line_width(7); c.stroke()
    text(c, f"MAY {yr}", 0, -166, 50, color="#ffffff")
    for r in range(5):
        for col in range(7):
            n = r * 7 + col - 2
            if 1 <= n <= 31:
                x, y = -150 + col * 50, -80 + r * 52
                text(c, str(n), x, y, 28, color="#333333")
                if n == 13 and u > 1.3:
                    k = prog(u, 1.3, 1.8); c.new_path(); c.arc_negative(x, y, 24, -0.5, -0.5 - TAU * k) if False else c.arc(x, y, 24, -1.6, -1.6 + TAU * k)
                    c.set_source_rgb(.85, .15, .1); c.set_line_width(5); c.stroke()
    c.restore()

def sh_baby(c, u, d, f):
    cam(c, 640, 380, 1.3 + 0.15 * ease_io(u / d))
    vgrad(c, "#dfeaf2", "#b9cad6")
    c.rectangle(-500, 520, 2500, 400); c.set_source_rgb(.82, .76, .66); c.fill()
    rrect(c, 430, 380, 420, 150, 20); fill_stroke(c, "#f7f1e6", 6, "#1a1a1a")
    for x in range(450, 850, 36): wline(c, [(x, 380), (x, 300)], f, amp=.6, seed=x)
    wline(c, [(430, 300), (850, 300)], f, seed=9)
    for lx in (450, 830): wline(c, [(lx, 530), (lx, 600)], f, seed=lx)
    rk = math.sin(u * 3) * 0.04
    c.save(); c.translate(640, 360); c.rotate(rk)
    c.save(); c.scale(1.5, 1); c.arc(0, 0, 70, 0, TAU); c.restore(); fill_stroke(c, "#ffffff", 5, "#1a1a1a")
    c.arc(-55, -6, 38, 0, TAU); fill_stroke(c, "#f2d6b3", 5, "#1a1a1a")
    for ex in (-66, -46): c.move_to(ex - 5, -8); c.curve_to(ex - 2, -3, ex + 2, -3, ex + 5, -8); c.set_line_width(3); c.set_source_rgb(*INK); c.stroke()
    c.arc(-56, 8, 6, 0.1 * math.pi, 0.9 * math.pi); c.stroke()
    c.restore()
    for i in range(3):
        k = prog(u, 0.3 + i * .2, 0.8 + i * .2)
        if k > 0:
            y = 280 - 160 * k; c.save(); c.translate(560 + i * 80, y); c.scale(.8 * (1 - k * .3), .8 * (1 - k * .3))
            c.move_to(0, 12); c.curve_to(-30, -10, -14, -34, 0, -16); c.curve_to(14, -34, 30, -10, 0, 12); c.close_path()
            c.set_source_rgba(.9, .3, .4, 1 - k * .7); c.fill(); c.restore()
    label(c, "ROBERT DOUGLAS THOMAS", 640, 580, 30, prog(u, 0.6, 1.0), fill="#ffe9a8")

def sh_london(c, u, d, f):
    z = 1.0 + 1.6 * ease_io(prog(u, 1.0, d)); px, py = 470, 420
    cam(c, 640 + (px - 640) * ease_io(prog(u, 1.0, d)), 360 + (py - 360) * ease_io(prog(u, 1.0, d)), z)
    vgrad(c, "#efe7d4", "#ddd2b8")
    rnd = random.Random(5)
    for i in range(30):
        c.arc(rnd.uniform(0, 1280), rnd.uniform(0, 720), rnd.uniform(30, 90), 0, TAU); c.set_source_rgba(.55, .7, .45, .25); c.fill()
    for i in range(40):
        x = rnd.uniform(0, 1280); y = rnd.uniform(0, 720); c.move_to(x, y); c.line_to(x + rnd.uniform(-200, 200), y + rnd.uniform(-120, 120))
        c.set_source_rgba(.4, .35, .3, .25); c.set_line_width(3); c.stroke()
    pts = [(-50, 380), (150, 330), (300, 450), (470, 470), (560, 360), (520, 280), (680, 250), (860, 330), (1000, 300), (1150, 380), (1350, 360)]
    p = ease_io(prog(u, 0.0, 1.0)); n = max(2, int(p * len(pts)))
    c.move_to(*pts[0])
    for i in range(1, n):
        a, b = pts[i - 1], pts[i]; c.curve_to(a[0] + 50, a[1], b[0] - 50, b[1], b[0], b[1])
    c.set_source_rgb(.18, .35, .6); c.set_line_width(22); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    text(c, "LONDON", 760, 160, 64, color="#5a4a3a")
    text(c, "River Thames", 900, 360, 26, color="#2c4f80", rot=0.1)
    k = ease_out_back(prog(u, 0.7, 1.0))
    if k > 0:
        c.save(); c.translate(px, py - 30 * (1 - k)); c.scale(k, k)
        c.move_to(0, 0); c.curve_to(-24, -30, -24, -56, 0, -56); c.curve_to(24, -56, 24, -30, 0, 0); fill_stroke(c, "#d6402f", 4, "#1a1a1a")
        c.arc(0, -38, 8, 0, TAU); c.set_source_rgb(1, 1, 1); c.fill(); c.restore()
        label(c, "BARNES", px, py + 30, 26, prog(u, 0.9, 1.2), fill="#ffffff")

def house(c, x, ground, w, h, col):
    c.rectangle(x, ground - h, w, h); fill_stroke(c, col, 5, "#1a1a1a")
    c.move_to(x - 12, ground - h); c.line_to(x + w / 2, ground - h - 70); c.line_to(x + w + 12, ground - h); c.close_path(); fill_stroke(c, "#6b3b2a", 5, "#1a1a1a")
    for wx in (x + 24, x + w - 64):
        c.rectangle(wx, ground - h + 30, 40, 50); fill_stroke(c, "#fff3c4", 4, "#1a1a1a")
    c.rectangle(x + w / 2 - 20, ground - 80, 40, 80); fill_stroke(c, "#2f4f6f", 4, "#1a1a1a")

def leafy(c, x, ground, h, u, seed=0):
    c.rectangle(x - 9, ground - h * .5, 18, h * .5); c.set_source_rgb(.35, .22, .13); c.fill()
    sw = math.sin(u * 2 + seed) * 6
    for dx, dy, r in ((-40, -.62, 60), (40, -.62, 60), (0, -.85, 70), (0, -.55, 60)):
        c.arc(x + dx + sw, ground + h * dy, r, 0, TAU); c.set_source_rgb(.35, .58, .3); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()

def sh_street(c, u, d, f):
    cam(c, 520 + 260 * ease_io(u / d), 340, 1.15)
    vgrad(c, "#bfe0f2", "#e8f3f8")
    c.rectangle(-500, 520, 3000, 60); c.set_source_rgb(.7, .7, .7); c.fill()
    c.rectangle(-500, 580, 3000, 400); c.set_source_rgb(.3, .5, .7); c.fill()
    for i in range(5):
        y = 610 + i * 30; c.move_to(-500, y)
        for x in range(-500, 2500, 50): c.line_to(x, y + math.sin(x / 50 + u * 2 + i) * 5)
        c.set_source_rgba(1, 1, 1, .25); c.set_line_width(3); c.stroke()
    cols = ["#d9b38c", "#c98f6a", "#e3cfa6", "#b98466", "#d6c2a0", "#c7a27a"]
    for i in range(9): house(c, -100 + i * 190, 520, 160, 200 + (i % 3) * 30, cols[i % len(cols)])
    for i in range(9): leafy(c, -10 + i * 190, 540, 200, u, i)
    c.save(); c.translate(400 + 120 * u, 640); rrect(c, -70, -20, 140, 30, 12); fill_stroke(c, "#ffffff", 4, "#1a1a1a"); c.restore()
    label(c, "SOUTHWEST LONDON", 700, 120, 34, prog(u, 0.2, 0.6))

def sh_mum(c, u, d, f):
    cam(c, 640 - 40 * ease_io(u / d), 360, 1.25)
    vgrad(c, "#f4f1ec", "#d9d3ca")
    c.move_to(800, 140); c.curve_to(820, 420, 820, 560, 820, 600); c.line_to(1180, 600); c.curve_to(1180, 560, 1180, 420, 1160, 140); c.close_path()
    c.set_source_rgb(.85, .88, .92); c.fill()
    suit_figure(c, 990, 590, 0.8)
    for i, ft in enumerate((0.5, 1.3, 2.2)):
        if ft < u < ft + 0.15:
            c.rectangle(-500, -500, 2500, 2000); c.set_source_rgba(1, 1, 1, .6); c.fill()
    c.save(); c.translate(720, 330); rrect(c, -30, -20, 60, 40, 6); fill_stroke(c, "#333333", 4, "#111111")
    c.arc(0, 0, 13, 0, TAU); fill_stroke(c, "#88aacc", 3, "#111111"); c.restore()
    wline(c, [(720, 350), (720, 600)], f, seed=2)
    person(c, 450, 600, 0.36, P_(A_talk, u), f, head="coded", hair="#c99a5b", style="long", t=u, seed=1)
    label(c, "MUM: CLARE", 450, 150, 32, prog(u, 0.2, 0.5), fill="#ffd6e0")
    label(c, "MODELLING AGENCY", 990, 120, 28, prog(u, 0.6, 0.9))

def vintage_car(c, x, y, s, col="#c0392b"):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(-220, -20); c.curve_to(-220, -70, -170, -80, -120, -82); c.curve_to(-80, -150, 60, -150, 100, -84)
    c.curve_to(190, -82, 230, -60, 230, -20); c.close_path(); fill_stroke(c, col, 6, "#141414")
    c.move_to(-60, -86); c.curve_to(-40, -130, 50, -130, 70, -86); c.close_path(); c.set_source_rgb(.75, .88, .95); c.fill()
    c.rectangle(-230, -30, 470, 14); c.set_source_rgb(.85, .85, .85); c.fill()
    for wx in (-140, 150):
        c.arc(wx, -10, 40, 0, TAU); fill_stroke(c, "#1a1a1a", 4); c.arc(wx, -10, 20, 0, TAU); fill_stroke(c, "#eeeeee", 3, "#1a1a1a")
    c.restore()

def sh_dad(c, u, d, f):
    cam(c, 700, 360, 1.15 + 0.2 * ease_io(u / d))
    vgrad(c, "#a9cbe0", "#e3eef4")
    c.rectangle(-500, 560, 2500, 400); c.set_source_rgb(.55, .55, .55); c.fill()
    c.rectangle(-500, 640, 2500, 400); c.set_source_rgb(.25, .45, .65); c.fill()
    c.move_to(900, 560); c.line_to(1500, 560); c.line_to(1480, 640); c.line_to(940, 640); c.close_path(); fill_stroke(c, "#3a4a5a", 5, "#141414")
    c.rectangle(1000, 400, 300, 160); fill_stroke(c, "#a07a4a", 5, "#141414")
    text(c, "FROM: USA", 1150, 470, 34); text(c, "TO: LONDON", 1150, 515, 28)
    k = ease_io(prog(u, 0.2, 1.4)); vintage_car(c, 1150 - 420 * k, 560, 0.7)
    person(c, 380, 590, 0.36, P_(A_point, u, aR1=1.35, aR2=1.4) if u > 1.2 else P_(A_rest, u), f, head="coded", hair="#5a4632", style="short", t=u, seed=2)
    label(c, "DAD: RICHARD", 380, 150, 32, prog(u, 0.2, 0.5), fill="#cfe6ff")
    label(c, "VINTAGE CARS", 760, 260, 28, prog(u, 1.2, 1.5))

def sh_sisters(c, u, d, f):
    if u < 2.1: cam(c, 640, 380 - 20 * ease_io(u / 2.1), 1.2)
    else: cam(c, 820, 430, 2.0, 0.03)
    vgrad(c, "#f6e9d6", "#e2cfb2")
    c.rectangle(-500, 580, 2500, 400); c.set_source_rgb(.62, .5, .38); c.fill()
    person(c, 400, 590, 0.36, P_(A_rest, u), f, head="coded", hair="#7a5230", style="long", t=u, seed=3)
    person(c, 640, 590, 0.33, P_(A_rest, u + 1), f, head="coded", hair="#a57a4a", style="long", t=u, seed=4)
    person(c, 860, 590, 0.24, A_wave(u), f)
    label(c, "ELIZABETH", 400, 200, 28, prog(u, 0.3, 0.6), fill="#ffd6e0")
    label(c, "VICTORIA", 640, 230, 28, prog(u, 0.7, 1.0), fill="#ffd6e0")
    label(c, "LITTLE ROB", 860, 330, 28, prog(u, 1.2, 1.5), fill="#cfe6ff")

def sh_family(c, u, d, f):
    if u < 2.2: cam(c, 640, 360, 1.05 - 0.05 * ease_io(u / 2.2))
    else: cam(c, 960, 330, 1.7)
    vgrad(c, "#bfe0f2", "#e8f3f8")
    c.rectangle(-500, 560, 2500, 400); c.set_source_rgb(.45, .65, .35); c.fill()
    house(c, 300, 560, 360, 300, "#e3cfa6"); leafy(c, 230, 580, 260, u, 1); leafy(c, 740, 580, 240, u, 2)
    for i, (x, hc, st, sc) in enumerate(((330, "#5a4632", "short", .36), (420, "#c99a5b", "long", .35), (500, "#7a5230", "long", .3), (570, "#a57a4a", "long", .28))):
        person(c, x, 620, sc, P_(A_rest, u + i), f, head="coded", hair=hc, style=st, t=u, seed=i)
    person(c, 640, 620, 0.22, P_(A_rest, u), f)
    c.save(); c.translate(960, 300)
    c.arc(0, 0, 150, math.pi, TAU); c.close_path(); fill_stroke(c, "#ffffff", 6, "#1a1a1a")
    for i, col in enumerate(("#3fbf5a", "#f2c94c", "#d6402f")):
        c.move_to(0, 0); c.arc(0, 0, 130, math.pi + i * math.pi / 3, math.pi + (i + 1) * math.pi / 3); c.close_path(); c.set_source_rgba(*hexc(col)[:3], .8); c.fill()
    na = math.pi + 0.18 + 0.05 * math.sin(u * 8)
    wline(c, [(0, 0), (math.cos(na) * 120, math.sin(na) * 120)], f, seed=7); c.arc(0, 0, 10, 0, TAU); c.set_source_rgb(*INK); c.fill()
    text(c, "FAME-O-METER", 0, 40, 30)
    c.restore()
    if u > 2.2: label(c, "NOT EVEN CLOSE", 960, 420, 34, prog(u, 2.4, 2.8), fill="#ffd0c8", rot=0.05)

# shot list: (start, function, grayscale)
SHOTS = [
    (0.0, sh_martini, 0), (T(0) + 2.7, sh_tux, 0), (T(1), sh_six, 0), (T(2), sh_calendar, 0), (T(2) + 1.1, sh_seventh, 0),
    (T(3), sh_maze_top, 0), (T(3) + 2.6, sh_maze_side, 0), (T(4), sh_forest, 0), (T(5), sh_rain, 0),
    (T(6), sh_lighthouse, 1), (T(6) + 1.6, sh_gull, 1), (T(7), sh_road, 0), (T(8), sh_because, 0), (T(9), sh_title, 0),
    (T(10), sh_1986, 0), (T(10) + 2.3, sh_baby, 0), (T(11), sh_london, 0), (T(11) + 2.1, sh_street, 0),
    (T(12), sh_mum, 0), (T(13), sh_dad, 0), (T(14), sh_sisters, 0), (T(15), sh_family, 0),
]


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if sys.argv[1] == "stills":
        stills([s[0] + 0.9 for s in SHOTS], SHOTS, TOTAL, CAPS, prefix=os.path.join(here, "out", "st"))
    else:
        render_all(SHOTS, TOTAL, CAPS, os.path.join(here, "out", "preview.mp4"), outdir=os.path.join(here, "out", "shots"))
