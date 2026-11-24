"""Glue between the settings and the engine/content modules (assembly track).

* The user may override a tradition's fixed calendar and Paschalion rule. Feasts are recomputed with
  feasts._compute() on a copy of the tradition dict carrying the overrides:
  - Paschalion: any rule (western / eastern / astronomical).
  - Fixed calendar: within the Julian family (gregorian / julian / revised_julian; byzantine = Julian months
    with the Anno Mundi era) the override moves the fixed feasts. Feast tables of Coptic/Ethiopian
    traditions are written in those calendars, and the Julian-family tables in Julian months, so a switch
    between the two families changes only the DISPLAY calendar, not the feast dates (a note says so).
* Astronomical Pascha outside 1850-2149 (DE440s): paschalion.OutsideEphemeris -> the movable cycle is left
  out with a clear note; fixed feasts are still shown.
"""
from __future__ import annotations

import html
from datetime import date, timedelta
from functools import lru_cache

import calendars as cal
import feasts
import saints
import names
import paschalion
import sects
import theme

JULIAN_FAMILY = ("gregorian", "julian", "revised_julian", "byzantine")
CAL_OPTIONS = ("gregorian", "julian", "revised_julian", "coptic", "ethiopian", "byzantine")
RULE_OPTIONS = ("western", "eastern", "astronomical")
HOURS_OPTIONS = ("roman", "byzantine", "coptic", "ethiopian", "armenian", "west_syriac", "east_syriac")

# Native names of the calendars and rules for the 'English · native' selectors. These forms were added by the
# assembly track (the content track's names.py has no calendar names); they are listed as unverified on the
# About page together with names.UNCERTAIN.
CAL_NATIVE = {
    "gregorian": ("Calendarium Gregorianum", "la"),
    "julian": ("Calendarium Iulianum", "la"),
    "revised_julian": ("Νέον Ἡμερολόγιον", "grc"),
    "coptic": ("التقويم القبطي", "ar"),
    "ethiopian": ("የኢትዮጵያ ዘመን አቆጣጠር", "am"),
    "byzantine": ("Ἔτος Κόσμου", "grc"),
}
RULE_NATIVE = {
    "western": ("Computus Gregorianus", "la"),
    "eastern": ("Πασχάλιον", "grc"),
    "astronomical": ("", "en"),
}
APP_UNCERTAIN = [(f"calendar:{k}", lg, v) for k, (v, lg) in CAL_NATIVE.items()] + \
                [(f"rule:{k}", lg, v) for k, (v, lg) in RULE_NATIVE.items() if v]

HOURS_NAME = {
    "roman": "Roman (Liturgy of the Hours)", "byzantine": "Byzantine (Horologion)", "coptic": "Coptic (Agpeya)",
    "ethiopian": "Ethiopian (Sa'atat)", "armenian": "Armenian (Zhamagirk')", "west_syriac": "West Syriac (Shehimo)",
    "east_syriac": "East Syriac (Hudra)",
}
NATIVITY_KEYS = ("nativity", "genna", "nativity_theophany")


# ------------------------------------------------------------------ labels
def cal_label(c: str) -> str:
    nat = CAL_NATIVE.get(c, ("", "en"))[0]
    return f"{cal.NAME[c]} · {nat}" if nat else cal.NAME[c]


def cal_label_html(c: str) -> str:
    nat, lg = CAL_NATIVE.get(c, ("", "en"))
    return theme.label(cal.NAME[c], nat, lg)


def rule_label(r: str) -> str:
    nat = RULE_NATIVE.get(r, ("", "en"))[0]
    return f"{paschalion.RULE_NAME[r]} · {nat}" if nat else paschalion.RULE_NAME[r]


def trad_label(t: dict) -> str:
    nat = t.get("name_native") or ""
    return f"{t['name_en']} · {nat}" if nat and nat != t["name_en"] else t["name_en"]


