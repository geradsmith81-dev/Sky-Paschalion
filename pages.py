"""Sky Paschalion pages: render_*(ctx). Every table is HTML (class px-table / px-grid), never st.dataframe.

ctx keys (app.py): place, now, today, tz, trad, trad_key, cal, rule, lang, hours, variant, phone, feast_cal,
apply_preset.
"""
from __future__ import annotations

import html
import os
import re
from datetime import date, datetime, timedelta

import streamlit as st

import calendars as cal
import common
import explain
import feasts
import liturgy as L
import names
import ornaments as orn
import orient_live
import paschalion
import sects
import sky_engine
import sky_layer
import theme

HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape


# ============================================================================== small helpers
def card(title_html: str, body: str, cls: str = "") -> str:
    return f"<div class='px-card {cls}'><h3>{title_html}</h3>{body}</div>"


def kv(rows) -> str:
    return "<div class='px-kv'>" + "".join(f"<div>{a}</div><div>{b}</div>" for a, b in rows) + "</div>"


def table(head, rows, row_cls=None) -> str:
    th = "".join(f"<th>{h}</th>" for h in head)
    body = []
    for i, r in enumerate(rows):
        c = f" class='{row_cls[i]}'" if row_cls and row_cls[i] else ""
        body.append(f"<tr{c}>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>")
    return f"<div class='px-scroll'><table class='px-table'><thead><tr>{th}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"


def tm(dt) -> str:
    return dt.strftime("%H:%M") if dt is not None else "—"


def rank_label(rank: str) -> str:
    return feasts.RANKS.get(rank, (9, rank.replace("_", " ")))[1]


_ENTRY_CACHE: dict = {}


def _entry_for(info, key: str):
    """The feasts.py entry for `key` that applies to tradition info = (trad_key, cal, rule), or None."""
    if not info:
        return None
    if info not in _ENTRY_CACHE:
        eff = L.effective(*info)
        idx = {}
        for entries in (feasts.FIXED, feasts.MOVABLE, feasts.SPECIAL):
            for e in entries:
                if feasts._applies(e, eff):
                    idx.setdefault(e["key"], e)
        _ENTRY_CACHE[info] = (idx, eff.get("fixed_calendar", info[1]))
    idx, c_own = _ENTRY_CACHE[info]
    e = idx.get(key)
    return (e, c_own) if e else None


def explain_pop(key, inner: str, info=None, pop: str = "inline", text: str | None = None,
                rank: str | None = None) -> str:
    """Wrap a feast/fast name (chip or plain) in a click-to-open explanation. pop: inline | float | float_r."""
    body = text if text is not None else explain.text(key) if key else None
    if not body:
        return inner
    title = E(names.NAMES.get(key, {}).get("en", key.replace("_", " "))) if key else "Wednesday and Friday fast"
    meta = []
    if rank:
        meta.append(E(rank_label(rank)))
    ent = _entry_for(info, key) if key else None
    if ent:
        rt = _rule_text(*ent)
        if rt:
            meta.append(E(rt) if ("month" in ent[0] or "base" in ent[0]) else rt)
    foot = f"<div class='px-pop-src'>{' · '.join(meta)}</div>" if meta else ""
    cls = {"inline": "px-pop px-pop-inline", "float": "px-pop", "float_r": "px-pop px-pop-r"}.get(pop, "px-pop px-pop-inline")
    return (f"<details class='{cls}'><summary title='Click for an explanation'>{inner}</summary>"
            f"<div class='px-popbody'><div class='px-pop-title'>{title}</div>{E(body)}{foot}</div></details>")


def chip_for(key: str, rank: str, kind: str, lang: str, variant=None, info=None, pop: str = "inline") -> str:
    k = theme.chip_kind(kind, rank)
    title = E(rank_label(rank))
    chip = (f"<span class='px-chip' title='{title}' style='background:{theme.CHIP[k]}'>"
            f"{L.feast_name_html(key, lang, variant)}</span>")
    return explain_pop(key, chip, info, pop, rank=rank)


def plain_chip(kind: str, text: str) -> str:
    return f"<span class='px-chip' style='background:{theme.CHIP[kind]}'>{E(text)}</span>"


def day_chips(ctx, d: date, events=None, with_periods=True, with_weekly=True, pop: str = "inline") -> str:
    k, c, r, lg, v = ctx["trad_key"], ctx["cal"], ctx["rule"], ctx["lang"], ctx["variant"]
    info = (k, c, r)
    if events is None:
        events, _ = L.events_between(k, c, r, d, d)
    out = [chip_for(key, rank, kind, lg, v, info, pop) for dd, key, rank, kind in events if dd == d]
    shown = {key for dd, key, rank, kind in events if dd == d}
    if with_periods:
        for s, e, key in L.periods_covering(k, c, r, d):
            if key not in shown and s != e:
                chip = (f"<span class='px-chip' title='{E(L.civil(s))} – {E(L.civil(e))}' "
                        f"style='background:{theme.CHIP['fast']}'>{L.feast_name_html(key, lg, v)}</span>")
                out.append(explain_pop(key, chip, info, pop))
    if with_weekly and L.is_weekly_fast(k, c, r, d):
        out.append(explain_pop(None, plain_chip("fast", "Fast day (" + ("Friday" if d.weekday() == 4 else "Wednesday") + ")"),
                               None, pop, text=explain.WEEKLY))
    return "".join(out)


def notes_for(ctx, d0: date, d1: date):
    _, notes = L.events_between(ctx["trad_key"], ctx["cal"], ctx["rule"], d0, d1)
    for n in notes:
        st.html(f"<div class='px-warn'>{E(n)}</div>")


def cal_note(ctx):
    t = ctx["trad"]
    if ctx["feast_cal"] != ctx["cal"] and not (ctx["cal"] == "byzantine" and ctx["feast_cal"] == "julian"):
        st.html(f"<div class='px-note'>Dates are shown in the {E(L.cal_label(ctx['cal']))} calendar; the fixed feasts "
                f"of {E(t['name_en'])} are kept by the {E(cal.NAME[ctx['feast_cal']])} calendar.</div>")


