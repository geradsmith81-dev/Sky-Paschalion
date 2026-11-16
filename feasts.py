"""feasts.py - fixed and movable feasts and fasts for Sky Paschalion.

Contract objects
----------------
FIXED   : list of dict(key, rites|traditions|communions, cal, month, day, rank, kind, sources, ...)
          Dates are given in the tradition's own fixed calendar:
            cal = 'own'       -> month/day read in the tradition's fixed_calendar
                                 (julian | gregorian | revised_julian); this is how one
                                 Byzantine entry serves both Julian and New-Calendar churches.
            cal = 'julian' | 'gregorian' | 'coptic' | 'ethiopian'  -> that calendar explicitly.
          Optional keys:
            end=(month, day)      fast runs to this date (same cal; wraps into next year if earlier)
            rule='nearest_sunday' celebrate on the Sunday nearest month/day (Armenian)
            native='29 Koiak'     date as written in the tradition's own reckoning (display)
            obligation=True       Latin holy day of obligation (CIC can. 1246)
            exclude=[keys]        traditions excluded although their rite matches
            note='...'
MOVABLE : list of dict(key, rites|traditions|communions, base, offset_days, rank, kind, sources, ...)
            base = 'pascha' or a key computed earlier for the same tradition
                   (e.g. 'advent_1', 'vardavar', 'assumption_armenian').
            days=n            fast length in days, or
            end_fixed=(cal, month, day)  fast ends on a fixed date ('own' allowed)
feasts_for(tradition_key, gregorian_year) -> sorted list[(date, key, rank, kind)]
            Fasts are reported once, on their first day, with kind='fast'.

Additions (not in the contract, safe to ignore)
----------------------------------------------
fasts_for(tradition_key, year)        -> list[(start, end, key)] full fast periods starting in year
weekly_fast_days(tradition_key, year) -> sorted list[date] of Wednesday/Friday fast days
RANKS                                 -> rank key -> (order, English label)

Engine use: Pascha comes from the Engine's paschalion.easter(year, rule) (all three rules);
if that module cannot be imported, a built-in Gauss/Meeus computus is used for 'western'
and 'eastern' ('astronomical' then raises). Fixed-date conversion uses built-in Julian Day
arithmetic (Julian, Gregorian, Coptic, Ethiopian); 'revised_julian' is treated as Gregorian,
which is exact from 1 Mar 1600 to 28 Feb 2800.

Simplifications (documented, see notes per entry):
 * Roman transfers (Annunciation/Joseph in Holy Week, Epiphany/Ascension/Corpus Christi to
   Sunday by bishops' conferences) are not applied.
 * Byzantine fast-free weeks and the Typikon's fish/oil gradations are not modelled;
   weekly_fast_days() only removes the major fast-free periods.
 * Coptic/Ethiopian Nativity is placed on Julian 25 December (= 29 Koiak/Tahsas, or 28 in the
   years when 29 Koiak falls on 8 January), as the churches do.
"""
from datetime import date, timedelta

try:  # Engine track module (same name/signature as CONTRACT.md)
    import paschalion as _pas
except Exception:  # pragma: no cover - fallback only
    _pas = None

import sects

# ------------------------------------------------------------------ sources
WP_GREAT = "https://en.wikipedia.org/wiki/Great_feasts_in_the_Eastern_Orthodox_Church"
WP_HDO = "https://en.wikipedia.org/wiki/Holy_day_of_obligation"
WP_GRC = "https://en.wikipedia.org/wiki/General_Roman_Calendar"
WP_LITYEAR = "https://en.wikipedia.org/wiki/Liturgical_year"
WP_NATFAST = "https://en.wikipedia.org/wiki/Nativity_Fast"
WP_DORMFAST = "https://en.wikipedia.org/wiki/Dormition_Fast"
WP_APFAST = "https://en.wikipedia.org/wiki/Apostles%27_Fast"
WP_NINEVEH = "https://en.wikipedia.org/wiki/Fast_of_Nineveh"
WP_GREATLENT = "https://en.wikipedia.org/wiki/Great_Lent"
WP_CROSS = "https://en.wikipedia.org/wiki/Feast_of_the_Cross"
COPT_STTAKLA = "https://st-takla.org/faith/en/terms/feasts.html"
COPT_MVW = "https://mvwcopts.ca/coptic-orthodox/coptic-feasts-fasts/"
COPT_SMSK = "https://www.smskmonastery.ca/fasts-feasts"
WP_COPTFAST = "https://en.wikipedia.org/wiki/Fasting_and_Abstinence_of_the_Coptic_Orthodox_Church_of_Alexandria"
WP_COPTCAL = "https://en.wikipedia.org/wiki/Coptic_calendar"
WP_ETHFAST = "https://en.wikipedia.org/wiki/Fasting_and_abstinence_in_the_Ethiopian_Orthodox_Tewahedo_Church"
WP_ETHCAL = "https://en.wikipedia.org/wiki/Ethiopian_calendar"
WP_MESKEL = "https://en.wikipedia.org/wiki/Meskel"
WP_TIMKAT = "https://en.wikipedia.org/wiki/Timkat"
WP_GENNA = "https://en.wikipedia.org/wiki/Ethiopian_Christmas"
ARM_PRELACY = "https://www.armenianprelacy.org/feast-days.html"
ARM_SYDNEY = "https://armenianchurchsydney.org.au/liturgical-year-of-the-armenian-apostolic-church/"
ARM_ARAK29 = "https://arak29.org/gotoroot/wp-content/uploads/sites/9/2020/04/009Calendar.pdf"
WP_VARDAVAR = "https://en.wikipedia.org/wiki/Vardavar"
ARM_JERUSALEM = "https://www.custodia.org/en/news/the-custodys-greetings-for-the-armenian-christmas/"
ARM_TASBEHA = "https://tasbeha.org/community/discussion/13080/why-do-copts-celebrate-easter-on-april-15-and-armenians-on-april-8"
WCC_FAQ = "https://www.oikoumene.org/resources/documents/frequently-asked-questions-about-the-date-of-easter"
SYR_FEASTS = "http://syriacorthodoxresources.org/Feast/"
SYR_FASTS = "http://syriacorthodoxresources.org/Feast/fasts.html"
WP_SAWMA = "https://en.wikipedia.org/wiki/Sawma_Rabba"

BYZ = ["byzantine"]
SLAVIC_POKROV = ["russian_orthodox", "ukrainian_greek_catholic", "orthodox_church_of_ukraine", "ruthenian_greek_catholic",
                 "slovak_greek_catholic", "belarusian_greek_catholic", "russian_greek_catholic", "polish_orthodox",
                 "czech_slovak_orthodox", "orthodox_church_in_america", "serbian_orthodox", "bulgarian_orthodox",
                 "romanian_orthodox", "romanian_greek_catholic", "macedonian_greek_catholic"]

