"""
Paschalion: the date of Pascha (Easter) and the movable cycle that hangs on it.

Rule keys (CONTRACT.md)
-----------------------
western       Gregorian computus (Clavius, 1582): ecclesiastical equinox 21 March (Gregorian),
              Gregorian epact table with solar and lunar corrections. Implemented with the
              "Anonymous Gregorian algorithm" (Meeus, Astronomical Algorithms, 2nd ed., ch. 8;
              Butcher 1876). Easter is the Sunday after the Paschal full moon (PFM).
eastern       Julian/Alexandrian computus (19-year Metonic cycle, Dionysius Exiguus):
              ecclesiastical equinox 21 March Julian, Easter computed in the Julian calendar
              (Meeus' Julian algorithm) and returned as the proleptic-Gregorian civil date.
              Used by the Eastern Orthodox (Julian and Revised Julian churches alike, except
              Finland), Oriental Orthodox and Eastern Catholic churches that follow them.
astronomical  WCC/MECC consultation, Aleppo, 5-10 March 1997, "Towards a Common Date for
              Easter": Easter = the Sunday following the first astronomical full moon after
              the astronomical vernal (March) equinox, the instants being "determined by the
              most accurate possible scientific means" and reckoned on the meridian of
              Jerusalem.  Implementation (exactly):
                * March equinox = instant the Sun's apparent geocentric ecliptic longitude of
                  date is 0 deg (Skyfield almanac.seasons on JPL DE440s).
                * Full moon = instant the Moon-Sun apparent geocentric elongation in
                  ecliptic longitude is 180 deg (Skyfield almanac.moon_phases on DE440s).
                * The first full moon whose instant is at or after the equinox instant.
                * Its calendar date is taken in LOCAL MEAN TIME OF THE JERUSALEM MERIDIAN,
                  35.2296 deg E (Church of the Holy Sepulchre) = UTC + 2 h 20 min 55.1 s.
                  (Variant `meridian='ist'` = UTC+2, Israel Standard Time without DST,
                  for sensitivity tests only.)
                * Easter = the first Sunday strictly after that date (a full moon falling
                  on a Sunday sends Easter to the following Sunday).
              Available only for years covered by the ephemeris (DE440s: 1850-2149).

All returned `date` values are proleptic Gregorian civil dates.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from functools import lru_cache

import calendars as cal

RULES = ("western", "eastern", "astronomical")
RULE_NAME = {
    "western": "Western (Gregorian computus)",
    "eastern": "Eastern (Julian / Alexandrian computus)",
    "astronomical": "Astronomical (WCC Aleppo 1997, Jerusalem meridian)",
}
JERUSALEM_LON = 35.2296
JERUSALEM_LAT = 31.7784
LMT_OFFSET = timedelta(hours=JERUSALEM_LON / 15.0)   # 2:20:55.1
MERIDIANS = {"lmt": LMT_OFFSET, "ist": timedelta(hours=2), "utc": timedelta(0)}


class OutsideEphemeris(ValueError):
    pass


def _check_rule(rule: str) -> None:
    if rule not in RULES:
        raise KeyError(f"unknown paschalion rule {rule!r}; expected one of {RULES}")


# ----------------------------------------------------------------------------------------------
# computistic Easter
# ----------------------------------------------------------------------------------------------
def western_easter(year: int) -> date:
    """Gregorian Easter (Meeus/Butcher 'anonymous' algorithm). Valid for year >= 1583."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    month, day = divmod(h + l_ - 7 * m + 114, 31)
    return date(year, month, day + 1)


def eastern_easter_julian(year: int) -> cal.CDate:
    """Julian-calendar date of Orthodox Pascha (Meeus' Julian algorithm)."""
    a, b, c = year % 4, year % 7, year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month, day = divmod(d + e + 114, 31)
    return cal.CDate(year, month, day + 1, "julian")


def eastern_easter(year: int) -> date:
    return cal.to_gregorian(eastern_easter_julian(year))


