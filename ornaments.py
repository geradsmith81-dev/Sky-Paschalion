"""Decorative SVG for Sky Paschalion, after late-antique mosaics (Ravenna, 5th-6th centuries).

* Chi-Rho (the Christogram, chi + rho) between alpha and omega: gold tesserae on a deep blue tessellated
  ground, inside a gold ring and an optional laurel wreath. Late-antique monograms of this kind appear on
  Ravenna sarcophagi and mosaics; the gold-on-night-blue ground follows the vault of the Mausoleum of
  Galla Placidia (c. 425-450) and the starry medallion of the apse of Sant'Apollinare in Classe (549).
  The omega is drawn by default as the uncial (lower-case-like) form usual in late-antique inscriptions
  and mosaics; pass omega='capital' for the capital form.
* cross_svg(style, size): the cross forms used by the traditions in sects.py:
  latin | greek | coptic | ethiopian | armenian | syriac | russian.
  (Russian three-bar cross: the lower, slanted bar rises on the viewer's left, i.e. Christ's right.)
  These are simplified, generic emblems drawn for the app, not copies of any particular object.
* Mosaic borders and dividers: a jewelled band (pearls and gems on gold, as on the borders of the
  Ravenna mosaics) and a meander band, as repeatable tiles (CSS background) and as full dividers.

Everything is plain SVG text. It renders in browsers and in resvg (resvg-py), which makes the PNG icons.
All drawings use a fixed viewBox and only scale with `size`, so they stay crisp at any size.

Technique: each letter stroke is drawn as (1) a dark outline, (2) a darker-gold 'grout' stroke and
(3) two or three parallel rows of dashed gold strokes, the dashes being the tesserae and the dash gaps the
grout lines. A second and third dashed layer in other golds recolour every few tesserae, so the gold
varies as real glass tesserae do, with only a handful of SVG elements per stroke. Below 96 px the
tesserae are left out (they would blur) and the letters are drawn as solid gold strokes.
"""
from __future__ import annotations

import base64
import math
import random

# Palette (the same hex values as theme.py; kept here so this module has no imports from the app).
NIGHT = "#0a1433"        # deep mosaic lapis, the ground
NIGHT_2 = "#0f1c45"
NIGHT_3 = "#132457"
NIGHT_4 = "#0c173b"
NIGHT_5 = "#182c66"
GROUT_BLUE = "#060c22"
GOLD = "#e8c25c"         # gold tesserae
GOLD_LIGHT = "#f5dc8e"
GOLD_MID = "#d9ab45"
GOLD_DEEP = "#a8792a"    # gold in shade
GROUT_GOLD = "#6e4f1c"
OUTLINE = "#05091a"
PORPHYRY = "#7a2f6b"     # imperial purple stone
PORPHYRY_DEEP = "#5e2152"
PEARL = "#f3eee2"
EMERALD = "#2f7a4f"
LAUREL = "#3d8a55"
LAUREL_DARK = "#24603a"
CREAM = "#f6eedb"

CROSS_STYLES = ("latin", "greek", "coptic", "ethiopian", "armenian", "syriac", "russian")


# ---------------------------------------------------------------- helpers
def _svg(w, h, body, vw=None, vh=None, extra=""):
    vw = w if vw is None else vw
    vh = h if vh is None else vh
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {vw} {vh}'"
            f"{extra}>{body}</svg>")