RANKS = {
    "feast_of_feasts": (0, "Feast of Feasts"),
    "great_feast": (1, "Great Feast (Twelve)"),
    "solemnity": (1, "Solemnity"),
    "major": (1, "Major Feast of the Lord"),
    "tabernacle": (1, "Tabernacle Feast (Daghavar)"),
    "lordly": (1, "Feast of the Lord"),
    "triduum": (1, "Paschal Triduum"),
    "great": (2, "Great Feast"),
    "feast": (2, "Feast"),
    "minor": (2, "Minor Feast of the Lord"),
    "season": (3, "Liturgical season"),
    "memorial": (3, "Memorial"),
    "commemoration": (3, "Commemoration"),
    "great_fast": (2, "Great Fast"),
    "fast": (3, "Fast"),
    "fast_day": (3, "Fast day"),
}

# ===================================================================== FIXED
FIXED = [
    # ---------------- Roman Rite (Latin Church) ----------------
    dict(key="mary_mother_of_god", rites=["latin"], cal="own", month=1, day=1, rank="solemnity", kind="feast", obligation=True, sources=[WP_HDO, WP_GRC]),
    dict(key="epiphany", rites=["latin"], cal="own", month=1, day=6, rank="solemnity", kind="feast", obligation=True,
         note="Transferred to the Sunday 2-8 Jan where it is not a holy day of obligation (not applied).", sources=[WP_HDO, WP_GRC]),
    dict(key="presentation_of_the_lord", rites=["latin"], cal="own", month=2, day=2, rank="feast", kind="feast", sources=[WP_GRC]),
    dict(key="joseph", rites=["latin"], cal="own", month=3, day=19, rank="solemnity", kind="feast", obligation=True, sources=[WP_HDO, WP_GRC]),
    dict(key="annunciation", rites=["latin"], cal="own", month=3, day=25, rank="solemnity", kind="feast",
         note="Transferred when it falls in Holy Week or the Easter Octave (not applied).", sources=[WP_GRC]),
    dict(key="nativity_john_baptist", rites=["latin"], cal="own", month=6, day=24, rank="solemnity", kind="feast", sources=[WP_GRC]),
    dict(key="peter_paul", rites=["latin"], cal="own", month=6, day=29, rank="solemnity", kind="feast", obligation=True, sources=[WP_HDO, WP_GRC]),
    dict(key="transfiguration", rites=["latin"], cal="own", month=8, day=6, rank="feast", kind="feast", sources=[WP_GRC]),
    dict(key="assumption", rites=["latin"], cal="own", month=8, day=15, rank="solemnity", kind="feast", obligation=True, sources=[WP_HDO, WP_GRC]),
    dict(key="nativity_theotokos", rites=["latin"], cal="own", month=9, day=8, rank="feast", kind="feast", sources=[WP_GRC]),
    dict(key="exaltation_cross", rites=["latin"], cal="own", month=9, day=14, rank="feast", kind="feast", sources=[WP_GRC, WP_CROSS]),
    dict(key="all_saints", rites=["latin"], cal="own", month=11, day=1, rank="solemnity", kind="feast", obligation=True, sources=[WP_HDO, WP_GRC]),
    dict(key="all_souls", rites=["latin"], cal="own", month=11, day=2, rank="commemoration", kind="commemoration", sources=[WP_GRC]),
    dict(key="immaculate_conception", rites=["latin"], cal="own", month=12, day=8, rank="solemnity", kind="feast", obligation=True, sources=[WP_HDO, WP_GRC]),
    dict(key="nativity", rites=["latin"], cal="own", month=12, day=25, rank="solemnity", kind="feast", obligation=True, sources=[WP_HDO, WP_GRC]),

    # ---------------- Byzantine Rite (Eastern Orthodox + Byzantine Catholics) ----------------
    dict(key="church_new_year", rites=BYZ, cal="own", month=9, day=1, rank="commemoration", kind="commemoration",
         note="Indiction - beginning of the church year.", sources=[WP_GREAT]),
    dict(key="nativity_theotokos", rites=BYZ, cal="own", month=9, day=8, rank="great_feast", kind="feast", sources=[WP_GREAT]),
    dict(key="exaltation_cross", rites=BYZ, cal="own", month=9, day=14, rank="great_feast", kind="feast",
         note="Also a strict fast day.", sources=[WP_GREAT, WP_CROSS]),
    dict(key="protection_theotokos", traditions=SLAVIC_POKROV, cal="own", month=10, day=1, rank="great", kind="feast",
         note="Pokrov - kept chiefly in Slavic and Romanian use.", sources=[WP_LITYEAR]),
    dict(key="entry_theotokos", rites=BYZ, cal="own", month=11, day=21, rank="great_feast", kind="feast", sources=[WP_GREAT]),
    dict(key="nativity_fast", rites=BYZ, cal="own", month=11, day=15, end=(12, 24), rank="great_fast", kind="fast",
         note="Philip's Fast, 40 days. Some Melkite use shortens it to 10-24 Dec (not applied).", sources=[WP_NATFAST]),
    dict(key="nativity", rites=BYZ, cal="own", month=12, day=25, rank="great_feast", kind="feast", sources=[WP_GREAT]),
    dict(key="circumcision", rites=BYZ, cal="own", month=1, day=1, rank="great", kind="feast",
         note="With St Basil the Great.", sources=[WP_GREAT]),
    dict(key="theophany_eve", rites=BYZ, cal="own", month=1, day=5, rank="fast_day", kind="fast", sources=[WP_GREAT]),
    dict(key="theophany", rites=BYZ, cal="own", month=1, day=6, rank="great_feast", kind="feast", sources=[WP_GREAT]),
    dict(key="meeting_of_the_lord", rites=BYZ, cal="own", month=2, day=2, rank="great_feast", kind="feast", sources=[WP_GREAT]),
    dict(key="annunciation", rites=BYZ, cal="own", month=3, day=25, rank="great_feast", kind="feast", sources=[WP_GREAT]),
    dict(key="nativity_john_baptist", rites=BYZ, cal="own", month=6, day=24, rank="great", kind="feast", sources=[WP_APFAST]),
    dict(key="peter_paul", rites=BYZ, cal="own", month=6, day=29, rank="great", kind="feast", sources=[WP_APFAST]),
    dict(key="dormition_fast", rites=BYZ, cal="own", month=8, day=1, end=(8, 14), rank="great_fast", kind="fast", sources=[WP_DORMFAST]),
    dict(key="transfiguration", rites=BYZ, cal="own", month=8, day=6, rank="great_feast", kind="feast", sources=[WP_GREAT]),
    dict(key="dormition", rites=BYZ, cal="own", month=8, day=15, rank="great_feast", kind="feast", sources=[WP_GREAT, WP_DORMFAST]),
    dict(key="beheading_john_baptist", rites=BYZ, cal="own", month=8, day=29, rank="great", kind="feast",
         note="Also a strict fast day.", sources=[WP_LITYEAR]),

    # ---------------- Alexandrian (Coptic) Rite: dates in the Coptic calendar ----------------
    dict(key="nayrouz", rites=["alexandrian"], cal="coptic", month=1, day=1, native="1 Thout", rank="feast", kind="feast",
         note="Coptic New Year / Feast of the Martyrs.", sources=[WP_COPTCAL, COPT_SMSK]),
    dict(key="feast_of_the_cross", rites=["alexandrian"], cal="coptic", month=1, day=17, native="17 Thout", rank="feast", kind="feast",
         note="Three-day feast 17-19 Thout.", sources=[COPT_SMSK, WP_CROSS]),
    dict(key="nativity_fast", rites=["alexandrian"], cal="coptic", month=3, day=16, end=(4, 28), native="16 Hathor - 28 Koiak",
         rank="great_fast", kind="fast", note="43 days: 40 days plus 3 added in the 10th century (Mokattam).", sources=[WP_COPTFAST, COPT_MVW]),
    dict(key="nativity", rites=["alexandrian"], cal="julian", month=12, day=25, native="29 Koiak", rank="major", kind="feast",
         note="29 Koiak = 7 January; kept on 28 Koiak in years when 29 Koiak falls on 8 January.", sources=[COPT_STTAKLA, WP_COPTFAST]),
    dict(key="circumcision", rites=["alexandrian"], cal="coptic", month=5, day=6, native="6 Tobi", rank="minor", kind="feast", sources=[COPT_STTAKLA, COPT_MVW]),
    dict(key="theophany", rites=["alexandrian"], cal="coptic", month=5, day=11, native="11 Tobi", rank="major", kind="feast", sources=[COPT_STTAKLA, COPT_MVW]),
    dict(key="wedding_at_cana", rites=["alexandrian"], cal="coptic", month=5, day=13, native="13 Tobi", rank="minor", kind="feast", sources=[COPT_STTAKLA, COPT_MVW]),
    dict(key="presentation_of_the_lord", rites=["alexandrian"], cal="coptic", month=6, day=8, native="8 Meshir", rank="minor", kind="feast", sources=[COPT_STTAKLA, COPT_MVW]),
    dict(key="feast_of_the_cross_2", rites=["alexandrian"], cal="coptic", month=7, day=10, native="10 Paremhat", rank="feast", kind="feast", sources=[COPT_SMSK]),
    dict(key="annunciation", rites=["alexandrian"], cal="coptic", month=7, day=29, native="29 Paremhat", rank="major", kind="feast", sources=[COPT_STTAKLA, COPT_MVW]),
    dict(key="entry_into_egypt", rites=["alexandrian"], cal="coptic", month=9, day=24, native="24 Pashons", rank="minor", kind="feast", sources=[COPT_STTAKLA, COPT_MVW]),
    dict(key="apostles_feast", rites=["alexandrian"], cal="coptic", month=11, day=5, native="5 Epip", rank="feast", kind="feast",
         note="Martyrdom of Sts Peter and Paul (12 July).", sources=[WP_COPTFAST, COPT_SMSK]),
    dict(key="virgin_fast", rites=["alexandrian"], cal="coptic", month=12, day=1, end=(12, 15), native="1-15 Mesori", rank="great_fast", kind="fast",
         note="St Mary's Fast, 7-21 August; Wikipedia gives the end as 16 Mesori (the feast).", sources=[COPT_MVW, WP_COPTFAST]),
    dict(key="transfiguration", rites=["alexandrian"], cal="coptic", month=12, day=13, native="13 Mesori", rank="minor", kind="feast", sources=[COPT_STTAKLA, COPT_MVW]),
    dict(key="assumption", rites=["alexandrian"], cal="coptic", month=12, day=16, native="16 Mesori", rank="feast", kind="feast", sources=[COPT_STTAKLA]),

    # ---------------- Ge'ez Rite (Ethiopian / Eritrean): dates in the Ethiopian calendar ----------------
    dict(key="enkutatash", rites=["geez"], cal="ethiopian", month=1, day=1, native="1 Meskerem", rank="feast", kind="feast",
         note="New Year (Feast of St John).", sources=[WP_ETHCAL]),
    dict(key="meskel", rites=["geez"], cal="ethiopian", month=1, day=17, native="17 Meskerem", rank="great", kind="feast",
         note="27 September (28 in leap years); Demera bonfire on the eve.", sources=[WP_MESKEL]),
    dict(key="tsome_nebiyat", rites=["geez"], cal="ethiopian", month=3, day=15, end=(4, 28), native="15 Hidar - 28 Tahsas",
         rank="great_fast", kind="fast", note="Fast of the Prophets (Advent), about 40 days.", sources=[WP_ETHFAST, WP_NATFAST]),
    dict(key="genna", rites=["geez"], cal="julian", month=12, day=25, native="29 Tahsas", rank="major", kind="feast",
         note="7 January (29 Tahsas; 28 Tahsas in the years when 29 Tahsas falls on 8 January).", sources=[WP_GENNA]),
    dict(key="ketera", rites=["geez"], cal="ethiopian", month=5, day=10, native="10 Tir", rank="fast_day", kind="fast",
         note="Eve of Timkat (Gahad).", sources=[WP_TIMKAT, WP_ETHFAST]),
    dict(key="timkat", rites=["geez"], cal="ethiopian", month=5, day=11, native="11 Tir", rank="major", kind="feast",
         note="19 January (20 in leap years).", sources=[WP_TIMKAT]),
    dict(key="annunciation", rites=["geez"], cal="ethiopian", month=7, day=29, native="29 Megabit", rank="major", kind="feast",
         note="Same day as Coptic 29 Paremhat.", sources=[WP_ETHCAL, COPT_STTAKLA]),
    dict(key="apostles_feast", rites=["geez"], cal="ethiopian", month=11, day=5, native="5 Hamle", rank="feast", kind="feast",
         note="Sts Peter and Paul; same day as Coptic 5 Epip.", sources=[WP_ETHFAST]),
    dict(key="tsome_filseta", rites=["geez"], cal="ethiopian", month=12, day=1, end=(12, 15), native="1-15 Nehase", rank="great_fast", kind="fast",
         note="Fast of the Assumption, 15 days (dates by correspondence with Coptic 1-15 Mesori).", sources=[WP_ETHFAST, COPT_MVW]),
    dict(key="debre_tabor", rites=["geez"], cal="ethiopian", month=12, day=13, native="13 Nehase", rank="major", kind="feast",
         note="Transfiguration; same day as Coptic 13 Mesori.", sources=[COPT_STTAKLA]),
    dict(key="filseta", rites=["geez"], cal="ethiopian", month=12, day=16, native="16 Nehase", rank="feast", kind="feast",
         note="Assumption of the Virgin; same day as Coptic 16 Mesori.", sources=[WP_ETHFAST, COPT_STTAKLA]),

    # ---------------- Armenian Rite ----------------
    dict(key="nativity_fast_armenian", rites=["armenian"], cal="own", month=12, day=30, end=(1, 4), rank="fast", kind="fast",
         note="Fast of Nativity/Theophany as listed by the Eastern Prelacy (30 Dec-4 Jan); weekday-dependent in practice.", sources=[ARM_PRELACY]),
    dict(key="nativity_theophany", rites=["armenian"], cal="own", month=1, day=6, rank="tabernacle", kind="feast",
         note="Nativity and Baptism together; Jerusalem Patriarchate (Julian) = 19 January.", sources=[WCC_FAQ, ARM_JERUSALEM, ARM_SYDNEY]),
    dict(key="presentation_of_the_lord", rites=["armenian"], cal="own", month=2, day=14, rank="feast", kind="feast",
         note="Tearnendaraj, 40 days after 6 January (forum source only - verify).", sources=[ARM_TASBEHA]),
    dict(key="annunciation", rites=["armenian"], cal="own", month=4, day=7, rank="feast", kind="feast", sources=[ARM_PRELACY]),
    dict(key="assumption_armenian", rites=["armenian"], cal="own", month=8, day=15, rule="nearest_sunday", rank="tabernacle", kind="feast",
         note="Sunday nearest 15 August.", sources=[ARM_PRELACY, ARM_SYDNEY, WP_DORMFAST]),
    dict(key="nativity_theotokos", rites=["armenian"], cal="own", month=9, day=8, rank="feast", kind="feast", sources=[ARM_PRELACY]),
    dict(key="exaltation_cross_armenian", rites=["armenian"], cal="own", month=9, day=14, rule="nearest_sunday", rank="tabernacle", kind="feast",
         note="Khachverats - Sunday nearest 14 September.", sources=[ARM_PRELACY, ARM_SYDNEY, ARM_ARAK29]),
    dict(key="entry_theotokos", rites=["armenian"], cal="own", month=11, day=21, rank="feast", kind="feast", sources=[ARM_PRELACY]),
    dict(key="conception_theotokos", rites=["armenian"], cal="own", month=12, day=9, rank="feast", kind="feast", sources=[ARM_PRELACY]),

    # ---------------- West Syriac Rite (Syriac Orthodox, Malankara, Syriac Catholic, Syro-Malankara, Maronite) ----------------
    dict(key="circumcision", rites=["west_syriac"], cal="own", month=1, day=1, rank="lordly", kind="feast", sources=[SYR_FEASTS]),
    dict(key="theophany", rites=["west_syriac"], cal="own", month=1, day=6, rank="lordly", kind="feast", note="Denho.", sources=[SYR_FEASTS]),
    dict(key="maron", traditions=["maronite"], cal="own", month=2, day=9, rank="great", kind="feast", note="St Maron, patron of the Maronite Church (date not cross-checked).", sources=["https://en.wikipedia.org/wiki/Maron"]),
    dict(key="presentation_of_the_lord", rites=["west_syriac"], cal="own", month=2, day=2, rank="lordly", kind="feast", sources=[SYR_FEASTS]),
    dict(key="annunciation", rites=["west_syriac"], cal="own", month=3, day=25, rank="feast", kind="feast", sources=[SYR_FEASTS]),
    dict(key="apostles_fast_syriac", rites=["west_syriac"], cal="own", month=6, day=26, end=(6, 28), rank="fast", kind="fast",
         note="Three days from 26 June (Barsoum 1951); Malankara churches keep a longer fast (not modelled).", sources=[SYR_FASTS]),
    dict(key="peter_paul", rites=["west_syriac"], cal="own", month=6, day=29, rank="feast", kind="feast", sources=[SYR_FEASTS]),
    dict(key="transfiguration", rites=["west_syriac"], cal="own", month=8, day=6, rank="lordly", kind="feast", sources=[SYR_FEASTS]),
    dict(key="virgin_fast", rites=["west_syriac"], cal="own", month=8, day=10, end=(8, 14), rank="fast", kind="fast",
         note="Five days from 10 August (Barsoum 1951).", sources=[SYR_FASTS]),
    dict(key="assumption", rites=["west_syriac"], cal="own", month=8, day=15, rank="feast", kind="feast", sources=[SYR_FEASTS]),
    dict(key="nativity_theotokos", rites=["west_syriac"], cal="own", month=9, day=7, rank="feast", kind="feast",
         note="7 September in the Syriac Orthodox calendar.", exclude=["maronite"], sources=[SYR_FEASTS]),
    dict(key="nativity_theotokos", traditions=["maronite"], cal="own", month=9, day=8, rank="feast", kind="feast", sources=[WP_LITYEAR]),
    dict(key="exaltation_cross", rites=["west_syriac"], cal="own", month=9, day=14, rank="lordly", kind="feast", sources=[SYR_FEASTS]),
    dict(key="nativity_fast", rites=["west_syriac"], cal="own", month=12, day=15, end=(12, 24), rank="fast", kind="fast",
         note="Source says 'fifteen days commencing on 15 December' - inconsistent with Christmas on the 25th; modelled as 15-24 Dec.",
         sources=[SYR_FASTS]),
    dict(key="nativity", rites=["west_syriac"], cal="own", month=12, day=25, rank="lordly", kind="feast", sources=[SYR_FEASTS]),

    # ---------------- East Syriac Rite (Assyrian, Ancient, Chaldean, Syro-Malabar) ----------------
    dict(key="nativity_fast", traditions=["ancient_church_of_the_east"], cal="gregorian", month=12, day=1, end=(12, 24), rank="fast", kind="fast",
         note="Wikipedia: dawn-to-dusk fast 1-25 December on the Gregorian calendar.", sources=[WP_NATFAST]),
    dict(key="nativity", rites=["east_syriac"], cal="own", month=12, day=25, rank="lordly", kind="feast", sources=[WP_LITYEAR]),
    dict(key="theophany", rites=["east_syriac"], cal="own", month=1, day=6, rank="lordly", kind="feast", note="Denha.", sources=[WP_LITYEAR]),
    dict(key="assumption", rites=["east_syriac"], cal="own", month=8, day=15, rank="feast", kind="feast",
         note="Commemoration of the Virgin Mary (the Dormition feast proper is not kept in the East Syriac rite).", sources=[WP_DORMFAST]),
    dict(key="exaltation_cross", traditions=["assyrian_church_of_the_east", "ancient_church_of_the_east"], cal="own", month=9, day=13,
         rank="lordly", kind="feast", note="Church of the East: finding of the Cross on 13 September.", sources=[WP_CROSS]),
    dict(key="exaltation_cross", traditions=["chaldean_catholic", "syro_malabar_catholic"], cal="own", month=9, day=14,
         rank="feast", kind="feast", note="14 September assumed for the Catholic East Syriac churches (not verified).", sources=[WP_CROSS]),
]

