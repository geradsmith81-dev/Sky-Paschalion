"""
Sky layer for Sky Paschalion: Sun times, temporal (unequal) hours, the canonical hours of the
seven hours systems, orientation (ad orientem / towards Jerusalem) and the Moon.

Astronomy: JPL DE440s via sky_engine (Skyfield). Sunrise/sunset = Sun's centre at -0.8333 deg
(upper limb, standard refraction, sea-level horizon); civil / nautical / astronomical twilight
= centre at -6 / -12 / -18 deg. Solar noon = upper meridian transit.

Temporal hours. The day from sunrise to sunset is divided into 12 equal "day hours", the night
from sunset to the next sunrise into 12 "night hours" (the ancient horae temporales); their
length changes with season and latitude and they are equal (60 min) only at the equinoxes.

Canonical hours. Each office is anchored either to a Sun event (dawn, sunrise, sunset) or to a
NOMINAL CLOCK TIME as given by the tradition in "equinoctial" form (6 am = sunrise,
noon, 3 pm, 6 pm = sunset, 9 pm, midnight ...). A nominal time h is converted to
unequal hours:  6 <= h <= 18 -> sunrise + (h-6) day hours;  h > 18 -> sunset + (h-18) night
hours of the following night;  h < 6 -> previous sunset + (h+6) night hours.  Hence "the
third hour" (9 am nominal) = the end of the 3rd temporal hour of the day, "the sixth hour" =
solar noon (to within the asymmetry of refraction), "midnight" = middle of the night.
These are the times the hours *name*; actual parish and monastic practice groups and
shifts them (notes per office). Where the Sun does not rise or set (polar day/night) every
office falls back to its nominal clock time in local civil time and is flagged.

Liturgical day. Byzantine, West Syriac and East Syriac lists for date D begin with Vespers
(Ramsho / Ramsha) on the evening of D-1, because the liturgical day begins at sunset; the
Armenian list begins with the Night Office of the night before D; the Roman list follows the
civil day (Matins of the preceding night first); the Coptic and Ethiopian lists follow the
order of the Agpeya / prayer manuals (Prime first, Midnight last, the following night).
"""
from __future__ import annotations

import math
from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache
from zoneinfo import ZoneInfo

import sky_engine as se

HOLY_SEPULCHRE = (31.7784, 35.2296)
EAST = 90.0
EARTH_RADIUS_KM = 6371.0
HOURS_SYSTEMS = ("roman", "byzantine", "coptic", "ethiopian", "armenian", "west_syriac", "east_syriac")
_HORIZONS = {"sun": -0.8333, "civil": -6.0, "nautical": -12.0, "astronomical": -18.0}


# ----------------------------------------------------------------------------------------------
# Sun times
# ----------------------------------------------------------------------------------------------
@lru_cache(maxsize=512)
def _sun_table(d0: date, d1: date, lat: float, lon: float, tzname: str) -> dict:
    """{date: sun_times dict} for local dates d0..d1 inclusive (one root search per horizon)."""
    tz = ZoneInfo(tzname)
    start = datetime.combine(d0, time(0), tz).astimezone(timezone.utc) - timedelta(hours=1)
    end = datetime.combine(d1 + timedelta(days=1), time(0), tz).astimezone(timezone.utc) + timedelta(hours=1)
    ev = {}
    for name, h in _HORIZONS.items():
        ev[name] = se.sun_events(lat, lon, start, end, horizon=h)
    up, low = se.meridian_transits(lat, lon, start, end + timedelta(hours=14))
    out = {}
    d = d0
    while d <= d1:
        def first(lst):
            v = [x.astimezone(tz) for x in lst if x.astimezone(tz).date() == d]
            return v[0] if v else None

        def last(lst):
            v = [x.astimezone(tz) for x in lst if x.astimezone(tz).date() == d]
            return v[-1] if v else None

        row = {"date": d, "tz": tzname}
        row["dawn_astronomical"] = first(ev["astronomical"][0])
        row["dawn_nautical"] = first(ev["nautical"][0])
        row["dawn_civil"] = first(ev["civil"][0])
        row["sunrise"] = first(ev["sun"][0])
        noon = first(up)
        row["solar_noon"] = noon
        row["sunset"] = last(ev["sun"][1])
        row["dusk_civil"] = last(ev["civil"][1])
        row["dusk_nautical"] = last(ev["nautical"][1])
        row["dusk_astronomical"] = last(ev["astronomical"][1])
        lows = [x.astimezone(tz) for x in low if noon is not None and x.astimezone(tz) > noon]
        row["solar_midnight"] = lows[0] if lows else None   # the night following `d`
        row["dawn"], row["dusk"] = row["dawn_civil"], row["dusk_civil"]
        if row["sunrise"] and row["sunset"] and row["sunset"] > row["sunrise"]:
            row["day_length_h"] = (row["sunset"] - row["sunrise"]).total_seconds() / 3600.0
            row["polar"] = None
        else:
            row["day_length_h"] = None
            ref = noon or datetime.combine(d, time(12), tz)
            alt, _ = se.sun_altaz(lat, lon, ref.astimezone(timezone.utc))
            if row["sunrise"] is None and row["sunset"] is None:
                row["polar"] = "polar_day" if alt > -0.8333 else "polar_night"
                row["day_length_h"] = 24.0 if alt > -0.8333 else 0.0
            else:
                row["polar"] = "partial"   # rise or set only (day of transition)
        out[d] = row
        d += timedelta(days=1)
    return out


