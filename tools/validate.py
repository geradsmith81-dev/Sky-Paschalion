"""
Validation of the Sky Paschalion engine. Run from the engine folder:
    python tools/validate.py            (writes tools/validation_results.json)
Needs: python-dateutil, convertdate, ethiopian-date (pip) and de440s.bsp in ./ephem or SKY_EPHEM_DIR.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import calendars as C          # noqa: E402
import paschalion as P         # noqa: E402
import sky_engine as se        # noqa: E402
import sky_layer as SL         # noqa: E402
from convertdate import coptic as cd_coptic, julian as cd_julian  # noqa: E402
from dateutil import easter as du  # noqa: E402
from ethiopian_date import EthiopianDateConverter as ETH  # noqa: E402

R: dict = {}
T0 = time.time()


def daterange(a: date, b: date):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)


def ymd(c):
    return (c.year, c.month, c.day)


# 1. computistic Easter vs dateutil ------------------------------------------------------------
ys = range(1583, 2300)
w = sum(P.easter(y, "western") == du.easter(y, du.EASTER_WESTERN) for y in ys)
e = sum(P.easter(y, "eastern") == du.easter(y, du.EASTER_ORTHODOX) for y in ys)
ej = sum(ymd(P.eastern_easter_julian(y)) == ymd(du.easter(y, du.EASTER_JULIAN)) for y in ys)
pfm_ok = {"western": 0, "eastern": 0}
sunday_ok = {"western": 0, "eastern": 0}
pfm_range = {}
for r in ("western", "eastern"):
    offs = []
    for y in ys:
        ea, pf = P.easter(y, r), P.paschal_full_moon(y, r)
        sunday_ok[r] += ea.weekday() == 6
        pfm_ok[r] += 1 <= (ea - pf).days <= 7
        offs.append((pf - P.ecclesiastical_equinox(y, r)).days)
    pfm_range[r] = [min(offs), max(offs)]
R["easter_vs_dateutil"] = {"years": "1583-2299", "n": len(ys), "western_method3": w,
                           "eastern_method2_gregorian": e, "eastern_method1_julian": ej,
                           "easter_is_sunday": sunday_ok, "easter_minus_pfm_in_1_7": pfm_ok,
                           "pfm_minus_ecclesiastical_equinox_days_range": pfm_range}
R["western_eastern_same_day_1583_2299"] = sum(P.easter(y, "western") == P.easter(y, "eastern") for y in ys)
R["western_eastern_same_day_1900_2099"] = sum(P.easter(y, "western") == P.easter(y, "eastern")
                                              for y in range(1900, 2100))

# 2. astronomical Easter 1850-2149 -------------------------------------------------------------
ya = range(1850, 2150)
rows = [P.astronomical_detail(y, "lmt") for y in ya]
ast = {d["year"]: d["easter"] for d in rows}
W = {y: P.easter(y, "western") for y in ya}
E = {y: P.easter(y, "eastern") for y in ya}
diff_w, diff_e = {}, {}
for y in ya:
    k = (ast[y] - W[y]).days
    diff_w[k] = diff_w.get(k, 0) + 1
    k = (ast[y] - E[y]).days
    diff_e[k] = diff_e.get(k, 0) + 1
ist_years = [y for y in ya if P.astronomical_easter(y, "ist") != ast[y]]
utc_years = [y for y in ya if P.astronomical_easter(y, "utc") != ast[y]]
# date-based variant: accept a full moon whose Jerusalem DATE equals the equinox DATE even if it
# precedes the equinox instant
date_based_diff = []
for d in rows:
    y = d["year"]
    eq_date = (d["equinox_utc"] + P.LMT_OFFSET).date()
    prev = [t for t in se.full_moons(date(y, 2, 1), date(y, 3, 31)) if t < d["equinox_utc"]]
    if prev and (prev[-1] + P.LMT_OFFSET).date() >= eq_date:
        alt = P._next_sunday_after((prev[-1] + P.LMT_OFFSET).date())
        date_based_diff.append({"year": y, "instant_rule": str(d["easter"]), "date_rule": str(alt)})
knife = []
for d in rows:
    if d["knife_edge_hours"] < 1.0:
        y = d["year"]
        knife.append({"year": y, "easter": str(d["easter"]),
                      "equinox_utc": d["equinox_utc"].strftime("%Y-%m-%d %H:%M"),
                      "full_moon_utc": d["full_moon_utc"].strftime("%Y-%m-%d %H:%M"),
                      "full_moon_jerusalem_lmt": d["full_moon_local"].strftime("%Y-%m-%d %H:%M %a"),
                      "h_from_sat_sun_midnight": round(d["hours_from_saturday_midnight"], 2),
                      "h_fm_after_equinox": round(d["hours_fm_after_equinox"], 2),
                      "h_prev_fm_before_equinox": round(d["hours_prev_fm_before_equinox"], 2),
                      "western": str(W[y]), "eastern": str(E[y])})
R["astronomical"] = {"years": "1850-2149", "n": len(ya),
                     "equal_western": sum(ast[y] == W[y] for y in ya),
                     "equal_eastern": sum(ast[y] == E[y] for y in ya),
                     "equal_both": sum(ast[y] == W[y] == E[y] for y in ya),
                     "equal_neither": sum(ast[y] != W[y] and ast[y] != E[y] for y in ya),
                     "astro_minus_western_days": dict(sorted(diff_w.items())),
                     "astro_minus_eastern_days": dict(sorted(diff_e.items())),
                     "differs_if_IST_UTC+2": len(ist_years), "IST_years": ist_years,
                     "differs_if_UTC": len(utc_years), "UTC_years": utc_years,
                     "date_based_equinox_rule_differs": date_based_diff,
                     "knife_edge_lt_1h": knife,
                     "knife_edge_lt_2h_years": [d["year"] for d in rows if d["knife_edge_hours"] < 2.0],
                     "western_diverge_2001_2149": [y for y in range(2001, 2150) if ast[y] != W[y]]}

# WCC Aleppo 1997 table: (astronomical Easter, vernal full moon on the Jerusalem meridian), Gregorian dates.
# Source: English Wikipedia "Template:Table of dates of Easter", revision 1295050452, fetched 15 Nov 2026 via the
# MediaWiki API and saved verbatim in tools/ref/. The template cites WCC/MECC, "Towards a Common Date for Easter",
# Aleppo, 10 March 1997. The WCC report's own table covers 2001-2025; Wikipedia extends it to 2045
# (rows 2026-2045 are Wikipedia's own extension and are checked separately as WCC_EXT).
import re as _re, pathlib as _pl
_MON = {"March": 3, "April": 4, "May": 5}
_wt = (_pl.Path(__file__).parent / "ref" / "wikipedia_Table_of_dates_of_Easter_rev1295050452.wikitext").read_text(encoding="utf8")
_rows = _re.findall(r"\|y=(\d{4})\|([A-Za-z]+ \d+)\|([A-Za-z]+ \d+)\|", _wt)
def _md(s):
    m, d = s.split()
    return f"{_MON[m]:02d}-{int(d):02d}"
_ALL = {int(y): (_md(ea), _md(fm)) for y, fm, ea in _rows}
WCC = {y: v for y, v in _ALL.items() if 2001 <= y <= 2025}
WCC_EXT = {y: v for y, v in _ALL.items() if y > 2025}
assert len(WCC) == 25, len(WCC)
wcc_e = wcc_f = 0
wcc_rows = []
for y, (ea, fm) in WCC.items():
    d = P.astronomical_detail(y, "lmt")
    ok_e = str(d["easter"])[5:] == ea
    ok_f = str(d["full_moon_local_date"])[5:] == fm
    wcc_e += ok_e
    wcc_f += ok_f
    if not (ok_e and ok_f):
        wcc_rows.append({"year": y, "table_easter": ea, "engine_easter": str(d["easter"]),
                         "table_fm": fm, "engine_fm_lmt": d["full_moon_local"].strftime("%m-%d %H:%M"),
                         "engine_fm_utc": d["full_moon_utc"].strftime("%m-%d %H:%M"),
                         "equinox_utc": d["equinox_utc"].strftime("%m-%d %H:%M")})
R["wcc_table_2001_2025"] = {"n": len(WCC), "easter_match": wcc_e, "full_moon_date_match": wcc_f,
                            "mismatches": wcc_rows}
ext_e = ext_f = 0
ext_rows = []
for y, (ea, fm) in WCC_EXT.items():
    d = P.astronomical_detail(y, "lmt")
    ok_e = str(d["easter"])[5:] == ea
    ok_f = str(d["full_moon_local_date"])[5:] == fm
    ext_e += ok_e
    ext_f += ok_f
    if not (ok_e and ok_f):
        ext_rows.append({"year": y, "table_easter": ea, "engine_easter": str(d["easter"]),
                         "table_fm": fm, "engine_fm_lmt": d["full_moon_local"].strftime("%m-%d %H:%M"),
                         "engine_fm_utc": d["full_moon_utc"].strftime("%m-%d %H:%M")})
R["wikipedia_extension_2026_2045"] = {"n": len(WCC_EXT), "easter_match": ext_e,
                                      "full_moon_date_match": ext_f, "mismatches": ext_rows}

# 3. calendars, every day 1850-2149 -------------------------------------------------------------
a, b = date(1850, 1, 1), date(2149, 12, 31)
cnt = dict(days=0, coptic=0, coptic_back=0, julian=0, julian_back=0,
           ethiopian_vs_convertdate_coptic_plus_276=0, ethiopian_pkg_comparable=0,
           ethiopian_pkg_not_comparable=0, ethiopian=0, ethiopian_back=0, byzantine=0)
eth_err = []
eth_mis_years = set()
for d in daterange(a, b):
    cnt["days"] += 1
    jd = C.jdn_of(d)
    # convertdate uses astronomical JD: civil day with JDN n starts at JD n - 0.5
    c = C.from_jdn("coptic", jd)
    cnt["coptic"] += ymd(c) == tuple(cd_coptic.from_jd(jd - 0.5))
    cnt["coptic_back"] += int(cd_coptic.to_jd(*ymd(c)) + 0.5) == jd
    jj = C.from_jdn("julian", jd)
    cnt["julian"] += ymd(jj) == tuple(cd_julian.from_jd(jd - 0.5))
    cnt["julian_back"] += int(cd_julian.to_jd(*ymd(jj)) + 0.5) == jd
    et = C.from_jdn("ethiopian", jd)
    # independent epoch check: Ethiopian = convertdate Coptic with year + 276
    cy, cm, cdd = cd_coptic.from_jd(jd - 0.5)
    cnt["ethiopian_vs_convertdate_coptic_plus_276"] += ymd(et) == (cy + 276, cm, cdd)
    # ethiopian-date 1.0 returns datetime.date, so it cannot express month 13 or days 29-31 of
    # some months; those days are counted as not comparable.
    try:
        r = ETH.to_ethiopian(d.year, d.month, d.day)
        cnt["ethiopian_pkg_comparable"] += 1
        same = ymd(et) == (r.year, r.month, r.day)
        cnt["ethiopian"] += same
        if not same:
            eth_mis_years.add(d.year)
        g = ETH.to_gregorian(*ymd(et))
        cnt["ethiopian_back"] += (g.year, g.month, g.day) == ymd(d)
    except Exception as exc:  # recorded, not hidden
        cnt["ethiopian_pkg_not_comparable"] += 1
        if len(eth_err) < 3:
            eth_err.append(f"{d} -> {ymd(et)}: {exc!r}")
    bz = C.from_jdn("byzantine", jd)
    cnt["byzantine"] += (C.BYZ_TO_JULIAN_MONTH[bz.month] == jj.month and bz.day == jj.day and
                         bz.year == (jj.year + 5509 if jj.month >= 9 else jj.year + 5508))
cnt["ethiopian_pkg_errors_sample"] = eth_err
cnt["ethiopian_pkg_mismatch_years"] = sorted(eth_mis_years)
# Genna (Ethiopian Nativity, 29 Tahsas) - expected 7 January Gregorian in 1900-2099, 8 January in
# the Ethiopian year after an Ethiopian leap year (as for Coptic 29 Koiak)
genna = {}
for gy in range(1900, 2100):
    ey = C.from_gregorian("ethiopian", date(gy, 1, 7)).year
    g = C.to_gregorian(C.CDate(ey, 4, 29, "ethiopian"))
    genna[f"{g.day} Jan"] = genna.get(f"{g.day} Jan", 0) + 1
cnt["genna_29_tahsas_1900_2099"] = genna
cnt["genna_1901_engine"] = str(C.to_gregorian(C.CDate(1893, 4, 29, "ethiopian")))
_r = ETH.to_gregorian(1893, 4, 29)
cnt["genna_1901_ethiopian_date_pkg"] = f"{_r.year:04d}-{_r.month:02d}-{_r.day:02d}"
R["calendars_daily_1850_2149"] = cnt

# round trips: every calendar, every day 1583-2299, and every 13th day 0002-9999
rt_n, rt_fail = 0, {k: 0 for k in C.CALENDARS}
for d in daterange(date(1583, 1, 1), date(2299, 12, 31)):
    rt_n += 1
    for k in C.CALENDARS:
        rt_fail[k] += C.to_gregorian(C.from_gregorian(k, d)) != d
wide_n, wide_fail = 0, {k: 0 for k in C.CALENDARS}
o = date(2, 1, 1).toordinal()
while o < date(9999, 12, 31).toordinal():
    d = date.fromordinal(o)
    wide_n += 1
    for k in C.CALENDARS:
        cd = C.from_gregorian(k, d)
        wide_fail[k] += (C.to_gregorian(cd) != d or not 1 <= cd.day <= C.month_length(k, cd.year, cd.month))
    o += 13
R["roundtrip"] = {"daily_1583_2299_days": rt_n, "fail": rt_fail,
                  "every_13th_day_0002_9999": wide_n, "wide_fail": wide_fail}

# Revised Julian -------------------------------------------------------------------------------
rj_days = 0
rj_eq = 0
for d in daterange(date(1600, 3, 1), date(2799, 2, 28)):
    rj_days += 1
    rj_eq += ymd(C.from_gregorian("revised_julian", d)) == ymd(d)


def rj_ml(yy, mm):
    if mm == 2:
        return 29 if (yy % 4 == 0 and (yy % 100 != 0 or yy % 900 in (200, 600))) else 28
    return [31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mm - 1]


# independent reference: walk day by day from 1 Jan 2000 (RJ = Gregorian) using month lengths only
y_, m_, d_ = 2000, 1, 1
cur, ref_n, ref_ok = date(2000, 1, 1), 0, 0
while cur <= date(9999, 12, 31):
    ref_n += 1
    ref_ok += ymd(C.from_gregorian("revised_julian", cur)) == (y_, m_, d_)
    d_ += 1
    if d_ > rj_ml(y_, m_):
        d_, m_ = 1, m_ + 1
        if m_ > 12:
            m_, y_ = 1, y_ + 1
    if cur == date(9999, 12, 31):
        break
    cur += timedelta(days=1)
spot = {}
for g in (date(2800, 2, 28), date(2800, 2, 29), date(2800, 3, 1), date(2900, 2, 28), date(2900, 3, 1),
          date(3200, 3, 1), date(3300, 3, 1)):
    c = C.from_gregorian("revised_julian", g)
    spot[str(g)] = f"{c.year:04d}-{c.month:02d}-{c.day:02d}"
R["revised_julian"] = {"equal_gregorian_1600-03-01_2799-02-28": rj_eq, "days": rj_days,
                       "daybyday_reference_2000_9999_match": ref_ok, "reference_days": ref_n,
                       "spot": spot,
                       "leap_centuries_2000_4000": [y for y in range(2000, 4001, 100)
                                                    if C.is_leap("revised_julian", y)]}

# anchors --------------------------------------------------------------------------------------
cop_years = range(1567, 1866)  # Coptic years whose 1 Thout falls in 1850..2148
nay_julian_ok = 0
nay = {"n": 0, "rule_ok": 0}
for cy in cop_years:
    g = C.year_start("coptic", cy)
    jj = C.from_gregorian("julian", g)
    nay_julian_ok += (jj.month, jj.day) == (8, 30 if C.is_leap("julian", jj.year + 1) else 29)
    if 1900 <= g.year <= 2099:
        nay["n"] += 1
        nay[f"{g.day} Sep"] = nay.get(f"{g.day} Sep", 0) + 1
        nay["rule_ok"] += (g.month, g.day) == (9, 12 if (g.year + 1) % 4 == 0 else 11)
enk_same = sum(C.year_start("ethiopian", cy + 276) == C.year_start("coptic", cy) for cy in cop_years)
nat = {"n": 0, "8_jan_only_in_gregorian_leap_years": True}
nat28 = 0
for gy in range(1900, 2100):
    cy = C.from_gregorian("coptic", date(gy, 1, 7)).year
    g = C.to_gregorian(C.CDate(cy, 4, 29, "coptic"))
    nat["n"] += 1
    nat[f"{g.day} Jan"] = nat.get(f"{g.day} Jan", 0) + 1
    if g.day == 8:
        nat["8_jan_only_in_gregorian_leap_years"] &= gy % 4 == 0
        nat28 += C.to_gregorian(C.CDate(cy, 4, 28, "coptic")) == date(gy, 1, 7)
nat["years_with_8_jan_where_28_koiak_is_7_jan"] = nat28
R["anchors"] = {
    "nayrouz_is_29_or_30_aug_julian": [nay_julian_ok, len(cop_years)],
    "nayrouz_gregorian_1900_2099": nay,
    "enkutatash_equals_nayrouz": [enk_same, len(cop_years)],
    "coptic_29_koiak_1900_2099": nat,
    "nayrouz_2025": str(C.year_start("coptic", 1742)),
    "enkutatash_2025": str(C.year_start("ethiopian", 2018)),
    "byzantine": {"AM_7534_starts": str(C.year_start("byzantine", 7534)),
                  "2026-01-01": str(C.from_gregorian("byzantine", date(2026, 1, 1))),
                  "2026-09-14": str(C.from_gregorian("byzantine", date(2026, 9, 14))),
                  "indiction_7534": C.indiction(7534)},
    "coptic_epoch_julian": str(C.from_gregorian("julian", C.to_gregorian(C.CDate(1, 1, 1, "coptic")))),
    "ethiopian_epoch_julian": str(C.from_gregorian("julian", C.to_gregorian(C.CDate(1, 1, 1, "ethiopian")))),
}

# 4. movable cycle -----------------------------------------------------------------------------
WD = {"zacchaeus_sunday": 6, "publican_pharisee": 6, "septuagesima": 6, "nineveh_fast_start": 0,
      "meatfare_sunday": 6, "ash_wednesday": 2, "clean_monday": 0, "great_lent_start_coptic": 0,
      "lazarus_saturday": 5, "palm_sunday": 6, "holy_thursday": 3, "good_friday": 4, "holy_saturday": 5,
      "pascha": 6, "thomas_sunday": 6, "mid_pentecost": 2, "ascension": 3, "pentecost": 6,
      "trinity_sunday": 6, "all_saints_sunday": 6, "corpus_christi": 3, "sacred_heart": 4,
      "apostles_fast_start": 0}
mv_n = mv_bad = 0
missing = set()
for rule, yrs in (("western", ys), ("eastern", ys), ("astronomical", ya)):
    for y in yrs:
        m = P.movable(y, rule)
        missing |= set(WD) - set(m)
        for k, wd in WD.items():
            mv_n += 1
            mv_bad += m[k].weekday() != wd
R["movable_weekday_checks"] = {"checks": mv_n, "wrong": mv_bad, "missing_contract_keys": sorted(missing)}
af = {}
for style in ("julian", "revised_julian", "coptic"):
    lens = [P.apostles_fast_days(y, "eastern", style) for y in range(1900, 2100)]
    af[style] = {"min_days": min(lens), "max_days": max(lens), "years_omitted": sum(x == 0 for x in lens)}
R["apostles_fast_eastern_1900_2099"] = af
R["sample_2026"] = {r: {k: str(v) for k, v in P.movable(2026, r).items()} for r in P.RULES}

# 5. sky layer sanity --------------------------------------------------------------------------
sk = {}
st = SL.sun_times(date(2026, 3, 20), 31.7784, 35.2296, "Asia/Jerusalem")
sk["jerusalem_2026_03_20"] = {k: (v.strftime("%H:%M:%S") if isinstance(v, datetime) else v)
                              for k, v in st.items() if k != "date"}
hs = SL.canonical_hours(date(2026, 6, 21), 31.7784, 35.2296, "Asia/Jerusalem", "roman")
noon = SL.sun_times(date(2026, 6, 21), 31.7784, 35.2296, "Asia/Jerusalem")["solar_noon"]
sext = [h for h in hs if h["key"] == "sext"][0]["start"]
sk["sext_minus_solar_noon_s_jerusalem_2026_06_21"] = round((sext - noon).total_seconds(), 1)
th = SL.temporal_hours(date(2026, 12, 21), 51.5, -0.12, "Europe/London")
sk["london_2026_12_21_day_hour_min"] = round(th[0]["length_min"], 2)
sk["london_2026_12_21_night_hour_min"] = round(th[12]["length_min"], 2)
sk["bearing_to_jerusalem"] = {"Rome": round(SL.bearing_to_jerusalem(41.9022, 12.4533), 2),
                              "Moscow": round(SL.bearing_to_jerusalem(55.7558, 37.6173), 2),
                              "Addis Ababa": round(SL.bearing_to_jerusalem(9.03, 38.74), 2),
                              "New York": round(SL.bearing_to_jerusalem(40.7128, -74.006), 2)}
sk["sunrise_azimuth_2026_03_20_equator"] = round(SL.sunrise_azimuth(date(2026, 3, 20), 0.0, 30.0,
                                                                     "Africa/Kampala"), 2)
sk["tromso_2026_06_21_polar"] = SL.sun_times(date(2026, 6, 21), 69.65, 18.96, "Europe/Oslo")["polar"]
ok_order = n_order = 0
for sysn in SL.HOURS_SYSTEMS:
    for dd in (date(2026, 3, 20), date(2026, 6, 21), date(2026, 12, 21)):
        for lat, lon, tz in ((31.7784, 35.2296, "Asia/Jerusalem"), (59.94, 30.31, "Europe/Moscow"),
                             (-33.87, 151.21, "Australia/Sydney")):
            h = SL.canonical_hours(dd, lat, lon, tz, sysn)
            n_order += 1
            ok_order += all(h[i]["start"] <= h[i + 1]["start"] for i in range(len(h) - 1))
sk["canonical_hours_non_decreasing"] = [ok_order, n_order]
mp = SL.moon_phase(datetime(2025, 4, 13, 0, 22, tzinfo=timezone.utc))
sk["moon_phase_at_2025_paschal_fm"] = {"name": mp["phase_name"], "elongation": round(mp["elongation_deg"], 2),
                                       "illumination": round(mp["illumination"], 4)}
R["sky"] = sk
R["runtime_s"] = round(time.time() - T0, 1)
R["ephemeris"] = se.load()[2]
R["generated_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

with open(os.path.join(HERE, "validation_results.json"), "w", encoding="utf-8") as f:
    json.dump(R, f, indent=1, default=str, ensure_ascii=False)
print(json.dumps({k: R[k] for k in ("easter_vs_dateutil", "wcc_table_2001_2025", "runtime_s")}, default=str))