def hour_html(system: str, key: str, lang: str, en_fallback: str) -> str:
    try:
        i = names.HOUR_KEYS[system].index(key)
        en = names.HOURS[system]["en"][i]
        nat = names.HOURS[system].get(lang, [None] * 99)[i] if lang != "en" else None
    except (KeyError, ValueError, IndexError):
        return E(en_fallback)
    return theme.label(en, nat or "", lang)


# ============================================================================== Today
def _sky_covers(d: date) -> bool:
    """True if the loaded ephemeris covers d with a margin (the Moon's next full/new moon is searched ahead)."""
    try:
        return sky_engine.covers(d - timedelta(days=40)) and sky_engine.covers(d + timedelta(days=40))
    except Exception:
        return False


def render_today(ctx):
    t, c, r, lg, v = ctx["trad"], ctx["cal"], ctx["rule"], ctx["lang"], ctx["variant"]
    pl, now, d = ctx["place"], ctx["now"], ctx["today"]
    lat, lon, tz = pl["lat"], pl["lon"], pl["tz"]
    sky_ok = _sky_covers(d)
    sun = sky_layer.sun_times(d, lat, lon, tz) if sky_ok else {}

    # --- the date in the chosen calendar (one calendar card)
    x = cal.from_gregorian(c, d)
    lines = [f"<div class='px-big'>{L.date_html(c, d, lg)}</div>"]
    if c != "gregorian":
        lines.append(f"<div class='px-muted'>Civil date: {E(d.strftime('%A'))} {E(L.civil(d))} (Gregorian)</div>")
    if c in ("coptic", "ethiopian") and x.month == 13:
        lines.append("<div class='px-muted'>The short thirteenth month (epagomenal days).</div>")
    if sun.get("sunset") is not None and now >= sun["sunset"]:
        nd = d + timedelta(days=1)
        lines.append(f"<div class='px-obs'>After sunset ({tm(sun['sunset'])}) the liturgical day of "
                     f"{L.date_html(c, nd, lg)} has begun (Vespers of the eve).</div>")
    seas = L.season(ctx["trad_key"], c, r, d)
    if seas:
        lines.append(f"<div class='px-line'><b>Season:</b> {E(' · '.join(seas))}</div>")
    chips = day_chips(ctx, d)
    lines.append(f"<div style='margin-top:.35rem'>{chips or '<span class=px-muted>No feast or fast of this tradition today.</span>'}</div>")
    # next Pascha
    p = L.pascha(d.year, r)
    if p is not None and p < d:
        p = L.pascha(d.year + 1, r)
    if p is not None:
        days = (p - d).days
        lines.append(f"<div class='px-line'><b>Pascha:</b> {L.date_html(c, p, lg)}"
                     f"{'' if days == 0 else f' (in {days} days)'}{' — today. Christ is risen!' if days == 0 else ''}</div>")
    else:
        lines.append("<div class='px-line'>Astronomical Pascha is unavailable for this year (DE440s covers 1850–2149).</div>")
    title = f"Today in the {L.cal_label_html(c)} calendar"
    notes_for(ctx, d, d)
    cal_note(ctx)

    # --- sun, hours, Moon
    if not sky_ok:
        st.html(card(title, "".join(lines)))
        st.html("<div class='px-warn'>The Sun, the Moon, the hours of prayer and the sunrise point need the JPL DE440s "
                "ephemeris, which covers 1850–2149; they are not shown for this date.</div>")
        tgt = "east"
        orient_live.show(sky_layer.EAST, tgt, pl.get("name", ""), None, lat, lon, title_html="Face east · ad orientem")
        return
    if sun.get("polar"):
        sun_rows = [("Sun", "Polar day: the Sun does not set" if sun["polar"] == "polar_day" else "Polar night: the Sun does not rise")]
    else:
        sun_rows = []
    sun_rows += [("Dawn (civil)", tm(sun.get("dawn_civil"))), ("Sunrise", tm(sun.get("sunrise"))),
                 ("Solar noon", tm(sun.get("solar_noon"))), ("Sunset", tm(sun.get("sunset"))),
                 ("Dusk (civil)", tm(sun.get("dusk_civil")))]
    sys_ = ctx["hours"]
    nxt = None
    for dd in (d, d + timedelta(days=1)):
        for h in sky_layer.canonical_hours(dd, lat, lon, tz, sys_):
            if h["start"] is not None and h["start"] > now:
                nxt = h
                break
        if nxt:
            break
    if nxt:
        when = tm(nxt["start"]) + ("" if nxt["start"].date() == d else f" ({L.civil(nxt['start'].date())})")
        hour_txt = (f"{hour_html(sys_, nxt['key'], lg, nxt['name_en'])} at <b>{when}</b>"
                    + (" <span class='px-muted'>(nominal clock time: polar)</span>" if nxt.get("polar_fallback") else ""))
    else:
        hour_txt = "—"
    mp = sky_layer.moon_phase(now)
    nfm = mp["next_full_moon"].astimezone(now.tzinfo)
    moon_html = (f"<div style='display:flex;align-items:center;gap:.8rem'>{theme.moon(mp['illumination'], mp['waxing'], 46)}"
                 f"<div><b>{E(mp['phase_name'])}</b>, {mp['illumination'] * 100:.0f}% lit, age {mp['age_days']:.1f} days"
                 f"<div class='px-muted'>Next full moon: {E(L.civil(nfm.date()))} {tm(nfm)}</div></div></div>")
    sky_body = (kv(sun_rows) + f"<div class='px-line' style='margin-top:.4rem'><b>Next hour of prayer</b> "
                f"({E(L.HOURS_NAME[sys_])}): {hour_txt}</div>" + "<div style='margin-top:.5rem'>" + moon_html + "</div>")

    if ctx["phone"]:
        st.html(card(title, "".join(lines)))
        st.html(card(f"The sky at {E(pl.get('name', ''))}", sky_body))
    else:
        a, b = st.columns([1.2, 1])
        with a:
            st.html(card(title, "".join(lines)))
        with b:
            st.html(card(f"The sky at {E(pl.get('name', ''))}", sky_body))

    # --- live compass
    sr = sky_layer.sunrise_azimuth(d, lat, lon, tz)
    opts = ["east", "jerusalem"] + (["sunrise"] if sr is not None else [])
    if st.session_state.get("orient_target") not in opts:
        st.session_state["orient_target"] = "east"
    tgt = st.radio("Face", opts, key="orient_target", horizontal=True,
                   format_func=lambda k: orient_live.TARGETS[k][0])
    if tgt == "jerusalem":
        bearing = sky_layer.bearing_to_jerusalem(lat, lon)
        dist = sky_layer.distance_to_jerusalem_km(lat, lon)
    elif tgt == "sunrise":
        bearing, dist = sr, None
    else:
        bearing, dist = sky_layer.EAST, None
    if sr is None:
        st.caption("No sunrise here today (polar day or night), so the sunrise point is not offered.")
    orient_live.show(bearing, tgt, pl.get("name", ""), dist, lat, lon,
                     title_html={"east": "Face east · ad orientem", "jerusalem": "Toward Jerusalem",
                                 "sunrise": "Toward today's sunrise"}[tgt])


