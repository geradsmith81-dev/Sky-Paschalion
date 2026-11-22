"""Colours, fonts and ornament for Sky Paschalion · Πασχάλιον: late-antique mosaic (Ravenna, 5th-6th c.).

Palette: the night-blue glass ground and gold tesserae of the Mausoleum of Galla Placidia (c. 425-450) and of
the apse of Sant'Apollinare in Classe (549); porphyry (imperial purple stone) as the accent; cream text like
the pearl and marble tesserae. Ornaments (Chi-Rho with alpha and omega, crosses of each tradition, jewelled and
meander bands, Moon, orientation compass): see ornaments.py. CSS classes all start with the prefix 'px-'.

Every text colour has at least 7:1 contrast (WCAG AAA) on its background (computed with the WCAG 2.x
relative-luminance formula; FORCE_CSS pins these colours, so the ratios are the same whether Streamlit,
the browser or the phone is in light or dark mode):
  text colour              BG    CARD  SIDEBAR  SUNDAY_BG  FEAST_BG  FAST_BG
  TEXT          #f6eedb  15.7    13.6     14.7       11.5      13.3     14.4
  MUTED         #dad1ba  11.9    10.4     11.2        8.7      10.1     11.0
  GOLD          #e8c25c  10.6     9.2     10.0        7.8       9.0      9.8
  LINK          #a6d5f2  11.6    10.1     10.9        8.5       9.8     10.7
  OBS           #c3e4a6  12.9    11.2     12.1        9.4      11.0     11.9
  PORPHYRY_TEXT #e6b8dc  10.6     9.2      9.9        7.7       9.0      9.7
  chips (INK #0a1433 on pastel): pascha 14.7, great_feast 11.7, feast 13.7, fast 11.3, strict_fast 9.4,
    fast_free 12.8, commemoration 11.8, movable 13.1, civil 13.8
  INK on GOLD: 10.6:1 · white on LAPIS #2a4d9b (primary buttons): 8.0:1 · white on #24356c (hover, today row):
  11.7:1 · white on PORPHYRY #7a2f6b: 8.6:1 · white on PORPHYRY_DEEP #5e2152: 11.6:1
  lowest of all: 7.7:1 (all >= 7:1).

Fonts (assets/fonts, WOFF2 subsets, SIL Open Font License 1.1; see THIRD_PARTY_design.md): embedded as data
URIs by apply(), each with a unicode-range, so text in every liturgical script displays on any device:
  PxSerif (Noto Serif: Latin + polytonic Greek, regular and bold), PxDisplay (Cinzel Bold: titles), PxSlavonic (Ponomar: Church
  Slavonic), PxCoptic (Noto Sans Coptic), PxEthiopic (Noto Serif Ethiopic: Ge'ez), PxArmenian (Noto Serif
  Armenian), PxSyriac (Noto Sans Syriac = Estrangela), PxSyriacWestern (Serto), PxSyriacEastern (Madnhaya),
  PxArabic (Noto Naskh Arabic).
"""
from __future__ import annotations

import base64
import functools
import html
import os

import streamlit as st

import ornaments as orn

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "assets", "fonts")
CSS_PREFIX = "px-"

# ---------------------------------------------------------------- palette
BG = "#0a1433"            # deep mosaic lapis (night-blue glass ground)
CARD = "#13204a"          # blue glass panel
SIDEBAR = "#0e1a3d"
SUNDAY_BG = "#1a2c63"     # Sundays (the Lord's Day) in month grids
FEAST_BG = "#2b2412"      # gold-ground cells: great feasts
FAST_BG = "#26163a"       # porphyry-dark cells: fast days
TEXT = "#f6eedb"          # cream (pearl and marble tesserae)
MUTED = "#dad1ba"
GOLD = "#e8c25c"          # gold tesserae
GOLD_LIGHT = "#f5dc8e"
GOLD_DEEP = "#a8792a"     # gold in shade (rules, borders)
LINK = "#a6d5f2"          # pale sky blue
OBS = "#c3e4a6"           # pale laurel green: what is observed in the sky
INK = "#0a1433"           # dark ink for chips and gold buttons
LAPIS = "#2a4d9b"         # ultramarine glass (primary buttons: white text 8.0:1)
LAPIS_HOVER = "#24356c"
PORPHYRY = "#7a2f6b"      # imperial porphyry (accent, ornament; white text 8.6:1)
PORPHYRY_DEEP = "#5e2152"
PORPHYRY_TEXT = "#e6b8dc" # porphyry-pink text on the dark ground
PEARL = "#f3eee2"
EMERALD = "#2f7a4f"       # laurel green (ornament only)
OBS_BG = "#16331f"

# Chips for feasts.py kinds and ranks: dark ink on pastel.
CHIP = {
    "pascha": "#f7e7b0", "great_feast": "#efcd6e", "feast": "#f2dfa6", "commemoration": "#bcd3f2",
    "fast": "#d9c6e6", "strict_fast": "#c9b3dc", "fast_free": "#b9e1da", "movable": "#c7e3c0", "civil": "#e9e0c9",
}
KIND_LABEL = {
    "pascha": "Pascha (Easter)", "great_feast": "Great feast", "feast": "Feast", "commemoration": "Commemoration",
    "fast": "Fast", "strict_fast": "Strict fast", "fast_free": "Fast-free", "movable": "Movable (from Pascha)",
    "civil": "Civil date",
}

