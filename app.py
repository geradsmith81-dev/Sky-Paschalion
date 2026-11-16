"""Sky Paschalion · Πασχάλιον — the Christian calendars of the apostolic churches, with Pascha and the sky
from NASA JPL astronomy.

Run:  streamlit run app.py      (desktop: double-click "Start app.bat", port 8514)
"""
import os
import sys
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import streamlit as st  # noqa: E402

st.set_page_config(page_title="Sky Paschalion · Πασχάλιον",
                   page_icon=os.path.join(HERE, "assets", "icons", "favicon-32.png"),
                   layout="wide", initial_sidebar_state="auto")

from zoneinfo import ZoneInfo  # noqa: E402

import calendars as cal  # noqa: E402
import device  # noqa: E402
import liturgy as L  # noqa: E402
import locator  # noqa: E402
import names  # noqa: E402
import pages  # noqa: E402
import places  # noqa: E402
import sects  # noqa: E402
import sky_layer  # noqa: E402
import theme  # noqa: E402

PAGES = {
    "Today": ("Today", pages.render_today),
    "Month": ("Month", pages.render_month),
    "Year": ("Year", pages.render_year),
    "Feasts": ("Feasts & fasts", pages.render_feasts),
    "Paschalion": ("Paschalion", pages.render_paschalion),
    "Hours": ("Hours", pages.render_hours),
    "Compare": ("Compare", pages.render_compare),
    "Traditions": ("Traditions", pages.render_traditions),
    "How": ("How it works", pages.render_how),
    "About": ("About", pages.render_about),
}
ALL_SCRIPT_PAGES = ("Compare", "Traditions", "About", "Feasts")


# ---------------------------------------------------------------------------------------------- tradition state
def apply_preset(key: str, set_communion: bool = True):
    """Set the tradition and the four preset fields (calendar, Paschalion, language, hours)."""
    t = sects.get(key)
    p = sects.preset(key)
    if set_communion:
        st.session_state["communion"] = t["communion"]
    st.session_state["tradition"] = key
    st.session_state["cal"] = p["fixed_calendar"]
    st.session_state["rule"] = p["paschalion"]
    st.session_state["lang"] = p["lang"]
    st.session_state["hours"] = p["hours_system"]


def _on_communion():
    first = sects.by_communion(st.session_state["communion"])[0]["key"]
    apply_preset(first)


def _on_tradition():
    apply_preset(st.session_state["tradition"])


if "tradition" not in st.session_state or st.session_state["tradition"] not in sects.BY_KEY:
    apply_preset(sects.DEFAULT_TRADITION)
for _k, _opts in (("cal", L.CAL_OPTIONS), ("rule", L.RULE_OPTIONS), ("hours", L.HOURS_OPTIONS)):
    if st.session_state.get(_k) not in _opts:
        st.session_state[_k] = sects.preset(st.session_state["tradition"])[
            {"cal": "fixed_calendar", "rule": "paschalion", "hours": "hours_system"}[_k]]
_trad = sects.get(st.session_state["tradition"])
if st.session_state.get("lang") not in _trad["liturgical_languages"]:
    st.session_state["lang"] = _trad["liturgical_languages"][0]

# ---------------------------------------------------------------------------------------------- theme (fonts)
_page_now = st.session_state.get("page", "Today")
if _page_now in ALL_SCRIPT_PAGES:
    theme.apply()   # these pages show every church's native name: all bundled scripts
else:
    _scripts = set(theme.scripts_for_langs(_trad["liturgical_languages"]))
    _scripts |= set(theme.scripts_for_langs([L.CAL_NATIVE[st.session_state["cal"]][1]]))
    theme.apply(scripts=tuple(sorted(_scripts)))


# ---------------------------------------------------------------------------------------------- where the user is
def _browser_tz():
    try:
        return st.context.timezone
    except Exception:
        return None


if "place" not in st.session_state:
    guess = locator.place_from_timezone(_browser_tz())
    if guess is None:
        guess = dict(places.BY_NAME[places.DEFAULT], src="default")
    st.session_state["place"] = guess
    st.session_state["place_src"] = guess["src"]


def _on_pick():
    v = st.session_state.get("locator")
    p = v.get("pick") if hasattr(v, "get") else getattr(v, "pick", None)
    if not isinstance(p, dict) or "lat" not in p:
        return
    try:
        lat, lon = float(p["lat"]), float(p["lon"])
    except (TypeError, ValueError):
        return
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return
    if p.get("auto") and st.session_state.get("place_src") == "manual":
        return   # the user already chose a place by hand: keep it
    acc = p.get("acc") if isinstance(p.get("acc"), (int, float)) else None
    st.session_state["place"] = locator.place_from_device(lat, lon, acc, _browser_tz())
    st.session_state["place_src"] = "gps"


def _set_manual(pl: dict):
    st.session_state["place"] = dict(pl, src="manual")
    st.session_state["place_src"] = "manual"


# ---------------------------------------------------------------------------------------------- header + navigation
trad = sects.get(st.session_state["tradition"])
theme.header(tradition=trad, lang=st.session_state["lang"])
phone = device.phone()
page = st.radio("Page", list(PAGES), key="page", horizontal=True, format_func=lambda k: PAGES[k][0],
                label_visibility="collapsed")

_pl = st.session_state["place"]
_how = {"gps": "from your device", "timezone": "first guess from your time zone",
        "manual": "chosen by you", "default": "starting place"}.get(st.session_state.get("place_src"), "")
locator.show(f"{_pl.get('label', _pl['name'])}  ({_how})",
             auto=st.session_state.get("place_src") in ("default", "timezone"), on_pick=_on_pick)

