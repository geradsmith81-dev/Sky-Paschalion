"""The live 'Face east' compass (Today page), adapted from Sky Taqwim's qibla_live.py.

Christians have long prayed facing east (ad orientem), the direction of the rising Sun and of the Lord's
return; many also turn toward Jerusalem. The dial (N, E, S, W) and a gold arrow toward the chosen target are
drawn in Python; a small browser component turns them with the phone, like a compass:

* the phone's compass gives its heading from MAGNETIC north (iPhone/iPad: webkitCompassHeading after the user
  taps the button and allows "Motion & Orientation"; Android: the absolute device-orientation event,
  heading = 360 - alpha, plus screen.orientation.angle);
* the magnetic declination of the place (World Magnetic Model WMM2025, via pygeomag) turns that into a heading
  from TRUE north, the reference of all three bearings;
* the dial is turned by -heading (so N points to true north) and the arrow by (bearing - heading), so the
  arrow points to the target however the phone is turned. Within 5 degrees (phone held flat) the card says so.

Targets: due East (90 degrees true, the default), Jerusalem (initial great-circle bearing to the Church of the
Holy Sepulchre, sky_layer.bearing_to_jerusalem) and today's sunrise point (sky_layer.sunrise_azimuth).
Computers have no compass: the dial then stays with north at the top (the static drawing).
Nothing leaves the browser: the readings are used only to turn the drawing.

All layout is written as inline styles: on Streamlit Community Cloud the stylesheet given to
components.v2 (css=) is not applied. theme.apply() also injects theme.ORIENT_LIVE_CSS page-wide.
"""
from __future__ import annotations

import html
import math
from datetime import datetime, timezone

import streamlit as st

import ornaments as orn
from theme import ORIENT_LIVE_CSS as CSS

try:   # World Magnetic Model (NOAA/BGS, public domain) through pygeomag (MIT); the coefficient file ships
    from pygeomag import GeoMag   # inside the pygeomag package (pygeomag/wmm/WMM_2025.COF)
    _GM = GeoMag(coefficients_file="wmm/WMM_2025.COF")   # NB: high_resolution=True crashes; do not use it
except Exception:   # pragma: no cover - the compass still works, only uncorrected for declination
    _GM = None

TARGETS = {
    "east": ("East (ad orientem)", "Due east, 90° from true north: the traditional direction of Christian prayer."),
    "jerusalem": ("Jerusalem", "Initial great-circle bearing to the Church of the Holy Sepulchre (31.7784 N, 35.2296 E)."),
    "sunrise": ("Sunrise point today", "Where the Sun rises today at this place (azimuth of the Sun's centre at sunrise)."),
}
TARGET_WORD = {"east": "east", "jerusalem": "Jerusalem", "sunrise": "the sunrise point"}


def declination(lat: float, lon: float, when: datetime | None = None) -> float | None:
    """Magnetic declination in degrees (east positive) from WMM2025, or None if the model is unavailable."""
    if _GM is None:
        return None
    t = when or datetime.now(timezone.utc)
    year = t.year + (t.timetuple().tm_yday - 0.5) / (366 if t.year % 4 == 0 else 365)
    try:
        return float(_GM.calculate(glat=float(lat), glon=float(lon), alt=0, time=year,
                                   allow_date_outside_lifespan=True).d)
    except Exception:
        return None


