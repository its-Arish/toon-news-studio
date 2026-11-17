# Toon News Studio — Style Guide

Latest news stories told as 2D cartoon storytelling. Inspired by fast cartoon-explainer channels — **style only**: our stories, our characters.

## 1. Pacing (the most important rule)
- **Something changes on screen every 2–3 seconds.** Attention spans are short.
- Change ≠ only zoom. Rotate through:
  - **Cuts** to a new angle of the same set (wide → close-up → over-the-shoulder → cut-in on a prop)
  - **Camera moves**: pan/track with a walking character, slide sideways, slow push-in, pull-out
  - **Snap zoom** onto a key object (a number, a chart, a face)
  - **Dutch tilt** (camera rotated 2–5°) for drama or unease
  - **Shake** for shock moments
  - **Pop-ins**: labels, year tags, numbers, props bouncing in (`ease_out_back`)
  - **Things drawing on**: charts, routes, maps, circles on calendars
- No shot runs longer than ~3 s without an internal camera change.
- **Typed title cards** (white handwriting on black) for the episode title and chapter breaks.
- Never repeat the same kind of change three times in a row.

## 2. Characters
- **Few main characters, reused across episodes.** Count varies per story (one, two or several).
- **Main character** = hand-drawn caricature **head** (PNG, transparent) on a **coded stick body**.
  - Head PNG lives in `assets/characters/<name>/head.png`, with its neck pivot point noted in code.
  - Body: 2-bone arms and legs (elbows/knees bend), 3-prong fork hands, outward feet (front view) or forward feet (side view).
  - Wanted head variants for full acting: eyes closed, 3–4 mouth shapes, surprised, worried/sad, angry, side profile. Same drawing, only the face changes.
- **Side characters** = coded round heads (dot eyes, small smile, blush, hair cap; `style="short"` or `"long"`), same stick body, head scale 1.4 so they match the main head size.
- **Anonymous groups** = black suit silhouettes (`suit_figure`) or crowds of coded heads.
- **Other real people** in a story appear as generic coded figures with a **name label** — no drawn likeness.
- Actions available (`toonkit/rig.py`): `A_rest`, `A_talk`, `A_walk`, `A_wave`, `A_point`, `A_shrug`, `A_shock`; blend between with `lerpP`; lie down / fall with `person(..., rot=...)`; masks/props drawn over the head.

## 3. Look
- **Ink**: near-black outlines, thick (8 px at rig scale); lines **boil** (re-jitter every 4 frames, ±1.6 px) so they feel hand-inked.
- **Colour**: flat fills, vertical gradient skies/walls, warm paper tones for maps and explainer boards.
- **Light**: soft radial glows, spotlight cones, lamp light behind characters in dark scenes (keeps black lines readable).
- **Grade**: film grain + vignette on every frame; grayscale for storm / flashback / "went mad" moments.
- **Props are simple and bold**: calendars, trophies, cars, buildings, gauges ("fame-o-meter"), road maps with icon stops.

## 4. Text
- Font: **Patrick Hand** (`assets/fonts/PatrickHand.ttf`).
- **Labels**: white (or tinted) rounded boxes with ink outline, slight rotation, bounce in. Use for names ("MUM: CLARE"), years ("2008"), punchlines ("NOT EVEN CLOSE").
- **Captions**: bottom-centre, white text on a dark rounded box, max ~980 px wide, wrap to 2 lines.

## 5. Rules for real news
- **Fact-check the script against current sources before animating.** Fix dates, quotes and attributions.
- **No copyrighted characters, logos or signature costumes** (superhero suits/logos, 007 gun barrel, film-franchise characters). Show those moments with our own stand-ins: a plain mask in a rainy red city, a tuxedo + martini, a hedge maze + trophy, a moonlit forest with sparkles.

## 6. Deliverables
- Video + captions + SFX in one file; voiceover as a separate file; music and SFX also as separate full-length tracks of identical length.
- 1280×720, 30 fps, H.264 (crf 18).

## 7. Workflow
1. Script → fact-check → corrected script.
2. Voiceover (Gemini TTS) → line timings (until then: placeholder timing at 2.6 words/s, `caps_from_lines`).
3. Shot list keyed to script lines: `SHOTS = [(start_time, shot_fn, grayscale), ...]`, 2–3 s each.
4. Render **stills** at the busiest moment of every shot and look at them.
5. Render each shot to its own file in parallel, join with the concat demuxer (`render_all`).
6. Send a 1-minute preview for approval before the full episode.
