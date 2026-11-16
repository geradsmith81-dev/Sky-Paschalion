"""
Calendar arithmetic for Sky Paschalion. Every conversion passes through the Julian Day
Number (JDN: the integer day count whose day 0 is 1 January 4713 BC Julian, noon-based day
taken as the civil day it falls in). Years use astronomical numbering (year 0 = 1 BC).

Calendar keys (CONTRACT.md):
  gregorian       proleptic Gregorian calendar (Inter gravissimas, 1582).
  julian          proleptic Julian calendar; leap year every 4th year.
  revised_julian  Milankovic's Revised Julian calendar (Pan-Orthodox Congress, Constantinople
                  1923): Julian months; century years are leap only when year mod 900 is 200
                  or 600. Identical to the Gregorian calendar from 1 March 1600 to
                  28 February 2800.
  coptic          Coptic (Alexandrian) calendar, Anno Martyrum (era of Diocletian):
                  1 Thout AM 1 = 29 August AD 284 Julian. 12 months of 30 days + Pi Kogi
                  Enavot (Nasie, month 13) of 5 days, 6 in a leap year (AM mod 4 == 3).
                  1 Thout (Nayrouz) = 29 Aug Julian, 30 Aug Julian in the year before a
                  Julian leap year (= 11/12 September Gregorian in 1900-2099).
  ethiopian       Ethiopian calendar, Amete Mihret (Era of Incarnation):
                  1 Meskerem year 1 = 29 August AD 8 Julian. Same structure as the Coptic
                  calendar; year = Coptic AM + 276 (7/8 years behind the Gregorian AD year).
                  Month 13 = Pagume, 5 days, 6 when year mod 4 == 3.
  byzantine       Byzantine Anno Mundi (era of Constantinople, creation 1 September
                  5509 BC): Julian months and days, the year beginning on 1 September.
                  AM = AD + 5509 from 1 September to 31 December, AD + 5508 from
                  1 January to 31 August (Julian dates).
                  MONTH NUMBERING: month 1 = September ... month 4 = December,
                  month 5 = January ... month 12 = August (order of the Byzantine year).

The Coptic and Ethiopian liturgical (and traditional civil) day begins at sunset; the
function liturgical_date() applies that rule. All other functions work with civil dates.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

CALENDARS = ("gregorian", "julian", "revised_julian", "coptic", "ethiopian", "byzantine")

NAME = {
    "gregorian": "Gregorian",
    "julian": "Julian",
    "revised_julian": "Revised Julian (Milanković)",
    "coptic": "Coptic (Alexandrian)",
    "ethiopian": "Ethiopian",
    "byzantine": "Byzantine (Anno Mundi)",
}
ERA = {
    "gregorian": "AD",
    "julian": "AD",
    "revised_julian": "AD",
    "coptic": "AM (Anno Martyrum)",
    "ethiopian": "Amete Mihret",
    "byzantine": "AM (Anno Mundi)",
}

# JDN of the first day of each era.
COPTIC_EPOCH = 1825030      # 1 Thout AM 1 = 29 Aug 284 Julian (Friday)
ETHIOPIAN_EPOCH = 1724221   # 1 Meskerem 1 Amete Mihret = 29 Aug 8 Julian
ETHIOPIAN_COPTIC_OFFSET = 276
BYZANTINE_OFFSET = 5509     # AM = AD + 5509 from 1 September
JDN_GREGORIAN_ORDINAL = 1721425   # JDN = date.toordinal() + this

# Byzantine month number (1 = September) -> Julian month number, and back.
BYZ_TO_JULIAN_MONTH = {1: 9, 2: 10, 3: 11, 4: 12, 5: 1, 6: 2, 7: 3, 8: 4, 9: 5, 10: 6, 11: 7, 12: 8}
JULIAN_TO_BYZ_MONTH = {v: k for k, v in BYZ_TO_JULIAN_MONTH.items()}

_ML = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


@dataclass(frozen=True, order=True)
class CDate:
    year: int
    month: int
    day: int
    cal: str = "gregorian"

    def to_jdn(self) -> int:
        return to_jdn(self.cal, self.year, self.month, self.day)

    def to_gregorian(self) -> date:
        return to_gregorian(self)

    def weekday(self) -> int:
        """Monday = 0 ... Sunday = 6 (as datetime.date.weekday)."""
        return (self.to_jdn()) % 7

    def __str__(self) -> str:
        return f"{self.day} {self.month}/{self.year} ({self.cal})"


# ----------------------------------------------------------------------------------------------
# leap rules
# ----------------------------------------------------------------------------------------------
def _greg_leap(y: int) -> bool:
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def _jul_leap(y: int) -> bool:
    return y % 4 == 0


def _rj_leap(y: int) -> bool:
    if y % 4:
        return False
    if y % 100:
        return True
    return y % 900 in (200, 600)


def is_leap(cal: str, y: int) -> bool:
    """Leap year of the calendar. For coptic/ethiopian: the 13th month has 6 days.
    For byzantine: the AM year contains 29 February (Julian)."""
    if cal == "gregorian":
        return _greg_leap(y)
    if cal == "julian":
        return _jul_leap(y)
    if cal == "revised_julian":
        return _rj_leap(y)
    if cal in ("coptic", "ethiopian"):
        return y % 4 == 3
    if cal == "byzantine":
        # Jan-Aug of AM y lie in Julian year y - 5508
        return _jul_leap(y - (BYZANTINE_OFFSET - 1))
    raise KeyError(cal)


def months_in_year(cal: str, y: int) -> int:
    _check(cal)
    return 13 if cal in ("coptic", "ethiopian") else 12


def month_length(cal: str, y: int, m: int) -> int:
    _check(cal)
    if not 1 <= m <= months_in_year(cal, y):
        raise ValueError(f"month {m} out of range for {cal}")
    if cal in ("coptic", "ethiopian"):
        return 30 if m <= 12 else (6 if is_leap(cal, y) else 5)
    if cal == "byzantine":
        jm = BYZ_TO_JULIAN_MONTH[m]
        jy = _byz_julian_year(y, m)
        return 29 if (jm == 2 and _jul_leap(jy)) else _ML[jm - 1]
    if m == 2 and is_leap(cal, y):
        return 29
    return _ML[m - 1]


def _check(cal: str) -> None:
    if cal not in CALENDARS:
        raise KeyError(f"unknown calendar key {cal!r}; expected one of {CALENDARS}")


def _byz_julian_year(am: int, m: int) -> int:
    """Julian AD year of Byzantine month m (1 = September) of year AM."""
    return am - BYZANTINE_OFFSET if m <= 4 else am - BYZANTINE_OFFSET + 1


# ----------------------------------------------------------------------------------------------
# to JDN
# ----------------------------------------------------------------------------------------------
def _julian_to_jdn(y: int, m: int, d: int) -> int:
    a = (14 - m) // 12
    yy = y + 4800 - a
    mm = m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - 32083


def _gregorian_to_jdn(y: int, m: int, d: int) -> int:
    a = (14 - m) // 12
    yy = y + 4800 - a
    mm = m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045


def _rj_leaps_through(y: int) -> int:
    """Number of Revised Julian leap years in 1..y (negative counts for y < 0, so that
    differences are exact for all integers)."""
    return (y // 4 - y // 100 + (y - 200) // 900 + 1 + (y - 600) // 900 + 1)


# JDN of 1 January AD 1 (RJ) fixed so that 1 January 2000 RJ = 1 January 2000 Gregorian.
_RJ_DOY_CUM = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)


def _rj_days_before_year(y: int) -> int:
    return 365 * (y - 1) + _rj_leaps_through(y - 1)


def _rj_doy(y: int, m: int, d: int) -> int:
    return _RJ_DOY_CUM[m - 1] + d + (1 if (m > 2 and _rj_leap(y)) else 0)


_RJ_EPOCH = _gregorian_to_jdn(2000, 1, 1) - _rj_days_before_year(2000) - 1


def _rj_to_jdn(y: int, m: int, d: int) -> int:
    return _RJ_EPOCH + _rj_days_before_year(y) + _rj_doy(y, m, d)


def to_jdn(cal: str, y: int, m: int, d: int) -> int:
    _check(cal)
    if not 1 <= d <= month_length(cal, y, m):
        raise ValueError(f"day {d} out of range for {cal} {y}-{m}")
    if cal == "gregorian":
        return _gregorian_to_jdn(y, m, d)
    if cal == "julian":
        return _julian_to_jdn(y, m, d)
    if cal == "revised_julian":
        return _rj_to_jdn(y, m, d)
    if cal in ("coptic", "ethiopian"):
        ep = COPTIC_EPOCH if cal == "coptic" else ETHIOPIAN_EPOCH
        return ep - 1 + 365 * (y - 1) + y // 4 + 30 * (m - 1) + d
    if cal == "byzantine":
        return _julian_to_jdn(_byz_julian_year(y, m), BYZ_TO_JULIAN_MONTH[m], d)
    raise KeyError(cal)


# ----------------------------------------------------------------------------------------------
# from JDN
# ----------------------------------------------------------------------------------------------
def _jdn_to_julian(j: int) -> tuple[int, int, int]:
    c = j + 32082
    dd = (4 * c + 3) // 1461
    e = c - (1461 * dd) // 4
    mm = (5 * e + 2) // 153
    day = e - (153 * mm + 2) // 5 + 1
    month = mm + 3 - 12 * (mm // 10)
    year = dd - 4800 + mm // 10
    return year, month, day


def _jdn_to_gregorian(j: int) -> tuple[int, int, int]:
    a = j + 32044
    b = (4 * a + 3) // 146097
    c = a - 146097 * b // 4
    dd = (4 * c + 3) // 1461
    e = c - 1461 * dd // 4
    mm = (5 * e + 2) // 153
    day = e - (153 * mm + 2) // 5 + 1
    month = mm + 3 - 12 * (mm // 10)
    year = 100 * b + dd - 4800 + mm // 10
    return year, month, day


def _jdn_to_rj(j: int) -> tuple[int, int, int]:
    n = j - _RJ_EPOCH  # day count, 1 = 1 Jan AD 1
    y = int((n - 1) // 365.24222) + 1  # mean RJ year = 365.242222 d
    while _rj_days_before_year(y) >= n:
        y -= 1
    while _rj_days_before_year(y + 1) < n:
        y += 1
    doy = n - _rj_days_before_year(y)
    leap = _rj_leap(y)
    m = 12
    while m > 1 and _RJ_DOY_CUM[m - 1] + (1 if (m > 2 and leap) else 0) >= doy:
        m -= 1
    d = doy - _RJ_DOY_CUM[m - 1] - (1 if (m > 2 and leap) else 0)
    return y, m, d


def from_jdn(cal: str, jdn: int) -> CDate:
    _check(cal)
    if cal == "gregorian":
        return CDate(*_jdn_to_gregorian(jdn), cal)
    if cal == "julian":
        return CDate(*_jdn_to_julian(jdn), cal)
    if cal == "revised_julian":
        return CDate(*_jdn_to_rj(jdn), cal)
    if cal in ("coptic", "ethiopian"):
        ep = COPTIC_EPOCH if cal == "coptic" else ETHIOPIAN_EPOCH
        n = jdn - ep  # 0 = first day of the era
        y = (4 * n + 1463) // 1461
        day0 = n - (365 * (y - 1) + y // 4)  # 0-based day of year
        m = day0 // 30 + 1
        d = day0 % 30 + 1
        return CDate(y, m, d, cal)
    if cal == "byzantine":
        jy, jm, jd = _jdn_to_julian(jdn)
        am = jy + BYZANTINE_OFFSET if jm >= 9 else jy + BYZANTINE_OFFSET - 1
        return CDate(am, JULIAN_TO_BYZ_MONTH[jm], jd, cal)
    raise KeyError(cal)


def from_gregorian(cal: str, d: date) -> CDate:
    """Convert a datetime.date (proleptic Gregorian) to a CDate in calendar `cal`."""
    return from_jdn(cal, d.toordinal() + JDN_GREGORIAN_ORDINAL)


def to_gregorian(cd: CDate) -> date:
    """Convert a CDate to datetime.date (proleptic Gregorian, years 1..9999)."""
    return date.fromordinal(to_jdn(cd.cal, cd.year, cd.month, cd.day) - JDN_GREGORIAN_ORDINAL)


def convert(cd: CDate, cal: str) -> CDate:
    return from_jdn(cal, cd.to_jdn())


def jdn_of(d: date) -> int:
    return d.toordinal() + JDN_GREGORIAN_ORDINAL


def date_of_jdn(j: int) -> date:
    return date.fromordinal(j - JDN_GREGORIAN_ORDINAL)


def year_start(cal: str, y: int) -> date:
    """Gregorian date of the first day of year y of calendar cal
    (1 Jan; 1 Thout / Nayrouz; 1 Meskerem / Enkutatash; 1 September Julian for byzantine)."""
    return to_gregorian(CDate(y, 1, 1, cal))


def days_in_year(cal: str, y: int) -> int:
    return sum(month_length(cal, y, m) for m in range(1, months_in_year(cal, y) + 1))


def julian_gregorian_offset(d: date) -> int:
    """Days by which the Julian date lags the Gregorian date on Gregorian date d (13 in 1900-2099)."""
    j = from_gregorian("julian", d)
    # the Julian (y, m, d) read with the Gregorian day-count formula (29 Feb counts as day 60)
    return jdn_of(d) - _gregorian_to_jdn(j.year, j.month, j.day)


# ----------------------------------------------------------------------------------------------
# sunset-based liturgical day
# ----------------------------------------------------------------------------------------------
def liturgical_date(cal: str, local_datetime: datetime, sunset_local: datetime | None) -> CDate:
    """Date in calendar `cal` of the day running at `local_datetime`, where the day begins at
    sunset (Coptic, Ethiopian and Eastern liturgical usage). At or after `sunset_local` of the
    civil day the next date is returned. If sunset_local is None (polar day/night) the civil
    date is used. Both datetimes must be in the same local time zone (or both naive)."""
    d = local_datetime.date()
    if sunset_local is not None and local_datetime >= sunset_local:
        d = d + timedelta(days=1)
    return from_gregorian(cal, d)


# ----------------------------------------------------------------------------------------------
# small helpers for the UI
# ----------------------------------------------------------------------------------------------
def indiction(am_or_date) -> int:
    """Byzantine indiction (1..15) of a Byzantine AM year, or of the Byzantine year containing a
    datetime.date. Indiction = AM mod 15 (0 -> 15); AM 7534 (Sept 2025 Julian) is indiction 4."""
    am = am_or_date if isinstance(am_or_date, int) else from_gregorian("byzantine", am_or_date).year
    r = am % 15
    return 15 if r == 0 else r


def month_dates(cal: str, y: int, m: int) -> list[date]:
    """Gregorian dates of every day of month m of year y in calendar cal."""
    first = to_jdn(cal, y, m, 1)
    return [date_of_jdn(first + i) for i in range(month_length(cal, y, m))]
