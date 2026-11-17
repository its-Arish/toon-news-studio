# toon-news-studio

2D cartoon storytelling of the latest news stories — all drawn and animated in code (Python + Cairo + FFmpeg).

- **[STYLE.md](STYLE.md)** — the house style: pacing, characters, look, text, rules, workflow.
- `toonkit/` — the reusable kit
  - `core.py` — drawing primitives, easing, film grain + vignette
  - `rig.py` — cut-out stick-body rig with boiling ink lines + actions (walk, wave, point, shrug, shock, talk)
  - `scene.py` — camera, glows, labels, sparkles, main/side characters, captions, render pipeline
- `assets/` — character heads, fonts
- `episodes/<yyyy-mm-slug>/` — one folder per story: `script.txt` + `film.py` (shot list)

## Setup
```bash
pip install pycairo numpy pillow
mkdir -p ~/.fonts && cp assets/fonts/PatrickHand.ttf ~/.fonts/ && fc-cache -f
# ffmpeg must be installed
```

## Run an episode
```bash
python3 episodes/2026-11-pattinson-bond/film.py stills   # one still per shot → out/st_*.png
python3 episodes/2026-11-pattinson-bond/film.py render   # → out/preview.mp4
```

## New episode
Copy an episode folder, replace `SCRIPT` lines and write new `sh_*` shot functions; keep every shot 2–3 s (see STYLE.md).

## Episodes
| Episode | Status |
|---|---|
| 2026-11 The Entire History of Robert Pattinson, the seventh James Bond | first minute approved; waiting on voiceover |
