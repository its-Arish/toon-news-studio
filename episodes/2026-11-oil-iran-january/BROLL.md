# B-roll: ARE OIL PRICES FINALLY DROPPING? WHAT WILL HAPPEN IN JANUARY? USA IRAN WAR

Made with `tools/news_shots.py` (news clips) and `tools/make_historymap_maps.py` → `tools/record_historymap.mjs` → `tools/conform_maps.py` (History Map clips).
All clips are 1280×720, 30 fps, H.264 crf 18, with a separate `<id>_sfx.wav` sound track (also muxed into the mp4) and a `<id>.png` still.

Rules kept: no fact invented, highlighted sentences are the page's own words and say the same thing as the script line; every photo/video on a page is blurred (no faces of real people, byline headshots included); one sentence + outlet name per clip.

## News clips

| id | script line | file | duration | status |
|---|---|---|---|---|
| 01-npr-epstein-3m | the Justice Department released more than three million pages of the Epstein files | `news_shots/01-npr-epstein-3m.mp4` | 4.00 s | **fixed** — highlight changed to the page's real wording, same fact: "released more than 3 million pages, including more than 2,000 videos and 180,000 images"; matching now ignores whitespace so a sentence across a link boundary is found |
| 02-npr-not-wrongdoing | Being named in those files is not proof of a crime | `news_shots/02-npr-not-wrongdoing.mp4` | 4.00 s | **ok** |
| 03-indy-clinton-hours | They began just hours after Bill Clinton had testified to Congress about Epstein | — | — | **skipped** — page gone: the Independent/AOL article now returns "the page you're looking for does not exist" |
| 04-wrap-massie | bombing a country on the other side of the world would not make the Epstein files go away | `news_shots/04-wrap-massie.mp4` | 4.00 s | **fixed** — sentence sat inside a collapsed "read more" block and a newsletter sign-up box covered it; tool now opens clipped blocks and hides inline newsletter boxes |
| 05-newsweek-poll | One poll in March, from a left-leaning group, found more than half of voters | `news_shots/05-newsweek-poll.mp4` | 4.00 s | **fixed** — marker missed the words after a late layout shift; tool now re-measures until the sentence stops moving |
| 06-wh-true-morons | The White House called that idea ridiculous | `news_shots/06-wh-true-morons.mp4` | 4.00 s | **ok** |
| 07-abc-oil-126 | By the end of April, oil hit one hundred and twenty-six dollars | `news_shots/07-abc-oil-126.mp4` | 4.00 s | **ok** — headline highlight; the video player on the page is a black box with a loading spinner |
| 08-wusf-bondi | The Attorney General, Pam Bondi, was pushed out in April | `news_shots/08-wusf-bondi.mp4` | 4.00 s | **ok** |
| 09-pbs-63pct | sixty-three percent of Americans blamed the President for high gas prices | `news_shots/09-pbs-63pct.mp4` | 4.00 s | **fixed** — first take was not scrolled to the sentence (marker off-screen); fixed scroll |
| 10-yahoo-senate-9 | flipping nine seats, the most for any party in nearly seventy years | `news_shots/10-yahoo-senate-9.mp4` | 4.00 s | **fixed** — first takes landed on the Yahoo homepage (Escape key navigated away); Escape is now pressed only when a dialog is open |
| 11-reuters-71pct | seventy-one percent of Americans want Congress to pass a law ending it | `news_shots/11-reuters-71pct.mp4` | 4.00 s | **ok** — clip from the first run, checked; later re-runs get a Cloudflare bot check |
| 12-cnbc-brent-90 | Oil dropped below ninety dollars for the first time since August | `news_shots/12-cnbc-brent-90.mp4` | 4.00 s | **ok** |
| 13-aaa-under-4 | Gas fell under four | `news_shots/13-aaa-under-4.mp4` | 4.00 s | **ok** |
| 14-cnbc-80pct | Gulf crude exports were back above eighty percent of their pre-war level | `news_shots/14-cnbc-80pct.mp4` | 4.00 s | **ok** |
| 15-spg-surplus | supply is now bigger than demand for the first time since the war began | `news_shots/15-spg-surplus.mp4` | 4.03 s | **fixed** — S&P blocks automated Chromium (Akamai "Access Denied"); captured in Brave (headed). 3 lines, so it holds to 4.03 s |
| 16-gcaptain-65pct | Ship traffic through Hormuz is still about sixty-five percent below normal | `news_shots/16-gcaptain-65pct.mp4` | 4.00 s | **fixed** — first take blurred the whole article (wrapper with a background image) and the marker drifted; both fixed |
| 17-aj-third-carrier | A third American aircraft carrier just arrived in the region | `news_shots/17-aj-third-carrier.mp4` | 4.00 s | **fixed** — journalist byline headshot was sharp; now blurred (byline photos always are) |
| 18-axios-massie-218 | Thomas Massie got the two hundred and eighteen signatures | `news_shots/18-axios-massie-218.mp4` | 4.00 s | **ok** — clip from the first run, checked; later re-runs get a Cloudflare bot check |
| 19-yahoo-greene | Marjorie Taylor Greene ... claimed that he personally blocked the files | `news_shots/19-yahoo-greene.mp4` | 4.00 s | **fixed** — same Yahoo homepage issue as 10, fixed |
| 20-npr-subpoena | Subpoenas. They can force people to testify and hand over documents | `news_shots/20-npr-subpoena.mp4` | 4.00 s | **fixed** — highlight changed to the page's real wording, same fact: "the ability to subpoena records for review and compel individuals to testify before lawmakers" |
| 21-cbs-meeks | in January he will bring a war powers resolution | `news_shots/21-cbs-meeks.mp4` | 4.00 s | **ok** |
| 22-cbs-new-year | we will see what happens after the new year starts | `news_shots/22-cbs-new-year.mp4` | 4.00 s | **ok** |
| 23-bloomberg-dec11 | on the 11th of December, the government runs out of money | — | — | **skipped** — Bloomberg "Press & Hold" bot check + paywall (tried Playwright, Brave and Chrome with a profile). Needs you to pass the check / sign in, then rerun (see below). Note: this URL is the "Brent crude falls below $90" article; check it really contains the 11 December funding sentence |
| 24-bnp-78 | BNP Paribas expects about seventy-eight dollars a barrel | `news_shots/24-bnp-78.mp4` | 4.00 s | **ok** |
| 25-eia-diesel | diesel to average about five dollars a gallon next year | `news_shots/25-eia-diesel.mp4` | 4.00 s | **fixed** — first take was not scrolled to the sentence (marker off-screen); fixed scroll |
| 26-ap-thanksgiving | This Thanksgiving is already on track to be the most expensive ever at the pump | `news_shots/26-ap-thanksgiving.mp4` | 4.00 s | **ok** |