def comm_label(ckey: str) -> str:
    c = next(x for x in sects.COMMUNIONS if x["key"] == ckey)
    nat = c.get("name_native") or ""
    return f"{c['name_en']} · {nat}" if nat and nat != c["name_en"] else c["name_en"]


def lang_label(lg: str) -> str:
    return names.LANG_NAMES.get(lg, lg)


def feast_name_html(key: str, lang: str, variant=None) -> str:
    """'English · native' for a feast/fast key, with a '?' mark on forms not yet verified."""
    d = names.NAMES.get(key, {})
    en = d.get("en", key.replace("_", " "))
    nat = names.native(key, lang) if lang != "en" else None
    out = theme.label(en, nat or "", lang, variant)
    if nat and names.is_uncertain(key, lang):
        out += "<sup title='Unverified form (see About)'>?</sup>"
    return out


def feast_name(key: str, lang: str) -> str:
    return names.label(key, lang)


# ------------------------------------------------------------------ dates in a calendar
def cdate(c: str, d: date):
    return cal.from_gregorian(c, d)


def month_name_html(c: str, m: int, lang: str) -> str:
    mc = "julian" if c == "byzantine" else c
    # Byzantine month m (1 = September) -> Julian month name
    jm = cal.BYZ_TO_JULIAN_MONTH[m] if c == "byzantine" else m
    en = names.MONTHS[mc]["en"][jm - 1]
    nat = names.MONTHS[mc].get(lang, [None] * 13)[jm - 1] if lang != "en" and lang in names.MONTHS[mc] else ""
    return theme.label(en, nat or "", lang)


def month_name(c: str, m: int, lang: str = "en") -> str:
    mc = "julian" if c == "byzantine" else c
    jm = cal.BYZ_TO_JULIAN_MONTH[m] if c == "byzantine" else m
    out = names.month_label(mc, jm, lang)
    a, _, b = out.partition(names.SEP)
    return a if b == a else out


def weekday_html(d: date, lang: str) -> str:
    en = names.WEEKDAYS["en"][d.weekday()]
    nat = names.WEEKDAYS.get(lang, [None] * 7)[d.weekday()] if lang != "en" and lang in names.WEEKDAYS else ""
    return theme.label(en, nat or "", lang)


def date_html(c: str, d: date, lang: str, weekday: bool = True) -> str:
    x = cal.from_gregorian(c, d)
    era = cal.ERA[c]
    extra = f", indiction {cal.indiction(x.year)}" if c == "byzantine" else ""
    wd = weekday_html(d, lang) + ", " if weekday else ""
    return f"{wd}{x.day} {month_name_html(c, x.month, lang)} {x.year} {html.escape(era)}{extra}"


def date_plain(c: str, d: date, lang: str = "en") -> str:
    x = cal.from_gregorian(c, d)
    return f"{x.day} {month_name(c, x.month, 'en')} {x.year} {cal.ERA[c]}"


def civil(d: date) -> str:
    return f"{d.day} {d.strftime('%b')} {d.year}"


# ------------------------------------------------------------------ feasts with overrides
def feast_calendar(trad: dict, display_cal: str) -> str:
    """The calendar the fixed feasts are reckoned in, given the display/override calendar."""
    own = trad["fixed_calendar"]
    if own in JULIAN_FAMILY and display_cal in JULIAN_FAMILY:
        return "julian" if display_cal == "byzantine" else display_cal
    return own


def effective(trad_key: str, display_cal: str, rule: str) -> dict:
    t = dict(sects.BY_KEY[trad_key])
    t["fixed_calendar"] = feast_calendar(t, display_cal)
    t["paschalion"] = rule
    return t


_MOVABLE_KEYS = {e["key"] for e in feasts.MOVABLE} | {"pascha"}


