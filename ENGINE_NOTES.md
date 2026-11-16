# Sky Paschalion engine: notes

Flat modules: `calendars.py`, `paschalion.py`, `sky_layer.py`, `sky_engine.py`; tests in `tests/test_engine.py`; validation in `tools/validate.py` → `tools/validation_results.json` and `VALIDATION.md`. They need Python 3.12, skyfield, numpy and tzdata (Windows). The validation script also needs python-dateutil, convertdate and ethiopian-date.

Ephemeris: `sky_engine.load()` looks in `./ephem/` (next to the modules), then in `$SKY_EPHEM_DIR`. It prefers de440.bsp to de440s.bsp. If neither is present it downloads de440s.bsp from JPL into `./ephem/`. The pattern is the Sky Luach / Sky Taqwim one, with the SKY_EPHEM_DIR step added.

## Calendar rules (calendars.py)
- Every conversion goes through the integer JDN. `jdn_of(date) = date.toordinal() + 1721425`. Years are astronomical (0 = 1 BC).
- **gregorian / julian**: standard JDN formulas (Fliegel–Van Flandern type).
- **revised_julian** (Milanković, Pan-Orthodox Congress 1923): leap if y % 4 == 0, except century years, which are leap only if y % 900 ∈ {200, 600}. The epoch is set so that 1 Jan 2000 RJ = 1 Jan 2000 Gregorian. It is identical to Gregorian from 1 Mar 1600 to 28 Feb 2800. From 1 Mar 2800 it runs one day ahead (Gregorian 1 Mar 2800 = RJ 2 Mar 2800) until RJ 29 Feb 2900.
- **coptic** (Anno Martyrum): 1 Thout AM 1 = 29 Aug 284 Julian = JDN 1825030. Months 1–12 have 30 days; month 13 (Pi Kogi Enavot / Nasie) has 5 days, or 6 when AM % 4 == 3. Nayrouz is 29 Aug Julian, or 30 Aug before a Julian leap year (11/12 Sep Gregorian in 1900–2099).
- **ethiopian** (Amete Mihret): 1 Meskerem 1 = 29 Aug 8 Julian = JDN 1724221. The structure is identical to the Coptic calendar, with year = AM + 276. Month 13 is Pagume. Enkutatash falls on the same day as Nayrouz.
- **byzantine** (Anno Mundi, creation 1 Sep 5509 BC): Julian months and days. AM = AD + 5509 from 1 Sep to 31 Dec and AD + 5508 from 1 Jan to 31 Aug. AM 7534 began 1 Sep 2025 Julian = 14 Sep 2025 Gregorian. **Month numbering: 1 = September … 4 = December, 5 = January … 12 = August**, in the order of the Byzantine year. Maps: `BYZ_TO_JULIAN_MONTH`, `JULIAN_TO_BYZ_MONTH`. `indiction(am)` = AM mod 15 (0 → 15).
- `liturgical_date(cal, local_dt, sunset_local)`: from sunset onward the next day's date is returned. It works for any calendar key; contract use is coptic/ethiopian.
- Coptic Nativity: 29 Koiak = 7 Jan, except in the Coptic year after a Coptic leap year (January of Gregorian leap years, 1900–2099), when 29 Koiak = 8 Jan and 28 Koiak = 7 Jan. The Coptic Church then keeps the Nativity on 28 Koiak (or on both days). This is a content-track decision; the engine only converts. Ethiopian Genna (29 Tahsas) follows the same pattern.

## Paschalion rules (paschalion.py)
- **western**: Meeus/Butcher 'anonymous' Gregorian algorithm. Ecclesiastical PFM = 21 March + i (Oudin/Clavius epact).
- **eastern**: Meeus' Julian algorithm; Easter is computed in the Julian calendar and converted to Gregorian through the JDN. PFM = 21 March Julian + ((19·(y mod 19) + 15) mod 30), converted to Gregorian.
- **astronomical** (WCC/MECC Aleppo 1997):
  - March equinox: Skyfield `almanac.seasons` (apparent geocentric ecliptic longitude of the Sun = 0°, ecliptic of date) on DE440s.
  - Full moon: `almanac.moon_phases` (apparent geocentric elongation of 180° in ecliptic longitude).
  - The first full moon whose instant is ≥ the equinox instant is used. Its date is taken in **local mean time of the Jerusalem meridian, 35.2296° E = UTC + 2 h 20 min 55.1 s**. Easter is the first Sunday strictly after that date.
  - `astronomical_detail(year, meridian='lmt'|'ist'|'utc')` returns the instants, margins and knife-edge hours. 'ist' (UTC+2) and 'utc' exist only for sensitivity studies.
  - Range: DE440s covers 1850–2149. Outside it the engine raises `paschalion.OutsideEphemeris` (a ValueError).
- `paschal_full_moon(year, rule)`: a `date` for western/eastern, a tz-aware UTC `datetime` for astronomical.
- `march_equinox(year)`: tz-aware UTC.

