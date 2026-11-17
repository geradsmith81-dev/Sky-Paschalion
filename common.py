"""What the churches share: feasts and fasts grouped by MEANING across rites, with each church's date.

The feast keys in feasts.py differ by rite (Ethiopian 'fasika' = Pascha, Armenian 'vardavar' = Transfiguration ...).
GROUPS maps each shared observance to every key that expresses it. summary(year) asks liturgy.year_events for
every church with the church's OWN calendar and Paschalion (as on the Compare page) and reports, per group, how
many churches keep it and on which civil (Gregorian) dates in that year.

Counts describe the app's data, which lists the major feasts only (see SOURCES.md for known gaps), not every
local observance.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date

import feasts
import liturgy as L
import sects

# (group key, English label, kind 'feast' | 'fast', keys that express it). Order = display order.
GROUPS = [
    ("pascha", "Pascha (Easter)", "feast", ["pascha", "fasika"]),
    ("palm_sunday", "Palm Sunday", "feast", ["palm_sunday", "hosanna"]),
    ("holy_thursday", "Holy Thursday", "feast", ["holy_thursday", "covenant_thursday"]),
    ("good_friday", "Good Friday", "fast", ["good_friday", "siklet"]),
    ("ascension", "Ascension", "feast", ["ascension"]),
    ("pentecost", "Pentecost", "feast", ["pentecost"]),
    ("nativity", "Nativity of Christ (Christmas)", "feast", ["nativity", "genna", "nativity_theophany"]),
    ("theophany", "Theophany / Epiphany", "feast", ["theophany", "epiphany", "timkat", "nativity_theophany"]),
    ("exaltation_cross", "Exaltation (Finding) of the Cross", "feast",
     ["exaltation_cross", "meskel", "exaltation_cross_armenian", "feast_of_the_cross"]),
    ("dormition", "Dormition / Assumption of the Virgin", "feast",
     ["dormition", "assumption", "filseta", "assumption_armenian"]),
    ("annunciation", "Annunciation", "feast", ["annunciation"]),
    ("transfiguration", "Transfiguration", "feast", ["transfiguration", "debre_tabor", "vardavar"]),
    ("presentation", "Presentation (Meeting) of the Lord", "feast", ["presentation_of_the_lord", "meeting_of_the_lord"]),
    ("nativity_theotokos", "Nativity of the Virgin", "feast", ["nativity_theotokos"]),
    ("peter_paul", "Sts Peter and Paul", "feast", ["peter_paul", "apostles_feast"]),
    ("great_lent", "Great Lent (the fast before Pascha)", "fast",
     ["lent", "great_lent", "great_lent_coptic", "abiy_tsom", "great_lent_armenian", "sawma_rabba"]),
    ("nativity_fast", "Nativity Fast", "fast", ["nativity_fast", "tsome_nebiyat", "nativity_fast_armenian"]),
    ("apostles_fast", "Apostles' Fast", "fast", ["apostles_fast", "tsome_hawaryat", "apostles_fast_syriac"]),
    ("dormition_fast", "Fast of the Virgin (Dormition Fast)", "fast",
     ["dormition_fast", "virgin_fast", "tsome_filseta", "assumption_fast_armenian"]),
    ("nineveh_fast", "Fast of Nineveh", "fast", ["nineveh_fast", "tsome_nenewe", "catechumens_fast"]),
]
GROUP_BY_KEY = {g[0]: g for g in GROUPS}

# Earliest attestation of the oldest shared observances. Source: data/early_church_meta.json ('attestation', 16 Nov
# 2026) for pascha, good_friday, palm_sunday, ascension, pentecost, great_lent, exaltation_cross and dormition.
# That file has ONE combined entry 'nativity_theophany'; it was split here into 'theophany' (its c. 200 part) and
# 'nativity' (its 4th-century part). The Chronograph of 354 citation for 'nativity' is NOT in that file: it was
# added for this app from general reference knowledge and has not been checked against a source (ADDED below).
ATTESTED = {
    "pascha": ("2nd century", "Quartodeciman controversy: Eusebius, Church History 5.23-25 (Polycrates and Victor, "
                              "c. 190); Melito of Sardis, Peri Pascha (c. 160-170)."),
    "good_friday": ("2nd century (pre-Paschal fast); 4th century (Jerusalem liturgy)",
                    "Irenaeus in Eusebius, Church History 5.24.12; Egeria, Itinerarium 37 (c. 381-384)."),
    "palm_sunday": ("late 4th century, Jerusalem", "Egeria, Itinerarium 31 (c. 381-384)."),
    "ascension": ("late 4th century as a separate 40th-day feast",
                  "Egeria, Itinerarium 42; Apostolic Constitutions 5.20 (c. 380). Earlier it was kept within Pentecost."),
    "pentecost": ("c. 200", "Tertullian, On Baptism 19; Origen, Against Celsus 8.22."),
    "great_lent": ("325 (forty days)", "Council of Nicaea, canon 5; Athanasius, Festal Letters (from the 330s). "
                                       "Before then a fast of one to several days (Irenaeus)."),
    "theophany": ("c. 200", "Clement of Alexandria, Stromata 1.21; Epiphanius, Panarion 51."),
    "nativity": ("4th century", "Epiphanius, Panarion 51; Egeria, Itinerarium 25 (Jerusalem keeps the Nativity at "
                                "Epiphany). Added for this app, not in the research file: Chronograph of 354 "
                                "(25 December at Rome, 336) - unverified."),
    "exaltation_cross": ("335", "Dedication of the Holy Sepulchre basilica, 13 Sept 335, the Cross shown 14 Sept: "
                                "Eusebius, Life of Constantine 4.43-47; Egeria, Itinerarium 48-49."),
    "dormition": ("5th century", "Armenian Lectionary of Jerusalem (c. 417-439): Mary Theotokos on 15 August; "
                                 "made universal by Emperor Maurice (582-602)."),
}

# Keys whose note includes material not taken from early_church_meta.json.
ADDED = {"nativity", "theophany"}

_CACHE: dict = {}


def _church_dates(tkey: str, year: int) -> dict:
    """group key -> (first civil date in `year`, key used) for one church, using its own preset."""
    p = sects.preset(tkey)
    c, r = p["fixed_calendar"], p["paschalion"]
    ev, per, _ = L.year_events(tkey, c, r, year)
    found = {}
    for gk, _lab, _kind, keys in GROUPS:
        best = None
        for dd, key, _rank, _k in ev:
            if key in keys and dd.year == year and (best is None or dd < best[0]):
                best = (dd, key)
        for s, _e, key in per:
            if key in keys and s.year == year and (best is None or s < best[0]):
                best = (s, key)
        if best is None:
            # kept, but no occurrence starting in this civil year (e.g. a fast that began the previous December)
            eff = L.effective(tkey, c, r)
            for entries in (feasts.FIXED, feasts.MOVABLE, feasts.SPECIAL):
                for e in entries:
                    if e["key"] in keys and feasts._applies(e, eff):
                        best = (None, e["key"])
                        break
                if best:
                    break
        if best:
            found[gk] = best
    return found


def summary(year: int) -> list[dict]:
    """One dict per group: key, label, kind, n (churches keeping it), total, missing (church keys),
    dates (list of (date, [church keys]) sorted by date), names (distinct English names of the keys used)."""
    if year in _CACHE:
        return _CACHE[year]
    per_church = {t["key"]: _church_dates(t["key"], year) for t in sects.TRADITIONS}
    total = len(sects.TRADITIONS)
    out = []
    for gk, lab, kind, keys in GROUPS:
        by_date = defaultdict(list)
        used = Counter()
        for tk, found in per_church.items():
            if gk in found:
                dd, key = found[gk]
                by_date[dd].append(tk)
                used[key] += 1
        n = sum(len(v) for v in by_date.values())
        dated = sorted(((d, v) for d, v in by_date.items() if d is not None), key=lambda x: x[0])
        out.append({"key": gk, "label": lab, "kind": kind, "n": n, "total": total,
                    "missing": [t["key"] for t in sects.TRADITIONS if gk not in per_church[t["key"]]],
                    "dates": dated, "undated": by_date.get(None, []),
                    "keys": [k for k, _ in used.most_common()]})
    _CACHE[year] = out
    return out


def weekly_fast_churches(year: int) -> int:
    """How many churches keep a weekly (Wednesday and/or Friday) fast in the app's data."""
    n = 0
    for t in sects.TRADITIONS:
        p = sects.preset(t["key"])
        try:
            if L.weekly_fasts(t["key"], p["fixed_calendar"], p["paschalion"], year):
                n += 1
        except Exception:
            pass
    return n