# =================================================================== MOVABLE
MOVABLE = [
    # ---------------- Roman ----------------
    dict(key="christ_the_king", rites=["latin"], base="advent_1", offset_days=-7, rank="solemnity", kind="feast", sources=[WP_GRC]),
    dict(key="ash_wednesday", rites=["latin"], base="pascha", offset_days=-46, rank="fast_day", kind="fast",
         note="Lent begins; fast and abstinence.", sources=[WP_LITYEAR]),
    dict(key="lent", rites=["latin"], base="pascha", offset_days=-46, days=44, rank="season", kind="fast",
         note="Ash Wednesday to the Mass of the Lord's Supper.", sources=[WP_LITYEAR]),
    dict(key="palm_sunday", rites=["latin"], base="pascha", offset_days=-7, rank="solemnity", kind="feast", sources=[WP_LITYEAR]),
    dict(key="holy_thursday", rites=["latin"], base="pascha", offset_days=-3, rank="triduum", kind="feast", sources=[WP_LITYEAR]),
    dict(key="good_friday", rites=["latin"], base="pascha", offset_days=-2, rank="triduum", kind="fast", sources=[WP_LITYEAR]),
    dict(key="holy_saturday", rites=["latin"], base="pascha", offset_days=-1, rank="triduum", kind="commemoration", sources=[WP_LITYEAR]),
    dict(key="pascha", rites=["latin"], base="pascha", offset_days=0, rank="feast_of_feasts", kind="feast", sources=[WP_LITYEAR]),
    dict(key="divine_mercy", rites=["latin"], base="pascha", offset_days=7, rank="feast", kind="feast", note="Second Sunday of Easter.", sources=[WP_LITYEAR]),
    dict(key="ascension", rites=["latin"], base="pascha", offset_days=39, rank="solemnity", kind="feast", obligation=True,
         note="Transferred to the 7th Sunday of Easter in many countries (not applied).", sources=[WP_HDO]),
    dict(key="pentecost", rites=["latin"], base="pascha", offset_days=49, rank="solemnity", kind="feast", sources=[WP_LITYEAR]),
    dict(key="trinity_sunday", rites=["latin"], base="pascha", offset_days=56, rank="solemnity", kind="feast", sources=[WP_GRC]),
    dict(key="corpus_christi", rites=["latin"], base="pascha", offset_days=60, rank="solemnity", kind="feast", obligation=True,
         note="Transferred to the following Sunday in many countries (not applied).", sources=[WP_HDO]),
    dict(key="sacred_heart", rites=["latin"], base="pascha", offset_days=68, rank="solemnity", kind="feast", sources=[WP_GRC]),
    dict(key="immaculate_heart", rites=["latin"], base="pascha", offset_days=69, rank="memorial", kind="feast", sources=[WP_GRC]),

    # ---------------- Byzantine ----------------
    dict(key="zacchaeus_sunday", rites=BYZ, base="pascha", offset_days=-77, rank="commemoration", kind="commemoration",
         note="Slavic usage: Sunday before the Triodion.", sources=[WP_GREATLENT]),
    dict(key="publican_pharisee", rites=BYZ, base="pascha", offset_days=-70, rank="commemoration", kind="commemoration",
         note="Triodion begins.", sources=[WP_GREATLENT]),
    dict(key="prodigal_son", rites=BYZ, base="pascha", offset_days=-63, rank="commemoration", kind="commemoration", sources=[WP_GREATLENT]),
    dict(key="meatfare_sunday", rites=BYZ, base="pascha", offset_days=-56, rank="commemoration", kind="commemoration", sources=[WP_GREATLENT]),
    dict(key="cheesefare_sunday", rites=BYZ, base="pascha", offset_days=-49, rank="commemoration", kind="commemoration",
         note="Forgiveness Sunday.", sources=[WP_GREATLENT]),
    dict(key="great_lent", rites=BYZ, base="pascha", offset_days=-48, days=48, rank="great_fast", kind="fast",
         note="Clean Monday to Holy Saturday (40 days + Lazarus Saturday, Palm Sunday and Holy Week).", sources=[WP_GREATLENT]),
    dict(key="lazarus_saturday", rites=BYZ, base="pascha", offset_days=-8, rank="commemoration", kind="commemoration", sources=[WP_GREATLENT]),
    dict(key="palm_sunday", rites=BYZ, base="pascha", offset_days=-7, rank="great_feast", kind="feast", sources=[WP_GREAT]),
    dict(key="holy_thursday", rites=BYZ, base="pascha", offset_days=-3, rank="commemoration", kind="commemoration", sources=[WP_GREATLENT]),
    dict(key="good_friday", rites=BYZ, base="pascha", offset_days=-2, rank="fast_day", kind="fast", sources=[WP_GREATLENT]),
    dict(key="holy_saturday", rites=BYZ, base="pascha", offset_days=-1, rank="commemoration", kind="commemoration", sources=[WP_GREATLENT]),
    dict(key="pascha", rites=BYZ, base="pascha", offset_days=0, rank="feast_of_feasts", kind="feast", sources=[WP_GREAT]),
    dict(key="thomas_sunday", rites=BYZ, base="pascha", offset_days=7, rank="commemoration", kind="commemoration", sources=[WP_LITYEAR]),
    dict(key="mid_pentecost", rites=BYZ, base="pascha", offset_days=24, rank="commemoration", kind="commemoration", sources=[WP_LITYEAR]),
    dict(key="ascension", rites=BYZ, base="pascha", offset_days=39, rank="great_feast", kind="feast", sources=[WP_GREAT]),
    dict(key="pentecost", rites=BYZ, base="pascha", offset_days=49, rank="great_feast", kind="feast", sources=[WP_GREAT]),
    dict(key="all_saints_sunday", rites=BYZ, base="pascha", offset_days=56, rank="commemoration", kind="commemoration", sources=[WP_APFAST]),
    dict(key="apostles_fast", rites=BYZ, base="pascha", offset_days=57, end_fixed=("own", 6, 28), rank="great_fast", kind="fast",
         note="Monday after All Saints to 28 June; may vanish in New-Calendar years with a late Pascha.", sources=[WP_APFAST]),

    # ---------------- Alexandrian (Coptic) ----------------
    dict(key="nineveh_fast", rites=["alexandrian"], base="pascha", offset_days=-69, days=3, rank="fast", kind="fast",
         note="Jonah's fast: Monday-Wednesday, two weeks before the 55-day Great Fast.", sources=[WP_NINEVEH, COPT_MVW]),
    dict(key="jonah_feast", rites=["alexandrian"], base="pascha", offset_days=-66, rank="commemoration", kind="feast", sources=[COPT_SMSK]),
    dict(key="great_lent_coptic", rites=["alexandrian"], base="pascha", offset_days=-55, days=55, rank="great_fast", kind="fast",
         note="Preparation week + 40 days + Holy Week (55 days).", sources=[WP_COPTFAST]),
    dict(key="palm_sunday", rites=["alexandrian"], base="pascha", offset_days=-7, rank="major", kind="feast", sources=[COPT_STTAKLA]),
    dict(key="covenant_thursday", rites=["alexandrian"], base="pascha", offset_days=-3, rank="minor", kind="feast", sources=[COPT_STTAKLA]),
    dict(key="good_friday", rites=["alexandrian"], base="pascha", offset_days=-2, rank="fast_day", kind="fast", sources=[WP_COPTFAST]),
    dict(key="pascha", rites=["alexandrian"], base="pascha", offset_days=0, rank="feast_of_feasts", kind="feast", sources=[COPT_STTAKLA]),
    dict(key="thomas_sunday", rites=["alexandrian"], base="pascha", offset_days=7, rank="minor", kind="feast", sources=[COPT_STTAKLA]),
    dict(key="ascension", rites=["alexandrian"], base="pascha", offset_days=39, rank="major", kind="feast", sources=[COPT_STTAKLA]),
    dict(key="pentecost", rites=["alexandrian"], base="pascha", offset_days=49, rank="major", kind="feast", sources=[COPT_STTAKLA]),
    dict(key="apostles_fast", rites=["alexandrian"], base="pascha", offset_days=50, end_fixed=("coptic", 11, 4), rank="great_fast", kind="fast",
         note="Monday after Pentecost to 4 Epip (11 July).", sources=[WP_COPTFAST, WP_APFAST]),

    # ---------------- Ge'ez (Ethiopian / Eritrean) ----------------
    dict(key="tsome_nenewe", rites=["geez"], base="pascha", offset_days=-69, days=3, rank="fast", kind="fast", sources=[WP_NINEVEH, WP_ETHFAST]),
    dict(key="abiy_tsom", rites=["geez"], base="pascha", offset_days=-55, days=55, rank="great_fast", kind="fast",
         note="Hudade / Great Lent, 55 days (as in the Coptic Church).", sources=[WP_ETHFAST, WP_COPTFAST]),
    dict(key="hosanna", rites=["geez"], base="pascha", offset_days=-7, rank="major", kind="feast", sources=[COPT_STTAKLA]),
    dict(key="siklet", rites=["geez"], base="pascha", offset_days=-2, rank="fast_day", kind="fast", note="Good Friday.", sources=[WP_ETHFAST]),
    dict(key="fasika", rites=["geez"], base="pascha", offset_days=0, rank="feast_of_feasts", kind="feast", sources=[WP_ETHCAL]),
    dict(key="ascension", rites=["geez"], base="pascha", offset_days=39, rank="major", kind="feast", note="Erget.", sources=[COPT_STTAKLA]),
    dict(key="pentecost", rites=["geez"], base="pascha", offset_days=49, rank="major", kind="feast", note="Paraclete.", sources=[COPT_STTAKLA]),
    dict(key="tsome_hawaryat", rites=["geez"], base="pascha", offset_days=50, end_fixed=("ethiopian", 11, 4), rank="great_fast", kind="fast",
         note="Monday after Pentecost to 4 Hamle (11 July); Wikipedia's '26 June' equivalence is erroneous.", sources=[WP_ETHFAST]),

    # ---------------- Armenian ----------------
    dict(key="catechumens_fast", rites=["armenian"], base="pascha", offset_days=-69, days=5, rank="fast", kind="fast",
         note="Arajavorats: five days (Mon-Fri), the Armenian form of the Nineveh fast.", sources=[WP_NINEVEH, ARM_PRELACY]),
    dict(key="great_lent_armenian", rites=["armenian"], base="pascha", offset_days=-48, days=48, rank="great_fast", kind="fast",
         note="Medz Bahk from the Monday after Poon Paregentan, with Holy Week.", sources=[WP_GREATLENT]),
    dict(key="palm_sunday", rites=["armenian"], base="pascha", offset_days=-7, rank="feast", kind="feast", sources=[ARM_SYDNEY]),
    dict(key="holy_thursday", rites=["armenian"], base="pascha", offset_days=-3, rank="commemoration", kind="commemoration", sources=[ARM_SYDNEY]),
    dict(key="good_friday", rites=["armenian"], base="pascha", offset_days=-2, rank="fast_day", kind="fast", sources=[ARM_SYDNEY]),
    dict(key="pascha", rites=["armenian"], base="pascha", offset_days=0, rank="feast_of_feasts", kind="feast", sources=[ARM_PRELACY]),
    dict(key="ascension", rites=["armenian"], base="pascha", offset_days=39, rank="feast", kind="feast", sources=[ARM_SYDNEY]),
    dict(key="pentecost", rites=["armenian"], base="pascha", offset_days=49, rank="feast", kind="feast", sources=[ARM_SYDNEY]),
    dict(key="vardavar", rites=["armenian"], base="pascha", offset_days=98, rank="tabernacle", kind="feast",
         note="Transfiguration, 98 days (14 weeks) after Easter.", sources=[WP_VARDAVAR, ARM_PRELACY]),
    dict(key="vardavar_fast", rites=["armenian"], base="vardavar", offset_days=-6, days=5, rank="fast", kind="fast",
         note="Mon-Fri before the tabernacle feast.", sources=[ARM_PRELACY]),
    dict(key="assumption_fast_armenian", rites=["armenian"], base="assumption_armenian", offset_days=-6, days=5, rank="fast", kind="fast",
         sources=[ARM_PRELACY]),
    dict(key="exaltation_fast_armenian", rites=["armenian"], base="exaltation_cross_armenian", offset_days=-6, days=5, rank="fast", kind="fast",
         sources=[ARM_PRELACY, "https://armenianchurch.us/season-of-the-cross-6/"]),

    # ---------------- West Syriac ----------------
    dict(key="nineveh_fast", rites=["west_syriac"], base="pascha", offset_days=-69, days=3, rank="fast", kind="fast",
         note="Three days from the Monday of the third week before Great Lent.", sources=[SYR_FASTS, WP_NINEVEH]),
    dict(key="great_lent", rites=["west_syriac"], base="pascha", offset_days=-48, days=48, rank="great_fast", kind="fast",
         note="Forty-eight days before Easter (Barsoum). Maronites begin on 'Ash Monday'.", sources=[SYR_FASTS]),
    dict(key="palm_sunday", rites=["west_syriac"], base="pascha", offset_days=-7, rank="lordly", kind="feast", sources=[SYR_FEASTS]),
    dict(key="holy_thursday", rites=["west_syriac"], base="pascha", offset_days=-3, rank="lordly", kind="feast", sources=[SYR_FEASTS]),
    dict(key="good_friday", rites=["west_syriac"], base="pascha", offset_days=-2, rank="fast_day", kind="fast", sources=[SYR_FEASTS]),
    dict(key="pascha", rites=["west_syriac"], base="pascha", offset_days=0, rank="feast_of_feasts", kind="feast", sources=[SYR_FEASTS]),
    dict(key="ascension", rites=["west_syriac"], base="pascha", offset_days=39, rank="lordly", kind="feast", sources=[SYR_FEASTS]),
    dict(key="pentecost", rites=["west_syriac"], base="pascha", offset_days=49, rank="lordly", kind="feast", sources=[SYR_FEASTS]),

    # ---------------- East Syriac ----------------
    dict(key="nineveh_fast", rites=["east_syriac"], base="pascha", offset_days=-69, days=3, rank="fast", kind="fast",
         note="Rogation of the Ninevites (Ba'utha d-Ninwaye).", sources=[WP_NINEVEH]),
    dict(key="sawma_rabba", rites=["east_syriac"], base="pascha", offset_days=-48, days=48, rank="great_fast", kind="fast",
         note="Begins after Pethurta Sunday (seven weeks before Easter); 'fifty days' fast' in India.", sources=[WP_SAWMA]),
    dict(key="palm_sunday", rites=["east_syriac"], base="pascha", offset_days=-7, rank="lordly", kind="feast", sources=[WP_LITYEAR]),
    dict(key="holy_thursday", rites=["east_syriac"], base="pascha", offset_days=-3, rank="lordly", kind="feast",
         note="Pesaha Thursday in Kerala.", sources=[WP_SAWMA]),
    dict(key="good_friday", rites=["east_syriac"], base="pascha", offset_days=-2, rank="fast_day", kind="fast", sources=[WP_SAWMA]),
    dict(key="pascha", rites=["east_syriac"], base="pascha", offset_days=0, rank="feast_of_feasts", kind="feast", sources=[WP_SAWMA]),
    dict(key="ascension", rites=["east_syriac"], base="pascha", offset_days=39, rank="lordly", kind="feast", sources=[WP_LITYEAR]),
    dict(key="pentecost", rites=["east_syriac"], base="pascha", offset_days=49, rank="lordly", kind="feast", sources=[WP_LITYEAR]),
]

