"""Split a hand-drawn head into a blank face + movable eye and brow sprites.
Usage: python3 tools/split_face.py assets/characters/rob
Boxes are in head.png pixel coordinates (see FACE dict). A character folder may hold
boxes.json to override them: {"eyeL":[x0,y0,x1,y1], ..., "skin":[x0,y0,x1,y1],
"brow":"dark"|"yellow", "fill":"flat"|"inpaint", "pivot":[x,y], "scale":1.0}."""
import sys, json, os
import numpy as np, cv2
from PIL import Image, ImageFilter

FACE = {   # x0, y0, x1, y1 in head.png pixels
    "eyeL": (120, 199, 177, 231), "eyeR": (211, 193, 254, 225),
    "browL": (112, 179, 191, 206), "browR": (213, 172, 258, 199),
    "mouth": (143, 270, 235, 310),
}
d = sys.argv[1]
OPT = {}
if os.path.exists(os.path.join(d, "boxes.json")):
    OPT = json.load(open(os.path.join(d, "boxes.json")))
    FACE = {k: tuple(OPT[k]) for k in ("eyeL", "eyeR", "browL", "browR", "mouth")}
im = np.array(Image.open(os.path.join(d, "head.png")).convert("RGBA"))
rgb = im[..., :3].copy(); alpha = im[..., 3]
lum = rgb.mean(axis=2)
H, W = lum.shape
erase = np.zeros((H, W), np.uint8)
meta = {}

def box_mask(b, pad=0):
    m = np.zeros((H, W), np.uint8); x0, y0, x1, y1 = b
    m[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad] = 255; return m

for k in ("eyeL", "eyeR"):
    x0, y0, x1, y1 = FACE[k]
    m = np.zeros((H, W), np.uint8)
    cv2.ellipse(m, ((x0 + x1) // 2, (y0 + y1) // 2), ((x1 - x0) // 2 + 2, (y1 - y0) // 2 + 2), 0, 0, 360, 255, -1)
    erase |= m
    a = Image.fromarray(m).filter(ImageFilter.GaussianBlur(1.2))
    spr = Image.fromarray(im).copy(); spr.putalpha(Image.fromarray(np.minimum(np.array(a), alpha)))
    spr.crop((x0 - 4, y0 - 4, x1 + 4, y1 + 4)).save(os.path.join(d, f"{k}.png"))
    meta[k] = {"x": x0 - 4, "y": y0 - 4, "cx": (x0 + x1) / 2, "cy": (y0 + y1) / 2, "w": (x1 - x0) / 2}

for k in ("browL", "browR"):
    bm = box_mask(FACE[k])
    if OPT.get("brow") == "yellow":   # light hair-coloured brows with dark strokes
        r_, g_, b_ = rgb[..., 0].astype(int), rgb[..., 1].astype(int), rgb[..., 2].astype(int)
        sel = ((r_ > 190) & (g_ > 150) & (b_ < 150) & (r_ - b_ > 70)) | (lum < 110)
        dark = (sel & (bm > 0)).astype(np.uint8) * 255
        dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    else:
        dark = ((lum < 120) & (bm > 0)).astype(np.uint8) * 255
    dark = cv2.dilate(dark, np.ones((3, 3), np.uint8), iterations=1)
    erase |= cv2.dilate(dark, np.ones((3, 3), np.uint8), iterations=1)
    a = Image.fromarray(dark).filter(ImageFilter.GaussianBlur(0.7))
    spr = Image.fromarray(im).copy(); spr.putalpha(a)
    x0, y0, x1, y1 = FACE[k]
    spr.crop((x0 - 4, y0 - 4, x1 + 4, y1 + 4)).save(os.path.join(d, f"{k}.png"))
    ys, xs = np.nonzero(dark)
    meta[k] = {"x": x0 - 4, "y": y0 - 4, "cx": float(xs.mean()), "cy": float(ys.mean())}

x0, y0, x1, y1 = FACE["mouth"]
# keep the drawn mouth as a sprite too: used for the closed/rest mouth so the drawing stays intact
spr = Image.fromarray(im).crop((x0 - 4, y0 - 4, x1 + 4, y1 + 4)); spr.save(os.path.join(d, "mouth.png"))
m = np.zeros((H, W), np.uint8)
cv2.ellipse(m, ((x0 + x1) // 2, (y0 + y1) // 2), ((x1 - x0) // 2, (y1 - y0) // 2), 0, 0, 360, 255, -1)
erase |= m
# lip colour sample = median of pinkish pixels inside the mouth box
mb = rgb[y0:y1, x0:x1].reshape(-1, 3); pink = mb[(mb[:, 0] > 150) & (mb[:, 1] < 150)]
if OPT: pink = mb[(mb.mean(axis=1) > 90) & (mb.mean(axis=1) < 170)]
meta["mouth"] = {"cx": (x0 + x1) / 2, "cy": (y0 + y1) / 2 - 4, "w": x1 - x0, "x": x0 - 4, "y": y0 - 4,
                 "lip": [int(v) for v in np.median(pink, axis=0)] if len(pink) else [200, 120, 110]}

sx0, sy0, sx1, sy1 = OPT.get("skin", (150, 235, 230, 265))
region = rgb[sy0:sy1, sx0:sx1].reshape(-1, 3); skin = np.median(region[region.mean(axis=1) > 150], axis=0)
meta["skin"] = [int(v) for v in skin]
fillm = cv2.dilate(erase, np.ones((3, 3), np.uint8), iterations=1)
if OPT.get("fill") == "inpaint":   # shaded faces: rebuild the skin from its surroundings
    hole = cv2.dilate(fillm, np.ones((3, 3), np.uint8), iterations=2) > 0
    # ignore ink and hair around the hole so only skin bleeds in (normalized convolution)
    r_, g_, b_ = [rgb[..., i].astype(int) for i in range(3)]
    skinlike = (r_ > 170) & (g_ > 90) & (g_ < 200) & (b_ < 140) & (r_ - g_ > 40)
    wgt = (~hole & skinlike & (alpha > 200)).astype(np.float32)
    acc = np.zeros_like(rgb, dtype=np.float32); ws = np.zeros(wgt.shape, np.float32)
    for sig in (4, 9, 18):       # coarse-to-fine so big holes still fill
        a_ = cv2.GaussianBlur(rgb.astype(np.float32) * wgt[..., None], (0, 0), sig)
        w_ = cv2.GaussianBlur(wgt, (0, 0), sig)
        need = (ws < 0.02) & (w_ > 1e-3)
        acc[need] = a_[need] / w_[need, None]; ws[need] = 1
    blank = rgb.astype(np.float32).copy()
    soft = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 1.2)[..., None]
    blank = blank * (1 - soft) + acc * soft
else:
    blank = rgb.astype(np.float32).copy(); blank[fillm > 0] = skin
    soft = cv2.GaussianBlur(fillm.astype(np.float32) / 255, (0, 0), 1.5)[..., None]
    blank = (blank * soft + rgb.astype(np.float32) * (1 - soft))
    blank[fillm > 0] = skin
blank = np.clip(blank, 0, 255).astype(np.uint8)
out = np.dstack([blank, alpha]); Image.fromarray(out).save(os.path.join(d, "head_blank.png"))
for k in ("pivot", "scale", "ink", "hands"):
    if k in OPT: meta[k] = OPT[k]
json.dump(meta, open(os.path.join(d, "face.json"), "w"), indent=1)
print(json.dumps(meta))
