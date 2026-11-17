"""Full episode, timed to the voiceover SRT.
Run from repo root:
  python3 episodes/2026-11-pattinson-bond/full.py stills [from to]   # one still per shot
  python3 episodes/2026-11-pattinson-bond/full.py render             # out/full_video.mp4 (no audio)
"""
import sys, os, re, math, random, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import cairo
from toonkit.core import text, rrect, fill_stroke, hexc, ease_io, prog, clamp, W, H, FPS
from toonkit.rig import wline, INK, A_rest, A_talk, A_wave, A_point, A_shrug, A_shock, A_walk, REST
from toonkit import scene as SC
from toonkit.scene import cam, vgrad, glow, label, stars, suit_figure, P_, lerpP, ease_out_back, stills, render_all
from toonkit.kit import *
from toonkit import kit as K

spec = importlib.util.spec_from_file_location("ep_film", os.path.join(HERE, "film.py"))
F1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(F1)

# ----------------------------------------------------------------------------- captions from SRT
def parse_srt(p):
    blocks = open(p, encoding="utf-8").read().strip().split("\n\n"); out = []
    for b in blocks:
        ln = b.strip().split("\n")
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", ln[1])
        g = [int(x) for x in m.groups()]
        out.append((g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000, g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000, " ".join(ln[2:])))
    return out

SRT = parse_srt(os.path.join(HERE, "voiceover.srt"))
FIX = [  # speech-to-text mistakes -> script spelling
    ("His mother Claire", "His mother, Clare,"), ("modeling", "modelling"), ("little rob", "little Rob"),
    ("Herodian school", "Harrodian School"), ("He taught him so piano", "He taught himself piano"),
    ("his sisters modelling", "his sister's modelling"), ("Tess of the Derbe", "Tess of the d'Urbervilles,"),
    ("Wills, a talent agent", "a talent agent"), ("Nebelongs", "Nibelungs"), ("Sword of Zantin", "Sword of Xanten"),
    ("Ring came a much", "Then came a much"), ("Cedric Degree", "Cedric Diggory"), ("tri-visit tournament", "Triwizard Tournament"),
    ("small spars", "small bars"), ("Catherine Hardwick", "Catherine Hardwicke"), ("Cosmopolus", "Cosmopolis"),
    ("water for elephants, in remember me, in Bellamy", "Water for Elephants, in Remember Me, in Bel Ami"),
    ("the Rover", "The Rover"), ("Mischot", "Michôd"), ("named Ray", "named Rey"), ("maps to the stars", "Maps to the Stars"),
    ("the Lost City of Z", "The Lost City of Z"), ("go to sea", "go to see"), ("Safty Brothers", "Safdie brothers"), ("Safty", "Safdie"),
    ("in the King", "in The King"), ("Timothy Shala", "Timothée Chalamet"), ("came the Lighthouse", "came The Lighthouse"),
    ("this was it by now", "this was it. By now"), ("helps them in character", "helps the main character"),
    ("Twilight Guy", "Twilight guy"), ("When the Batman", "When The Batman"), ("Oscar of Parasite", "Oscar for Parasite"),
    ("print it back", "printed back"), ("Die, my love", "Die My Love"), ("by Lin", "by Lynne"), ("Ramsey", "Ramsay"),
    ("Sukeye", "Suki"), ("came the drama", "came The Drama"), ("engaged couple, Wood.", "engaged couple."),
    ("Tom Holland and Hathaway", "Tom Holland, Anne Hathaway"), ("playing Antinus.", "playing Antinous,"),
    ("The leader of the suitors trying to take over Odysseus's home, in December", "the leader of the suitors trying to take over Odysseus's home. In December"),
    ("appear in Dune.", "appear in Dune:"), ("Part three directed", "Part Three, directed"), ("Amazon's MGM", "Amazon MGM"),
    ("Stephen", "Steven"), ("It takes over from", "He takes over from"), ("Aero 07", "007"), ("license to kill", "licence to kill"),
    ("a half a puff", "a Hufflepuff"), ("was laughed as Batman", "was laughed at as Batman"),
]
CAPS = []
for a, b, t in SRT:
    for x, y in FIX: t = t.replace(x, y)
    CAPS.append((a, b, t))
TOTAL = 732.0   # voiceover is 728.59 s; 3.4 s tail holds the end card (voiceover padded to match)
def C(n): return SRT[n - 1][0]

# ----------------------------------------------------------------------------- shot registry
SHOTS = []; SFX = []

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

# old first-minute shots with live faces: patch the static head the old shots use
_CUR = {"expr": "smile", "u": 0.0}
def _head(c, mask=False):
    K.rob_head(c, _CUR["expr"], _CUR["u"], 0.0, mask)
SC.main_head = _head

def old(t, fn, expr="smile", gray=0, sfx=()):
    def _(c, u, d, f, k):
        _CUR["expr"] = expr; _CUR["u"] = u; fn(c, u, d, f)
    _.__name__ = fn.__name__
    at(t, gray, sfx)(_)

R = rob
def N(c, x, s, u, f, name=None, ground=600, act=A_rest, **kw):
    nt = kw.pop("name_t", prog(u, .2, .5))
    npc(c, x, ground, s, act(u + kw.pop("ph", 0)), f, u=u, name=name, name_t=nt, **kw)

# ============================================================================= 0:00 – 0:51  (first minute)
old(0.0, F1.sh_martini, sfx=[(0.2, "shake"), (1.9, "pour")])
old(2.5, F1.sh_tux, sfx=[(0.8, "swoosh")])
old(C(2), F1.sh_six, sfx=[(0.1 + i * .3, "pop") for i in range(6)])
old(C(2) + 2.15, F1.sh_calendar, sfx=[(0.05, "stamp")])
old(C(2) + 3.1, F1.sh_seventh, expr="smug", sfx=[(0.15, "boom"), (0.6, "pop")])
old(C(3), F1.sh_maze_top, sfx=[(0.3, "pop")])
old(C(3) + 1.75, [(0, "determined"), (1.6, "shock"), (1.95, "dead")] and F1.sh_maze_side, expr=[(0, "determined"), (1.6, "shock"), (1.95, "dead")], sfx=[(1.9, "thud")])
old(C(4) - 0.25, F1.sh_forest, expr="dreamy", sfx=[(0.1, "sparkle")])
old(C(4) + 1.6, F1.sh_rain, expr="determined", sfx=[(0, "rain")])
old(C(4) + 3.5, F1.sh_lighthouse, gray=1, sfx=[(0.6, "thunder")])
old(C(5) - 0.05, F1.sh_gull, expr="mad", gray=1, sfx=[(0.3, "squawk")])
old(C(6), F1.sh_road)
old(C(7), F1.sh_because, expr="smug", sfx=[(0.6, "pop")])
old(C(8), F1.sh_title, sfx=[(0.0, "type")], )
old(C(8) + 3.75, F1.sh_1986, sfx=[(1.3, "pop")])
old(C(9) + 1.3, F1.sh_baby, sfx=[(0.3, "heart")])
old(C(9) + 3.3, F1.sh_london, sfx=[(0.7, "pop")])
old(C(9) + 5.3, F1.sh_street)
old(C(11), F1.sh_mum, sfx=[(0.5, "shutter"), (1.3, "shutter"), (2.2, "shutter")])
old(C(12), F1.sh_dad, sfx=[(0.3, "car")])
old(C(13), F1.sh_sisters, expr="happy", sfx=[(0.3, "pop"), (0.7, "pop"), (1.2, "pop")])
old(C(13) + 3.4, F1.sh_family, sfx=[(2.4, "pop")])