# ---------------------------------------------------------------- fonts
# key: (css family, file, weight, unicode-range)
FONTS = {
    "serif": ("PxSerif", "PxSerif-Regular.woff2", "400",
              "U+0020-007E, U+00A0-017F, U+0218-021B, U+02B0-02FF, U+0300-036F, U+0370-03FF, U+1DC0-1DFF, U+1E00-1E9F, "
              "U+1F00-1FFF, U+2000-206F, U+20AC, U+2116, U+2122, U+2190, U+2192, U+2212, U+25CC"),
    "serif_bold": ("PxSerif", "PxSerif-Bold.woff2", "700",
              "U+0020-007E, U+00A0-017F, U+0218-021B, U+02B0-02FF, U+0300-036F, U+0370-03FF, U+1DC0-1DFF, U+1E00-1E9F, "
              "U+1F00-1FFF, U+2000-206F, U+20AC, U+2116, U+2122, U+2190, U+2192, U+2212, U+25CC"),
    # Cinzel Bold serves every weight of the display face (titles and headings are bold anyway).
    "display": ("PxDisplay", "PxDisplay-Bold.woff2", "400 900",
                "U+0020-007E, U+00A0-017F, U+0218-021B, U+02B0-02FF, U+0300-036F, U+1E00-1E9F, U+2000-206F, U+20AC, U+2116, U+2122"),
    "slavonic": ("PxSlavonic", "PxSlavonic-Regular.woff2", 400,
                 "U+0020-007E, U+00A0-00BF, U+0300-036F, U+0400-052F, U+1C80-1C8F, U+1DC0-1DFF, U+2000-206F, U+2DE0-2DFF, "
                 "U+2E00-2E7F, U+A640-A69F, U+FE20-FE2F, U+1E030-1E08F"),
    "coptic": ("PxCoptic", "PxCoptic-Regular.woff2", 400,
               "U+0020-007E, U+00A0-00BF, U+0300-036F, U+03E2-03EF, U+2000-206F, U+2C80-2CFF, U+FE20-FE2F, U+102E0-102FF"),
    "ethiopic": ("PxEthiopic", "PxEthiopic-Regular.woff2", 400,
                 "U+0020-007E, U+00A0-00BF, U+1200-139F, U+2000-206F, U+2D80-2DDF, U+AB00-AB2F, U+1E7E0-1E7FF"),
    "armenian": ("PxArmenian", "PxArmenian-Regular.woff2", 400,
                 "U+0020-007E, U+00A0-00BF, U+0530-058F, U+2000-206F, U+FB13-FB17"),
    "syriac": ("PxSyriac", "PxSyriac-Regular.woff2", 400,
               "U+0020-007E, U+00A0-00BF, U+0300-036F, U+060C, U+061B-061F, U+0640, U+064B-0652, U+0670, U+0700-074F, "
               "U+0860-086F, U+2000-206F"),
    "syriac_western": ("PxSyriacWestern", "PxSyriacWestern-Regular.woff2", 400,
                       "U+0020-007E, U+00A0-00BF, U+0300-036F, U+060C, U+061B-061F, U+0640, U+064B-0652, U+0670, "
                       "U+0700-074F, U+0860-086F, U+2000-206F"),
    "syriac_eastern": ("PxSyriacEastern", "PxSyriacEastern-Regular.woff2", 400,
                       "U+0020-007E, U+00A0-00BF, U+0300-036F, U+060C, U+061B-061F, U+0640, U+064B-0652, U+0670, "
                       "U+0700-074F, U+0860-086F, U+2000-206F"),
    "arabic": ("PxArabic", "PxArabic-Regular.woff2", 400,
               "U+0600-06FF, U+0750-077F, U+08A0-08FF, U+FB50-FDFF, U+FE70-FEFF, U+200C-200F"),
}
# Font groups by script (a 'script' key in apply(scripts=...) loads these files).
SCRIPT_FONTS = {
    "latin": ("serif", "serif_bold", "display"), "greek": ("serif", "serif_bold", "display"),
    "slavonic": ("slavonic",), "coptic": ("coptic",), "ethiopic": ("ethiopic",), "armenian": ("armenian",),
    "syriac": ("syriac", "syriac_western", "syriac_eastern"), "arabic": ("arabic",),
}
ALL_SCRIPTS = tuple(SCRIPT_FONTS)

SERIF = "'PxSerif', 'Noto Serif', 'Palatino Linotype', Palatino, 'Book Antiqua', Georgia, 'Times New Roman', serif"
DISPLAY = "'PxDisplay', 'Cinzel', 'Trajan Pro', " + SERIF
STACK = {
    "latin": SERIF, "greek": SERIF,
    "slavonic": "'PxSlavonic', 'Ponomar Unicode', 'Ponomar', 'Monomakh Unicode', 'Noto Serif', " + SERIF,
    "coptic": "'PxCoptic', 'Noto Sans Coptic', 'Antinoou', 'Segoe UI Historic', " + SERIF,
    "ethiopic": "'PxEthiopic', 'Noto Serif Ethiopic', 'Abyssinica SIL', 'Nyala', 'Ebrima', " + SERIF,
    "armenian": "'PxArmenian', 'Noto Serif Armenian', 'Sylfaen', " + SERIF,
    "syriac": "'PxSyriac', 'Noto Sans Syriac', 'Estrangelo Edessa', 'Segoe UI Historic', sans-serif",
    "syriac_western": "'PxSyriacWestern', 'Noto Sans Syriac Western', 'Serto Jerusalem', 'PxSyriac', sans-serif",
    "syriac_eastern": "'PxSyriacEastern', 'Noto Sans Syriac Eastern', 'East Syriac Adiabene', 'PxSyriac', sans-serif",
    "arabic": "'PxArabic', 'Noto Naskh Arabic', 'Amiri', 'Traditional Arabic', 'Segoe UI', Tahoma, sans-serif",
}

