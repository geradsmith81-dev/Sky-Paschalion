# Saints' days: sources, coverage and limits

Added 24 November 2026. The saints' days in `saints_data.py` (281 saints, 444 dated commemorations) were
compiled in four research tracks, one per rite family. Each date was checked against at least one source that
gives it for that church; movable rules were checked against published calendars for at least two years where
one could be found. The saint summaries are original wording; where a saint appears in several rites, one
summary written to suit every church was kept and the sources were combined. Coverage is the major saints of
each church, not the full daily calendar. The four track reports follow, unchanged apart from heading levels.

General limits:

* Latin dates are the nominal dates of the General Roman Calendar. Displacement by Sundays, solemnities, Lent,
  Holy Week, the Easter Octave and 17-24 December is not modelled (24 displaced memorials in 2026), and
  national or diocesan calendars are not modelled.
* Byzantine Greek Catholic churches receive the general Menaion dates; national saints were added only where a
  church calendar was found (none for ten Greek Catholic churches). Transfers out of Holy Week (e.g. St George
  to Bright Monday) are not modelled.
* Coptic Catholic, Ethiopian Catholic and Eritrean Catholic coverage rests on the shared Synaxarium and is
  provisional.
* Armenian Catholic and the Armenian Patriarchate of Jerusalem use the Armenian Apostolic rules without a
  church-specific check. The Syriac Catholic Church has one entry and the Ancient Church of the East none,
  because no calendar of saints was found for them.

## Saints' days for Sky Paschalion: Latin Church (General Roman Calendar)

Data file: saints_latin.json. Scope: rite `latin` (tradition `latin_catholic`, Gregorian calendar).

### Counts
- 109 saints, 109 day entries. All entries are fixed dates (`"cal": "own"`, which is Gregorian for this church) with `"rites": ["latin"]`.
- Rank `major`: 19 entries. These are the feasts of saints in the General Roman Calendar: the apostles and evangelists, the Conversion of St Paul, the Chair of St Peter, St Mary Magdalene, St Lawrence, the Archangels, St Stephen and the Holy Innocents.
- Rank `saint`: 64 obligatory memorials and 26 selected optional memorials. Each entry's `note` states its rank in the General Roman Calendar.
- Checker (`saints_check.py`, tradition `latin_catholic`): **0 schema problems** for 2025, 2026 and 2027, with 109 dated commemorations in each year.

### Churches covered
- Latin Church (`latin_catholic`) only.

### What is included
- Every feast and every obligatory memorial of a saint in the current General Roman Calendar. This includes the 2021 memorial of Sts Martha, Mary and Lazarus (29 Jul) and Mary Magdalene's rank as a feast since 2016.
- Two days are each split into two chips that share one celebration:
  - 2 Jan: `s_basil_great` and `s_gregory_nazianzen`.
  - 3 May: `s_philip_apostle` and `s_james_brother_of_the_lord`.
  The notes say so.
- 29 Sep is `s_michael_archangel`, with a note that Gabriel and Raphael are included.
- 29 Aug is `s_beheading_of_john_the_baptist`. 22 Feb is `s_chair_of_peter`. 25 Jan is `s_conversion_of_paul`.
- Selected optional memorials (well-known saints, recent additions, Doctors of the Church and Eastern saints): St Blaise (3 Feb), St Josephine Bakhita (8 Feb), St Gregory of Narek (27 Feb), St Patrick (17 Mar), St George (23 Apr), St John of Ávila (10 May), St Bede the Venerable (25 May), St Ephrem the Syrian (9 Jun), Sts John Fisher and Thomas More (22 Jun), St Cyril of Alexandria (27 Jun), St Bridget of Sweden (23 Jul), St Sharbel Makhluf (24 Jul), St Teresa Benedicta of the Cross (Edith Stein) (9 Aug), St Teresa of Calcutta (5 Sep), St Hildegard of Bingen (17 Sep), Sts Cosmas and Damian (26 Sep), St Faustina Kowalska (5 Oct), St John Henry Newman (9 Oct), St John Paul II (22 Oct), St Martin de Porres (3 Nov), St Albert the Great (15 Nov), St Catherine of Alexandria (25 Nov), St John Damascene (4 Dec), St Nicholas (6 Dec), St Juan Diego Cuauhtlatoatzin (9 Dec), St Thomas Becket (29 Dec).