# ============================================================================= childhood
@at(C(15), sfx=[(0.4, "pop"), (0.9, "pop"), (1.4, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_street(c, u, f)
    for i, (x, hair, st, guess) in enumerate(((260, "#5a4632", "short", "DENTIST?"), (560, "#c99a5b", "long", "ACCOUNTANT?"), (860, "#1a1a1a", "short", "PLUMBER?"))):
        N(c, x, .36, u, f, hair=hair, style=st, seed=i, ph=i)
        label(c, guess, x, 140, 30, prog(u, .3 + i * .5, .6 + i * .5))
    R(c, 1100, 600, .26, A_rest(u), f, u, expr="neutral")

@at(C(15) + 2.4, sfx=[(0.5, "stamp")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 330, 1.25), mv="push", seed=k)
    bg_street(c, u, f)
    for i, x in enumerate((300, 640, 980)):
        N(c, x, .4, u, f, hair=("#5a4632", "#c99a5b", "#1a1a1a")[i], style=("short", "long", "short")[i], seed=i,
          act=lambda v: P_(A_shrug, v))
    label(c, "MOVIE STAR?", 640, 120, 48, prog(u, .1, .4), fill="#f2c94c")
    stamp(c, 640, 250, .8, u, "NOPE", t0=0.5)

@at(C(17), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 340, 1.0), mv="push", seed=k)
    bg_school(c, u, f)
    label(c, "THE HARRODIAN SCHOOL", 640, 40, 38, prog(u, .2, .5))
    R(c, 400, 640, .24, A_walk(u), f, u, enter="left", expr="neutral")

@at(C(17) + 2.6, sfx=[(0.3, "notes")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), (800, 380, 1.6, .02), mv="panL", seed=k)
    bg_classroom(c, u, f)
    N(c, 330, .38, u, f, hair="#bbbbbb", style="short", glasses=True, act=lambda v: P_(A_point, v, aR1=-2.3, aR2=-2.5), facing=1, name="TEACHER")
    c.rectangle(650, 470, 340, 30); fill_stroke(c, "#a07a4a", 5, "#1a1a1a")
    R(c, 820, 640, .3, P_(A_rest, u, tilt=-0.12), f, u, expr="dreamy")
    notes(c, 860, 300, u, 6, seed=1)

@at(C(19), sfx=[(0.2, "notes")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 380, 1.15), mv="push", seed=k)
    bg_room(c, u, f, wall="#3a3f5a", floor="#4a3a2a", night=True)
    piano(c, 760, 600, .9)
    R(c, 520, 610, .36, P_(A_rest, u, aR1=1.1, aR2=1.5 + .15 * math.sin(u * 14), aL1=0.9, aL2=1.4 + .15 * math.sin(u * 13)), f, u, expr="dreamy")
    notes(c, 760, 300, u, 7, seed=3, color=(1, .95, .8))

@at(C(19) + 2.4, sfx=[(0.1, "strum")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.2), mv="dutch", seed=k)
    bg_room(c, u, f, wall="#3a3f5a", floor="#4a3a2a", night=True)
    R(c, 560, 610, .4, P_(A_rest, u, bob=3 * math.sin(u * 8)), f, u, outfit=("guitar",), expr="happy")
    c.save(); c.translate(900, 420); c.rotate(.08); rrect(c, -120, -80, 240, 160, 8); fill_stroke(c, "#fdf6e3", 5, "#1a1a1a")
    text(c, "SONGS", 0, -50, 36); [c.rectangle(-90, -20 + i * 26, 180 * (0.6 + 0.4 * ((i * 7) % 3) / 2), 5) for i in range(4)]; c.set_source_rgb(.3, .3, .5); c.fill(); c.restore()
    notes(c, 560, 260, u, 6, seed=5, color=(1, .95, .8))

@at(C(21), sfx=[(0.4, "door")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_wall(c, u, f, "#d8d0e8", "#b8aed0", "#6a5a7a")
    door(c, 760, 600, .9, u, ease_io(prog(u, .2, 1.0)), sign="MODELLING")
    N(c, 480, .38, u, f, hair="#7a5230", style="long", seed=3, act=lambda v: P_(A_point, v, aR1=1.3, aR2=1.35), name="SISTER")
    R(c, 300, 620, .27, A_rest(u), f, u, expr="surprised")

@at(C(21) + 2.6, sfx=[(0.3, "shutter"), (0.9, "shutter"), (1.6, "shutter"), (2.2, "shutter")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.2), mv="dutch", seed=k)
    vgrad(c, "#f4f1ec", "#d9d3ca")
    c.move_to(320, 120); c.curve_to(330, 420, 330, 560, 330, 620); c.line_to(960, 620); c.curve_to(960, 560, 960, 420, 950, 120); c.close_path(); c.set_source_rgb(.85, .88, .92); c.fill()
    pose = [A_rest, lambda v: P_(A_point, v, aR1=2.4, aR2=-2.6), A_shrug, lambda v: P_(A_rest, v, lean=.12)][int(u * 1.4) % 4]
    R(c, 640, 610, .26, pose(u), f, u, expr=["smile", "smug", "happy", "neutral"][int(u * 1.4) % 4])
    for ft in (0.3, 0.9, 1.6, 2.2):
        if ft < u < ft + .1: c.rectangle(-500, -500, 2500, 2000); c.set_source_rgba(1, 1, 1, .6); c.fill()
    label(c, "AGE 12", 1000, 140, 36, prog(u, .2, .5), fill="#ffd6e0")

@at(C(23), sfx=[(0.3, "slide")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="pull", seed=k)
    bg_paper(c, u, f)
    c.move_to(200, 520); c.line_to(1080, 520); c.move_to(200, 520); c.line_to(200, 140); c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
    pts = [(220, 200), (420, 230), (620, 330), (820, 440), (1060, 500)]
    n = max(2, int(len(pts) * ease_io(prog(u, .1, 2.2))) + 1)
    c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:n]]; c.set_source_rgb(.84, .25, .18); c.set_line_width(9); c.stroke()
    for i, a in enumerate((12, 13, 14, 15)): text(c, f"AGE {a}", 260 + i * 250, 560, 30)
    label(c, "MODELLING JOBS", 640, 100, 38, prog(u, .1, .4))
    R(c, 1120, 620, .22, A_shrug(u), f, u, expr="sad")

@at(C(24), sfx=[(0.2, "boom")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 300, 1.6), mv="push", seed=k)
    bg_wall(c, u, f, "#203040", "#101820", "#1a2028")
    spot(c, 640, a=.22)
    R(c, 640, 600, .4, P_(A_rest, u, tilt=.04), f, u, expr="determined")
    label(c, "AGE 15", 900, 160, 40, prog(u, .3, .6), fill="#f2c94c")

@at(C(25), sfx=[(0.5, "door")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 340, 1.0), mv="panR", seed=k)
    bg_street(c, u, f)
    c.rectangle(380, 230, 520, 330); fill_stroke(c, "#8a4a3a", 7, "#1a1a1a")
    rrect(c, 400, 250, 480, 70, 8); fill_stroke(c, "#fff3c4", 5, "#1a1a1a"); text(c, "BARNES THEATRE COMPANY", 640, 285, 30)
    door(c, 640, 560, .55, u, ease_io(prog(u, .5, 1.1)))
    R(c, 640 - 240 * (1 - ease_io(prog(u, 0, .9))), 620, .2, A_walk(u) if u < .9 else A_rest(u), f, u, expr="smile")

@at(C(25) + 2.4, sfx=[(0.2, "rope")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="rise", seed=k)
    vgrad(c, "#2a2420", "#141010"); c.rectangle(-600, 600, 2600, 600); c.set_source_rgb(.18, .14, .1); c.fill()
    for x in (300, 420, 1050): wline(c, [(x, -200), (x, 600)], f, seed=x)
    rrect(c, 820, 420, 180, 180, 6); fill_stroke(c, "#7a5a3a", 5, "#1a1a1a"); text(c, "PROPS", 910, 510, 34)
    pull = math.sin(u * 4) * .25
    R(c, 520, 610, .38, P_(A_rest, u, aR1=2.6 + pull, aR2=2.9 + pull, aL1=-2.4 - pull, aL2=-2.9 - pull, lean=-.05), f, u, expr="determined")
    label(c, "BACKSTAGE", 640, 80, 40, prog(u, .1, .4), fill="#f2c94c")

@at(C(26) - 0.3, sfx=[(0.1, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_stage(c, u, f)
    spot(c, 640, a=.2)
    R(c, 640, 600, .36, A_wave(u), f, u, expr="happy")
    label(c, "SMALL PARTS", 640, 90, 40, prog(u, .1, .4), fill="#f2c94c")

@at(C(27))
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="pull", seed=k)
    bg_stage(c, u, f)
    spot(c, 450, a=.25); spot(c, 830, a=.25)
    N(c, 450, .38, u, f, hair="#c99a5b", style="long", act=A_talk, seed=1)
    N(c, 830, .38, u, f, hair="#1a1a1a", act=A_wave, seed=2)
    R(c, 1120, 560, .24, A_rest(u), f, u, expr="neutral", shadow=False)
    c.rectangle(1040, 280, 180, 300); c.set_source_rgba(0, 0, 0, .35); c.fill()

@at(C(28), sfx=[(0.3, "tick")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="panL", seed=k)
    bg_wall(c, u, f, "#e8dcc6", "#cdbf a6".replace(" ", ""), "#8a6a4a")
    clock(c, 950, 230, 100, u, 1.0, txt="ON TIME")
    R(c, 480, 610, .38, A_wave(u), f, u, expr="happy", enter="left")

@at(C(28) + 2.3, sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_stage(c, u, f, curtain="#2a4a7a")
    spot(c, 640, a=.25)
    R(c, 640, 600, .36, P_(A_talk, u), f, u, expr="worried", talk=.8, seed=2)
    label(c, "TESS OF THE D'URBERVILLES", 640, 80, 36, prog(u, .1, .4), fill="#ffffff")

@at(C(29), sfx=[(0.6, "ding")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 380, 1.3), mv="push", seed=k)
    vgrad(c, "#1a1216", "#0a0708"); seats(c, 2, 520, u=u, seed=1)
    N(c, 640, .42, u, f, ground=640, hair="#222222", shades=True, outfit=("suit",), act=lambda v: P_(A_point, v, aR1=2.2, aR2=2.6))
    label(c, "TALENT AGENT", 640, 70, 36, prog(u, .1, .4), fill="#f2c94c")
    if u > .6: text(c, "!", 790, 150, 120, color="#f2c94c")

@at(C(30), sfx=[(0.2, "door"), (0.5, "choir")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 340, 1.0), mv="push", seed=k)
    bg_dark(c, u, f)
    door(c, 640, 600, 1.1, u, ease_io(prog(u, .1, .9)), light=(1, .92, .6))
    R(c, 640, 640, .3, A_walk(u), f, u, expr="dreamy", facing=1)

# ============================================================================= first screen jobs
@at(C(31), sfx=[(0.1, "click")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="pull", seed=k)
    bg_dark(c, u, f, "#2a2a30", "#101014")
    rrect(c, 140, 80, 1000, 560, 10); c.set_source_rgb(.9, .88, .82); c.fill()
    for x, y in ((160, 100), (1120, 100), (160, 620), (1120, 620)):
        c.move_to(x, y); c.line_to(x + (40 if x < 640 else -40), y); c.move_to(x, y); c.line_to(x, y + (40 if y < 360 else -40)); c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
    R(c, 1040, 600, .12, A_wave(u), f, u, expr="happy")
    label(c, "TINY", 1040, 380, 30, prog(u, .3, .6), fill="#f2c94c")

@at(C(32), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_room(c, u, f, wall="#e0d4bc", floor="#8a6a4a")
    def inner(c2, uu):
        vgrad(c2, "#5a6a8a", "#2a3040"); c2.rectangle(-300, 40, 600, 300); c2.set_source_rgb(.2, .25, .2); c2.fill()
        c2.move_to(-140, 40); c2.line_to(-140, -60); c2.line_to(-120, -60); c2.line_to(-120, -90); c2.line_to(-90, -60); c2.line_to(-60, -90); c2.line_to(-60, -60); c2.line_to(-40, -60); c2.line_to(-40, 40); c2.close_path(); c2.set_source_rgb(.15, .15, .2); c2.fill()
        c2.save(); c2.translate(60 + 40 * math.sin(uu * 2), -40); c2.move_to(-60, 0); c2.curve_to(0, -50, 40, -40, 80, 0); c2.curve_to(40, 20, 0, 20, -60, 0); c2.set_source_rgb(.3, .5, .25); c2.fill(); c2.restore()
    tv(c, 560, 330, 1.0, inner, u)
    label(c, "2004", 1000, 420, 44, prog(u, .2, .5), fill="#f2c94c")
    label(c, "RING OF THE NIBELUNGS", 560, 70, 34, prog(u, .5, .8))
    label(c, "GERMAN TV", 1000, 500, 30, prog(u, .7, 1.0))

@at(C(33), sfx=[(0.3, "swoosh")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="dutch", seed=k)
    bg_paper(c, u, f)
    flip = clamp((u - .6) / .4)
    c.save(); c.translate(640, 360); c.scale(abs(math.cos(flip * math.pi)) + .02, 1)
    rrect(c, -170, -230, 340, 460, 10); fill_stroke(c, "#2a3a5a" if flip < .5 else "#5a2a2a", 7, "#141414")
    text(c, "RING OF THE" if flip < .5 else "SWORD OF", 0, -40, 40, color="#ffffff"); text(c, "NIBELUNGS" if flip < .5 else "XANTEN", 0, 20, 52, color="#f2c94c")
    c.restore()
    label(c, "SAME FILM, NEW NAME", 640, 640, 32, prog(u, 1.2, 1.5))

@at(C(34), sfx=[(0.1, "thunder")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 330, 1.35), mv="push", seed=k)
    bg_wall(c, u, f, "#7a8090", "#5a6070", "#3a3a40")
    for i in range(3):
        cx = 520 + i * 90 + math.sin(u + i) * 10
        c.arc(cx, 90, 70, 0, TAU); c.set_source_rgb(.35, .38, .45); c.fill()
    rain(c, f, 60, .5)
    R(c, 640, 600, .38, P_(A_rest, u, tilt=.1), f, u, expr="sad")

@at(C(35), sfx=[(0.3, "clap")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="panR", seed=k)
    bg_wall(c, u, f, "#d8d0c0", "#b8ad98", "#6a5a4a")
    clapboard(c, 980, 200, .55, u, "VANITY FAIR", "2004")
    N(c, 520, .38, u, f, hair="#e0c070", style="long", act=A_talk, name="REESE WITHERSPOON", seed=1)
    R(c, 260, 610, .3, A_wave(u), f, u, expr="happy")

@at(C(35) + 2.6, sfx=[(0.4, "scissor"), (1.0, "scissor")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 340, 1.05), mv="push", seed=k)
    bg_paper(c, u, f)
    film_strip(c, 640, 330, 1.0, u, n=6, cut=({0, 2, 4}, .4))
    scissors(c, 640 + 200 * math.sin(u * 2), 200, .9, u)
    label(c, "CUT!", 640, 600, 44, prog(u, .5, .8), fill="#ffd0c8")

@at(C(36) + 0.8, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="pull", seed=k)
    R(c, 0, 0, 0.0001, A_rest(u), f, u) if False else None
    bg_cinema(c, u, f, screen=lambda c2, uu: (tiny_head(c2, 1100, 400, .12) if (uu % 1.4) < .2 else None))
    seats(c, 3, 520, u=u, seed=2)
    label(c, "WHO?", 640, 260, 46, prog(u, .6, .9))

@at(C(37) + 0.4)
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.2), mv="push", seed=k)
    bg_cinema(c, u, f)
    seats(c, 2, 560, u=u, seed=3)
    R(c, 640, 640, .32, P_(A_rest, u, tilt=.08), f, u, expr="sad")

@at(C(38), sfx=[(0.4, "tick")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="panR", seed=k)
    bg_wall(c, u, f, "#e2e2da", "#c4c4b8", "#7a7a72")
    door(c, 1150, 600, .8, u, 0, sign="AUDITIONS")
    for i, x in enumerate((300, 460, 620, 780, 940)):
        if i == 2: R(c, x, 610, .3, A_rest(u + i), f, u, expr="worried")
        else: N(c, x, .3, u, f, ground=610, hair=("#3a2a1a", "#c99a5b", "#1a1a1a", "#a57a4a", "#7a5230")[i], style=("short", "long")[i % 2], seed=i, ph=i)

@at(C(38) + 2.2, sfx=[(0.2, "tick"), (0.6, "tick"), (1.0, "tick"), (1.4, "stamp")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="push", seed=k)
    bg_paper(c, u, f)
    rrect(c, 300, 140, 680, 420, 14); fill_stroke(c, "#2e4a3a", 9, "#6b4a2b")
    text(c, "AUDITIONS", 470, 220, 44, color="#ffffff"); text(c, "BOOKED", 820, 220, 44, color="#ffffff")
    n = int(clamp(u / 1.6) * 14)
    for i in range(n):
        x = 360 + (i % 5) * 26 + (i // 5) * 0; y = 280 + (i // 5) * 70
        c.move_to(x, y); c.line_to(x + (60 if i % 5 == 4 else 0) - (130 if i % 5 == 4 else 0), y + 50) if False else None
        c.move_to(x, y); c.line_to(x, y + 50); c.set_source_rgb(1, 1, 1); c.set_line_width(5); c.stroke()
    if u > 1.4: c.move_to(820, 280); c.line_to(820, 330); c.set_source_rgb(1, 1, 1); c.set_line_width(5); c.stroke()

# ============================================================================= Harry Potter
@at(C(39), sfx=[(0.1, "boom"), (0.6, "magic")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 380, 1.0), mv="push", seed=k)
    bg_dark(c, u, f, "#1a2040", "#080a18", "#0a0c18")
    goblet(c, 640, 520, .9, u)
    label(c, "2005", 300, 130, 44, prog(u, .1, .4), fill="#f2c94c")
    if u > 1.0:
        pk = ease_io(prog(u, 1.0, 1.8)); c.save(); c.translate(640 + 200 * pk, 250 - 120 * pk); c.rotate(pk * 4)
        rrect(c, -40, -25, 80, 50, 4); fill_stroke(c, "#f3e7cf", 3, "#1a1a1a"); c.restore()
    label(c, "GOBLET OF FIRE", 640, 650, 34, prog(u, 2.0, 2.3))

@at(C(40), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (640, 250, 1.8), mv="panR", seed=k)
    bg_dark(c, u, f, "#2a2418", "#120e08", "#1a140c")
    spot(c, 640, a=.25)
    R(c, 640, 600, .4, P_(A_rest, u, tilt=-.05), f, u, outfit=("scarf",), expr="smile")
    label(c, "CEDRIC DIGGORY", 640, 60, 40, prog(u, .2, .5), fill="#f2c94c")
    label(c, "HANDSOME", 330, 260, 32, prog(u, 1.0, 1.3)); label(c, "DECENT", 950, 300, 32, prog(u, 1.5, 1.8))

@at(C(41) - 0.4, sfx=[(0.3, "fanfare")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="rise", seed=k)
    bg_dark(c, u, f, "#2a2418", "#120e08")
    trophy(c, 640, 250, 2.0, u)
    R(c, 400, 600, .34, P_(A_point, u, aR1=2.4, aR2=2.8), f, u, outfit=("scarf",), expr="happy")
    label(c, "TRIWIZARD CHAMPION", 640, 80, 38, prog(u, .2, .5), fill="#f2c94c")
    stars(c, 640, 250, 160, 12, u, seed=4, color=(1, .95, .6))

@at(C(42), sfx=[(0.3, "tick"), (0.8, "tick"), (1.3, "tick")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="push", seed=k)
    bg_paper(c, u, f)
    rrect(c, 380, 120, 520, 460, 10); fill_stroke(c, "#ffffff", 7, "#1a1a1a"); text(c, "CASTING NOTES", 640, 170, 40)
    for i, t in enumerate(("Young", "Unknown", "Likeable")):
        y = 260 + i * 100; rrect(c, 430, y - 25, 50, 50, 6); fill_stroke(c, "#ffffff", 5, "#1a1a1a"); text(c, t, 520, y, 40, align="l")
        if u > .3 + i * .5: c.move_to(438, y); c.line_to(452, y + 16); c.line_to(476, y - 18); c.set_source_rgb(.2, .65, .3); c.set_line_width(8); c.stroke()

@at(C(43), sfx=[(0.2, "pop"), (0.5, "pop"), (0.8, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panL", seed=k)
    bg_paper(c, u, f)
    R(c, 640, 600, .38, A_wave(u), f, u, outfit=("scarf",), expr="happy")
    rating(c, 640, 110, 1.0, 5, u, .2)
    thumbs(c, 330, 360, .9); thumbs(c, 950, 360, .9)

@at(C(43) + 2.2, sfx=[(1.0, "thud"), (1.3, "sad")])
def _(c, u, d, f, k):
    cam(c, 700, 470, 1.6, -.04)
    vgrad(c, "#2b3346", "#151a25"); c.rectangle(-500, 560, 2500, 400); c.set_source_rgb(.2, .26, .14); c.fill()
    F1.hedge_wall(c, -300, 260, 140, 560); F1.hedge_wall(c, 1050, 1600, 140, 560)
    trophy(c, 900, 500, 1.0, u)
    kk = ease_io(prog(u, .8, 1.3))
    R(c, 760, 560, .36, A_shock(u) if kk < .05 else A_rest(u), f, u, outfit=("scarf",), rot=-1.5 * kk, expr="shock" if kk < .5 else "dead", shadow=False)

@at(C(44), sfx=[(0.3, "gasp")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="pull", seed=k)
    bg_cinema(c, u, f, screen=lambda c2, uu: (F1.hedge_wall(c2, 140, 500, 100, 430), F1.hedge_wall(c2, 780, 1140, 100, 430)))
    crowd(c, -100, 1400, 560, rows=3, s=.24, u=u, seed=5)
    label(c, "MILLIONS WATCHING", 640, 470, 38, prog(u, .3, .6), fill="#f2c94c")

@at(C(45), sfx=[(0.2, "ping"), (0.65, "ping"), (1.1, "ping"), (1.55, "ping")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_paper(c, u, f)
    phone(c, 640, 360, 1.0, u, [("#HandsomeHufflepuff", "#fff1b8"), ("who IS he??", "#e8f1ff"), ("that face tho", "#ffe0ea"), ("cedric fan club", "#e8ffe8")], .1)
    hearts_up(c, 640, 600, u, 8)

@at(C(46), sfx=[(0.3, "pop"), (1.2, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_street(c, u, f)
    R(c, 640, 620, .34, A_walk(u * .3), f, u, expr="worried")
    for i, x in enumerate((260, 1000)):
        N(c, x, .34, u, f, ground=620, hair=("#c99a5b", "#1a1a1a")[i], style=("long", "short")[i], seed=i, act=lambda v: P_(A_point, v, aR1=1.4 if i == 0 else -1.4, aR2=1.4 if i == 0 else -1.4))
    label(c, "THAT GUY!", 260, 120, 32, prog(u, .3, .6)); label(c, "WHAT'S HIS NAME?", 1000, 120, 30, prog(u, 1.2, 1.5))

@at(C(46) + 2.2, sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 300, 1.6), mv="push", seed=k)
    bg_paper(c, u, f)
    R(c, 640, 640, .45, A_shrug(u), f, u, expr="worried")
    c.save(); c.translate(820, 420); c.rotate(-.1); rrect(c, -120, -50, 240, 100, 10); fill_stroke(c, "#ffffff", 5, "#1a1a1a"); text(c, "HELLO, I'M", 0, -22, 26, color="#c0392b"); text(c, "???", 0, 20, 46); c.restore()

# ============================================================================= dead end / open mic
@at(C(47), sfx=[(0.3, "boing")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panL", seed=k)
    bg_desert(c, u, f)
    c.save(); c.translate(900, 600); c.rectangle(-10, -330, 20, 330); fill_stroke(c, "#7a5a3a", 4, "#1a1a1a")
    c.rotate(math.pi / 4); rrect(c, -110, -110, 220, 220, 14); c.restore()
    c.save(); c.translate(900, 270); c.rotate(math.pi / 4); rrect(c, -110, -110, 220, 220, 14); fill_stroke(c, "#f2c94c", 6, "#1a1a1a"); c.restore()
    text(c, "DEAD", 900, 250, 44); text(c, "END", 900, 295, 44)
    R(c, 520, 610, .36, A_shrug(u), f, u, expr="smug")

@at(C(48), sfx=[(0.6, "stamp"), (1.3, "stamp"), (2.0, "stamp")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_paper(c, u, f)
    for i, x in enumerate((340, 640, 940)):
        headshot(c, x, 340, 1.0, rot=(-.08, .04, .1)[i])
        stamp(c, x, 340, .55, u, "REJECTED", t0=.6 + i * .7)

@at(C(48) + 2.6, sfx=[(0.3, "sad")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 330, 1.4), mv="push", seed=k)
    bg_wall(c, u, f, "#d0ccc4", "#b0aca4", "#6a6862")
    R(c, 640, 600, .4, P_(A_rest, u, tilt=.12, lean=.04), f, u, expr="sad")
    for i in range(5):
        c.save(); c.translate(380 + i * 130, 560 + (i % 2) * 20); c.rotate(.3 * (i - 2)); rrect(c, -50, -36, 100, 72, 4); fill_stroke(c, "#ffffff", 4, "#1a1a1a"); c.restore()

@at(C(49), sfx=[(0.2, "pop"), (0.7, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="panR", seed=k)
    bg_paper(c, u, f)
    for i, (yr, x) in enumerate((("2007", 400), ("2008", 880))):
        rrect(c, x - 200, 180, 400, 300, 8); fill_stroke(c, "#1a1a1a", 6, "#000000"); c.rectangle(x - 180, 200, 360, 260); c.set_source_rgb(.85, .82, .74); c.fill()
        R(c, x + 140, 450, .09, A_wave(u), f, u, expr="happy", shadow=False)
        label(c, yr, x, 140, 40, prog(u, .2 + i * .5, .5 + i * .5), fill="#f2c94c")
    label(c, "SMALL ROLES", 640, 580, 38, prog(u, 1.2, 1.5))

@at(C(50), sfx=[(0, "pub"), (0.2, "strum")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 380, 1.05), mv="push", seed=k)
    bg_pub(c, u, f)
    rrect(c, 380, 560, 520, 50, 6); fill_stroke(c, "#5a3a20", 5, "#1a1a1a")
    spot(c, 640, a=.18)
    R(c, 640, 570, .36, P_(A_rest, u, bob=3 * math.sin(u * 7)), f, u, outfit=("guitar",), expr="dreamy")
    crowd(c, -100, 1400, 650, rows=1, s=.22, u=u, seed=7, dark=True)
    notes(c, 640, 250, u, 6, seed=2, color=(1, .9, .7))

@at(C(50) + 2.6, sfx=[(0.2, "footsteps")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_street(c, u, f, night=True)
    door(c, 1100, 560, .7, u, 0, sign="CASTING")
    x = 200 + 650 * ease_io(clamp(u / d))
    R(c, x, 620, .32, A_walk(u), f, u, outfit=("guitar",), expr="determined")

# ============================================================================= Twilight
@at(C(52), sfx=[(0.2, "pop"), (1.2, "door")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_wall(c, u, f, "#d8dce4", "#b8bcc6", "#5a5e66")
    label(c, "2008", 300, 120, 44, prog(u, .1, .4), fill="#f2c94c")
    door(c, 760, 600, .9, u, ease_io(prog(u, 1.2, 1.8)), sign="AUDITION")
    R(c, 460, 610, .36, A_walk(u) if u < 1.2 else A_rest(u), f, u, expr="worried")

@at(C(52) + 2.7, sfx=[(0.2, "boom")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="dutch", seed=k)
    bg_forest(c, u, f)
    book(c, 640, 340, 1.1, "TWILIGHT", u, .05)
    label(c, "VAMPIRE NOVEL", 640, 610, 36, prog(u, .6, .9), fill="#cfe3ff")

@at(C(54), sfx=[(0.3, "nervous")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="push", seed=k)
    bg_studio_office(c, u, f)
    for i, x in enumerate((480, 780)):
        N(c, x, .36, u, f, ground=600, hair=("#bbbbbb", "#3a2a1a")[i], outfit=("suit",), glasses=i == 0, seed=i, act=A_shock)
        for j in range(2):
            yy = 140 + ((u * 100 + j * 50 + i * 30) % 80)
            c.save(); c.translate(x + 70 + j * 20, yy); c.move_to(0, -14); c.curve_to(10, 0, 10, 10, 0, 10); c.curve_to(-10, 10, -10, 0, 0, -14); fill_stroke(c, "#8fd3ff", 3, "#1a1a1a"); c.restore()
    label(c, "NERVOUS STUDIO", 640, 60, 36, prog(u, .2, .5))

@at(C(54) + 2.8, sfx=[(0.1, "cash"), (1.3, "ding")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="pull", seed=k)
    bg_paper(c, u, f)
    bills(c, 640, 360, u, 10, seed=3)
    counter(c, 640, 330, 1.0, u, 37000000, .1, 1.2)
    label(c, "MODEST BUDGET", 640, 520, 38, prog(u, 1.3, 1.6))

@at(C(55), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panL", seed=k)
    bg_wall(c, u, f, "#e6dccb", "#c8bca6", "#6a5a4a")
    chair(c, 800, 600, .9, "HARDWICKE", u)
    N(c, 450, .38, u, f, hair="#3a2a1a", style="long", act=A_talk, name="CATHERINE HARDWICKE", seed=4)

@at(C(56), sfx=[(0.3, "pop"), (0.9, "sparkle")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (640, 300, 1.5), mv="push", seed=k)
    bg_wall(c, u, f, "#3a4458", "#202838", "#2a2a34")
    spot(c, 640, a=.2)
    R(c, 470, 600, .38, P_(A_talk, u), f, u, expr="neutral", talk=.6, seed=1, facing=-1)
    N(c, 820, .38, u, f, hair="#5a3a22", style="long", act=A_talk, name="KRISTEN STEWART", seed=6, facing=-1)
    for i in range(5):
        x = 600 + i * 22 + math.sin(u * 5 + i) * 10; y = 260 + math.sin(u * 7 + i * 2) * 30
        c.save(); c.translate(x, y); c.rotate(u * 3 + i); c.move_to(0, -14); c.line_to(4, -4); c.line_to(14, 0); c.line_to(4, 4); c.line_to(0, 14); c.line_to(-4, 4); c.line_to(-14, 0); c.line_to(-4, -4); c.close_path(); c.set_source_rgb(1, .9, .3); c.fill(); c.restore()
    label(c, "CHEMISTRY", 640, 80, 40, prog(u, 1.0, 1.3), fill="#f2c94c")

@at(C(58), sfx=[(0.3, "stamp"), (0.5, "cheer")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 330, 1.35), mv="push", seed=k)
    bg_paper(c, u, f)
    R(c, 640, 620, .4, A_shock(u), f, u, expr="happy")
    stamp(c, 640, 330, 1.0, u, "CAST!", color="#2d8a3e", t0=.3)

@at(C(59), sfx=[(0.1, "stamp")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="dutch", seed=k)
    bg_wall(c, u, f)
    calendar(c, 640, 360, 1.0, "NOVEMBER", "2008", "IN CINEMAS", color="#3a4a6a", u=u)

@at(C(60), sfx=[(0.2, "cash"), (1.4, "ding")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="push", seed=k)
    vgrad(c, "#0d1530", "#05081a")
    globe(c, 640, 330, 200, u)
    bills(c, 640, 330, u, 14, seed=5, spread=900)
    counter(c, 640, 600, .8, u, 400000000, .1, 1.2)

@at(C(61), sfx=[(0.3, "gasp")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 330, 1.3), mv="push", seed=k)
    bg_studio_office(c, u, f)
    for i, x in enumerate((480, 800)):
        N(c, x, .4, u, f, hair=("#bbbbbb", "#3a2a1a")[i], outfit=("suit",), glasses=i == 0, seed=i, act=A_shock)
    label(c, "WHAT?!", 640, 80, 54, prog(u, .3, .6), fill="#f2c94c")

@at(C(62), sfx=[(0.1, "flip")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="push", seed=k)
    bg_paper(c, u, f)
    for i in range(6):
        kk = clamp(u * 3 - i * .3)
        if kk >= 1: continue
        c.save(); c.translate(640, 360); c.rotate(-kk * 1.2); c.translate(kk * 600, -kk * 300)
        rrect(c, -170, -190, 340, 380, 10); fill_stroke(c, "#ffffff", 6, "#1a1a1a"); text(c, f"WEEK {i + 1}", 0, 0, 60); c.restore()
    R(c, 1050, 600, .3, P_(A_shock, u), f, u, expr="shock")

@at(C(63), sfx=[(0.3, "footsteps")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_street(c, u, f)
    R(c, 300 + 300 * ease_io(clamp(u / d)), 620, .34, A_walk(u), f, u, expr="smile")
    label(c, "BEFORE", 640, 80, 40, prog(u, .1, .4))

@at(C(63) + 2.4, sfx=[(0, "crowd"), (0.2, "shutter"), (0.7, "shutter"), (1.2, "shutter")])
def _(c, u, d, f, k):
    sx, sy = shake(u, 4, 0)
    autocam(c, u, d, (640 + sx, 360 + sy, 1.15), mv="push", seed=k)
    bg_street(c, u, f)
    crowd(c, -200, 1500, 520, rows=2, s=.3, u=u, seed=9, phones=True, jump=True)
    R(c, 640, 650, .36, A_shock(u), f, u, expr="shock")
    flashes(c, u, 0, 100, 1280, 500, seed=3)
    label(c, "AFTER", 640, 70, 40, prog(u, .1, .4), fill="#f2c94c")

@at(C(64), sfx=[(0, "crowd")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="pull", seed=k)
    vgrad(c, "#1a2040", "#0a0c1a")
    c.rectangle(240, 40, 800, 540); fill_stroke(c, "#d8cdb8", 7, "#1a1a1a")
    for r in range(4):
        for i in range(6): c.rectangle(280 + i * 125, 70 + r * 100, 70, 70); c.set_source_rgb(*((1, .85, .5) if (r + i) % 3 else (.3, .3, .4))); c.fill()
    text(c, "HOTEL", 640, 30, 50, color="#f2c94c")
    crowd(c, -200, 1500, 600, rows=2, s=.26, u=u, seed=10, signs=["WE ♥ ROB", "MARRY ME", "ROB!!"], jump=True)

@at(C(65), sfx=[(0.1, "pop"), (0.9, "pop"), (1.7, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="panR", seed=k)
    bg_wall(c, u, f, "#e8e0d0", "#d0c4ae", "#8a7a64")
    poster(c, 300, 330, .9, "VAMPIRE!", "rob", u, .1, bg="#3a2a4a")
    lunchbox(c, 650, 430, .8, u, .9)
    magazine(c, 990, 330, .9, "STAR", u, 1.7)

@at(C(65) + 2.4, sfx=[(0.2, "shutter"), (0.6, "shutter")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="dutch", seed=k)
    bg_paper(c, u, f)
    for i in range(8):
        magazine(c, 160 + (i % 4) * 320, 220 + (i // 4) * 300, .62, ["STAR", "TEEN", "HOT", "WOW"][i % 4], u, .05 * i, bg=["#f2c94c", "#ff8fa8", "#8fd3ff", "#b9f28f"][i % 4], rot=(-.1, .06, -.04, .09)[i % 4])
    label(c, "AROUND THE WORLD", 640, 650, 38, prog(u, .6, .9), fill="#f2c94c")

@at(C(66), sfx=[(0.2 + i * .35, "pop") for i in range(5)])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="panR", seed=k)
    bg_forest(c, u, f)
    for i, yr in enumerate(("2008", "2009", "2010", "2011", "2012")):
        kk = pop(u, .2 + i * .35)
        if kk <= .002: continue
        c.save(); c.translate(200 + i * 220, 330); c.scale(kk, kk); reel(c, 0, 0, 80, u); c.restore()
        label(c, yr, 200 + i * 220, 460, 32, prog(u, .3 + i * .35, .6 + i * .35))
    label(c, "5 FILMS", 640, 100, 44, prog(u, 2.0, 2.3), fill="#cfe3ff")

@at(C(66) + 2.6, sfx=[(0.1, "cash"), (1.4, "ding")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    vgrad(c, "#0f1d33", "#06101c")
    bills(c, 640, 360, u, 16, seed=8, spread=1100)
    counter(c, 640, 330, .85, u, 3000000000, .1, 1.4, suffix="+")
    R(c, 1120, 640, .26, A_shock(u), f, u, expr="shock")

@at(C(68), sfx=[(0.3, "fanfare")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="rise", seed=k)
    vgrad(c, "#0d1530", "#05081a")
    globe(c, 640, 640, 250, u)
    R(c, 640, 400, .26, A_wave(u), f, u, expr="smile")
    flashes(c, u, 100, 0, 1180, 300, seed=1, rate=4)

@at(C(69) - 0.6, sfx=[(0.2, "shutter"), (0.5, "shutter")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 260, 1.9), mv="dutch", seed=k)
    bg_dark(c, u, f)
    R(c, 640, 600, .45, P_(A_rest, u, tilt=.08), f, u, outfit=("sweat",), expr="worried")
    flashes(c, u, 200, 0, 1080, 500, seed=6, rate=8)

@at(C(70), sfx=[(0.5, "laugh")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 380, 1.05), mv="push", seed=k)
    bg_tvset(c, u, f)
    N(c, 900, .36, u, f, ground=600, hair="#3a2a1a", outfit=("suit",), act=A_talk, seed=3, name="INTERVIEW")
    R(c, 380, 600, .36, A_talk(u), f, u, expr=[(0, "smug"), (1.0, "laugh")], talk=.5, seed=4)
    mic(c, 640, 420, .7)

@at(C(71) - 1.2, sfx=[(0.3, "pop"), (0.9, "boo")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0)
    c.save(); c.rectangle(0, 0, 640, 720); c.clip(); vgrad(c, "#ffd6e0", "#ffb3c6"); hearts_up(c, 320, 650, u, 8)
    crowd(c, 20, 640, 640, rows=1, s=.3, u=u, seed=11, jump=True); label(c, "CHARMING!", 320, 120, 44, prog(u, .2, .5)); c.restore()
    c.save(); c.rectangle(640, 0, 640, 720); c.clip(); vgrad(c, "#5a2a2a", "#2a1010")
    crowd(c, 660, 1280, 640, rows=1, s=.3, u=u, seed=12, signs=["BOO", "HOW DARE", "RUDE"]); label(c, "BETRAYAL!", 960, 120, 44, prog(u, .8, 1.1), fill="#ffb3b3"); c.restore()
    c.move_to(640, 0); c.line_to(640, 720); c.set_source_rgb(*INK); c.set_line_width(8); c.stroke()

@at(C(72), sfx=[(0.4, "ding")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 330, 1.3), mv="push", seed=k)
    bg_paper(c, u, f)
    bulb(c, 640, 170, .9, ease_io(prog(u, .4, .7)))
    R(c, 640, 640, .36, A_talk(u), f, u, expr="neutral", talk=.6)

@at(C(73), sfx=[(0.3, "slam")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), (640, 260, 1.8), mv="push", seed=k)
    bg_wall(c, u, f, "#2a2030", "#141018", "#1a141e")
    R(c, 640, 600, .36, P_(A_shock, u), f, u, expr="worried")
    box_trap(c, 640, 600, 420, 520, "VAMPIRE", u)

# ============================================================================= indie pivot
@at(C(75), sfx=[(0.3, "pop"), (1.6, "swoosh")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="panL", seed=k)
    bg_desert(c, u, f)
    signpost(c, 640, 600, .9, "BIG MOVIES", "SMALL, WEIRD FILMS", u)
    R(c, 380 + 400 * ease_io(prog(u, 1.6, d)), 620, .3, A_walk(u) if u > 1.6 else A_rest(u), f, u, expr="determined")

@at(C(76), sfx=[(0.2, "footsteps")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="panR", seed=k)
    bg_dark(c, u, f, "#1a1a2a", "#0a0a12")
    marquee(c, 260, 220, .7, "TWILIGHT", u)
    glow(c, 260, 220, 300, (1, .9, .5), .3)
    door(c, 1080, 600, .7, u, .3, light=(.6, .7, 1), sign="ART HOUSE")
    R(c, 450 + 450 * ease_io(clamp(u / d)), 620, .3, A_walk(u), f, u, expr="determined")

@at(C(77), sfx=[(0.2, "pop"), (0.6, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_wall(c, u, f, "#cfd6de", "#aab4c0", "#4a5260")
    label(c, "2012", 300, 120, 44, prog(u, .1, .4), fill="#f2c94c")
    chair(c, 820, 600, .9, "CRONENBERG", u, .3)
    clapboard(c, 380, 360, .55, u, "COSMOPOLIS", "2012", .6)

@at(C(78) - 1.0, sfx=[(0, "engine")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 380, 1.0), (900, 380, 1.7), mv="panR", seed=k)
    bg_city_night(c, u, f, sky=("#1a2030", "#080a10"))
    c.rectangle(-600, 600, 2800, 400); c.set_source_rgb(.15, .15, .17); c.fill()
    for i in range(10): c.rectangle(-600 + i * 300 - (u * 400) % 300, 660, 140, 10); c.set_source_rgb(.9, .9, .7); c.fill()
    limo(c, 640, 640, .9, u)
    label(c, "COLD. STRANGE.", 640, 90, 40, prog(u, .3, .6), fill="#cfe3ff")

@at(C(79), sfx=[(0.3, "gasp")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_wall(c, u, f, "#e6e0d0", "#c8c0aa", "#6a6050")
    for i, x in enumerate((300, 640, 980)):
        N(c, x, .36, u, f, hair=("#bbbbbb", "#3a2a1a", "#c99a5b")[i], style=("short", "short", "long")[i], glasses=True, seed=i, ph=i, act=A_shock)
        c.save(); c.translate(x + 70, 420); rrect(c, -40, -55, 80, 110, 4); fill_stroke(c, "#ffffff", 4, "#1a1a1a"); c.restore()
    label(c, "HE CAN ACT?!", 640, 80, 48, prog(u, .4, .7), fill="#f2c94c")

@at(C(80), sfx=[(0.1, "pop"), (0.8, "pop"), (1.5, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="panR", seed=k)
    bg_wall(c, u, f, "#e8e0d0", "#d0c4ae", "#8a7a64")
    poster(c, 300, 330, .85, "WATER FOR ELEPHANTS", "elephant", u, .1, bg="#c46a2a")
    poster(c, 640, 330, .85, "REMEMBER ME", "rain", u, .8, bg="#3a4a6a")
    poster(c, 980, 330, .85, "BEL AMI", "hat", u, 1.5, bg="#7a2a3a")

@at(C(80) + 2.5, sfx=[(0.1, "pop"), (0.9, "pop"), (1.7, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 300, 1.5), mv="push", seed=k)
    bg_paper(c, u, f)
    i = int(u / .8) % 4
    outfits = [("suit",), ("explorer",), ("toga",), ("tux",)]
    exprs = ["smug", "surprised", "happy", "determined"]
    R(c, 640, 640, .45, A_rest(u), f, u, outfit=outfits[i], expr=exprs[i])
    label(c, "NEW VERSION", 640, 80, 38, prog(u, .1, .4))

@at(C(82), sfx=[(0.4, "rip"), (1.1, "rip")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="dutch", seed=k)
    bg_wall(c, u, f, "#bdb5a5", "#9a927f", "#5a5448")
    for i, x in enumerate((330, 640, 950)):
        poster(c, x, 330, .8, ("FILM A", "FILM B", "FILM C")[i], ("hat", "rain", "desert")[i], u, 0, bg="#6a6a6a", torn=ease_io(prog(u, .4 + i * .7, 1.0 + i * .7)) if i != 1 else 0)
    label(c, "FORGOTTEN", 640, 650, 36, prog(u, 1.0, 1.3))

@at(C(83), sfx=[(0.3, "pop"), (1.2, "heart")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_paper(c, u, f)
    balance(c, 640, 260, .9, "PAY", "DIRECTOR", -.25 * ease_io(prog(u, .5, 1.3)), u)
    R(c, 1130, 640, .26, A_point(u), f, u, facing=-1, expr="smile")

@at(C(83) + 2.7, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="panL", seed=k)
    bg_paper(c, u, f)
    heart(c, 640, 300, 4 + .3 * math.sin(u * 8))
    label(c, "DIRECTORS HE ADMIRED", 640, 560, 38, prog(u, .3, .6))

@at(C(84), sfx=[(0.2, "chalk")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.2), mv="push", seed=k)
    bg_classroom(c, u, f)
    c.rectangle(250, 100, 780, 310); c.set_source_rgb(.18, .29, .23); c.fill()
    text(c, "THE PLAN", 640, 180, 70, color="#ffffff")
    R(c, 1080, 620, .3, P_(A_point, u, aR1=-1.9, aR2=-2.1), f, u, facing=1, expr="smug")

@at(C(85), sfx=[(0.3, "cash"), (1.4, "ding")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (560, 300, 1.6), mv="panR", seed=k)
    bg_wall(c, u, f, "#f0e6d0", "#d8c8a8", "#8a6a4a")
    rrect(c, 760, 80, 340, 90, 10); fill_stroke(c, "#ffffff", 6, "#1a1a1a"); text(c, "CAREER SHOP", 930, 125, 44)
    N(c, 930, .3, u, f, ground=560, hair="#bbbbbb", glasses=True, act=A_rest, seed=7)
    rrect(c, 700, 380, 460, 220, 10); fill_stroke(c, "#a07a4a", 6, "#1a1a1a")
    R(c, 520, 610, .38, P_(A_point, u, aR1=1.3, aR2=1.4), f, u, outfit=("bag",), expr="smug")
    label(c, "TWILIGHT MONEY", 380, 220, 30, prog(u, .3, .6), fill="#d6f5d0")

@at(C(87), sfx=[(0.3, "paper")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="dutch", seed=k)
    bg_paper(c, u, f)
    c.save(); c.translate(640, 360); c.rotate(-.04); rrect(c, -260, -300, 520, 600, 6); fill_stroke(c, "#ffffff", 6, "#1a1a1a")
    text(c, "ROBERT'S CV", 0, -250, 44)
    for i, t in enumerate(("Vampire", "Limousine guy", "Desert drifter", "Jungle explorer", "???")):
        text(c, "• " + t, -200, -160 + i * 70, 38, align="l")
    c.restore()
    label(c, "ODD ON PAPER", 1050, 600, 34, prog(u, .6, .9), fill="#f2c94c")

@at(C(88), sfx=[(0, "wind"), (0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_desert(c, u, f)
    dust(c, u, 40, 1)
    label(c, "THE ROVER · 2014", 640, 70, 40, prog(u, .2, .5), fill="#f2c94c")
    R(c, 640, 620, .38, P_(A_rest, u, lean=-.05, tilt=-.06), f, u, expr="tired")

@at(C(89) - 0.5, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="push", seed=k)
    bg_paper(c, u, f)
    c.save(); c.translate(640, 380); c.scale(1.8, 1.8)
    c.move_to(-170, -40); c.curve_to(-120, -110, -20, -120, 30, -100); c.curve_to(80, -130, 120, -110, 160, -60)
    c.curve_to(190, 10, 170, 70, 110, 100); c.curve_to(40, 130, -40, 110, -100, 80); c.curve_to(-170, 60, -190, 10, -170, -40); c.close_path()
    fill_stroke(c, "#e8b26a", 3, "#1a1a1a"); c.restore()
    map_pin(c, 480, 380, 1.0, u, .4, "OUTBACK")
    label(c, "DAVID MICHÔD", 640, 80, 36, prog(u, .7, 1.0))

@at(C(89) + 1.5, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 280, 1.7), mv="push", seed=k)
    bg_desert(c, u, f); dust(c, u, 30, 2)
    R(c, 640, 620, .45, P_(A_rest, u, tilt=.1), f, u, expr="tired", outfit=("eyebags",))
    label(c, "REY", 900, 140, 44, prog(u, .3, .6), fill="#f2c94c")

@at(C(90), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panL", seed=k)
    bg_hills(c, u, f)
    label(c, "MAPS TO THE STARS", 640, 120, 42, prog(u, .2, .5), fill="#f2c94c")
    label(c, "CRONENBERG AGAIN", 640, 200, 32, prog(u, .7, 1.0))
    R(c, 640, 640, .32, A_wave(u), f, u, expr="smug")

@at(C(91), sfx=[(0, "jungle"), (0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (640, 260, 1.7), mv="panR", seed=k)
    bg_jungle(c, u, f)
    label(c, "THE LOST CITY OF Z · 2016", 640, 70, 38, prog(u, .2, .5), fill="#f2c94c")
    R(c, 640, 620, .38, A_walk(u * .5), f, u, outfit=("explorer",), expr="determined")

@at(C(92) - 0.3, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="push", seed=k)
    bg_jungle(c, u, f)
    chair(c, 640, 600, .9, "JAMES GRAY", u)

@at(C(93), sfx=[(0.6, "cricket")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 380, 1.05), mv="pull", seed=k)
    bg_cinema(c, u, f)
    seats(c, 3, 520, u=u, seed=4, sparse=True)
    label(c, "OLD FANS?", 640, 230, 46, prog(u, .3, .6))

@at(C(94), sfx=[(0.2, "pop"), (0.6, "pop"), (1.0, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_wall(c, u, f, "#e6e0d0", "#c8c0aa", "#6a6050")
    for i, x in enumerate((300, 640, 980)):
        N(c, x, .36, u, f, hair=("#bbbbbb", "#3a2a1a", "#c99a5b")[i], style=("short", "short", "long")[i], glasses=True, seed=i, ph=i, act=A_wave)
    rating(c, 640, 90, .9, 4, u, .2)

@at(C(94) + 2.5, sfx=[(0.3, "sparkle"), (1.0, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 330, 1.35), mv="push", seed=k)
    bg_forest(c, u, f)
    kk = ease_io(prog(u, .6, 1.2))
    if kk < 1: stars(c, 640, 300, 140, int(20 * (1 - kk)), u, seed=7)
    R(c, 640, 620, .4, A_rest(u), f, u, outfit=("explorer",) if u > 1.0 else (), expr="smug" if u > 1.0 else "dreamy")
    label(c, "MORE THAN A VAMPIRE", 640, 80, 38, prog(u, 1.0, 1.3), fill="#cfe3ff")

# ============================================================================= Good Time
@at(C(96), sfx=[(0.2, "boom")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="dutch", seed=k)
    bg_paper(c, u, f)
    signpost(c, 640, 640, 1.0, "BEFORE", "AFTER", u)
    label(c, "TURNING POINT", 640, 70, 50, prog(u, .1, .4), fill="#f2c94c")

@at(C(96) + 2.4, sfx=[(0.2, "neon"), (0.8, "pop"), (1.2, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_nyc(c, u, f)
    label(c, "GOOD TIME · 2017", 640, 70, 42, prog(u, .1, .4), fill="#ff8fd0")
    N(c, 470, .36, u, f, hair="#1a1a1a", glasses=True, seed=1, name="JOSH SAFDIE", act=A_talk)
    N(c, 810, .36, u, f, hair="#2a1a10", cap="#2f4f6f", seed=2, name="BENNY SAFDIE", act=A_talk)

@at(C(98), sfx=[(0, "siren")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="push", seed=k)
    bg_bank(c, u, f, alarm=True)
    R(c, 640, 620, .36, A_shock(u), f, u, outfit=("bag",), expr="shock")
    label(c, "CONNIE", 640, 60, 40, prog(u, .2, .5), fill="#ffffff")

@at(C(98) + 2.4, sfx=[(0, "siren"), (0.2, "footsteps")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_nyc(c, u, f)
    for i in range(6):
        x = (i * 260 - u * 700) % 1600 - 200
        c.rectangle(x, 560, 8, 40); c.set_source_rgb(.4, .4, .5); c.fill()
    R(c, 640, 620, .36, A_walk(u * 1.8), f, u, outfit=("bag", "sweat"), expr="worried")
    c.arc(250, 400, 120, 0, TAU); c.set_source_rgba(.9, .2, .3, .35); c.fill()

@at(C(99), sfx=[(0.2, "tick")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_nyc(c, u, f)
    clock(c, 640, 300, 160, u, 6.0, txt="ONE LONG NIGHT")

@at(C(99) + 2.4, sfx=[(0.1, "siren")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.2), mv="dutch", seed=k)
    bg_nyc(c, u, f)
    R(c, 640, 620, .38, A_walk(u * 2.2), f, u, outfit=("sweat",), expr="shout")
    for i in range(3):
        a = .35 + .25 * math.sin(u * 12 + i * 2)
        glow(c, 200 + i * 450, 200, 260, (1, .1, .1) if i % 2 else (.1, .3, 1), a)

@at(C(100), sfx=[(0.3, "heartbeat")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 230, 2.3), mv="push", seed=k)
    bg_nyc(c, u, f)
    R(c, 640, 620, .45, P_(A_rest, u, tilt=.05), f, u, outfit=("sweat",), expr="worried")
    label(c, "MAGNETIC", 820, 150, 30, prog(u, 1.0, 1.3), fill="#ff8fd0")

@at(C(101), sfx=[(0, "crowd"), (0.3, "shutter"), (0.8, "shutter")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), (640, 260, 1.6), mv="rise", seed=k)
    bg_redcarpet(c, u, f)
    label(c, "CANNES FILM FESTIVAL", 640, 70, 40, prog(u, .1, .4), fill="#f2c94c")
    R(c, 640, 560, .3, A_wave(u), f, u, outfit=("tux",), expr="smile")
    flashes(c, u, 100, 200, 1180, 600, seed=2)

@at(C(102), sfx=[(0.2, "paper"), (0.7, "paper")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_paper(c, u, f)
    newspaper(c, 420, 320, .9, "BEST OF HIS GENERATION", u, .1, rot=-.08, spin=True)
    newspaper(c, 880, 400, .8, "A REVELATION", u, .7, rot=.06, spin=True)

@at(C(103), sfx=[(0.2, "laugh"), (1.6, "gasp")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panL", seed=k)
    bg_room(c, u, f)
    N(c, 450, .38, u, f, hair="#5a4632", seed=4, act=A_shrug if u < 1.6 else A_shock)
    if u < 1.6: label(c, "HA! VAMPIRE!", 450, 80, 34, prog(u, .1, .4))
    newspaper(c, 860, 380, .7, "BEST OF HIS GENERATION", u, 1.4, rot=.05)

@at(C(103) + 2.7, sfx=[(0.3, "paper")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="push", seed=k)
    bg_paper(c, u, f)
    for i in range(6): newspaper(c, 200 + (i % 3) * 440, 220 + (i // 3) * 280, .62, "BEST OF HIS GENERATION", u, .08 * i, rot=(-.08, .05, -.03)[i % 3])

@at(C(104), sfx=[(0.1, "type")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (640, 320, 1.6), mv="push", seed=k)
    bg_room(c, u, f, wall="#dfe6ee", floor="#6a6258")
    laptop(c, 760, 430, .9, u, ["To: Safdie brothers", "Can we work together?", "- Rob"], .2)
    R(c, 340, 620, .36, P_(A_rest, u, aR1=1.0, aR2=1.5 + .1 * math.sin(u * 20)), f, u, expr="determined")

@at(C(105) - 0.6, sfx=[(0.4, "ping")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 300, 1.5), mv="dutch", seed=k)
    bg_room(c, u, f, wall="#dfe6ee", floor="#6a6258")
    R(c, 640, 620, .42, A_point(u), f, u, expr="smug")
    label(c, "SENT", 900, 200, 44, prog(u, .3, .6), fill="#d6f5d0")

@at(C(106), sfx=[(0.1, "swoosh"), (0.4, "footsteps")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="panR", seed=k)
    bg_paper(c, u, f)
    R(c, 300 + 600 * ease_io(clamp(u / d)), 620, .38, A_walk(u * 2), f, u, expr="determined")
    for i in range(4): c.move_to(200 + 600 * ease_io(clamp(u / d)) - i * 40, 380 + i * 40); c.line_to(120 + 600 * ease_io(clamp(u / d)) - i * 40, 380 + i * 40); c.set_source_rgb(*INK); c.set_line_width(5); c.stroke()
    label(c, "GOING AFTER IT", 640, 90, 40, prog(u, .3, .6), fill="#f2c94c")

# ============================================================================= High Life, The King, The Lighthouse
@at(C(108), sfx=[(0.2, "whirr")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_dark(c, u, f, "#2a1a3a", "#0a0614")
    for i, col in enumerate(("#d6402f", "#3f7fd6", "#3fbf5a", "#f2c94c")):
        reel(c, 250 + i * 260, 330, 90, u * (1 + i * .3), col)
    label(c, "STRANGE & AMBITIOUS", 640, 560, 40, prog(u, .3, .6), fill="#f2c94c")

@at(C(109), sfx=[(0, "space"), (0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="panR", seed=k)
    bg_space(c, u, f)
    spaceship(c, 640, 330, .9, u)
    label(c, "HIGH LIFE · 2018", 640, 70, 40, prog(u, .2, .5), fill="#cfe3ff")
    label(c, "CLAIRE DENIS", 640, 600, 34, prog(u, .9, 1.2))

@at(C(110) - 1.4, sfx=[(0, "space")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 330, 1.3), mv="rise", seed=k)
    bg_space(c, u, f)
    R(c, 640, 600 + 20 * math.sin(u * 1.5), .38, P_(A_rest, u, aL1=-1.2, aL2=-1.0, aR1=1.2, aR2=1.0, lL1=-.5, lR1=.5), f, u, rot=.2 * math.sin(u), expr="dreamy", shadow=False)

@at(C(111), sfx=[(0.1, "fanfare")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="push", seed=k)
    bg_throne(c, u, f)
    label(c, "THE KING · 2019", 640, 40, 40, prog(u, .1, .4), fill="#f2c94c")
    N(c, 640, .38, u, f, hair="#3a2a1a", seed=2, outfit=("crown",), name="TIMOTHÉE CHALAMET")

@at(C(111) + 2.4, sfx=[(0.3, "laugh")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 300, 1.45), mv="dutch", seed=k)
    bg_throne(c, u, f)
    R(c, 640, 620, .42, A_talk(u), f, u, outfit=("wig",), expr="smug", talk=.9, seed=3)
    label(c, "THE DAUPHIN", 900, 120, 36, prog(u, .3, .6))

@at(C(112), sfx=[(0.3, "pop"), (1.2, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_throne(c, u, f)
    gauge(c, 380, 330, 1.0, "ACCENT", .97 * ease_io(prog(u, .2, .9)), u, colors=("#3fbf5a", "#f2c94c", "#d6402f"))
    gauge(c, 900, 330, 1.0, "CONFIDENCE", .97 * ease_io(prog(u, 1.0, 1.7)), u, colors=("#3fbf5a", "#f2c94c", "#d6402f"))
    R(c, 640, 640, .26, A_shrug(u), f, u, outfit=("wig",), expr="smug")

@at(C(113), gray=1, sfx=[(0.5, "thunder")])
def _(c, u, d, f, k):
    F1.sh_lighthouse(c, u, d, f)
    label(c, "THE LIGHTHOUSE · 2019", 640, 650, 40, prog(u, .1, .4))

@at(C(114), sfx=[(0.3, "boom")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (640, 250, 1.8), mv="push", seed=k)
    bg_dark(c, u, f)
    spot(c, 640, a=.3)
    R(c, 640, 600, .4, P_(A_rest, u, tilt=-.04), f, u, expr="determined")
    label(c, "IMPOSSIBLE TO IGNORE", 640, 80, 42, prog(u, .6, .9), fill="#f2c94c")

@at(C(115), gray=1, sfx=[(0.3, "projector")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_wall(c, u, f, "#bbbbbb", "#888888", "#444444")
    c.save(); c.translate(520, 360)
    reel(c, -90, -180, 80, u); reel(c, 110, -180, 80, u)
    rrect(c, -170, -100, 340, 200, 16); fill_stroke(c, "#333333", 7, "#111111")
    c.arc(220, 0, 60, 0, TAU); fill_stroke(c, "#222222", 7, "#111111"); c.restore()
    N(c, 980, .36, u, f, hair="#3a3a3a", beard=True, seed=3, name="ROBERT EGGERS", act=A_point)
    label(c, "BLACK & WHITE", 520, 610, 38, prog(u, .8, 1.1))

@at(C(116), gray=0, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="push", seed=k)
    bg_paper(c, u, f)
    c.save(); c.translate(640, 380); c.scale(2.2, 2.2)
    c.move_to(-200, 40); c.curve_to(-150, -40, -60, -60, 0, -30); c.curve_to(60, -60, 140, -40, 200, 0); c.curve_to(120, 30, 40, 60, -20, 70); c.curve_to(-100, 80, -180, 80, -200, 40)
    c.close_path(); fill_stroke(c, "#a8c890", 3, "#1a1a1a"); c.restore()
    map_pin(c, 700, 360, 1.0, u, .3, "NOVA SCOTIA, CANADA")

@at(C(116) + 1.6, gray=1, sfx=[(0, "storm")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="dutch", seed=k)
    bg_sea(c, u, f, storm=True)
    if lightning(c, 400, 0, 1.0, u): c.rectangle(-600, -600, 2600, 2000); c.set_source_rgba(1, 1, 1, .4); c.fill()
    rain(c, f, 180, .5)
    label(c, "CRAMPED. WET.", 640, 90, 40, prog(u, .3, .6))

@at(C(117), gray=1, sfx=[(0.3, "creak")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (520, 260, 1.7), mv="panL", seed=k)
    bg_gray_room(c, u, f)
    R(c, 450, 610, .38, P_(A_rest, u, tilt=.1 * math.sin(u * 3)), f, u, outfit=("swirl",), expr="mad")
    N(c, 850, .38, u, f, hair="#cccccc", beard=True, seed=5, name="WILLEM DAFOE", act=A_shock)
    label(c, "SLOWLY GOING MAD", 640, 660, 34, prog(u, 1.2, 1.5))

@at(C(118), gray=1, sfx=[(0.2, "squawk"), (1.0, "squawk")])
def _(c, u, d, f, k):
    F1.sh_gull(c, u, d, f) if False else None
    sx, sy = shake(u, 3, 0)
    cam(c, 640 + sx, 330, 1.2, .05)
    vgrad(c, "#6b6f75", "#2a2d31"); c.rectangle(-500, 560, 2500, 400); c.set_source_rgb(.3, .3, .3); c.fill()
    R(c, 520, 600, .4, A_talk(u), f, u, expr="shout", talk=1.0)
    F1.gull(c, 820, 430, .9, u)
    label(c, "LONG SPEECHES", 320, 100, 32, prog(u, .3, .6)); label(c, "SEAGULLS", 900, 260, 32, prog(u, .9, 1.2))
    rain(c, f, 80, .35)

@at(C(118) + 2.5, gray=1, sfx=[(0.1, "thunder")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="dutch", seed=k)
    bg_sea(c, u, f, storm=True)
    if lightning(c, 900, 0, 1.0, u, .9): c.rectangle(-600, -600, 2600, 2000); c.set_source_rgba(1, 1, 1, .35); c.fill()
    R(c, 520, 640, .4, P_(A_shock, u), f, u, expr="shout", talk=1.0)
    rain(c, f, 160, .5)
    label(c, "SHOUTING AT THE WEATHER", 640, 80, 36, prog(u, .2, .5))

@at(C(119), sfx=[(0.3, "pop"), (1.4, "cheer")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_paper(c, u, f)
    lvl = 1 - ease_io(prog(u, .1, 1.3))
    rrect(c, 220, 230, 300, 150, 14); fill_stroke(c, "#ffffff", 7, "#1a1a1a"); c.rectangle(520, 280, 24, 50); c.set_source_rgb(*INK); c.fill()
    c.rectangle(235, 245, 270 * lvl, 120); c.set_source_rgb(*((.2, .7, .3) if lvl > .3 else (.85, .2, .15))); c.fill()
    label(c, "EXHAUSTING", 370, 450, 34, prog(u, .3, .6))
    rating(c, 900, 300, 1.0, 5, u, 1.3)
    label(c, "CRITICS LOVED IT", 900, 450, 34, prog(u, 1.5, 1.8), fill="#f2c94c")

# ============================================================================= Tenet
@at(C(120), sfx=[(0.8, "smash")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="push", seed=k)
    bg_wall(c, u, f, "#2a2030", "#141018", "#1a141e")
    R(c, 640, 600, .36, A_shock(u) if u > .8 else A_rest(u), f, u, expr="happy" if u > .8 else "determined")
    box_trap(c, 640, 600, 420, 520, "VAMPIRE", u, brk=.8)

@at(C(121) - 0.8, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_wall(c, u, f, "#dfe6ee", "#c3ccd8", "#5a6270")
    for i, x in enumerate((360, 640, 920)):
        N(c, x, .34, u, f, hair=("#bbbbbb", "#3a2a1a", "#1a1a1a")[i], seed=i, outfit=("suit",), act=lambda v: P_(A_rest, v, aR1=2.6, aR2=-2.2, aL1=-2.6, aL2=2.2), glasses=i == 1)
    label(c, "BIG DIRECTORS NOTICED", 640, 70, 40, prog(u, .3, .6), fill="#f2c94c")

@at(C(122), sfx=[(0.2, "clap")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="dutch", seed=k)
    bg_wall(c, u, f, "#1a2030", "#0a0e18", "#14181e")
    clapboard(c, 420, 300, .7, u, "TENET", "2020")
    chair(c, 900, 600, .85, "NOLAN", u, .5)

@at(C(123), sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (640, 260, 1.7), mv="push", seed=k)
    bg_dark(c, u, f, "#1a2030", "#0a0e18")
    spot(c, 640, a=.2)
    R(c, 640, 600, .4, P_(A_rest, u, aR1=2.1, aR2=2.9), f, u, outfit=("suit", "drink"), expr="smug")
    label(c, "NEIL", 900, 120, 44, prog(u, .2, .5), fill="#f2c94c"); label(c, "CALM. ELEGANT.", 900, 200, 30, prog(u, .8, 1.1))

@at(C(124), sfx=[(0.1, "rewind")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panL", seed=k)
    bg_paper(c, u, f)
    clock(c, 400, 330, 150, -u, 3.0)
    R(c, 900 - 200 * ease_io(clamp(u / d)), 620, .32, A_walk(-u), f, u, facing=1, outfit=("suit",), expr="neutral")
    for i in range(3): c.move_to(1080 + i * 30, 400); c.line_to(1140 + i * 30, 360); c.line_to(1140 + i * 30, 440); c.close_path(); c.set_source_rgba(.8, .2, .2, .7); c.fill()
    label(c, "FORWARDS & BACKWARDS", 640, 620, 36, prog(u, .3, .6))

@at(C(125), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_dark(c, u, f, "#1a2030", "#0a0e18")
    spot(c, 450, a=.3); spot(c, 830, a=.12)
    N(c, 450, .38, u, f, hair="#3a2a1a", seed=2, outfit=("suit",), name="LEAD")
    R(c, 830, 600, .34, P_(A_rest, u), f, u, outfit=("suit",), expr="smile")
    label(c, "SUPPORTING ROLE", 830, 110, 32, prog(u, .5, .8))

@at(C(126) - 1.2, sfx=[(0.3, "pop"), (1.3, "stamp")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (640, 300, 1.5), mv="panR", seed=k)
    bg_paper(c, u, f)
    if u < 1.3: heart(c, 640, 300, 3.0); label(c, "HEARTTHROB", 640, 470, 40, 1.0)
    else:
        stamp(c, 640, 330, 1.0, u, "SERIOUS ACTOR", color="#2d5aa8", t0=1.3)
    R(c, 1100, 640, .28, A_point(u), f, u, facing=-1, outfit=("suit",), expr="smug")

@at(C(127), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="push", seed=k)
    bg_city_night(c, u, f, sky=("#2a3044", "#10121a"))
    marquee(c, 640, 250, .9, "CLOSED", u, color="#7a7a7a")
    label(c, "2020 · PANDEMIC", 640, 70, 40, prog(u, .2, .5), fill="#f2c94c")

@at(C(127) + 2.5, sfx=[(0.5, "cricket")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 380, 1.1), mv="pull", seed=k)
    bg_cinema(c, u, f, screen=lambda c2, uu: (clock(c2, 640, 230, 140, -uu, 3.0)))
    seats(c, 3, 520, u=u, seed=6, sparse=True)
    label(c, "SMALL AUDIENCES", 640, 470, 38, prog(u, .3, .6))

@at(C(128), sfx=[(0.1, "cash"), (1.3, "ding")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="push", seed=k)
    vgrad(c, "#0d1530", "#05081a")
    bills(c, 640, 360, u, 14, seed=9, spread=1000)
    counter(c, 640, 330, .9, u, 300000000, .1, 1.2, suffix="+")

@at(C(128) + 2.8, sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="panL", seed=k)
    bg_city_night(c, u, f, sky=("#2a3044", "#10121a"))
    for i, x in enumerate((240, 640, 1040)): marquee(c, x, 300, .5, "CLOSED", u, color="#7a7a7a")
    label(c, "WHILE CINEMAS WERE CLOSED", 640, 560, 36, prog(u, .2, .5), fill="#f2c94c")

@at(C(129), sfx=[(0.1, "boom")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0 + 1.2 * ease_io(clamp(u / d)))
    bg_black(c, u, f)
    text(c, "?", 640, 380, 260, color="#f2c94c")

# ============================================================================= The Batman
@at(C(130), sfx=[(0.05, "stamp")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="push", seed=k)
    bg_wall(c, u, f)
    calendar(c, 640, 360, 1.0, "MAY", "2019", "ANNOUNCEMENT", color="#3a3a4a", u=u)

@at(C(130) + 1.9, sfx=[(0, "rain"), (0.2, "boom")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 330, 1.05), (640, 250, 1.6, -.03), mv="push", seed=k)
    bg_city_night(c, u, f)
    glow(c, 700, 330, 380, (1, .85, .6), .4)
    R(c, 640, 600, .42, A_rest(u), f, u, mask=True, expr="determined")
    rain(c, f, 140, .45)
    label(c, "THE NEXT BATMAN", 640, 70, 40, prog(u, .4, .7), fill="#ffb3b3")

@at(C(131), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_wall(c, u, f, "#cfd6de", "#aab4c0", "#4a5260")
    rrect(c, 200, 120, 880, 360, 10); fill_stroke(c, "#d8b88a", 7, "#6b4a2b")
    for i in range(4):
        c.save(); c.translate(320 + i * 210, 290); c.rotate((-.06, .05, -.03, .07)[i]); rrect(c, -70, -90, 140, 180, 4); fill_stroke(c, "#ffffff", 4, "#1a1a1a")
        c.arc(0, -20, 40, 0, TAU); c.set_source_rgb(.15, .15, .15); c.fill(); text(c, "?", 0, -18, 50, color="#ffffff"); c.restore()
    label(c, "WANTED: NEW BRUCE WAYNE", 640, 80, 38, prog(u, .2, .5), fill="#f2c94c")
    N(c, 1130, .3, u, f, hair="#3a2a1a", glasses=True, beard=True, seed=8, name="MATT REEVES")

@at(C(132), sfx=[(0, "rain"), (0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="dutch", seed=k)
    bg_city_night(c, u, f)
    magnifier(c, 640, 330, 1.5, -.5 + .1 * math.sin(u * 2))
    rain(c, f, 140, .4)
    label(c, "DETECTIVE STORY", 640, 600, 38, prog(u, .3, .6), fill="#ffb3b3")

@at(C(133), sfx=[(0.2, "ping"), (0.6, "ping"), (1.0, "ping"), (1.4, "ping")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_paper(c, u, f)
    phone(c, 640, 360, 1.0, u, [("NO WAY", "#ffd6d6"), ("the VAMPIRE??", "#ffe9cc"), ("not my Batman", "#ffd6d6"), ("lol sparkles", "#eeeeee")], .1, .4)
    thumbs(c, 300, 380, .9, up=False); thumbs(c, 980, 380, .9, up=False)

@at(C(134), sfx=[(0.2, "sparkle"), (0.6, "laugh")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_forest(c, u, f)
    stars(c, 640, 300, 200, 30, u, seed=2)
    crowd(c, -100, 1400, 650, rows=1, s=.28, u=u, seed=13, signs=["SPARKLY!", "LOL"])

@at(C(135), sfx=[(0.3, "boo")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (640, 300, 1.5), mv="push", seed=k)
    bg_city_night(c, u, f)
    crowd(c, -200, 1500, 560, rows=2, s=.3, u=u, seed=14, signs=["NOT THE TWILIGHT GUY", "NO!", "BOO"])
    label(c, "TWILIGHT GUY CAN'T BE BATMAN", 640, 70, 36, prog(u, .3, .6), fill="#ffb3b3")

@at(C(136), sfx=[(0.6, "click")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 300, 1.5), mv="push", seed=k)
    bg_room(c, u, f, wall="#dfe6ee", floor="#6a6258")
    R(c, 640, 620, .42, P_(A_rest, u, aR1=1.0, aR2=2.2 - 1.0 * ease_io(prog(u, .4, 1.0))), f, u, expr="neutral")
    c.save(); c.translate(780, 400 + 160 * ease_io(prog(u, .4, 1.0))); rrect(c, -22, -38, 44, 76, 8); fill_stroke(c, "#222222", 4, "#000000"); c.restore()

@at(C(137), sfx=[(0.2, "clank"), (0.8, "clank")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="dutch", seed=k)
    bg_wall(c, u, f, "#3a3f4a", "#22262e", "#1a1c22")
    lift = abs(math.sin(u * 4)); s_ = .4
    a2 = 0.25 + 2.3 * lift
    P = P_(A_rest, u, aL1=-0.35, aL2=-a2, aR1=0.35, aR2=a2, bob=4)
    R(c, 640, 600, s_, P, f, u, outfit=("sweat",), expr="determined")
    hy = 600 - (500 - 4) * s_
    for sg in (-1, 1):
        ex = math.sin(sg * .35) * 176; ey = SHOULDER_Y + math.cos(.35) * 176
        hx = ex + math.sin(sg * a2) * 178; hyy = ey + math.cos(a2) * 178
        dumbbell(c, 640 + hx * s_, hy + hyy * s_, .32, rot=math.pi / 2)

@at(C(138), sfx=[(0.2, "clap")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_city_night(c, u, f)
    clapboard(c, 640, 300, .8, u, "THE BATMAN", "2020")
    label(c, "SHOOTING STARTS", 640, 600, 38, prog(u, .5, .8), fill="#ffb3b3")

@at(C(138) + 2.5, sfx=[(0.3, "stamp")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="dutch", seed=k)
    bg_wall(c, u, f)
    calendar(c, 420, 340, .8, "SEPTEMBER", "2020", "", color="#3a3a4a", u=u)
    c.save(); c.translate(900, 340); kk = pop(u, .3); c.scale(kk, kk)
    for i in range(8):
        a = i / 8 * TAU + math.pi / 8; (c.move_to if i == 0 else c.line_to)(math.cos(a) * 150, math.sin(a) * 150)
    c.close_path(); fill_stroke(c, "#d6402f", 8, "#ffffff"); text(c, "STOP", 0, 0, 80, color="#ffffff"); c.restore()

@at(C(139), sfx=[(0.6, "beep")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="push", seed=k)
    bg_room(c, u, f, wall="#e4ece8", floor="#7a8a84")
    test_kit(c, 820, 350, 1.0, u, .5)
    R(c, 420, 620, .38, A_shock(u), f, u, expr=[(0, "neutral"), (.8, "shock")])
    label(c, "POSITIVE", 820, 640, 38, prog(u, 1.0, 1.3), fill="#ffd0c8")

@at(C(140), sfx=[(0.1, "tick")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="push", seed=k)
    bg_paper(c, u, f)
    hourglass(c, 640, 330, 1.1, u)
    label(c, "DELAYED", 640, 620, 44, prog(u, .3, .6), fill="#ffd0c8")

@at(C(141), sfx=[(0, "crowd"), (0.2, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), (640, 270, 1.4), mv="rise", seed=k)
    bg_city_night(c, u, f)
    marquee(c, 640, 230, .9, "THE BATMAN", u)
    crowd(c, -200, 1500, 620, rows=2, s=.26, u=u, seed=15)
    label(c, "MARCH 2022", 640, 420, 40, prog(u, .4, .7), fill="#f2c94c")

@at(C(142) - 0.4, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="panL", seed=k)
    bg_paper(c, u, f)
    for i, x in enumerate((260, 520, 780)):
        c.save(); c.translate(x, 340); c.scale(.6, .6); c.rotate((-.06, .04, -.02)[i]); rrect(c, -150, -220, 300, 440, 6); fill_stroke(c, ("#3a5a9a", "#5a5a5a", "#2a2a2a")[i], 7, "#141414"); text(c, "OLD", 0, 0, 60, color="#ffffff"); c.restore()
    c.save(); c.translate(1060, 340); c.scale(.75, .75); rrect(c, -150, -220, 300, 440, 6); fill_stroke(c, "#6a1a1a", 7, "#141414"); text(c, "NEW", 0, 0, 70, color="#ffffff"); c.restore()
    label(c, "VERY DIFFERENT", 1060, 620, 34, prog(u, .3, .6), fill="#f2c94c")

@at(C(143), gray=0, sfx=[(0, "rain")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (640, 260, 1.6), mv="panR", seed=k)
    bg_city_night(c, u, f)
    glow(c, 640, 330, 380, (1, .85, .6), .35)
    R(c, 640, 600, .4, P_(A_rest, u, tilt=.06), f, u, mask=True, expr="neutral")
    rain(c, f, 160, .45)
    label(c, "LONG. RAINY. QUIET.", 640, 70, 40, prog(u, .3, .6), fill="#ffb3b3")

@at(C(144), sfx=[(0, "rain")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="push", seed=k)
    bg_mansion(c, u, f)
    rain(c, f, 80, .3)
    label(c, "NEVER LEAVES THE HOUSE", 640, 650, 36, prog(u, .3, .6))

@at(C(144) + 2.4, sfx=[(0.2, "yawn")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 270, 1.8), mv="push", seed=k)
    bg_room(c, u, f, wall="#3a3f5a", floor="#2a2a34", night=True)
    R(c, 640, 620, .45, P_(A_rest, u, tilt=.08), f, u, outfit=("eyebags",), expr="tired")
    label(c, "SLEEPLESS", 900, 160, 34, prog(u, .3, .6), fill="#cfe3ff")

@at(C(145), sfx=[(0.1, "cash"), (1.2, "ding")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="pull", seed=k)
    vgrad(c, "#2a0a0e", "#0e0406")
    bills(c, 640, 360, u, 14, seed=11, spread=1000)
    counter(c, 640, 330, .9, u, 770000000, .1, 1.1)

@at(C(146), sfx=[(0.3, "fanfare")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), (640, 200, 1.6), mv="rise", seed=k)
    bg_city_night(c, u, f)
    c.rectangle(520, 420, 240, 180); fill_stroke(c, "#f2c94c", 7, "#1a1a1a"); text(c, "1", 640, 510, 120)
    R(c, 640, 420, .26, A_wave(u), f, u, expr="happy")
    label(c, "LEADING MAN", 640, 640, 40, prog(u, .3, .6), fill="#f2c94c")

@at(C(147) + 0.2, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="dutch", seed=k)
    bg_paper(c, u, f)
    label(c, "ONE OF THE BIGGEST FRANCHISES", 640, 330, 40, prog(u, .1, .4), fill="#f2c94c")
    stars(c, 640, 330, 300, 20, u, seed=12, color=(1, .85, .3))

@at(C(148), gray=1, sfx=[(0.2, "shutter")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="push", seed=k)
    bg_wall(c, u, f, "#f4f1ec", "#d9d3ca", "#8a8a8a")
    R(c, 640, 610, .26, A_rest(u), f, u, expr="neutral")
    label(c, "THE BOY WHOSE MODELLING DRIED UP", 640, 80, 32, prog(u, .2, .5))

@at(C(148) + 2.5, sfx=[(0, "rain"), (0.2, "boom")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 280, 1.7), mv="push", seed=k)
    bg_city_night(c, u, f)
    glow(c, 640, 300, 380, (1, .85, .6), .4)
    R(c, 640, 600, .45, A_rest(u), f, u, mask=True, expr="smug")
    rain(c, f, 140, .4)

# ============================================================================= Mickey 17, Die My Love, private life
@at(C(149), sfx=[(0.2, "engine")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="push", seed=k)
    bg_paper(c, u, f)
    gauge(c, 640, 400, 1.6, "NO SLOWING DOWN", .9 * ease_io(prog(u, .1, 1.2)), u)

@at(C(150), sfx=[(0.2, "clap")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_space(c, u, f)
    clapboard(c, 420, 300, .7, u, "MICKEY 17", "2025")
    N(c, 940, .36, u, f, hair="#3a3a3a", glasses=True, seed=9, name="BONG JOON-HO", act=A_wave)

@at(C(151) - 0.5, sfx=[(0.2, "fanfare")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="push", seed=k)
    bg_dark(c, u, f)
    trophy(c, 640, 300, 3.0, u)
    label(c, "OSCAR WINNER · PARASITE", 640, 600, 36, prog(u, .3, .6), fill="#f2c94c")

@at(C(152), sfx=[(0, "space")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="panR", seed=k)
    bg_space(c, u, f)
    spaceship(c, 420 + 200 * ease_io(clamp(u / d)), 330, .9, u)
    label(c, "DANGEROUS JOB", 640, 620, 38, prog(u, .3, .6), fill="#ffd0c8")

@at(C(152) + 2.3, sfx=[(0.2, "printer"), (1.4, "ding")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_wall(c, u, f, "#d8e2ea", "#b8c4d0", "#5a6470")
    kk = (u * .9) % 1
    printer(c, 640, 600, .9, u, ease_io(kk), count=f"#{14 + int(u * .9)}")

@at(C(153) + 0.6, sfx=[(0.3, "ding")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panL", seed=k)
    bg_wall(c, u, f, "#d8e2ea", "#b8c4d0", "#5a6470")
    for i in range(4): R(c, 260 + i * 250, 620, .26, A_wave(u + i), f, u, expr=("smile", "happy", "surprised", "smug")[i], seed=i)
    label(c, "OVER AND OVER", 640, 70, 40, prog(u, .3, .6), fill="#f2c94c")

@at(C(154), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_paper(c, u, f)
    label(c, "STRANGE", 300, 140, 36, prog(u, .1, .4)); label(c, "FUNNY", 640, 110, 36, prog(u, .5, .8)); label(c, "TENDER", 980, 140, 36, prog(u, .9, 1.2))
    hearts_up(c, 640, 640, u, 5)
    R(c, 640, 620, .36, A_shrug(u), f, u, expr="happy")

@at(C(155) - 1.5, sfx=[(0.3, "pop"), (1.0, "shout")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (640, 300, 1.35), mv="panR", seed=k)
    bg_wall(c, u, f, "#d8e2ea", "#b8c4d0", "#5a6470")
    R(c, 420, 620, .3, P_(A_rest, u, lean=.12, tilt=.2, aL1=-.3, aL2=.6, aR1=.3, aR2=-.6), f, u, expr="worried", seed=1)
    R(c, 860, 620, .42, A_shock(u), f, u, expr="shout", talk=1.0, seed=2)
    label(c, "MEEK", 420, 200, 36, prog(u, .3, .6), fill="#cfe3ff"); label(c, "LOUD", 860, 70, 44, prog(u, .8, 1.1), fill="#ffd0c8")

@at(C(156), sfx=[(0.4, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_paper(c, u, f)
    balance(c, 640, 260, .9, "BUDGET", "BOX OFFICE", .22 * ease_io(prog(u, .3, 1.2)), u)

@at(C(156) + 2.7, sfx=[(0.2, "cheer")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="dutch", seed=k)
    bg_paper(c, u, f)
    newspaper(c, 640, 330, 1.0, "ONE OF HIS BEST", u, .1, spin=True)
    rating(c, 640, 590, .9, 5, u, .5)

@at(C(157), sfx=[(0.3, "pop"), (0.9, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_room(c, u, f, wall="#e6d8c6", floor="#8a6a4a")
    R(c, 420, 620, .36, A_talk(u), f, u, expr="neutral", talk=.5, facing=1)
    N(c, 820, .36, u, f, hair="#d9b36a", style="long", seed=6, name="JENNIFER LAWRENCE", act=A_talk, ground=620)
    label(c, "DIE MY LOVE", 640, 70, 40, prog(u, .9, 1.2), fill="#f2c94c")

@at(C(158) - 2.0, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="push", seed=k)
    bg_wall(c, u, f, "#e6dccb", "#c8bca6", "#6a5a4a")
    chair(c, 640, 600, .9, "LYNNE RAMSAY", u)

@at(C(158) + 0.8, sfx=[(0.3, "baby"), (1.5, "baby")])
def _(c, u, d, f, k):
    sx, sy = shake(u, 2, 0)
    autocam(c, u, d, (640 + sx, 380 + sy, 1.15), mv="dutch", seed=k)
    bg_room(c, u, f, wall="#d6c8b6", floor="#7a5a3a", night=True)
    rrect(c, 520, 420, 240, 110, 16); fill_stroke(c, "#f7f1e6", 5, "#1a1a1a")
    R(c, 300, 620, .36, P_(A_rest, u, aL1=-2.6, aL2=-3.0, aR1=2.6, aR2=3.0, tilt=.1), f, u, outfit=("eyebags",), expr="tired")
    N(c, 980, .36, u, f, hair="#d9b36a", style="long", seed=6, act=A_shock, ground=620)
    text(c, "WAAH!", 640, 360, 50, color="#c0392b", rot=math.sin(u * 20) * .1)
    gauge(c, 640, 170, .7, "STRAIN", .9, u)

@at(C(159), sfx=[(0.2, "click")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="pull", seed=k)
    bg_dark(c, u, f, "#2a2a30", "#101014")
    on = u < .5
    c.save(); c.translate(640, 330); rrect(c, -160, -100, 320, 200, 16); fill_stroke(c, "#333333", 7, "#111111")
    c.arc(220, 0, 70, 0, TAU); fill_stroke(c, "#222222", 7, "#111111"); c.arc(-120, -70, 12, 0, TAU); c.set_source_rgb(*((1, .1, .1) if on else (.3, .3, .3))); c.fill(); c.restore()
    label(c, "OFF CAMERA", 640, 560, 40, prog(u, .6, .9))

@at(C(160), sfx=[(0.3, "heart")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (640, 280, 1.5), mv="push", seed=k)
    bg_street(c, u, f)
    R(c, 500, 620, .38, A_rest(u), f, u, expr="happy")
    N(c, 790, .38, u, f, hair="#e8c070", style="long", seed=7, name="SUKI WATERHOUSE", act=A_rest, ground=620)
    hearts_up(c, 640, 400, u, 6)
    label(c, "TOGETHER SINCE 2018", 640, 660, 34, prog(u, 1.0, 1.3), fill="#ffd6e0")

@at(C(161), sfx=[(0.2, "stamp"), (1.2, "heart")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_wall(c, u, f, "#dfeaf2", "#b9cad6", "#82766a")
    calendar(c, 380, 340, .8, "MARCH", "2024", "A DAUGHTER", color="#d65a8a", u=u)
    c.save(); c.translate(870, 380); c.save(); c.scale(1.5, 1); c.arc(0, 0, 70, 0, TAU); c.restore(); fill_stroke(c, "#ffe0ea", 5, "#1a1a1a")
    c.arc(-55, -6, 38, 0, TAU); fill_stroke(c, "#f2d6b3", 5, "#1a1a1a"); c.restore()
    hearts_up(c, 870, 330, u, 5, color="#ff8fb0")

@at(C(162), sfx=[(0.3, "lock")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_wall(c, u, f, "#cfe0c8", "#a8c4a0", "#5a7a4a")
    c.rectangle(380, 300, 520, 300); fill_stroke(c, "#e3cfa6", 6, "#1a1a1a")
    gate(c, 120, 1160, 600, 260, u)
    label(c, "PRIVATE", 640, 120, 44, prog(u, .3, .6), fill="#ffd0c8")

@at(C(162) + 2.6, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 330, 1.35), mv="dutch", seed=k)
    bg_tvset(c, u, f)
    mic(c, 820, 330, .9, txt="NO COMMENT")
    R(c, 480, 600, .4, P_(A_rest, u, aR1=1.2, aR2=-2.0), f, u, expr="smug")

@at(C(163) + 0.5, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_street(c, u, f)
    crowd(c, -100, 1400, 620, rows=1, s=.3, u=u, seed=16, phones=True)
    label(c, "VERY FAMOUS", 640, 80, 42, prog(u, .3, .6), fill="#f2c94c")

@at(C(164), sfx=[(0.4, "boing")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_forest(c, u, f)
    peek = .5 + .5 * math.sin(u * 2.4)
    c.save(); c.translate(870 + 60 * peek, 0); R(c, 0, 600, .38, A_rest(u), f, u, expr="smug"); c.restore()
    c.rectangle(780, 0, 140, 620); c.set_source_rgb(.16, .11, .08); c.fill()
    qmarks(c, 400, 260, u, 4, seed=3, color="#cfe3ff")
    label(c, "HARD TO FIND", 400, 560, 40, prog(u, .3, .6), fill="#cfe3ff")

@at(C(165), sfx=[(0.2, "strum")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (640, 280, 1.6), mv="panR", seed=k)
    bg_room(c, u, f, wall="#3a3f5a", floor="#4a3a2a", night=True)
    R(c, 640, 620, .4, P_(A_rest, u, bob=3 * math.sin(u * 8)), f, u, outfit=("guitar",), expr="dreamy")
    notes(c, 640, 260, u, 7, seed=8, color=(1, .95, .8))
    label(c, "STILL MAKING MUSIC", 640, 70, 38, prog(u, .3, .6), fill="#f2c94c")

@at(C(166), sfx=[(0.2, "vinyl")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_forest(c, u, f)
    vinyl(c, 640, 320, 190, u, "TWILIGHT SOUNDTRACK: 2 OF HIS SONGS")

@at(C(166) + 2.6, sfx=[(0.2, "notes")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 380, 1.1), mv="panL", seed=k)
    bg_room(c, u, f, wall="#3a3f5a", floor="#4a3a2a", night=True)
    piano(c, 760, 600, .9)
    R(c, 520, 610, .36, P_(A_rest, u, aR1=1.1, aR2=1.5 + .15 * math.sin(u * 14), aL1=0.9, aL2=1.4 + .15 * math.sin(u * 13)), f, u, expr="dreamy")
    notes(c, 760, 300, u, 7, seed=4, color=(1, .95, .8))

# ============================================================================= 2026
@at(C(167), sfx=[(0.2, "pop"), (0.6, "pop"), (1.0, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_paper(c, u, f)
    R(c, 640, 640, .38, P_(A_rest, u, aL1=-2.4, aL2=-2.9 + .3 * math.sin(u * 8), aR1=2.4, aR2=2.9 + .3 * math.sin(u * 8 + 1)), f, u, expr="surprised")
    for i in range(3):
        a = u * 4 + i * TAU / 3; c.save(); c.translate(640 + math.cos(a) * 160, 170 + math.sin(a) * 50); c.scale(.25, .25)
        rrect(c, -190, -60, 380, 230, 10); fill_stroke(c, "#222222", 9, "#0a0a0a"); c.restore()
    label(c, "BUSIEST YEAR: 2026", 640, 600, 38, prog(u, .3, .6), fill="#f2c94c")

@at(C(168), sfx=[(0.2, "bells")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_wall(c, u, f, "#f6e9ee", "#e2cfd8", "#a08a90")
    label(c, "THE DRAMA · APRIL", 640, 60, 40, prog(u, .1, .4), fill="#ffd6e0")
    cake(c, 640, 600, .9)
    R(c, 330, 620, .34, A_rest(u), f, u, outfit=("suit",), expr="happy")
    N(c, 950, .34, u, f, hair="#3a2a1a", style="long", seed=8, name="ZENDAYA", ground=620)

@at(C(168) + 2.6, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="push", seed=k)
    bg_wall(c, u, f, "#f6e9ee", "#e2cfd8", "#a08a90")
    rings(c, 640, 300, 1.6, u)
    label(c, "WEDDING PLANS", 640, 550, 40, prog(u, .3, .6))

@at(C(169), sfx=[(0.5, "crack")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="dutch", seed=k)
    bg_wall(c, u, f, "#e6d0d8", "#c8a8b4", "#7a5a64")
    cake(c, 640, 600, .9, crack=ease_io(prog(u, .5, .9)))
    c.save(); c.translate(940, 260); c.rotate(.1); rrect(c, -110, -70, 220, 140, 6); fill_stroke(c, "#f3e7cf", 5, "#1a1a1a")
    c.move_to(-110, -70); c.line_to(0, 10); c.line_to(110, -70); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke(); text(c, "SECRET", 0, 40, 34, color="#c0392b"); c.restore()
    R(c, 300, 620, .32, A_shock(u), f, u, outfit=("suit",), expr="shock")

@at(C(170), sfx=[(0, "sea"), (0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="panR", seed=k)
    bg_sea(c, u, f)
    ship(c, 640, 470, .9, u)
    label(c, "THE ODYSSEY · JULY", 640, 70, 42, prog(u, .2, .5), fill="#f2c94c")

@at(C(170) + 2.6, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_palace(c, u, f)
    chair(c, 640, 600, .9, "NOLAN", u)
    label(c, "HOMER'S EPIC", 640, 90, 40, prog(u, .3, .6))

@at(C(171), sfx=[(0.2 + i * .3, "pop") for i in range(4)])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_palace(c, u, f)
    for i, (nm, hr, st) in enumerate((("MATT DAMON", "#c9a26a", "short"), ("TOM HOLLAND", "#5a3a22", "short"), ("ANNE HATHAWAY", "#3a2a1a", "long"), ("ZENDAYA", "#2a1a10", "long"))):
        N(c, 220 + i * 280, .3, u, f, hair=hr, style=st, seed=i, outfit=("toga",), name=nm, name_t=1.0, ph=i) if u > .2 + i * .3 else None

@at(C(172) - 1.2, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), (640, 260, 1.6), mv="push", seed=k)
    bg_palace(c, u, f)
    for i, x in enumerate((260, 1020)): N(c, x, .32, u, f, hair=("#3a2a1a", "#7a5230")[i], seed=i + 4, outfit=("toga",), act=A_talk)
    R(c, 640, 620, .4, A_point(u), f, u, outfit=("toga",), expr="smug")
    label(c, "ANTINOUS", 640, 70, 44, prog(u, .2, .5), fill="#f2c94c")

@at(C(172) + 1.6, sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="dutch", seed=k)
    bg_palace(c, u, f)
    crowd(c, -100, 1400, 640, rows=1, s=.3, u=u, seed=17)
    label(c, "LEADER OF THE SUITORS", 640, 80, 40, prog(u, .2, .5), fill="#f2c94c")

@at(C(173) - 0.3, sfx=[(0, "wind"), (0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="panR", seed=k)
    bg_dunes(c, u, f)
    label(c, "DUNE: PART THREE · DECEMBER", 640, 80, 38, prog(u, .3, .6), fill="#ffffff")
    N(c, 980, .32, u, f, hair="#3a3a3a", seed=10, name="DENIS VILLENEUVE", ground=640) if u > 1.5 else None

@at(C(174) + 1.8, sfx=[(0.2, "flip"), (1.4, "stamp")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="push", seed=k)
    bg_city_night(c, u, f)
    yr = 2026 + int(2 * ease_io(clamp(u / 1.2)))
    calendar(c, 640, 340, .9, "THE BATMAN II", str(yr), "PUSHED BACK", color="#3a3a4a", u=u)

# ============================================================================= Bond
@at(C(176), sfx=[(0.1, "stamp"), (0.4, "boom")])
def _(c, u, d, f, k):
    sx, sy = shake(u, 10, 1.5)
    autocam(c, u, d, (640 + sx, 360 + sy, 1.15), mv="push", seed=k)
    bg_wall(c, u, f)
    calendar(c, 640, 360, 1.0, "MONDAY", "16", "NOVEMBER 2026", u=u)

@at(C(176) + 2.7, sfx=[(0.2, "boom")])
def _(c, u, d, f, k):
    sx, sy = shake(u, 8, 0)
    autocam(c, u, d, (640 + sx, 360 + sy, 1.0), mv="pull", seed=k)
    vgrad(c, "#1a1a24", "#08080c")
    crowd(c, -200, 1500, 620, rows=2, s=.3, u=u, seed=18, jump=True)
    label(c, "THE NEWS THAT SHOOK EVERYTHING", 640, 100, 38, prog(u, .2, .5), fill="#f2c94c")

@at(C(177), sfx=[(0.1, "news")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="push", seed=k)
    bg_news(c, u, f)
    R(c, 640, 470, .3, A_rest(u), f, u, outfit=("tux",), expr="smug", shadow=False)
    breaking_bar(c, u, "ROBERT PATTINSON IS THE NEW JAMES BOND", .3)

@at(C(177) + 2.3, sfx=[(0.2, "boom")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 300, 1.5), mv="dutch", seed=k)
    vgrad(c, "#1d1a24", "#08070b"); c.rectangle(-500, 600, 2500, 400); c.set_source_rgb(.12, .1, .14); c.fill()
    spot(c, 640, a=.3)
    R(c, 640, 600, .4, A_rest(u), f, u, outfit=("tux", "drink"), expr="smug")
    label(c, "AMAZON MGM STUDIOS", 640, 80, 36, prog(u, .3, .6))

@at(C(178), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_wall(c, u, f, "#2a2a34", "#16161c", "#1e1e24")
    chair(c, 400, 600, .9, "VILLENEUVE", u)
    book(c, 900, 340, .8, "SCRIPT", u, .6, color="#2a2a2a")
    label(c, "STEVEN KNIGHT", 900, 600, 34, prog(u, 1.0, 1.3))

@at(C(179), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_city_night(c, u, f, sky=("#1a2440", "#0a0e1a"))
    c.rectangle(380, 160, 520, 440); fill_stroke(c, "#d8dce4", 7, "#1a1a1a")
    for r in range(4):
        for i in range(5): c.rectangle(410 + i * 100, 190 + r * 90, 60, 60); c.set_source_rgb(*((1, .9, .6) if (r + i) % 2 else (.3, .35, .45))); c.fill()
    label(c, "FIRST BOND FILM MADE BY AMAZON", 640, 80, 36, prog(u, .3, .6), fill="#f2c94c")

@at(C(180), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="dutch", seed=k)
    bg_wall(c, u, f, "#2a2a34", "#16161c", "#1e1e24")
    c.save(); c.translate(640, 350); c.rotate(-.03); rrect(c, -200, -260, 400, 520, 8); fill_stroke(c, "#111111", 7, "#000000")
    text(c, "TITLE:", 0, -120, 40, color="#bbbbbb"); text(c, "???", 0, -60, 70, color="#f2c94c")
    text(c, "RELEASE:", 0, 60, 40, color="#bbbbbb"); text(c, "???", 0, 120, 70, color="#f2c94c"); c.restore()

@at(C(181), sfx=[(0.3, "pop"), (1.4, "swoosh")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), (760, 300, 1.4), mv="panR", seed=k)
    vgrad(c, "#1d1a24", "#08070b"); c.rectangle(-500, 600, 2500, 400); c.set_source_rgb(.12, .1, .14); c.fill()
    for i in range(6): suit_figure(c, 120 + i * 140, 600, .8)
    label(c, "DANIEL CRAIG · 5 FILMS", 820, 120, 32, prog(u, .3, .6))
    spot(c, 1080, a=.25)
    R(c, 1080, 600, .3, A_wave(u), f, u, outfit=("tux",), expr="smug", enter="right")

@at(C(182), sfx=[(0.2, "type")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="push", seed=k, split=99)
    bg_paper(c, u, f)
    quote_card(c, 640, 330, 980, "He has the timeless soul of 007 and brings a spirit that is completely new.", "Denis Villeneuve", u, .1)

@at(C(183), sfx=[(0.2, "type")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.0), mv="push", seed=k, split=99)
    bg_paper(c, u, f)
    quote_card(c, 640, 300, 980, "To say this role is a dream come true is an understatement.", "Robert Pattinson", u, .1)
    R(c, 1150, 660, .22, A_rest(u), f, u, outfit=("tux",), expr="happy")

# ============================================================================= the idea is not new / ending
@at(C(184), sfx=[(0.1, "rewind")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.15), mv="dutch", seed=k)
    bg_wall(c, u, f)
    yr = int(2026 - 7 * ease_io(clamp(u / 1.2)))
    calendar(c, 640, 360, 1.0, "BACK IN", str(yr), "", color="#3a4a6a", u=u)

@at(C(185), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_wall(c, u, f, "#2a2a34", "#16161c", "#1e1e24")
    N(c, 450, .38, u, f, hair="#bbbbbb", glasses=True, seed=11, name="DANNY BOYLE", act=A_talk)
    label(c, "WAS SET TO DIRECT BOND", 880, 300, 32, prog(u, .9, 1.2))

@at(C(186), sfx=[(0.2, "space"), (1.2, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_cinema(c, u, f, screen=lambda c2, uu: (bg_space(c2, uu, f), spaceship(c2, 640, 230, .6, uu)))
    N(c, 360, .36, u, f, hair="#bbbbbb", glasses=True, seed=11, ground=640, act=A_point)
    def inner(c2): tiny_head(c2, 0, -10, .35); text(c2, "BOND?", 0, 60, 34, color="#c0392b")
    bubble(c, 820, 470, 260, 200, u, 1.2, inner)

@at(C(186) + 2.5, sfx=[(0.3, "ding")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 330, 1.35), mv="push", seed=k)
    bg_paper(c, u, f)
    N(c, 640, .4, u, f, hair="#bbbbbb", glasses=True, seed=11, act=A_point, ground=640)
    label(c, "“PATTINSON SHOULD BE BOND”", 640, 80, 40, prog(u, .2, .5), fill="#f2c94c")

@at(C(187), sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panL", seed=k)
    bg_city_night(c, u, f)
    R(c, 640, 600, .38, A_rest(u), f, u, mask=True, expr="neutral")
    label(c, "JUST NAMED BATMAN", 640, 80, 38, prog(u, .3, .6), fill="#ffb3b3")

@at(C(188) - 1.6, sfx=[(0.3, "sparkle")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_street(c, u, f)
    for i, x in enumerate((300, 640, 980)):
        N(c, x, .32, u, f, hair=("#5a4632", "#c99a5b", "#1a1a1a")[i], style=("short", "long", "short")[i], seed=i, ground=640)
        def inner(c2): tiny_head(c2, 0, 0, .25); stars(c2, 0, 0, 50, 6, u, seed=i)
        bubble(c, x + 60, 190, 170, 140, u, .3 + i * .3, inner, tail=(-40, 90))

@at(C(189), sfx=[(0.3, "boom"), (0.6, "sparkle")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 300, 1.4), mv="push", seed=k)
    vgrad(c, "#1d1a24", "#08070b"); c.rectangle(-500, 600, 2500, 400); c.set_source_rgb(.12, .1, .14); c.fill()
    spot(c, 640, a=.3)
    R(c, 640, 600, .42, A_rest(u), f, u, outfit=("tux",), expr="smug")
    stars(c, 640, 300, 150, 14, u, seed=9)
    label(c, "7 YEARS LATER", 640, 70, 40, prog(u, .2, .5), fill="#f2c94c")

@at(C(189) + 2.5, sfx=[(0.2, "swoosh")])
def _(c, u, d, f, k):
    cam(c, 820, 400, .72 + .04 * ease_io(clamp(u / d)), -.02)
    F1.sh_road.__globals__  # road drawing reused below
    vgrad(c, "#efe7d4", "#ddd2b8")
    c.move_to(*F1.RP[0]); [c.line_to(*q) for q in F1.RP[1:]]
    c.set_source_rgb(*INK); c.set_line_width(46); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
    c.set_source_rgb(.45, .42, .4); c.set_line_width(36); c.stroke()
    for sp, kind in F1.STOPS:
        q = F1.RP[int(sp * (len(F1.RP) - 1))]; F1.icon(c, kind, q[0], q[1] - 70)
    label(c, "THE WHOLE PATH", 820, 120, 44, prog(u, .2, .5), fill="#f2c94c")

# quick montage (callbacks)
@at(C(191), gray=1, sfx=[(0.1, "shutter")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="push", seed=k)
    bg_street(c, u, f)
    R(c, 640, 620, .3, A_wave(u), f, u, expr="smile")
    label(c, "BARNES", 640, 80, 40, 1.0)

@at(C(191) + 2.2, gray=1, sfx=[(0.1, "shutter")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.1), mv="panR", seed=k)
    bg_stage(c, u, f); spot(c, 640, a=.25)
    R(c, 640, 600, .36, A_wave(u), f, u, expr="happy")
    label(c, "THEATRE KID", 640, 80, 40, 1.0)

@at(C(192), gray=1, sfx=[(0.2, "scissor")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 340, 1.05), mv="push", seed=k)
    bg_paper(c, u, f)
    film_strip(c, 640, 330, 1.0, u, n=6, cut=({1, 3}, .2))
    scissors(c, 640, 200, .8, u)

@at(C(192) + 2.2, gray=1, sfx=[(0.6, "thud")])
def _(c, u, d, f, k):
    cam(c, 700, 470, 1.6, -.04)
    vgrad(c, "#2b3346", "#151a25"); c.rectangle(-500, 560, 2500, 400); c.set_source_rgb(.2, .26, .14); c.fill()
    F1.hedge_wall(c, -300, 260, 140, 560); F1.hedge_wall(c, 1050, 1600, 140, 560)
    kk = ease_io(prog(u, .4, .9))
    R(c, 760, 560, .36, A_rest(u), f, u, outfit=("scarf",), rot=-1.5 * kk, expr="dead" if kk > .5 else "shock", shadow=False)

@at(C(193), sfx=[(0.2, "sparkle"), (0.8, "cash")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 330, 1.2), mv="push", seed=k)
    bg_forest(c, u, f)
    R(c, 640, 600, .4, A_rest(u), f, u, expr="dreamy")
    stars(c, 640, 300, 140, 20, u, seed=7)
    bills(c, 640, 330, u, 10, seed=4, spread=900)
    label(c, "BILLIONS", 640, 70, 40, prog(u, .3, .6), fill="#f2c94c")

@at(C(193) + 2.4, sfx=[(0.2, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 300, 1.6), mv="dutch", seed=k)
    bg_forest(c, u, f)
    R(c, 640, 600, .44, P_(A_rest, u, tilt=.1), f, u, expr="worried")
    qmarks(c, 640, 120, u, 3, seed=2, color="#cfe3ff")

@at(C(194), sfx=[(0.1, "whirr")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_dark(c, u, f, "#2a1a3a", "#0a0614")
    for i, (kind, ttl, bg) in enumerate((("desert", "ROVER", "#c46a2a"), ("space", "HIGH LIFE", "#1a1a3a"), ("hat", "LIGHTHOUSE", "#555555"), ("rob", "GOOD TIME", "#7a2a6a"))):
        poster(c, 200 + i * 290, 330, .7, ttl, kind, u, .1 + i * .2, bg=bg)
    label(c, "A DECADE OF HARD FILMS", 640, 640, 38, prog(u, .9, 1.2), fill="#f2c94c")

@at(C(195), sfx=[(0.1, "type"), (1.6, "ping")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_room(c, u, f, wall="#dfe6ee", floor="#6a6258")
    laptop(c, 640, 430, .9, u, ["To: the directors", "I'd like to work with you."], .1)

@at(C(195) + 2.0, sfx=[(0.2, "boo")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="dutch", seed=k)
    bg_city_night(c, u, f)
    crowd(c, -200, 1500, 620, rows=2, s=.3, u=u, seed=14, signs=["NOT BATMAN!", "BOO"])
    rain(c, f, 100, .35)

@at(C(196), sfx=[(0.2, "boom"), (0.5, "fanfare")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 300, 1.3), mv="push", seed=k)
    vgrad(c, "#1d1a24", "#08070b"); c.rectangle(-500, 600, 2500, 400); c.set_source_rgb(.12, .1, .14); c.fill()
    for i in range(6): suit_figure(c, 100 + i * 120, 600, .7)
    spot(c, 960, a=.3)
    R(c, 960, 600, .38, A_rest(u), f, u, outfit=("tux", "drink"), expr="smug")
    label(c, "MOST FAMOUS JOB IN SPY CINEMA", 640, 70, 36, prog(u, .3, .6), fill="#f2c94c")

@at(C(197), sfx=[(0.3, "pop"), (1.6, "chain")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_paper(c, u, f)
    label(c, "FAME", 330, 300, 60, prog(u, .2, .5), fill="#ffd0c8")
    c.move_to(480, 300); c.line_to(780, 300); c.set_source_rgb(*INK); c.set_line_width(10); c.stroke()
    c.move_to(780, 270); c.line_to(830, 300); c.line_to(780, 330); c.close_path(); c.fill()
    label(c, "FREEDOM", 980, 300, 60, prog(u, .9, 1.2), fill="#d6f5d0")
    R(c, 640, 660, .26, A_point(u), f, u, expr="determined")

@at(C(197) + 2.3, sfx=[(0.2, "chain")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 330, 1.3), mv="push", seed=k)
    bg_paper(c, u, f)
    kk = ease_io(prog(u, .4, 1.0))
    for side in (-1, 1):
        c.save(); c.translate(640 + side * (60 + 300 * kk), 320 + 200 * kk * kk); c.rotate(side * kk)
        for j in range(3): c.save(); c.translate(side * j * 50, 0); c.scale(1.4, .8); c.arc(0, 0, 24, 0, TAU); c.restore(); c.set_source_rgb(.5, .5, .55); c.set_line_width(10); c.stroke()
        c.restore()
    R(c, 640, 640, .38, A_shock(u) if u > .4 else A_rest(u), f, u, expr="happy" if u > .4 else "determined")

@at(C(198), sfx=[(0.3, "sparkle")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="push", seed=k)
    bg_forest(c, u, f)
    R(c, 420, 600, .38, P_(A_point, u, aR1=1.3, aR2=1.4), f, u, expr="smile")
    c.save(); c.translate(860, 600); suit_figure(c, 0, 0, .9); c.restore()
    stars(c, 860, 360, 120, 16, u, seed=3)

@at(C(199), sfx=[(0.2, "cash"), (1.2, "whirr")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_paper(c, u, f)
    bills(c, 400, 330, u, 8, seed=6, spread=300)
    c.move_to(560, 330); c.line_to(760, 330); c.set_source_rgb(*INK); c.set_line_width(10); c.stroke()
    c.move_to(760, 300); c.line_to(810, 330); c.line_to(760, 360); c.close_path(); c.fill()
    for i in range(3): reel(c, 920 + (i % 2) * 140, 220 + i * 120, 60, u * (1 + i * .2), ("#d6402f", "#3f7fd6", "#3fbf5a")[i])
    label(c, "VAMPIRE MONEY", 400, 560, 34, prog(u, .2, .5), fill="#d6f5d0"); label(c, "EVERYTHING AFTER", 990, 620, 34, prog(u, 1.0, 1.3))

@at(C(200), sfx=[(0.0, "type")])
def _(c, u, d, f, k):
    cam(c, 640, 360, 1.0 + .05 * u / d)
    bg_black(c, u, f)
    l1 = "The real history of"; l2 = "Robert Pattinson"
    text(c, l1[:int(len(l1) * clamp(u / .8))], 640, 300, 46, color="#bdbdbd")
    n2 = int(len(l2) * clamp((u - .8) / .9))
    if n2: text(c, l2[:n2], 640, 390, 92, color="#ffffff")

@at(C(201), sfx=[(0.3, "stamp"), (0.9, "stamp")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="dutch", seed=k)
    bg_paper(c, u, f)
    label(c, "LUCK", 400, 330, 70, 1.0, fill="#ffffff"); label(c, "LOOKS", 880, 330, 70, 1.0, fill="#ffffff")
    for x, t0 in ((400, .3), (880, .9)):
        if u > t0:
            kk = clamp((u - t0) / .15); c.move_to(x - 130 * kk, 260); c.line_to(x + 130 * kk, 400); c.set_source_rgb(.84, .25, .18); c.set_line_width(14); c.stroke()

@at(C(202), sfx=[(0.3, "pop")])
def _(c, u, d, f, k):
    autocam(c, u, d, (640, 360, 1.05), mv="panR", seed=k)
    bg_paper(c, u, f)
    for i, (kind, x) in enumerate((("maze", 230), ("fang", 440), ("mask", 650), ("light", 860))):
        F1.icon(c, kind, x, 330) if u > .1 + i * .25 else None
    c.save(); c.translate(1080, 330); kk = pop(u, 1.2); c.scale(1.6 * kk, 1.6 * kk); F1.icon(c, "star", 0, 0); c.restore()
    label(c, "THE HARD ROLE, EVERY TIME", 640, 560, 38, prog(u, .5, .8), fill="#f2c94c")

@at(C(202) + 2.6, sfx=[(0.2, "boom"), (0.6, "fanfare")])
def _(c, u, d, f, k):
    e_ = ease_io(clamp(u / (d - 1.0)))
    cam(c, 980 - 340 * e_, 300 + 60 * e_, 1.8 - .8 * e_)
    vgrad(c, "#1d1a24", "#08070b"); c.rectangle(-500, 600, 2500, 400); c.set_source_rgb(.12, .1, .14); c.fill()
    for i in range(6): suit_figure(c, 60 + i * 110, 600, .7)
    spot(c, 980, a=.35); glow(c, 980, 360, 300, (1, .9, .6), .3)
    R(c, 980, 600, .38, A_rest(u), f, u, outfit=("tux", "drink"), expr=[(0, "smug"), (2.5, "happy")])
    c.save(); c.translate(1120, 180); kk = pop(u, .6); c.scale(kk, kk); c.arc(0, 0, 36, 0, TAU); fill_stroke(c, "#f2c94c", 5, "#1a1a1a"); text(c, "7", 0, 2, 46); c.restore()

@at(C(203) + 1.6, sfx=[(0.1, "type")], whoosh=False)
def _(c, u, d, f, k):
    bg_black(c, u, f)
    l = "THE HARDEST ROLE CHOSE HIM"
    text(c, l[:int(len(l) * clamp(u / 1.0))], 640, 360, 56, color="#f2c94c")

SHOTS.sort(key=lambda s: s[0])
SFX.sort()
OUTDIR = os.path.join(HERE, "out", "fshots")

def _work(i):
    SC.render_shot(i, SHOTS, TOTAL, CAPS, outdir=OUTDIR)

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    if sys.argv[1] == "stills":
        a = float(sys.argv[2]) if len(sys.argv) > 2 else 0; b = float(sys.argv[3]) if len(sys.argv) > 3 else TOTAL
        nxt = [s[0] for s in SHOTS[1:]] + [TOTAL]
        ts = [s[0] + min(1.2, (e - s[0]) * .6) for s, e in zip(SHOTS, nxt) if a <= s[0] < b]
        stills(ts, SHOTS, TOTAL, CAPS, prefix=os.path.join(HERE, "out", "fs"))
        print(len(ts), "stills")
    elif sys.argv[1] == "info":
        nxt = [s[0] for s in SHOTS[1:]] + [TOTAL]
        durs = [e - s[0] for s, e in zip(SHOTS, nxt)]
        print(len(SHOTS), "shots; mean", round(sum(durs) / len(durs), 2), "max", round(max(durs), 2), "min", round(min(durs), 2))
        for s, dd in zip(SHOTS, durs):
            if dd > 3.4 or dd < 0.6: print("  ", round(s[0], 2), s[1].__name__, round(dd, 2))
    else:
        import subprocess
        from multiprocessing import get_context
        from concurrent.futures import ProcessPoolExecutor
        os.makedirs(OUTDIR, exist_ok=True)
        todo = [i for i in range(len(SHOTS)) if not os.path.exists(os.path.join(OUTDIR, f"s{i:02d}.mp4"))]
        with ProcessPoolExecutor(max_workers=2, mp_context=get_context("fork")) as ex:
            for n, _ in enumerate(ex.map(_work, todo)):
                if n % 10 == 0: print("shot", n, "/", len(todo), flush=True)
        with open(os.path.join(OUTDIR, "list.txt"), "w") as fh:
            for i in range(len(SHOTS)): fh.write(f"file s{i:02d}.mp4\n")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-i", os.path.join(OUTDIR, "list.txt"), "-c", "copy",
                        os.path.join(HERE, "out", "full_video.mp4")], check=True)
        print("done")
