# Sky Paschalion · Πασχάλιον — Traditions content: sources

Traditions track (sects.py, feasts.py, names.py). All web sources were accessed on
**15 November 2026**. Every TRADITIONS / FIXED / MOVABLE entry carries its own `sources`
list; this file collects them, records how each kind of fact was checked, and lists the
conflicts and gaps that remain open.

## 1. Method

* **Primates.** Baseline from Wikipedia's *List of current popes and patriarchs* and
  *List of current Christian leaders* (revisions current on 15 Nov 2026), read through the
  MediaWiki API. Each primate that changed since 2024 was then confirmed in news or
  official sources (below). `primate_now.as_of` = 2026-11-15 for every entry.
* **Calendars and Paschalia.** Pro Oriente (Vienna) church fact boxes, read for 41
  churches. Its calendar field was used, but its "current incumbent" field was not: it is
  out of date for at least the Chaldean, Romanian Greek Catholic and Ancient Church of the
  East entries. Calendar facts were cross-checked against Wikipedia (*Revised Julian
  calendar*), OrthodoxWiki and the church-specific sources below.
* **Feasts and fasts.** Each date comes from the church's own pages where these were
  reachable (Coptic dioceses, Armenian prelacies, Syriac Orthodox Resources). Otherwise it
  comes from the Wikipedia article on that feast or fast. Computed results were tested
  against dated examples in those sources (tests/test_content.py).
