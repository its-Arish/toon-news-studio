"""Rig test for the trump character: walk, run, talk, point, shrug, shock, wave, face close-up.
Run from repo root:  python3 episodes/2026-11-oil-iran-january/rigtest/rig_test.py [stills|render]
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from toonkit.core import ease_io, prog, clamp, W, H, FPS
from toonkit.rig import A_rest, A_talk, A_wave, A_point, A_shrug, A_shock, A_walk, A_run
from toonkit.scene import cam, label, render_all, stills
from toonkit import kit as K

WHO = "trump"
NAME = "DONALD TRUMP"

def sh_walk(c, u, d, f):
    cam(c, 640, 380, 1.0); K.bg_street(c, u, f)
    x = -150 + 520 * ease_io(u / d)
    K.rob(c, x, 600, 0.42, A_walk(u), f, u, who=WHO, expr="determined", name=NAME, name_t=prog(u, .3, .7))

def sh_run(c, u, d, f):
    cam(c, 640 + 60 * u, 380, 1.05); K.bg_hills(c, u, f)
    K.rob(c, 300 + 330 * u, 600, 0.42, A_run(u), f, u, who=WHO, expr=[(0, "worried"), (1.2, "shock")])

def sh_talk(c, u, d, f):
    cam(c, 640, 300, 1.08 + 0.08 * ease_io(u / d)); K.bg_news(c, u, f)
    K.rob(c, 640, 640, 0.48, A_talk(u), f, u, who=WHO, expr="determined", talk=0.9)
    label(c, "TALKING", 980, 160, 34, prog(u, .2, .5))

def sh_point(c, u, d, f):
    cam(c, 600, 320, 1.02, -0.02); K.bg_room(c, u, f)
    K.rob(c, 520, 600, 0.45, A_point(u), f, u, who=WHO, expr=[(0, "neutral"), (0.8, "angry")], talk=0.5 if u > .8 else 0)

def sh_shrug(c, u, d, f):
    cam(c, 640, 330, 1.0); K.bg_wall(c, u, f)
    K.rob(c, 640, 610, 0.45, A_shrug(u), f, u, who=WHO, expr="smug")

def sh_shock(c, u, d, f):
    sx, sy = K.shake(u, 7, 0.8); cam(c, 640 + sx, 320 + sy, 1.05); K.bg_dark(c, u, f)
    K.rob(c, 640, 620, 0.46, A_shock(u), f, u, who=WHO, expr="shock")

def sh_face(c, u, d, f):
    k = ease_io(u / 0.6)
    cam(c, 640, 360 - 200 * k, 1.0 + 1.3 * k); K.bg_gray_room(c, u, f)
    seq = [(0, "neutral"), (0.7, "surprised"), (1.4, "worried"), (2.1, "happy"), (2.8, "angry"), (3.4, "neutral")]
    K.rob(c, 640, 640, 0.42, A_rest(u), f, u, who=WHO, expr=seq, talk=0.8 if 3.4 < u < 4.2 else 0)

def sh_wave_pair(c, u, d, f):
    cam(c, 640, 340, 0.95); K.bg_studio_office(c, u, f)
    K.rob(c, 420, 600, 0.38, A_wave(u), f, u, who=WHO, expr="smile")
    K.rob(c, 860, 600, 0.38, A_rest(u), f, u, who="rob", expr="happy", facing=-1)   # old character still works

D = [2.6, 2.4, 2.6, 2.5, 2.3, 2.0, 4.4, 2.4]
FNS = [sh_walk, sh_run, sh_talk, sh_point, sh_shrug, sh_shock, sh_face, sh_wave_pair]
SHOTS = []; t = 0
for dd, fn in zip(D, FNS):
    SHOTS.append((t, fn, False)); t += dd
TOTAL = t
CAPS = []

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "render":
        render_all(SHOTS, TOTAL, CAPS, os.path.join(out, "rig_test.mp4"), outdir=os.path.join(out, "shots"))
    else:
        mids = [s[0] + dd * .6 for s, dd in zip(SHOTS, D)] + [SHOTS[6][0] + x for x in (0.9, 1.6, 2.3, 3.0)]
        stills(mids, SHOTS, TOTAL, CAPS, prefix=os.path.join(out, "st"))