# Language codes of the contract -> (script, writing direction, HTML lang attribute).
LANG_SCRIPT = {
    "en": ("latin", "ltr", "en"), "la": ("latin", "ltr", "la"), "ro": ("latin", "ltr", "ro"),
    "grc": ("greek", "ltr", "grc"), "cu": ("slavonic", "ltr", "cu"), "cop": ("coptic", "ltr", "cop"),
    "gez": ("ethiopic", "ltr", "gez"), "xcl": ("armenian", "ltr", "xcl"), "syc": ("syriac", "rtl", "syc"),
    "ar": ("arabic", "rtl", "ar"), "ka": ("latin", "ltr", "ka"),   # Georgian: system fonts (no bundled face)
    "am": ("ethiopic", "ltr", "am"),   # Amharic (Ethiopic script; used for the Ethiopian calendar's own name)
    "ml": ("latin", "ltr", "ml"), "hu": ("latin", "ltr", "hu"), "fi": ("latin", "ltr", "fi"),
    "sq": ("latin", "ltr", "sq"),      # Malayalam uses system fonts (no bundled face)
}
# Syriac script variants (sects.py notes which one each church uses).
SYRIAC_VARIANT = {"estrangela": "syriac", "serto": "syriac_western", "madnhaya": "syriac_eastern",
                  "western": "syriac_western", "eastern": "syriac_eastern"}


@functools.lru_cache(maxsize=None)
def _font_b64(fname: str) -> str | None:
    try:
        with open(os.path.join(FONT_DIR, fname), "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")
    except OSError:
        return None


@functools.lru_cache(maxsize=32)
def font_face(scripts: tuple | None = None) -> str:
    """@font-face rules (fonts embedded as data URIs) for the given scripts (keys of SCRIPT_FONTS);
    None = all bundled fonts (about 0.56 MB of base64). Latin/Greek is always included (about 0.19 MB). A missing
    file is skipped: the stacks above then fall back to the system's fonts."""
    want = ["latin"] + list(ALL_SCRIPTS if scripts is None else scripts)
    keys = []
    for s in want:
        for k in SCRIPT_FONTS.get(s, ()):
            if k not in keys:
                keys.append(k)
    out = []
    for k in keys:
        family, fname, weight, urange = FONTS[k]
        b64 = _font_b64(fname)
        if not b64:
            continue
        out.append(f"@font-face {{ font-family: '{family}'; src: url(data:font/woff2;base64,{b64}) format('woff2'); "
                   f"font-weight: {weight}; font-style: normal; font-display: swap; unicode-range: {urange}; }}")
    return "\n".join(out)


def scripts_for_langs(langs) -> tuple:
    """The script keys needed for a list of language codes, e.g. a tradition's liturgical_languages:
    scripts_for_langs(['syc', 'ar']) -> ('syriac', 'arabic')."""
    out = []
    for lg in langs or ():
        s = LANG_SCRIPT.get(lg, ("latin",))[0]
        if s not in out:
            out.append(s)
    return tuple(out)


def native(text: str, lang: str, variant: str | None = None, cls: str = "") -> str:
    """Text in a liturgical language, as a span with the right font, lang and direction.
    variant: Syriac script variant (estrangela | serto | madnhaya)."""
    script, direction, code = LANG_SCRIPT.get(lang, ("latin", "ltr", lang or "en"))
    if script == "syriac" and variant:
        script = SYRIAC_VARIANT.get(variant, "syriac")
    extra = f" {cls}" if cls else ""
    return (f"<span class='px-native px-s-{script}{extra}' lang='{html.escape(code)}' dir='{direction}'>"
            f"{html.escape(text)}</span>")


def label(en: str, native_text: str = "", lang: str = "en", variant: str | None = None) -> str:
    """'English · native' as HTML (the series' display convention)."""
    if not native_text or lang == "en" or native_text.strip() == (en or "").strip():
        return html.escape(en)
    return f"{html.escape(en)} <span class='px-dot'>·</span> {native(native_text, lang, variant)}"


# ---------------------------------------------------------------- page CSS
JEWEL = orn.data_uri(orn.jewel_band_tile_svg(28))
MEANDER = orn.data_uri(orn.meander_tile_svg(22))
CROSS_ICON = orn.data_uri(orn.cross_svg("greek", 40))
_SCRIPT_CSS = "\n".join(f".px-s-{k} {{ font-family: {v}; }}" for k, v in STACK.items())