# ---------------------------------------------------------------------------------------------- settings
device.switch()
panel = device.input_panel("Settings: tradition, calendar, place")
with panel:
    st.subheader("Tradition")
    st.selectbox("Communion", sects.COMMUNION_KEYS, key="communion", format_func=L.comm_label,
                 on_change=_on_communion,
                 help="The four communions of the ancient apostolic sees: Catholic, Eastern Orthodox, "
                      "Oriental Orthodox and the Church of the East.")
    _members = [t["key"] for t in sects.by_communion(st.session_state["communion"])]
    if st.session_state["tradition"] not in _members:
        apply_preset(_members[0], set_communion=False)
    st.selectbox("Church", _members, key="tradition", on_change=_on_tradition,
                 format_func=lambda k: L.trad_label(sects.get(k)) + (" (provisional)" if sects.get(k).get("provisional") else ""),
                 help="Choosing a church sets its calendar, Paschalion, language and hours below; each can then be changed.")
    trad = sects.get(st.session_state["tradition"])
    cal_key = st.selectbox("Fixed calendar", L.CAL_OPTIONS, key="cal", format_func=L.cal_label,
                           help="The calendar in which dates are shown and fixed feasts are kept. Byzantine (Anno Mundi) "
                                "is the Julian calendar with the era of the world, the year beginning on 1 September.")
    rule = st.selectbox("Paschalion (date of Pascha)", L.RULE_OPTIONS, key="rule", format_func=L.rule_label,
                        help="Western: Gregorian computus. Eastern: Julian (Alexandrian) computus. Astronomical: the "
                             "WCC Aleppo 1997 proposal, computed from JPL DE440s (1850-2149 only).")
    lang = st.selectbox("Display language", trad["liturgical_languages"], key="lang", format_func=L.lang_label,
                        help="Names are shown as 'English · liturgical language'.")
    hours = st.selectbox("Hours of prayer", L.HOURS_OPTIONS, key="hours", format_func=lambda k: L.HOURS_NAME[k])
    _p = sects.preset(trad["key"])
    _diff = [n for n, a, b in (("calendar", cal_key, _p["fixed_calendar"]), ("Paschalion", rule, _p["paschalion"]),
                               ("hours", hours, _p["hours_system"])) if a != b]
    if _diff:
        st.caption("Changed from the church's own practice: " + ", ".join(_diff) + ".")
        st.button("Restore the church's settings", on_click=apply_preset, args=(trad["key"],), key="restore")

    st.subheader("Your place")
    q = st.text_input("Search for a town or city", key="place_q", placeholder="e.g. Thessaloniki, Aleppo, Aksum")
    if q.strip():
        res = places.search(q)
        if res:
            pick = st.selectbox("Matches", range(len(res)), key="place_pick", format_func=lambda i: places.label(res[i]))
            if st.button("Use this place", key="place_use", width="stretch"):
                r = res[pick]
                _set_manual({"name": r["name"], "country": r["country"], "lat": r["lat"], "lon": r["lon"],
                             "tz": r["tz"], "label": places.label(r)})
                st.rerun()
        else:
            st.caption("No town of 15,000+ people by that name. Try a nearby city, or enter coordinates below.")
    pre = st.selectbox("…or a preset", ["—"] + [p["name"] for p in places.PRESETS], key="place_preset",
                       format_func=lambda n: n if n == "—" or not places.BY_NAME[n]["note"]
                       else f"{n} — {places.BY_NAME[n]['note']}")
    if pre != "—" and st.session_state.get("_last_preset") != pre:
        st.session_state["_last_preset"] = pre
        _set_manual(dict(places.BY_NAME[pre]))
        st.rerun()
    place = st.session_state["place"]
    place.setdefault("label", place["name"])
    with st.expander("Exact coordinates"):
        lat = st.number_input("Latitude (° north, negative = south)", -89.0, 89.0, float(place["lat"]), 0.0001,
                              format="%.4f", key=f"lat_{place['name']}_{place['lat']:.4f}")
        lon = st.number_input("Longitude (° east, negative = west)", -180.0, 180.0, float(place["lon"]), 0.0001,
                              format="%.4f", key=f"lon_{place['name']}_{place['lon']:.4f}")
        place = dict(place, lat=lat, lon=lon)
        st.caption(f"Time zone: {place['tz']}")
    st.caption(f"Using: {place['label']}")

# ---------------------------------------------------------------------------------------------- now (or a test date)
tz = ZoneInfo(place["tz"])
_ov = st.session_state.get("_now_override")
now = None
if _ov:
    try:
        now = datetime.fromisoformat(str(_ov))
        now = now.replace(tzinfo=tz) if now.tzinfo is None else now.astimezone(tz)
    except ValueError:
        now = None
if now is None:
    now = datetime.now(tz)

ctx = {
    "place": place, "now": now, "today": now.date(), "tz": place["tz"],
    "trad": trad, "trad_key": trad["key"], "cal": cal_key, "rule": rule, "lang": lang, "hours": hours,
    "variant": trad.get("syriac_script"), "phone": phone,
    "feast_cal": L.feast_calendar(trad, cal_key), "apply_preset": apply_preset,
}

PAGES[page][1](ctx)

st.html("<div class='px-meander' role='presentation' style='margin-top:1.2rem'></div>"
        "<div class='px-muted' style='font-size:.8rem'>Astronomy: NASA JPL DE440s via Skyfield. Dates follow each "
        "church's published rules as recorded in the app's sources; local custom may differ. "
        "Follow your parish or diocese for the days you keep.</div>")
