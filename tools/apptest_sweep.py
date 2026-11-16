"""Headless sweep of Sky Paschalion with Streamlit AppTest.

Run from the app folder:   python tools/apptest_sweep.py        (conda env 'luach' here; any env with requirements.txt)
Each batch of cases runs in a fresh subprocess (sys.executable) with a timeout of 170 s, so a hung run cannot
stall the sweep. AppTest.from_file needs an ABSOLUTE path. Every case must finish with 0 exceptions; a few cases
also check the rendered text (Coptic Nativity 28 vs 29 Koiak, Pascha dates, 'Use' button, outside-ephemeris note).
Results: tools/apptest_results.json.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(HERE, "app.py")
sys.path.insert(0, HERE)
BATCH = 12
TIMEOUT = 170


def build_cases() -> list[dict]:
    import sects
    cases = []

    def add(name, page, trad="latin_catholic", state=None, checks=None, click=None):
        p = sects.preset(trad)
        s = {"tradition": trad, "communion": sects.get(trad)["communion"], "cal": p["fixed_calendar"],
             "rule": p["paschalion"], "lang": p["lang"], "hours": p["hours_system"], "page": page}
        s.update(state or {})
        cases.append({"name": name, "state": s, "checks": checks or [], "click": click})

    # 1. Today x every tradition (55), each with its own preset
    for t in sects.TRADITIONS:
        add(f"today/{t['key']}", "Today", t["key"])
    # 2. every page with the default and with an Eastern, Oriental and East Syriac church
    pages = ["Today", "Month", "Year", "Feasts", "Paschalion", "Hours", "Compare", "Traditions", "How", "About"]
    for pg in pages:
        for tk in ("latin_catholic", "russian_orthodox", "coptic_orthodox", "assyrian_church_of_the_east"):
            add(f"page/{pg}/{tk}", pg, tk)
    # 3. every calendar on Month, Year, Today and Feasts (with a Byzantine-rite and an Alexandrian church)
    for c in ("gregorian", "julian", "revised_julian", "coptic", "ethiopian", "byzantine"):
        for pg in ("Month", "Year", "Today", "Feasts"):
            add(f"cal/{c}/{pg}", pg, "constantinople", {"cal": c})
        add(f"cal/{c}/Month/coptic", "Month", "coptic_orthodox", {"cal": c})
        add(f"cal/{c}/Month/phone", "Month", "latin_catholic", {"cal": c, "phone_layout": True})
    # 4. every Paschalion rule on Paschalion, Year, Month, Today
    for r in ("western", "eastern", "astronomical"):
        for pg in ("Paschalion", "Year", "Month", "Today"):
            add(f"rule/{r}/{pg}", pg, "latin_catholic", {"rule": r})
    # 5. every hours system on Hours and Today (London)
    for h in ("roman", "byzantine", "coptic", "ethiopian", "armenian", "west_syriac", "east_syriac"):
        add(f"hours/{h}/Hours", "Hours", "latin_catholic", {"hours": h})
        add(f"hours/{h}/Today", "Today", "latin_catholic", {"hours": h})
    # 6. every display language (with a church that lists it) on Today, Month, Year, Hours, Feasts
    seen = {}
    for t in sects.TRADITIONS:
        for lg in t["liturgical_languages"]:
            seen.setdefault(lg, t["key"])
    for lg, tk in sorted(seen.items()):
        for pg in ("Today", "Month", "Year", "Hours", "Feasts"):
            add(f"lang/{lg}/{pg}", pg, tk, {"lang": lg})
    # 7. astronomical Pascha outside 1850-2149
    for pg in ("Today", "Month", "Year", "Feasts"):
        add(f"outside/2200/{pg}", pg, "russian_orthodox", {"rule": "astronomical", "_now_override": "2200-04-01T10:00"},
            checks=["not available for 2200"] if pg in ("Year", "Feasts", "Month") else [])
    add("edge/2149-12-20/Today", "Today", "latin_catholic", {"_now_override": "2149-12-20T10:00"})
    add("edge/1850-01-05/Today", "Today", "latin_catholic", {"_now_override": "1850-01-05T10:00"},
        checks=["not shown for this date"])
    add("outside/paschalion-range", "Paschalion", "latin_catholic", {"pa_y0": 2140, "pa_n": 20, "pa_yd": 2150},
        checks=["unavailable (outside 1850–2149)", "Unavailable for 2150"])
    add("outside/paschalion-1700", "Paschalion", "latin_catholic", {"pa_y0": 1700, "pa_n": 10, "pa_yd": 1700})
    # 8. polar place (Tromsø): midnight Sun and polar night, every hours system
    troms = {"name": "Tromsø", "country": "NO", "lat": 69.6492, "lon": 18.9553, "tz": "Europe/Oslo", "label": "Tromsø",
             "src": "manual"}
    for when in ("2026-06-21T12:00", "2026-12-21T12:00"):
        for h in ("roman", "byzantine", "coptic", "ethiopian", "armenian", "west_syriac", "east_syriac"):
            add(f"polar/{when[:10]}/{h}", "Hours", "latin_catholic",
                {"hours": h, "place": troms, "place_src": "manual", "_now_override": when,
                 "hours_date": when[:10]}, checks=["Polar"])
        add(f"polar/{when[:10]}/Today", "Today", "latin_catholic",
            {"place": troms, "place_src": "manual", "_now_override": when})
    # 9. fixed dates
    for tk in ("latin_catholic", "constantinople", "russian_orthodox", "coptic_orthodox", "armenian_etchmiadzin"):
        add(f"pascha2025/{tk}", "Today", tk, {"_now_override": "2025-04-20T10:00"}, checks=["Christ is risen"])
    add("pascha2026/western", "Today", "latin_catholic", {"_now_override": "2026-04-05T10:00"}, checks=["Christ is risen"])
    add("pascha2026/eastern", "Today", "russian_orthodox", {"_now_override": "2026-04-12T10:00"}, checks=["Christ is risen"])
    add("pascha2026/eastern-not-western", "Today", "russian_orthodox", {"_now_override": "2026-04-05T10:00"},
        checks=["(in 7 days)"])
    add("coptic-nativity/2027", "Today", "coptic_orthodox", {"_now_override": "2027-01-07T10:00"},
        checks=["29 Koiak", "Nativity of Christ"])
    add("coptic-nativity/2028", "Today", "coptic_orthodox", {"_now_override": "2028-01-07T10:00"},
        checks=["28 Koiak", "Nativity of Christ"])
    add("ethiopian-genna/2028", "Today", "ethiopian_orthodox", {"_now_override": "2028-01-07T10:00"},
        checks=["28 Tahsas"])
    add("compare/2028-01-07", "Compare", "latin_catholic", {"_now_override": "2028-01-07T10:00"}, checks=["28 Koiak"])
    # 10. interactions
    add("click/use-coptic", "Traditions", "latin_catholic", click="use_coptic_orthodox",
        checks=["state:tradition=coptic_orthodox", "state:cal=coptic", "state:rule=eastern"])
    add("click/month-next", "Month", "latin_catholic", {"_now_override": "2026-12-15T10:00"}, click="mon_next",
        checks=["January"])
    add("click/month-prev-coptic", "Month", "coptic_orthodox", {"_now_override": "2026-09-12T10:00"}, click="mon_prev")
    add("click/restore", "Today", "latin_catholic", {"rule": "eastern"}, click="restore", checks=["state:rule=western"])
    for tgt in ("east", "jerusalem", "sunrise"):
        add(f"compass/{tgt}", "Today", "latin_catholic", {"orient_target": tgt})
    return cases


WORKER = r"""
import json, os, re, sys, time, traceback
from datetime import date
os.environ.setdefault("SKY_EPHEM_DIR", r"C:\AfterglowApp\ephem")
from streamlit.testing.v1 import AppTest
APP, cases = sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8"))
out = []
def text_of(at):
    parts = []
    for h in at.get("html"):
        b = h.proto.body
        if b.lstrip().startswith("<style"):
            continue
        b = re.sub(r"<svg.*?</svg>", " ", b, flags=re.S)
        parts.append(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", b)))
    for m in list(at.markdown) + list(at.caption):
        parts.append(m.value)
    return " ".join(parts)
for c in cases:
    t0 = time.time()
    rec = {"name": c["name"], "exceptions": [], "failed_checks": []}
    try:
        at = AppTest.from_file(APP, default_timeout=120)
        for k, v in c["state"].items():
            if k in ("hours_date", "cmp_date") and isinstance(v, str):
                v = date.fromisoformat(v)
            at.session_state[k] = v
        at.run()
        if c.get("click"):
            at.button(key=c["click"]).click().run()
        rec["exceptions"] = [str(e.message)[:400] for e in at.exception]
        rec["errors"] = [str(e.value)[:200] for e in at.error]
        txt = text_of(at)
        for chk in c["checks"]:
            if chk.startswith("state:"):
                k, v = chk[6:].split("=", 1)
                if str(at.session_state[k]) != v:
                    rec["failed_checks"].append(chk + " got " + str(at.session_state[k]))
            elif chk not in txt:
                rec["failed_checks"].append(chk)
    except Exception as ex:
        rec["exceptions"].append("harness: " + repr(ex)[:400] + " " + traceback.format_exc()[-600:])
    rec["sec"] = round(time.time() - t0, 2)
    out.append(rec)
print("RESULT" + json.dumps(out))
"""


def main():
    cases = build_cases()
    wpath = os.path.join(HERE, "tools", "_sweep_worker.py")
    with open(wpath, "w", encoding="utf-8") as f:
        f.write(WORKER)
    results, t0 = [], time.time()
    for i in range(0, len(cases), BATCH):
        chunk = cases[i:i + BATCH]
        cpath = os.path.join(HERE, "tools", f"_sweep_cases_{i}.json")
        with open(cpath, "w", encoding="utf-8") as f:
            json.dump(chunk, f)
        try:
            r = subprocess.run([sys.executable, wpath, APP, cpath], capture_output=True, text=True, timeout=TIMEOUT,
                               encoding="utf-8", errors="replace", cwd=HERE)
            line = next((l for l in r.stdout.splitlines() if l.startswith("RESULT")), None)
            if line is None:
                results += [{"name": c["name"], "exceptions": ["worker died: " + r.stderr[-500:]], "failed_checks": []}
                            for c in chunk]
            else:
                results += json.loads(line[6:])
        except subprocess.TimeoutExpired:
            results += [{"name": c["name"], "exceptions": [f"timeout > {TIMEOUT}s (batch)"], "failed_checks": []}
                        for c in chunk]
        finally:
            os.remove(cpath)
        done = len(results)
        print(f"{done}/{len(cases)} runs, {sum(1 for r in results if r['exceptions'])} with exceptions, "
              f"{time.time() - t0:.0f}s", flush=True)
    os.remove(wpath)
    summary = {"runs": len(results), "with_exceptions": sum(1 for r in results if r["exceptions"]),
               "exceptions": sum(len(r["exceptions"]) for r in results),
               "failed_checks": sum(len(r["failed_checks"]) for r in results),
               "checks": sum(len(c["checks"]) for c in cases), "seconds": round(time.time() - t0, 1)}
    with open(os.path.join(HERE, "tools", "apptest_results.json"), "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=1, ensure_ascii=False)
    print("SUMMARY " + json.dumps(summary))
    for r in results:
        if r["exceptions"] or r["failed_checks"]:
            print("FAIL", r["name"], r["exceptions"][:2], r["failed_checks"])
    return 0 if summary["exceptions"] == 0 and summary["failed_checks"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
