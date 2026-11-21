#!/usr/bin/env python3
"""Conform recorded History Map segments into finished map clips in the house format.

  python3 tools/conform_maps.py episodes/2026-11-oil-iran-january [shot ids...]

historymap/raw/<seg>.mp4 (1920x1080, 60 fps, from tools/record_historymap.mjs) + <seg>.proj.json
→ maps/<shot>.mp4      1280x720, 30 fps, H.264 crf 18, exactly dur x 30 frames, WITH its sound effects
  maps/<shot>_sfx.wav  the sound effects alone (same length), for the separate SFX track
  maps/<shot>.png      final frame

Per frame: dark leading frames (satellite tiles not drawn yet) are replaced by the first good frame;
pins, pin names, arrow labels, our labels and notes are drawn in Patrick Hand at the screen positions
the recorder logged (white rounded boxes, ink outline, slight tilt, bounce in); then grain + vignette
exactly as tools/news_shots.py grades its frames.
Sound: a quiet whoosh on the cut and on every camera move, an impact when the camera lands from space,
a pop for every pin / label, a soft swoosh as each arrow starts drawing.
"""
import json, math, subprocess, sys, zlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'tools'))
import news_shots as NS            # grade(), write_wav(): same grain + vignette as the news clips
from toonkit import sfx

W, H, FPS = 1280, 720, 30
FONT = ROOT / 'assets/fonts/PatrickHand.ttf'
INK = (24, 22, 20, 255)
RED = (200, 49, 43, 255)
SAFE_BOTTOM = 560     # keep labels clear of the caption zone (bottom-centre captions in the edit)


def font(px): return ImageFont.truetype(str(FONT), px)


def ease(t): t = min(1.0, max(0.0, t)); return t * t * (3 - 2 * t)


def ease_out_back(t, k=1.7):
    t = min(1.0, max(0.0, t)); t -= 1; return 1 + t * t * ((k + 1) * t + k)


def text_width(d, txt, f):
    """width of a label; '→' (not in Patrick Hand) is drawn as an inked arrow 0.9 em wide"""
    parts = txt.split('→')
    return sum(d.textlength(p, font=f) for p in parts) + (len(parts) - 1) * f.size * 0.9