CSS_BODY = f"""
.block-container, [data-testid="stMainBlockContainer"] {{ padding-top: 4.6rem; }}
[data-testid="stAppViewContainer"] {{ background:
   radial-gradient(ellipse at 50% -10%, rgba(42,77,155,.40), rgba(0,0,0,0) 58%), {BG}; }}
[data-testid="stSidebar"] {{ background: {SIDEBAR}; border-right: 1px solid rgba(232,194,92,.30); }}
.stApp, .stApp p, .stApp li, .stApp label {{ font-family: {SERIF}; }}
h1, h2, h3, h4 {{ font-family: {DISPLAY}; color: {GOLD}; letter-spacing: .02em; }}
{_SCRIPT_CSS}
.px-native {{ unicode-bidi: isolate; color: inherit; }}
.px-native[dir="rtl"] {{ direction: rtl; }}
.px-s-syriac, .px-s-syriac_western, .px-s-syriac_eastern, .px-s-arabic {{ font-size: 1.12em; line-height: 1.5; }}
.px-s-ethiopic {{ line-height: 1.55; }}
.px-dot {{ color: {GOLD}; }}
.px-head {{ display: flex; align-items: center; gap: 14px; margin: .4rem 0 .2rem 0; }}
.px-head svg {{ flex: 0 0 auto; border-radius: 12px; }}
.px-title {{ font-family: {DISPLAY}; font-size: 2.05rem; font-weight: 700; color: {GOLD}; line-height: 1.15; letter-spacing: .03em; }}
.px-title-gr {{ font-family: {SERIF}; font-weight: 400; color: {GOLD_LIGHT}; font-size: 1.6rem; margin-left: .4rem; letter-spacing: 0; }}
.px-sub {{ color: {MUTED}; margin-bottom: .4rem; font-size: .95rem; }}
.px-band {{ height: 28px; background-image: url("{JEWEL}"); background-repeat: repeat-x; background-size: auto 28px;
            margin: .25rem 0 .7rem 0; border-top: 1px solid {GOLD_DEEP}; border-bottom: 1px solid {GOLD_DEEP}; }}
.px-meander {{ height: 22px; background-image: url("{MEANDER}"); background-repeat: repeat-x; background-size: auto 22px;
               margin: .4rem 0 .6rem 0; }}
.px-card {{ background: {CARD}; border: 1px solid {GOLD_DEEP}; outline: 1px solid rgba(232,194,92,.35); outline-offset: -5px;
            border-radius: 4px; padding: .95rem 1.15rem; margin-bottom: .8rem; color: {TEXT}; }}
.px-card h3 {{ font-family: {DISPLAY}; color: {GOLD}; margin: 0 0 .4rem 0; font-size: 1.08rem; font-weight: 700;
               padding-left: 27px; background: url("{CROSS_ICON}") no-repeat left center; background-size: 19px 19px; }}
.px-big {{ font-family: {SERIF}; font-size: 1.55rem; font-weight: 700; color: {TEXT}; line-height: 1.25; }}
.px-muted {{ color: {MUTED}; font-size: .92rem; }}
.px-obs {{ color: {OBS}; }}
.px-porph {{ color: {PORPHYRY_TEXT}; }}
.px-grid {{ width: 100%; border-collapse: separate; border-spacing: 4px; table-layout: fixed; }}
.px-grid th {{ font-family: {DISPLAY}; color: {GOLD}; font-weight: 700; font-size: .9rem; padding: 2px 4px; text-align: left;
               border-bottom: 2px solid {GOLD_DEEP}; }}
.px-grid td {{ background: {CARD}; border-radius: 3px; vertical-align: top; padding: 5px 6px; height: 108px; color: {TEXT};
               border: 1px solid rgba(168,121,42,.55); }}
.px-grid td.px-empty {{ background: transparent; border: none; }}
.px-grid td.px-sun {{ background: {SUNDAY_BG}; }}
.px-grid td.px-feast {{ background: {FEAST_BG}; box-shadow: inset 0 3px 0 {GOLD}; }}
.px-grid td.px-fast {{ background: {FAST_BG}; box-shadow: inset 0 -3px 0 {PORPHYRY}; }}
.px-grid td.px-today {{ border: 2px solid {GOLD}; }}
.px-civ {{ font-weight: 700; font-size: 1.05rem; color: {TEXT}; }}
.px-cal {{ float: right; text-align: right; font-size: .95rem; color: {GOLD}; line-height: 1.2; }}
.px-cal small {{ color: {MUTED}; font-size: .74rem; display: block; }}
.px-chip {{ display: inline-block; color: {INK}; border-radius: 3px; padding: 1px 6px; margin: 2px 2px 0 0; font-size: .78rem;
            font-weight: 600; line-height: 1.45; border: 1px solid rgba(10,20,51,.35); }}
.px-chip .px-native {{ color: {INK}; font-weight: 600; }}
.px-chip .px-dot {{ color: {INK}; }}
.px-line {{ font-size: .78rem; color: {MUTED}; display: block; margin-top: 2px; }}
.px-line b {{ color: {TEXT}; }}
.px-legend span {{ margin-right: 6px; }}
.px-table {{ width: 100%; border-collapse: collapse; font-size: .93rem; }}
.px-table th {{ font-family: {DISPLAY}; color: {GOLD}; text-align: left; border-bottom: 2px solid {GOLD_DEEP}; padding: 5px 6px; }}
.px-table td {{ color: {TEXT}; border-bottom: 1px solid rgba(168,121,42,.40); padding: 5px 6px; vertical-align: top; }}
.px-table tr.px-today-row td {{ background: {LAPIS_HOVER}; color: #ffffff; font-weight: 700; }}
.px-table td.px-diff {{ color: {GOLD}; font-weight: 700; }}
.px-scroll {{ overflow-x: auto; -webkit-overflow-scrolling: touch; max-height: 70vh; overflow-y: auto;
              border: 1px solid {GOLD_DEEP}; border-radius: 6px; background: {CARD}; }}
.px-badge {{ display: inline-flex; align-items: center; gap: .4rem; background: {CARD}; color: {TEXT}; border: 1px solid {GOLD};
             border-radius: 999px; padding: .12rem .7rem .12rem .45rem; font-family: {SERIF}; font-size: .9rem; font-weight: 700;
             vertical-align: middle; }}
.px-badge svg {{ flex: 0 0 auto; }}
.px-badge .px-native {{ font-weight: 400; }}
.px-pop {{ display: inline-block; position: relative; vertical-align: top; }}
.px-pop > summary {{ list-style: none; cursor: pointer; display: inline; }}
.px-pop > summary::-webkit-details-marker {{ display: none; }}
.px-pop > summary .px-chip {{ text-decoration: underline dotted rgba(10,20,51,.6); text-underline-offset: 2px; }}
.px-pop[open] > summary .px-chip {{ outline: 2px solid {GOLD}; }}
.px-popbody {{ position: absolute; z-index: 1000; left: 0; top: calc(100% + 4px); width: 340px; max-width: 80vw; background: {CARD};
               color: {TEXT}; border: 1px solid {GOLD}; border-radius: 6px; padding: .7rem .85rem; box-shadow: 0 8px 24px rgba(0,0,0,.65);
               font-size: .86rem; line-height: 1.45; text-align: left; white-space: normal; font-weight: 400; }}
.px-pop-r .px-popbody {{ left: auto; right: 0; }}
.px-dlg .px-scroll {{ max-height: none; overflow-y: visible; }}
.px-pop-inline {{ margin: 2px 2px 0 0; }}
.px-pop-inline > summary .px-chip {{ margin: 0; }}
.px-pop-inline[open] {{ display: block; }}
.px-pop-inline .px-popbody {{ position: static; width: auto; max-width: 34rem; margin: 5px 0 4px 0; box-shadow: none; }}
.px-pop > summary .px-fxname {{ text-decoration: underline dotted {MUTED}; text-underline-offset: 3px; }}
.px-pop[open] > summary .px-fxname {{ color: {GOLD}; }}
.px-pop > summary:focus-visible {{ outline: 2px solid {GOLD}; outline-offset: 2px; }}
.px-pop-title {{ font-family: {DISPLAY}; color: {GOLD}; font-weight: 700; font-size: 1rem; margin-bottom: .3rem; }}
.px-pop-src {{ color: {MUTED}; font-size: .78rem; margin-top: .45rem; font-style: italic; }}
.px-orient {{ display: flex; flex-wrap: wrap; align-items: center; gap: .6rem 1.1rem; background: {CARD};
              border: 1px solid {GOLD_DEEP}; border-radius: 6px; padding: .7rem .9rem; color: {TEXT}; }}
.px-orient svg {{ flex: 0 0 auto; max-width: 100%; height: auto; }}
.px-orient-deg {{ font-family: {SERIF}; font-size: 1.7rem; font-weight: 700; color: {GOLD}; line-height: 1.1; }}
.px-orient-text {{ color: {MUTED}; font-size: .9rem; }}
.px-moon, .px-cross {{ display: inline-block; vertical-align: middle; line-height: 0; }}
a {{ color: {LINK}; }}
@media (pointer: coarse) {{
  .px-grid td {{ height: auto; min-height: 80px; }}
  div[data-testid="stRadio"] label {{ padding: 6px 4px; }}
  button {{ min-height: 44px; }}
}}
@media (max-width: 640px) {{
  .px-popbody {{ position: static; width: auto; max-width: none; margin-top: 4px; }}
  .px-title {{ font-size: 1.45rem; }} .px-title-gr {{ font-size: 1.2rem; }}
  .px-big {{ font-size: 1.28rem; }}
  .px-head svg {{ width: 52px; height: 52px; }}
  .px-grid td {{ padding: 3px 3px; }}
}}
"""

