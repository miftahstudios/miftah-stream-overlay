#!/usr/bin/env python3
"""Build the standalone single-file overlay from the template.

Inlines tracks.json (966 tracks) and orgs.json so the file works with no
server: open it directly as an OBS/Streamlabs Browser Source (Local file).
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
tpl = open(os.path.join(BASE, "standalone-template.html"), encoding="utf-8").read()
tracks = json.load(open(os.path.join(BASE, "tracks.json"), encoding="utf-8"))
orgs = json.load(open(os.path.join(BASE, "orgs.json"), encoding="utf-8"))

# Slim the track objects to what the overlay displays.
slim = [{"id": t["id"], "title": t["title"], "sub": t.get("sub", ""),
         "kind": t.get("kind", "")} for t in tracks]

out = tpl.replace("/*__TRACKS__*/", json.dumps(slim, ensure_ascii=False))
out = out.replace("/*__ORGS__*/", json.dumps(orgs, ensure_ascii=False))
p = os.path.join(BASE, "miftah-overlay-standalone.html")
open(p, "w", encoding="utf-8").write(out)
print(f"wrote {p} ({len(out)//1024} KB, {len(slim)} tracks)")
