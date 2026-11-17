"""toonkit.scene: camera, lighting, labels, characters (main + coded side characters), captions, frame pipeline."""
import math, random, os, subprocess
import cairo
import numpy as np
from .core import text, rrect, fill_stroke, hexc, ease_io, ease_out_back, prog, clamp, W, H, FPS, grain, vig
from .rig import (wline, limb, hand, HEAD, HEAD_PIVOT, INK, NECK_Y, SHOULDER_Y, UA, FA, TH, SH, FOOT, HIP_H,
                  A_rest, A_talk, A_wave, A_point, A_shrug, A_shock, A_walk, REST)

TAU = 2 * math.pi
_eob = ease_out_back
def ease_out_back(t, s=1.9):
    return max(1e-3, _eob(t, s))

# ------------------------------------------------------------------ helpers
def cam(c, cx, cy, z=1.0, rot=0.0):
    c.translate(W / 2, H / 2); c.rotate(rot); c.scale(z, z); c.translate(-cx, -cy)

def vgrad(c, top, bot, x0=-2000, y0=-2000, w=6000, h=6000):
    g = cairo.LinearGradient(0, 0, 0, 720)
    g.add_color_stop_rgb(0, *hexc(top)[:3]); g.add_color_stop_rgb(1, *hexc(bot)[:3])
    c.rectangle(x0, y0, w, h); c.set_source(g); c.fill()

def glow(c, x, y, r, rgb, a):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *rgb, a); g.add_color_stop_rgba(1, *rgb, 0)
    c.arc(x, y, r, 0, TAU); c.set_source(g); c.fill()

def label(c, s, x, y, size=30, t=1.0, rot=-0.03, fill="#ffffff", ink="#1a1a1a"):
    if t <= 0: return
    k = ease_out_back(t)
    c.select_font_face("Patrick Hand"); c.set_font_size(size); e = c.text_extents(s)
    dx, dy = c.user_to_device(x, y); sc = math.hypot(*c.user_to_device_distance(1, 0))
    hw = (e.width / 2 + 22) * sc; hh = size * 0.7 * sc
    ndx = min(max(dx, hw + 8), W - hw - 8) if hw * 2 < W - 16 else dx
    ndy = min(max(dy, hh + 8), H - 112 - hh)
    if (ndx, ndy) != (dx, dy): x, y = c.device_to_user(ndx, ndy)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(k, k)
    rrect(c, -e.width / 2 - 16, -size * 0.62, e.width + 32, size * 1.24, 6); fill_stroke(c, fill, 3.5, ink)
    text(c, s, 0, 0, size, color=ink); c.restore()

def stars(c, x, y, r, n, t, seed=0, color=(1, 1, 1)):
    rnd = random.Random(seed)
    for i in range(n):
        a = rnd.random() * TAU; d = rnd.random() * r
        tw = 0.5 + 0.5 * math.sin(t * (4 + rnd.random() * 4) + i)
        s = 4 + 10 * tw
        px, py = x + math.cos(a) * d, y + math.sin(a) * d * 1.5
        c.save(); c.translate(px, py); c.rotate(t * 0.5 + i)
        c.move_to(0, -s); c.line_to(s * .25, -s * .25); c.line_to(s, 0); c.line_to(s * .25, s * .25)
        c.line_to(0, s); c.line_to(-s * .25, s * .25); c.line_to(-s, 0); c.line_to(-s * .25, -s * .25); c.close_path()
        c.set_source_rgba(*color, 0.4 + 0.6 * tw); c.fill(); c.restore()

# ------------------------------------------------------------------ characters
def body(c, P, frame):
    for side, (k1, k2) in (("L", ("lL1", "lL2")), ("R", ("lR1", "lR2"))):
        ankle, _ = limb(c, (0, 0), P[k1], P[k2], TH, SH, frame, seed=10 if side == "L" else 20)
        ff = (-1 if side == "L" else 1, 0.3); fs = (1, 0.12)
        fx = (ff[0] * (1 - P["feet"]) + fs[0] * P["feet"], ff[1] * (1 - P["feet"]) + fs[1] * P["feet"])
        n = math.hypot(*fx)
        wline(c, [ankle, (ankle[0] + fx[0] / n * FOOT, ankle[1] + fx[1] / n * FOOT)], frame, seed=30 if side == "L" else 40)
    c.rotate(P["lean"])
    wline(c, [(0, 0), (0, NECK_Y + 6)], frame, seed=50)
    for side, (k1, k2) in (("L", ("aL1", "aL2")), ("R", ("aR1", "aR2"))):
        w, a = limb(c, (0, SHOULDER_Y), P[k1], P[k2], UA, FA, frame, seed=60 if side == "L" else 70)
        hand(c, w, a, frame, seed=80 if side == "L" else 90)