# ============================================================================== Month
def _shift_month(c, k_y, k_m, step):
    y, m = st.session_state[k_y], st.session_state[k_m]
    m += step
    n = cal.months_in_year(c, y)
    if m < 1:
        y -= 1
        m = cal.months_in_year(c, y)
    elif m > n:
        y, m = y + 1, 1
    st.session_state[k_y], st.session_state[k_m] = y, m


def render_month(ctx):
    c, lg, d0 = ctx["cal"], ctx["lang"], ctx["today"]
    x = cal.from_gregorian(c, d0)
    k_y, k_m = f"mon_y_{c}", f"mon_m_{c}"
    st.session_state.setdefault(k_y, x.year)
    st.session_state.setdefault(k_m, x.month)
    if st.session_state[k_m] > cal.months_in_year(c, st.session_state[k_y]):
        st.session_state[k_m] = 1
    a, b, cc, dcol = st.columns([1, 2.2, 1.2, 1]) if not ctx["phone"] else (st.container(),) * 4
    with a:
        st.button("◀ Previous", key="mon_prev", on_click=_shift_month, args=(c, k_y, k_m, -1))
    with b:
        st.selectbox("Month", list(range(1, cal.months_in_year(c, st.session_state[k_y]) + 1)), key=k_m,
                     format_func=lambda m: L.month_name(c, m, lg))
    with cc:
        st.number_input(f"Year ({cal.ERA[c]})", min_value=1, max_value=9000, step=1, key=k_y)
    with dcol:
        st.button("Next ▶", key="mon_next", on_click=_shift_month, args=(c, k_y, k_m, 1))
    y, m = int(st.session_state[k_y]), int(st.session_state[k_m])
    try:
        days = cal.month_dates(c, y, m)
    except Exception as ex:   # out of datetime range
        st.html(f"<div class='px-warn'>That month cannot be shown ({E(str(ex))}).</div>")
        return
    if days[0].year < 2 or days[-1].year > 9998:
        st.html("<div class='px-warn'>That month is outside the supported range of years.</div>")
        return
    k, r, v = ctx["trad_key"], ctx["rule"], ctx["variant"]
    events, notes = L.events_between(k, c, r, days[0], days[-1])
    st.html(f"<h3 style='margin:.2rem 0'>{L.month_name_html(c, m, lg)} {y} {E(cal.ERA[c])}</h3>"
            f"<div class='px-muted'>{E(L.cal_label(c))} · civil dates {E(L.civil(days[0]))} – {E(L.civil(days[-1]))} (Gregorian)</div>")
    for n in notes:
        st.html(f"<div class='px-warn'>{E(n)}</div>")
    cal_note(ctx)

    def cell(dd: date) -> tuple[str, str]:
        cx = cal.from_gregorian(c, dd)
        chips = day_chips(ctx, dd, events, pop="inline" if ctx["phone"] else ("float_r" if dd.weekday() >= 4 else "float"))
        cls = []
        if dd.weekday() == 6:
            cls.append("px-sun")
        if any(e[0] == dd and e[3] == "feast" and feasts.RANKS.get(e[2], (9,))[0] <= 1 for e in events):
            cls.append("px-feast")
        elif L.periods_covering(k, c, r, dd) or L.is_weekly_fast(k, c, r, dd):
            cls.append("px-fast")
        if dd == d0:
            cls.append("px-today")
        civ = f"{dd.day}" + (f" {dd.strftime('%b')}" if dd.day == 1 or dd == days[0] else "")
        if c == "gregorian":
            head = f"<span class='px-civ'>{dd.day}</span>"
        else:
            head = f"<span class='px-cal'>{cx.day}</span><span class='px-civ' title='Civil (Gregorian) date'>{E(civ)}</span>"
        return " ".join(cls), head + "<div style='clear:both'></div>" + chips

    if ctx["phone"]:
        rows = []
        for dd in days:
            cls, inner = cell(dd)
            rows.append(f"<div class='px-list-day {'px-today' if dd == d0 else ''}'><b>{L.weekday_html(dd, lg)}</b> "
                        f"{inner}</div>")
        st.html("".join(rows))
    else:
        head = "".join(f"<th>{L.weekday_html(date(2024, 1, 1) + timedelta(days=i), lg)}</th>" for i in range(7))
        cells = ["<td class='px-empty'></td>"] * days[0].weekday()
        for dd in days:
            cls, inner = cell(dd)
            cells.append(f"<td class='{cls}'>{inner}</td>")
        while len(cells) % 7:
            cells.append("<td class='px-empty'></td>")
        trs = "".join("<tr>" + "".join(cells[i:i + 7]) + "</tr>" for i in range(0, len(cells), 7))
        st.html(f"<table class='px-grid'><thead><tr>{head}</tr></thead><tbody>{trs}</tbody></table>")
    st.html(theme.legend(["pascha", "great_feast", "feast", "commemoration", "fast", "strict_fast", "movable"]))


