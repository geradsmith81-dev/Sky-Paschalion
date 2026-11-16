"""Check the live compass JavaScript (orient_live.JS) and the locator JS with QuickJS (pip install quickjs).

The module's `export default function` is turned into a plain function and driven with mock browser objects
(window, screen, DeviceOrientationEvent, elements). Checks: syntax of both scripts; the rotation maths
(dial = -heading, arrow = bearing - heading, true heading = magnetic + declination); Android
(deviceorientationabsolute, heading = 360 - alpha + screen angle); iOS (webkitCompassHeading after the tap,
plus screen angle); 'facing' within 5 degrees only when the phone is flat; the status texts.
Run from the app folder:  python tools/js_check.py
"""
import ast
import json
import os
import re
import sys

import quickjs

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def js_of(fname):
    src = open(os.path.join(HERE, fname), encoding="utf-8").read()
    t = ast.parse(src)
    for n in t.body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "JS":
            return n.value.value
    raise SystemExit(f"no JS in {fname}")


MOCK = r"""
var __log = [];
function El(cls) { this.cls = cls; this.style = {}; this.textContent = ''; this.className = cls; this.isConnected = true;
  this.handlers = {}; this.on = {};
  this.classList = { toggle: (c, v) => { this.on[c] = !!v; } };
  this.addEventListener = (ev, f) => { this.handlers[ev] = f; }; }
var H = {};
var window = { addEventListener: function (ev, f) { (H[ev] = H[ev] || []).push(f); }, self: 1, top: 1,
               matchMedia: function () { return { matches: true }; }, location: { href: 'x' } };
var screen = { orientation: { angle: 0 } };
var navigator = { vibrate: function () { __log.push('vibrate'); } };
var RAF = [];
function requestAnimationFrame(f) { RAF.push(f); }
function setTimeout(f, ms) { }
window.requestAnimationFrame = requestAnimationFrame;
function makeParent() {
  var els = { '.px-ol-stage': new El('px-ol-stage'), '.px-ol-dial': new El('px-ol-dial'), '.px-ol-arrow': new El('px-ol-arrow'),
              '.px-ol-status': new El('px-ol-status'), '.px-ol-btn': new El('px-ol-btn'), '.px-ol-tab': new El('px-ol-tab') };
  return { els: els, innerHTML: '', querySelector: function (s) { return els[s]; } };
}
function tick() { var f = RAF.shift(); if (f) f(); }
function rot(el) { var m = /rotate\((-?[0-9.]+)deg\)/.exec(el.style.transform || ''); return m ? parseFloat(m[1]) : null; }
"""


def run_case(js, setup, data, events, frames=1):
    """setup: JS defining DeviceOrientationEvent etc.; events: list of (event name, JS object literal)."""
    ctx = quickjs.Context()
    body = js.replace("export default function", "var __main = function")
    ctx.eval(MOCK + setup + "\n" + body)
    ctx.eval(f"var P = makeParent(); __main({{ data: {json.dumps(data)}, parentElement: P }});")
    for ev, obj in events:
        if ev == "click":
            ctx.eval("P.els['.px-ol-btn'].handlers['click']();")
            continue
        ctx.eval(f"(H['{ev}'] || []).forEach(function (f) {{ f({obj}); }});")
    for _ in range(frames):
        ctx.eval("tick();")
    res = ctx.eval("JSON.stringify({dial: rot(P.els['.px-ol-dial']), arrow: rot(P.els['.px-ol-arrow']),"
                   " status: P.els['.px-ol-status'].textContent, on: !!P.els['.px-ol-stage'].on['px-ol-on'],"
                   " btn: P.els['.px-ol-btn'].style.display || ''})")
    return json.loads(res)


ANDROID = "window.ondeviceorientationabsolute = null; var DeviceOrientationEvent = function () {}; window.DeviceOrientationEvent = DeviceOrientationEvent;"
IOS = ("var DeviceOrientationEvent = function () {}; DeviceOrientationEvent.requestPermission = function () {"
       " return { then: function (f) { f('granted'); return { catch: function () {} }; } }; };"
       " window.DeviceOrientationEvent = DeviceOrientationEvent;")


def norm180(a):
    return ((a % 360) + 540) % 360 - 180