def sun_times(d: date, lat: float, lon: float, tzname: str) -> dict:
    """Sun events of local civil date d, as tz-aware local datetimes (None when the event does
    not occur). Keys: dawn_astronomical, dawn_nautical, dawn_civil, sunrise, solar_noon,
    sunset, dusk_civil, dusk_nautical, dusk_astronomical, solar_midnight (the night after d),
    dawn (= dawn_civil), dusk (= dusk_civil), day_length_h, polar (None | 'polar_day' |
    'polar_night' | 'partial'), date, tz."""
    return dict(_sun_table(d, d, round(lat, 6), round(lon, 6), tzname)[d])


def _tables(d: date, lat: float, lon: float, tzname: str) -> dict:
    return _sun_table(d - timedelta(days=1), d + timedelta(days=1), round(lat, 6), round(lon, 6), tzname)


# ----------------------------------------------------------------------------------------------
# temporal hours
# ----------------------------------------------------------------------------------------------
def _split(a: datetime, b: datetime, part: str) -> list[dict]:
    step = (b - a) / 12
    return [{"index": i + 1, "part": part, "start": a + step * i, "end": a + step * (i + 1),
             "length_min": step.total_seconds() / 60.0} for i in range(12)]


def temporal_hours(d: date, lat: float, lon: float, tzname: str) -> list[dict]:
    """12 day hours (sunrise..sunset of d) + 12 night hours (sunset of d .. sunrise of d+1):
    [{index 1..12, part 'day'|'night', start, end, length_min}]. [] at polar day/night."""
    t = _tables(d, lat, lon, tzname)
    a, b, c = t[d]["sunrise"], t[d]["sunset"], t[d + timedelta(days=1)]["sunrise"]
    if not (a and b and c) or not (a < b < c):
        return []
    return _split(a, b, "day") + _split(b, c, "night")