# The location button (locator.py from Sky Luach / Sky Taqwim: its component CSS). The px-, tq- and sl-
# prefixes are all styled, so the button looks right whichever prefix the component's JavaScript uses.
_PIN = orn.data_uri(orn.cross_svg("greek", 32, color=GOLD, line=LAPIS))
LOCATOR_CSS = f"""
.px-loc, .tq-loc, .sl-loc {{ display:flex; flex-wrap:wrap; align-items:center; gap:.5rem .8rem; margin:.1rem 0 .5rem 0; font-family: {SERIF}; }}
.px-loc-btn, .tq-loc-btn, .sl-loc-btn {{ background:{LAPIS}; color:#ffffff; border:1px solid {GOLD}; border-radius:6px;
  padding:.35rem .8rem .35rem 2rem; font-weight:700; font-size:.92rem; cursor:pointer; min-height:36px;
  background-image:url("{_PIN}"); background-repeat:no-repeat; background-position:.55rem center; background-size:16px 16px; }}
.px-loc-btn:hover, .tq-loc-btn:hover, .sl-loc-btn:hover {{ background-color:{LAPIS_HOVER}; }}
.px-loc-btn:focus-visible, .tq-loc-btn:focus-visible, .sl-loc-btn:focus-visible {{ outline:2px solid {GOLD}; outline-offset:2px; }}
.px-loc-place, .tq-loc-place, .sl-loc-place {{ color:{TEXT}; font-size:.95rem; }}
.px-loc-status, .tq-loc-status, .sl-loc-status {{ color:{MUTED}; font-size:.88rem; }}
.px-loc-status a, .tq-loc-status a, .sl-loc-status a {{ color:{LINK}; }}
@media (pointer: coarse) {{ .px-loc-btn, .tq-loc-btn, .sl-loc-btn {{ min-height:44px; }} }}
"""

# The live 'Face east' compass (orient_live.py). Injected page-wide by apply(); the component's layout is ALSO
# written as inline styles, because components.v2 css= is not applied on Streamlit Community Cloud.
ORIENT_LIVE_CSS = f"""
.px-ol-wrap {{ position: relative; padding-top: 14px; flex: 0 0 auto; }}
.px-ol-lubber {{ position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 0; height: 0;
                border-left: 9px solid transparent; border-right: 9px solid transparent; border-top: 13px solid {PORPHYRY_TEXT}; }}
.px-ol-stage {{ position: relative; border-radius: 50%; transition: box-shadow .25s; }}
.px-ol-stage.px-ol-on {{ box-shadow: 0 0 0 4px {OBS}, 0 0 18px 4px rgba(195,228,166,.55); }}
.px-ol-dial, .px-ol-arrow {{ position: absolute; inset: 0; will-change: transform; transform-origin: 50% 50%; }}
.px-ol-dial svg, .px-ol-arrow svg {{ width: 100% !important; height: 100% !important; max-width: none !important; display: block; }}
.px-ol-info {{ flex: 1 1 13rem; min-width: 12rem; }}
.px-ol-btn {{ display: none; margin-top: .55rem; background: {LAPIS}; color: #ffffff; border: 1px solid {GOLD};
             border-radius: 6px; padding: .45rem .9rem; font: 700 .95rem {SERIF}; min-height: 44px; cursor: pointer; }}
.px-ol-btn:focus-visible {{ outline: 2px solid {GOLD}; outline-offset: 2px; }}
.px-ol-status {{ margin-top: .45rem; color: {TEXT}; font-size: .95rem; font-weight: 600; min-height: 1.3em; }}
.px-ol-status.px-ol-good {{ color: {OBS}; }}
.px-ol-status.px-ol-warn {{ color: {GOLD}; }}
.px-ol-tab {{ display: none; margin-top: .4rem; color: {LINK}; font-size: .92rem; }}
"""

