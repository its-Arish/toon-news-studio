#!/usr/bin/env python3
"""maps.json → History Map project files (one per on-screen segment) + manifest.json.

  python3 tools/make_historymap_maps.py episodes/2026-11-oil-iran-january/maps.json

Same project-file format as naah/projects/america/tools/make_historymap_shots.py: a GeoJSON
FeatureCollection with a `historymap` member (settings, regions, arrows, scripted `shot`).

Each map shot is cut into segments of 1.8-3 s. A segment is one eased camera move (History Map
plays one move per shot), and the next segment starts where the last one stopped, so the camera
reads as a chain of moves: something changes every 2-3 s (move, region fade, arrow draw, pin pop).

Only the satellite map, coloured regions and arrows come from History Map. Pins, pin names,
arrow labels and our labels are drawn afterwards in Patrick Hand by tools/conform_maps.py, at
the screen positions the recorder logs for every frame (so they can pop on their own beat).

Timing: each clip lasts as long as its line is spoken in voiceover.srt (next to maps.json), else 'dur'.
The PLAN's pin / label / arrow times are keyed to the SRT word times noted beside each shot.
"""
import json, math, os, sys

FPS = 30
CSS_W = 1024  # History Map canvas width (CSS px) while recording (the app keeps a 1024x576 stage; exported at 1920x1080)


def qz(zoom):
    """maps.json 'zoom' is a MapLibre zoom on the 960 px recording canvas → History Map qz."""
    return round(2 ** zoom * 512 / CSS_W, 4)