# ----------------------------------------------------------------------------------------------
# canonical hours
# ----------------------------------------------------------------------------------------------
# (key, name_en, anchor, day_offset, note)
#   anchor = ('nominal', h) | ('event', sun_times key)
#   day_offset = -1 for offices of the eve that belong to the liturgical day D
_ROMAN = [
    ("matins", "Matins (Vigils; Office of Readings)", ("nominal", 2.0), 0,
     "Night office of the preceding night; Rule of St Benedict ch. 8: rise 'at the eighth hour of "
     "the night' (nominal 2 am). Since 1971 the Office of Readings may be said at any hour."),
    ("lauds", "Lauds (Morning Prayer)", ("event", "dawn_civil"), 0,
     "At daybreak (civil dawn). With Vespers one of the two 'hinges' of the Office (GILH 37)."),
    ("prime", "Prime (First Hour)", ("nominal", 6.0), 0,
     "Sunrise, first hour of the day. Suppressed for general use by Sacrosanctum Concilium 89d "
     "(1963); kept in the 1962 Breviary and by some monastic communities."),
    ("terce", "Terce (Third Hour)", ("nominal", 9.0), 0,
     "Close of the 3rd temporal hour (≈ 9 am). Daytime Prayer: Terce, Sext or None, one may be chosen."),
    ("sext", "Sext (Sixth Hour)", ("nominal", 12.0), 0, "Midday (end of the 6th hour = solar noon)."),
    ("none", "None (Ninth Hour)", ("nominal", 15.0), 0, "Mid-afternoon (≈ 3 pm), hour of the Crucifixion."),
    ("vespers", "Vespers (Evening Prayer)", ("event", "sunset"), 0,
     "Evening, at the lighting of the lamps; in practice usually late afternoon or early evening. "
     "Sundays and solemnities also have First Vespers on the eve."),
    ("compline", "Compline (Night Prayer)", ("nominal", 21.0), 0,
     "Before retiring; nominal 9 pm (3rd night hour). Practice varies widely."),
]
_BYZANTINE = [
    ("vespers", "Vespers (Hesperinos)", ("event", "sunset"), -1,
     "Begins the liturgical day on the eve; the lamp-lighting hymn 'O Joyful Light' is sung at "
     "sunset. The Ninth Hour is read just before it."),
    ("compline", "Compline (Apodeipnon)", ("nominal", 21.0), -1,
     "'After supper', before sleep (Small Compline; Great Compline in Lent)."),
    ("midnight", "Midnight Office (Mesonyktikon)", ("nominal", 24.0), -1,
     "Middle of the night; in parishes usually read just before Orthros."),
    ("matins", "Orthros (Matins)", ("event", "dawn_civil"), 0,
     "Night-to-dawn office; the Great Doxology at its close is meant to coincide with sunrise. "
     "In parishes often served in the morning before the Divine Liturgy, or on the eve as part of a Vigil."),
    ("prime", "First Hour", ("nominal", 7.0), 0, "Close of the 1st temporal hour (nominal 7 am); follows Orthros."),
    ("terce", "Third Hour", ("nominal", 9.0), 0, "≈ 9 am; Descent of the Holy Spirit (Acts 2:15). Before the Liturgy."),
    ("sext", "Sixth Hour", ("nominal", 12.0), 0, "Midday; the Typika may follow."),
    ("none", "Ninth Hour", ("nominal", 15.0), 0,
     "≈ 3 pm; the last office of the liturgical day, read before Vespers of the next day."),
]
_COPTIC = [
    ("prime", "First Hour (Prime)", ("nominal", 6.0), 0, "On rising, sunrise; the Resurrection."),
    ("terce", "Third Hour (Terce)", ("nominal", 9.0), 0, "≈ 9 am; Pentecost and Christ's trial."),
    ("sext", "Sixth Hour (Sext)", ("nominal", 12.0), 0, "Midday; the Crucifixion."),
    ("none", "Ninth Hour (None)", ("nominal", 15.0), 0, "≈ 3 pm; Christ's death on the Cross."),
    ("vespers", "Eleventh Hour (Vespers)", ("event", "sunset"), 0,
     "Named for the 11th hour of the day; prayed at sunset (nominal 6 pm). The Coptic day begins at sunset."),
    ("compline", "Twelfth Hour (Compline)", ("nominal", 21.0), 0,
     "Named for the 12th hour; prayed before sleep (nominal 9 pm)."),
    ("veil", "Prayer of the Veil", ("nominal", 22.0), 0,
     "Additional office, usually prayed by bishops, priests and monks after Compline; not one of the "
     "seven. Nominal time chosen here (after Compline) — no fixed hour."),
    ("midnight", "Midnight Prayer (three watches)", ("nominal", 24.0), 0,
     "Midnight of the night after this date (three services/watches). Often prayed before dawn."),
]
_ETHIOPIAN = [
    ("prime", "Morning Prayer (on rising)", ("nominal", 6.0), 0,
     "'First upon arising from bed in the morning'. The Ethiopian clock counts hours from about "
     "06:00 (12 o'clock = 6 am)."),
    ("terce", "Third Hour", ("nominal", 9.0), 0, "≈ 9 am (3 o'clock on the Ethiopian clock)."),
    ("sext", "Sixth Hour", ("nominal", 12.0), 0, "Midday."),
    ("none", "Ninth Hour", ("nominal", 15.0), 0, "≈ 3 pm."),
    ("vespers", "Evening Prayer", ("event", "sunset"), 0, "Sunset; the liturgical day begins at sunset."),
    ("compline", "Prayer before Sleep", ("nominal", 21.0), 0, "Before retiring (nominal 9 pm)."),
    ("midnight", "Midnight Prayer", ("nominal", 24.0), 0,
     "Midnight of the night after this date. The Se'atat (Horologium) of Abba Giyorgis of Gascha "
     "(15th c.) is chanted through the night towards dawn in churches and monasteries."),
]
_ARMENIAN = [
    ("midnight", "Night Office", ("nominal", 24.0), -1,
     "Midnight of the preceding night; the daily cycle begins at nightfall. Now usually said in the "
     "morning together with the Morning Office."),
    ("lauds", "Morning Office", ("event", "dawn_civil"), 0, "At dawn."),
    ("prime", "Sunrise Office", ("event", "sunrise"), 0, "At sunrise (nominal 6 am)."),
    ("terce", "Third Hour", ("nominal", 9.0), 0, "≈ 9 am; one of the three midday 'Little Hours'."),
    ("sext", "Sixth Hour", ("nominal", 12.0), 0, "Midday."),
    ("none", "Ninth Hour", ("nominal", 15.0), 0, "≈ 3 pm."),
    ("vespers", "Evening Office", ("event", "sunset"), 0, "At sunset; held daily in most churches."),
    ("peace", "Peace Office", ("nominal", 19.0), 0,
     "After sunset (first of two compline offices); nominal 7 pm chosen here (1st night hour)."),
    ("rest", "Rest Office", ("nominal", 21.0), 0, "Before retiring for sleep; last office of the day."),
]
_WEST_SYRIAC = [
    ("vespers", "Ramsho (Evening)", ("event", "sunset"), -1,
     "Begins the liturgical day on the eve (nominal 6 pm)."),
    ("compline", "Soutoro (Compline)", ("nominal", 21.0), -1, "Before sleep (nominal 9 pm)."),
    ("matins", "Lilyo (Night Office, three qawme)", ("nominal", 24.0), -1, "Midnight (nominal 12 am)."),
    ("lauds", "Sapro (Morning)", ("nominal", 6.0), 0, "Morning, sunrise (nominal 6 am)."),
    ("terce", "Tloth sho'in (Third Hour)", ("nominal", 9.0), 0, "≈ 9 am."),
    ("sext", "Sheth sho'in (Sixth Hour)", ("nominal", 12.0), 0, "Midday."),
    ("none", "Tsha' sho'in (Ninth Hour)", ("nominal", 15.0), 0,
     "≈ 3 pm; ends the liturgical day. In parish practice the hours are often grouped: Ramsho + "
     "Soutoro in the evening, Lilyo + Sapro (+ Third/Sixth/Ninth) in the morning."),
]
_EAST_SYRIAC = [
    ("vespers", "Ramsha (Evening)", ("event", "sunset"), -1,
     "First office of the liturgical day (nominal 6 pm); the most important congregational hour."),
    ("compline", "Suba'a (Compline)", ("nominal", 21.0), -1, "Nominal 9 pm; monastic."),
    ("matins", "Lelya (Night Office)", ("nominal", 24.0), -1,
     "Night office; sources differ: midnight, or 9 pm 'before sleep' in Syro-Malabar usage."),
    ("vigil", "Qala d-Shahra (Vigil)", ("nominal", 3.0), 0, "Nominal 3 am; monastic."),
    ("lauds", "Sapra (Morning)", ("nominal", 6.0), 0, "Nominal 6 am (sunrise)."),
    ("terce", "Qutta'a (Third Hour)", ("nominal", 9.0), 0, "Nominal 9 am; monastic."),
    ("sext", "'Endana (Noon)", ("nominal", 12.0), 0, "Midday; monastic."),
    ("none", "d-Bathar Sha'in (Ninth Hour)", ("nominal", 15.0), 0,
     "Nominal 3 pm; monastic. Parishes of the Assyrian and Ancient Church of the East (and "
     "Chaldean/Syro-Malabar faithful) chiefly keep Ramsha, Lelya and Sapra. Transliterations vary."),
]
HOURS_DEFS = {"roman": _ROMAN, "byzantine": _BYZANTINE, "coptic": _COPTIC, "ethiopian": _ETHIOPIAN,
              "armenian": _ARMENIAN, "west_syriac": _WEST_SYRIAC, "east_syriac": _EAST_SYRIAC}