def main():
    js = js_of("orient_live.py")
    loc = js_of("locator.py")
    checks, fails = 0, []

    def ok(cond, msg):
        nonlocal checks
        checks += 1
        if not cond:
            fails.append(msg)

    # syntax of both modules
    for name, src in (("orient_live", js), ("locator", loc)):
        try:
            c = quickjs.Context()
            c.eval(MOCK + "var DeviceOrientationEvent = function(){};\n" + src.replace("export default function", "var __m = function"))
            ok(True, name)
        except Exception as ex:
            ok(False, f"{name} syntax: {ex}")

    # static drawing (no compass yet): dial 0, arrow = bearing
    r = run_case(js, ANDROID.replace("window.ondeviceorientationabsolute = null;", ""), {"html": "x", "bearing": 113.6, "decl": 0, "target": "Jerusalem"}, [], 0)
    ok(abs(r["dial"]) < 1e-9 and abs(r["arrow"] - 113.6) < 0.01, f"static drawing {r}")

    # Android: heading = 360 - alpha + screen angle; true = + decl
    for alpha, angle, decl, bearing in [(270, 0, 0, 90), (300, 0, 2.5, 90), (10, 90, -4.0, 113.6), (180, 270, 0, 45)]:
        setup = ANDROID + f" screen.orientation.angle = {angle};"
        r = run_case(js, setup, {"html": "x", "bearing": bearing, "decl": decl, "target": "east"},
                     [("deviceorientationabsolute", f"{{alpha: {alpha}, beta: 2, gamma: -3}}")])
        h = (360 - alpha) + angle + decl
        ok(abs(norm180(r["dial"] + h)) < 0.01, f"android dial alpha={alpha} angle={angle}: {r['dial']} vs {-h}")
        ok(abs(norm180(r["arrow"] - (bearing - h))) < 0.01, f"android arrow alpha={alpha}: {r['arrow']} vs {bearing - h}")
        facing = abs(norm180(bearing - h)) <= 5
        ok(r["on"] == facing, f"android facing flag alpha={alpha}: {r['on']} vs {facing}")
        ok(("You are facing east." in r["status"]) == facing, f"android status alpha={alpha}: {r['status']}")
    # iOS: needs the tap; webkitCompassHeading + screen angle
    r0 = run_case(js, IOS, {"html": "x", "bearing": 90, "decl": 0, "target": "east"}, [], 0)
    ok(r0["btn"] == "inline-block", f"iOS shows the button before the tap: {r0}")
    for wch, angle, decl, bearing in [(90, 0, 0, 90), (45, 0, 1.2, 90), (350, 90, 0, 113.6)]:
        setup = IOS + f" screen.orientation.angle = {angle};"
        r = run_case(js, setup, {"html": "x", "bearing": bearing, "decl": decl, "target": "Jerusalem"},
                     [("click", None), ("deviceorientation", f"{{webkitCompassHeading: {wch}, webkitCompassAccuracy: 10, beta: 5, gamma: 5}}")])
        h = wch + angle + decl
        ok(abs(norm180(r["dial"] + h)) < 0.01, f"iOS dial wch={wch}: {r['dial']} vs {-h}")
        ok(abs(norm180(r["arrow"] - (bearing - h))) < 0.01, f"iOS arrow wch={wch}: {r['arrow']} vs {bearing - h}")
        ok(r["btn"] == "none", f"iOS hides the button after the tap: {r['btn']}")
        if abs(norm180(bearing - h)) <= 5:
            ok("You are facing Jerusalem." in r["status"], f"iOS facing status: {r['status']}")
        else:
            side = "right" if norm180(bearing - h) > 0 else "left"
            ok(f"to the {side} to face Jerusalem" in r["status"], f"iOS turn status: {r['status']}")
    # not flat: no 'facing', asks to hold flat
    r = run_case(js, ANDROID, {"html": "x", "bearing": 90, "decl": 0, "target": "east"},
                 [("deviceorientationabsolute", "{alpha: 270, beta: 70, gamma: 0}")])
    ok(not r["on"] and "Hold the phone flat" in r["status"], f"upright phone: {r}")
    print(f"JS CHECK: {checks - len(fails)}/{checks} passed")
    for f in fails:
        print("FAIL", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
