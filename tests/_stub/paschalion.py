"""TEST-ONLY stub of the Engine track's paschalion.py (CONTRACT.md names). Not shipped as app code."""
from datetime import timedelta

def easter(year, rule):
    import feasts
    return feasts._easter_internal(year, rule)

def movable(year, rule):
    p = easter(year, rule)
    off = {"zacchaeus_sunday": -77, "publican_pharisee": -70, "septuagesima": -63, "nineveh_fast_start": -69,
           "meatfare_sunday": -56, "ash_wednesday": -46, "clean_monday": -48, "great_lent_start_coptic": -55,
           "lazarus_saturday": -8, "palm_sunday": -7, "holy_thursday": -3, "good_friday": -2, "holy_saturday": -1,
           "pascha": 0, "thomas_sunday": 7, "mid_pentecost": 24, "ascension": 39, "pentecost": 49,
           "trinity_sunday": 56, "all_saints_sunday": 56, "corpus_christi": 60, "sacred_heart": 68,
           "apostles_fast_start": 57}
    return {k: p + timedelta(days=v) for k, v in off.items()}