def draw_text(d, x, y, txt, f, fill):
    parts = txt.split('→')
    for i, p in enumerate(parts):
        d.text((x, y), p, font=f, fill=fill); x += d.textlength(p, font=f)
        if i < len(parts) - 1:
            aw = f.size * 0.9; cy = y + f.size * 0.62; lw = max(2, f.size // 12)
            d.line([(x + aw * 0.12, cy), (x + aw * 0.85, cy)], fill=fill, width=lw)
            d.line([(x + aw * 0.58, cy - aw * 0.25), (x + aw * 0.88, cy), (x + aw * 0.58, cy + aw * 0.25)], fill=fill, width=lw, joint='curve')
            x += aw


_sprites = {}


def label_sprite(txt, px, bg, fg=INK):
    """white (or tinted) rounded box with ink outline, tilted -2.5..2.5 deg (stable per text)"""
    key = (txt, px, bg)
    if key in _sprites: return _sprites[key]
    f = font(px)
    d0 = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    tw = text_width(d0, txt, f)
    padx, pady, ol = px * 0.42, px * 0.16, max(3, px // 11)
    bw, bh = int(tw + 2 * padx), int(px * 1.25 + 2 * pady)
    im = Image.new('RGBA', (bw + 24, bh + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([12 + 4, 12 + 5, 12 + bw + 4, 12 + bh + 5], int(px * 0.32), fill=(0, 0, 0, 90))     # drop shadow
    d.rounded_rectangle([12, 12, 12 + bw, 12 + bh], int(px * 0.32), fill=bg, outline=INK, width=ol)
    draw_text(d, 12 + padx, 12 + pady - px * 0.02, txt, f, fg)
    tilt = ((zlib.crc32(txt.encode()) % 1000) / 1000 - 0.5) * 5
    im = im.rotate(tilt, resample=Image.BICUBIC, expand=True)
    _sprites[key] = im
    return im


def paste_scaled(frame, sprite, cx, cy, k, alpha=1.0):
    if k <= 0.02 or alpha <= 0.01: return
    w, h = max(1, int(sprite.width * k)), max(1, int(sprite.height * k))
    sp = sprite.resize((w, h), Image.BICUBIC) if (w, h) != sprite.size else sprite
    if alpha < 1: sp = sp.copy(); sp.putalpha(sp.getchannel('A').point(lambda v: int(v * alpha)))
    frame.alpha_composite(sp, (int(cx - w / 2), int(cy - h / 2)))


def clamp_box(cx, cy, sprite, k=1.0):
    hw, hh = sprite.width * k / 2, sprite.height * k / 2
    return min(max(cx, 14 + hw), W - 14 - hw), min(max(cy, 14 + hh), SAFE_BOTTOM - hh)


def draw_pin(d, x, y, style, k, tsec):
    r = 9 * k
    if r < 1: return
    if style == 'target':
        ph = (tsec % 1.2) / 1.2                                        # pulse ring
        rr = (16 + 22 * ph) * k; a = int(200 * (1 - ph))
        d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(255, 255, 255, a), width=3)
        for rad, wdt, col in [(15 * k, 7, INK), (15 * k, 3, (255, 255, 255, 255)), (7 * k, 0, None)]:
            if col: d.ellipse([x - rad, y - rad, x + rad, y + rad], outline=col, width=wdt)
        d.ellipse([x - 6 * k, y - 6 * k, x + 6 * k, y + 6 * k], fill=RED, outline=INK, width=3)
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            d.line([(x + dx * 18 * k, y + dy * 18 * k), (x + dx * 27 * k, y + dy * 27 * k)], fill=INK, width=6)
            d.line([(x + dx * 18 * k, y + dy * 18 * k), (x + dx * 27 * k, y + dy * 27 * k)], fill=(255, 255, 255, 255), width=3)
    else:
        d.ellipse([x - r - 3, y - r - 3, x + r + 3, y + r + 3], fill=INK)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 255))
        d.ellipse([x - r * 0.55, y - r * 0.55, x + r * 0.55, y + r * 0.55], fill=RED)


def note_chip(txt):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = font(26)
    tw = d.textlength(txt, font=f); x, y = 36, H - 76
    d.rounded_rectangle([x, y, x + tw + 28, y + 42], 10, fill=(0, 0, 0, 158))
    d.text((x + 14, y + 5), txt, font=f, fill=(255, 255, 255, 230))
    return im


def decode(path, n):
    cmd = ['ffmpeg', '-v', 'error', '-i', str(path), '-vf', 'fps=30,scale=1280:720:flags=lanczos,tpad=stop_mode=clone:stop=30',
           '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    got = len(raw) // (W * H * 3)
    assert got == n, f'{path.name}: decoded {got} frames, wanted {n}'
    return np.frombuffer(raw, np.uint8).reshape(n, H, W, 3)


def fix_dark_lead(frames, name):
    m = frames[:, 60:660:8, ::8].mean(axis=(1, 2, 3))
    k = 0
    while k < len(m) and m[k] < 30: k += 1
    if 0 < k < len(m):
        print(f'   {name}: {k} dark lead frame(s) replaced by the first good frame')
        frames = frames.copy(); frames[:k] = frames[k]
    elif k == len(m):
        raise SystemExit(f'{name}: every frame is dark, re-record it')
    return frames


def conform_shot(ep, segs):
    sid = segs[0]['shot_id']; total = segs[0]['shot_frames']
    raw = ep / 'historymap' / 'raw'; out = ep / 'maps'; out.mkdir(exist_ok=True)
    tmp = out / f'{sid}.video.mp4'
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS), str(tmp)],
                           stdin=subprocess.PIPE)
    SR = sfx.SR
    mix = np.zeros(int(total / FPS * SR) + SR, np.float64)
    sfx._place(mix, sfx.swoosh(1) * 0.8, 0.0)                     # the cut
    gi, last, seed = 0, None, 10
    for m in segs:
        n = m['frames']; t_seg = m['offset'] / FPS
        frames = decode(raw / f"{m['seg']}.mp4", n)
        if not m['shot'].get('space'): frames = fix_dark_lead(frames, m['seg'])
        proj = json.loads((raw / f"{m['seg']}.proj.json").read_text())['frames']
        pt_ms = np.array([p['t'] for p in proj])
        npins, nlab = len(m['pins']), len(m['labels'])
        note = note_chip(m['note']) if m.get('note') else None
        note_first = m.get('note') and not any(o['k'] == m['k'] - 1 and o.get('note') for o in segs)
        # sounds for this segment
        if m['k'] > 0: sfx._place(mix, sfx.whoosh(seed) * 0.45, t_seg); seed += 1
        if m['shot'].get('space'):
            land = m['shot']['durMs'] * m['shot']['spaceFrac'] / 1000
            sfx._place(mix, sfx.whoosh(seed) * 0.6, t_seg + max(0, land - 0.9)); sfx._place(mix, sfx.thud(seed) * 0.8, t_seg + land); seed += 1
        if m.get('rise'): sfx._place(mix, sfx.whoosh(seed) * 0.7, t_seg + 0.1); seed += 1
        for p in m['pins'] + m['labels']:
            if p['at'] >= 0: sfx._place(mix, sfx.pop(seed) * 0.7, t_seg + p['at']); seed += 1
        for a in m['arrows']:
            if a['at'] >= 0: sfx._place(mix, sfx.swoosh(seed) * 0.5, t_seg + a['at']); seed += 1

        for i in range(n):
            tl = i / FPS
            pr = proj[int(np.abs(pt_ms - tl * 1000).argmin())]
            sc = W / pr['w']; far = pr['z'] < 2.4
            P = [(x * sc, y * sc, occ) for x, y, occ in pr['p']]
            fr = Image.fromarray(frames[i]).convert('RGBA')
            d = ImageDraw.Draw(fr)
            visible = lambda j: not far and not P[j][2] and -40 < P[j][0] < W + 40 and -40 < P[j][1] < H + 40
            # arrow labels under the tail
            for j, a in enumerate(m['arrows']):
                q = npins + nlab + j
                if not a['label'] or not visible(q): continue
                prog = 1.0 if a['at'] < 0 else ease((tl - a['at']) / max(0.1, a['end'] - a['at']))
                if prog < 0.12: continue
                k = 1.0 if a['at'] < 0 else ease_out_back((prog - 0.12) / 0.3)
                sp = label_sprite(a['label'], 26, (255, 255, 255, 255) if a['color'].lower() == '#ffffff' else (255, 225, 77, 255))
                cx, cy = clamp_box(P[q][0], P[q][1] + 34, sp)
                paste_scaled(fr, sp, cx, cy, k)
            # pins + names
            for j, p in enumerate(m['pins']):
                if not visible(j): continue
                age = 9 if p['at'] < 0 else tl - p['at']
                if age < 0: continue
                k = ease_out_back(age / 0.32)
                draw_pin(d, P[j][0], P[j][1], p['style'], k, tl + t_seg)
                sp = label_sprite(p['name'], 30, (255, 255, 255, 255))
                right = P[j][0] + 22 + sp.width < W - 14
                cx = P[j][0] + (22 + sp.width / 2 if right else -22 - sp.width / 2)
                cx, cy = clamp_box(cx, P[j][1] - 30, sp)
                paste_scaled(fr, sp, cx, cy, ease_out_back((age - 0.08) / 0.32))
            # our statement labels (yellow)
            for j, lb in enumerate(m['labels']):
                q = npins + j
                if far or P[q][2]: continue
                age = 9 if lb['at'] < 0 else tl - lb['at']
                if age < 0: continue
                sp = label_sprite(lb['text'], 40, (255, 225, 77, 255))
                cx, cy = clamp_box(P[q][0], P[q][1], sp)
                paste_scaled(fr, sp, cx, cy, ease_out_back(age / 0.35))
            if note is not None:
                a = ease(tl / 0.3) if note_first else 1.0
                if a >= 0.99: fr.alpha_composite(note)
                elif a > 0: fr = Image.blend(fr, Image.alpha_composite(fr, note), a)
            rgb = NS.grade(np.asarray(fr.convert('RGB')), gi // 2)
            enc.stdin.write(rgb.tobytes()); last = rgb; gi += 1
    enc.stdin.close(); enc.wait()
    assert gi == total, f'{sid}: wrote {gi} frames, wanted {total}'
    Image.fromarray(last).save(out / f'{sid}.png')
    mix = mix[: int(total / FPS * SR)]
    wav = out / f'{sid}_sfx.wav'
    NS.write_wav(wav, mix, SR)
    final = out / f'{sid}.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(tmp), '-i', str(wav), '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-shortest', str(final)], check=True)
    tmp.unlink()
    got = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames',
                              '-of', 'csv=p=0', str(final)], capture_output=True, text=True).stdout.strip())
    assert got == total, f'{sid}: final clip has {got} frames, wanted {total}'
    print(f'{sid}: {len(segs)} segment(s) → maps/{sid}.mp4, {got} frames ({got / FPS:.2f} s) ✓')


def main():
    ep = Path(sys.argv[1]).resolve()
    only = set(sys.argv[2:])
    man = json.loads((ep / 'historymap' / 'manifest.json').read_text())
    shots = {}
    for m in man: shots.setdefault(m['shot_id'], []).append(m)
    for sid, segs in shots.items():
        if only and sid not in only: continue
        conform_shot(ep, segs)


if __name__ == '__main__':
    main()