# ============================================================================== Year
def render_year(ctx):
    c, r, lg, v, k, d0 = ctx["cal"], ctx["rule"], ctx["lang"], ctx["variant"], ctx["trad_key"], ctx["today"]
    x = cal.from_gregorian(c, d0)
    ky = f"year_{c}"
    st.session_state.setdefault(ky, x.year)
    y = int(st.number_input(f"Year of the {L.cal_label(c)} calendar ({cal.ERA[c]})", min_value=2, max_value=8999,
                            step=1, key=ky))
    try:
        s = cal.year_start(c, y)
        e = cal.year_start(c, y + 1) - timedelta(days=1)
    except Exception as ex:
        st.html(f"<div class='px-warn'>That year cannot be shown ({E(str(ex))}).</div>")
        return
    if s.year < 2 or e.year > 9998:
        st.html("<div class='px-warn'>That year is outside the supported range.</div>")
        return
    events, notes = L.events_between(k, c, r, s, e)
    st.html(f"<div class='px-muted'>{E(L.cal_label(c))} year {y} {E(cal.ERA[c])} runs from {E(L.civil(s))} to "
            f"{E(L.civil(e))} (civil, Gregorian). Paschalion: {E(L.rule_label(r))}.</div>")
    for n in notes:
        st.html(f"<div class='px-warn'>{E(n)}</div>")
    cal_note(ctx)
    st.subheader("Feasts and commemorations")
    rows, rc = [], []
    for dd, key, rank, kind in events:
        if kind == "fast":
            continue
        rows.append([L.date_html(c, dd, lg), E(L.civil(dd)), chip_for(key, rank, kind, lg, v, (k, c, r)), E(rank_label(rank))])
        rc.append("px-today-row" if dd == d0 else "")
    st.html(table(["Date (" + E(cal.NAME[c]) + ")", "Civil date", "Feast", "Rank"], rows, rc))

    st.subheader("Fasts")
    per = []
    for gy in range(s.year - 1, e.year + 1):
        per += [p for p in L.year_events(k, c, r, gy)[1] if p[1] >= s and p[0] <= e and p not in per]
    per.sort()
    frows = [[L.date_html(c, a, lg, weekday=False), L.date_html(c, b, lg, weekday=False),
              f"{(b - a).days + 1}", explain_pop(key, f"<span class='px-fxname'>{L.feast_name_html(key, lg, v)}</span>",
                                                   (k, c, r))] for a, b, key in per]
    st.html(table(["Begins", "Ends", "Days", "Fast"], frows))
    wf = sorted(dd for gy in range(s.year, e.year + 1) for dd in L.weekly_fasts(k, c, r, gy) if s <= dd <= e)
    st.caption(f"Besides these, {len(wf)} Wednesdays and Fridays in this year are kept as fast days "
               f"({'Fridays only, Latin practice' if ctx['trad'].get('rite') == 'latin' else 'Wednesdays and Fridays'}; "
               "fast-free weeks and great feasts excluded; simplified, no fish/oil gradations).")

    st.subheader("The movable cycle (from Pascha)")
    ps = [gy for gy in range(s.year, e.year + 1) if (L.pascha(gy, r) is not None and s <= L.pascha(gy, r) <= e)]
    if not ps:
        st.html("<div class='px-warn'>No Pascha can be computed in this year with this rule.</div>")
        return
    P = L.pascha(ps[0], r)
    mv_keys = {m["key"] for m in feasts.MOVABLE} | {"pascha"}
    allev = []
    for gy in (ps[0] - 1, ps[0], ps[0] + 1):
        allev += list(L.year_events(k, c, r, gy)[0])
    mrows = sorted({(dd, key, rank, kind) for dd, key, rank, kind in allev
                    if key in mv_keys and -80 <= (dd - P).days <= 80})
    st.html(table(["Days from Pascha", "Date (" + E(cal.NAME[c]) + ")", "Civil date", "Feast or fast"],
                  [[f"{(dd - P).days:+d}" if dd != P else "0", L.date_html(c, dd, lg), E(L.civil(dd)),
                    chip_for(key, rank, kind, lg, v, (k, c, r))] for dd, key, rank, kind in mrows]))
    with st.expander("Every date the engine derives from Pascha (all traditions)"):
        mv = L.movable(ps[0], r) or {}
        st.html(table(["Key", "Days from Pascha", "Civil date"],
                      [[E(names.NAMES.get(kk, {}).get("en", kk.replace("_", " "))), f"{(dd - P).days:+d}", E(L.civil(dd))]
                       for kk, dd in sorted(mv.items(), key=lambda z: z[1])]))


# ============================================================================== Feasts dictionary
def _rule_text(e: dict, c_own: str) -> str:
    if "month" in e:
        cc = c_own if e["cal"] == "own" else e["cal"]
        mc = "julian" if cc in ("byzantine", "revised_julian", "gregorian") else cc
        mn = names.MONTHS[mc]["en"][e["month"] - 1]
        txt = f"{e['day']} {mn} ({cal.NAME.get(cc, cc)})"
        if e.get("rule") == "nearest_sunday":
            txt += ", kept on the nearest Sunday"
        return txt
    if "base" in e:
        b = e["base"]
        bn = "Pascha" if b == "pascha" else names.NAMES.get(b, {}).get("en", b.replace("_", " "))
        o = e.get("offset_days", 0)
        return bn if o == 0 else f"{bn} {o:+d} days"
    return E(e.get("note", ""))


def render_feasts(ctx):
    t, c, r, lg, v, k = ctx["trad"], ctx["cal"], ctx["rule"], ctx["lang"], ctx["variant"], ctx["trad_key"]
    eff = L.effective(k, c, r)
    gy = ctx["today"].year
    st.html(f"<div class='px-muted'>Every feast and fast in the app's tables that {theme.tradition_badge(t, lg)} keeps, "
            f"with the rule, this year's civil date and the sources. A <sup>?</sup> marks a liturgical-language form "
            f"that has not been verified (listed on the About page).</div>")
    cal_note(ctx)
    if L.year_events(k, c, r, gy)[2]:
        st.html(f"<div class='px-warn'>{E(L.year_events(k, c, r, gy)[2])}</div>")
    ev = {}
    for dd, key, rank, kind in L.year_events(k, c, r, gy)[0]:
        ev.setdefault(key, dd)
    rows = []
    for group, entries in (("Fixed", feasts.FIXED), ("Movable", feasts.MOVABLE), ("Season", feasts.SPECIAL)):
        for e in entries:
            if not feasts._applies(e, eff):
                continue
            dd = ev.get(e["key"])
            src = " ".join(f"<a href='{E(u)}' target='_blank' rel='noopener'>[{i + 1}]</a>"
                           for i, u in enumerate(e.get("sources", [])))
            rows.append([chip_for(e["key"], e.get("rank", "feast"), e.get("kind", "feast"), lg, v, (k, c, r)),
                         E(group), E(_rule_text(e, eff["fixed_calendar"])),
                         E(rank_label(e.get("rank", ""))),
                         (L.date_html(c, dd, lg, weekday=False) if dd else "<span class='px-muted'>not this year</span>"),
                         src + (f"<div class='px-muted'>{E(e['note'])}</div>" if e.get("note") and "month" in e else "")])
    st.html(table(["Feast or fast", "Kind", "Rule", "Rank", f"Date in {gy}", "Sources"], rows))


