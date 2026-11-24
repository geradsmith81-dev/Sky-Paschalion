"""Saints' days for Sky Paschalion: data in saints_data.py, dates computed here in each church's own calendar.

Each DAYS entry is one commemoration of one saint (SAINTS key) by some churches:

    applies    "rites": [...] | "traditions": [...] | "communions": [...]   (as feasts._applies) + optional "exclude"
    rank       "major" (great saint, feast-level in that church) | "saint" (memorial / commemoration)
    date rule, exactly one of
      fixed    "cal": own|gregorian|julian|coptic|ethiopian, "month", "day"
               ('own' = the church's fixed calendar: Julian for Old-Calendar churches, Revised Julian/Gregorian
               for New-Calendar ones; Coptic months 1-13 = Thout..Nasie; Ethiopian 1-13 = Meskerem..Pagume)
      offset   "base": "pascha" | a feasts.py key the church keeps, "offset_days": int
      weekday  a fixed date ("cal","month","day") or a "base" (+ optional "offset_days"), plus
               "weekday": 0=Mon .. 6=Sun, "n": +k = the k-th such weekday strictly AFTER the date,
               -k = the k-th strictly BEFORE it
      nth      "cal","month","weekday","nth": 1..5 or -1 (last) - e.g. the third Sunday of July
    optional   "note", "sources"

SAINTS[key] = {"en": English name, "text": 2-4 sentence summary, "sources": [urls]}.
Keys start with 's_' so they never collide with feast keys (names.NAMES / explain.TEXT).
"""
from __future__ import annotations

from datetime import date, timedelta

import feasts
import paschalion

try:
    from saints_data import SAINTS, DAYS
except ImportError:          # data module not installed yet
    SAINTS, DAYS = {}, []

RANKS = {"major": "Great saint", "saint": "Saint's day"}
CALS = {"own", "gregorian", "julian", "coptic", "ethiopian"}


def _month_days(cal: str, y: int, m: int) -> list[date]:
    out = []
    for d in range(1, 32):
        try:
            out.append(feasts.to_gregorian(cal, y, m, d))
        except ValueError:
            break
    return out


def _fixed(cal: str, m: int, d: int, gy: int) -> list[date]:
    return [g for g, _y in feasts._in_year(cal, m, d, gy)]


def _shift_weekday(d0: date, weekday: int, n: int) -> date:
    step = 1 if n > 0 else -1
    d, k = d0, 0
    while True:
        d += timedelta(days=step)
        if d.weekday() == weekday:
            k += 1
            if k == abs(n):
                return d


class _Known:
    """Feast dates of one church, by Gregorian year, computed lazily from feasts._compute."""

    def __init__(self, trad: dict):
        self.trad, self.by_year = trad, {}

    def get(self, key: str, gy: int):
        if gy not in self.by_year:
            known = {}
            try:
                ev, _ = feasts._compute(self.trad, gy)
                for dd, k, _r, _kind in ev:
                    known.setdefault(k, dd)
                known["pascha"] = feasts.easter(gy, self.trad["paschalion"])
            except paschalion.OutsideEphemeris:
                pass
            self.by_year[gy] = known
        return self.by_year[gy].get(key)


def _anchors(e: dict, trad: dict, gy: int, known: _Known) -> list[date]:
    """The date(s) a rule starts from, in and around year gy."""
    if "base" in e:
        out = []
        for y in (gy - 1, gy, gy + 1):
            b = known.get(e["base"], y)
            if b is not None:
                out.append(b + timedelta(days=e.get("offset_days", 0)))
        return out
    cal = feasts._own(e["cal"], trad)
    return [g for y in (gy - 1, gy, gy + 1) for g in _fixed(cal, e["month"], e["day"], y)]


def dates_for(e: dict, trad: dict, gy: int, known: _Known | None = None) -> list[date]:
    """Gregorian dates in year gy of one DAYS entry for one (effective) tradition dict."""
    known = known or _Known(trad)
    if "nth" in e:
        cal = feasts._own(e["cal"], trad)
        out = []
        for y in feasts._years_for(cal, gy):
            ds = [d for d in _month_days(cal, y, e["month"]) if d.weekday() == e["weekday"]]
            n = e["nth"]
            if ds and (n == -1 or 1 <= n <= len(ds)):
                d = ds[-1] if n == -1 else ds[n - 1]
                if d.year == gy:
                    out.append(d)
        return sorted(set(out))
    anchors = _anchors(e, trad, gy, known)
    if "weekday" in e:
        anchors = [_shift_weekday(a, e["weekday"], e.get("n", 1)) for a in anchors]
    return sorted({d for d in anchors if d.year == gy})