# Latin feasts computed from Christmas/Epiphany rather than from Pascha
SPECIAL = [
    dict(key="advent_1", rites=["latin"], rank="season", kind="feast", note="First Sunday of Advent: Sunday 27 Nov-3 Dec.", sources=[WP_LITYEAR]),
    dict(key="holy_family", rites=["latin"], rank="feast", kind="feast", note="Sunday within the Christmas octave, else 30 Dec.", sources=[WP_GRC]),
    dict(key="baptism_of_the_lord", rites=["latin"], rank="feast", kind="feast", note="Sunday after 6 January.", sources=[WP_GRC]),
]

# ===================================================== calendar arithmetic
_COPTIC_EPOCH = 1825030      # JDN of 1 Thout 1 AM = 29 Aug 284 (Julian)
_ETHIOPIAN_EPOCH = 1724221   # JDN of 1 Meskerem 1 Amete Mihret = 29 Aug 8 (Julian)


def _jdn_greg(y, m, d):
    a = (14 - m) // 12
    yy = y + 4800 - a
    mm = m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045


def _jdn_jul(y, m, d):
    a = (14 - m) // 12
    yy = y + 4800 - a
    mm = m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - 32083


def _jdn_alex(epoch, y, m, d):
    return epoch + 365 * (y - 1) + y // 4 + 30 * (m - 1) + d - 1