@lru_cache(maxsize=512)
def year_events(trad_key: str, display_cal: str, rule: str, gy: int):
    """(events, periods, note) for Gregorian year gy, with the overrides applied."""
    t = effective(trad_key, display_cal, rule)
    note = ""
    try:
        ev, pe = feasts._compute(t, gy)
    except paschalion.OutsideEphemeris:
        t2 = dict(t, paschalion="western")
        ev, pe = feasts._compute(t2, gy)
        ev = [e for e in ev if e[1] not in _MOVABLE_KEYS]
        pe = [p for p in pe if p[2] not in _MOVABLE_KEYS]
        note = (f"Astronomical Pascha is not available for {gy}: the JPL DE440s ephemeris covers "
                f"1850-2149. Pascha and the feasts and fasts that depend on it are not shown.")
    return tuple(ev), tuple(_trim_fasts(pe, trad_key, display_cal, rule, gy, ev)), note


def _trim_fasts(periods, trad_key, display_cal, rule, gy, ev):
    """The Nativity fast ends on the eve of the Nativity. The content tables give the Coptic/Ethiopian fast as
    '16 Hathor - 28 Koiak'; in years when the Nativity itself is kept on 28 Koiak (= 7 January, the Coptic
    year after a Coptic leap year) the fast would then cover the feast day, so it is shortened by one day.
    Only fasts ending on a Nativity feast are touched (other feasts that fall inside a fast do not end it)."""
    feast_days = {d for d, k, r, kind in ev if kind == "feast" and k in NATIVITY_KEYS}
    nxt = None
    out = []
    for s, e, key in periods:
        if e.year != gy and e not in feast_days:     # period runs into next year: check that year's feasts too
            if nxt is None:
                try:
                    nev, _ = feasts._compute(effective(trad_key, display_cal, rule), e.year)
                except paschalion.OutsideEphemeris:
                    nev = []
                nxt = {d for d, k, r, kind in nev if kind == "feast" and k in NATIVITY_KEYS}
            if e in nxt and e > s:
                e = e - timedelta(days=1)
        elif e in feast_days and e > s:
            e = e - timedelta(days=1)
        out.append((s, e, key))
    return out


@lru_cache(maxsize=512)
def saint_events(trad_key: str, display_cal: str, rule: str, gy: int):
    """Saints' days (date, saint key, rank) in Gregorian year gy, with the calendar/Paschalion overrides applied."""
    t = effective(trad_key, display_cal, rule)
    try:
        return tuple(saints.for_year(t, gy))
    except paschalion.OutsideEphemeris:
        return tuple(saints.for_year(dict(t, paschalion="western"), gy))


def saints_between(trad_key, display_cal, rule, d0: date, d1: date):
    out = []
    for gy in range(d0.year, d1.year + 1):
        out += [x for x in saint_events(trad_key, display_cal, rule, gy) if d0 <= x[0] <= d1]
    return out


def events_between(trad_key, display_cal, rule, d0: date, d1: date):
    ev, notes = [], []
    for gy in range(d0.year, d1.year + 1):
        e, _, n = year_events(trad_key, display_cal, rule, gy)
        ev += [x for x in e if d0 <= x[0] <= d1]
        if n and n not in notes:
            notes.append(n)
    return ev, notes


def periods_covering(trad_key, display_cal, rule, d: date):
    out = []
    for gy in (d.year - 1, d.year):
        _, pe, _ = year_events(trad_key, display_cal, rule, gy)
        out += [p for p in pe if p[0] <= d <= p[1] and p not in out]
    return out


def pascha(year: int, rule: str):
    try:
        return paschalion.easter(year, rule)
    except paschalion.OutsideEphemeris:
        return None


def movable(year: int, rule: str):
    try:
        return paschalion.movable(year, rule)
    except paschalion.OutsideEphemeris:
        return None