### Excluded by design
- Marian and Christological celebrations, and the dedications of the Lateran, St Mary Major and the basilicas of Sts Peter and Paul.
- Everything already in the app's `latin` feast list: St Joseph, Nativity of St John the Baptist, Sts Peter and Paul, All Saints, All Souls, and the others.
- St Valentine, who is not in the General Roman Calendar.
- These 81 optional memorials of saints, to keep the calendar to what a wall calendar would show: 7 Jan: Saint Raymond of Penyafort; 13 Jan: Saint Hilary; 20 Jan: Saint Fabian; 20 Jan: Saint Sebastian; 27 Jan: Saint Angela Merici; 3 Feb: Saint Ansgar; 8 Feb: Saint Jerome Emiliani; 17 Feb: The Seven Holy Founders of the Servite Order; 21 Feb: Saint Peter Damian; 4 Mar: Saint Casimir; 8 Mar: Saint John of God; 9 Mar: Saint Frances of Rome; 18 Mar: Saint Cyril of Jerusalem; 23 Mar: Saint Turibius of Mongrovejo; 2 Apr: Saint Francis of Paola; 4 Apr: Saint Isidore; 5 Apr: Saint Vincent Ferrer; 13 Apr: Saint Martin I; 21 Apr: Saint Anselm; 23 Apr: Saint Adalbert; 24 Apr: Saint Fidelis of Sigmaringen; 28 Apr: Saint Peter Chanel; 28 Apr: Saint Louis Grignon de Montfort; 30 Apr: Saint Pius V; 1 May: Saint Joseph the Worker; 12 May: Saints Nereus and Achilleus; 12 May: Saint Pancras; 18 May: Saint John I; 20 May: Saint Bernardine of Siena; 21 May: Saint Christopher Magallanes; 22 May: Saint Rita of Cascia; 25 May: Saint Gregory VII; 25 May: Saint Mary Magdalene de' Pazzi; 27 May: Saint Augustine of Canterbury; 29 May: Saint Paul VI; 2 Jun: Saints Marcellinus and Peter; 6 Jun: Saint Norbert; 19 Jun: Saint Romuald; 22 Jun: Saint Paulinus of Nola; 30 Jun: The First Martyrs of Holy Roman Church; 4 Jul: Saint Elizabeth of Portugal; 5 Jul: Saint Anthony Zaccaria; 6 Jul: Saint Maria Goretti; 9 Jul: Saint Augustine Zhao Rong; 14 Jul: Saint Camillus de Lellis; 20 Jul: Saint Apollinaris; 21 Jul: Saint Lawrence of Brindisi; 30 Jul: Saint Peter Chrysologus; 2 Aug: Saint Eusebius of Vercelli; 2 Aug: Saint Peter Julian Eymard; 7 Aug: Saint Sixtus II; 7 Aug: Saint Cajetan; 12 Aug: Saint Jane Frances de Chantal; 13 Aug: Saints Pontian; 16 Aug: Saint Stephen of Hungary; 19 Aug: Saint John Eudes; 23 Aug: Saint Rose of Lima; 25 Aug: Saint Louis; 25 Aug: Saint Joseph Calasanz; 9 Sep: Saint Peter Claver; 17 Sep: Saint Robert Bellarmine; 19 Sep: Saint Januarius; 28 Sep: Saint Wenceslaus; 28 Sep: Saint Lawrence Ruiz and Companions; 6 Oct: Saint Bruno; 9 Oct: Saint Denis; 9 Oct: Saint John Leonardi; 11 Oct: Saint John XXIII; 14 Oct: Saint Callistus I; 16 Oct: Saint Hedwig; 19 Oct: Saints John de Brébeuf; 19 Oct: Saint Paul of the Cross; 23 Oct: Saint John of Capistrano; 16 Nov: Saint Margaret of Scotland; 16 Nov: Saint Gertrude; 23 Nov: Saint Clement I; 23 Nov: Saint Columban; 11 Dec: Saint Damasus I; 21 Dec: Saint Peter Canisius; 23 Dec: Saint John of Kanty; 31 Dec: Saint Sylvester I.

### Uncertainties and limits
1. **Precedence is not modelled.** The app shows each saint on the nominal date every year. In practice, Roman Rite precedence rules omit a feast or memorial that falls on a Sunday, a solemnity, or a day of Holy Week or the Easter Octave. On Lenten weekdays and from 17 to 24 Dec, memorials become commemorations only. Each affected entry has a note ending "(not modelled)". The Liturgical Calendar API shows these displacements:
   - 2025, displaced (not celebrated): Sts Timothy and Titus (01-26); St Polycarp (02-23); St George (04-23); St Mark (04-25); St Bede the Venerable (05-25); St Justin Martyr (06-01); St Ephrem the Syrian (06-09); Sts John Fisher and Thomas More (06-22); St Cyril of Alexandria (06-27); St Lawrence (08-10); St Bartholomew (08-24); St Matthew (09-21); St Faustina Kowalska (10-05); St Andrew (11-30); St Ambrose (12-07); St John of the Cross (12-14); Holy Innocents (12-28).
   - 2026, displaced: Conversion of St Paul (01-25); St Josephine Bakhita (02-08); Chair of St Peter (02-22); St John Baptist de La Salle (04-07); St Stanislaus (04-11); St James, brother of the Lord (05-03); St Philip the Apostle (05-03); St John of Ávila (05-10); St Matthias (05-14); St Bede the Venerable (05-25); St Aloysius Gonzaga (06-21); St Irenaeus (06-28); Sts Joachim and Anne (07-26); St Teresa Benedicta of the Cross (Edith Stein) (08-09); St John Chrysostom (09-13); Sts Andrew Kim Tae-gon, Paul Chong Ha-sang and Companions (09-20); St Vincent de Paul (09-27); St Francis of Assisi (10-04); St Luke (10-18); St Albert the Great (11-15); St Cecilia (11-22); St Nicholas (12-06); St Lucy (12-13); St John the Apostle (12-27).
   - 2027 (through 27 Nov), displaced: St Anthony the Great (01-17); St Francis de Sales (01-24); St John Bosco (01-31); St Scholastica (02-10); Sts Cyril and Methodius (02-14); Sts Perpetua and Felicity (03-07); St Stanislaus (04-11); St Mark (04-25); St Athanasius (05-02); St Anthony of Padua (06-13); St Cyril of Alexandria (06-27); St Benedict (07-11); St James, son of Zebedee (07-25); St Alphonsus Liguori (08-01); St Dominic (08-08); Beheading of St John the Baptist (08-29); St Teresa of Calcutta (09-05); Sts Cosmas and Damian (09-26); St Ignatius of Antioch (10-17).
2. **National and diocesan calendars are not modelled.** Examples: St Patrick is a solemnity in Ireland, St George in England, and Sts Cyril and Methodius in some Slavic countries. Bishops' conferences also move some days.
3. **Gaps in the sources.**
   - The Liturgical Calendar API still ranks Mary Magdalene as a memorial. The rank of feast follows the 2016 decree.
   - The API does not yet include St John Henry Newman (9 Oct), whose entry relies on the decree published on 3 Feb 2026.
   - The Wikipedia list omits St John of Ávila (10 May). That date relies on the 2021 decree and the API.
4. **3 May identification.** The Latin Church identifies James son of Alphaeus with James the brother of the Lord, so the shared key `s_james_brother_of_the_lord` is used there. Byzantine churches keep the two separately, on 9 and 23 October. The shared text states this difference.
5. **Shared keys.** Texts for the shared canonical keys are written to be valid in all churches. The other track agents may write different texts for the same keys, so the integrator should choose one per key.
6. **Text checking.** The summaries are original wording drawn from general knowledge and the cited Wikipedia articles. Dates and statistics in them were checked by hand but not against a second source for every sentence.

