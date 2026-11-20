# Prompt for Claude Code (run on the Mac)

Copy everything inside the box into Claude Code, started in the folder that holds both repos (for example `~/Projects`).

```
You are working on the Toon News Studio episode "ARE OIL PRICES FINALLY DROPPING? WHAT WILL HAPPEN IN JANUARY? USA IRAN WAR".
Two repos are involved:
  - its-Arish/toon-news-studio  (branch episode/oil-iran-january) — the episode, the news-shot tool, the shot lists
  - its-Arish/naah              (branch america-historymap-tools) — History Map (vendor/historymap) and its recorder

Goal: make two sets of B-roll clips for the episode, (A) highlighted news-article clips and (B) History Map animated map clips,
and push them back to toon-news-studio. Do not change the script.

SETUP
1. Clone or update both repos. In toon-news-studio: git checkout episode/oil-iran-january && git pull.
   In naah: git fetch origin america-historymap-tools && git checkout america-historymap-tools && git pull.
   (History Map is only on that branch, not on main.)
2. Read toon-news-studio/STYLE.md, episodes/2026-11-oil-iran-january/notes.md, news_shots.json and maps.json.
   Read naah/vendor/historymap/README.md, naah/docs/sessions/2026-11-20-america-historymap-swap.md,
   naah/projects/america/tools/make_historymap_shots.py and record_historymap.mjs — they show the History Map
   project-file format and the recording method that already worked on this Mac.
3. pip install -r requirements.txt playwright && python3 -m playwright install chromium ; check ffmpeg is installed.
   (requirements.txt includes scipy, which the marker sound effects need.)
   Install the font: cp toon-news-studio/assets/fonts/PatrickHand.ttf ~/Library/Fonts/

PART A — NEWS-ARTICLE CLIPS
4. From toon-news-studio run:
     python3 tools/news_shots.py episodes/2026-11-oil-iran-january/news_shots.json
   Every clip plays in this order: the article appears whole (swoosh) and stays on screen ~1 s so the viewer sees
   the real news page and headline -> the camera pushes in to the paragraph -> a marker-cap click, then the yellow
   marker draws across the sentence line by line with a marker-stroke sound per line, the rest of the page dims ->
   hold ~0.9 s. The highlight is animated after the screenshot, never baked into the page.
   Output per shot in episodes/2026-11-oil-iran-january/news_shots/: <id>.mp4 (≈4 s, with sound),
   <id>_sfx.wav (the sound alone, same length, for the separate SFX track), <id>.png (final frame), plus report.json.
   All 26 news shots must end up as clips; none may be dropped without telling me why.
5. For every shot not "ok" in report.json:
   - Open news_shots/raw/<id>.png and look at it.
   - Paywall / sign-in / bot check: rerun that shot with
       python3 tools/news_shots.py <json> --only <id> --profile ~/.toon-news-chrome --headed --chrome
     If a sign-in page appears, stop and ask me to sign in in that window, then rerun.
   - Wording differs on the live page: copy the page's real sentence (same fact) into "highlight" in news_shots.json and rerun.
     Never highlight a sentence that says something different from the script line in "line".
   - Page gone or still blocked: mark it "skipped" with the reason in report.json and move on.
6. Check every clip: extract frames at 0.5 s and at the end (ffmpeg -ss) and look at them. Reject and redo any where
   the first frame isn't a readable news page, the marker lands on the wrong words, a pop-up or ad covers the text,
   or the page is blank/dark. To change only timing/look without reopening sites: python3 tools/news_shots.py <json> --reuse

PART B — HISTORY MAP CLIPS
7. Serve History Map: cd naah/vendor/historymap && python3 -m http.server 8743
8. For each shot in toon-news-studio/episodes/2026-11-oil-iran-january/maps.json, write a History Map project file
   (GeoJSON with a "historymap" member and a scripted "shot", same format make_historymap_shots.py writes) to
   toon-news-studio/episodes/2026-11-oil-iran-january/historymap/<id>.geojson, plus a manifest.json like the America one.
   Use: regions (iso3 + colour), pins, our labels, arrows (from/to, colour, label, when), camera moves, start from space
   where asked. Satellite style, map labels off. Keep the satellite layer — do not strip it.
   Pacing rule: something changes every 2–3 s (camera move, region fade, arrow draw, pin pop). If a shot is longer
   than ~3 s, split it into segments the way make_historymap_shots.py does.
   Durations: use "dur" from maps.json; if episodes/2026-11-oil-iran-january/voiceover.srt exists, time each map to its
   "line" in the SRT instead.
   Respect every "_check" note (e.g. carrier positions are illustrative: no ship names, generic label only).
9. Record each segment to MP4 using the same method as naah/projects/america/tools/record_historymap.mjs
   (Playwright driving Brave/Chrome on localhost:8743, 960×540 CSS at pixel ratio 2 → 1920×1080). Copy that script into
   toon-news-studio/tools/record_historymap.mjs and point it at this episode's manifest — don't edit the America project.
   Lessons from the America session: record only after map.areTilesLoaded() plus a 1–2 s settle (no dark first frames);
   check each file's length and retry any that come back near 0 s; if the recorder hangs after a download, reload the
   page and the segment.
10. Conform every clip to the house format: 1280×720, 30 fps, H.264 crf 18, exact frame count = dur × 30,
    then add grain + vignette and our Patrick Hand labels the same way tools/news_shots.py grades its frames.
    Output: episodes/2026-11-oil-iran-january/maps/<id>.mp4

FINISH
11. Write episodes/2026-11-oil-iran-january/BROLL.md: a table with id · script line · file · duration · status (ok / fixed / skipped + why).
12. Commit only the scripts, json, BROLL.md, the final .png stills and the final .mp4 clips (not raw/ screenshots,
    not historymap recordings before conform). If the clips are large, use Git LFS or tell me the total size before pushing.
    Push to branch episode/oil-iran-january.
13. Tell me: how many news clips and map clips are ready, which were skipped and why, and anything I need to do
    (sign in somewhere, approve a wording change).

Do not edit toonkit/, assets/characters/ or the script — the character rig and script are handled separately.

Rules: do not invent facts or change what a highlighted sentence says; real people only as name labels, no photos of
faces; keep each news clip short (one sentence + outlet name) — no full paragraphs; ask me before deleting anything.
```

## Sign in once (only if paywalls block shots)
```
python3 tools/news_shots.py episodes/2026-11-oil-iran-january/news_shots.json --only 23-bloomberg-dec11 --profile ~/.toon-news-chrome --headed --chrome
```
Sign in when the window opens; the profile keeps the cookies for later runs.