def for_year(trad: dict, gy: int) -> list[tuple]:
    """Sorted (date, saint key, rank) for one effective tradition dict in Gregorian year gy."""
    known = _Known(trad)
    out = []
    for e in DAYS:
        if feasts._applies(e, trad):
            for d in dates_for(e, trad, gy, known):
                out.append((d, e["key"], e.get("rank", "saint")))
    return sorted(set(out))


def entries_for(trad: dict) -> list[dict]:
    return [e for e in DAYS if feasts._applies(e, trad)]


def name(key: str) -> str:
    return SAINTS.get(key, {}).get("en", key[2:].replace("_", " ") if key.startswith("s_") else key)


def text(key: str) -> str | None:
    return SAINTS.get(key, {}).get("text")


def rule_text(e: dict, trad: dict, month_names) -> str:
    """Plain-English rule, e.g. '23 April (Julian)', 'Pascha +7 days', 'third Sunday of July'."""
    wd = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    ordn = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", -1: "last"}

    def fixed_txt(cal, m, d=None):
        cc = feasts._own(cal, trad)
        mn = month_names(cc, m)
        return (f"{d} {mn}" if d else mn) + f" ({cc.replace('_', ' ').title()})"

    if "nth" in e:
        return f"{ordn.get(e['nth'], e['nth'])} {wd[e['weekday']]} of {fixed_txt(e['cal'], e['month'])}"
    if "base" in e:
        b = "Pascha" if e["base"] == "pascha" else e["base"].replace("_", " ")
        o = e.get("offset_days", 0)
        start = b if o == 0 else f"{b} {o:+d} days"
    else:
        start = fixed_txt(e["cal"], e["month"], e["day"])
    if "weekday" in e:
        n = e.get("n", 1)
        rel = "after" if n > 0 else "before"
        return f"{ordn.get(abs(n), abs(n))} {wd[e['weekday']]} {rel} {start}"
    return start


def validate(saints=None, days=None, rites=None, trad_keys=None, feast_keys=None) -> list[str]:
    """Schema problems in the data (empty list = valid)."""
    import sects
    saints = SAINTS if saints is None else saints
    days = DAYS if days is None else days
    rites = rites or {t["rite"] for t in sects.TRADITIONS}
    trad_keys = trad_keys or set(sects.BY_KEY)
    comms = {t["communion"] for t in sects.TRADITIONS}
    feast_keys = feast_keys or ({e["key"] for g in (feasts.FIXED, feasts.MOVABLE, feasts.SPECIAL) for e in g}
                                | {"pascha"})
    errs = []
    for k, s in saints.items():
        if not k.startswith("s_"):
            errs.append(f"{k}: key must start with s_")
        if not s.get("en"):
            errs.append(f"{k}: no English name")
        t = s.get("text", "")
        if not 80 <= len(t) <= 700:
            errs.append(f"{k}: text length {len(t)} (want 80-700)")
        if not s.get("sources"):
            errs.append(f"{k}: no sources")
    used = set()
    for i, e in enumerate(days):
        tag = f"days[{i}] {e.get('key')}"
        if e.get("key") not in saints:
            errs.append(f"{tag}: key not in SAINTS")
        used.add(e.get("key"))
        if not any(e.get(f) for f in ("rites", "traditions", "communions")):
            errs.append(f"{tag}: no rites/traditions/communions")
        bad = (set(e.get("rites", ())) - rites) | (set(e.get("traditions", ())) - trad_keys) \
            | (set(e.get("exclude", ())) - trad_keys) | (set(e.get("communions", ())) - comms)
        if bad:
            errs.append(f"{tag}: unknown rite/tradition/communion {sorted(bad)}")
        if e.get("rank", "saint") not in RANKS:
            errs.append(f"{tag}: bad rank {e.get('rank')}")
        kinds = [("nth" in e), ("base" in e), ("cal" in e and "nth" not in e)]
        if sum(kinds) != 1:
            errs.append(f"{tag}: need exactly one of fixed (cal/month/day), base, or nth rule")
        if "cal" in e and e["cal"] not in CALS:
            errs.append(f"{tag}: bad cal {e['cal']}")
        if "base" in e and e["base"] not in feast_keys:
            errs.append(f"{tag}: base {e['base']} is not a feasts.py key")
        if "cal" in e and "nth" not in e and not ("month" in e and "day" in e):
            errs.append(f"{tag}: fixed rule needs month and day")
        if "weekday" in e and not (0 <= e["weekday"] <= 6):
            errs.append(f"{tag}: weekday must be 0..6")
    for k in set(saints) - used:
        errs.append(f"{k}: saint has no DAYS entry")
    return errs