# ============================================================================== Paschalion
def render_paschalion(ctx):
    t, c, r, lg, d0 = ctx["trad"], ctx["cal"], ctx["rule"], ctx["lang"], ctx["today"]
    st.html(f"<div class='px-muted'>Pascha (Easter) by the three rules. {theme.tradition_badge(t, lg)} follows "
            f"<b>{E(L.rule_label(r))}</b>{' (changed in the settings)' if r != t['paschalion'] else ''}. "
            f"Civil (Gregorian) dates are the common reference; the church's own column is in the chosen calendar. "
            f"The astronomical rule needs the JPL DE440s ephemeris, which covers 1850–2149.</div>")
    a, b = st.columns(2) if not ctx["phone"] else (st.container(), st.container())
    with a:
        st.session_state.setdefault("pa_y0", d0.year)
        y0 = int(st.number_input("First year", min_value=1583, max_value=4000, step=1, key="pa_y0"))
    with b:
        st.session_state.setdefault("pa_n", 15)
        n = int(st.slider("Number of years", 5, 60, key="pa_n"))
    rows, rc = [], []
    for y in range(y0, y0 + n):
        w, e_, a_ = L.pascha(y, "western"), L.pascha(y, "eastern"), L.pascha(y, "astronomical")
        mine = {"western": w, "eastern": e_, "astronomical": a_}[r]
        same = "all three" if (a_ is not None and w == e_ == a_) else ("Western = Eastern" if w == e_ else "")
        rows.append([str(y), (L.date_html(c, mine, lg) if mine else "<span class='px-muted'>unavailable</span>"),
                     E(L.civil(w)), E(L.civil(e_)),
                     E(L.civil(a_)) if a_ else "<span class='px-muted'>unavailable (outside 1850–2149)</span>",
                     f"<span class='px-obs'>{same}</span>" if same else ""])
        rc.append("px-today-row" if y == d0.year else "")
    st.html(table(["Year", f"{E(t['name_en'])} ({E(cal.NAME[c])})", "Western", "Eastern", "Astronomical", "Common date"],
                  rows, rc))

    st.subheader("Paschal full moons and the equinox")
    st.session_state.setdefault("pa_yd", d0.year)
    yd = int(st.number_input("Year to examine", min_value=1583, max_value=4000, step=1, key="pa_yd"))
    cards = []
    for rule in ("western", "eastern"):
        P = paschalion.easter(yd, rule)
        pfm = paschalion.paschal_full_moon(yd, rule)
        eq = paschalion.ecclesiastical_equinox(yd, rule)
        cards.append(card(E(paschalion.RULE_NAME[rule]), kv([
            ("Pascha", f"<b>{E(L.civil(P))}</b>"),
            ("Ecclesiastical full moon", E(L.civil(pfm)) + f" ({E(pfm.strftime('%A'))})"),
            ("Ecclesiastical equinox", E(L.civil(eq)) + (" (21 March Julian)" if rule == "eastern" else " (21 March)")),
            ("Full moon → Pascha", f"{(P - pfm).days} days"),
        ])))
    try:
        det = paschalion.astronomical_detail(yd)
        fl = det["full_moon_local"]
        ke = det["knife_edge_hours"]
        edge = (f"<div class='px-warn'>Knife-edge year: the full moon falls only {ke:.2f} h from the Saturday/Sunday "
                f"midnight (Jerusalem mean time). A different ephemeris, ΔT or meridian could move Easter by a week.</div>"
                if ke is not None and ke < 2 else
                f"<div class='px-muted'>Margin from the Saturday/Sunday midnight: {ke:.1f} h.</div>" if ke is not None else "")
        cards.append(card(E(paschalion.RULE_NAME["astronomical"]), kv([
            ("Pascha", f"<b>{E(L.civil(det['easter']))}</b>"),
            ("March equinox (UTC)", E(det["equinox_utc"].strftime("%d %b %Y %H:%M"))),
            ("Full moon (UTC)", E(det["full_moon_utc"].strftime("%d %b %Y %H:%M"))),
            ("Full moon, Jerusalem mean time", E(fl.strftime("%d %b %Y %H:%M %A"))),
            ("Full moon after equinox", f"{det['hours_fm_after_equinox'] / 24:.1f} days"),
        ]) + edge))
    except paschalion.OutsideEphemeris:
        cards.append(card(E(paschalion.RULE_NAME["astronomical"]),
                          f"<div class='px-warn'>Unavailable for {yd}: the JPL DE440s ephemeris covers 1850–2149.</div>"))
    st.html("<div class='px-cols'>" + "".join(cards) + "</div>")
    st.caption("Western and Eastern use the ecclesiastical (tabular) Moon and a fixed 21 March equinox; the Eastern rule "
               "reckons them in the Julian calendar. The astronomical rule (WCC/MECC Aleppo 1997) takes the true equinox "
               "and full moon from JPL DE440s and dates the full moon at the meridian of Jerusalem.")


