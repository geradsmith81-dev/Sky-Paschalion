# Sky Paschalion engine: VALIDATION

Generated 2026-11-15 18:39 UTC by `tools/validate.py` (results in `tools/validation_results.json`), ephemeris `de440s.bsp` (JPL DE440s via Skyfield 1.54), runtime 118.6 s. Every number below is copied from that file. Fast unit tests: `tests/test_engine.py`, 8/8 passed.

## 1. Easter computus vs python-dateutil (1583–2299, 717 years)

| Check | Matches |
|---|---|
| `easter(y,'western')` = `dateutil.easter(y, EASTER_WESTERN)` (method 3) | 717 / 717 |
| `easter(y,'eastern')` = `dateutil.easter(y, EASTER_ORTHODOX)` (method 2, Gregorian date) | 717 / 717 |
| Julian-calendar Pascha `eastern_easter_julian(y)` = `dateutil.easter(y, EASTER_JULIAN)` (method 1) | 717 / 717 |
| Easter is a Sunday (western / eastern) | 717 / 717 |
| 1 ≤ Easter − ecclesiastical PFM ≤ 7 days (western / eastern) | 717 / 717 |
| PFM − ecclesiastical equinox (21 March of the rule's calendar), days | western [0, 28], eastern [0, 28] (expected 0..28) |

The engine's algorithms are independent of dateutil's: Western uses the Meeus/Butcher 'anonymous' algorithm, and Eastern uses Meeus' Julian algorithm followed by a JDN conversion. dateutil uses Oudin's formulation. The ecclesiastical PFM uses the Oudin/Clavius epact (`21 March + i`).
Western and Eastern Easter fall on the same day in 226 of 717 years (1583–2299) and in 57 of 200 years (1900–2099).

## 2. Astronomical Easter (WCC Aleppo 1997), 1850–2149 (300 years, the DE440s range)

Rule as implemented: March equinox instant and the first full-moon instant at or after it come from DE440s (apparent geocentric ecliptic longitude). The full moon's date is taken in local mean time of the Jerusalem meridian, 35.2296° E (UTC + 2 h 20 min 55 s). Easter is the first Sunday strictly after that date.

| Agreement | Years |
|---|---|
| astronomical = Western | 269 |
| astronomical = Eastern | 90 |
| astronomical = both (Western = Eastern) | 77 |
| astronomical = neither | 18 |

Astronomical − Western, days → years: {'-28': 10, '-7': 6, '0': 269, '7': 15}. Astronomical − Eastern: {'-35': 74, '-28': 16, '-7': 120, '0': 90}.
Years 2001–2149 where astronomical ≠ Western: 2019, 2038, 2045, 2049, 2057, 2069, 2076, 2089, 2095, 2096, 2106, 2114, 2119, 2120, 2133, 2143, 2147. For 2045 the engine gives 2045-04-02, one week before both Western (2045-04-09) and Eastern (2045-04-09).

**Meridian sensitivity.** Reckoning the full-moon date in UTC+2 (Israel Standard Time) instead of Jerusalem LMT changes Easter in 1 year (1873). Reckoning it in UTC changes Easter in 4 years (1873, 1998, 2120, 2143).

**Equinox comparison.** The engine compares instants (full moon ≥ equinox). A date-based reading would also accept a full moon on the equinox's Jerusalem date even if it came a few hours earlier. That reading would change Easter in 5 years: 1886 (1886-04-25 → 1886-03-21); 1905 (1905-04-23 → 1905-03-26); 1981 (1981-04-26 → 1981-03-22); 2000 (2000-04-23 → 2000-03-26); 2068 (2068-04-22 → 2068-03-25).

### Knife-edge years (margin < 1 h)

The margin is the smaller of two gaps: from the full moon to the nearest Saturday→Sunday midnight (Jerusalem LMT), and from either of the two candidate full moons to the equinox. A margin under 1 hour means a different ephemeris, ΔT or meridian convention could move Easter by a week (by four or five weeks in equinox cases).

| Year | Full moon UTC | Full moon Jerusalem LMT | Margin (h) | Astronomical | Western | Eastern |
|---|---|---|---|---|---|---|
| 1869 | 1869-03-27 21:32 | 1869-03-27 23:53 Sat | -0.11 from Sat/Sun midnight | 1869-03-28 | 1869-03-28 | 1869-05-02 |
| 1873 | 1873-04-12 21:50 | 1873-04-13 00:11 Sun | +0.19 from Sat/Sun midnight | 1873-04-20 | 1873-04-13 | 1873-04-20 |
| 1974 | 1974-04-06 21:00 | 1974-04-06 23:21 Sat | -0.65 from Sat/Sun midnight | 1974-04-07 | 1974-04-14 | 1974-04-14 |
| 1998 | 1998-04-11 22:23 | 1998-04-12 00:44 Sun | +0.74 from Sat/Sun midnight | 1998-04-19 | 1998-04-12 | 1998-04-19 |
| 2120 | 2120-04-13 22:23 | 2120-04-14 00:44 Sun | +0.74 from Sat/Sun midnight | 2120-04-21 | 2120-04-14 | 2120-04-21 |
| 2123 | 2123-04-10 20:57 | 2123-04-10 23:18 Sat | -0.69 from Sat/Sun midnight | 2123-04-11 | 2123-04-11 | 2123-04-18 |

Years with margin < 2 h: 1869, 1873, 1971, 1974, 1981, 1998, 2120, 2123, 2143. No year in 1850–2149 has an equinox margin under 2 h, so all knife edges are Saturday/Sunday-midnight cases. For future years ΔT is extrapolated (Skyfield's built-in table), which adds an uncertainty that grows to several minutes by the 2100s. That matters only for years whose margin is that small, i.e. the knife-edge years listed here.

### WCC Aleppo 1997 table (2001–2025) and Wikipedia's extension (2026–2045)

Reference: English Wikipedia, "Template:Table of dates of Easter", revision 1295050452, fetched 15 Nov 2026 through the MediaWiki API and stored verbatim in `tools/ref/`. The template cites WCC/MECC, *Towards a Common Date for Easter*, Aleppo, 10 March 1997. The WCC report's own table covers 2001–2025; the rows for 2026–2045 are Wikipedia's extension and are reported separately. `tools/validate.py` parses the stored file, so no reference date is typed in by hand. (The WCC document itself returned HTTP 403 to automated requests and was not read.)

| Range | Rows | Astronomical Easter matches | Vernal full-moon date matches (Jerusalem LMT) |
|---|---|---|---|
| 2001–2025 (WCC table) | 25 | 25 | 24 |
| 2026–2045 (Wikipedia extension) | 20 | 20 | 17 |

Full-moon mismatches. In none of them does the Easter Sunday change:

| Year | Table | DE440s, Jerusalem LMT | DE440s, UTC |
|---|---|---|---|
| 2019 | 20 Mar | 21 Mar 04:03 | 21 Mar 01:42 (equinox 20 Mar 21:58 UTC) |
| 2026 | 3 Apr | 2 Apr 04:32 | 2 Apr 02:11 |
| 2029 | 29 Mar | 30 Mar 04:47 | 30 Mar 02:26 |
| 2030 | 17 Apr | 18 Apr 05:40 | 18 Apr 03:20 |

Every mismatched full moon falls more than 4 hours after local midnight on the Jerusalem meridian, so no meridian convention (LMT, UTC+2 or UTC) reproduces the table's date. In 2026 the table's date is *later* than the full moon. These rows look like errors in the reference table, not in the engine. The 2019 row matters to the rule: the full moon came about 4 hours after the equinox, which makes 2019 the one WCC-table year in which astronomical Easter (24 Mar) differs from Western Easter (21 Apr). The table and the engine agree on that Easter date.

## 3. Calendars

Every day 1850-01-01 … 2149-12-31 (109573 days):

| Check | Matches |
|---|---|
| Coptic vs convertdate 2.5.1 `coptic.from_jd` | 109573 / 109573 |
| Coptic → JD vs convertdate `coptic.to_jd` | 109573 / 109573 |
| Julian vs convertdate `julian.from_jd` / `to_jd` | 109573 / 109573 of 109573 |
| Ethiopian = convertdate Coptic with year + 276 | 109573 / 109573 |
| Byzantine AM = Julian date with AM = AD+5509 (Sep–Dec) / AD+5508 (Jan–Aug), month 1 = September | 109573 / 109573 |
| Ethiopian vs pip `ethiopian-date` 1.0 (comparable days only) | 102459 / 107471 |

`ethiopian-date` 1.0 returns `datetime.date` objects, so it cannot express Pagume (month 13) or days 29–30 of some months; 2102 days were not comparable. All of its 5012 disagreements fall in the Gregorian years 1901, 1902, 1903, 1904, 1905, 1906, 1907, 2101, 2102, 2103, 2104, 2105, 2106, 2107. In those years the package is one day off around the Gregorian non-leap centuries 1900 and 2100. Example: Genna 1893 (29 Tahsas), engine 1901-01-07, package 1901-01-06. The engine's 7 January agrees with the Julian 25 December rule, so the package is judged wrong here.

**Round trips** `to_gregorian(from_gregorian(cal, d)) == d`: every day 1583–2299 (261879 days × 6 calendars), failures {'gregorian': 0, 'julian': 0, 'revised_julian': 0, 'coptic': 0, 'ethiopian': 0, 'byzantine': 0}; every 13th day 0002–9999 (280900 days), failures {'gregorian': 0, 'julian': 0, 'revised_julian': 0, 'coptic': 0, 'ethiopian': 0, 'byzantine': 0}.

**Revised Julian** (convertdate has no Revised Julian module; two independent checks):
- equal to Gregorian on every day 1600-03-01 … 2799-02-28: 437925 / 437925;
- equal to a day-by-day walk from 1 Jan 2000 using only the Milanković month lengths, every day 2000–9999: 2921940 / 2921940;
- spot dates (Gregorian → RJ): 2800-02-28 → 2800-02-28, 2800-02-29 → 2800-03-01, 2800-03-01 → 2800-03-02, 2900-02-28 → 2900-02-29, 2900-03-01 → 2900-03-01, 3200-03-01 → 3200-03-02, 3300-03-01 → 3300-03-01;
- leap centuries 2000–4000: [2000, 2400, 2900, 3300, 3800] (year mod 900 ∈ {200, 600}).

**Anchors**
- Nayrouz (1 Thout) is 29 Aug Julian, or 30 Aug Julian before a Julian leap year, for 299 / 299 Coptic years beginning 1850–2148.
- Nayrouz 1900–2099 in Gregorian dates: 11 Sep 150 times, 12 Sep 50 times. The rule '12 Sep when the next Gregorian year is a leap year' holds 200 / 200 times. Nayrouz 2025 = 2025-09-11.
- Enkutatash (1 Meskerem) = Nayrouz in 299 / 299 years; Enkutatash 2025 = 2025-09-11 (Ethiopian 2018).
- 29 Koiak, 1900–2099: 7 Jan in 151 years, 8 Jan in 49 years. The 8 Jan years are exactly the Coptic years after a Coptic leap year (January of Gregorian leap years): True. In all 49 of them 28 Koiak = 7 Jan, matching the practice of keeping the Nativity on 28 Koiak in those years (Wikipedia 'Christmas' date table; The Coptist, 2025). Ethiopian Genna (29 Tahsas) has the same pattern: {'7 Jan': 151, '8 Jan': 49}.
- Byzantine: AM 7534 began 2025-09-14 (= 1 Sept 2025 Julian), indiction 4; 1 Jan 2026 = 19 4/7534 (byzantine); 14 Sep 2026 = 1 1/7535 (byzantine).
- Era epochs: 1 Thout AM 1 = 29 8/284 (julian); 1 Meskerem 1 Amete Mihret = 29 8/8 (julian).

## 4. Movable cycle
Weekday checks of all 23 contract keys, for western and eastern (1583–2299) and astronomical (1850–2149): 39882 checks, 0 wrong, missing keys [].
Apostles' Fast with eastern Pascha, 1900–2099 (fasting days = start … eve of the feast): Julian fixed calendar 8–42 days, never omitted. Revised Julian 0–29 days, omitted in 22 years. Coptic (Pentecost Monday → 5 Epip) 15–49 days.

## 5. Sky layer (internal consistency; no external almanac comparison was run)
- Jerusalem (Holy Sepulchre), 20 Mar 2026, IST: civil dawn 05:18:51, sunrise 05:43:09, solar noon 11:46:32, sunset 17:50:25, civil dusk 18:14:46; day length 12.121 h.
- Sext (sunrise + 6 temporal hours) − solar noon, Jerusalem 21 Jun 2026: -0.0 s.
- London, 21 Dec 2026: day hour 39.14 min, night hour 80.9 min.
- Bearing to the Holy Sepulchre: {'Rome': 111.78, 'Moscow': 184.99, 'Addis Ababa': 352.34, 'New York': 54.06} (deg from true north, spherical great circle).
- Sunrise azimuth at the equator on the 2026 March equinox: 90.18° (expected ≈ 90°). Tromsø, 21 Jun 2026: polar_day.
- Canonical hours in liturgical order (non-decreasing), 7 systems × 3 dates × Jerusalem, St Petersburg and Sydney: 63 / 63. In St Petersburg on 21 Jun the nominal Roman Matins (02:00) would fall after civil dawn. It is moved onto Lauds and flagged in its note.
- Moon at the 2025 Paschal full moon (13 Apr 00:22 UTC): {'name': 'Full Moon', 'elongation': 180.0, 'illumination': 0.9996}.

## Known limits
- Astronomical Easter is available only for 1850–2149 with de440s.bsp. With de440.bsp (1550–2650) in `ephem/` it extends automatically, but that range was not validated here.
- The WCC check uses a secondary transcription (see §2).
- Sun times were not compared with an external almanac (USNO, timeanddate) in this run.