# Per shot: segments with seconds, camera move (center/zoom from → to), what appears and when (s within
# the segment; negative = already on screen from an earlier segment). Word times = word index / words × dur.
W, Y, R, B, A = '#ffffff', '#ffe14d', '#C8312B', '#2F6FD6', '#F3B562'
F = lambda n: n / FPS   # segment lengths are given in frames so they add up to the SRT line exactly
PLAN = {
    'map01-strikes': {   # SRT 5.23 s: February 0.9, Israel 2.8, launched 3.2, strikes 3.8, Iran 4.6
        'globe': True,   # starts from space, so the whole shot stays on the globe projection (no jump between segments)
        'segs': [
            {'s': F(78), 'from': ([44.0, 31.0], 4.2), 'to': ([44.0, 31.0], 4.2), 'space': 0.75, 'regions': ['IRN', 'ISR'],
             'pins': [('TEHRAN', [51.39, 35.69], 'dot', 2.05)]},
            {'s': F(79), 'from': ([44.0, 31.0], 4.2), 'to': ([46.0, 32.0], 4.55), 'regions': ['IRN', 'ISR'],
             'pins': [('TEHRAN', [51.39, 35.69], 'dot', -1)],
             'arrows': [([34.9, 31.6], [51.39, 35.69], W, '28 FEB', 0.3, 1.5, False)]},
        ]},
    'map02-hormuz': {    # SRT 7.44 s: Hormuz 1.2, Oman 3.9, fifth 5.7, oil 7.1
        'segs': [
            {'s': F(75), 'from': ([56.4, 26.5], 4.6), 'to': ([56.4, 26.5], 5.2), 'regions': ['IRN'],
             'pins': [('STRAIT OF HORMUZ', [56.45, 26.55], 'dot', 1.2)]},
            {'s': F(74), 'from': ([56.4, 26.5], 5.2), 'to': ([56.43, 26.53], 6.3), 'regions': ['IRN'], 'late': ['OMN'], 'late_at': 1.35,
             'pins': [('STRAIT OF HORMUZ', [56.45, 26.55], 'dot', -1)]},
            {'s': F(74), 'from': ([56.43, 26.53], 6.3), 'to': ([56.45, 26.55], 7.2), 'regions': ['IRN', 'OMN'],
             'pins': [('STRAIT OF HORMUZ', [56.45, 26.55], 'dot', -1)],
             'labels': [("~1/5 OF THE WORLD'S OIL", [58.2, 25.2], 0.7)]},
        ]},
    'map03-blockade': {  # SRT 6.40 s: blockade 1.7, ports 2.9, Iran kept hitting ships 4.3-5.9
        'segs': [
            {'s': F(64), 'from': ([56.0, 26.4], 5.0), 'to': ([55.2, 26.7], 5.2), 'regions': ['IRN'],
             'labels': [('US BLOCKADE · 14 JULY', [55.0, 25.6], 1.6)]},
            {'s': F(64), 'from': ([55.2, 26.7], 5.2), 'to': ([54.5, 27.0], 5.4), 'regions': ['IRN'],
             'labels': [('US BLOCKADE · 14 JULY', [55.0, 25.6], -1)],
             'pins': [('BANDAR ABBAS', [56.27, 27.18], 'dot', 0.75), ('KHARG ISLAND', [50.32, 29.24], 'dot', 1.3)]},
            {'s': F(64), 'from': ([54.5, 27.0], 5.4), 'to': ([54.0, 27.5], 5.75), 'regions': ['IRN'],
             'labels': [('US BLOCKADE · 14 JULY', [55.0, 25.6], -1)],
             'pins': [('BANDAR ABBAS', [56.27, 27.18], 'dot', -1), ('KHARG ISLAND', [50.32, 29.24], 'dot', -1)]},
        ]},
    'map04-escape': {    # SRT 11.04 s: southern side 1.4, trackers 2.8, guided by American forces 5.2, Gulf 6.6,
                         # pipelines 8.9, skip Hormuz 9.7, completely 10.4
        'segs': [
            {'s': F(90), 'from': ([56.75, 26.25], 7.0), 'to': ([56.6, 26.2], 6.9),
             'arrows': [([55.6, 26.0], [57.6, 25.4], Y, 'TRACKERS OFF', 1.0, 2.6, False)]},
            {'s': F(84), 'from': ([56.6, 26.2], 6.9), 'to': ([54.0, 25.6], 5.6),
             'arrows': [([55.6, 26.0], [57.6, 25.4], Y, 'TRACKERS OFF', -1, -1, False)],
             'labels': [('GUIDED BY US FORCES', [56.6, 24.6], 2.1)]},
            {'s': F(84), 'from': ([54.0, 25.6], 5.6), 'to': ([47.0, 24.5], 4.4), 'late': ['SAU', 'ARE'], 'late_at': 0.8,
             'arrows': [([55.6, 26.0], [57.6, 25.4], Y, '', -1, -1, False)]},
            {'s': F(73), 'from': ([47.0, 24.5], 4.4), 'to': ([47.4, 24.4], 4.55), 'regions': ['SAU', 'ARE'],
             'arrows': [([55.6, 26.0], [57.6, 25.4], Y, '', -1, -1, False),
                        ([49.67, 25.94], [38.06, 24.09], W, 'EAST-WEST PIPELINE → YANBU', 0.2, 1.0, True),
                        ([53.6, 23.8], [56.33, 25.12], W, '→ FUJAIRAH', 0.6, 1.2, True)],
             'labels': [('PIPELINES SKIP HORMUZ', [45.0, 21.5], 1.1)]},
        ]},
    'map05-carriers': {  # SRT 3.60 s: third 0.1, carrier 1.5, region 3.1; positions illustrative, generic names only
        'note': 'POSITIONS ILLUSTRATIVE',
        'segs': [
            {'s': F(54), 'from': ([55.0, 20.0], 3.25), 'to': ([55.0, 20.0], 3.55),
             'pins': [('CARRIER 1', [61.5, 21.0], 'target', 0.2), ('CARRIER 2', [58.9, 23.9], 'target', 0.6)]},
            {'s': F(54), 'from': ([55.0, 20.0], 3.55), 'to': ([56.5, 19.5], 3.75),
             'pins': [('CARRIER 1', [61.5, 21.0], 'target', -1), ('CARRIER 2', [58.9, 23.9], 'target', -1),
                      ('CARRIER 3', [63.5, 17.5], 'target', 0.1)],
             'labels': [('3 US CARRIERS IN THE REGION', [56.0, 15.0], 0.9)]},
        ]},
    'map06-tankers-hit': {  # SRT 6.08 s: Hormuz 1.5, 65 3.0, tankers 4.3, hit 5.8
        'note': 'APPROXIMATE LOCATION',
        'note_from': 2,     # segment index the note appears in (with the tanker pin)
        'segs': [
            {'s': F(61), 'from': ([56.45, 26.4], 5.6), 'to': ([56.45, 26.4], 6.0), 'regions': ['IRN']},
            {'s': F(61), 'from': ([56.45, 26.4], 6.0), 'to': ([56.45, 26.4], 6.6), 'regions': ['IRN'],
             'labels': [('TRAFFIC −65%', [58.0, 25.0], 0.9)]},
            {'s': F(60), 'from': ([56.45, 26.4], 6.6), 'to': ([56.55, 26.35], 7.0), 'regions': ['IRN'],
             'labels': [('TRAFFIC −65%', [58.0, 25.0], -1)],
             'pins': [('TANKER HIT · 20 NOV', [56.6, 26.3], 'target', 0.25)]},
        ]},
    'map07-three-roads': {  # SRT 4.04 s; ends on the globe for the cut to the cartoon fork
        'globe': True,
        'segs': [
            {'s': F(54), 'from': ([56.4, 26.5], 5.6), 'to': ([56.4, 26.5], 5.0), 'regions': ['IRN', 'USA']},
            {'s': F(67), 'from': ([56.4, 26.5], 5.0), 'to': ([-22.0, 30.0], 1.75), 'regions': ['IRN', 'USA'], 'rise': True},
        ]},
}