# ============================================================================== Hours
def render_hours(ctx):
    pl, lg, sys_ = ctx["place"], ctx["lang"], ctx["hours"]
    st.session_state.setdefault("hours_date", ctx["today"])
    d = st.date_input("Date", key="hours_date", min_value=date(1850, 1, 2), max_value=date(2149, 12, 30))
    lat, lon, tz = pl["lat"], pl["lon"], pl["tz"]
    st.html(f"<div class='px-muted'>{E(sky_layer.SYSTEM_NAME[sys_])} at {E(pl.get('label', pl['name']))} "
            f"({lat:.3f}°, {lon:.3f}°, {E(tz)}). Offices are set by the Sun: 'the third hour' is three unequal "
            f"(temporal) hours after sunrise, Sext is solar noon, Vespers is sunset.</div>")
    hours = sky_layer.canonical_hours(d, lat, lon, tz, sys_)
    rows, rc = [], []
    now = ctx["now"]
    for h in hours:
        s = h["start"]
        when = tm(s) + ("" if s is None or s.date() == d else f" <span class='px-muted'>({E(L.civil(s.date()))})</span>")
        flag = " <span class='px-prov'>polar: nominal time</span>" if h.get("polar_fallback") else ""
        rows.append([hour_html(sys_, h["key"], lg, h["name_en"]), when + flag, E(str(h.get("anchor", ""))), E(h.get("note", ""))])
        rc.append("px-today-row" if (s is not None and d == ctx["today"] and s <= now < s + timedelta(hours=1)) else "")
    st.html(table(["Office", "Begins", "Set by", "Note"], rows, rc))
    sun = sky_layer.sun_times(d, lat, lon, tz)
    if sun.get("polar"):
        st.html(f"<div class='px-note'>{'Polar day: the Sun does not set' if sun['polar'] == 'polar_day' else 'Polar night: the Sun does not rise'} "
                "on this date. Offices fall back to their nominal clock times.</div>")
    if sys_ == "ethiopian" and d == ctx["today"]:
        hh, mm, part = sky_layer.ethiopian_clock(now)
        st.caption(f"Ethiopian clock now: {hh}:{mm:02d} of the {'day (counted from 06:00)' if part == 'day' else 'night (counted from 18:00)'}.")
    with st.expander("The Sun and the 24 unequal hours"):
        st.html(kv([(E(k.replace('_', ' ')), tm(v)) for k, v in sun.items()
                    if isinstance(v, datetime)]))
        th = sky_layer.temporal_hours(d, lat, lon, tz)
        if th:
            st.html(table(["Hour", "Begins", "Ends", "Length"],
                          [[f"{E(str(h.get('part', '')))} hour {h.get('index', i + 1)}", tm(h.get("start")), tm(h.get("end")),
                            f"{h.get('length_min', 0):.0f} min"] for i, h in enumerate(th)]))
        else:
            st.caption("No unequal hours at this place and date (polar day or night).")


# ============================================================================== Compare
COMPARE_DEFAULT = ["latin_catholic", "constantinople", "russian_orthodox", "coptic_orthodox", "armenian_etchmiadzin",
                   "ethiopian_orthodox", "syriac_orthodox", "assyrian_church_of_the_east"]


def render_compare(ctx):
    d0 = ctx["today"]
    st.html("<div class='px-muted'>Several churches side by side, each in its own calendar, Paschalion and first "
            "liturgical language (their own practice, not the settings above).</div>")
    st.session_state.setdefault("cmp_keys", [k for k in COMPARE_DEFAULT if k in sects.BY_KEY])
    st.session_state.setdefault("cmp_date", d0)
    keys = st.multiselect("Churches", [t["key"] for t in sects.TRADITIONS], key="cmp_keys",
                          format_func=lambda k: L.trad_label(sects.get(k)))
    d = st.date_input("Date", key="cmp_date", min_value=date(1583, 1, 1), max_value=date(4000, 12, 31))
    rows = []
    for k in keys:
        t = sects.get(k)
        p = sects.preset(k)
        c, r, lg = p["fixed_calendar"], p["paschalion"], p["lang"]
        sub = {"trad_key": k, "cal": c, "rule": r, "lang": lg, "variant": t.get("syriac_script")}
        P = L.pascha(d.year, r)
        nat, _ = L.nativity_date(k, c, r, d.year)
        chips = day_chips(sub, d)
        prov = "<span class='px-prov' title='%s'>provisional</span>" % E(t.get("notes", "")[:300]) if t.get("provisional") else ""
        rows.append([theme.tradition_badge(t, lg) + prov,
                     L.date_html(c, d, lg) + f"<div class='px-muted'>{E(L.cal_label(c))}</div>",
                     (L.date_html(c, P, lg, weekday=False) + f"<div class='px-muted'>{E(L.civil(P))} · {E(r)}</div>") if P else "—",
                     (L.date_html(c, nat, lg, weekday=False) + f"<div class='px-muted'>{E(L.civil(nat))}</div>") if nat else "—",
                     chips or "<span class='px-muted'>—</span>"])
    if rows:
        st.html(table(["Church", f"{E(L.civil(d))} in its calendar", f"Pascha {d.year}", f"Nativity {d.year}",
                       "Feasts and fasts that day"], rows))
    else:
        st.caption("Choose one or more churches.")


# ============================================================================== Traditions
def _primate(t) -> str:
    p = t.get("primate_now") or {}
    if not isinstance(p, dict):
        return E(str(p))
    src = p.get("source")
    s = E(p.get("name", "—"))
    if p.get("since"):
        s += f" (since {E(str(p['since']))})"
    s += f" <span class='px-muted'>as of {E(str(p.get('as_of', '')))}</span>"
    if src:
        s += f" <a href='{E(src)}' target='_blank' rel='noopener'>source</a>"
    return s