HOUR_KEYS = {s: [k for k, *_ in defs] for s, defs in HOURS_DEFS.items()}
SYSTEM_NAME = {
    "roman": "Roman Breviary / Liturgy of the Hours", "byzantine": "Byzantine Horologion",
    "coptic": "Coptic Agpeya", "ethiopian": "Ethiopian Sa'atat (seven hours of prayer)",
    "armenian": "Armenian Zhamagirk' (Book of Hours)", "west_syriac": "West Syriac Shehimo",
    "east_syriac": "East Syriac Hudra / Qdham u-Wathar",
}


def _nominal_dt(h: float, day: date, t: dict, tz) -> tuple[datetime, bool]:
    """Nominal clock hour h of civil day `day` -> unequal-hour datetime; (dt, polar_fallback)."""
    prev, cur, nxt = t.get(day - timedelta(days=1)), t.get(day), t.get(day + timedelta(days=1))
    try:
        if 6.0 <= h <= 18.0:
            a, b = cur["sunrise"], cur["sunset"]
            if a and b and a < b:
                return a + (b - a) * ((h - 6.0) / 12.0), False
        elif h > 18.0:
            a, b = cur["sunset"], nxt["sunrise"]
            if a and b and a < b:
                return a + (b - a) * ((h - 18.0) / 12.0), False
        else:
            a, b = prev["sunset"], cur["sunrise"]
            if a and b and a < b:
                return a + (b - a) * ((h + 6.0) / 12.0), False
    except (TypeError, KeyError):
        pass
    return datetime.combine(day, time(0), tz) + timedelta(hours=h), True