def srt_lengths(ep, shots):
    """Spoken length of each map line in voiceover.srt (word times interpolated inside each cue)."""
    import re, difflib
    def ts(x):
        h, m, r = x.split(':'); sec, ms = r.split(','); return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
    W = []
    for blk in open(os.path.join(ep, 'voiceover.srt')).read().strip().split('\n\n'):
        L = blk.strip().split('\n'); a, c = (ts(v) for v in L[1].split(' --> ')); ws = ' '.join(L[2:]).split()
        tot = sum(len(w) + 1 for w in ws); acc = 0
        for w in ws:
            t0 = a + (c - a) * acc / tot; acc += len(w) + 1
            W.append((re.sub(r'[^a-z0-9]', '', w.lower()), t0, a + (c - a) * acc / tot))
    words = [w for w, _, _ in W]
    norm = lambda t: [re.sub(r'[^a-z0-9]', '', w.lower()) for w in t.split()]
    out = {}
    for sid, sh in shots.items():
        first, last = norm(sh['line'].split('...')[0]), norm(sh['line'].split('...')[-1])
        i = max(range(len(words)), key=lambda i: difflib.SequenceMatcher(None, words[i:i + len(first)], first).ratio())
        while words[i] != first[0] and i + 1 < len(words) and words[i + 1] == first[0]: i += 1
        j = max(range(i, min(len(words), i + 400)), key=lambda j: (difflib.SequenceMatcher(None, words[max(i, j - len(last) + 1):j + 1], last).ratio(), -j))
        out[sid] = (W[i][1], W[j][2] - W[i][1])
    return out


# maps.json gives Saudi Arabia / UAE / Oman amber (#F3B562); on the satellite style that colour vanishes
# into the desert, so they are drawn in green instead (noted in BROLL.md).
COLOUR_OVERRIDE = {'#F3B562': '#2FA35B'}

SETTINGS = {'style': 'satellite', 'aspect': '16:9', 'accent': '#C8312B', 'globe': False, 'pitch': False,
            'labels': False, 'pace': 1, 'title': '', 'subtitle': '', 'watermark': '', 'format': 'mp4',
            'quality': 2, 'fillOpacity': 0.5, 'borders': True, 'fromSpace': False, 'zoomHop': False}


