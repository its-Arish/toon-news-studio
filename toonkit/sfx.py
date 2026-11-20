"""toonkit.sfx: procedural sound effects, mixed into one full-length track.

build_track(events, total_seconds, out_wav)  where events = [(time, name), ...]
Every sound is synthesized (no samples), so there is nothing to license.
"""
import math, random
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
_rng = np.random.default_rng(7)

def _t(d): return np.arange(int(d * SR)) / SR
def _noise(d): return _rng.standard_normal(int(d * SR))
def _lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def _hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def _bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], "band", fs=SR, output="sos"), x)
def _env(n, a=0.005, r=0.1):
    e = np.ones(n); na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr); return e
def _dec(d, k): return np.exp(-_t(d) * k)
def _norm(x, g):
    m = np.abs(x).max() or 1; return x / m * g
def _sine(f, d, ph=0.0):
    t = _t(d); f = np.broadcast_to(f, t.shape) if np.ndim(f) else f
    if np.ndim(f): return np.sin(2 * np.pi * np.cumsum(f) / SR + ph)
    return np.sin(2 * np.pi * f * t + ph)
def _ks(f, d, damp=0.996):
    n = int(d * SR); p = int(SR / f); buf = _rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = damp * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out
def _cat(*parts):
    return np.concatenate(parts)
def _place(dst, src, at):
    i = int(at * SR)
    if i >= len(dst): return
    j = min(len(dst), i + len(src)); dst[i:j] += src[:j - i]

def whoosh(seed=0):
    r = random.Random(seed); d = 0.38; n = _noise(d)
    lo = _lp(n, 900 + r.random() * 600); hi = _hp(_lp(n, 4000), 1200)
    k = np.sin(np.linspace(0, np.pi, len(n))) ** 2
    return _norm(lo * k + hi * k * np.linspace(0, 1, len(n)), 0.07)
def swoosh(seed=0): x = whoosh(seed)[: int(.25 * SR)]; return _norm(x * _env(len(x), .01, .08), .14)
def pop(seed=0):
    d = .09; f = np.linspace(700, 260, int(d * SR)); return _norm(_sine(f, d) * _dec(d, 40), .22)
def stamp(seed=0):
    d = .22; return _norm(_sine(np.linspace(140, 60, int(d * SR)), d) * _dec(d, 18) + _lp(_noise(d), 1500) * _dec(d, 40) * .6, .45)
def boom(seed=0):
    d = 1.4; return _norm(_sine(np.linspace(70, 38, int(d * SR)), d) * _dec(d, 3) + _lp(_noise(d), 200) * _dec(d, 4) * .7, .5)
def thud(seed=0):
    d = .3; return _norm(_sine(np.linspace(110, 55, int(d * SR)), d) * _dec(d, 14), .45)
def sparkle(seed=0):
    r = random.Random(seed); out = np.zeros(int(.9 * SR))
    for i in range(9):
        d = .25; s = _sine(r.uniform(2200, 5200), d) * _dec(d, 18); _place(out, s, i * .08 + r.random() * .03)
    return _norm(out, .1)
def magic(seed=0):
    d = 1.0; x = _sine(np.linspace(500, 2400, int(d * SR)), d) * _env(int(d * SR), .05, .4); sp = np.zeros(len(x)); src = sparkle(seed)[:len(x)]; sp[:len(src)] = src
    return _norm(x + sp * 2, .14)
def rain(seed=0, d=3.2):
    x = _lp(_hp(_noise(d), 800), 6000); return _norm(x * _env(len(x), .4, .8), .1)
def storm(seed=0):
    d = 3.6; return _norm(rain(seed, d) + _lp(_noise(d), 120) * .8 * _env(int(d * SR), .5, 1), .16)
def thunder(seed=0):
    d = 2.8; n = _lp(_noise(d), 260); e = _dec(d, 1.6) * (1 + .6 * np.abs(np.sin(_t(d) * 9))); return _norm(n * e, .5)
def squawk(seed=0):
    out = np.zeros(int(.7 * SR))
    for k, at in enumerate((0, .28)):
        d = .22; t = _t(d); f = 950 + 220 * np.sin(2 * np.pi * 28 * t) - 300 * t / d
        s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * _env(len(t), .01, .06); _place(out, _lp(s, 3000), at)
    return _norm(out, .2)
def click(seed=0): d = .03; return _norm(_hp(_noise(d), 2000) * _dec(d, 200), .2)
def type_(seed=0):
    r = random.Random(seed); out = np.zeros(int(1.5 * SR))
    for i in range(14): _place(out, click(i), i * .1 + r.random() * .03)
    return _norm(out, .16)
