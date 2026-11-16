# How Sky Paschalion works

Sky Paschalion · Πασχάλιον shows the Christian calendars of the churches of the ancient apostolic sees, the date of
Pascha (Easter) by the three rules in use or proposed, the hours of prayer set by the Sun, the Moon, and a live
compass for praying toward the east. It is the Christian member of the Sky series (Sky Luach, Sky Taqwim,
Sky Gahshomar). Astronomy comes from NASA JPL's DE440s ephemeris through Skyfield.

## 1. The pages

| Page | What it shows |
|---|---|
| Today | The date in the chosen calendar (with its era), the day's feasts, fasts and commemorations, the liturgical season, the Wednesday/Friday fast, sunrise and sunset, the next hour of prayer, the Moon, and the live *Face east* compass. |
| Month | A month of the chosen calendar as a grid (a day-by-day list in phone layout). Each cell carries the Gregorian civil date as the reference and the day of the chosen calendar; no other calendar is shown. |
| Year | The feasts, the fasting periods and the movable cycle for one year of the chosen calendar. |
| Feasts & fasts | Every feast and fast the chosen church keeps in the app's tables, with its rule, rank, this year's date and sources. |
| Paschalion | Pascha for a range of years by the church's rule and by all three rules side by side, then the Paschal full moons and the equinox for one year, with a warning in knife-edge years. |
| Hours | The canonical hours of the chosen system for a date and place, with notes, and the 24 unequal (temporal) hours. |
| Compare | Several churches side by side, each in its own calendar: the date, Pascha, the Nativity and that day's feasts. This is the only page that puts calendars side by side. |
| Traditions | The churches by communion: see, apostle, primate (with date and source), calendar, Paschalion, languages and a **Use** button that applies the church's settings. |
| How it works / About | This text, the validation report, the licence, credits, the list of unverified names and of provisional entries. |

## 2. Churches and settings

The app lists 55 churches of the four communions that trace their bishops to the apostles: the Catholic Church
(the Latin Church and 23 Eastern Catholic churches, 24 entries), the Eastern Orthodox churches (19 entries), the
Oriental Orthodox churches (10) and the Church of the East (Assyrian and Ancient, 2). Each entry (`sects.py`)
records the church's fixed calendar, Paschalion rule, liturgical languages and hours system. Choosing a church
sets these four values; each can then be changed in the settings, and **Restore the church's settings** puts
them back. 13 entries are marked *provisional*: their calendar or primate rests on sources that could not be
fully confirmed, and the note says why.

## 3. Calendars (`calendars.py`)

All conversions go through the Julian Day Number.

* **Gregorian** and **Julian**: the standard rules. The Julian calendar now runs 13 days behind (1900–2099).
* **Revised Julian** (Milanković, Constantinople 1923): century years are leap only when the year divided by 900
  leaves 200 or 600. It agrees with the Gregorian calendar from 1 March 1600 to 28 February 2800.
* **Coptic** (Anno Martyrum) and **Ethiopian** (Amete Mihret): twelve months of 30 days and a short thirteenth
  month of 5 or 6 days. The year begins on 29 August Julian (30 August before a Julian leap year), i.e. 11 or
  12 September Gregorian today. Ethiopian year = Coptic year + 276.
* **Byzantine** (Anno Mundi, from 1 September 5509 BC): Julian months and days, the year beginning on
  1 September, with the indiction. In the app it is a display era over the Julian calendar.

The liturgical day begins at sunset; after sunset the Today page says which liturgical day has begun.

**Changing the calendar.** Within the Julian family (Gregorian, Julian, Revised Julian, Byzantine) a change of
calendar moves the fixed feasts (e.g. Nativity on 25 December Gregorian or Julian). The feast tables of the
Coptic and Ethiopian churches are written in their own calendars, so for those churches (and for the others
when a Coptic or Ethiopian display is chosen) only the display changes, and a note says which calendar the
feasts are kept by.

**Coptic and Ethiopian Nativity.** 29 Koiak (29 Tahsas) falls on 7 January in most years and on 8 January in
the year after a Coptic leap year. The churches keep the Nativity on 7 January, which is then 28 Koiak. The app
always shows the Coptic date computed by the converter, never a fixed "29 Koiak". In those years the Nativity
Fast, given in the tables as "16 Hathor – 28 Koiak", is shortened by one day so that it ends on the eve of the
feast (6 Coptic and Ethiopian churches × 50 years in 1900–2099).

## 4. The Paschalion (`paschalion.py`)

Pascha is the first Sunday after the first full moon on or after the spring equinox. The rules differ in how
the full moon and the equinox are reckoned:

* **Western** (Gregorian computus, 1582): the ecclesiastical Moon of the Gregorian epact tables and a fixed
  equinox on 21 March (Meeus/Butcher algorithm).
* **Eastern** (Julian or Alexandrian computus, kept by the Orthodox, Oriental Orthodox and most Eastern
  churches): the 19-year Metonic cycle and 21 March, both in the Julian calendar; the result is converted to the
  Gregorian date.
* **Astronomical** (proposal of the World Council of Churches / Middle East Council of Churches, Aleppo 1997):
  the true March equinox and full moon from JPL DE440s. The full moon's date is taken on the meridian of
  Jerusalem (local mean time, UTC + 2 h 20 min 55 s), and Pascha is the next Sunday after it. DE440s covers
  1850–2149; outside those years the astronomical rule is shown as *unavailable* and nothing is guessed.

Pascha moves the whole movable cycle: the pre-Lenten Sundays, Lent, Holy Week, Ascension (+39 days),
Pentecost (+49) and the feasts after it, and the start of the Apostles' Fast.

