"""Tests for the Traditions track (sects, feasts, names).

Run from the module folder:  python -m pytest tests  (or: python tests/test_content.py)
If the Engine's paschalion/calendars modules are not importable, the TEST-ONLY stubs in
tests/_stub are put on sys.path. The stubs are never imported by the shipped modules.
"""
import os, sys
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
try:
    import paschalion  # noqa: F401  (real Engine module, if present)
except ImportError:
    sys.path.insert(0, os.path.join(HERE, "_stub"))

import sects, feasts, names

CALS = {"gregorian", "julian", "revised_julian", "coptic", "ethiopian", "byzantine"}
RULES = {"western", "eastern", "astronomical"}
HOURS = {"roman", "byzantine", "coptic", "ethiopian", "armenian", "west_syriac", "east_syriac"}


def _get(trad, year, key):
    return [d for d, k, r, kind in feasts.feasts_for(trad, year) if k == key]


def test_sects_schema():
    assert [c["key"] for c in sects.COMMUNIONS] == ["catholic", "eastern_orthodox", "oriental_orthodox", "church_of_the_east"]
    assert sects.DEFAULT_TRADITION == "latin_catholic"
    keys = [t["key"] for t in sects.TRADITIONS]
    assert len(keys) == len(set(keys))
    for t in sects.TRADITIONS:
        assert t["fixed_calendar"] in CALS and t["paschalion"] in RULES and t["hours_system"] in HOURS
        assert t["primate_now"]["as_of"] == "2026-11-15" and t["sources"]
        p = sects.preset(t["key"])
        assert set(p) == {"fixed_calendar", "paschalion", "lang", "hours_system"}
    eastern_catholic = [t for t in sects.TRADITIONS if t["communion"] == "catholic" and t["key"] != "latin_catholic"]
    assert len(eastern_catholic) == 23


def test_scope_no_protestant_entries():
    blob = " ".join(t["name_en"].lower() for t in sects.TRADITIONS)
    for word in ("anglican", "lutheran", "old catholic", "methodist"):
        assert word not in blob


def test_calendar_conversions():
    assert feasts.to_gregorian("coptic", 1742, 1, 1) == date(2025, 9, 11)      # Nayrouz 1742 AM
    assert feasts.to_gregorian("ethiopian", 2018, 1, 1) == date(2025, 9, 11)
    assert feasts.to_gregorian("julian", 2025, 12, 25) == date(2026, 1, 7)


def test_easter():
    assert feasts.easter(2026, "western") == date(2026, 4, 5)
    assert feasts.easter(2026, "eastern") == date(2026, 4, 12)
    assert feasts.easter(2025, "western") == feasts.easter(2025, "eastern") == date(2025, 4, 20)
    assert feasts.easter(2024, "eastern") == date(2024, 5, 5)


def test_nativity_dates():
    assert _get("latin_catholic", 2026, "nativity") == [date(2026, 12, 25)]
    assert _get("russian_orthodox", 2026, "nativity") == [date(2026, 1, 7)]
    assert _get("church_of_greece", 2026, "nativity") == [date(2026, 12, 25)]
    assert _get("coptic_orthodox", 2027, "nativity") == [date(2027, 1, 7)]
    assert _get("ethiopian_orthodox", 2026, "genna") == [date(2026, 1, 7)]
    assert _get("armenian_etchmiadzin", 2026, "nativity_theophany") == [date(2026, 1, 6)]
    assert _get("armenian_jerusalem", 2026, "nativity_theophany") == [date(2026, 1, 19)]


def test_ethiopian_fixed():
    assert _get("ethiopian_orthodox", 2026, "meskel") == [date(2026, 9, 27)]
    assert _get("ethiopian_orthodox", 2026, "timkat") == [date(2026, 1, 19)]
    assert _get("ethiopian_orthodox", 2024, "timkat") == [date(2024, 1, 20)]   # leap-year shift (Wikipedia)


def test_coptic_movable_2024():
    # ukmidcopts.org table for 2024: Nineveh 26-28 Feb, Lent 11 Mar, Easter 5 May
    f = dict((k, (s, e)) for s, e, k in feasts.fasts_for("coptic_orthodox", 2024))
    assert f["nineveh_fast"] == (date(2024, 2, 26), date(2024, 2, 28))
    assert f["great_lent_coptic"][0] == date(2024, 3, 11)
    assert f["apostles_fast"] == (date(2024, 6, 24), date(2024, 7, 11))
    assert _get("coptic_orthodox", 2024, "pascha") == [date(2024, 5, 5)]