def _date_from_jdn(j):
    return date.fromordinal(j - 1721425)


def _month_len(cal, y, m):
    if cal in ("coptic", "ethiopian"):
        if m < 13:
            return 30
        return 6 if y % 4 == 3 else 5
    if m == 2:
        if cal == "julian":
            return 29 if y % 4 == 0 else 28
        return 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28
    return 31 if m in (1, 3, 5, 7, 8, 10, 12) else 30


def to_gregorian(cal, y, m, d):
    """Convert (cal, y, m, d) to datetime.date. revised_julian/byzantine month-days are
    treated as Gregorian/Julian respectively (RJ = Gregorian 1600-2800)."""
    if d > _month_len("gregorian" if cal in ("gregorian", "revised_julian") else cal, y, m):
        raise ValueError("invalid day")
    if cal in ("gregorian", "revised_julian"):
        return date(y, m, d)
    if cal in ("julian", "byzantine"):
        return _date_from_jdn(_jdn_jul(y, m, d))
    if cal == "coptic":
        return _date_from_jdn(_jdn_alex(_COPTIC_EPOCH, y, m, d))
    if cal == "ethiopian":
        return _date_from_jdn(_jdn_alex(_ETHIOPIAN_EPOCH, y, m, d))
    raise ValueError("unknown calendar " + cal)


