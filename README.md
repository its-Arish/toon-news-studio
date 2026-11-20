# toon-news-studio

2D cartoon storytelling of the latest news stories — all drawn and animated in code (Python + Cairo + FFmpeg).

- **[STYLE.md](STYLE.md)** — the house style: pacing, characters, look, text, rules, workflow.
- `toonkit/` — the reusable kit
  - `core.py` — drawing primitives, easing, film grain + vignette
  - `rig.py` — cut-out stick-body rig with boiling ink lines + actions (walk, wave, point, shrug, shock, talk)
  - `scene.py` — camera, glows, labels, sparkles, main/side characters, captions, render pipeline
  - `face.py` — live facial expressions on the hand-drawn head (16 expressions, blinking, talking)
  - `kit.py` — actors with outfits, side characters, crowds, ~50 props, ~30 backgrounds, auto-camera
  - `sfx.py` — synthesized sound effects and the full-length SFX track
- `tools/split_face.py` — turns a drawn head into blank face + eye/brow sprites
- `tools/news_shots.py` — opens news articles, highlights the quoted sentence, outputs house-style stills + 2.5 s push-in clips (run on a machine with internet; see an episode's `news_shots.json`)
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
python3 episodes/2026-11-pattinson-bond/film.py render   # → out/preview.mp4 (first-minute preview)
python3 episodes/2026-11-pattinson-bond/full.py stills   # full episode, one still per shot
python3 episodes/2026-11-pattinson-bond/full.py render   # → out/full_video.mp4
```

## New episode
Copy an episode folder, replace `SCRIPT` lines and write new `sh_*` shot functions; keep every shot 2–3 s (see STYLE.md).

## Episodes
| Episode | Status |
|---|---|
| 2026-11 The Entire History of Robert Pattinson, the seventh James Bond | full 12-min episode rendered (247 shots), timed to voiceover |
| 2026-11 Are Oil Prices Finally Dropping? What Will Happen in January? USA Iran War | script v2 + news-shot and History Map lists; B-roll via `CLAUDE_CODE_PROMPT.md` |