### Verification
- All 109 dates were checked against the Wikipedia "General Roman Calendar" list (wikitext fetched 24 Nov 2026). For 108 of them, the Liturgical Calendar API (General Roman Calendar for 2025, 2026 and 2027, with Vatican decrees applied) independently confirms the date: wherever the API lists the celebration, the date the checker prints agrees with it in all three years, with 0 mismatches.
- Additions since 2016 were checked against the Vatican decrees: Mary Magdalene raised to a feast (2016); Gregory of Narek, John of Ávila and Hildegard (2021); Martha, Mary and Lazarus (2021); Teresa of Calcutta (decree of 24 Dec 2024, published 11 Feb 2025); Newman (decree of 9 Nov 2025, published 3 Feb 2026).
- All dates are fixed, so no movable rule needed checking over several years.

### Main sources
- Wikipedia, General Roman Calendar: https://en.wikipedia.org/wiki/General_Roman_Calendar
- Liturgical Calendar API (General Roman Calendar): https://litcal.johnromanodorazio.com/api/v5/calendar/2026 (also /2025 and /2027)
- 2021 decree on the three Doctors: https://www.vatican.va/roman_curia/congregations/ccdds/documents/rc_con_ccdds_doc_20210125_decreto-dottori_en.html
- 2021 decree on Martha, Mary and Lazarus: https://www.ewtn.com/catholicism/library/in-the-household-of-bethany-28967
- 2016 decree on Mary Magdalene: https://press.vatican.va/content/salastampa/en/bollettino/pubblico/2016/06/10/160610b.html
- 2025 decree on Teresa of Calcutta: https://press.vatican.va/content/salastampa/en/bollettino/pubblico/2025/02/11/250211b.html
- 2026 decree on Newman: https://press.vatican.va/content/salastampa/en/bollettino/pubblico/2026/02/03/260203a.html
- A Wikipedia article for each saint, given in the `sources` field of each `saints` entry.

## Saints' days for Sky Paschalion: Byzantine rite

File: saints_byzantine.json. It contains **126 saints** and **154 day entries**. saints_check.py reports **0 schema problems** for 2025, 2026 and 2027.

### Coverage
- **General Byzantine entries** (76, `rites: ['byzantine']`) apply to all 33 Byzantine-rite churches. They cover the major saints of the fixed Menaion: the apostles and evangelists, the great martyrs, the Cappadocian and Alexandrian Fathers, the archangels, Nicholas, Spyridon and others. They also cover eight movable commemorations: Theodore Saturday, the 2nd, 4th and 5th Sundays of Lent, the Myrrhbearers, and the Fathers of the First, Fourth and Seventh Councils. All dates are kept in each church's own calendar (`cal: own`).
- **Church-specific entries** (78, `traditions`), by tradition key:

  - russian_orthodox: 20
  - orthodox_church_in_america: 19
  - bulgarian_orthodox: 11
  - ruthenian_greek_catholic: 9
  - ukrainian_greek_catholic: 9
  - cypriot_orthodox: 8
  - serbian_orthodox: 7
  - romanian_orthodox: 7
  - church_of_greece: 6
  - mount_athos: 6
  - finnish_orthodox: 6
  - constantinople: 5
  - georgian_orthodox: 5
  - alexandria_greek_orthodox: 4
  - jerusalem_greek_orthodox: 4
  - albanian_orthodox: 4
  - antioch_greek_orthodox: 3
  - orthodox_church_of_ukraine: 3
  - old_calendarists: 2
  - romanian_greek_catholic: 2
  - polish_orthodox: 2
  - slovak_greek_catholic: 2
  - czech_slovak_orthodox: 1

- No national entries: belarusian_greek_catholic, russian_greek_catholic, macedonian_greek_catholic, croatian_serbian_greek_catholic, hungarian_greek_catholic, bulgarian_greek_catholic, albanian_greek_catholic, melkite_greek_catholic, italo_albanian_catholic, greek_byzantine_catholic. These churches receive the general entries only, and no St Catherine or St Mercurius entry (see below).

### Usage differences handled
- **St Catherine and St Mercurius**: 24 Nov in Slavic usage (Russian, OCA, Ruthenian GC, UGCC, Bulgarian, Serbian) and 25 Nov in Greek usage (the Greek patriarchates and churches, Old Calendarists, Romanian Orthodox and Romanian GC, Finland).
- **St George**: Bulgaria keeps 6 May on the civil calendar. Autumn feasts are added for Georgia (Giorgoba, 10/23 Nov), Serbia (Đurđic, 3/16 Nov) and Russia (Yuriev Day, 26 Nov / 9 Dec).
- **St Spyridon**: the Ruthenian calendar keeps him on 11 Dec.
- **Rank overrides**, using exclude plus a separate entry: Mark is major for Alexandria, Barnabas for Cyprus, Athanasius the Athonite for Athos, and James the Brother of the Lord for Jerusalem.

### Rule-based dates verified for two years
| Commemoration | Rule | Verified against |
|---|---|---|
| Theodore Saturday, Palamas, Climacus, Mary of Egypt, Myrrhbearers, First Council | Pascha -43/-35/-21/-14/+14/+42 | OCA daily pages 2025 and 2026 |
| Fathers of the Fourth Council | Sunday after 12 Jul (13-19 Jul) | OCA 13 Jul 2025, 19 Jul 2026 |
| Fathers of the Seventh Council | Sunday after 10 Oct (11-17 Oct) | OCA 12 Oct 2025, 11 Oct 2026 |
| New Martyrs of Russia | Sunday after 21 Jan O.S. (nearest Sunday to 25 Jan O.S.) | Rule from drevo-info; 5 Feb 2023 (Ekaterinburg diocese); computed 9 Feb 2025 and 8 Feb 2026 |
| All Saints of Russia; Saints of North America | Pascha +63 | 22 Jun 2025 and 14 Jun 2026 (Russian parish and press pages; OCA) |
| Karelian Enlighteners (Finland) | Saturday after 30 Oct | ort.fi 1 Nov 2025 and 31 Oct 2026 |