def canonical_hours(d: date, lat: float, lon: float, tzname: str, system: str) -> list[dict]:
    """Canonical hours of (liturgical) date d for an hours system (HOURS_SYSTEMS).
    Returns [{key, name_en, start (tz-aware local), note, anchor, civil_date, polar_fallback}]
    in liturgical order (see module docstring)."""
    if system not in HOURS_DEFS:
        raise KeyError(f"unknown hours system {system!r}; expected one of {HOURS_SYSTEMS}")
    tz = ZoneInfo(tzname)
    t = dict(_sun_table(d - timedelta(days=2), d + timedelta(days=2), round(lat, 6), round(lon, 6), tzname))
    out = []
    for key, name, anchor, off, note in HOURS_DEFS[system]:
        day = d + timedelta(days=off)
        fallback = False
        if anchor[0] == "event":
            start = t[day][anchor[1]]
            desc = anchor[1].replace("_", " ")
            if start is None:   # e.g. no civil dawn in a white night: use nominal 5 am / 6 am / 6 pm
                hnom = {"dawn_civil": 5.0, "sunrise": 6.0, "sunset": 18.0}.get(anchor[1], 6.0)
                start, fallback = _nominal_dt(hnom, day, t, tz)
                desc += f" (absent; nominal {hnom:g} h used)"
        else:
            h = anchor[1]
            start, fallback = _nominal_dt(h, day, t, tz)
            desc = _describe_nominal(h)
        if fallback:
            note = note + " [Sun does not rise/set: local clock time used]"
        out.append({"key": key, "name_en": name, "start": start, "note": note, "anchor": desc,
                    "civil_date": start.date(), "polar_fallback": fallback,
                    "_nominal": anchor[0] == "nominal"})
    # In very short nights (e.g. white nights near 60 deg N) a nominal night hour can fall after
    # an event-anchored dawn office. Keep the liturgical order: move the nominal-anchored office
    # onto its neighbour's time and say so.
    for i in range(1, len(out)):
        a, b = out[i - 1], out[i]
        if b["start"] < a["start"]:
            if a["_nominal"] and not b["_nominal"]:
                a["start"] = b["start"]
                a["note"] += " [short night: moved to coincide with the next office]"
            else:
                b["start"] = a["start"]
                b["note"] += " [short night: moved to coincide with the previous office]"
            a["civil_date"], b["civil_date"] = a["start"].date(), b["start"].date()
    for h in out:
        h.pop("_nominal", None)
    return out


def _describe_nominal(h: float) -> str:
    if 6.0 <= h <= 18.0:
        n = h - 6.0
        return "sunrise" if n == 0 else ("sunset" if n == 12 else f"sunrise + {n:g} day hours")
    if h > 18.0:
        return f"sunset + {h - 18.0:g} night hours"
    return f"previous sunset + {h + 6.0:g} night hours"