def test_armenian_sunday_rules():
    # Eastern Prelacy example year 2017: Assumption 13 Aug, Exaltation 17 Sep, fasts 7-11 Aug, 11-15 Sep
    assert _get("armenian_cilicia", 2017, "assumption_armenian") == [date(2017, 8, 13)]
    assert _get("armenian_cilicia", 2017, "exaltation_cross_armenian") == [date(2017, 9, 17)]
    f = dict((k, (s, e)) for s, e, k in feasts.fasts_for("armenian_cilicia", 2017))
    assert f["assumption_fast_armenian"] == (date(2017, 8, 7), date(2017, 8, 11))
    assert f["exaltation_fast_armenian"] == (date(2017, 9, 11), date(2017, 9, 15))
    assert _get("armenian_etchmiadzin", 2026, "exaltation_cross_armenian") == [date(2026, 9, 13)]
    p = feasts.easter(2026, "western")
    assert (_get("armenian_etchmiadzin", 2026, "vardavar")[0] - p).days == 98


def test_byzantine_great_feasts_count():
    twelve = {k for d, k, r, kind in feasts.feasts_for("constantinople", 2026) if r == "great_feast"}
    assert len(twelve) == 12


def test_finland_western_pascha():
    assert _get("finnish_orthodox", 2026, "pascha") == [date(2026, 4, 5)]


def test_all_traditions_all_years_run():
    for t in sects.TRADITIONS:
        for y in (1950, 2000, 2026, 2027, 2099):
            ev = feasts.feasts_for(t["key"], y)
            assert ev and all(d.year == y for d, *_ in ev)
            assert any(k in ("pascha", "fasika") for _, k, _, _ in ev), (t["key"], y)


def test_names_cover_feasts_and_labels():
    for k in feasts.all_keys():
        assert k in names.NAMES and "en" in names.NAMES[k], k
    assert names.label("pascha", "grc").startswith("Pascha")
    assert names.label("pascha", "xx") == names.NAMES["pascha"]["en"]
    for cal in ("gregorian", "julian", "coptic", "ethiopian"):
        for lang, lst in names.MONTHS[cal].items():
            assert len(lst) == (13 if cal in ("coptic", "ethiopian") else 12), (cal, lang)
    for lang, lst in names.WEEKDAYS.items():
        assert len(lst) == 7, lang
    for sysk, d in names.HOURS.items():
        n = len(names.HOUR_KEYS[sysk])
        for lang, lst in d.items():
            assert len(lst) == n, (sysk, lang)
    for k, lang in names.UNCERTAIN:
        assert isinstance(k, str) and isinstance(lang, str)


def test_every_feast_and_fast_has_explanation():
    import explain
    keys = {e["key"] for grp in (feasts.FIXED, feasts.MOVABLE, feasts.SPECIAL) for e in grp}
    missing = sorted(k for k in keys if not explain.TEXT.get(k, "").strip())
    assert not missing, missing
    assert not sorted(set(explain.TEXT) - keys), "explanations for unknown keys"
    assert all(40 <= len(v) <= 600 for v in explain.TEXT.values())
    assert explain.WEEKLY.strip()

def test_every_church_has_founding_apostle():
    groups = sects.by_apostle()
    assert sum(len(v) for v in groups.values()) == len(sects.TRADITIONS)
    order = [a for a, _ in sects.APOSTLE_ORDER]
    assert set(groups) <= set(order), set(groups) - set(order)
    for t in sects.TRADITIONS:
        a = sects.APOSTLES[t["key"]]
        assert a[1] in ("claimed", "via mother church"), t["key"]


def test_common_groups_use_known_keys():
    keys = {e["key"] for grp in (feasts.FIXED, feasts.MOVABLE, feasts.SPECIAL) for e in grp}
    try:
        import common
    except ImportError:          # common imports liturgy -> streamlit; skip where streamlit is absent
        return
    for g in common.GROUPS:
        assert set(g[3]) <= keys, (g[0], set(g[3]) - keys)
    sm = {g["key"]: g for g in common.summary(2026)}
    assert sm["pascha"]["n"] == len(sects.TRADITIONS)
    assert {(d.month, d.day): len(v) for d, v in sm["nativity"]["dates"]}.get((12, 25)) == 32

if __name__ == "__main__":
    import inspect
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and inspect.isfunction(fn):
            try:
                fn(); print("PASS", name)
            except AssertionError as e:
                fails += 1; print("FAIL", name, e)
    print("failures:", fails)
    sys.exit(1 if fails else 0)