* **Liturgical-language names.** Month names for the Coptic (Bohairic + Arabic), Ethiopian
  (Ge'ez script) and Syriac/Arabic Julian–Gregorian calendars were copied from the
  Wikipedia month tables. Every other single form was looked up automatically in
  English Wiktionary under the language header (Latin; Ancient Greek; Old Church
  Slavonic/Church Slavonic; Coptic; Ge'ez; Old Armenian; Classical Syriac/Aramaic; Arabic).
  A form counts as verified only on an exact page match; its URL is stored in
  `names.VERIFIED`. **Every other form is in `names.UNCERTAIN`**, and that includes all
  multi-word feast titles: the Latin Missal titles, the Greek and Slavonic feast titles and
  the Armenian phrases. Church Slavonic is given in plain modern Church Slavonic
  orthography without stress marks or titla. It was **not** checked against Ponomar texts.

## 2. Primates changed 2024–2026 (confirmed)

| Church | Holder (since) | Confirmation |
|---|---|---|
| Rome | Leo XIV (8 May 2025) | press.vatican.va bulletin 11 Nov 2026 (apostolic journey) |
| Georgia | Shio III (elected 11 May 2026; Ilia II reposed 17 Mar 2026) | georgianchurch.ca/about-us/our-patriarch/ ; orthodoxtimes.com (17 Mar 2026) |
| Albania | Joani/John Pelushi (elected 16 Mar 2025, enthroned 29 Mar 2025) | orthochristian.com/168139.html ; /168571.html |
| Finland (autonomous) | Elia Wallgrén (elected 28 Nov 2024, enthroned 15 Dec 2024) | orthodoxtimes.com enthronement report; basilica.ro |
| Bulgaria | Daniil (30 Jun 2024) | Wikipedia infobox; Pro Oriente |
| Chaldean Catholic | Paul III Nona (elected 12 Apr 2026; Sako's resignation accepted 10 Mar 2026; communion celebrated 14 Oct 2026) | vaticannews.va (12 Apr 2026); thetablet.co.uk; infovaticana.com (27 Oct 2026) |
| Eritrean Orthodox | Abune Basilios (elected 9 Dec 2024, enthroned 26 Jan 2025) | copticorthodox.church (relations page); oikoumene.org |
| Ethiopian Catholic | Tesfaye Tadesse Gebresilasie (Wikipedia: from 12 Jun 2026; Pro Oriente: "since 2025") | conflict noted in sects.py |
| Romanian Greek Catholic | Claudiu-Lucian Pop (5 Nov 2025, Wikipedia) | Pro Oriente still lists Mureșan — flagged |
| Jacobite (Malankara, under Antioch) | Baselios Joseph (25 Mar 2025) | Wikipedia biography |
| Slovak Greek Catholic | Jonáš Maxim (appointed 26 Oct 2023) | Wikipedia infobox |
| Armenian (Etchmiadzin) | Karekin II — still in office; criminal case pending (hearing 28 Aug 2026) | armenianchurch.org news 27 Aug and 18 Sep 2026 |
| Ethiopian Orthodox | Abune Mathias I — still in office May 2026 | addisstandard.com (13 May 2026) |
| Ancient Church of the East | Gewargis III Younan (consecrated 9 Jun 2023) — no reunion with the ACoE | syriacpress.com (14 Feb 2026) |

Unchanged and checked in the 2026 Wikipedia lists: Bartholomew I, Theodore II, John X, Theophilos III, Kirill,
Porfirije, Daniel (Romania), Georgios III (Cyprus), Ieronymos II, Sawa, Rastislav, Tikhon, Epiphanius,
Tawadros II, Ignatius Aphrem II, Aram I, Nourhan Manougian, Sahak II Mashalian, Baselios Marthoma Mathews III,
Mar Awa III, Sviatoslav Shevchuk, Raphael Thattil, Baselios Cleemis, William Skurla, Péter Fülöp Kocsis,
Menghesteab Tesfamariam, Ibrahim Isaac Sidrak, Youssef Absi, Bechara al-Rahi, Ignatius Joseph III Younan,
Raphaël Bedros XXI Minassian, Milan Stipić.
**Not verified (primate_now says so):** Greek, Bulgarian, Macedonian, Belarusian and Albanian Greek Catholic heads.

## 3. Calendar usage — key sources

* Revised Julian adopters/non-adopters: https://en.wikipedia.org/wiki/Revised_Julian_calendar ; https://orthodoxwiki.org/Church_Calendar ; WCC FAQ https://www.oikoumene.org/resources/documents/frequently-asked-questions-about-the-date-of-easter
* UGCC New Style for fixed feasts from 1 Sep 2023, Paschalion unchanged: https://ugcc.ua/en/data/historical-decision-the-ugcc-in-ukraine-switches-to-a-new-calendar-232/ ; OCU Revised Julian 2023: https://en.wikipedia.org/wiki/Adoption_of_the_Gregorian_calendar
* Finland: whole year Gregorian incl. Pascha: https://www.pro-oriente.at/en/easternchurches/the-orthodox-church/other-orthodox-churches
* Czech Lands & Slovakia: parish choice Julian/Revised Julian, Orthodox Pascha: https://orthochristian.com/138194.html
* Melkite Pascha with the Orthodox in Syria since 2002: https://www.mliles.com/melkite/paschadatepress.shtml ; Egypt/Jordan/Cyprus Catholics on the Orthodox date: https://www.catholicworldreport.com/2025/04/16/ecumenical-expert-no-theological-reasons-to-celebrate-easter-on-different-dates/ ; https://melkite.org/bishop-nicholas/eastern-catholicism-in-the-middle-east
* Coptic Catholic mixed Christmas practice: https://thetablet.org/egyptian-culture-intertwined-in-coptic-christmas/
* Armenian Gregorian since 1923, Jerusalem Julian: https://armenianchurchsydney.org.au/liturgical-year-of-the-armenian-apostolic-church/ ; https://www.custodia.org/en/news/the-custodys-greetings-for-the-armenian-christmas/
* Syriac Orthodox Gregorian fixed feasts since 1955, Julian Pascha in the Middle East, Malankara Gregorian since 1953: http://syriacorthodoxresources.org/Feast/ ; https://www.soc-wus.org/ourchurch/syriac%20calendar.htm
* Pro Oriente fact boxes (calendar field): https://www.pro-oriente.at/en/easternchurches/ (41 pages; per-church URLs in sects.py)
* Byzantine Forum calendar survey (2008, secondary, used only where nothing better was found): https://www.byzcath.org/forums/ubbthreads.php/topics/309736/which-churches-follow-what-calendar

## 4. Feasts and fasts — key sources

* Twelve Great Feasts: https://en.wikipedia.org/wiki/Great_feasts_in_the_Eastern_Orthodox_Church
* Latin holy days of obligation (CIC can. 1246): https://en.wikipedia.org/wiki/Holy_day_of_obligation ; https://en.wikipedia.org/wiki/General_Roman_Calendar
* Coptic seven major / seven minor feasts: https://st-takla.org/faith/en/terms/feasts.html ; https://mvwcopts.ca/coptic-orthodox/coptic-feasts-fasts/ ; https://www.smskmonastery.ca/fasts-feasts ; dated check table https://ukmidcopts.org/coptic/calendar/
* Coptic fasts (43-day Advent, 55-day Lent, Apostles to 5 Epip, Virgin 1–16 Mesori): https://en.wikipedia.org/wiki/Fasting_and_Abstinence_of_the_Coptic_Orthodox_Church_of_Alexandria
* Ethiopian: Meskel 17 Meskerem https://en.wikipedia.org/wiki/Meskel ; Timkat 11 Tir https://en.wikipedia.org/wiki/Timkat ; Genna 29 Tahsas https://en.wikipedia.org/wiki/Ethiopian_Christmas ; fasts https://en.wikipedia.org/wiki/Fasting_and_abstinence_in_the_Ethiopian_Orthodox_Tewahedo_Church
* Armenian: Sunday-nearest rules and fasts https://www.armenianprelacy.org/feast-days.html ; https://arak29.org/gotoroot/wp-content/uploads/sites/9/2020/04/009Calendar.pdf ; Vardavar = Easter + 98 https://en.wikipedia.org/wiki/Vardavar
* Syriac Orthodox fixed feasts and six fasts (Barsoum): http://syriacorthodoxresources.org/Feast/ ; http://syriacorthodoxresources.org/Feast/fasts.html
* East Syriac: https://en.wikipedia.org/wiki/Sawma_Rabba ; Church of the East Cross 13 Sep https://en.wikipedia.org/wiki/Feast_of_the_Cross
* Nineveh fast, Nativity fast, Dormition fast, Apostles' fast: Wikipedia articles of those titles.

## 5. Open conflicts and simplifications (shown as notes in the app)

1. Syriac Catholic Pascha: Pro Oriente says "Julian"; the default here is Western (provisional).
2. Malankara Orthodox: Pro Oriente says "Gregorian", Religion Media Centre says "Julian"; the default is Gregorian/Western (provisional).
3. Ethiopian and Eritrean Catholic: Pro Oriente says "Gregorian"; modelled on the Ethiopian calendar with Alexandrian Pascha (provisional).
4. Ruthenian: the US Metropolia is Gregorian/Western; Mukachevo practice is not verified.
5. Bulgarian, Greek, Macedonian, Belarusian and Albanian Greek Catholic calendars are thinly sourced (provisional flags).
6. Syriac Orthodox Advent fast: the source says "fifteen days commencing on the 15th of December"; modelled as 15–24 Dec.
7. Ethiopian Apostles' fast: Wikipedia equates 4 Hamle with "26 June", which is wrong (4 Hamle = 11 July). The 4 Hamle date is used.
8. Armenian Presentation (14 Feb) rests on a forum source only.
9. Roman transfers (Epiphany, Ascension, Corpus Christi to Sunday; Annunciation and Joseph out of Holy Week) are not applied.
10. Byzantine abstinence gradations are not modelled. `weekly_fast_days()` removes only the main fast-free periods.
11. `revised_julian` is computed as Gregorian. This is exact until 28 Feb 2800.

## Feast and fast explanations (explain.py)

Clicking a feast or fast name anywhere in the app opens a short explanation (added 17 November 2026).
`explain.TEXT` holds one paragraph for each of the 95 feast and fast keys in feasts.py, plus `explain.WEEKLY` for
the Wednesday and Friday fast. The texts were written for this app from standard reference knowledge
(Gospel passages, councils, papal acts, UNESCO listings). They have **not** been checked one by one against the
sources above. Dates and lengths that differ between churches are given in general terms. Under each text the
popover shows the selected church's rank and rule, taken from feasts.py.

## Shared feasts and founding apostles (summary links, 17 November 2026)

Two links under the page menu open summary windows.

* **What all the churches share** (`common.py`). Feast keys differ by rite, so `common.GROUPS` maps each
  observance to every key that expresses it (for example Pascha = `pascha` / `fasika`, Nativity = `nativity` /
  `genna` / `nativity_theophany`). Each church is computed with its own calendar and Paschalion, as on the
  Compare page. Counts reflect feasts.py, which lists major feasts only, so 'not listed' may be a gap in the data
  (see the known gaps above). The first-attestation notes (`common.ATTESTED`) for Pascha, Good Friday, Palm
  Sunday, Ascension, Pentecost, Great Lent, the Exaltation of the Cross and the Dormition come from the
  'attestation' list in `data/early_church_meta.json` (Early Church research, 16 November 2026). That file has a
  single combined entry for the Nativity and Theophany; it was split here into a Theophany note (c. 200) and a
  Nativity note (4th century). The Nativity note's citation of the Chronograph of 354 (25 December at Rome, 336)
  is **not** in that file: it was added for this app from general reference knowledge and is unverified. The
  Wednesday/Friday note (Didache 8.1) was also added for this app.
* **Churches by founding apostle** (`sects.APOSTLE_ORDER`, `sects.APOSTLES`, `sects.by_apostle()`). Each church is
  listed once, under its principal apostle, marked as 'claimed' or 'via mother church', as decided on
  16 November 2026 and copied from the same `early_church_meta.json`. These are traditions of origin, not
  historical findings.