def _years_for(cal, gy):
    if cal == "coptic":
        return (gy - 285, gy - 284, gy - 283)
    if cal == "ethiopian":
        return (gy - 9, gy - 8, gy - 7)
    return (gy - 1, gy, gy + 1)


def _in_year(cal, m, d, gy):
    """All Gregorian dates in year gy that carry month/day (m, d) in calendar cal."""
    out = []
    for y in _years_for(cal, gy):
        try:
            g = to_gregorian(cal, y, m, d)
        except ValueError:
            continue
        if g.year == gy:
            out.append((g, y))
    return out


# ============================================================== Paschalion
def _easter_internal(year, rule):
    if rule == "western":
        a = year % 19; b = year // 100; c = year % 100
        d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4
        l_ = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l_) // 451
        month = (h + l_ - 7 * m + 114) // 31
        day = (h + l_ - 7 * m + 114) % 31 + 1
        return date(year, month, day)
    if rule == "eastern":
        a = year % 4; b = year % 7; c = year % 19
        d = (19 * c + 15) % 30
        e = (2 * a + 4 * b - d + 34) % 7
        month = (d + e + 114) // 31
        day = (d + e + 114) % 31 + 1
        return to_gregorian("julian", year, month, day)
    raise RuntimeError("astronomical Paschalion needs the Engine's paschalion module")