def heart(seed=0):
    out = np.zeros(int(.6 * SR)); _place(out, thud(), 0); _place(out, thud() * .7, .18); return _norm(out, .3)
def heartbeat(seed=0):
    out = np.zeros(int(2.2 * SR))
    for k in range(3): _place(out, heart(), k * .7)
    return _norm(out, .3)
def shutter(seed=0):
    out = np.zeros(int(.12 * SR)); _place(out, click(), 0); _place(out, click() * .8, .05); return _norm(out + _hp(_noise(.12), 3000) * _dec(.12, 60) * .2, .28)
def engine(seed=0):
    d = 1.6; t = _t(d); s = np.sign(np.sin(2 * np.pi * (55 + 6 * np.sin(2 * np.pi * 3 * t)) * t)); return _norm(_lp(s, 400) * _env(len(t), .2, .4), .14)
def car(seed=0): return engine(seed)
def notes(seed=0):
    r = random.Random(seed); out = np.zeros(int(1.4 * SR)); scale = [523, 587, 659, 784, 880, 1047]
    for i in range(5): d = .4; _place(out, _sine(r.choice(scale), d) * _dec(d, 9), i * .22)
    return _norm(out, .14)
def strum(seed=0):
    out = np.zeros(int(1.4 * SR))
    for i, f in enumerate((196, 247, 294, 392, 494)): _place(out, _ks(f, 1.2), i * .025)
    return _norm(_lp(out, 4000), .22)
def door(seed=0):
    d = .6; t = _t(d); cr = np.sin(2 * np.pi * np.cumsum(180 + 60 * np.sin(2 * np.pi * 7 * t)) / SR) * _env(len(t), .05, .2) * .3
    out = cr.copy(); _place(out, thud() * .6, .45); return _norm(_lp(out, 2000), .2)
def choir(seed=0):
    d = 1.8; x = sum(_sine(f, d) + .3 * _sine(f * 2, d) for f in (262, 330, 392)); return _norm(_lp(x, 2500) * _env(int(d * SR), .5, .7), .1)
def clap(seed=0): d = .1; return _norm(_bp(_noise(d), 800, 4000) * _dec(d, 50), .3)
def scissor(seed=0):
    out = np.zeros(int(.4 * SR))
    for at in (0, .16): d = .08; _place(out, _hp(_noise(d), 3500) * _dec(d, 50), at)
    return _norm(out, .2)
def tick(seed=0):
    out = np.zeros(int(2.0 * SR))
    for k in range(4): d = .04; _place(out, _sine(2400, d) * _dec(d, 120) + _hp(_noise(d), 3000) * _dec(d, 200) * .3, k * .5)
    return _norm(out, .16)
def fanfare(seed=0):
    out = np.zeros(int(1.6 * SR))
    for k, (f, at, d) in enumerate(((392, 0, .22), (523, .22, .22), (659, .44, 1.0))):
        t = _t(d); s = sum(np.sign(np.sin(2 * np.pi * f * h * t)) / h for h in (1, 2, 3)); _place(out, _lp(s, 2500) * _env(len(t), .02, .2), at)
    return _norm(out, .17)
def gasp(seed=0): d = .45; return _norm(_bp(_noise(d), 600, 3000) * np.sin(np.linspace(0, np.pi, int(d * SR))) ** 2, .1)
def ping(seed=0): d = .45; return _norm(_sine(1760, d) * _dec(d, 10) + .3 * _sine(3520, d) * _dec(d, 14), .14)
def boing(seed=0):
    d = .6; t = _t(d); f = 220 + 140 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 5); return _norm(_sine(f, d) * _dec(d, 4), .22)
def sad(seed=0):
    out = np.zeros(int(2.0 * SR))
    for k, (f0, f1) in enumerate(((330, 311), (311, 294), (294, 262))):
        d = .55; t = _t(d); f = np.linspace(f0, f1, len(t)); s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)); _place(out, _lp(s, 900) * _env(len(t), .03, .15), k * .55)
    return _norm(out, .16)
def footsteps(seed=0):
    out = np.zeros(int(2.0 * SR))
    for k in range(5): d = .08; _place(out, _lp(_noise(d), 600) * _dec(d, 40), k * .38)
    return _norm(out, .16)
def murmur(d=2.8, lo=300, hi=1500, g=.13, swell=False):
    t = _t(d); n = _bp(_noise(d), lo, hi); am = 1 + .5 * np.sin(2 * np.pi * 3.1 * t) * np.sin(2 * np.pi * 1.3 * t)
    e = _env(len(t), .4, .8) * (np.linspace(.5, 1, len(t)) if swell else 1); return _norm(n * am * e, g)