### movable(year, rule) offsets from Pascha (days)
zacchaeus_sunday −77, publican_pharisee −70, nineveh_fast_start −69 (Mon; Coptic/Ethiopian Fast of Nineveh = Syriac Ba'utha, 2 weeks before the 55-day fast, 3 weeks before a 48-day Lent), nineveh_fast_end −67, septuagesima −63, prodigal_son −63, meatfare_sunday −56, sexagesima −56, great_lent_start_coptic −55, cheesefare_sunday −49, quinquagesima −49, clean_monday −48, ash_wednesday −46, laetare_sunday −21, lazarus_saturday −8, palm_sunday −7, holy_thursday −3, good_friday −2, holy_saturday −1, pascha 0, easter_monday +1, thomas_sunday +7, mid_pentecost +24, ascension +39, pentecost +49, whit_monday +50, trinity_sunday +56, all_saints_sunday +56, corpus_christi +60 (Thursday; often moved to the Sunday, +63), sacred_heart +68, apostles_fast_start +57 (Byzantine), apostles_fast_start_coptic +50 (extra key).

### apostles_fast(year, rule, tradition_style)
`tradition_style` is a fixed-calendar key or an alias:
- 'julian' | 'revised_julian' | 'gregorian' (aliases: 'byzantine', 'old_calendar' → julian; 'new_calendar' → revised_julian): start = P+57, end = 29 June of that calendar (Julian 29 June = 12 July Gregorian in 1900–2099).
- 'coptic' | 'ethiopian' (aliases 'alexandrian', 'oriental'): start = P+50, end = 5 Epip / 5 Hamle (12 July Gregorian in 1900–2099).

`end` is the feast day. **If start > end the fast is omitted that year.** With eastern Pascha on the Revised Julian calendar this happens in 22 of the 200 years 1900–2099. `apostles_fast_days()` returns max(0, end − start).

Armenian, West Syriac and East Syriac Apostles' Fast customs are not modelled; the function raises KeyError for those styles.

## Hours (sky_layer.py)
- Sun events use Skyfield risings and settings of the Sun's centre: −0.8333° (sunrise/sunset), −6°/−12°/−18° (twilights). Solar noon is the upper meridian transit. `solar_midnight` is the lower transit in the night after the date.
- Temporal hours: 12 equal parts of sunrise→sunset and 12 of sunset→next sunrise.
- `canonical_hours` anchors each office either to a Sun event or to the tradition's nominal clock time (6 am = sunrise … 6 pm = sunset, 9 pm, midnight). The nominal time is mapped onto unequal hours, so 'third hour' = sunrise + 3 day hours and Sext = solar noon. See `HOURS_DEFS` for each office's anchor and note. `HOUR_KEYS[system]` gives the key order.
- Liturgical day: Byzantine, West Syriac and East Syriac lists start with Vespers of the eve (D−1). The Armenian list starts with the Night Office of the preceding night. The Roman list runs in civil order (Matins of the preceding night first). The Coptic and Ethiopian lists follow the book order and end with Midnight of the following night.
- In polar day/night, offices fall back to their nominal clock time and set `polar_fallback=True`. In very short nights a nominal office that would come after a dawn-anchored one is moved onto it and flagged in its note.
- Common hour keys: matins, lauds, prime, terce, sext, none, vespers, compline, midnight, veil (Coptic), peace and rest (Armenian), vigil (East Syriac).
- Each item: {key, name_en, start (tz-aware local), note, anchor, civil_date, polar_fallback}.
- `bearing_to_jerusalem` gives the spherical initial great-circle bearing to 31.7784 N, 35.2296 E. Also available: `distance_to_jerusalem_km`, `EAST = 90.0`, `sunrise_azimuth` / `sunset_azimuth` (apparent topocentric, from true north), `moon_phase` (8 named phases, illumination, age, next new/full), `next_full_moon` (UTC), `ethiopian_clock(local_dt)` (hours counted from 06:00/18:00) and `march_equinox` (re-exported).

## Sources
- Meeus, J., *Astronomical Algorithms*, 2nd ed. (Willmann-Bell 1998), ch. 7–8 (JD, Easter).
- WCC/MECC consultation, Aleppo, 5–10 March 1997, *Towards a Common Date for Easter* (oikoumene.org; the report returned HTTP 403 to automated requests). Its 2001–2025 date table is checked through Wikipedia's 'Template:Table of dates of Easter' (rev. 1295050452, stored in tools/ref/; see VALIDATION.md §2).
- JPL DE440/DE440s: Park et al., *AJ* 161:105 (2021); Skyfield (Rhodes) almanac routines.
- Revised Julian rule: Pan-Orthodox Congress, Constantinople 1923 (M. Milanković).
- Coptic/Ethiopian epochs and leap rule: Dershowitz & Reingold, *Calendrical Calculations*; Wikipedia 'Coptic calendar'. Nativity 28/29 Koiak practice: Wikipedia 'Christmas' (date table); The Coptist (5 Jan 2025).
- Hours: Wikipedia 'Fixed prayer times', 'Breviary', 'Shehimo', 'Ramsha', 'Syro-Malabaric Rite'; ethiopianorthodox.org ('Worship'); Encyclopedia.com 'Armenian Liturgy'; Armenian Church News (UK) on the nine services; Rule of St Benedict ch. 8; Sacrosanctum Concilium 89; General Instruction of the Liturgy of the Hours 37.
- Cross-check libraries: python-dateutil (easter), convertdate 2.5.1 (coptic, julian), ethiopian-date 1.0 (defective around 1900/2100; see VALIDATION.md).
