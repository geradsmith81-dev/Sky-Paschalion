"""
Astronomy from NASA JPL's DE440s planetary ephemeris (via Skyfield) for Sky Paschalion.

Adapted from the Sky Luach / Sky Taqwim sky_engine.py (same load() contract):

* March equinox and the other seasons (Skyfield almanac.seasons: apparent geocentric
  ecliptic longitude of the Sun = 0, 90, 180, 270 deg of date)
* moon phases (almanac.moon_phases: apparent geocentric elongation in ecliptic longitude
  = 0, 90, 180, 270 deg); full moon = 180 deg
* sunrise / sunset / twilight for any place

Ephemeris search order: ./ephem/ (next to this file), then the folder named by the
environment variable SKY_EPHEM_DIR; de440.bsp (1550-2650) is preferred over de440s.bsp
(1849-12-26 .. 2150-01-22) when present. If neither is found, de440s.bsp is downloaded
from JPL into ./ephem/.
"""
from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache

import numpy as np
from skyfield import almanac
from skyfield.api import Loader, wgs84

HERE = os.path.dirname(os.path.abspath(__file__))
EPHEM_DIR = os.path.join(HERE, "ephem")
EPHEM_NAMES = ("de440.bsp", "de440s.bsp")

# Church of the Holy Sepulchre (Anastasis), Jerusalem.
JERUSALEM = {"name": "Jerusalem (Church of the Holy Sepulchre)", "lat": 31.7784, "lon": 35.2296,
             "elev": 760.0, "tz": "Asia/Jerusalem"}


class EphemerisMissing(RuntimeError):
    pass


def _search_dirs() -> list[str]:
    dirs = [EPHEM_DIR]
    env = os.environ.get("SKY_EPHEM_DIR")
    if env:
        dirs.append(env)
    return dirs


@lru_cache(maxsize=1)
def load():
    """Return (timescale, ephemeris, filename)."""
    for d in _search_dirs():
        for name in EPHEM_NAMES:
            if os.path.exists(os.path.join(d, name)):
                loader = Loader(d, verbose=False)
                return loader.timescale(builtin=True), loader(name), name
    os.makedirs(EPHEM_DIR, exist_ok=True)
    loader = Loader(EPHEM_DIR, verbose=False)
    ts = loader.timescale(builtin=True)
    try:
        url = "https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de440s.bsp"
        loader.download(url, filename="de440s.bsp")
        return ts, loader("de440s.bsp"), "de440s.bsp"
    except Exception as exc:  # pragma: no cover - network failure
        raise EphemerisMissing(
            "The JPL ephemeris file de440s.bsp is missing and could not be downloaded "
            f"({exc}). Put de440s.bsp into the 'ephem' folder or set SKY_EPHEM_DIR.") from exc


def ephemeris_range() -> tuple[date, date]:
    """First and last whole UTC dates covered by the loaded ephemeris."""
    ts, eph, name = load()
    seg = eph.segments[0].spk_segment
    t0 = ts.tdb_jd(seg.start_jd)
    t1 = ts.tdb_jd(seg.end_jd)
    return t0.utc_datetime().date() + timedelta(days=1), t1.utc_datetime().date() - timedelta(days=1)


def covers(d: date) -> bool:
    lo, hi = ephemeris_range()
    return lo <= d <= hi


def bodies():
    ts, eph, _ = load()
    return ts, eph, eph["earth"], eph["sun"], eph["moon"]


def _clamp_dates(start: date, end: date) -> tuple[date, date]:
    lo, hi = ephemeris_range()
    return max(start, lo), min(end, hi)


def moon_phase_events(start: date, end: date) -> list[tuple[datetime, int]]:
    """(UTC datetime, phase) with phase 0 new, 1 first quarter, 2 full, 3 last quarter."""
    ts, eph, *_ = bodies()
    start, end = _clamp_dates(start, end)
    t, y = almanac.find_discrete(ts.utc(start.year, start.month, start.day),
                                 ts.utc(end.year, end.month, end.day), almanac.moon_phases(eph))
    return [(ti.utc_datetime(), int(yi)) for ti, yi in zip(t, y)]