### Main sources
- OCA Lives of the Saints, daily pages for every day of 2025 and 2026 (oca.org/saints/lives/YYYY/MM/DD)
- Wikipedia, 'Month Day (Eastern Orthodox liturgics)': all 366 pages, fetched through the MediaWiki API
- Metropolitan Cantor Institute (Byzantine Catholic Archeparchy of Pittsburgh), Calendar of Saints: Ruthenian usage
- UGCC official church calendar 2024 (ugcc.ua)
- Bulgarian Patriarchate monthly calendar 2026 (bg-patriarshia.bg)
- Finnish Orthodox Church calendar and memorial-day index (ort.fi)
- Serbian: slovoljubve.com 2026 calendar, molitvenik.rs, kalendarcrkveni.com
- Romanian: crestinortodox.ro, calendar-romanesc.ro, doxologia.ro
- Polish: cerkiew.pl; Slovak GC: grkathe.sk; Georgian: agenda.ge and Wikipedia
- Saint summaries are original wording. Each saint has a Wikipedia source (or an official church page where no article exists).

### Omissions and uncertainties
- Thirteen Syrian (Assyrian) Fathers, Georgia: no source found for a single joint commemoration date; omitted.
- David of Gareja (Garejoba, Georgia): movable date not confirmed; omitted.
- St Catherine and St Mercurius omitted for churches with no confirmed date. Confirmed 24 Nov (Slavic usage): Russian, OCA, Ruthenian GC, Ukrainian GC, Bulgarian, Serbian. Confirmed 25 Nov: Greek-usage patriarchates and churches, Old Calendarists, Romanian Orthodox and Romanian GC, Finland. Not confirmed (no entry): OCU, Georgian, Polish, Czech-Slovak, and the Belarusian, Russian, Slovak, Hungarian, Macedonian, Croatian-Serbian, Bulgarian, Albanian, Melkite, Italo-Albanian and Greek Byzantine Catholic churches.
- No national saints added for the Russian, Belarusian, Croatian-Serbian, Bulgarian, Macedonian, Hungarian, Albanian, Melkite, Italo-Albanian or Greek Byzantine Catholic churches, because no calendar source was found. Romanian GC has only St Catherine (25 Nov); its national saints were not sourced.
- OCU: Theodosius of the Caves and Boris and Gleb not sourced for the OCU, so they are given only to the Russian Orthodox Church and the UGCC.
- Bl. Vasil Hopko: the Ruthenian (Pittsburgh MCI) and Slovak calendars give 11 May; Wikipedia says US Greek Catholics keep 23 July. 11 May (MCI) is used for the Ruthenian church.
- Bl. Theodore Romzha is given to the Ruthenian church only (MCI); he is not sourced for the Slovak or Hungarian GC calendars.
- Ruthenian usage moves St Spyridon to 11 Dec because 12 Dec is Our Lady of Guadalupe (MCI). A separate entry models this.
- Bulgarian Church keeps St George on 6 May on the civil (Gregorian) calendar, although it is Revised Julian; modelled with cal 'gregorian'.
- Not modelled: transfer of St George to Bright Monday when 23 Apr falls before Pascha (Greek usage), and transfers of other feasts falling in Holy Week. Noted on the George entry.
- Canonical shared keys not used for Byzantine, by editorial choice (minor in Byzantine practice): s_patrick, s_benedict, s_augustine, s_jerome, s_leo_the_great, s_ambrose, s_isaac_the_syrian, s_jacob_of_nisibis, s_gregory_illuminator. Byzantine dates for them exist (e.g. Patrick 17 Mar, Jerome and Augustine 15 Jun) if wanted.
- Greek-usage Catholic churches (Melkite, Italo-Albanian, Greek Byzantine, Albanian GC, etc.) receive the general Menaion entries. Those dates come from the OCA, Wikipedia's Orthodox liturgics pages and the Ruthenian MCI calendar, not from each Catholic church's own calendar.
- Fathers of the Fourth and Seventh Councils (weekday rules) are verified for 2025 and 2026 against OCA (Revised Julian). Their Julian-calendar dates come from applying the same rule; they were not checked against a published Julian calendar.
- New Martyrs of Russia: the rule (Sunday nearest 25 Jan O.S.) comes from drevo-info and an Ekaterinburg diocese page for 2023 (5 Feb). The computed 2025 (9 Feb) and 2026 (8 Feb) dates follow the rule but were not checked against a 2025/2026 calendar page.
- Romanian national saints are sourced from Romanian calendar websites (crestinortodox.ro, calendar-romanesc.ro), not from the Patriarchate site basilica.ro, which was not accessed. The OCU dates are sourced from Ukrainian media that report the OCU calendar.
- Greek-church local saints (Nektarios, Dionysios, Porphyrios, Paisios, Lazarus, Epiphanius, Astius) are sourced from the OCA and from Wikipedia's Orthodox liturgics pages, which cite the Greek Great Synaxaristes. The goarch.org calendar was not reachable.
- Polish Orthodox follows the Julian calendar in the app; parishes using the new calendar are not modelled. Civil dates of Gabriel (3 May) and Maxim (6 Sep) agree with the Polish sources.
- Ranks (major vs saint) are editorial judgments based on the church's typikon marks where available (Bulgarian, Romanian and Serbian red-letter days) and are otherwise approximate.
- There are 154 day entries, against the suggested 100-130, because several saints have two commemorations and Catherine and Mercurius are split by usage.

## Saints' days for Sky Paschalion: Alexandrian (Coptic) and Ge'ez (Ethiopian/Eritrean) rites