# Small additions used by app.py / pages.py (assembly track).
APP_CSS = f"""
.px-prov {{ display: inline-block; background: {PORPHYRY_DEEP}; color: #ffffff; border: 1px solid {PORPHYRY_TEXT};
           border-radius: 3px; padding: 0 6px; font-size: .74rem; font-weight: 700; margin-left: .35rem; vertical-align: middle; }}
.px-kv {{ display: grid; grid-template-columns: max-content 1fr; gap: .15rem .9rem; font-size: .93rem; }}
.px-kv > div:nth-child(odd) {{ color: {MUTED}; }}
.px-kv > div:nth-child(even) {{ color: {TEXT}; }}
.px-note {{ border-left: 3px solid {GOLD}; padding: .35rem .7rem; margin: .4rem 0; background: rgba(19,32,74,.85); color: {TEXT}; font-size: .92rem; }}
.px-warn {{ border-left: 3px solid {PORPHYRY_TEXT}; padding: .35rem .7rem; margin: .4rem 0; background: rgba(94,33,82,.55); color: #ffffff; font-size: .92rem; }}
.px-list-day {{ border-bottom: 1px solid rgba(168,121,42,.40); padding: .35rem .2rem; }}
.px-list-day.px-today {{ background: {LAPIS_HOVER}; }}
.px-table td a, .px-card a {{ color: {LINK}; }}
.px-cols {{ display: flex; flex-wrap: wrap; gap: .8rem; }}
.px-cols > .px-card {{ flex: 1 1 15rem; min-width: 14rem; }}
"""