def full_moons(start: date, end: date) -> list[datetime]:
    return [t for t, k in moon_phase_events(start, end) if k == 2]


SEASON_NAMES = ["March equinox", "June solstice", "September equinox", "December solstice"]


def seasons(start: date, end: date) -> list[tuple[datetime, int]]:
    """(UTC datetime, k) with k 0=March equinox, 1=June solstice, 2=Sept equinox, 3=Dec solstice."""
    ts, eph, *_ = bodies()
    start, end = _clamp_dates(start, end)
    t, y = almanac.find_discrete(ts.utc(start.year, start.month, start.day),
                                 ts.utc(end.year, end.month, end.day), almanac.seasons(eph))
    return [(ti.utc_datetime(), int(yi)) for ti, yi in zip(t, y)]


def moon_illumination(when_utc: list[datetime]) -> np.ndarray:
    """Illuminated fraction of the Moon (geocentric) at the given UTC datetimes."""
    ts, eph, *_ = bodies()
    return almanac.fraction_illuminated(eph, "moon", ts.from_datetimes(when_utc))


def moon_elongation(when_utc: list[datetime]) -> np.ndarray:
    """Moon minus Sun apparent ecliptic longitude of date, 0..360 deg (0 new, 180 full)."""
    from skyfield.framelib import ecliptic_frame
    ts, eph, earth, sun, moon = bodies()
    t = ts.from_datetimes(when_utc)
    e = earth.at(t)
    _, ls, _ = e.observe(sun).apparent().frame_latlon(ecliptic_frame)
    _, lm, _ = e.observe(moon).apparent().frame_latlon(ecliptic_frame)
    return (lm.degrees - ls.degrees) % 360.0


def observer(lat: float, lon: float, elev: float = 0.0):
    return wgs84.latlon(lat, lon, elevation_m=elev)


def sun_events(lat: float, lon: float, start_utc: datetime, end_utc: datetime,
               horizon: float = -0.8333) -> tuple[list[datetime], list[datetime]]:
    """Risings and settings (UTC) of the Sun's centre through `horizon` degrees
    (-0.8333 = upper limb on a sea-level horizon with standard refraction)."""
    ts, eph, earth, sun, moon = bodies()
    obs = earth + observer(lat, lon)
    t0, t1 = ts.from_datetime(start_utc), ts.from_datetime(end_utc)
    tr, yr = almanac.find_risings(obs, sun, t0, t1, horizon_degrees=horizon)
    tsun, ys = almanac.find_settings(obs, sun, t0, t1, horizon_degrees=horizon)
    rises = [t.utc_datetime() for t, ok in zip(tr, yr) if ok]
    sets = [t.utc_datetime() for t, ok in zip(tsun, ys) if ok]
    return rises, sets


def meridian_transits(lat: float, lon: float, start_utc: datetime, end_utc: datetime):
    """(upper transits, lower transits) of the Sun, UTC."""
    ts, eph, earth, sun, moon = bodies()
    t, y = almanac.find_discrete(ts.from_datetime(start_utc), ts.from_datetime(end_utc),
                                 almanac.meridian_transits(eph, sun, observer(lat, lon)))
    up = [ti.utc_datetime() for ti, yi in zip(t, y) if yi == 1]
    low = [ti.utc_datetime() for ti, yi in zip(t, y) if yi == 0]
    return up, low


def sun_altaz(lat: float, lon: float, when_utc: datetime) -> tuple[float, float]:
    """Apparent topocentric altitude and azimuth (deg, azimuth from true north) of the Sun."""
    ts, eph, earth, sun, moon = bodies()
    obs = earth + observer(lat, lon)
    alt, az, _ = obs.at(ts.from_datetime(when_utc)).observe(sun).apparent().altaz()
    return float(alt.degrees), float(az.degrees)