Data file: [saints_coptic_ethiopian.json]({{artifact:1579d261-a055-4376-aef3-fc3f01a79173}})

### Counts
- 65 saints and 91 day entries: 55 Coptic-calendar entries and 36 Ethiopian-calendar entries.
- saints_check.py reports **0 schema problems** for 2025, 2026 and 2027.
- Days per church in 2026: Coptic Orthodox 55, Coptic Catholic 49, Ethiopian Orthodox 36, Eritrean Orthodox 36, Ethiopian Catholic 15, Eritrean Catholic 15. In 2027 the Coptic counts are 54 and 48 (see the 22 Koiak note below).
- All dates are fixed dates in the church's own calendar (`cal: coptic` / `cal: ethiopian`). There are no movable (Pascha-based) rules.

### Churches covered
coptic_orthodox and coptic_catholic (rite `alexandrian`); ethiopian_orthodox, eritrean_orthodox, ethiopian_catholic and eritrean_catholic (rite `geez`).

Scope rule:
- Apostles, biblical saints, archangels, martyrs and fathers from before 451, and Takla Haymanot (whom Wikipedia lists as venerated by all three Catholic churches of these rites) use `rites`.
- Saints venerated only by the Oriental Orthodox use `traditions`: coptic_orthodox for St Dioscorus of Alexandria, St Severus of Antioch, St Shenoute the Archimandrite, St Samuel the Confessor, St Abraam of Fayoum, St Kyrillos VI; ethiopian_orthodox and eritrean_orthodox for the native Ethiopian and Eritrean saints and the Ethiopian Gabriel and Uriel feasts.

### Verification
- Coptic: each date was read from the copticchurch.net Synaxarium day page (all 366 day pages were scraped and indexed). Where possible it was cross-checked against the same day in Budge's translation of the Ethiopic Synaxarium, whose day numbers mirror the Coptic ones.
- Several copticchurch.net pages repeat another day's entries. In these cases the date was settled by Budge and Wikipedia: James son of Zebedee on 17 Parmouti (not 2 Parmouti) and Severus on 14 Meshir (not 9 Meshir).
- Ethiopian: dates come from Budge, *The Book of the Saints of the Ethiopian Church* (1928, Wikisource), together with current EOTC sources: Mahibere Kidusan (eotcmk.org), the EOTC-MA 'Order of Calendar', and the St Mary EOTC Cathedral (Toronto) list of annual commemorations.
- Spot check: for all 91 entries the app's 2026 Gregorian date was compared with the Gregorian equivalent in Budge's day heading. All agree except St Thomas, where Budge's heading is internally inconsistent (see below).
- Known fixed points also agree, for example 22 Tobi = 30 Jan, 29 Koiak = 7 Jan, and Tahsas 19 = 28 Dec 2025 but 29 Dec 2027 (leap-year shift).
- No commemoration duplicates a feast already in the app: Peter and Paul, the Cross feasts and the Marian feasts were left out.
- Monthly Ethiopian (and Coptic Michael) commemorations are mentioned in the summary text or the entry `note`. Only the annual days are modelled.

### Coptic saints (50)
St Abanoub, St Abraam of Fayoum, St Andrew the Apostle, St Anthony the Great, St Athanasius the Great, St Barbara, St Barnabas the Apostle, St Bartholomew the Apostle, St Basil the Great, St Cyril of Alexandria, St Demiana, St Dioscorus of Alexandria, The Forty-Nine Martyrs of Scetis, St Gabriel the Archangel, St George, The Holy Innocents, St James, Brother of the Lord, St James, son of Alphaeus, St James the Apostle, son of Zebedee, St John the Apostle and Evangelist, St John Chrysostom, St John the Baptist, St John the Short, St Kyrillos VI, St Luke the Evangelist, St Macarius the Great, St Marina of Antioch, St Mark the Evangelist, St Mary Magdalene, St Mary of Egypt, St Matthew the Apostle and Evangelist, St Matthias the Apostle, St Menas, St Mercurius, St Michael the Archangel, St Moses the Black, St Nicholas of Myra, St Pachomius the Great, St Paul the First Hermit, St Peter, Seal of the Martyrs, St Philip the Apostle, St Pishoy, St Raphael the Archangel, St Samuel the Confessor, St Severus of Antioch, St Shenoute the Archimandrite, St Stephen the Protomartyr, St Takla Haymanot, St Thaddaeus the Apostle, St Thomas the Apostle

### Ethiopian/Eritrean saints (29)
Sts Abreha and Atsbeha, St Anthony the Great, St Aregawi (Za-Mika’el), St Arsema (Rhipsime), Sts Kirkos and Iyaluta (Cyricus and Julitta), St Ewostatewos, St Filipos of Debre Bizen, St Frumentius (Abba Salama), St Gabra Manfas Qeddus (Abo), St Gabriel the Archangel, St Garima (Isaac), St George, The Holy Innocents, St John the Apostle and Evangelist, St John the Baptist, St Lalibela (Gabra Masqal), St Libanos (Mata’e), St Mark the Evangelist, St Mercurius, St Michael the Archangel, St Moses the Black, St Raphael the Archangel, St Samuel of Waldebba, St Stephen the Protomartyr, St Takla Haymanot, St Thomas the Apostle, St Uriel the Archangel, St Walatta Petros, St Yared

Of these, the ones applied to the whole Ge'ez rite (including the Catholic churches) are: St Anthony the Great, St George, St John the Apostle and Evangelist, St John the Baptist, St Mark the Evangelist, St Mercurius, St Michael the Archangel, St Moses the Black, St Raphael the Archangel, St Stephen the Protomartyr, St Takla Haymanot, St Thomas the Apostle, The Holy Innocents.

