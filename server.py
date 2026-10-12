#!/usr/bin/env python3
"""Miftah Learning Corner stream overlay server.

Serves the OBS browser-source overlay and the track controller.
Run:  python3 server.py
Then: overlay -> http://localhost:8901/overlay   (add as OBS Browser Source, 1920x1080)
      control -> http://localhost:8901/control   (open in a browser; also works
                 from your phone on the same Wi-Fi via your PC's LAN IP)
"""
import json
import os
import urllib.parse
import urllib.request
import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.abspath(__file__))
PORT = 8901
P_LAT, P_LON = 39.9555, -75.2115  # Philadelphia
PRAYER_MARKS = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
_prayer_cache = {"date": None, "marks": []}


def load_prayer_times():
    """Fetch today's prayer times (ISNA method) once per day; [] on failure."""
    today = datetime.date.today().isoformat()
    if _prayer_cache["date"] == today and _prayer_cache["marks"]:
        return _prayer_cache["marks"]
    try:
        dd = datetime.date.today().strftime("%d-%m-%Y")
        url = (f"https://api.aladhan.com/v1/timings/{dd}"
               f"?latitude={P_LAT}&longitude={P_LON}&method=2")
        timings = json.load(urllib.request.urlopen(url, timeout=15))["data"]["timings"]
        marks = [{"name": n, "at": f"{today}T{timings[n].split(' ')[0]}:00"}
                 for n in PRAYER_MARKS]
        _prayer_cache.update(date=today, marks=marks)
    except Exception:
        pass
    return _prayer_cache["marks"]

tracks = json.load(open(os.path.join(BASE, "tracks.json"), encoding="utf-8"))
STATE = os.path.join(BASE, "state.json")


def load_orgs():
    return json.load(open(os.path.join(BASE, "orgs.json"), encoding="utf-8"))

try:
    index = json.load(open(STATE))["index"]
except Exception:
    index = 0
index = max(0, min(int(index), len(tracks) - 1))


def save():
    json.dump({"index": index}, open(STATE, "w"))


def read_file(name):
    with open(os.path.join(BASE, name), encoding="utf-8") as f:
        return f.read()


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, ctype="text/html"):
        b = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        global index
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/overlay"):
            self._send(read_file("overlay.html"))
        elif path == "/control":
            self._send(read_file("control.html"))
        elif path == "/player":
            self._send(read_file("player.html"))
        elif path == "/api/now":
            self._send(json.dumps(
                {"index": index, "total": len(tracks), "track": tracks[index]},
                ensure_ascii=False), "application/json")
        elif path == "/api/orgs":
            self._send(json.dumps(load_orgs(), ensure_ascii=False), "application/json")
        elif path == "/api/prayers":
            self._send(json.dumps(load_prayer_times()), "application/json")
        elif path == "/api/tracks":
            self._send(read_file("tracks.json"), "application/json")
        else:
            self.send_error(404)

    def do_POST(self):
        global index
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/next":
            index = (index + 1) % len(tracks)
        elif path == "/api/prev":
            index = (index - 1) % len(tracks)
        elif path == "/api/set":
            try:
                body = json.loads(self.rfile.read(
                    int(self.headers.get("Content-Length", 0)) or 0))
                i = int(body.get("index", index))
                index = max(0, min(i, len(tracks) - 1))
            except Exception:
                pass
        elif path == "/api/auto":
            # Player page reports what YouTube is actually playing.
            # Prefer the playlist index (matches fill order); fall back to
            # matching by video id (first occurrence wins on duplicates).
            try:
                body = json.loads(self.rfile.read(
                    int(self.headers.get("Content-Length", 0)) or 0))
                i = int(body.get("index", -1))
                if 0 <= i < len(tracks):
                    index = i
                else:
                    vid = body.get("video_id") or ""
                    for n, t in enumerate(tracks):
                        if t["id"] == vid:
                            index = n
                            break
            except Exception:
                pass
        else:
            self.send_error(404)
            return
        save()
        self._send(json.dumps(
            {"index": index, "total": len(tracks), "track": tracks[index]},
            ensure_ascii=False), "application/json")


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), H)
    print(f"Overlay: http://localhost:{PORT}/overlay")
    print(f"Control: http://localhost:{PORT}/control")
    print(f"{len(tracks)} tracks loaded, starting at #{index + 1}")
    srv.serve_forever()