def easter(year, rule):
    """Pascha (Gregorian civil date) - Engine first, built-in fallback."""
    if _pas is not None:
        try:
            r = _pas.easter(year, rule)
            return r.date() if hasattr(r, "date") and not isinstance(r, date) else r
        except Exception:
            if rule == "astronomical":
                raise
    return _easter_internal(year, rule)


# =================================================================== helpers
def _applies(entry, trad):
    if trad["key"] in entry.get("exclude", ()):
        return False
    return (trad["key"] in entry.get("traditions", ()) or trad.get("rite") in entry.get("rites", ())
            or trad["communion"] in entry.get("communions", ()))


def _own(cal, trad):
    return trad["fixed_calendar"] if cal == "own" else cal


def _nearest_sunday(d):
    back = (d.weekday() + 1) % 7      # days since the previous Sunday (0 if Sunday)
    return d - timedelta(days=back) if back <= 3 else d + timedelta(days=7 - back)


def _latin_specials(gy):
    nov27 = date(gy, 11, 27)
    adv = nov27 + timedelta(days=(6 - nov27.weekday()) % 7)
    hf = None
    for dd in range(26, 32):
        if date(gy, 12, dd).weekday() == 6:
            hf = date(gy, 12, dd)
    if hf is None:
        hf = date(gy, 12, 30)
    jan7 = date(gy, 1, 7)
    bapt = jan7 + timedelta(days=(6 - jan7.weekday()) % 7)
    return {"advent_1": adv, "holy_family": hf, "baptism_of_the_lord": bapt}