def _f(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def _poly(points):
    return " ".join(f"{_f(x)},{_f(y)}" for x, y in points)


def _offset(points, d):
    """The polyline moved sideways by d (left of the direction of travel is negative)."""
    out = []
    n = len(points)
    for i, (x, y) in enumerate(points):
        if i == 0:
            dx, dy = points[1][0] - x, points[1][1] - y
        elif i == n - 1:
            dx, dy = x - points[i - 1][0], y - points[i - 1][1]
        else:
            dx, dy = points[i + 1][0] - points[i - 1][0], points[i + 1][1] - points[i - 1][1]
        L = math.hypot(dx, dy) or 1.0
        out.append((x - dy / L * d, y + dx / L * d))
    return out


def _arc(cx, cy, r, a0, a1, n=24):
    """Points on a circle from angle a0 to a1 (degrees, 0 = +x, clockwise on screen)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _bezier(p0, p1, p2, p3, n=16):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        pts.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return pts


def _tess_stroke(points, width, tess=True, rows=None, seed=0):
    """One letter stroke: outline, grout and rows of gold tesserae (or solid gold if tess=False)."""
    p = _poly(points)
    out = [f"<polyline points='{p}' fill='none' stroke='{OUTLINE}' stroke-width='{_f(width + 5)}' "
           f"stroke-linejoin='round' stroke-linecap='square'/>"]
    if not tess:
        out.append(f"<polyline points='{p}' fill='none' stroke='{GOLD}' stroke-width='{_f(width)}' "
                   f"stroke-linejoin='round' stroke-linecap='square'/>")
        return "".join(out)
    out.append(f"<polyline points='{p}' fill='none' stroke='{GROUT_GOLD}' stroke-width='{_f(width)}' "
               f"stroke-linejoin='round' stroke-linecap='square'/>")
    rows = rows or max(2, round(width / 9.5))
    rw = width / rows
    tile = rw * 0.86            # tessera length along the stroke
    gap = rw * 0.16             # grout line
    rnd = random.Random(seed)
    for j in range(rows):
        off = (j - (rows - 1) / 2) * rw
        q = _poly(_offset(points, off)) if abs(off) > 1e-6 else p
        sw = _f(rw - gap)
        phase = _f(rnd.uniform(0, tile + gap))     # rows are staggered like courses of tesserae
        out.append(f"<polyline points='{q}' fill='none' stroke='{GOLD}' stroke-width='{sw}' "
                   f"stroke-dasharray='{_f(tile)} {_f(gap)}' stroke-dashoffset='{phase}' stroke-linejoin='round'/>")
        # recolour every 3rd and every 5th tessera (light and deep gold)
        per = tile + gap
        out.append(f"<polyline points='{q}' fill='none' stroke='{GOLD_LIGHT}' stroke-width='{sw}' "
                   f"stroke-dasharray='{_f(tile)} {_f(per * 3 - tile)}' stroke-dashoffset='{phase}' "
                   f"stroke-linejoin='round'/>")
        out.append(f"<polyline points='{q}' fill='none' stroke='{GOLD_MID}' stroke-width='{sw}' "
                   f"stroke-dasharray='{_f(tile)} {_f(per * 5 - tile)}' "
                   f"stroke-dashoffset='{_f(float(phase) + per * 2)}' stroke-linejoin='round'/>")
    return "".join(out)


def _ground_pattern(pid, s=13.0, seed=7):
    """A <pattern> of blue glass tesserae laid in staggered courses (6 x 6 tesserae, repeats seamlessly)."""
    rnd = random.Random(seed)
    blues = [NIGHT, NIGHT_2, NIGHT_3, NIGHT_4, NIGHT, NIGHT_2, NIGHT_5]
    n = 6
    W = n * s
    rects = []
    for r in range(n):
        shift = (s / 2) if r % 2 else 0.0
        for c in range(n + 1):
            x = c * s - shift
            col = rnd.choice(blues)
            g = s * 0.12
            rects.append(f"<rect x='{_f(x + g / 2)}' y='{_f(r * s + g / 2)}' width='{_f(s - g)}' "
                         f"height='{_f(s - g)}' rx='{_f(s * 0.12)}' fill='{col}'/>")
    return (f"<pattern id='{pid}' patternUnits='userSpaceOnUse' width='{_f(W)}' height='{_f(W)}'>"
            f"<rect width='{_f(W)}' height='{_f(W)}' fill='{GROUT_BLUE}'/>{''.join(rects)}</pattern>")


def _star(cx, cy, r, color=GOLD_LIGHT, core=PEARL):
    """A small eight-rayed mosaic star (as on the Galla Placidia vault)."""
    pts = []
    for k in range(16):
        rr = r if k % 2 == 0 else r * 0.38
        a = math.radians(k * 22.5 - 90)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return (f"<polygon points='{_poly(pts)}' fill='{color}'/>"
            f"<circle cx='{_f(cx)}' cy='{_f(cy)}' r='{_f(r * 0.22)}' fill='{core}'/>")


# ---------------------------------------------------------------- the Chi-Rho monogram
# All geometry on a 512 x 512 canvas, centre (256, 256).
C = 256.0


def _chi_rho_strokes(omega="uncial", scale=1.0, letters=True, small=False):
    """[(points, width, rows)] for chi, rho, alpha, omega (and serifs)."""
    W = 30.0 if not small else (54.0 if not letters else 44.0)   # main stroke width
    if small and not letters:
        arm, top, bot = 132.0, 66.0, 446.0
    elif small:
        arm, top, bot = 112.0, 92.0, 418.0
    else:
        arm, top, bot = 104.0, 96.0, 410.0
    strokes = []
    # chi: two diagonals
    strokes.append(([(C - arm, C - arm), (C + arm, C + arm)], W, 3))
    strokes.append(([(C + arm, C - arm), (C - arm, C + arm)], W, 3))
    # rho: stem and bowl (the bowl opens to the right, as P)
    bw = 54.0 if not small else (78.0 if not letters else 62.0)
    by = top + (100.0 if not small else (128.0 if not letters else 108.0))
    strokes.append(([(C, bot), (C, top)], W, 3))
    r = (by - top) / 2
    bowl = [(C, top), (C + bw - r, top)] + _arc(C + bw - r, top + r, r, -90, 90, 20) + [(C + bw - r, by), (C, by)]
    strokes.append((bowl, W * 0.9, 3))
    if not small:
        # serifs at the free ends (short bars across the stroke, as on monumental letters)
        s = 21.0
        strokes.append(([(C - s, bot), (C + s, bot)], 13.0, 1))
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            ex, ey = C + sx * arm, C + sy * arm
            k = s / math.sqrt(2)
            strokes.append(([(ex - sx * k, ey + sy * k), (ex + sx * k, ey - sy * k)], 13.0, 1))
    if letters:
        aw = 17.0 if not small else 30.0
        # alpha and omega stand in the side spaces between the arms of the chi
        if small:
            ax, ay, ah, hw = 86.0, 262.0, 124.0, 42.0
        else:
            ax, ay, ah, hw = 116.0, 262.0, 94.0, 30.0
        # Alpha with the broken (V-shaped) cross-bar of late-antique inscriptions
        strokes.append(([(ax - hw, ay + ah / 2), (ax, ay - ah / 2), (ax + hw, ay + ah / 2)], aw, 2))
        if not small:
            strokes.append(([(ax - hw * 0.52, ay + ah * 0.12), (ax, ay + ah * 0.26), (ax + hw * 0.52, ay + ah * 0.12)],
                            aw * 0.75, 1))
        else:
            strokes.append(([(ax - hw * 0.45, ay + ah * 0.16), (ax + hw * 0.45, ay + ah * 0.16)], aw * 0.75, 1))
        ox = 2 * C - ax
        oy = ay
        if omega == "capital":
            R = ah * 0.42
            ring = _arc(ox, oy - ah * 0.06, R, 128, 412, 30)
            strokes.append((ring, aw, 2))
            strokes.append(([(ox - R * 1.05, oy + ah / 2 - 2), (ox - R * 0.42, oy + ah / 2 - 2)], aw * 0.8, 1))
            strokes.append(([(ox + R * 0.42, oy + ah / 2 - 2), (ox + R * 1.05, oy + ah / 2 - 2)], aw * 0.8, 1))
        else:
            # uncial omega: two round bowls joined in the middle
            ww = hw * 1.18
            t, b = oy - ah * 0.30, oy + ah / 2 - aw / 2
            left = _bezier((ox - ww, t), (ox - ww * 1.12, b + 4), (ox - ww * 0.1, b + 8), (ox, oy + ah * 0.02), 14)
            right = _bezier((ox, oy + ah * 0.02), (ox + ww * 0.1, b + 8), (ox + ww * 1.12, b + 4), (ox + ww, t), 14)
            strokes.append((left + right[1:], aw, 2))
    return strokes


def _laurel(R=222.0, n=15, seed=3):
    """A laurel wreath: two branches rising from a tie at the bottom and meeting at the top."""
    rnd = random.Random(seed)
    out = []
    for side in (-1, 1):
        stem = []
        for i in range(n + 1):
            a = 90 + side * (14 + (180 - 30) * i / n)       # from the bottom tie round to the top
            stem.append((C + R * math.cos(math.radians(a)), C + R * math.sin(math.radians(a))))
        out.append(f"<polyline points='{_poly(stem)}' fill='none' stroke='{LAUREL_DARK}' stroke-width='4'/>")
        for i in range(1, n + 1):
            a = 90 + side * (14 + (180 - 30) * (i - 0.5) / n)
            ar = math.radians(a)
            tang = a + side * 90 + 180     # pointing along the branch toward the top
            for k, (dr, tilt) in enumerate(((-11, -30), (11, 30))):
                x = C + (R + dr) * math.cos(ar)
                y = C + (R + dr) * math.sin(ar)
                ang = tang + side * tilt * (-1 if k == 0 else 1)
                col = LAUREL if (i + k) % 2 else EMERALD
                out.append(f"<ellipse cx='{_f(x)}' cy='{_f(y)}' rx='16' ry='6.4' fill='{col}' stroke='{OUTLINE}' "
                           f"stroke-width='1.4' transform='rotate({_f(ang)} {_f(x)} {_f(y)})'/>")
                out.append(f"<line x1='{_f(x - 11 * math.cos(math.radians(ang)))}' y1='{_f(y - 11 * math.sin(math.radians(ang)))}' "
                           f"x2='{_f(x + 11 * math.cos(math.radians(ang)))}' y2='{_f(y + 11 * math.sin(math.radians(ang)))}' "
                           f"stroke='{GOLD_MID}' stroke-width='1.3' opacity='.85'/>")
            if i % 3 == 1:
                bx = C + (R + rnd.choice((-2, 2))) * math.cos(ar + side * 0.06)
                by = C + (R + rnd.choice((-2, 2))) * math.sin(ar + side * 0.06)
                out.append(f"<circle cx='{_f(bx)}' cy='{_f(by)}' r='4.2' fill='{GOLD_LIGHT}' stroke='{OUTLINE}' stroke-width='1'/>")
    # the ribbon that ties the two branches at the bottom
    out.append(f"<path d='M{_f(C - 14)},{_f(C + R + 2)} l-18,22 l10,2 l8,-10 M{_f(C + 14)},{_f(C + R + 2)} l18,22 l-10,2 l-8,-10' "
               f"fill='{PORPHYRY}' stroke='{OUTLINE}' stroke-width='1.5'/>")
    out.append(f"<circle cx='{_f(C)}' cy='{_f(C + R + 2)}' r='9' fill='{PORPHYRY}' stroke='{GOLD}' stroke-width='2'/>")
    return "".join(out)


def _ring(R, width, tess=True):
    pts = _arc(C, C, R, 0, 360, 72)
    return _tess_stroke(pts, width, tess=tess, rows=2 if width > 12 else 1, seed=11)


def chi_rho_svg(size: int = 64, wreath: bool | None = None, ground: bool = True, alpha_omega: bool = True,
                omega: str = "uncial", detail: str = "auto", maskable: bool = False, rounded: bool = False,
                uid: str = "px") -> str:
    """The emblem: a Chi-Rho between alpha and omega in gold tesserae on deep blue.

    size: pixel width = height of the <svg>. detail: 'full' (tesserae, wreath, stars), 'medium'
    (tesserae on the letters, plain ring, no wreath), 'simple' (solid gold letters, for <= 48 px),
    or 'auto' (full >= 160 px, medium >= 96 px, simple below). wreath: None = as the detail level decides.
    ground=False leaves the background transparent (for inline use on the app's own blue).
    maskable=True shrinks the art into the central 80 % safe circle for Android maskable icons.
    uid: prefix for the SVG ids (give each inline copy on one page its own uid).
    """
    if detail == "auto":
        detail = "full" if size >= 160 else ("medium" if size >= 96 else "simple")
    tess = detail in ("full", "medium")
    small = detail == "simple"
    if wreath is None:
        wreath = detail == "full"
    pid = f"{uid}-tess"
    defs = []
    body = []
    if ground:
        if detail == "simple":
            defs.append(f"<radialGradient id='{uid}-g' cx='50%' cy='42%' r='70%'><stop offset='0' stop-color='{NIGHT_5}'/>"
                        f"<stop offset='1' stop-color='{NIGHT}'/></radialGradient>")
            fill = f"url(#{uid}-g)"
        else:
            defs.append(_ground_pattern(pid))
            fill = f"url(#{pid})"
        rx = " rx='92'" if rounded else ""
        body.append(f"<rect width='512' height='512'{rx} fill='{fill}'/>")
        if detail == "full":
            # a lighter blue glow behind the monogram, and stars in the corners
            defs.append(f"<radialGradient id='{uid}-glow' cx='50%' cy='50%' r='50%'><stop offset='0' stop-color='#2a4d9b' "
                        f"stop-opacity='.45'/><stop offset='1' stop-color='#2a4d9b' stop-opacity='0'/></radialGradient>")
            body.append(f"<circle cx='256' cy='256' r='200' fill='url(#{uid}-glow)'/>")
            if not maskable:
                for (x, y) in ((40, 40), (472, 40), (40, 472), (472, 472), (256, 22), (22, 256), (490, 256)):
                    body.append(_star(x, y, 13))
    art = []
    if detail == "full":
        art.append(_ring(196, 9, tess=True))
        if wreath:
            art.append(_laurel())
        else:
            art.append(_ring(214, 14, tess=True))
    elif detail == "medium":
        art.append(_ring(214, 16, tess=True))
    else:
        art.append(f"<circle cx='256' cy='256' r='232' fill='none' stroke='{GOLD}' stroke-width='26'/>")
    for i, (pts, w, rows) in enumerate(_chi_rho_strokes(omega=omega, letters=alpha_omega, small=small)):
        art.append(_tess_stroke(pts, w, tess=tess, rows=rows, seed=100 + i))
    art_s = "".join(art)
    if maskable:
        art_s = f"<g transform='translate(256 256) scale(0.80) translate(-256 -256)'>{art_s}</g>"
    title = "<title>Chi-Rho between Alpha and Omega</title>"
    return _svg(size, size, title + f"<defs>{''.join(defs)}</defs>" + "".join(body) + art_s, 512, 512,
                extra=" role='img' aria-label='Chi-Rho between Alpha and Omega'")


def emblem_svg(size: int = 512) -> str:
    """The full emblem (wreath, tesserae, stars)."""
    return chi_rho_svg(size, detail="full")


def icon_svg(size: int = 512, maskable: bool = False, rounded: bool = False) -> str:
    """App icon art: full detail at >= 160 px, medium at 96-159 px, simple (solid gold) below 96 px."""
    return chi_rho_svg(size, maskable=maskable, rounded=rounded)


def icon_small_svg(size: int = 32) -> str:
    """Favicon art (16-48 px): solid gold Chi-Rho, thick strokes, no tesserae; alpha and omega from 48 px."""
    return chi_rho_svg(size, detail="simple", alpha_omega=size >= 48)


# ---------------------------------------------------------------- crosses
def _cross_body(style, fill, line):
    s = f"fill='{fill}' stroke='{line}' stroke-width='2.4' stroke-linejoin='round'"
    if style == "latin":
        return f"<path {s} d='M44,8 H56 V28 H78 V40 H56 V92 H44 V40 H22 V28 H44 Z'/>"
    if style == "greek":
        return f"<path {s} d='M43,12 H57 V43 H88 V57 H57 V88 H43 V57 H12 V43 H43 Z'/>"
    if style == "coptic":
        # equal arms, each ending in three points (for the Trinity), on a ring
        parts = [f"<circle cx='50' cy='50' r='27' fill='none' stroke='{line}' stroke-width='9'/>",
                 f"<circle cx='50' cy='50' r='27' fill='none' stroke='{fill}' stroke-width='5'/>"]
        arm = "M44,50 V24 L37,19 L40,13 L45,15 L50,6 L55,15 L60,13 L63,19 L56,24 V50 Z"
        for a in (0, 90, 180, 270):
            parts.append(f"<path {s} d='{arm}' transform='rotate({a} 50 50)'/>")
        parts.append(f"<rect x='42' y='42' width='16' height='16' fill='{fill}'/>")
        return "".join(parts)
    if style == "ethiopian":
        # openwork processional cross: a lattice lozenge with looped arms ending in crosslets
        st = f"fill='none' stroke='{fill}' stroke-width='3.6' stroke-linejoin='round' stroke-linecap='round'"
        so = f"fill='none' stroke='{line}' stroke-width='6.4' stroke-linejoin='round' stroke-linecap='round'"
        d = ("M50,14 L64,30 L86,36 L70,50 L86,64 L64,70 L50,86 L36,70 L14,64 L30,50 L14,36 L36,30 Z "
             "M50,26 L60,40 L74,50 L60,60 L50,74 L40,60 L26,50 L40,40 Z "
             "M50,26 V74 M26,50 H74 M40,40 L60,60 M60,40 L40,60")
        tips = ""
        for (x, y) in ((50, 8), (92, 50), (50, 92), (8, 50)):
            tips += f"M{x - 4},{y} H{x + 4} M{x},{y - 4} V{y + 4} "
        return (f"<path {so} d='{d} {tips}'/><path {st} d='{d} {tips}'/>"
                f"<circle cx='50' cy='50' r='4.5' fill='{fill}' stroke='{line}' stroke-width='1.6'/>")
    if style == "armenian":
        # flared arms whose ends split into two curling volutes (as on khachkars)
        parts = []
        arm = "M45,50 V26 L41,20 C30,22 30,8 40,9 C46,10 46,16 42,17 L50,13 L58,17 C54,16 54,10 60,9 C70,8 70,22 59,20 L55,26 V50 Z"
        for a in (0, 90, 180, 270):
            parts.append(f"<path {s} d='{arm}' transform='rotate({a} 50 50)'/>")
        parts.append(f"<circle cx='50' cy='50' r='7' fill='{fill}' stroke='{line}' stroke-width='2'/>")
        parts.append(f"<circle cx='50' cy='50' r='2.6' fill='{line}'/>")
        return "".join(parts)
    if style == "syriac":
        # flared (pattee) arms ending in three pearls each, as on East and West Syriac crosses
        parts = []
        arm = "M46,50 L40,16 Q50,20 60,16 L54,50 Z"
        for a in (0, 90, 180, 270):
            parts.append(f"<path {s} d='{arm}' transform='rotate({a} 50 50)'/>")
            for (x, y, r) in ((39, 12, 4.2), (50, 8.5, 4.6), (61, 12, 4.2)):
                parts.append(f"<circle cx='{x}' cy='{y}' r='{r}' fill='{fill}' stroke='{line}' stroke-width='1.8' "
                             f"transform='rotate({a} 50 50)'/>")
        parts.append(f"<circle cx='50' cy='50' r='6.5' fill='{fill}' stroke='{line}' stroke-width='2'/>")
        return "".join(parts)
    if style == "russian":
        # three bars: title board, main bar, slanted footrest raised on the viewer's left (Christ's right)
        return (f"<path {s} d='M45,4 H55 V15 H66 V23 H55 V31 H82 V41 H55 V96 H45 V41 H18 V31 H45 V23 H34 V15 H45 Z'/>"
                f"<path {s} d='M28,66 L72,79 L69.5,87 L25.5,74 Z'/>")
    raise ValueError(f"unknown cross style {style!r}; use one of {CROSS_STYLES}")


def cross_svg(style: str, size: int = 28, color: str = GOLD, line: str = OUTLINE, ground: str | None = None) -> str:
    """A cross in one of CROSS_STYLES (latin|greek|coptic|ethiopian|armenian|syriac|russian), gold on
    transparent by default; ground='#hex' adds a rounded square background."""
    style = (style or "latin").lower()
    bg = f"<rect width='100' height='100' rx='14' fill='{ground}'/>" if ground else ""
    label = f"{style.capitalize()} cross"
    return _svg(size, size, f"<title>{label}</title>{bg}{_cross_body(style, color, line)}", 100, 100,
                extra=f" role='img' aria-label='{label}'")


# ---------------------------------------------------------------- borders and dividers
def jewel_band_tile_svg(h: int = 28) -> str:
    """A repeatable tile (width = 2h) of the jewelled band: pearls and gems in gold settings between
    rows of gold tesserae. Use as a CSS background with repeat-x."""
    w = 2 * h
    k = h / 28.0
    body = [f"<rect width='{w}' height='{h}' fill='{NIGHT_2}'/>"]
    for y in (1.5 * k, h - 4.5 * k):
        for i in range(8):
            col = (GOLD, GOLD_LIGHT, GOLD_MID, GOLD)[i % 4]
            body.append(f"<rect x='{_f(i * w / 8 + 0.5)}' y='{_f(y)}' width='{_f(w / 8 - 1.2)}' height='{_f(3 * k)}' fill='{col}'/>")
    cy = h / 2
    # pearl
    body.append(f"<circle cx='{_f(w * 0.25)}' cy='{_f(cy)}' r='{_f(5.2 * k)}' fill='{PEARL}' stroke='{GOLD_DEEP}' stroke-width='{_f(1.6 * k)}'/>")
    # gem (porphyry oval in a gold setting) with two small pearls
    body.append(f"<ellipse cx='{_f(w * 0.75)}' cy='{_f(cy)}' rx='{_f(9 * k)}' ry='{_f(6.2 * k)}' fill='{GOLD}' stroke='{OUTLINE}' stroke-width='{_f(1 * k)}'/>")
    body.append(f"<ellipse cx='{_f(w * 0.75)}' cy='{_f(cy)}' rx='{_f(6.4 * k)}' ry='{_f(4 * k)}' fill='{PORPHYRY}'/>")
    for x in (0.0, w / 2, w):
        body.append(f"<circle cx='{_f(x)}' cy='{_f(cy)}' r='{_f(2.2 * k)}' fill='{GOLD_LIGHT}'/>")
    return _svg(w, h, "".join(body))


def meander_tile_svg(h: int = 28) -> str:
    """A repeatable tile of a gold meander (key pattern) band on blue, width = h."""
    w = h
    k = h / 28.0
    s = 2.6 * k
    d = (f"M0,{_f(22 * k)} H{_f(20 * k)} V{_f(6 * k)} H{_f(8 * k)} V{_f(14 * k)} H{_f(14 * k)} "
         f"M{_f(20 * k)},{_f(22 * k)} H{_f(28 * k)}")
    body = (f"<rect width='{w}' height='{h}' fill='{NIGHT_2}'/>"
            f"<rect y='0' width='{w}' height='{_f(1.6 * k)}' fill='{GOLD_DEEP}'/>"
            f"<rect y='{_f(h - 1.6 * k)}' width='{w}' height='{_f(1.6 * k)}' fill='{GOLD_DEEP}'/>"
            f"<path d='{d}' fill='none' stroke='{GOLD}' stroke-width='{_f(s)}' stroke-linecap='square'/>")
    return _svg(w, h, body)


def divider_svg(width: int = 640, h: int = 28, style: str = "jewel", center: bool = True) -> str:
    """A full-width mosaic divider: the jewelled (style='jewel') or meander (style='meander') band, with
    a small Chi-Rho medallion in the middle if center=True."""
    tile = jewel_band_tile_svg(h) if style == "jewel" else meander_tile_svg(h)
    tw = 2 * h if style == "jewel" else h
    uri = data_uri(tile)
    body = [f"<defs><pattern id='pxdiv-{style}' patternUnits='userSpaceOnUse' width='{tw}' height='{h}'>"
            f"<image href='{uri}' width='{tw}' height='{h}'/></pattern></defs>",
            f"<rect width='{width}' height='{h}' fill='url(#pxdiv-{style})'/>"]
    if center:
        m = h * 1.0
        x = width / 2 - m / 2
        inner = chi_rho_svg(int(m), detail="simple", alpha_omega=False)
        body.append(f"<rect x='{_f(x - 4)}' y='0' width='{_f(m + 8)}' height='{h}' fill='{NIGHT}'/>")
        body.append(f"<image x='{_f(x)}' y='0' width='{_f(m)}' height='{_f(m)}' href='{data_uri(inner)}'/>")
    return _svg(width, h, "".join(body))


def border_tile_svg(h: int = 28, style: str = "jewel") -> str:
    """Repeatable border tile ('jewel' or 'meander')."""
    return jewel_band_tile_svg(h) if style == "jewel" else meander_tile_svg(h)


def tessera_frame_css(color: str = GOLD) -> str:
    """CSS border-image value for a gold tesserae frame around cards (data URI)."""
    s = 12
    cells = []
    for i in range(3):
        for j in range(3):
            if i == 1 and j == 1:
                continue
            col = (GOLD, GOLD_LIGHT, GOLD_MID)[(i + 2 * j) % 3]
            cells.append(f"<rect x='{j * s + 0.6}' y='{i * s + 0.6}' width='{s - 1.2}' height='{s - 1.2}' fill='{col}'/>")
    svg = _svg(3 * s, 3 * s, f"<rect width='{3 * s}' height='{3 * s}' fill='{GROUT_GOLD}'/>" + "".join(cells))
    return f"url(\"{data_uri(svg)}\") 12 round"


def data_uri(svg: str) -> str:
    """An SVG string as a base64 data URI (for CSS backgrounds and <img src>)."""
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


# ---------------------------------------------------------------- the Moon and the orientation compass
def moon_phase_svg(illum: float, waxing: bool, size: int = 22, tilt: float = 0.0) -> str:
    """The Moon's phase: illum = illuminated fraction 0..1; waxing = lit on the right (northern-hemisphere
    view); tilt rotates the picture (degrees)."""
    k = max(0.0, min(1.0, float(illum)))
    r = 45.0
    # terminator: an ellipse of semi-axis |1 - 2k| * r
    ex = abs(1 - 2 * k) * r
    lit_right = bool(waxing)
    s1 = 1 if lit_right else 0
    # outer limb half (lit side) + terminator back
    sweep_t = (0 if k < 0.5 else 1) if lit_right else (1 if k < 0.5 else 0)
    d = (f"M50,5 A{r},{r} 0 0 {s1} 50,95 A{_f(ex)},{r} 0 0 {sweep_t} 50,5 Z")
    body = (f"<circle cx='50' cy='50' r='{r}' fill='{NIGHT_3}' stroke='{GOLD_DEEP}' stroke-width='3'/>"
            + (f"<path d='{d}' fill='{PEARL}'/>" if k > 0.005 else "")
            + f"<circle cx='50' cy='50' r='{r}' fill='none' stroke='{GOLD_DEEP}' stroke-width='3'/>")
    if tilt:
        body = f"<g transform='rotate({_f(tilt)} 50 50)'>{body}</g>"
    pct = round(k * 100)
    return _svg(size, size, f"<title>Moon {pct}% lit</title>{body}", 100, 100,
                extra=f" role='img' aria-label='Moon {pct}% lit'")


def orientation_compass_svg(bearing_deg: float, size: int = 160, east: bool = True, label: str = "Jerusalem") -> str:
    """A compass rose (north up) with a gold arrow to `bearing_deg` (e.g. the bearing to Jerusalem from
    sky_layer.bearing_to_jerusalem) and, if east=True, a pale marker for due East (liturgical east)."""
    b = float(bearing_deg) % 360.0
    out = [f"<circle cx='100' cy='100' r='94' fill='{NIGHT_2}' stroke='{GOLD_DEEP}' stroke-width='3'/>",
           f"<circle cx='100' cy='100' r='84' fill='none' stroke='{GOLD}' stroke-width='1.5' stroke-dasharray='5 3'/>"]
    for a in range(0, 360, 15):
        L = 12 if a % 90 == 0 else (7 if a % 45 == 0 else 4)
        ra = math.radians(a)
        out.append(f"<line x1='{_f(100 + 84 * math.sin(ra))}' y1='{_f(100 - 84 * math.cos(ra))}' "
                   f"x2='{_f(100 + (84 - L) * math.sin(ra))}' y2='{_f(100 - (84 - L) * math.cos(ra))}' "
                   f"stroke='{GOLD}' stroke-width='{2 if a % 90 == 0 else 1.2}'/>")
    for t, a in (("N", 0), ("E", 90), ("S", 180), ("W", 270)):
        ra = math.radians(a)
        out.append(f"<text x='{_f(100 + 62 * math.sin(ra))}' y='{_f(100 - 62 * math.cos(ra) + 6)}' text-anchor='middle' "
                   f"font-family='Georgia, serif' font-size='17' font-weight='700' fill='{CREAM}'>{t}</text>")
    if east:
        out.append(f"<path d='M100,100 L176,100' stroke='{PEARL}' stroke-width='3' stroke-dasharray='6 4' opacity='.8'/>")
    rb = math.radians(b)
    tipx, tipy = 100 + 80 * math.sin(rb), 100 - 80 * math.cos(rb)
    px, py = math.cos(rb), math.sin(rb)
    bx, by = 100 + 52 * math.sin(rb), 100 - 52 * math.cos(rb)
    out.append(f"<line x1='100' y1='100' x2='{_f(bx)}' y2='{_f(by)}' stroke='{OUTLINE}' stroke-width='9'/>")
    out.append(f"<line x1='100' y1='100' x2='{_f(bx)}' y2='{_f(by)}' stroke='{GOLD}' stroke-width='5'/>")
    out.append(f"<polygon points='{_f(tipx)},{_f(tipy)} {_f(bx + 11 * px)},{_f(by + 11 * py)} {_f(bx - 11 * px)},{_f(by - 11 * py)}' "
               f"fill='{GOLD}' stroke='{OUTLINE}' stroke-width='2'/>")
    out.append(f"<circle cx='100' cy='100' r='15' fill='{NIGHT}' stroke='{GOLD}' stroke-width='2'/>")
    out.append(f"<g transform='translate(88 88) scale(0.24)'>{_cross_body('greek', GOLD, OUTLINE)}</g>")
    import html as _h
    lab = _h.escape(label)
    return _svg(size, size, f"<title>{lab}: {b:.1f} degrees from true north</title>{''.join(out)}", 200, 200,
                extra=f" role='img' aria-label='{lab}: {b:.0f} degrees from true north'")