JS = r"""
const G = (window.__skypaschalionOrient = window.__skypaschalionOrient || {
  heading: null, shown: null, beta: 0, gamma: 0, acc: null, got: false, started: false, loop: false,
  view: null, facing: false
});

function norm180(a) { return ((a % 360) + 540) % 360 - 180; }
function screenAngle() {
  if (screen.orientation && typeof screen.orientation.angle === 'number') return screen.orientation.angle;
  if (typeof window.orientation === 'number') return window.orientation;
  return 0;
}

function onIOS(e) {          // iPhone / iPad: heading of the top of the device from magnetic north
  if (typeof e.webkitCompassHeading !== 'number' || isNaN(e.webkitCompassHeading)) return;
  G.heading = e.webkitCompassHeading + screenAngle();
  G.acc = (typeof e.webkitCompassAccuracy === 'number') ? e.webkitCompassAccuracy : null;
  G.beta = e.beta || 0; G.gamma = e.gamma || 0; G.got = true;
}
function onAbs(e) {          // Android: absolute orientation, alpha counter-clockwise from magnetic north
  if (e.alpha === null || e.alpha === undefined) return;
  G.heading = (360 - e.alpha) + screenAngle();
  G.beta = e.beta || 0; G.gamma = e.gamma || 0; G.got = true;
}
function onRel(e) { if (e.absolute === true) onAbs(e); }

function status(text, cls) {
  const V = G.view; if (!V || !V.status) return;
  if (V.status.textContent !== text) V.status.textContent = text;
  V.status.className = 'px-ol-status' + (cls ? ' ' + cls : '');
}

function frame() {
  const V = G.view;
  if (V && V.dial && V.dial.isConnected && G.heading !== null) {
    const target = G.heading + (V.decl || 0);                       // true heading of the top of the phone
    if (G.shown === null) G.shown = target;
    G.shown += norm180(target - G.shown) * 0.25;                    // smooth, and never spin the long way round
    const h = G.shown;
    V.dial.style.transform = 'rotate(' + (-h).toFixed(2) + 'deg)';
    V.arrow.style.transform = 'rotate(' + (V.bearing - h).toFixed(2) + 'deg)';
    const rel = norm180(V.bearing - h);
    const flat = Math.abs(G.beta) < 35 && Math.abs(G.gamma) < 35;
    const facing = flat && Math.abs(rel) <= 5;
    V.stage.classList.toggle('px-ol-on', facing);
    if (facing && !G.facing && navigator.vibrate) { try { navigator.vibrate(40); } catch (err) {} }
    G.facing = facing;
    if (!flat) status('Hold the phone flat, screen up, for a true reading.', 'px-ol-warn');
    else if (G.acc !== null && (G.acc < 0 || G.acc > 25)) status('The compass needs calibrating: move the phone in a figure of eight, then hold it flat.', 'px-ol-warn');
    else if (facing) status('You are facing ' + (V.target || 'east') + '.', 'px-ol-good');
    else {
      const turn = Math.round(Math.abs(rel));
      status('Turn ' + turn + '\u00b0 to the ' + (rel > 0 ? 'right' : 'left') + ' to face ' + (V.target || 'east') + ' (the arrow shows the way).', '');
    }
  }
  requestAnimationFrame(frame);
}

function start(manual) {
  if (G.started) return;
  G.started = true;
  if ('ondeviceorientationabsolute' in window) window.addEventListener('deviceorientationabsolute', onAbs, true);
  else window.addEventListener('deviceorientation', onRel, true);
  window.addEventListener('deviceorientation', onIOS, true);
  if (!G.loop) { G.loop = true; requestAnimationFrame(frame); }
  status('Reading the compass... hold the phone flat.', '');
  setTimeout(function () {
    if (G.got) return;
    G.started = false;
    const V = G.view; if (!V) return;
    status('No compass reading from this device. The dial shows the direction with north at the top.', 'px-ol-warn');
    if (window.self !== window.top && V.tab) V.tab.style.display = 'inline-block';
    if (V.btn) V.btn.style.display = manual ? 'inline-block' : 'none';
  }, 3000);
}

function askAndStart() {     // iPhone / iPad must ask, from a tap
  const D = window.DeviceOrientationEvent;
  if (D && typeof D.requestPermission === 'function') {
    D.requestPermission().then(function (r) {
      if (r === 'granted') { G.view.btn.style.display = 'none'; start(true); }
      else status('Compass not allowed. Close and reopen the app, then tap the button again and choose Allow. If iOS does not ask again: Settings > Apps > Safari > Advanced > Website Data, delete streamlit.app, and try again.', 'px-ol-warn');
    }).catch(function () { status('The compass could not be started on this device.', 'px-ol-warn'); });
  } else { G.view.btn.style.display = 'none'; start(true); }
}

export default function (component) {
  const { data, parentElement } = component;
  let V = parentElement.__skypaschalionOrient;
  const key = (data && data.html) || '';
  if (!V || V.key !== key) {
    parentElement.innerHTML = key;
    V = { key: key,
          stage: parentElement.querySelector('.px-ol-stage'),
          dial: parentElement.querySelector('.px-ol-dial'),
          arrow: parentElement.querySelector('.px-ol-arrow'),
          status: parentElement.querySelector('.px-ol-status'),
          btn: parentElement.querySelector('.px-ol-btn'),
          tab: parentElement.querySelector('.px-ol-tab') };
    parentElement.__skypaschalionOrient = V;
    if (V.btn) V.btn.addEventListener('click', askAndStart);
    if (V.tab) V.tab.href = window.location.href;
  }
  V.bearing = Number(data && data.bearing) || 0;
  V.decl = Number(data && data.decl) || 0;
  V.target = (data && data.target) || 'east';
  G.view = V; G.shown = null;
  if (G.heading === null) {            // not turning yet: the static drawing (north up)
    V.dial.style.transform = 'rotate(0deg)';
    V.arrow.style.transform = 'rotate(' + V.bearing.toFixed(2) + 'deg)';
  }
  const D = window.DeviceOrientationEvent;
  const touch = window.matchMedia && window.matchMedia('(pointer: coarse)').matches;
  if (G.got) { if (V.btn) V.btn.style.display = 'none'; if (!G.loop) { G.loop = true; requestAnimationFrame(frame); } return; }
  if (!D) { status('This browser has no compass. The dial shows the direction with north at the top.', ''); if (V.btn) V.btn.style.display = 'none'; return; }
  if (typeof D.requestPermission === 'function') {          // iPhone / iPad (and Safari on Mac)
    if (touch) { V.btn.style.display = 'inline-block'; status('Tap the button, allow Motion & Orientation, and hold the phone flat.', ''); }
    else { V.btn.style.display = 'none'; status('On a phone or tablet the arrow turns with the device, like a compass.', ''); }
  } else if (touch) {                                       // Android: no permission needed
    if (V.btn) V.btn.style.display = 'none';
    start(false);
  } else {
    if (V.btn) V.btn.style.display = 'none';
    status('On a phone or tablet the arrow turns with the device, like a compass.', '');
  }
}
"""