def main():
    mpath = os.path.abspath(sys.argv[1])
    ep = os.path.dirname(mpath)
    shots = {s['id']: s for s in json.load(open(mpath))['shots']}
    srt = srt_lengths(ep, shots) if os.path.exists(os.path.join(ep, 'voiceover.srt')) else {}
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    naah_idx = os.environ.get('HISTORYMAP_INDEX', os.path.expanduser('~/naah/vendor/historymap/data/index.json'))
    countries = {c['id']: c['name'] for c in json.load(open(naah_idx))['countries']}
    out = os.path.join(ep, 'historymap')
    os.makedirs(out, exist_ok=True)
    manifest = []
    for sid, plan in PLAN.items():
        sh = shots[sid]
        colour = {r['iso3']: COLOUR_OVERRIDE.get(r['color'], r['color']) for r in sh.get('regions', [])}
        # clip length: the line's spoken length in voiceover.srt when there is one, else 'dur'
        total = round(srt[sid][1] * FPS) if sid in srt else round(sh['dur'] * FPS)
        if sid in srt: print(f'{sid}: SRT {srt[sid][0]:.2f} s + {srt[sid][1]:.2f} s → {total} frames')
        frames = [round(sg['s'] * FPS) for sg in plan['segs']]
        assert sum(frames) == total, f'{sid}: segments {sum(frames)} f, dur {total} f'
        offset = 0
        for k, sg in enumerate(plan['segs']):
            n = frames[k]
            dur_ms = n / FPS * 1000
            regions = []
            for iso in sg.get('regions', []) + sg.get('late', []):
                regions.append({'id': iso, 'kind': 'country', 'name': countries[iso], 'color': colour[iso],
                                **({'late': True} if iso in sg.get('late', []) else {})})
            arrows, arrow_times = [], []
            for (a, b, col, label, t0, t1, straight) in sg.get('arrows', []):
                arrows.append({'from': a, 'to': b, 'color': col, 'label': '', 'head': 'arrow', **({'path': [a, b]} if straight else {})})
                arrow_times.append([-1000, -500] if t0 < 0 else [t0 * 1000, t1 * 1000])
            space = sg.get('space')
            shot = {'durMs': round(dur_ms, 3), 'from': {'center': sg['from'][0], 'qz': qz(sg['from'][1])},
                    'to': {'center': sg['to'][0], 'qz': qz(sg['to'][1])}, 'space': bool(space),
                    'drawStartMs': 270, 'drawEndMs': 1200, 'lateAtMs': round(sg.get('late_at', 0.45 * sg['s']) * 1000)}
            if space: shot['spaceFrac'] = space
            seg = f'{sid}_{k}'
            settings = dict(SETTINGS, globe=bool(plan.get('globe')))
            fc = {'type': 'FeatureCollection', 'name': f'Oil/Iran {seg}',
                  'historymap': {'version': 1, 'settings': settings, 'regions': regions, 'arrows': arrows, 'shot': shot},
                  'features': []}
            json.dump(fc, open(os.path.join(out, f'{seg}.geojson'), 'w'), indent=1, ensure_ascii=False)
            note = plan.get('note') if k >= plan.get('note_from', 0) else None
            manifest.append({
                'seg': seg, 'shot_id': sid, 'k': k, 'line': sh['line'], 'offset': offset, 'frames': n, 'shot_frames': total, 'srt_start': round(srt[sid][0], 3) if sid in srt else None,
                'file': f'historymap/{seg}.geojson', 'shot': shot, 'globe': settings['globe'], 'rise': bool(sg.get('rise')),
                'regions': [r['id'] for r in regions], 'narr': len(arrows),
                'arrow_times_ms': arrow_times,
                # straight (pipeline) arrows carry their label under the middle of the arrow, curved ones under the tail
                'arrows': [{'from': a, 'to': b, 'label': label, 'color': col, 'at': t0, 'end': t1,
                            'label_ll': [round((a[0] + b[0]) / 2, 4), round((a[1] + b[1]) / 2, 4)] if straight else a}
                           for (a, b, col, label, t0, t1, straight) in sg.get('arrows', [])],
                'pins': [{'name': nm, 'll': ll, 'style': st, 'at': at} for (nm, ll, st, at) in sg.get('pins', [])],
                'labels': [{'text': tx, 'll': ll, 'at': at} for (tx, ll, at) in sg.get('labels', [])],
                'note': note,
            })
            offset += n
    json.dump(manifest, open(os.path.join(out, 'manifest.json'), 'w'), indent=1, ensure_ascii=False)
    print(f'{len(PLAN)} map shots → {len(manifest)} segments in {os.path.relpath(out, root)}')


if __name__ == '__main__':
    main()