**24 of 26 news clips ready.**

## Map clips (History Map, satellite, map labels off)

| id | script line | file | duration | status |
|---|---|---|---|---|
| map01-strikes | on the 28th of February, the United States and Israel launched strikes on Iran | `maps/map01-strikes.mp4` | 5.23 s (157 frames; VO 1:03.45) | **ok** — starts from space (globe dive), Tehran pin, 28 FEB arrow Israel→Tehran on "Israel launched strikes"; 2 segments |
| map02-hormuz | It shut the Strait of Hormuz, the narrow strip of water between Iran and Oman that carries close to a fifth of the world's oil | `maps/map02-hormuz.mp4` | 7.43 s (223 frames; VO 2:00.40) | **fixed** — Iran, Hormuz pin on "Hormuz", Oman fades in on "Oman", "~1/5 OF THE WORLD'S OIL" on "fifth". Oman drawn green instead of amber (amber vanished over desert on satellite); 3 segments |
| map03-blockade | In July, the US Navy put its blockade of Iranian ports back in place, and Iran kept hitting ships | `maps/map03-blockade.mp4` | 6.40 s (192 frames; VO 2:31.08) | **ok** — "US BLOCKADE · 14 JULY" on "blockade", Bandar Abbas + Kharg Island pins on "ports"; 3 segments |
| map04-escape | Tankers started slipping through the southern side of the strait ... pipelines that skip Hormuz completely | `maps/map04-escape.mp4` | 11.03 s (331 frames; VO 3:57.76) | **fixed** — TRACKERS OFF route, "GUIDED BY US FORCES" (spoken in the VO between the two parts of the maps.json line), Saudi/UAE on "Gulf", pipelines on "pipelines", "PIPELINES SKIP HORMUZ". Saudi Arabia/UAE green instead of amber; pipeline label moved off its arrow; 4 segments |
| map05-carriers | A third American aircraft carrier just arrived in the region | `maps/map05-carriers.mp4` | 3.60 s (108 frames; VO 4:39.68) | **ok** — 3 carrier markers + "3 US CARRIERS IN THE REGION"; note "POSITIONS ILLUSTRATIVE" (exact positions are not public); 2 segments |
| map06-tankers-hit | Ship traffic through Hormuz is still about sixty-five percent below normal. Tankers are still being hit. | `maps/map06-tankers-hit.mp4` | 6.07 s (182 frames; VO 4:33.60) | **ok** — "TRAFFIC −65%" on "65", "TANKER HIT · 20 NOV" on "tankers" with note "APPROXIMATE LOCATION"; 3 segments |
| map07-three-roads | So what happens to oil in January? It comes down to three roads. | `maps/map07-three-roads.mp4` | 4.03 s (121 frames; VO 7:04.12) | **ok** — Iran/USA, rises out to the globe; 2 segments |

**7 of 7 map clips ready.**

History Map project files (load in History Map → open file): `historymap/<id>_<n>.geojson`, one per segment, plus `historymap/manifest.json` (timing, pins, labels, arrows per segment). Each segment is ≤ 3 s so something changes every 2–3 s. Timing follows `voiceover.srt`: each clip lasts exactly as long as its line is spoken (start time in the VO is given above), and pins, labels and arrows land on their spoken words.

## To do by hand

- **23 Bloomberg:** open Chrome with the tool profile, pass the "Press & Hold" check (and sign in if you have a subscription), close it, then run:  
  `python3 tools/news_shots.py episodes/2026-11-oil-iran-january/news_shots.json --only 23-bloomberg-dec11 --profile ~/.toon-news-chrome --headed --chrome`
- **03 Independent/AOL:** the article is gone. Give a replacement URL with the same fact, or drop the shot.
- History Map recording needs the scripted-shot support in `naah/vendor/historymap/app.js`, which is still uncommitted in the naah working tree (not on `america-historymap-tools`).