def crowd(seed=0): return murmur()
def pub(seed=0): return murmur(3.5, 250, 1200, .1)
def cheer(seed=0): return murmur(2.2, 600, 4000, .16, True)
def boo(seed=0): return murmur(2.0, 150, 600, .14)
def laugh(seed=0): return murmur(1.4, 500, 2500, .09, True)
def cash(seed=0):
    d = 1.0; x = sum(_sine(f, d) * _dec(d, k) for f, k in ((2093, 6), (3136, 8), (4186, 10))); out = _norm(x, 1)
    for i in range(6): _place(out, _hp(_noise(.03), 3000) * _dec(.03, 100) * .5, .05 + i * .06)
    return _norm(out, .2)
def ding(seed=0): d = 1.4; return _norm(_sine(1318, d) * _dec(d, 3) + .4 * _sine(2637, d) * _dec(d, 5), .2)
def flip(seed=0):
    out = np.zeros(int(.8 * SR))
    for k in range(5): d = .05; _place(out, _hp(_noise(d), 2500) * _dec(d, 60), k * .12)
    return _norm(out, .16)
def slam(seed=0): out = stamp(); return _norm(out + _lp(_noise(len(out) / SR), 3000) * _dec(len(out) / SR, 25), .45)
def smash(seed=0): return _norm(_cat(slam(), _hp(_noise(.5), 2500) * _dec(.5, 6) * .4), .45)
def crack(seed=0):
    d = .35; x = _hp(_noise(d), 1200) * _dec(d, 14); _place(x, thud() * .5, 0); return _norm(x, .32)
def rip(seed=0):
    d = .35; t = _t(d); return _norm(_hp(_noise(d), 1500) * (0.5 + .5 * np.sign(np.sin(2 * np.pi * 40 * t))) * _env(len(t), .01, .05), .2)
def chalk(seed=0): d = .3; return _norm(_sine(2600 + 300 * np.sin(2 * np.pi * 30 * _t(d)), d) * _env(int(d * SR), .02, .05), .06)
def paper(seed=0): d = .35; return _norm(_bp(_noise(d), 1500, 6000) * np.sin(np.linspace(0, np.pi, int(d * SR))), .12)
def wind(seed=0, d=3.0):
    t = _t(d); return _norm(_lp(_noise(d), 500) * (1 + .6 * np.sin(2 * np.pi * .7 * t)) * _env(len(t), .6, .9), .12)
def jungle(seed=0):
    out = wind(seed); r = random.Random(seed)
    for i in range(4):
        d = .18; f = np.linspace(r.uniform(2500, 3500), r.uniform(3500, 4500), int(d * SR)); _place(out, _sine(f, d) * _env(int(d * SR), .01, .08) * .4, .3 + i * .6)
    return _norm(out, .12)
def space(seed=0): d = 3.0; return _norm((_sine(55, d) + .6 * _sine(82.5, d)) * _env(int(d * SR), .8, 1.0), .1)
def sea(seed=0, d=3.0):
    t = _t(d); return _norm(_lp(_noise(d), 900) * (0.6 + .4 * np.sin(2 * np.pi * .35 * t)) * _env(len(t), .6, .8), .12)
def cricket(seed=0):
    out = np.zeros(int(2.0 * SR))
    for k in range(6):
        d = .12; s = _sine(4600, d) * (0.5 + .5 * np.sign(np.sin(2 * np.pi * 45 * _t(d)))) * _env(int(d * SR), .005, .02); _place(out, s, k * .33)
    return _norm(out, .05)
def neon(seed=0): d = 1.2; return _norm(_lp(np.sign(_sine(120, d)), 800) * _env(int(d * SR), .05, .2), .05)
def siren(seed=0):
    d = 2.6; t = _t(d); f = 750 + 250 * np.sin(2 * np.pi * 1.2 * t); return _norm(_sine(f, d) * _env(len(t), .2, .4), .1)
def projector(seed=0):
    d = 2.0; t = _t(d); return _norm(_hp(_noise(d), 2000) * (np.sin(2 * np.pi * 24 * t) > .7) * _env(len(t), .2, .3), .08)
def creak(seed=0):
    d = .9; t = _t(d); s = np.sign(np.sin(2 * np.pi * np.cumsum(90 + 40 * np.sin(2 * np.pi * 2 * t)) / SR)); return _norm(_lp(s, 900) * _env(len(t), .1, .2), .1)