# Streamlit's own widgets, text and menus. These rules set the colours directly, so the app reads the same
# (cream and gold on mosaic blue) whether the browser, the phone or Streamlit's menu is in light or dark mode,
# and even if .streamlit/config.toml is missing. Every pair here is at least 7:1 (WCAG AAA).
# Note: st.dataframe / st.data_editor draw on a canvas in Streamlit's theme colours, which CSS cannot
# recolour; use HTML tables (class px-table) instead.
FORCE_CSS = f"""
<style>
:root {{ color-scheme: dark; }}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stBottom"] > div {{ color: {TEXT}; }}
.stApp {{ background-color: {BG}; }}
[data-testid="stHeader"] {{ background: rgba(10,20,51,.92); color: {TEXT}; }}
[data-testid="stHeader"] button, [data-testid="stToolbar"] button {{ background-color: transparent !important; border-color: transparent !important; }}
[data-testid="stHeader"] button, [data-testid="stHeader"] a, [data-testid="stToolbar"] *,
[data-testid="stSidebarCollapseButton"] *, [data-testid="stExpandSidebarButton"] *, [data-testid="stSidebarCollapsedControl"] * {{
  color: {TEXT} !important; fill: currentColor; }}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {{ background-color: {SIDEBAR} !important; color: {TEXT}; }}
[data-testid="stSidebarNav"] a, [data-testid="stSidebarNav"] span {{ color: {TEXT} !important; }}
[data-testid="stSidebarNav"] a[aria-current="page"], [data-testid="stSidebarNav"] a:hover {{ background-color: {LAPIS_HOVER} !important; }}
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
[data-testid="stText"], [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p, label, legend,
[data-testid="stRadio"] label, [data-testid="stRadio"] p, [data-testid="stCheckbox"] p, [data-testid="stToggle"] p,
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] p, [data-testid="stMetricDelta"] {{ color: {TEXT} !important; }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p, .stCaption, small,
[data-testid="stWidgetLabel"] [data-testid="stTooltipIcon"] {{ color: {MUTED} !important; }}
[data-testid="stMarkdownContainer"] a, [data-testid="stCaptionContainer"] a {{ color: {LINK} !important; }}
[data-testid="stMarkdownContainer"] code {{ background: {CARD}; color: {GOLD}; }}
h1, h2, h3, h4, h5, h6, [data-testid="stHeading"] * {{ color: {GOLD} !important; }}
/* text boxes, number boxes, select boxes and their menus */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"], [data-baseweb="select"] > div,
[data-testid="stNumberInputContainer"], [data-testid="stDateInput"] [data-baseweb="input"] {{
  background-color: {CARD} !important; border-color: rgba(232,194,92,.55) !important; color: {TEXT} !important; }}
[data-baseweb="input"] input, [data-baseweb="base-input"] input, textarea, [data-baseweb="select"] input,
[data-baseweb="select"] div, [data-baseweb="select"] span {{ color: {TEXT} !important; -webkit-text-fill-color: {TEXT} !important; background-color: transparent; }}
input::placeholder, textarea::placeholder {{ color: {MUTED} !important; -webkit-text-fill-color: {MUTED}; opacity: 1; }}
[data-baseweb="select"] svg, [data-testid="stNumberInputContainer"] svg {{ color: {TEXT} !important; fill: currentColor; }}
[data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"] {{ background: {CARD} !important; color: {TEXT} !important; }}
[data-baseweb="popover"] > div, [data-baseweb="popover"] ul, [data-baseweb="menu"], [role="listbox"] {{
  background-color: {CARD} !important; color: {TEXT} !important; border-color: {GOLD_DEEP} !important; }}
[data-baseweb="popover"] li, [role="option"] {{ color: {TEXT} !important; background-color: {CARD}; }}
[data-baseweb="popover"] li:hover, [role="option"]:hover, [role="option"][aria-selected="true"] {{ background-color: {LAPIS_HOVER} !important; }}
[data-baseweb="tag"] {{ background-color: {LAPIS} !important; color: #ffffff !important; }}
[data-baseweb="tag"] * {{ color: #ffffff !important; }}
[data-baseweb="calendar"], [data-baseweb="calendar"] * {{ background-color: {CARD}; color: {TEXT}; }}
[data-baseweb="calendar"] [aria-selected="true"], [data-baseweb="calendar"] [aria-selected="true"] * {{ background-color: {GOLD} !important; color: {INK} !important; }}
[data-baseweb="tooltip"], [data-baseweb="tooltip"] * {{ background-color: {CARD} !important; color: {TEXT} !important; }}
[data-baseweb="slider"] [role="slider"] {{ background-color: {GOLD} !important; }}
[data-testid="stSliderThumbValue"], [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {{ color: {TEXT} !important; }}
/* buttons */
[data-testid^="stBaseButton-secondary"], [data-testid="stDownloadButton"] button, .stButton > button, [data-testid="stLinkButton"] a {{
  background-color: {CARD} !important; color: {TEXT} !important; border: 1px solid {GOLD} !important; }}
[data-testid^="stBaseButton-secondary"]:hover, [data-testid="stDownloadButton"] button:hover, .stButton > button:hover,
[data-testid="stLinkButton"] a:hover {{ background-color: {LAPIS_HOVER} !important; color: #ffffff !important; }}
[data-testid^="stBaseButton-primary"] {{ background-color: {LAPIS} !important; color: #ffffff !important; border: 1px solid {GOLD} !important; }}
[data-testid^="stBaseButton-pills"], [data-testid^="stBaseButton-segmented_control"] {{ background-color: {CARD} !important; color: {TEXT} !important;
  border-color: {GOLD_DEEP} !important; }}
[data-testid$="Active"][data-testid^="stBaseButton"] {{ background-color: {LAPIS} !important; color: #ffffff !important; border-color: {GOLD} !important; }}
[data-testid^="stBaseButton"] p {{ color: inherit !important; }}
/* radio dots, check boxes and toggles stay visible on the dark ground */
[data-testid="stRadio"] [role="radio"] > div:first-child, [data-baseweb="radio"] > div:first-child {{ border-color: {GOLD} !important; }}
[data-baseweb="checkbox"] [role="checkbox"], [data-baseweb="checkbox"] > div:first-child {{ border-color: {GOLD} !important; }}
/* expanders, tabs, alerts, tables */
[data-testid="stExpander"] details, [data-testid="stExpander"] > details {{ background-color: {CARD} !important;
  border-color: rgba(232,194,92,.45) !important; color: {TEXT} !important; }}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {{ color: {GOLD} !important; background-color: transparent; }}
[data-testid="stExpander"] summary:hover {{ background-color: #1a2a5a !important; }}
[data-baseweb="tab"] {{ background-color: transparent !important; }}
[data-baseweb="tab"], [data-baseweb="tab"] p {{ color: {TEXT} !important; }}
[data-baseweb="tab"][aria-selected="true"], [data-baseweb="tab"][aria-selected="true"] p {{ color: {GOLD} !important; }}
[data-testid="stAlertContainer"], [data-testid="stAlert"] > div {{ background-color: {CARD} !important; color: {TEXT} !important;
  border: 1px solid {GOLD_DEEP}; }}
[data-testid="stAlertContainer"] *, [data-testid="stAlert"] * {{ color: {TEXT} !important; }}
[data-testid="stTable"] table, [data-testid="stTable"] th, [data-testid="stTable"] td {{ color: {TEXT} !important;
  background-color: {CARD} !important; border-color: rgba(232,194,92,.3) !important; }}
[data-testid="stTable"] th {{ color: {GOLD} !important; }}
[data-testid="stSpinner"], [data-testid="stSpinner"] * {{ color: {TEXT} !important; }}
[data-testid="stToast"] {{ background-color: {CARD} !important; color: {TEXT} !important; }}
[data-testid="stPopoverBody"] {{ background-color: {CARD} !important; color: {TEXT} !important; }}
hr {{ border-color: rgba(232,194,92,.35) !important; }}
/* st.dialog windows (summary links): the box takes Streamlit's theme background, white in light mode, so pin it dark */
[data-testid="stDialog"] div:has(> [role="dialog"]), [data-testid="stDialog"] [role="dialog"] {{
  background-color: {CARD} !important; color: {TEXT} !important; }}
[data-testid="stDialog"] div:has(> [role="dialog"]) {{ border: 1px solid {GOLD} !important; }}
[data-testid="stDialog"] [role="dialog"] h2, [data-testid="stDialog"] [role="dialog"] h2 * {{ color: {GOLD} !important; }}
[data-testid="stDialog"] [role="dialog"] p, [data-testid="stDialog"] [role="dialog"] label,
[data-testid="stDialog"] [role="dialog"] [data-testid="stWidgetLabel"] * {{ color: {TEXT} !important; }}
[data-testid="stDialog"] button[aria-label="Close"], [data-testid="stDialog"] button[aria-label="Close"] svg {{
  color: {TEXT} !important; fill: currentColor; stroke: currentColor; }}
[data-testid="stDialog"] input {{ color: {TEXT} !important; -webkit-text-fill-color: {TEXT} !important;
  background-color: transparent !important; }}
[data-testid="stDialog"] .px-scroll {{ background-color: {BG}; }}
</style>
"""

TITLE = "Sky Paschalion"
TITLE_GR = "Πασχάλιον"
SUBTITLE = "the Christian calendars of the apostolic churches, with Pascha and the sky from NASA JPL astronomy"