## 5. Feasts, fasts and seasons (`feasts.py`, `liturgy.py`)

The content tables hold 89 fixed entries, 80 movable entries and 3 Latin seasonal markers, each with the
churches or rites that keep it, a rank, a kind (feast, fast, commemoration) and sources. Fixed entries are given
in the calendar where the church keeps them (e.g. 25 December, 29 Koiak, 17 Meskerem).

* **Seasons** (Today page). Latin: Advent, Christmas season (to the Baptism of the Lord), Lent, Paschal Triduum,
  Easter season (to Pentecost), Ordinary Time. Byzantine: the Triodion (from the Publican and the Pharisee to
  Holy Saturday, with Great Lent and Holy Week), the Pentecostarion (Pascha to All Saints' Sunday) and the season
  of the Octoechos. Other rites: Holy Week, the Holy Fifty Days, and any fasting period the church keeps.
* **Wednesday and Friday fasts**: Fridays in the Latin Church, Wednesdays and Fridays elsewhere, except the fifty
  days after Pascha and great feasts (and, in Byzantine use, the fast-free weeks). Grades of fasting (fish, oil,
  wine) are not modelled.

## 6. Hours of prayer (`sky_layer.py`)

Seven systems: Roman (Liturgy of the Hours / Breviary), Byzantine (Horologion), Coptic (Agpeya), Ethiopian
(Sa'atat), Armenian (Zhamagirk'), West Syriac (Shehimo) and East Syriac (Hudra). Each office is tied either to an
event of the Sun (sunrise, solar noon, sunset) or to its traditional clock hour, read as an *unequal* hour:
the day from sunrise to sunset and the night from sunset to sunrise are each divided into twelve. So Terce is
three day-hours after sunrise and Sext is solar noon. Byzantine and Syriac days begin with Vespers of the eve.
In polar day or night the offices fall back to their nominal clock times and are marked.

## 7. The *Face east* compass (`orient_live.py`)

Christians have long prayed facing east. The compass offers three directions: **East** (90° from true north,
the default), **Jerusalem** (the initial great-circle bearing to the Church of the Holy Sepulchre) and **today's
sunrise point**. On a phone the dial turns with the device: the phone's compass heading (from magnetic north)
is corrected by the local magnetic declination from the World Magnetic Model 2025, the dial is turned so that N
points to true north, and the arrow points to the chosen direction. iPhones and iPads ask for permission after a
tap on **Turn on the live compass**; Android phones need no permission. Hold the phone flat. When the top of the
phone points within 5° of the target, the card says so. On a computer, the drawing stays with north at the top.
The compass readings never leave the browser.

## 8. Names and languages (`names.py`)

Names are written *English · liturgical language* (Latin, polytonic Greek, Church Slavonic, Coptic, Ge'ez,
Classical Armenian, Syriac in the church's script, Arabic, and others), with bundled open fonts for each
script. A form that has not been confirmed in a cited source carries a small **?** and is listed on the About
page. The native names of the calendars and rules in the settings (e.g. *Calendarium Gregorianum*,
*Νέον Ἡμερολόγιον*) were added when the app was assembled and are listed there as unverified too.

## 9. Place and time

The app first guesses the place from the browser's time zone, then asks the device for its position (the
browser shows its own prompt). A place can also be searched (GeoNames towns of 15,000+ people) or chosen from
presets that include the apostolic sees (Jerusalem, Rome, Istanbul, Alexandria, Antakya, Moscow, Etchmiadzin,
Cairo, Addis Ababa, Asmara, Damascus, Beirut, Baghdad, Erbil, Kottayam and others). The position is used only in
the current browser session.

## 10. Checks

The engine's validation report (VALIDATION.md, unchanged) records, among others:

* Western and Eastern Pascha equal python-dateutil's in 717 / 717 years (1583–2299); Julian-calendar Pascha too.
* Astronomical Pascha 1850–2149 (300 years): equal to the Western date in 269 years, to the Eastern in 90, to
  both in 77, to neither in 18. It matches all 25 dates of the WCC Aleppo table for 2001–2025 and all 20 of
  Wikipedia's extension to 2045.
* Coptic, Julian and Ethiopian dates agree with convertdate on every one of the 109,573 days 1850–2149;
  round trips through all six calendars fail on 0 days.
* Knife-edge years (full moon within 1 h of the Saturday/Sunday midnight in Jerusalem mean time): 1869, 1873,
  1974, 1998, 2120, 2123.

The assembled app was tested headlessly with Streamlit AppTest (`tools/apptest_sweep.py`): 275 runs covering
the Today page for all 55 churches, every page with four churches, every calendar, rule, hours system and
display language, astronomical Pascha outside 1850–2149, a polar place (Tromsø at midsummer and midwinter), and
fixed dates (Pascha 2025, 2026; Coptic Nativity 2027 and 2028) — 0 exceptions, and 39 / 39 checks of the
rendered text and settings passed. The compass JavaScript was checked with QuickJS (`tools/js_check.py`,
33 / 33): the rotation of the dial and the arrow, Android and iPhone headings, screen rotation, magnetic
declination and the *facing* state.

## 11. Limits

* Dates follow each church's published rules as recorded in the sources; local custom, diocesan transfers
  (e.g. Ascension to Sunday) and particular monastic uses can differ.
* Astronomical Pascha needs DE440s (1850–2149).
* Sun times were checked for internal consistency, not against an external almanac.
* Fasting grades, the full Menaion of saints, and Armenian and Syriac Apostles' Fast customs are not modelled.
