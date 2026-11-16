"""Static HTML previews of a few pages, rendered to PNG with headless Microsoft Edge.

The app is run with Streamlit AppTest (no browser); every st.html block it produced is written, with the theme
CSS, into previews/<name>.html, and Edge takes a screenshot (previews/<name>.png). Streamlit's own widgets
(radio buttons, select boxes, the sidebar) are not part of a static preview; the live compass is added as its
static drawing. Headless Edge crashes now and then, so each screenshot is retried up to 7 times,
with a fresh profile folder each time. `python tools/render_previews.py name ...` renders only those cases.
Run from the app folder:  python tools/render_previews.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
os.environ.setdefault("SKY_EPHEM_DIR", r"C:\AfterglowApp\ephem")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = os.path.join(HERE, "previews")

CASES = [
    ("today_latin", "Today", "latin_catholic", {"_now_override": "2026-11-15T10:30"}, 1500),
    ("today_coptic_nativity_2028", "Today", "coptic_orthodox", {"_now_override": "2028-01-07T10:30"}, 1500),
    ("month_russian_julian", "Month", "russian_orthodox", {"_now_override": "2026-04-12T10:00"}, 1500),
    ("paschalion", "Paschalion", "latin_catholic", {"_now_override": "2026-11-15T10:00", "pa_n": 12}, 1700),
    ("hours_byzantine", "Hours", "constantinople", {"_now_override": "2026-11-15T10:00"}, 1300),
    ("compare", "Compare", "latin_catholic", {"_now_override": "2028-01-07T10:00"}, 1200),
]


def page_html(name, page, trad, state):
    from streamlit.testing.v1 import AppTest
    import sects
    import theme
    import orient_live
    p = sects.preset(trad)
    at = AppTest.from_file(os.path.join(HERE, "app.py"), default_timeout=120)
    s = {"tradition": trad, "communion": sects.get(trad)["communion"], "cal": p["fixed_calendar"],
         "rule": p["paschalion"], "lang": p["lang"], "hours": p["hours_system"], "page": page}
    s.update(state)
    for k, v in s.items():
        at.session_state[k] = v
    at.run()
    assert not at.exception, [e.message for e in at.exception]
    blocks = [h.proto.body for h in at.get("html")]
    css = [b for b in blocks if b.lstrip().startswith("<style")]
    body = [b for b in blocks if not b.lstrip().startswith("<style")]
    if page == "Today":
        pl = at.session_state["place"]
        body.insert(len(body) - 1, orient_live._html(90.0, "east", pl.get("name", ""), None,
                                                     orient_live.declination(pl["lat"], pl["lon"]), 170,
                                                     "Face east · ad orientem"))
    return ("<!doctype html><html><head><meta charset='utf-8'>" + "".join(css) +
            f"<style>body{{margin:0;background:{theme.BG};}} .wrap{{max-width:1240px;margin:0 auto;padding:18px 26px;"
            f"color:{theme.TEXT};font-family:{theme.SERIF}}}</style></head><body><div class='stApp'><div class='wrap'>"
            + "".join(f"<div style='margin-bottom:.6rem'>{b}</div>" for b in body) + "</div></div></body></html>")


def shot(html_path, png_path, height):
    for attempt in range(7):
        profile = tempfile.mkdtemp(prefix="px_edge_")   # Edge needs a writable profile folder of its own here
        if os.path.exists(png_path):
            os.remove(png_path)
        try:
            subprocess.run([EDGE, "--no-sandbox", "--disable-features=NetworkServiceSandbox", "--headless=new",
                            "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={profile}", f"--window-size=1280,{height}",
                            f"--screenshot={png_path}", "file:///" + html_path.replace(os.sep, "/")],
                           capture_output=True, timeout=90)
        except subprocess.TimeoutExpired:
            pass
        shutil.rmtree(profile, ignore_errors=True)   # do not leave profile folders behind (they fill the disk)
        if os.path.exists(png_path) and os.path.getsize(png_path) > 5000:
            return attempt + 1
        time.sleep(2)
    return 0


def main():
    os.makedirs(OUT, exist_ok=True)
    only = set(sys.argv[1:])
    for name, page, trad, state, h in CASES:
        if only and name not in only:
            continue
        hp = os.path.join(OUT, name + ".html")
        with open(hp, "w", encoding="utf-8") as f:
            f.write(page_html(name, page, trad, state))
        n = shot(hp, os.path.join(OUT, name + ".png"), h)
        print(f"{name}: {'ok after ' + str(n) + ' attempt(s)' if n else 'FAILED'}", flush=True)


if __name__ == "__main__":
    main()