_COMPONENT = st.components.v2.component("skypaschalion_orient", js=JS, css=CSS, isolate_styles=False)

_WRAP = "position:relative;padding-top:14px;flex:0 0 auto;"
_LUBBER = ("position:absolute;top:0;left:50%;transform:translateX(-50%);width:0;height:0;"
           "border-left:9px solid transparent;border-right:9px solid transparent;border-top:13px solid #e6b8dc;")
_STAGE = "position:relative;border-radius:50%;"
_LAYER = "position:absolute;top:0;left:0;width:100%;height:100%;transform-origin:50% 50%;line-height:0;"
_CARD = ("background:#13204a;border:1px solid #a8792a;border-radius:6px;padding:.8rem 1rem;margin:.3rem 0 .6rem 0;"
         "color:#f6eedb;")
_ROW = "display:flex;flex-wrap:wrap;align-items:center;gap:.6rem 1.2rem;"
_INFO = "flex:1 1 13rem;min-width:12rem;"
_DEG = "font-size:1.7rem;font-weight:700;color:#e8c25c;line-height:1.1;"
_TXT = "color:#dad1ba;font-size:.9rem;margin-top:.2rem;"
_BTN = ("display:none;margin-top:.55rem;background:#2a4d9b;color:#ffffff;border:1px solid #e8c25c;border-radius:6px;"
        "padding:.45rem .9rem;font-weight:700;font-size:.95rem;min-height:44px;cursor:pointer;")
_STATUS = "margin-top:.45rem;color:#f6eedb;font-size:.95rem;font-weight:600;min-height:1.3em;"
_TAB = "display:none;margin-top:.4rem;color:#a6d5f2;font-size:.92rem;"
_H3 = "color:#e8c25c;margin:0 0 .4rem 0;font-size:1.08rem;font-weight:700;"

GOLD, GOLD_DEEP, CARD, NIGHT, CREAM, PORPH = "#e8c25c", "#a8792a", "#13204a", "#0a1433", "#f6eedb", "#e6b8dc"


def _svg(body: str, size: int, extra: str = "") -> str:
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}' viewBox='0 0 160 160'"
            f"{extra}>{body}</svg>")


def dial_svg(size: int = 170) -> str:
    """Compass card: N, E, S, W, ticks every 15 degrees; E marked with a small cross (ad orientem)."""
    c, R = 80, 74
    out = [f"<circle cx='{c}' cy='{c}' r='{R}' fill='{CARD}' stroke='{GOLD}' stroke-width='2.2'/>",
           f"<circle cx='{c}' cy='{c}' r='{R - 5}' fill='none' stroke='{GOLD}' stroke-width='0.8' stroke-opacity='0.6'/>"]
    for deg in range(0, 360, 15):
        L = 9 if deg % 90 == 0 else (6 if deg % 45 == 0 else 3.5)
        a = math.radians(deg - 90)
        x1, y1 = c + (R - 5) * math.cos(a), c + (R - 5) * math.sin(a)
        x2, y2 = c + (R - 5 - L) * math.cos(a), c + (R - 5 - L) * math.sin(a)
        out.append(f"<line x1='{x1:.2f}' y1='{y1:.2f}' x2='{x2:.2f}' y2='{y2:.2f}' stroke='{GOLD}' "
                   f"stroke-width='{1.6 if L > 5 else 1}'/>")
    for lab, deg in (("N", 0), ("E", 90), ("S", 180), ("W", 270)):
        a = math.radians(deg - 90)
        x, y = c + 52 * math.cos(a), c + 52 * math.sin(a) + 5
        col = GOLD if lab in ("N", "E") else CREAM
        out.append(f"<text x='{x:.1f}' y='{y:.1f}' text-anchor='middle' font-family='Segoe UI, Helvetica, Arial, "
                   f"sans-serif' font-size='14' font-weight='700' fill='{col}'>{lab}</text>")
    # a small Greek cross beside the E (east)
    out.append(f"<g fill='{GOLD}'><rect x='{c + 34}' y='{c - 21}' width='3' height='9'/>"
               f"<rect x='{c + 31}' y='{c - 18}' width='9' height='3'/></g>")
    return _svg("".join(out), size, " role='presentation'")