def ethiopian_clock(local_dt: datetime) -> tuple[int, int, str]:
    """Traditional Ethiopian 12-hour clock reading (hour 1..12, minute, 'day'|'night'):
    hours are counted from 06:00 and 18:00 civil time (so 07:00 = 1 o'clock of the day)."""
    m = (local_dt.hour * 60 + local_dt.minute - 360) % 1440
    part = "day" if m < 720 else "night"
    hh, mm = divmod(m % 720, 60)
    return (12 if hh == 0 else hh), mm, part


# ----------------------------------------------------------------------------------------------
# orientation
# ----------------------------------------------------------------------------------------------
def bearing_to_jerusalem(lat: float, lon: float) -> float:
    """Initial great-circle bearing (deg clockwise from true north) to the Church of the Holy
    Sepulchre, 31.7784 N 35.2296 E (spherical Earth)."""
    p1, p2 = math.radians(lat), math.radians(HOLY_SEPULCHRE[0])
    dl = math.radians(HOLY_SEPULCHRE[1] - lon)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return math.degrees(math.atan2(y, x)) % 360.0


def distance_to_jerusalem_km(lat: float, lon: float) -> float:
    p1, p2 = math.radians(lat), math.radians(HOLY_SEPULCHRE[0])
    dl = math.radians(HOLY_SEPULCHRE[1] - lon)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(a)))


def sunrise_azimuth(d: date, lat: float, lon: float, tzname: str) -> float | None:
    """Azimuth (deg from true north) of the Sun at sunrise on d - the 'liturgical east' of a
    church oriented to the rising Sun on that day. None when the Sun does not rise."""
    sr = sun_times(d, lat, lon, tzname)["sunrise"]
    if sr is None:
        return None
    return se.sun_altaz(lat, lon, sr.astimezone(timezone.utc))[1]


def sunset_azimuth(d: date, lat: float, lon: float, tzname: str) -> float | None:
    ss = sun_times(d, lat, lon, tzname)["sunset"]
    if ss is None:
        return None
    return se.sun_altaz(lat, lon, ss.astimezone(timezone.utc))[1]


# ----------------------------------------------------------------------------------------------
# the Moon
# ----------------------------------------------------------------------------------------------
PHASE_NAMES = ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
               "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"]


def _as_utc(x) -> datetime:
    if isinstance(x, datetime):
        return x.replace(tzinfo=timezone.utc) if x.tzinfo is None else x.astimezone(timezone.utc)
    return datetime(x.year, x.month, x.day, 12, tzinfo=timezone.utc)   # a date: 12:00 UTC


def moon_phase(date_or_dt) -> dict:
    """Moon at a datetime (naive = UTC) or a date (12:00 UTC): elongation_deg (0 new .. 180 full),
    illumination (0..1), phase_index 0..7, phase_name, waxing, age_days (since the previous new
    moon), prev_new_moon, next_new_moon, next_full_moon (UTC)."""
    t = _as_utc(date_or_dt)
    el = float(se.moon_elongation([t])[0])
    ill = float(se.moon_illumination([t])[0])
    idx = int(((el + 22.5) % 360.0) // 45.0)
    ev = se.moon_phase_events((t - timedelta(days=32)).date(), (t + timedelta(days=32)).date())
    news = [x for x, k in ev if k == 0]
    prev_new = max([x for x in news if x <= t], default=None)
    next_new = min([x for x in news if x > t], default=None)
    nfm = min([x for x, k in ev if k == 2 and x > t], default=None)
    return {"when_utc": t, "elongation_deg": el, "illumination": ill, "phase_index": idx,
            "phase_name": PHASE_NAMES[idx], "waxing": el < 180.0,
            "age_days": (t - prev_new).total_seconds() / 86400.0 if prev_new else None,
            "prev_new_moon": prev_new, "next_new_moon": next_new, "next_full_moon": nfm}


def next_full_moon(dt) -> datetime:
    """First full moon strictly after dt (naive = UTC, or a date = 00:00 UTC); tz-aware UTC."""
    if isinstance(dt, datetime):
        t = _as_utc(dt)
    else:
        t = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)
    ev = se.moon_phase_events(t.date(), (t + timedelta(days=35)).date())
    return min(x for x, k in ev if k == 2 and x > t)


def march_equinox(year: int) -> datetime:
    """March equinox instant (UTC) - re-exported from paschalion for the sky page."""
    import paschalion
    return paschalion.march_equinox(year)