### Omissions and uncertainties
- Coptic Catholic, Ethiopian Catholic and Eritrean Catholic: no saints' calendar specific to these churches was found. The rite-wide entries rest on Wikipedia's statement that the Coptic calendar is used by Coptic Catholics and on the shared Synaxarium tradition, so their Catholic coverage is provisional. Saints venerated only by the Oriental Orthodox (Dioscorus, Severus, Shenoute, Samuel the Confessor, Abraam, Kyrillos VI) and most native Ethiopian saints are limited to the Orthodox churches.
- Coptic Catholic fixed-calendar practice: the app notes a mixed calendar (outside Upper Egypt the Nativity may be kept on 25 Dec Gregorian). If Coptic Catholics keep saints' days on Gregorian dates, the Coptic-calendar dates here would be wrong for them; this is unverified.
- St Simon the Tanner: omitted. He is not in the copticchurch.net Synaxarium, and no source giving his day was found.
- St Gabriel, Coptic: 30 Paremhat ('Gabriel the Announcer') and 26 Paoni (consecration of his church) are omitted; only 22 Koiak and 13 Paoni are modelled. The brief's '13 Paona?' is confirmed as 13 Paoni.
- St Demiana: the brief's second date '12 Paona' is not confirmed. The Synaxarium gives the consecration of her church on 12 Pashons, and that date is used.
- St Kyrillos VI: the brief's '30 Abib?' is not confirmed. The Synaxarium has him on 30 Meshir (9 March, the day of his death in 1971), and that date is used.
- Gabra Manfas Qeddus: the brief's '30 Tikimt' is not confirmed. EOTC sources give 5 Tikimt (great annual feast) and 5 Megabit (departure), and those are used. The app computes 14 March for 5 Megabit, as Budge and EOTC-MA do; Mahibere Kidusan and Wikipedia print '13 March' (a one-day conversion difference in the source, not a different Ethiopian date).
- Uriel: Budge's Synaxarium manuscript places his festival on 21 Hamle; the modern EOTC-MA calendar gives 22 Hamle, which is used (noted in the entry).
- Kirkos and Iyaluta: the annual feast follows EOTC-MA (15 Tir); Budge's manuscript places their martyrdom on 16 Tir and also 19 Hamle. 19 Hamle is represented by the Gabriel entry.
- Abreha and Atsbeha (4 Tikimt): the only date source is Budge's Synaxarium. The Wikipedia navbox lists Ezana and Saizana on 1 October, which does not match, so this date is single-sourced.
- Libanos (3 Tir) and Filipos of Debre Bizen (5 Nehase) are sourced only from Budge's 1928 Synaxarium translation; current Eritrean practice was not checked separately.
- Ethiopian St Mark: 30 Miyazya follows Budge and the monthly 30th of Wikipedia's calendar page. EOTC-MA lists a 'Saint Mark' on 22 Tikimt, which Budge gives to St Luke, so EOTC-MA was not followed.
- St Thomas: Budge's heading for 26 Ginbot prints 'June 2', but his neighbouring headings imply June 3. The app's 3 June agrees with the arithmetic and with the Coptic 26 Pashons.
- Omitted for volume or weak verification: Takla Haymanot's conception (24 Megabit) and the 24 Tir commemoration; Abune Habta Maryam (date found, but his biography could not be verified); the other Nine Saints besides Aregawi and Garima (Pantelewon and Yem'ata were not found in Budge); Simeon Stylites, Ephrem, Cosmas and Damian, the Forty Martyrs and Maximus and Domitius (all confirmed in the Coptic Synaxarium but left out to stay near the requested size).
- Gabriel (Ethiopian, 19 Tahsas and 19 Hamle), Uriel and the native Ethiopian saints are not applied to the Ethiopian or Eritrean Catholic churches, so those churches have no Gabriel day in this file.
- Calendar effect, not an error: before a Gregorian leap year, Coptic 22 Koiak (Gabriel) moves from 31 Dec to 1 Jan, so it has no date in 2027 and two in 2028.

### Main sources
- Coptic Synaxarium, CopticChurch.net: https://copticchurch.net/synaxarium/ (day pages `/synaxarium/<month>_<day>`)
- E. A. Wallis Budge (tr.), The Book of the Saints of the Ethiopian Church (1928), Wikisource: https://en.wikisource.org/wiki/The_Book_of_the_Saints_of_the_Ethiopian_church
- Mahibere Kidusan (EOTC Sunday School Dept.): https://eotcmk.org/e/ (Michael, Gabriel, Takla Haymanot, Gabra Manfas Qeddus, Yared, Arsema)
- EOTC-MA, Order of Calendar: https://www.eotc-ma.com/beliefs-and-origins-order-of-calend
- St Mary EOTC Cathedral, Toronto, services and annual commemorations: https://stmaryeotctoronto.com/services
- Wikipedia: Coptic calendar; Calendar of saints (Orthodox Tewahedo); individual saints' articles (given in each saint's `sources`).

## Saints' days: Armenian, West Syriac and East Syriac rites

Data file: `saints_armenian_syriac.json` (schema of `saints.py`). Checked with `saints_check.py` for 2025, 2026 and 2027: **0 schema problems**.

- Saints (keys): **65**
- Day entries: **90**

### Coverage by church (number of day entries that apply)

