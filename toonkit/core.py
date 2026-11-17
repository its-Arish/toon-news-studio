"""toonkit.core: drawing primitives, easing, film grain + vignette."""
import cairo, math, random, subprocess, sys
import numpy as np

W, H, FPS = 1280, 720, 30
OUT = "#262626"
FONT = "Patrick Hand"   # install assets/fonts/PatrickHand.ttf (see README)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out_back(t, s=1.9):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1
def ease_io(t):
    t = clamp(t); return t * t * (3 - 2 * t)
def prog(t, a, b): return clamp((t - a) / (b - a))
def hexc(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)

def fill_stroke(c, fill, lw=4, stroke=OUT):
    c.set_source_rgba(*hexc(fill)); c.fill_preserve()
    c.set_source_rgba(*hexc(stroke)); c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()

def rrect(c, x, y, w, h, r):
    c.new_sub_path()
    c.arc(x+w-r, y+r, r, -math.pi/2, 0); c.arc(x+w-r, y+h-r, r, 0, math.pi/2)
    c.arc(x+r, y+h-r, r, math.pi/2, math.pi); c.arc(x+r, y+r, r, math.pi, 1.5*math.pi); c.close_path()

def text(c, s, x, y, size, color=OUT, align="c", rot=0):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.select_font_face(FONT); c.set_font_size(size)
    e = c.text_extents(s)
    dx = {"c": -e.width/2 - e.x_bearing, "l": 0, "r": -e.width}[align]
    c.new_path(); c.move_to(dx, e.height/2); c.set_source_rgba(*hexc(color)); c.show_text(s); c.new_path(); c.restore()

def neon(c, s, x, y, size, color):
    c.save(); c.select_font_face(FONT); c.set_font_size(size); e = c.text_extents(s)
    c.new_path(); c.move_to(x - e.width/2 - e.x_bearing, y + e.height/2); c.text_path(s)
    r, g, b, _ = hexc(color)
    for lw, a in ((26, .06), (16, .1), (8, .2)):
        c.set_source_rgba(r, g, b, a); c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
    c.set_source_rgba(r, g, b, 1); c.fill(); c.restore()

# ---------- paper texture / grain / vignette ----------
rng = np.random.default_rng(3)
grain = [(rng.normal(0, 7, (H, W, 1))).astype(np.float32) for _ in range(6)]
yy, xx = np.mgrid[0:H, 0:W]
d = np.sqrt(((xx - W/2) / (W/2))**2 + ((yy - H/2) / (H/2))**2)
vig = (1 - 0.38 * np.clip(d - 0.35, 0, 1)**1.6)[..., None].astype(np.float32)

def post(surface, fi):
    buf = np.ndarray((H, W, 4), np.uint8, surface.get_data()).astype(np.float32)
    rgb = buf[..., :3] * vig + grain[(fi // 2) % 6]
    buf[..., :3] = np.clip(rgb, 0, 255)
    return buf.astype(np.uint8).tobytes()