def arrow_svg(size: int = 170) -> str:
    """A gold arrow pointing to the top of the drawing, with a small cross at its tip; same 160 x 160 frame."""
    c = 80
    cross = (f"<rect x='{c - 2.6}' y='6' width='5.2' height='18' fill='{GOLD}' stroke='{NIGHT}' stroke-width='1'/>"
             f"<rect x='{c - 8}' y='11' width='16' height='5.2' fill='{GOLD}' stroke='{NIGHT}' stroke-width='1'/>")
    arrow = (f"<polygon points='{c},27 {c - 13},52 {c - 5},50 {c - 5},{c + 30} {c + 5},{c + 30} {c + 5},50 {c + 13},52' "
             f"fill='{GOLD}' stroke='{NIGHT}' stroke-width='1.4' stroke-linejoin='round'/>"
             f"<polygon points='{c},27 {c},{c + 30} {c + 5},{c + 30} {c + 5},50 {c + 13},52' fill='{GOLD_DEEP}' opacity='0.55'/>")
    hub = f"<circle cx='{c}' cy='{c}' r='6' fill='{NIGHT}' stroke='{GOLD}' stroke-width='2'/>"
    return _svg(cross + arrow + hub, size, " role='presentation'")


def _html(bearing: float, target: str, place: str, distance_km: float | None, decl: float | None, size: int,
          title_html: str) -> str:
    b = float(bearing) % 360.0
    pts = ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"]
    word = pts[int((b + 22.5) // 45) % 8]
    name, expl = TARGETS.get(target, TARGETS["east"])
    where = f" from {html.escape(place)}" if place else ""
    dist = (f"<div class='px-orient-text' style='{_TXT}'>Jerusalem is {distance_km:,.0f} km away (great-circle).</div>"
            if (distance_km and target == "jerusalem") else "")
    if decl is None:
        dec = (f"<div class='px-orient-text' style='{_TXT}'>A magnetic compass differs from true north by the local "
               "declination (not available here, so the live arrow is not corrected for it).</div>")
    else:
        side = "east" if decl >= 0 else "west"
        dec = (f"<div class='px-orient-text' style='{_TXT}'>Magnetic north here is {abs(decl):.1f}° {side} of true north "
               f"(World Magnetic Model 2025); the live arrow allows for it, so it points along the true bearing.</div>")
    return (f"<div class='px-card px-ol-card' style='{_CARD}'><h3 style='{_H3}'>{title_html}</h3>"
            f"<div class='px-ol' style='{_ROW}'>"
            f"<div class='px-ol-wrap' style='{_WRAP}'>"
            f"<div class='px-ol-lubber' title='The top of your phone' style='{_LUBBER}'></div>"
            f"<div class='px-ol-stage' style='{_STAGE}width:{size}px;height:{size}px'>"
            f"<div class='px-ol-dial' style='{_LAYER}'>{dial_svg(size)}</div>"
            f"<div class='px-ol-arrow' style='{_LAYER}transform:rotate({b:.2f}deg)'>{arrow_svg(size)}</div></div></div>"
            f"<div class='px-ol-info' style='{_INFO}'>"
            f"<div class='px-orient-deg' style='{_DEG}'>{b:.1f}°</div>"
            f"<div class='px-orient-text' style='{_TXT}'>{html.escape(name)}{where}: {b:.1f}° from true north, "
            f"toward the {word}. {html.escape(expl)}</div>{dist}{dec}"
            f"<button type='button' class='px-ol-btn' style='{_BTN}'>Turn on the live compass</button>"
            f"<div class='px-ol-status' aria-live='polite' style='{_STATUS}'></div>"
            f"<a class='px-ol-tab' target='_blank' rel='noopener' style='{_TAB}'>Open the app in its own tab for the compass</a>"
            f"</div></div></div>")


def show(bearing: float, target: str, place: str, distance_km: float | None, lat: float, lon: float,
         title_html: str, size: int = 170, key: str = "orient_live"):
    decl = declination(lat, lon)
    markup = _html(bearing, target, place, distance_km, decl, size, title_html)
    return _COMPONENT(data={"html": markup, "bearing": float(bearing) % 360.0, "decl": decl or 0.0,
                            "target": TARGET_WORD.get(target, "east")},
                      key=key, width="stretch", height="content")