def _gregorian_pfm(year: int) -> date:
    """Ecclesiastical Paschal full moon, Gregorian (Oudin/Clavius epact): 21 March + i days."""
    g = year % 19
    c = year // 100
    h = (c - c // 4 - (8 * c + 13) // 25 + 19 * g + 15) % 30
    i = h - (h // 28) * (1 - (h // 28) * (29 // (h + 1)) * ((21 - g) // 11))
    return date(year, 3, 21) + timedelta(days=i)


def _julian_pfm(year: int) -> cal.CDate:
    """Ecclesiastical Paschal full moon, Julian calendar: 21 March Julian + ((19g+15) mod 30)."""
    i = (19 * (year % 19) + 15) % 30
    j = cal.to_jdn("julian", year, 3, 21) + i
    return cal.from_jdn("julian", j)


def ecclesiastical_equinox(year: int, rule: str) -> date:
    """21 March of the rule's calendar, as a Gregorian date (3 April Gregorian for eastern
    in 1900-2099). For 'astronomical' the UTC date of the true equinox is returned."""
    _check_rule(rule)
    if rule == "western":
        return date(year, 3, 21)
    if rule == "eastern":
        return cal.to_gregorian(cal.CDate(year, 3, 21, "julian"))
    return march_equinox(year).date()


# ----------------------------------------------------------------------------------------------
# astronomical Easter
# ----------------------------------------------------------------------------------------------
@lru_cache(maxsize=1024)
def march_equinox(year: int) -> datetime:
    """Instant (tz-aware UTC) of the March equinox from JPL DE440s."""
    import sky_engine as se
    if not se.covers(date(year, 3, 1)) or not se.covers(date(year, 3, 31)):
        lo, hi = se.ephemeris_range()
        raise OutsideEphemeris(f"{year}: outside the ephemeris range {lo}..{hi}")
    ev = [t for t, k in se.seasons(date(year, 3, 10), date(year, 3, 31)) if k == 0]
    if not ev:
        raise RuntimeError(f"no March equinox found in {year}")
    return ev[0]


@lru_cache(maxsize=1024)
def astronomical_full_moon(year: int) -> datetime:
    """First full moon (tz-aware UTC) at or after the March equinox instant."""
    import sky_engine as se
    eq = march_equinox(year)
    fms = [t for t in se.full_moons(date(year, 3, 10), date(year, 5, 5)) if t >= eq]
    return fms[0]


def _next_sunday_after(d: date) -> date:
    return d + timedelta(days=(6 - d.weekday()) % 7 or 7)


@lru_cache(maxsize=4096)
def astronomical_detail(year: int, meridian: str = "lmt") -> dict:
    """Everything behind the astronomical Easter of `year`.

    Keys: equinox_utc, full_moon_utc, offset (timedelta of the reckoning meridian),
    full_moon_local (naive local-meridian datetime), full_moon_local_date, easter,
    hours_fm_after_equinox, hours_from_saturday_midnight (signed: FM local time minus the
    nearest Saturday/Sunday midnight; small |value| = knife-edge), knife_edge_hours (min of
    the two margins that can change the date)."""
    off = MERIDIANS[meridian]
    eq = march_equinox(year)
    fm = astronomical_full_moon(year)
    fm_local = (fm + off).replace(tzinfo=None)
    fm_date = fm_local.date()
    easter_d = _next_sunday_after(fm_date)
    # nearest Saturday->Sunday midnight (local meridian)
    days_since_sun = (fm_date.weekday() + 1) % 7          # Sunday -> 0, Monday -> 1, ...
    sun_midnight = datetime.combine(fm_date - timedelta(days=days_since_sun), datetime.min.time())
    cands = [sun_midnight, sun_midnight + timedelta(days=7)]
    nearest = min(cands, key=lambda m: abs((fm_local - m).total_seconds()))
    h_sat = (fm_local - nearest).total_seconds() / 3600.0
    h_eq = (fm - eq).total_seconds() / 3600.0
    # the previous full moon's margin to the equinox also matters (it might fall just after)
    import sky_engine as se
    prev = [t for t in se.full_moons(date(year, 2, 1), date(year, 3, 31)) if t < eq]
    h_prev = (eq - prev[-1]).total_seconds() / 3600.0 if prev else float("inf")
    return {
        "year": year,
        "meridian": meridian,
        "equinox_utc": eq,
        "full_moon_utc": fm,
        "offset": off,
        "full_moon_local": fm_local,
        "full_moon_local_date": fm_date,
        "easter": easter_d,
        "hours_fm_after_equinox": h_eq,
        "hours_prev_fm_before_equinox": h_prev,
        "hours_from_saturday_midnight": h_sat,
        "knife_edge_hours": min(abs(h_sat), h_eq, h_prev),
    }


def astronomical_easter(year: int, meridian: str = "lmt") -> date:
    return astronomical_detail(year, meridian)["easter"]


# ----------------------------------------------------------------------------------------------
# public API
# ----------------------------------------------------------------------------------------------
def easter(year: int, rule: str) -> date:
    """Pascha / Easter Sunday of `year` under `rule`, as a Gregorian civil date."""
    _check_rule(rule)
    if rule == "western":
        return western_easter(year)
    if rule == "eastern":
        return eastern_easter(year)
    return astronomical_easter(year)


def paschal_full_moon(year: int, rule: str):
    """Ecclesiastical Paschal full moon as a Gregorian `date` for 'western' / 'eastern'
    (for 'eastern' = Julian date of the 14th of the Paschal moon converted to Gregorian);
    for 'astronomical' a tz-aware UTC datetime (astronomical_full_moon(year))."""
    _check_rule(rule)
    if rule == "western":
        return _gregorian_pfm(year)
    if rule == "eastern":
        return cal.to_gregorian(_julian_pfm(year))
    return astronomical_full_moon(year)


# Offsets from Pascha (days). Each entry: key -> offset.
OFFSETS = {
    "zacchaeus_sunday": -77,      # Byzantine (Slavic usage): Sunday before the Triodion
    "publican_pharisee": -70,     # Byzantine: Triodion begins
    "septuagesima": -63,          # Latin (pre-1969 calendar and Ordinariate): = Prodigal Son
    "prodigal_son": -63,
    "sexagesima": -56,
    "nineveh_fast_start": -69,    # Monday; Coptic/Ethiopian 3-day Fast of Nineveh, Syriac Ba'utha
    "nineveh_fast_end": -67,      # Wednesday
    "meatfare_sunday": -56,       # Byzantine: Sunday of the Last Judgement
    "quinquagesima": -49,
    "cheesefare_sunday": -49,     # Byzantine: Forgiveness Sunday
    "great_lent_start_coptic": -55,  # Monday; 55-day Coptic/Ethiopian Great Fast (Abiy Tsom)
    "clean_monday": -48,          # Byzantine Great Lent begins (also Maronite/Syriac Ash Monday)
    "ash_wednesday": -46,         # Latin Lent begins
    "laetare_sunday": -21,
    "lazarus_saturday": -8,
    "palm_sunday": -7,
    "holy_thursday": -3,
    "good_friday": -2,
    "holy_saturday": -1,
    "pascha": 0,
    "easter_monday": 1,
    "thomas_sunday": 7,           # Antipascha / Divine Mercy Sunday (Latin)
    "mid_pentecost": 24,          # Wednesday of the 4th week (Mesopentecost)
    "ascension": 39,
    "pentecost": 49,
    "whit_monday": 50,            # Monday of the Holy Spirit
    "trinity_sunday": 56,         # Latin
    "all_saints_sunday": 56,      # Byzantine
    "corpus_christi": 60,         # Thursday after Trinity (often transferred to Sunday, P+63)
    "sacred_heart": 68,           # Friday after the 2nd Sunday after Pentecost
    "apostles_fast_start": 57,    # Byzantine: Monday after All Saints (see apostles_fast)
}


def movable(year: int, rule: str) -> dict[str, date]:
    """All movable dates (Gregorian civil dates) of `year` derived from easter(year, rule).
    'apostles_fast_start' is the Byzantine start (P+57); for the Coptic/Ethiopian start
    (Monday after Pentecost, P+50) see 'apostles_fast_start_coptic' or apostles_fast()."""
    p = easter(year, rule)
    out = {k: p + timedelta(days=v) for k, v in OFFSETS.items()}
    out["apostles_fast_start_coptic"] = p + timedelta(days=50)
    return out


# Apostles' Fast ---------------------------------------------------------------------------------
_STYLE_ALIASES = {
    "byzantine": "julian", "old_calendar": "julian", "byzantine_julian": "julian",
    "new_calendar": "revised_julian", "byzantine_revised": "revised_julian",
    "alexandrian": "coptic", "oriental": "coptic",
}


def apostles_fast(year: int, rule: str, tradition_style: str = "julian") -> tuple[date, date]:
    """(start, end) of the Fast of the Holy Apostles, Gregorian dates.

    tradition_style is the tradition's fixed-calendar key ('julian', 'revised_julian',
    'gregorian', 'coptic', 'ethiopian'; aliases 'byzantine'/'old_calendar' -> julian,
    'new_calendar' -> revised_julian):
      julian / revised_julian / gregorian / byzantine:
          start = Monday after All Saints Sunday (Pascha + 57);
          end   = 29 June (feast of Ss Peter and Paul) in that fixed calendar
                  (Julian 29 June = 12 July Gregorian in 1900-2099).
      coptic / ethiopian:
          start = Monday after Pentecost (Pascha + 50);
          end   = 5 Epip (Coptic) = 5 Hamle (Ethiopian), the feast of the Apostles
                  (12 July Gregorian in 1900-2099).
    `end` is the feast day itself (the fast ends on its eve). If start > end the fast is
    omitted that year (happens with eastern Pascha on the Revised Julian / Gregorian fixed
    calendar when Pascha is late)."""
    _check_rule(rule)
    style = _STYLE_ALIASES.get(tradition_style, tradition_style)
    p = easter(year, rule)
    if style in ("coptic", "ethiopian"):
        start = p + timedelta(days=50)
        # 5 Epip of the Coptic year that contains `start`
        cy = cal.from_gregorian("coptic", start).year
        end = cal.to_gregorian(cal.CDate(cy, 11, 5, "coptic"))
        return start, end
    if style in ("julian", "revised_julian", "gregorian"):
        start = p + timedelta(days=57)
        end = cal.to_gregorian(cal.CDate(year, 6, 29, style))
        return start, end
    raise KeyError(f"unknown tradition_style {tradition_style!r}")


def apostles_fast_days(year: int, rule: str, tradition_style: str = "julian") -> int:
    """Number of fasting days (start .. eve of the feast); 0 when the fast is omitted."""
    s, e = apostles_fast(year, rule, tradition_style)
    return max(0, (e - s).days)


def pascha_table(years, rules=RULES) -> list[dict]:
    """[{year, western, eastern, astronomical}] (astronomical None outside the ephemeris)."""
    rows = []
    for y in years:
        row = {"year": y}
        for r in rules:
            try:
                row[r] = easter(y, r)
            except OutsideEphemeris:
                row[r] = None
        rows.append(row)
    return rows