| Church | Rite | Entries | Basis of verification |
|---|---|---|---|
| armenian_catholic | armenian | 20 | Armenian calendar applied as instructed; not checked separately |
| armenian_etchmiadzin | armenian | 21 | Armenian Diocese of Georgia (Mother See) multi-year feast pages 2025-2027; St John Armenian Church 2025 and 2026 calendars; Eastern Diocese posts |
| armenian_cilicia | armenian | 21 | as above, plus Western Prelacy (Cilicia) 2026 feasts and Eastern Prelacy 2025 notices |
| armenian_jerusalem | armenian | 21 | same rules in the Julian calendar; not checked against a Jerusalem calendar |
| armenian_constantinople | armenian | 21 | Armenian Apostolic calendar (same sources as Etchmiadzin) |
| maronite | west_syriac | 12 | Maronite Eparchy of Australia (2025), Maronite liturgical norms, Eparchy of Canada saints list, Wikipedia |
| syriac_catholic | west_syriac | 1 | Behnam and Sarah only (Syriac Catholic parish guide; Vatican News 2025) |
| syro_malankara_catholic | west_syriac | 9 | Syro-Malankara Catholic Sacred Lectionary 2025-26 |
| syriac_orthodox | west_syriac | 16 | Syriac Orthodox Resources feast list (Patr. Barsoum) and SOR calendars 2013/2014; Wikipedia |
| malankara_jacobite | west_syriac | 28 | SOR calendars 2013 and 2014 (Malankara usage), SOR feast list, Wikipedia |
| malankara_orthodox | west_syriac | 20 | MOSC Northeast American Diocese feasts list; mosc.in; Wikipedia |
| chaldean_catholic | east_syriac | 13 | Chaldean Patriarchate Calendar 2026 (one year only); rules shared with Syro-Malabar/Assyrian |
| syro_malabar_catholic | east_syriac | 20 | Official Syro-Malabar liturgical calendars 2024-25 (First Set) and 2025-26 (Second Set) |
| assyrian_church_of_the_east | east_syriac | 13 | Assyrian Church of the East, Diocese of Western Europe, calendars 2025 and 2026 |
| ancient_church_of_the_east | east_syriac | 0 | no calendar found - not covered |

### How dates were modelled and verified