@lru_cache(maxsize=256)
def weekly_fasts(trad_key: str, display_cal: str, rule: str, gy: int) -> frozenset:
    """Wednesday/Friday fast days, mirroring feasts.weekly_fast_days() but with the overrides applied."""
    t = effective(trad_key, display_cal, rule)
    ev, _, note = year_events(trad_key, display_cal, rule, gy)
    feast_days = {d for d, k, r, kind in ev if kind == "feast" and feasts.RANKS.get(r, (9,))[0] <= 2}
    excluded = set()
    for yy in (gy - 1, gy, gy + 1):
        p = pascha(yy, rule)
        if p is None:
            continue
        excluded |= {p + timedelta(days=i) for i in range(0, 50)}
        if t.get("rite") == "byzantine":
            excluded |= {p + timedelta(days=i) for i in range(-69, -62)}
            excluded |= {p + timedelta(days=i) for i in range(49, 57)}
            for g, y in feasts._in_year(feasts._own("own", t), 12, 25, yy):
                excluded |= {g + timedelta(days=i) for i in range(0, 11)}
    out = set()
    d = date(gy, 1, 1)
    while d.year == gy:
        wd = d.weekday()
        is_fast = (wd == 4) if t.get("rite") == "latin" else wd in (2, 4)
        if is_fast and d not in excluded and d not in feast_days:
            out.add(d)
        d += timedelta(days=1)
    return frozenset(out)


def is_weekly_fast(trad_key, display_cal, rule, d: date) -> bool:
    return d in weekly_fasts(trad_key, display_cal, rule, d.year)


# ------------------------------------------------------------------ seasons
def season(trad_key: str, display_cal: str, rule: str, d: date) -> list[str]:
    """Names of the liturgical season(s) for day d (English; keys from names.py where they exist)."""
    t = effective(trad_key, display_cal, rule)
    rite = t.get("rite")
    out = []
    mv = movable(d.year, rule)
    if mv is not None:
        P = mv["pascha"]
        if rite == "latin":
            ev, _, _ = year_events(trad_key, display_cal, rule, d.year)
            k = {e[1]: e[0] for e in ev}
            adv = k.get("advent_1")
            bap = k.get("baptism_of_the_lord")
            if adv and adv <= d <= date(d.year, 12, 24):
                out.append("Advent")
            elif d >= date(d.year, 12, 25) or (bap and d <= bap):
                out.append("Christmas season")
            elif mv["ash_wednesday"] <= d < mv["holy_thursday"]:
                out.append("Lent" + (" · Holy Week" if d >= mv["palm_sunday"] else ""))
            elif mv["holy_thursday"] <= d < P:
                out.append("Paschal Triduum" + (" (from the evening Mass of the Lord's Supper)" if d == mv["holy_thursday"] else ""))
            elif P <= d <= mv["pentecost"]:
                out.append("Easter season")
            else:
                out.append("Ordinary Time")
        elif rite == "byzantine":
            if mv["publican_pharisee"] <= d <= mv["holy_saturday"]:
                if mv["clean_monday"] <= d < mv["lazarus_saturday"]:
                    out.append("Triodion · Great Lent")
                elif mv["lazarus_saturday"] <= d <= mv["palm_sunday"]:
                    out.append("Triodion · Lazarus Saturday and Palm Sunday")
                elif d > mv["palm_sunday"]:
                    out.append("Triodion · Holy Week")
                else:
                    out.append("Triodion (pre-Lenten Sundays)")
            elif P <= d <= mv["all_saints_sunday"]:
                out.append("Pentecostarion")
            else:
                out.append("Octoechos (season after Pentecost)")
        else:
            if mv["palm_sunday"] < d < P:
                out.append("Holy Week (Week of Pascha)")
            elif P <= d <= mv["pentecost"]:
                out.append("Paschal season (the Holy Fifty Days)")
    for s, e, key in periods_covering(trad_key, display_cal, rule, d):
        nm = names.NAMES.get(key, {}).get("en", key.replace("_", " "))
        if s != e and all(nm not in x for x in out):
            out.append(nm)
    return out


def nativity_date(trad_key, display_cal, rule, gy: int):
    ev, _, _ = year_events(trad_key, display_cal, rule, gy)
    for d, k, r, kind in ev:
        if k in NATIVITY_KEYS:
            return d, k
    return None, None
