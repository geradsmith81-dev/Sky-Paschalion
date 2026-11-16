"""Place search (GeoNames cities with 15,000+ people, via geonamescache) with time zones, and the preset places.

Preset coordinates are city centres (rounded to 4 decimals; checked against the GeoNames entries by
tools/apptest_sweep.py); Jerusalem is the Church of the Holy Sepulchre, the reference point of the engine.
"""
from __future__ import annotations

import unicodedata
from functools import lru_cache

# name, country, lat, lon, tz, note (the see or church it stands for)
_P = [
    ("Jerusalem", "IL", 31.7784, 35.2296, "Asia/Jerusalem", "Church of the Holy Sepulchre; Patriarchates of Jerusalem"),
    ("Rome", "IT", 41.8919, 12.5113, "Europe/Rome", "Holy See"),
    ("Istanbul (Constantinople)", "TR", 41.0082, 28.9784, "Europe/Istanbul", "Ecumenical Patriarchate"),
    ("Alexandria", "EG", 31.2001, 29.9187, "Africa/Cairo", "See of St Mark"),
    ("Antakya (Antioch)", "TR", 36.2021, 36.1600, "Europe/Istanbul", "the ancient see of Antioch"),
    ("Moscow", "RU", 55.7558, 37.6173, "Europe/Moscow", "Patriarchate of Moscow"),
    ("Vagharshapat (Etchmiadzin)", "AM", 40.1656, 44.2925, "Asia/Yerevan", "Mother See of Holy Etchmiadzin"),
    ("Cairo", "EG", 30.0444, 31.2357, "Africa/Cairo", "Coptic Orthodox Patriarchate"),
    ("Addis Ababa", "ET", 9.0250, 38.7469, "Africa/Addis_Ababa", "Ethiopian Orthodox Tewahedo Church"),
    ("Asmara", "ER", 15.3229, 38.9251, "Africa/Asmara", "Eritrean Orthodox Tewahedo Church"),
    ("Damascus", "SY", 33.5138, 36.2765, "Asia/Damascus", "Antiochian and Syriac Orthodox Patriarchates"),
    ("Beirut", "LB", 33.8938, 35.5018, "Asia/Beirut", "Maronite, Melkite, Armenian Catholic and Syriac Catholic sees"),
    ("Baghdad", "IQ", 33.3152, 44.3661, "Asia/Baghdad", "Chaldean Catholic Patriarchate; Ancient Church of the East"),
    ("Erbil", "IQ", 36.1911, 44.0092, "Asia/Baghdad", "Assyrian Church of the East"),
    ("Kottayam", "IN", 9.5916, 76.5222, "Asia/Kolkata", "Malankara churches"),
    ("Kyiv", "UA", 50.4501, 30.5234, "Europe/Kyiv", "Kyivan churches"),
    ("Bucharest", "RO", 44.4268, 26.1025, "Europe/Bucharest", "Romanian Orthodox Patriarchate"),
    ("Belgrade", "RS", 44.7866, 20.4489, "Europe/Belgrade", "Serbian Orthodox Patriarchate"),
    ("Sofia", "BG", 42.6977, 23.3219, "Europe/Sofia", "Bulgarian Orthodox Patriarchate"),
    ("Tbilisi", "GE", 41.7151, 44.8271, "Asia/Tbilisi", "Georgian Orthodox Patriarchate"),
    ("Athens", "GR", 37.9838, 23.7275, "Europe/Athens", "Church of Greece"),
    ("Nicosia", "CY", 35.1856, 33.3823, "Asia/Nicosia", "Church of Cyprus"),
    ("Warsaw", "PL", 52.2297, 21.0122, "Europe/Warsaw", "Polish Orthodox Church"),
    ("Tirana", "AL", 41.3275, 19.8187, "Europe/Tirane", "Orthodox Autocephalous Church of Albania"),
    ("Prague", "CZ", 50.0755, 14.4378, "Europe/Prague", "Orthodox Church of the Czech Lands and Slovakia"),
    ("Helsinki", "FI", 60.1699, 24.9384, "Europe/Helsinki", "Orthodox Church of Finland"),
    ("London", "GB", 51.5074, -0.1278, "Europe/London", ""),
    ("Paris", "FR", 48.8566, 2.3522, "Europe/Paris", ""),
    ("New York", "US", 40.7128, -74.0060, "America/New_York", ""),
    ("Chicago", "US", 41.8781, -87.6298, "America/Chicago", ""),
    ("Los Angeles", "US", 34.0522, -118.2437, "America/Los_Angeles", ""),
    ("Toronto", "CA", 43.6532, -79.3832, "America/Toronto", ""),
    ("Buenos Aires", "AR", -34.6037, -58.3816, "America/Argentina/Buenos_Aires", ""),
    ("Johannesburg", "ZA", -26.2041, 28.0473, "Africa/Johannesburg", ""),
    ("Melbourne", "AU", -37.8136, 144.9631, "Australia/Melbourne", ""),
    ("Tromsø", "NO", 69.6492, 18.9553, "Europe/Oslo", "Arctic: midnight Sun and polar night"),
]
PRESETS = [{"name": n, "country": cc, "lat": la, "lon": lo, "tz": tz, "note": note, "label": n}
           for n, cc, la, lo, tz, note in _P]
BY_NAME = {p["name"]: p for p in PRESETS}
DEFAULT = "Jerusalem"


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()


@lru_cache(maxsize=1)
def _cities() -> list[dict]:
    try:
        import geonamescache
    except ImportError:
        return []
    gc = geonamescache.GeonamesCache()
    countries = gc.get_countries()
    states = gc.get_us_states()
    out = []
    for c in gc.get_cities().values():
        cc = c["countrycode"]
        region = states.get(c.get("admin1code", ""), {}).get("name", "") if cc == "US" else ""
        out.append({"name": c["name"], "country": cc,
                    "country_name": countries.get(cc, {}).get("name", cc), "region": region,
                    "lat": float(c["latitude"]), "lon": float(c["longitude"]), "tz": c["timezone"],
                    "pop": int(c["population"]), "key": _norm(c["name"]),
                    "alt": "|" + "|".join(_norm(a) for a in c.get("alternatenames", []) if a) + "|"})
    out.sort(key=lambda r: -r["pop"])
    return out


def search(query: str, limit: int = 12) -> list[dict]:
    """Exact name matches first, then alternate names, then prefixes; larger cities first."""
    q = _norm(query)
    if not q:
        return []
    cities = _cities()
    exact = [c for c in cities if c["key"] == q]
    alt = [c for c in cities if c["key"] != q and f"|{q}|" in c["alt"]]
    pref = [c for c in cities if c["key"] != q and c["key"].startswith(q) and f"|{q}|" not in c["alt"]]
    seen, out = set(), []
    for c in exact + alt + pref:
        k = (c["name"], c["country"], round(c["lat"], 2))
        if k not in seen:
            seen.add(k)
            out.append(c)
        if len(out) >= limit:
            break
    return out


def label(p: dict) -> str:
    parts = [p["name"]]
    if p.get("region"):
        parts.append(p["region"])
    parts.append(p.get("country_name") or p.get("country", ""))
    return ", ".join(x for x in parts if x)