def rope(seed=0): return creak(seed)
def rewind(seed=0):
    d = 1.0; t = _t(d); f = 600 + 900 * t / d + 300 * np.sin(2 * np.pi * 14 * t); return _norm(_lp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 2500) * _env(len(t), .05, .2), .12)
def beep(seed=0): d = .3; return _norm(_sine(1000, d) * _env(int(d * SR), .005, .03), .14)
def lock(seed=0): out = click(); return _norm(_cat(out, np.zeros(int(.05 * SR)), click()), .25)
def bells(seed=0):
    out = np.zeros(int(2.0 * SR))
    for k, f in enumerate((784, 659, 523, 659)): _place(out, _sine(f, 1.2) * _dec(1.2, 3) + .3 * _sine(f * 2.76, 1.2) * _dec(1.2, 6), k * .35)
    return _norm(out, .15)
def news(seed=0):
    out = np.zeros(int(1.4 * SR))
    for k, f in enumerate((440, 554, 659, 880)): d = .3 if k < 3 else .8; _place(out, _lp(np.sign(_sine(f, d)), 3000) * _env(int(d * SR), .01, .1), k * .15)
    return _norm(out, .18)
def chain(seed=0):
    out = np.zeros(int(.9 * SR)); r = random.Random(seed)
    for k in range(6): d = .2; _place(out, sum(_sine(r.uniform(2000, 5000), d) for _ in range(3)) * _dec(d, 25), k * .12)
    return _norm(out, .16)
def clank(seed=0): d = .5; return _norm(sum(_sine(f, d) for f in (420, 1130, 2210)) * _dec(d, 10), .2)
def vinyl(seed=0):
    d = 2.5; n = (_rng.random(int(d * SR)) > .9993) * _rng.uniform(-1, 1, int(d * SR)); return _norm(_hp(n, 1000) + _lp(_noise(d), 300) * .05, .1)
def printer(seed=0):
    d = 1.4; t = _t(d); return _norm(_bp(_noise(d), 400, 1600) * (0.6 + .4 * np.sign(np.sin(2 * np.pi * 12 * t))) * _env(len(t), .05, .2), .1)
def whirr(seed=0):
    d = 1.4; t = _t(d); f = np.linspace(80, 260, len(t)); return _norm(_lp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 1500) * _env(len(t), .1, .3), .09)
def shake(seed=0):
    out = np.zeros(int(1.7 * SR))
    for k in range(12): d = .06; _place(out, _hp(_noise(d), 3000) * _dec(d, 50), k * .13)
    return _norm(out, .13)
def pour(seed=0):
    d = .8; t = _t(d); return _norm(_bp(_noise(d), 300, 1500) * (0.6 + .4 * np.sin(2 * np.pi * 11 * t)) * _env(len(t), .05, .2), .12)
def slide(seed=0): return swoosh(seed)
def nervous(seed=0): return ping(seed) * .6
def marker(seed=0, d=0.45):
    """felt-tip highlighter stroke: dry fibre scratch + a faint squeak, length = the stroke."""
    r = random.Random(seed); d = max(.15, d); t = _t(d); n = _noise(d)
    grit = _bp(n, 1800, 6500) * (0.55 + .45 * np.abs(np.sin(2 * np.pi * r.uniform(55, 80) * t)))
    body = _bp(n, 500, 1600) * .35
    sq = _sine(np.linspace(r.uniform(1900, 2200), r.uniform(2300, 2600), len(t)), d) * .05
    return _norm((grit + body + sq) * _env(len(t), .02, .07), .16)
def marker_cap(seed=0):
    d = .06; return _norm(_bp(_noise(d), 1500, 5000) * _dec(d, 80) + _sine(900, d) * _dec(d, 60) * .4, .18)
def silence(seed=0): return np.zeros(1)

BANK = {k: v for k, v in globals().items() if callable(v) and not k.startswith("_")}
BANK["type"] = type_
for k in ("shout", "baby", "yawn"): BANK[k] = silence
for k in ("build_track", "murmur", "butter", "sosfilt"): BANK.pop(k, None)

def build_track(events, total, out_wav, gain=1.0):
    import wave
    mix = np.zeros(int(total * SR) + SR)
    for i, (t, name) in enumerate(events):
        fn = BANK.get(name, pop)
        _place(mix, fn(i), t)
    mix = mix[: int(total * SR)] * gain
    mix = np.tanh(mix * 1.2) / 1.2
    pk = np.abs(mix).max()
    if pk > .89: mix *= .89 / pk
    data = (mix * 32767).astype(np.int16)
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())
    return len(events)