def main_head(c, mask=False):
    c.set_source_surface(HEAD, -HEAD_PIVOT[0], -HEAD_PIVOT[1]); c.get_source().set_filter(cairo.FILTER_BEST); c.paint()
    if mask:   # plain black domino mask over the eyes
        c.save(); c.translate(18, -137)
        c.new_path(); c.move_to(-95, -8)
        c.curve_to(-70, -40, 100, -42, 118, -6); c.curve_to(110, 24, 40, 30, 12, 14)
        c.curve_to(-10, 30, -80, 26, -95, -8); c.close_path(); fill_stroke(c, "#111111", 4, "#000000")
        for ex in (-40, 42):
            c.save(); c.translate(ex, -4); c.scale(1.6, 0.6); c.arc(0, 0, 11, 0, TAU); c.restore()
            c.set_source_rgb(.95, .95, .95); c.fill()
        c.restore()

def coded_head(c, frame, skin="#f2d6b3", hair="#6b4a2b", style="short", t=0.0, seed=0, face=True, scale=1.4):
    c.save(); c.scale(scale, scale)
    cy = -96; R = 104
    if style == "long":
        rrect(c, -R - 6, cy - 40, 2 * R + 12, 200, 40); fill_stroke(c, hair, 5, "#141414")
    c.arc(0, cy, R, 0, TAU); fill_stroke(c, skin, 6, "#141414")
    c.save(); c.arc(0, cy, R, 0, TAU); c.clip()
    c.new_path(); c.arc(0, cy - 70, R * 0.95, 0, TAU); c.set_source_rgb(*hexc(hair)[:3]); c.fill()
    if style == "long":
        c.rectangle(-R, cy - 40, 30, 200); c.rectangle(R - 30, cy - 40, 30, 200); c.fill()
    c.restore()
    c.arc(0, cy, R, 0, TAU); c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
    if face:
        blink = math.fmod(t + seed * 0.7, 3.3) < 0.12
        for ex in (-34, 34):
            if blink:
                c.move_to(ex - 9, cy + 6); c.line_to(ex + 9, cy + 6); c.set_line_width(5); c.set_source_rgb(*INK); c.stroke()
            else:
                c.arc(ex, cy + 6, 8.5, 0, TAU); c.set_source_rgb(*INK); c.fill()
        c.arc(0, cy + 38, 20, 0.2 * math.pi, 0.8 * math.pi); c.set_line_width(5); c.set_source_rgb(*INK); c.stroke()
        for ex in (-58, 58):
            c.arc(ex, cy + 34, 12, 0, TAU); c.set_source_rgba(1, .45, .45, .25); c.fill()
    c.restore()

def person(c, x, ground, s, P, frame, head="main", facing=1, rot=0.0, mask=False, **hk):
    c.save()
    c.translate(x, ground - (HIP_H - P["bob"]) * s)
    c.scale(s * facing, s)
    if rot:
        c.translate(0, HIP_H); c.rotate(rot); c.translate(0, -HIP_H)
    if not rot:
        c.save(); c.translate(0, HIP_H - P["bob"]); c.scale(1, .18)
        c.arc(0, 0, 150, 0, TAU); c.set_source_rgba(0, 0, 0, .18); c.fill(); c.restore()
    body(c, P, frame)
    c.save(); c.translate(0, NECK_Y + 4); c.rotate(P["tilt"])
    if head == "main": main_head(c, mask)
    else: coded_head(c, frame, **hk)
    c.restore(); c.restore()

def suit_figure(c, x, ground, s, dark=True):
    c.save(); c.translate(x, ground); c.scale(s, s)
    col = "#121212"
    for lx in (-14, 14):
        c.rectangle(lx - 7, -60, 14, 60); c.set_source_rgb(.07, .07, .07); c.fill()
    rrect(c, -48, -230, 96, 180, 40); fill_stroke(c, col, 4, "#000000")
    c.move_to(-16, -226); c.line_to(0, -170); c.line_to(16, -226); c.close_path(); c.set_source_rgb(.95, .95, .95); c.fill()
    c.move_to(-14, -214); c.line_to(0, -206); c.line_to(14, -214); c.line_to(14, -198); c.line_to(0, -206); c.line_to(-14, -198); c.close_path()
    c.set_source_rgb(.05, .05, .05); c.fill()
    c.arc(0, -282, 50, 0, TAU); c.set_source_rgb(.09, .09, .09); c.fill()
    c.restore()

