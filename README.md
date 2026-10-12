# Miftah Stream Overlay — Now Playing + News Ticker

A news-style bottom bar for your Twitch stream. It cycles every 8 seconds between:

1. **♪ NOW PLAYING** — the current track from your AICP YouTube playlist order
   (nasheed title + artist, or the Islamic video / Ahlan Arabic / class title)
2. **FOLLOW — Youth of Truth** — find your chapter @youthoftruth
3. **LEARN — DigiTIES** — the Islamic education school (digities.org)
4. **WATCH — Evidence and Proofs** — @evidenceandproofs
5. **LEARN — Ahlan Arabic** — beginning Arabic podcast by Kuttab Academy

The right side of the bar shows the current time, the current prayer, and a
live countdown to the next prayer (Philadelphia, ISNA method — needs internet).

## Option A — Easy setup (no Python)

Use the single file `miftah-overlay-standalone.html`. The YouTube video player,
the ticker, and the prayer times are all inside this one page — nothing to
install, no server to run. The video fills the screen with the ticker as a
lower-third over it, like a news channel.

1. In Streamlabs Desktop (or OBS): Sources → **+** → **Browser Source** →
   check **Local file** → Browse → pick `miftah-overlay-standalone.html` →
   width 1920, height 1080 → Add Source. Drag it to the bottom of your canvas.
2. Make sure the browser source's audio is enabled so the nasheeds are heard
   on stream (in OBS: source properties → check "Control audio via OBS", then
   it appears in the audio mixer).
3. Right-click the source → **Interact**. Hover near the top of the window to
   reveal Prev / Play / Next, then press **Play**. The playlist starts and the
   ticker follows each video automatically. Close the Interact window.
4. To skip a track mid-stream: right-click the source → Interact → Next.

The org promos come from your Canva "Full Ad Reel". To change them, edit
`orgs.json` and rebuild the single file with `python3 build_standalone.py`
(or ask me to rebuild it).

## Option B — With phone controller (needs Python)

If you'd rather tap Next from your phone instead of using Interact, run the
little server: open a terminal in this folder and run `python3 server.py`
(`python server.py` on Windows; install Python from python.org first, checking
"Add python to PATH"). Then:

- Overlay: add a Browser Source with URL `http://localhost:8901/overlay`
  (1920x1080) — same bar, same ticker.
- Auto-play: open `http://localhost:8901/player` in your browser and press
  play — the overlay follows each video by itself.
- Tap controller: `http://localhost:8901/control`, or from your phone on the
  same Wi-Fi via `http://<your-PC-IP>:8901/control` (find the IP with
  `ipconfig` on Windows). Whichever updates last (player or taps) wins.

## Files

- `miftah-overlay-standalone.html` — **the easy one-file overlay** (Option A)
- `standalone-template.html` + `build_standalone.py` — rebuild the single file
  after editing tracks/orgs
- `server.py` — the tiny server for Option B (Python standard library only)
- `overlay.html` — the ticker bar served by the server (Option B)
- `control.html` — the tap-to-advance controller (Option B)
- `player.html` — auto-following playlist player (Option B)
- `tracks.json` — all 966 tracks in your AICP playlist order
- `orgs.json` — the cycling org promos (edit me, then rebuild the single file)
- `state.json` — your current track position (auto-saved, Option B)