def render_traditions(ctx):
    cur = ctx["trad_key"]
    st.html("<div class='px-muted'>The churches of the ancient apostolic sees, by communion. 'Use' applies a church's "
            "calendar, Paschalion, language and hours. Entries marked <span class='px-prov'>provisional</span> rest on "
            "sources the content track could not fully confirm; the note says why.</div>")
    for ck in sects.COMMUNION_KEYS:
        com = next(x for x in sects.COMMUNIONS if x["key"] == ck)
        st.html(f"<h3 style='margin:.8rem 0 .1rem 0'>{theme.label(com['name_en'], com.get('name_native', ''), _lang_of(com.get('name_native', '')))}</h3>"
                f"<div class='px-muted'>{E(com.get('notes', ''))}</div>")
        for t in sects.by_communion(ck):
            lg = t["liturgical_languages"][0]
            tag = " (provisional)" if t.get("provisional") else ""
            mark = " ✓ in use" if t["key"] == cur else ""
            with st.expander(L.trad_label(t) + tag + mark, expanded=False):
                rows = [("See", E(t.get("see", ""))), ("Apostle", E(t.get("apostle", ""))),
                        ("Primate", E(t.get("primate_title", ""))), ("Now", _primate(t)),
                        ("Calendar", L.cal_label_html(t["fixed_calendar"])),
                        ("Paschalion", E(L.rule_label(t["paschalion"]))),
                        ("Languages", E(", ".join(L.lang_label(x) for x in t["liturgical_languages"]))),
                        ("Hours", E(L.HOURS_NAME.get(t["hours_system"], t["hours_system"]))),
                        ("Rite", E(str(t.get("rite", "")).replace("_", " "))),
                        ("Status", E(str(t.get("status", "")).replace("_", " ")))]
                if t.get("syriac_script"):
                    rows.append(("Syriac script", E(t["syriac_script"])))
                body = theme.tradition_badge(t, lg) + kv(rows)
                if t.get("provisional"):
                    body += f"<div class='px-warn'><span class='px-prov'>provisional</span> {E(t.get('notes', ''))}</div>"
                elif t.get("notes"):
                    body += f"<div class='px-note'>{E(t['notes'])}</div>"
                srcs = t.get("sources") or []
                if srcs:
                    body += "<div class='px-muted' style='margin-top:.3rem'>Sources: " + " ".join(
                        f"<a href='{E(u)}' target='_blank' rel='noopener'>[{i + 1}]</a>" for i, u in enumerate(srcs)) + "</div>"
                st.html(body)
                st.button("Use", key=f"use_{t['key']}", on_click=ctx["apply_preset"], args=(t["key"],),
                          disabled=(t["key"] == cur))


def _lang_of(text: str) -> str:
    """Guess the script of a communion's native name for font selection (Greek, Syriac or Latin)."""
    if re.search(r"[\u0700-\u074f]", text or ""):
        return "syc"
    if re.search(r"[\u0370-\u03ff\u1f00-\u1fff]", text or ""):
        return "grc"
    return "la"


# ============================================================================== How it works / About
def _md(name: str) -> str:
    p = os.path.join(HERE, name)
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return f"*{name} is missing from this copy of the app.*"


def render_how(ctx):
    st.markdown(_md("HOW_IT_WORKS.md"))
    with st.expander("Validation report (VALIDATION.md)", expanded=False):
        st.markdown(_md("VALIDATION.md"))


def render_about(ctx):
    em = orn.chi_rho_svg(180, uid="pxabout")
    st.html(f"<div class='px-cols'><div style='flex:0 0 auto'>{em}</div><div class='px-card' style='flex:1 1 20rem'>"
            "<h3>Sky Paschalion · <span lang='grc'>Πασχάλιον</span></h3>"
            "<div>The Christian calendars of the churches of the ancient apostolic sees — Catholic (Latin and Eastern "
            "Catholic), Eastern Orthodox, Oriental Orthodox and the Church of the East — with Pascha by the Western, "
            "Eastern and astronomical rules, the hours of prayer set by the Sun, and the Moon, from NASA JPL DE440s.</div>"
            "<div class='px-muted' style='margin-top:.4rem'>Part of the Sky series with Sky Luach, Sky Taqwim and Sky "
            "Gahshomar. The emblem is a Chi-Rho between Alpha and Omega in the manner of the Ravenna mosaics.</div>"
            "<div style='margin-top:.4rem'>Licence: MIT, Copyright (c) 2026 Gerad Smith. Fonts and data keep their own "
            "licences (THIRD_PARTY.md).</div></div></div>")
    with st.expander("Licence (LICENSE)"):
        st.code(_md("LICENSE"), language=None)
    with st.expander("Third-party material and credits (THIRD_PARTY.md)"):
        st.markdown(_md("THIRD_PARTY.md"))

    st.subheader("Provisional traditions")
    pv = [t for t in sects.TRADITIONS if t.get("provisional")]
    st.html(table(["Church", "Why provisional"],
                  [[E(L.trad_label(t)), E(t.get("notes", ""))] for t in pv]))

    st.subheader("Names not yet verified")
    st.caption("Liturgical-language forms that the content track could not confirm in a cited source "
               "(names.UNCERTAIN), plus the calendar and rule names added for the settings. They are shown in the app "
               "with a ? mark and should be checked by a speaker of the language.")
    rows = [[E(k), E(names.LANG_NAMES.get(lg, lg)), theme.native(form, lg)] for k, lg, form in names.uncertain_table()]
    rows += [[E(k), E(names.LANG_NAMES.get(lg, "Amharic" if lg == "am" else lg)), theme.native(form, lg)]
             for k, lg, form in L.APP_UNCERTAIN]
    st.html(f"<div class='px-muted'>{len(rows)} forms.</div>" + table(["Name", "Language", "Form"], rows))

    st.subheader("Sources")
    with st.expander("Traditions, feasts and names (SOURCES.md)"):
        st.markdown(_md("SOURCES.md"))
    try:
        _, _, fname = sky_engine.load()
        eph = os.path.basename(str(fname))
    except Exception:
        eph = "not loaded"
    st.caption(f"Ephemeris in use: {eph}. Place search: GeoNames (CC BY 4.0) via geonamescache. "
               "Magnetic declination: World Magnetic Model 2025 (NOAA/BGS) via pygeomag.")


# ============================================================================== summary windows (links under the menu)
def _pop_html(inner: str, title: str, body_html: str) -> str:
    return (f"<details class='px-pop px-pop-inline'><summary title='Click to see the list'>{inner}</summary>"
            f"<div class='px-popbody'><div class='px-pop-title'>{title}</div>{body_html}</div></details>")


def _church_list(keys) -> str:
    return "<br>".join(E(sects.get(k)["name_en"]) for k in keys)


def _group_names(g) -> str:
    seen, out = set(), []
    for k in g["keys"]:
        en = names.NAMES.get(k, {}).get("en", k.replace("_", " "))
        if en not in seen:
            seen.add(en)
            out.append(en)
    return " · ".join(out)