def _fixed_end(cal, start_y, sm, sd, em, ed):
    ey = start_y + (1 if (em, ed) < (sm, sd) else 0)
    return to_gregorian(cal, ey, em, ed)


def _end_fixed_after(spec, trad, start):
    cal = _own(spec[0], trad)
    for y in _years_for(cal, start.year) + _years_for(cal, start.year + 1):
        try:
            g = to_gregorian(cal, y, spec[1], spec[2])
        except ValueError:
            continue
        if g >= start - timedelta(days=1) and (g - start).days < 200:
            return g
    return None


def _compute(trad, gy):
    """Return (events, periods): events = list[(date, key, rank, kind)],
    periods = list[(start, end, key)] for fasts starting in gy."""
    events, periods, known = [], [], {}
    for e in FIXED:
        if not _applies(e, trad):
            continue
        cal = _own(e["cal"], trad)
        for g, y in _in_year(cal, e["month"], e["day"], gy):
            if e.get("rule") == "nearest_sunday":
                g = _nearest_sunday(g)
            events.append((g, e["key"], e["rank"], e["kind"]))
            known[e["key"]] = g
            if e["kind"] == "fast":
                end = _fixed_end(cal, y, e["month"], e["day"], *e["end"]) if "end" in e else g
                periods.append((g, end, e["key"]))
    if trad.get("rite") == "latin":
        sp = _latin_specials(gy)
        for e in SPECIAL:
            if _applies(e, trad):
                events.append((sp[e["key"]], e["key"], e["rank"], e["kind"]))
                known[e["key"]] = sp[e["key"]]
    p = easter(gy, trad["paschalion"])
    known["pascha"] = p
    for e in MOVABLE:
        if not _applies(e, trad):
            continue
        base = known.get(e["base"])
        if base is None:
            continue
        g = base + timedelta(days=e["offset_days"])
        if "end_fixed" in e:
            end = _end_fixed_after(e["end_fixed"], trad, g)
            if end is None or end < g:      # fast vanishes (e.g. late Pascha, New Calendar)
                continue
        elif "days" in e:
            end = g + timedelta(days=e["days"] - 1)
        else:
            end = g
        if g.year != gy:
            continue
        events.append((g, e["key"], e["rank"], e["kind"]))
        known[e["key"]] = g
        if e["kind"] == "fast":
            periods.append((g, end, e["key"]))
    events.sort(key=lambda t: (t[0], RANKS.get(t[2], (9,))[0], t[1]))
    periods.sort()
    return events, periods


def feasts_for(tradition_key, gregorian_year):
    """Sorted list of (date, key, rank, kind) for one tradition in one Gregorian year.
    Fasts appear once, on their first day (kind='fast'); use fasts_for() for full ranges."""
    trad = sects.BY_KEY[tradition_key]
    return _compute(trad, gregorian_year)[0]


def fasts_for(tradition_key, gregorian_year):
    """List of (start, end, key) for fasting periods that start in gregorian_year."""
    trad = sects.BY_KEY[tradition_key]
    return _compute(trad, gregorian_year)[1]


def weekly_fast_days(tradition_key, gregorian_year):
    """Wednesdays and Fridays kept as fast days (Fridays only for the Latin Church), excluding
    the fifty days from Pascha to Pentecost and the days of the tradition's major/great feasts.
    Byzantine use also excludes 25 Dec-4 Jan, the week after Publican & Pharisee and Trinity week.
    Simplified: no fish/oil gradations, no local customs."""
    trad = sects.BY_KEY[tradition_key]
    events = feasts_for(tradition_key, gregorian_year)
    feast_days = {d for d, k, r, kind in events if kind == "feast" and RANKS.get(r, (9,))[0] <= 2}
    excluded = set()
    for yy in (gregorian_year - 1, gregorian_year, gregorian_year + 1):
        p = easter(yy, trad["paschalion"])
        excluded |= {p + timedelta(days=i) for i in range(0, 50)}
        if trad.get("rite") == "byzantine":
            excluded |= {p + timedelta(days=i) for i in range(-69, -62)}     # week after Publican & Pharisee
            excluded |= {p + timedelta(days=i) for i in range(49, 57)}       # Trinity week
            for g, y in _in_year(_own("own", trad), 12, 25, yy):
                excluded |= {g + timedelta(days=i) for i in range(0, 11)}   # 25 Dec - 4 Jan
    days = []
    d = date(gregorian_year, 1, 1)
    while d.year == gregorian_year:
        wd = d.weekday()
        is_fast = (wd == 4) if trad.get("rite") == "latin" else wd in (2, 4)
        if is_fast and d not in excluded and d not in feast_days:
            days.append(d)
        d += timedelta(days=1)
    return days


def all_keys():
    """Every feast/fast key used in the tables (for names.py coverage checks)."""
    return sorted({e["key"] for e in FIXED + MOVABLE + SPECIAL})