- **Armenian**: almost all saints' days are movable. Each rule (offset from Pascha, from the Assumption Sunday or from the Exaltation Sunday, or "first Saturday after a fixed day") was fitted to the dates published for 2025, 2026 and 2027 by the Armenian Diocese of Georgia (armenianchurch.ge, which lists each feast's dates for many years) and cross-checked against independent 2025 and 2026 parish/diocesan lists. All 20 movable Armenian rules (plus the fixed 24 April entry) reproduce the published dates for 2025, 2026 and 2027 (computed with `saints_check.py`).
- **West Syriac**: saints' days are fixed Gregorian dates, except St Ephrem (first Saturday of Great Lent = Pascha -43), the Friday of Confessors (Pascha +5) and St Charbel (third Sunday of July).
- **East Syriac**: the Fridays after Epiphany are modelled as the k-th Friday strictly after 6 January (verified: the Friday after a Friday Epiphany is the next week's Friday, per the 2023 Syro-Malabar calendar). Summer-season (Qaita) Fridays are Pascha +103 (Jacob of Nisibis), +110 (Mari), +131 (Shmoni) and +138 (Shimun bar Sabbae); Mar Addai is Pascha +28; Mar Aba (Assyrian) Pascha -58. All were matched for 2025 and 2026 against the Syro-Malabar and Assyrian calendars, and for 2026 against the Chaldean calendar.

#### Spot check of computed dates (2025 / 2026)

| Church | Commemoration | 2025 | 2026 |
|---|---|---|---|
| armenian_etchmiadzin | St Sarkis the Warrior | 2025-02-15 | 2026-01-31 |
| armenian_etchmiadzin | St Vardan and his Companions (Vardanants) | 2025-02-27 | 2026-02-12 |
| armenian_etchmiadzin | St Gregory the Illuminator | 2025-04-05, 2025-06-21, 2025-07-05 | 2026-03-21, 2026-06-06, 2026-06-20 |
| armenian_etchmiadzin | Sts Sahak and Mesrop | 2025-07-10 | 2026-06-25 |
| armenian_etchmiadzin | The Holy Translators (Targmanchats) | 2025-10-11 | 2026-10-10 |
| armenian_etchmiadzin | Sts Thaddeus and Bartholomew | 2025-11-29 | 2026-11-28 |
| armenian_jerusalem | Sts Thaddeus and Bartholomew | 2025-12-13 | 2026-12-12 |
| syriac_orthodox | St Ephrem the Syrian | 2025-03-08 | 2026-02-28 |
| malankara_jacobite | St Ephrem the Syrian | 2025-03-08 | 2026-02-21 |
| maronite | St Charbel Makhlouf | 2025-07-20 | 2026-07-19 |
| syro_malabar_catholic | St John the Baptist | 2025-01-10 | 2026-01-09 |
| syro_malabar_catholic | The Greek Doctors | 2025-02-07 | 2026-02-06 |
| assyrian_church_of_the_east | St Mar Aba the Great | 2025-02-21 | 2026-02-06 |
| chaldean_catholic | St Jacob of Nisibis | 2025-08-01 | 2026-07-17 |
| syro_malabar_catholic | St Shimun bar Sabbae | 2025-09-05 | 2026-08-21 |

### Omissions and uncertainties

- Armenian St Stephen the Protomartyr and the other late-December commemorations (David and James, Peter and Paul, James and John): their weekday moves irregularly between 23 and 29 December (e.g. Stephen 25 Dec 2025 Thu, 26 Dec 2026 Sat, 25 Dec 2027 Sat); no single base/weekday rule reproduces them, so they are omitted.
- Armenian St Nicholas, St John Chrysostom, St Gregory the Theologian, Constantine and Helen, Sahak Partev alone, Elijah: not added (irregular or single-source dates, or below wall-calendar level).
- Gregory of Narek, Nerses Shnorhali and Mesrop Mashtots have no separate Armenian Apostolic day; they are covered by the October Holy Translators feast (and Mesrop by the June Sahak-and-Mesrop feast). Gregory of Narek's Roman date (27 Feb) is not applied to the Armenian Catholic Church (no source found).
- Armenian Catholic Church: given the Armenian Apostolic calendar of saints (rites=['armenian']) as instructed; not verified against an Armenian Catholic calendar. The Genocide Martyrs (canonised only by the Apostolic Church) are excluded for Armenian Catholics.
- Armenian Patriarchate of Jerusalem (Julian calendar, Julian Easter): rules computed in its own calendar; no Jerusalem Patriarchate calendar was checked.
- Armenian rank choices (major vs saint) are editorial.
- Syriac Catholic Church: only Sts Behnam and Sarah (10 Dec) is sourced; no published Syriac Catholic calendar of saints was found, so other West Syriac saints are not applied to it.
- Syriac Orthodox: St Severus omitted (sources conflict: Barsoum's list gives the Thursday after the Fast of Nineveh, recent calendars 8 Feb, Wikipedia 29 Sep); kept 8 Feb for the Malankara Jacobite and Malankara Orthodox churches only. Jacob Baradaeus, Mark and Andrew are applied only to the Malankara Jacobite and Malankara Orthodox churches, because the supporting calendars are Malankara-usage. Mary Magdalene and Joachim and Anne are applied to those two and the Syro-Malankara Catholic Church. Ignatius of Antioch (20 Dec) is applied to the two Malankara churches and the Maronite Church (Maronite Eparchy of Canada saints list).
- Syriac Orthodox Jacob of Nisibis: SOR list gives 12 May, Wikipedia 15 July; omitted for West Syriac churches.
- Syriac Orthodox Ephrem and Friday of Confessors: rule ('first Saturday of Lent', 'Friday after Easter') from Patr. Barsoum's list and checked in SOR calendars for 2013 and 2014 (Gregorian Easter, Malankara usage); Syriac Orthodox Julian-Easter years not checked against a printed calendar.
- Malankara Orthodox: St Ephrem omitted (its diocesan list gives 24 Feb, contradicting 'first Saturday of Lent'); St Baselios Yeldho omitted for MOSC (date 2/3 Oct or Kanni 19 unclear); St Thomas given 21 Dec (martyrdom) only, as no MOSC source for 3 July was found; Forty Martyrs omitted (13 Mar vs 9 Mar conflict).
- Syro-Malankara Catholic: Ephrem (first Saturday of Lent) checked for 2026 only (2025-26 lectionary) plus the West Syriac rule; Mar Ivanios excluded (not a saint).
- Maronite St Charbel: third Sunday of July per the Maronite Eparchy of Australia and Wikipedia, but the Maronite 'Norms for the Liturgical Year' give 23 July and the Eparchy of Canada list 17 July; the Sunday rule is used and the conflict noted.
- Maronite St Ephrem 28 Jan rests on Wikipedia only.
- Syro-Malabar Syriac Fathers (6th Friday of Denha), Saints of the Syro-Malabar Church (7th Friday) and the Departed (last Friday): kept only in long Epiphany seasons (e.g. 2025, not 2026), so not modelled; Greek Fathers/Stephen/Evangelists Fridays may be rearranged in years with very early Easter (not modelled, noted in the entries).
- Syro-Malabar Peter and Paul on 29 June (an important feast and day of obligation in 2026) not added; only the Denha Friday is given.
- Assyrian Church of the East: Evangelists, Stephen, Greek and Syrian Fathers Fridays omitted (the Assyrian calendar merges them in short seasons: 2025 vs 2026 differ); Mar Mari omitted (Sat 9 Aug 2025 does not follow the Friday rule kept in 2026); Mar Zaia, Qardagh, Sergius and Bacchus, Elijah and others not added.
- Chaldean Catholic: only the 2026 Chaldean Patriarchate calendar was available. Fixed dates rest on it; movable rules (John the Baptist Friday, Confessors, Addai, Jacob of Nisibis, Mari, Shimun bar Sabbae) match it for 2026 and are the same rules verified for 2025 and 2026 in the Syro-Malabar and Assyrian calendars, but were not checked for a second Chaldean year. Peter and Paul, Evangelists, Stephen and Doctors Fridays omitted for Chaldeans.
- Ancient Church of the East: no published calendar found; no saints applied (0 entries).
- Addai and Mari are given separate keys (s_addai_apostle, s_mari_apostle) rather than the canonical s_addai_and_mari, because every source calendar commemorates them on different days.
- Wikipedia gives some different dates (Euphrasia 30 Aug, Mariam Thresia 6 Jun); the official Syro-Malabar calendar dates (29 Aug, 8 Jun) were used.

### Main sources

- Armenian Diocese in Georgia, church calendar (armenianchurch.ge/en/kalendar-prazdnikov), per-feast pages with dates 2020-2030
- St John Armenian Church, 2025 calendar (stjohnarmenianchurch.org/saints-and-feasts/) and 2026 calendar (/liturgicalcalendar2026/) - read via search snippets (site returned HTTP 502 to direct requests)
- Western Prelacy of the Armenian Apostolic Church, 2026 feasts (westernprelacy.org/feasts-and-calendar/) - via search snippets
- Eastern Diocese of the Armenian Church of America (armenianchurch.us) feast articles; Armenian Prelacy (armenianprelacy.org) 2025 notice
- Syriac Orthodox Resources: Feasts list (Patr. Aphrem Barsoum) and calendars 2013 and 2014 (syriacorthodoxresources.org)
- Malankara Orthodox Northeast American Diocese, Feasts & Memorials (neamericandiocese.org/feasts); mosc.in saints pages
- Syro-Malankara Catholic Church, Sacred Lectionary 2025-2026 (mccna.org)
- Maronite Eparchy of Australia, Days of Obligation and Feast Days (2025); Maronite Norms for the Liturgical Year (maronitemusic.org); Maronite Eparchy of Canada saints list (via search snippet)
- Syro-Malabar Major Archiepiscopal Commission for Liturgy, Liturgical Calendars 2024-25 and 2025-26 (syromalabarliturgy.org)
- Assyrian Church of the East, Diocese of Western Europe, Ecclesiastical Calendars 2025 and 2026 (acote.church)
- Chaldean Patriarchate Calendar 2026 (St George Chaldean Parish, Melbourne); Chaldean Diocese of St Thomas the Apostle, USA - liturgical year
- Wikipedia articles for biographies (fetched via the MediaWiki API)

All summaries are original wording. In the JSON, each saint's `sources` support the biography; each day entry's `sources` give the calendar(s) that state that date for that church.
