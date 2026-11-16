"""Fast engine tests (pytest, or `python tests/test_engine.py`). Astronomical tests need
de440s.bsp in ./ephem or SKY_EPHEM_DIR; they are skipped when the ephemeris is absent."""
import os
import sys
from datetime import date, datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import calendars as C   # noqa: E402
import paschalion as P  # noqa: E402


def _have_ephem():
    import sky_engine as se
    return any(os.path.exists(os.path.join(d, n)) for d in se._search_dirs() for n in se.EPHEM_NAMES)


# ---- calendars ----
def test_calendar_anchors():
    assert C.from_gregorian("coptic", date(2025, 9, 11)) == C.CDate(1742, 1, 1, "coptic")      # Nayrouz
    assert C.from_gregorian("ethiopian", date(2025, 9, 11)) == C.CDate(2018, 1, 1, "ethiopian")  # Enkutatash
    assert C.year_start("coptic", 1740) == date(2023, 9, 12)          # after Coptic leap year 1739
    assert C.to_gregorian(C.CDate(1741, 4, 29, "coptic")) == date(2025, 1, 7)   # Nativity
    assert C.to_gregorian(C.CDate(1740, 4, 29, "coptic")) == date(2024, 1, 8)   # year after a leap year
    assert C.to_gregorian(C.CDate(1740, 4, 28, "coptic")) == date(2024, 1, 7)
    assert C.from_gregorian("julian", date(2025, 1, 7)) == C.CDate(2024, 12, 25, "julian")
    assert C.year_start("byzantine", 7534) == date(2025, 9, 14)
    assert C.from_gregorian("byzantine", date(2026, 1, 1)).year == 7534
    assert C.indiction(7534) == 4
    assert C.to_gregorian(C.CDate(284, 8, 29, "julian")) == C.year_start("coptic", 1)


def test_revised_julian():
    assert C.from_gregorian("revised_julian", date(2026, 11, 15)) == C.CDate(2026, 11, 15, "revised_julian")
    assert C.from_gregorian("revised_julian", date(2800, 3, 1)) == C.CDate(2800, 3, 2, "revised_julian")
    assert C.from_gregorian("revised_julian", date(2900, 3, 1)) == C.CDate(2900, 3, 1, "revised_julian")
    assert [y for y in range(2000, 3000, 100) if C.is_leap("revised_julian", y)] == [2000, 2400, 2900]


def test_month_lengths_and_roundtrip():
    assert C.month_length("coptic", 1739, 13) == 6 and C.month_length("coptic", 1740, 13) == 5
    assert C.month_length("ethiopian", 2015, 13) == 6           # Pagume 6 days (2015 mod 4 == 3)
    assert C.months_in_year("ethiopian", 2018) == 13
    assert C.month_length("byzantine", 7532, 6) == 29           # Feb 2024 Julian
    for cal in C.CALENDARS:
        for o in range(date(1900, 1, 1).toordinal(), date(2101, 1, 1).toordinal(), 17):
            d = date.fromordinal(o)
            assert C.to_gregorian(C.from_gregorian(cal, d)) == d


def test_liturgical_date():
    ss = datetime(2025, 9, 10, 18, 5)
    assert C.liturgical_date("coptic", datetime(2025, 9, 10, 18, 30), ss) == C.CDate(1742, 1, 1, "coptic")
    assert C.liturgical_date("coptic", datetime(2025, 9, 10, 17, 0), ss).year == 1741


# ---- paschalion ----
def test_easter_known():
    known = {2024: ("2024-03-31", "2024-05-05"), 2025: ("2025-04-20", "2025-04-20"),
             2026: ("2026-04-05", "2026-04-12"), 2027: ("2027-03-28", "2027-05-02")}
    for y, (w, e) in known.items():
        assert str(P.easter(y, "western")) == w and str(P.easter(y, "eastern")) == e


def test_movable_offsets():
    m = P.movable(2026, "eastern")
    assert m["pascha"] == date(2026, 4, 12) and m["clean_monday"] == date(2026, 2, 23)
    assert m["great_lent_start_coptic"] == date(2026, 2, 16) and m["nineveh_fast_start"] == date(2026, 2, 2)
    assert m["pentecost"] == date(2026, 5, 31) and m["all_saints_sunday"] == date(2026, 6, 7)
    w = P.movable(2026, "western")
    assert w["ash_wednesday"] == date(2026, 2, 18) and w["corpus_christi"] == date(2026, 6, 4)
    s, e = P.apostles_fast(2026, "eastern", "julian")
    assert s == date(2026, 6, 8) and e == date(2026, 7, 12)
    s, e = P.apostles_fast(2026, "eastern", "coptic")
    assert s == date(2026, 6, 1) and e == date(2026, 7, 12)


def test_astronomical():
    if not _have_ephem():
        return
    assert P.easter(2019, "astronomical") == date(2019, 3, 24)
    assert P.easter(2025, "astronomical") == date(2025, 4, 20)
    assert P.easter(2001, "astronomical") == date(2001, 4, 15)
    eq = P.march_equinox(2026)
    assert eq.tzinfo is not None and eq.date() == date(2026, 3, 20)


def test_sky_layer():
    if not _have_ephem():
        return
    import sky_layer as SL
    st = SL.sun_times(date(2026, 3, 20), 31.7784, 35.2296, "Asia/Jerusalem")
    assert st["sunrise"] < st["solar_noon"] < st["sunset"]
    th = SL.temporal_hours(date(2026, 3, 20), 31.7784, 35.2296, "Asia/Jerusalem")
    assert len(th) == 24
    for system in SL.HOURS_SYSTEMS:
        hs = SL.canonical_hours(date(2026, 3, 20), 41.9, 12.45, "Europe/Rome", system)
        assert all({"key", "name_en", "start", "note"} <= set(h) for h in hs)
    assert abs(SL.bearing_to_jerusalem(41.9022, 12.4533) - 111.78) < 0.05
    assert SL.EAST == 90.0
    fm = SL.next_full_moon(datetime(2026, 3, 20, tzinfo=timezone.utc))
    assert fm.date() == date(2026, 4, 2)


if __name__ == "__main__":
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            n += 1
            print("ok", name)
    print(f"{n} tests passed")