def _group_cell(g) -> str:
    k0 = g["key"] if g["key"] in explain.TEXT else g["keys"][0]
    head = f"<span class='px-fxname'><b>{E(g['label'])}</b></span>"
    cell = explain_pop(k0, head, None, "inline")
    if " · " in _group_names(g) or _group_names(g) != g["label"]:
        cell += f"<div class='px-muted' style='font-size:.8rem'>{E(_group_names(g))}</div>"
    return cell


def _dates_cell(g, year: int) -> str:
    parts = []
    for d, ks in g["dates"]:
        lab = f"<span class='px-fxname'>{d.day} {d.strftime('%b')}</span>"
        cnt = f"{len(ks)} church" + ("" if len(ks) == 1 else "es")
        parts.append(_pop_html(lab, f"{d.day} {d.strftime('%B')} {year}: {cnt}", _church_list(ks))
                     + f" <span class='px-muted' style='font-size:.8rem'>{cnt}</span>")
    if g["undated"]:
        parts.append(f"<span class='px-muted'>{len(g['undated'])} with no date in {year}</span>")
    return "<br>".join(parts)


def render_common(ctx):
    y0 = ctx["today"].year
    st.session_state.setdefault("common_year", y0)
    y = int(st.number_input("Civil year", min_value=1583, max_value=4000, step=1, key="common_year"))
    sm = common.summary(y)
    total = len(sects.TRADITIONS)
    allg = [g for g in sm if g["n"] == total]
    most = [g for g in sm if g["n"] < total]
    st.html(f"<div class='px-muted'>Every church in the app keeps these feasts and fasts, though often on different days: "
            f"the Western and Eastern Paschalia, the Julian and Gregorian calendars and the Coptic and Ethiopian calendars "
            f"move them apart, and the rites call them by different names. Dates are civil (Gregorian) dates in {y}, "
            f"each church following its own calendar and Paschalion. Click a name for an explanation, or a date for the "
            f"churches that keep it on that day.</div>")
    rows = []
    for g in allg:
        att = common.ATTESTED.get(g["key"])
        att_html = (_pop_html(f"<span class='px-fxname'>{E(att[0])}</span>", "Earliest evidence", E(att[1]))
                    if att else "<span class='px-muted'>—</span>")
        rows.append([_group_cell(g), E("Fast" if g["kind"] == "fast" else "Feast"), _dates_cell(g, y), att_html])
    wk = common.weekly_fast_churches(y)
    if wk == total:
        rows.append([explain_pop(None, "<span class='px-fxname'><b>Wednesday and Friday fast</b></span>", None,
                                 "inline", text=explain.WEEKLY),
                     "Fast", "<span class='px-muted'>every week, outside fast-free weeks and great feasts "
                             "(Latin Church: Fridays)</span>",
                     _pop_html("<span class='px-fxname'>c. 100</span>", "Earliest evidence",
                               "Didache 8.1: fast on Wednesday and Friday, not with the hypocrites on Monday and Thursday.")])
    st.html(f"<div class='px-dlg'><h3 style='margin:.6rem 0 .2rem 0'>Kept by all {total} churches</h3>"
            + table(["Feast or fast", "Kind", f"Dates in {y}", "First attested"], rows) + "</div>")
    rows = []
    for g in sorted(most, key=lambda g: -g["n"]):
        miss = g["missing"]
        miss_html = _pop_html(f"<span class='px-fxname'>{len(miss)} not listed</span>",
                              f"Not listed for {len(miss)} church" + ("" if len(miss) == 1 else "es"), _church_list(miss))
        rows.append([_group_cell(g), E("Fast" if g["kind"] == "fast" else "Feast"),
                     f"{g['n']} of {total}<div style='margin-top:.2rem'>{miss_html}</div>", _dates_cell(g, y)])
    st.html("<div class='px-dlg'><h3 style='margin:.9rem 0 .2rem 0'>Kept by many churches</h3>"
            + table(["Feast or fast", "Kind", "Churches", f"Dates in {y}"], rows) + "</div>")
    st.caption("Counts follow the app's tables, which list the major feasts only. 'Not listed' can be a gap in those "
               "tables rather than a difference in practice: for example, the Ethiopian and Eritrean churches do keep "
               "Holy Thursday. First-attestation notes come from the Early Church research of 16 November 2026, except "
               "that the Nativity and Theophany notes were split from one combined entry and the Nativity note adds an "
               "unverified citation (Chronograph of 354), and the Wednesday/Friday note cites Didache 8.1 (added for "
               "this app).")


def render_apostles(ctx):
    cur = ctx["trad_key"]
    groups = sects.by_apostle()
    st.html("<div class='px-muted'>Each church appears once, under its <b>principal</b> founding apostle. "
            "<span class='px-obs'>claimed</span> = the church itself claims that apostle's foundation; "
            "<span class='px-prov'>via mother church</span> = it inherits the claim from the church it descends from. "
            "These are traditions of origin, not historical findings.</div>")
    for name, desc in sects.APOSTLE_ORDER:
        ms = groups.get(name, [])
        if not ms:
            continue
        rows = []
        for t in ms:
            basis = ("<span class='px-obs'>claimed</span>" if t["apostle_basis"] == "claimed"
                     else "<span class='px-prov'>via mother church</span>")
            nm = E(t["name_en"]) + (" <span class='px-muted'>(selected)</span>" if t["key"] == cur else "")
            rows.append([nm, E(t.get("see", "")), basis, f"<span class='px-muted'>{E(t['apostle_note'])}</span>"])
        st.html(f"<div class='px-dlg'><h3 style='margin:.8rem 0 .1rem 0'>{E(name)} <span class='px-muted' style='font-size:.8em'>· "
                f"{len(ms)} {'church' if len(ms) == 1 else 'churches'}</span></h3><div class='px-muted'>{E(desc)}</div>"
                + table(["Church", "See", "Basis", "Note"], rows) + "</div>")


@st.dialog("What all the churches share", width="large")
def dialog_common(ctx):
    render_common(ctx)


@st.dialog("Churches by founding apostle", width="large")
def dialog_apostles(ctx):
    render_apostles(ctx)