def P_(fn, u, **over):
    P = fn(u); P.update(over); return P

def lerpP(A, B, k):
    return {key: A[key] * (1 - k) + B[key] * k for key in A}

def captions(c, t, caps):
    for a, b, s in caps:
        if a <= t < b:
            c.select_font_face("Patrick Hand"); c.set_font_size(36)
            words = s.split(); lines = [""]
            for w in words:
                trial = (lines[-1] + " " + w).strip()
                if c.text_extents(trial).width > 980: lines.append(w)
                else: lines[-1] = trial
            for i, ln in enumerate(lines):
                y = H - 48 - (len(lines) - 1 - i) * 44
                e = c.text_extents(ln); x = W / 2 - e.width / 2 - e.x_bearing
                rrect(c, x - 16, y - 34, e.width + 32, 46, 10); c.set_source_rgba(0, 0, 0, .62); c.fill()
                c.new_path(); c.move_to(x, y); c.set_source_rgb(1, 1, 1); c.show_text(ln); c.new_path()

def frame_bytes(surf, t, fi, gray):
    buf = np.ndarray((H, W, 4), np.uint8, surf.get_data()).astype(np.float32)
    rgb = buf[..., :3]
    if gray:
        g = rgb @ np.array([0.114, 0.587, 0.299], np.float32)
        rgb = np.repeat(g[..., None], 3, axis=2) * 1.05
    rgb = rgb * vig + grain[(fi // 2) % 6]
    buf[..., :3] = np.clip(rgb, 0, 255)
    return buf.astype(np.uint8)

def draw_frame(surf, t, fi, SHOTS, TOTAL, CAPS):
    idx = max(i for i, s in enumerate(SHOTS) if s[0] <= t)
    st, fn, gray = SHOTS[idx]
    end = SHOTS[idx + 1][0] if idx + 1 < len(SHOTS) else TOTAL
    c = cairo.Context(surf); c.set_source_rgb(0, 0, 0); c.paint()
    c.save(); fn(c, t - st, end - st, fi); c.restore()
    arr = frame_bytes(surf, t, fi, gray)
    s2 = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_RGB24, W, H)
    c2 = cairo.Context(s2); captions(c2, t, CAPS); s2.flush()
    return arr

def stills(times, SHOTS, TOTAL, CAPS, prefix="st"):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    for t in times:
        arr = draw_frame(surf, t, int(t * FPS), SHOTS, TOTAL, CAPS)
        out = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_RGB24, W, H); out.write_to_png(f"{prefix}_{t:05.1f}.png")

def render_shot(i, SHOTS, TOTAL, CAPS, outdir="shots"):
    st = SHOTS[i][0]; end = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else TOTAL
    f0, f1 = int(round(st * FPS)), int(round(end * FPS))
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    tmp = f"{outdir}/s{i:02d}.tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        p.stdin.write(draw_frame(surf, fi / FPS, fi, SHOTS, TOTAL, CAPS).tobytes())
    p.stdin.close(); assert p.wait() == 0
    os.replace(tmp, f"{outdir}/s{i:02d}.mp4")


def caps_from_lines(lines, wps=2.6, start=0.4, pauses=None):
    """Placeholder timing until a voiceover exists: words / wps seconds per line."""
    pauses = pauses or {}; caps = []; t = start
    for i, line in enumerate(lines):
        d = len(line.split()) / wps + pauses.get(i, 0.25); caps.append((t, t + d, line)); t += d
    return caps, t + 1.0

def render_all(SHOTS, TOTAL, CAPS, out_mp4, outdir="shots"):
    from concurrent.futures import ProcessPoolExecutor
    from functools import partial
    os.makedirs(outdir, exist_ok=True)
    with ProcessPoolExecutor() as ex:
        list(ex.map(partial(render_shot, SHOTS=SHOTS, TOTAL=TOTAL, CAPS=CAPS, outdir=outdir), range(len(SHOTS))))
    with open(f"{outdir}/list.txt", "w") as fh:
        for i in range(len(SHOTS)): fh.write(f"file s{i:02d}.mp4\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-i", f"{outdir}/list.txt", "-c", "copy", out_mp4], check=True)
