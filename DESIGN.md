# Sky Paschalion design files (theme.py, ornaments.py, assets/)

Contract: CONTRACT.md v1 (Design track). Flat modules; `import theme` imports `ornaments`. No other app imports.

## theme.py

* Palette constants (hex): `BG #0a1433` (deep mosaic lapis), `CARD #13204a`, `SIDEBAR #0e1a3d`, `SUNDAY_BG #1a2c63`,
  `FEAST_BG #2b2412`, `FAST_BG #26163a`, `TEXT #f6eedb` (cream), `MUTED #dad1ba`, `GOLD #e8c25c`, `GOLD_LIGHT #f5dc8e`,
  `GOLD_DEEP #a8792a` (rules only, not text), `LINK #a6d5f2`, `OBS #c3e4a6`, `INK #0a1433`, `LAPIS #2a4d9b` (buttons),
  `LAPIS_HOVER #24356c`, `PORPHYRY #7a2f6b`, `PORPHYRY_DEEP #5e2152`, `PORPHYRY_TEXT #e6b8dc`, `PEARL #f3eee2`, `EMERALD #2f7a4f`.
  `CHIP[kind]` pastel chip colours, `KIND_LABEL[kind]`. `CSS_PREFIX = "px-"`.
* `apply(scripts=None)` — injects the page CSS with the @font-face rules (fonts as data URIs), `FORCE_CSS` and
  `LOCATOR_CSS`. `scripts=None` loads all fonts (~0.56 MB base64 per run); pass
  `theme.scripts_for_langs(tradition["liturgical_languages"])` to send only the needed scripts (Latin/Greek ~0.19 MB
  is always sent). `apply()` with no argument matches the contract.
* `FORCE_CSS` pins the colours of Streamlit's own widgets so the app is identical in light and dark mode.
* Helpers (HTML strings for `st.html`): `header(subtitle="", tradition=None, lang=None)` (calls st.html itself),
  `native(text, lang, variant=None)` (span with font, `lang`, `dir`; Syriac variant estrangela|serto|madnhaya),
  `label(en, native_text, lang, variant=None)` -> 'English · native', `tradition_badge(tradition_dict, lang=None)`,
  `chip(kind, text, native_text="", lang="en", rank=None, variant=None)`, `chip_kind(kind, rank)`, `legend(kinds=None)`,
  `cross(style, size)`, `divider(style="jewel"|"meander")`, `moon(illum, waxing, size, tilt)`,
  `orientation_box(bearing_deg, place="", distance_km=None, size=150, target="Jerusalem")`.
* Fonts: `FONTS`, `SCRIPT_FONTS`, `STACK`, `LANG_SCRIPT` (lang code -> script, dir, lang attr), `SYRIAC_VARIANT`,
  `font_face(scripts)`, `scripts_for_langs(langs)`, `css(scripts)`.
* CSS classes: px-head, px-title, px-title-gr, px-sub, px-band, px-meander, px-card, px-big, px-muted, px-obs, px-porph,
  px-grid (td.px-sun / px-feast / px-fast / px-today / px-empty), px-civ, px-cal, px-chip, px-line, px-legend, px-table
  (tr.px-today-row, td.px-diff), px-scroll, px-badge, px-pop (+ px-popbody, px-pop-title, px-pop-src, px-pop-r),
  px-orient, px-moon, px-cross, px-native + px-s-<script>, px-loc* (also tq-loc*, sl-loc* for a reused locator.py).

## ornaments.py

`chi_rho_svg(size=64, wreath=None, ground=True, alpha_omega=True, omega="uncial", detail="auto", maskable=False,
rounded=False, uid="px")`, `emblem_svg(size)`, `icon_svg(size, maskable, rounded)`, `icon_small_svg(size)`,
`cross_svg(style, size=28, color=GOLD, line=OUTLINE, ground=None)` with `CROSS_STYLES = latin, greek, coptic,
ethiopian, armenian, syriac, russian`, `jewel_band_tile_svg(h)`, `meander_tile_svg(h)`, `border_tile_svg(h, style)`,
`divider_svg(width, h, style, center)`, `tessera_frame_css()`, `moon_phase_svg(illum, waxing, size, tilt)`,
`orientation_compass_svg(bearing_deg, size, east, label)`, `data_uri(svg)`.
Detail levels: full (>= 160 px: tesserae, wreath, stars), medium (96-159 px: tesserae, ring), simple (< 96 px:
solid gold; alpha and omega only from 48 px, so the 16/32 px favicons show the Chi-Rho alone).
The Russian cross's footrest rises on the viewer's left (Christ's right).

## assets/

`paschalion_emblem.svg`, `paschalion_icon.png` (512), `paschalion_icon.ico` (16, 24, 32, 48, 64, 128, 256; each drawn
at its own size), `icons/` (apple-touch-icon 180, icon-180, icon-192, icon-512, icon-maskable-512, favicon-32,
favicon-16, favicon.svg), `fonts/` (WOFF2 subsets + OFL texts). Rebuild: `python tools/build_design_assets.py [--fonts]`.

## Checks run (15 Nov 2026, conda env luach, Streamlit 1.67)

* Contrast: palette table in theme.py's docstring (lowest designed pair 7.7:1). Rendered check in headless Edge:
  a mock page with Streamlit's widget markup (data-testid / data-baseweb attributes) and Streamlit's light-mode,
  then dark-mode, default colours underneath, with theme CSS + FORCE_CSS on top. Edge computed the colour of
  every text element against its composited background: light 73 elements, MIN 7.97; dark
  73 elements, MIN 7.97; none below 7:1 (lowest = white on the primary button). This is a mock of
  Streamlit's markup, not the live app: a live Streamlit page could not be rendered here (the headless browser
  never received the script output).
* Fonts: font test page (built with theme.css()) rendered in headless Edge; `document.fonts` lists all 11 bundled
  faces as `loaded` (read back from the DOM), and every script displays. Glyph coverage per Unicode block: see
  THIRD_PARTY_design.md (the subsets keep 100 % of what each original font covers in its blocks).
* Streamlit AppTest of a demo page using every helper: 0 exceptions.