def css(scripts: tuple | None = None) -> str:
    """The page stylesheet (fonts + layout), as one <style> block."""
    return f"<style>\n{font_face(scripts)}\n{CSS_BODY}\n</style>"


def apply(scripts=None):
    """Inject the theme. scripts: None = all bundled fonts (~0.56 MB per page run); or a tuple of
    script keys, e.g. theme.scripts_for_langs(tradition['liturgical_languages']), to send only those fonts.
    Latin/polytonic Greek and the display face are always included."""
    st.html(css(tuple(scripts) if scripts is not None else None))
    st.html(FORCE_CSS)
    # the components' stylesheets, page-wide as well (components.v2 css= is not applied on Streamlit Cloud)
    st.html("<style>" + LOCATOR_CSS + ORIENT_LIVE_CSS + APP_CSS + "</style>")


# ---------------------------------------------------------------- HTML helpers
def header(subtitle: str = "", tradition: dict | None = None, lang: str | None = None):
    """Title row: the Chi-Rho emblem, 'Sky Paschalion · Πασχάλιον', subtitle and (optionally) a badge for the
    selected tradition (a sects.TRADITIONS dict)."""
    emblem = orn.chi_rho_svg(68, detail="medium", rounded=True, uid="pxhead")
    sub = html.escape(subtitle or SUBTITLE)
    badge = f" {tradition_badge(tradition, lang)}" if tradition else ""
    st.html(f"<div class='px-head'>{emblem}<div><div class='px-title'>{TITLE}"
            f"<span class='px-title-gr' lang='grc' title='Paschalion: the reckoning of Pascha'>{TITLE_GR}</span>"
            f"</div><div class='px-sub'>{sub}{badge}</div></div></div><div class='px-band' role='presentation'></div>")


def tradition_badge(tradition: dict, lang: str | None = None) -> str:
    """A badge with the tradition's cross and its name as 'English · native'."""
    t = tradition or {}
    langs = t.get("liturgical_languages") or ["en"]
    lg = lang or langs[0]
    cross = orn.cross_svg(t.get("cross_style", "latin"), 18)
    return (f"<span class='px-badge'>{cross}{label(t.get('name_en', ''), t.get('name_native', ''), lg)}</span>")


# feasts.RANKS vocabulary -> chip colour (Sky Paschalion app, assembly track)
RANK_CHIP = {
    "feast_of_feasts": "pascha",
    "great_feast": "great_feast", "solemnity": "great_feast", "major": "great_feast", "tabernacle": "great_feast",
    "lordly": "great_feast", "triduum": "great_feast", "great": "great_feast",
    "feast": "feast", "minor": "feast",
    "season": "movable",
    "memorial": "commemoration", "commemoration": "commemoration",
    "great_fast": "strict_fast", "fast": "fast", "fast_day": "fast",
}


def chip_kind(kind: str, rank=None) -> str:
    """Map a feasts.py (kind, rank) to a CHIP key. kind = feast | fast | commemoration (or a CHIP key);
    rank = a feasts.RANKS key (feast_of_feasts, great_feast, solemnity, major, ..., great_fast, fast, fast_day)."""
    r = str(rank).lower() if rank is not None else ""
    if kind == "commemoration":
        return "commemoration"
    if kind == "fast":
        return "strict_fast" if r in ("great_fast", "strict") or "strict" in r else "fast"
    if r in RANK_CHIP:
        k = RANK_CHIP[r]
        return "feast" if k in ("fast", "strict_fast") else k
    if kind in CHIP:
        return kind
    return "feast"


def chip(kind: str, text: str, native_text: str = "", lang: str = "en", rank=None, variant: str | None = None) -> str:
    """A coloured chip for a feast, fast or commemoration, 'English · native'."""
    k = chip_kind(kind, rank)
    return (f"<span class='px-chip' style='background:{CHIP[k]}'>{label(text, native_text, lang, variant)}</span>")


def legend(kinds=None) -> str:
    ks = [k for k in KIND_LABEL if kinds is None or k in kinds]
    return "<div class='px-legend'>" + "".join(chip(k, KIND_LABEL[k]) for k in ks) + "</div>"


def cross(style: str, size: int = 20) -> str:
    return f"<span class='px-cross'>{orn.cross_svg(style, size)}</span>"


def divider(style: str = "jewel") -> str:
    """A mosaic band between sections ('jewel' or 'meander')."""
    return f"<div class='px-{'band' if style == 'jewel' else 'meander'}' role='presentation'></div>"


def moon(illum: float, waxing: bool, size: int = 22, tilt: float = 0.0) -> str:
    return f"<span class='px-moon'>{orn.moon_phase_svg(illum, waxing, size, tilt)}</span>"


def orientation_box(bearing_deg: float, place: str = "", distance_km: float | None = None, size: int = 150,
                    target: str = "Jerusalem") -> str:
    """The bearing to Jerusalem (Holy Sepulchre) on a compass, with due East marked for comparison."""
    b = float(bearing_deg) % 360.0
    pts = ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"]
    word = pts[int((b + 22.5) // 45) % 8]
    where = f" from {html.escape(place)}" if place else ""
    dist = (f"<div class='px-orient-text'>{html.escape(target)} is {distance_km:,.0f} km away (great-circle).</div>"
            if distance_km else "")
    return (f"<div class='px-orient'>{orn.orientation_compass_svg(b, size, east=True, label=target)}<div>"
            f"<div class='px-orient-deg'>{b:.1f}°</div>"
            f"<div class='px-orient-text'>{html.escape(target)}{where}: {b:.1f}° from true north, toward the {word}. "
            f"The dashed line is due East (90°).</div>{dist}"
            f"<div class='px-orient-text'>A magnetic compass differs from true north by the local declination.</div>"
            f"</div></div>")
