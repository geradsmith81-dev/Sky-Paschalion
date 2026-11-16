# Third-party material in the Sky Paschalion design files

The design code (`theme.py`, `ornaments.py`, `tools/build_design_assets.py`) and all drawings made by it — the
Chi-Rho emblem, the app icons (`assets/icons/`, `assets/paschalion_icon.ico`, `assets/paschalion_icon.png`,
`assets/paschalion_emblem.svg`), the seven cross forms, the jewelled and meander bands, the Moon and the
orientation compass — are original work for this app, drawn in code, under the app's MIT License
(Copyright (c) 2026 Gerad Smith). They follow late-antique models (Ravenna mosaics) in style only; no
photograph or image of any monument was copied or traced.

## Fonts (all SIL Open Font License 1.1)

Every font below was downloaded from the Google Fonts repository (github.com/google/fonts, `ofl/` folder,
15 Nov 2026), instanced from the variable font where needed (weight 400 or 700, width 100) and **subset** with
fontTools to the Unicode blocks the app uses, then saved as WOFF2 in `assets/fonts/`. A subset is a
"Modified Version" under the OFL. None of these fonts declares a Reserved Font Name in its licence, so a
modified version may be distributed; the files are renamed (`Px…`) to keep them distinct from the
originals. They are bundled with the app and are not sold by themselves. Each font's full licence text,
with its copyright line, is in `assets/fonts/OFL-<Font>.txt`.

| Font (version) | Designer | Copyright | Bundled file(s) | Licence text | Upstream source |
|---|---|---|---|---|---|
| Noto Serif 2.015 | Google | Copyright 2022 The Noto Project Authors (https://github.com/notofonts/latin-greek-cyrillic) | `PxSerif-Bold.woff2` (60 kB), `PxSerif-Regular.woff2` (57 kB) | [OFL-NotoSerif.txt](assets/fonts/OFL-NotoSerif.txt) | https://github.com/notofonts/latin-greek-cyrillic · via https://github.com/google/fonts/tree/main/ofl/notoserif |
| Cinzel 2.000 | Natanael Gama | Copyright 2020 The Cinzel Project Authors (https://github.com/NDISCOVER/Cinzel) | `PxDisplay-Bold.woff2` (25 kB) | [OFL-Cinzel.txt](assets/fonts/OFL-Cinzel.txt) | https://github.com/NDISCOVER/Cinzel · via https://github.com/google/fonts/tree/main/ofl/cinzel |
| Ponomar 1.302 | Aleksandr Andreev | Copyright 2025 The Ponomar Project Authors (https://github.com/slavonic/ponomar) | `PxSlavonic-Regular.woff2` (68 kB) | [OFL-Ponomar.txt](assets/fonts/OFL-Ponomar.txt) | https://github.com/slavonic/Ponomar · via https://github.com/google/fonts/tree/main/ofl/ponomar |
| Noto Sans Coptic 2.004 | Google | Copyright 2022 The Noto Project Authors (https://github.com/notofonts/coptic) | `PxCoptic-Regular.woff2` (20 kB) | [OFL-NotoSansCoptic.txt](assets/fonts/OFL-NotoSansCoptic.txt) | https://github.com/notofonts/coptic · via https://github.com/google/fonts/tree/main/ofl/notosanscoptic |
| Noto Serif Ethiopic 2.102 | Google | Copyright 2022 The Noto Project Authors (https://github.com/notofonts/ethiopic) | `PxEthiopic-Regular.woff2` (55 kB) | [OFL-NotoSerifEthiopic.txt](assets/fonts/OFL-NotoSerifEthiopic.txt) | https://github.com/notofonts/ethiopic · via https://github.com/google/fonts/tree/main/ofl/notoserifethiopic |
| Noto Serif Armenian 2.008 | Google | Copyright 2022 The Noto Project Authors (https://github.com/notofonts/armenian) | `PxArmenian-Regular.woff2` (16 kB) | [OFL-NotoSerifArmenian.txt](assets/fonts/OFL-NotoSerifArmenian.txt) | https://github.com/notofonts/armenian · via https://github.com/google/fonts/tree/main/ofl/notoserifarmenian |
| Noto Sans Syriac 3.000 | Google | Copyright 2022 The Noto Project Authors (https://github.com/notofonts/syriac) | `PxSyriac-Regular.woff2` (22 kB) | [OFL-NotoSansSyriac.txt](assets/fonts/OFL-NotoSansSyriac.txt) | https://github.com/notofonts/syriac · via https://github.com/google/fonts/tree/main/ofl/notosanssyriac |
| Noto Sans Syriac Western 3.001 | Google | Copyright 2022 The Noto Project Authors (https://github.com/notofonts/syriac) | `PxSyriacWestern-Regular.woff2` (24 kB) | [OFL-NotoSansSyriacWestern.txt](assets/fonts/OFL-NotoSansSyriacWestern.txt) | https://github.com/notofonts/syriac · via https://github.com/google/fonts/tree/main/ofl/notosanssyriacwestern |
| Noto Sans Syriac Eastern 3.001 | Google | Copyright 2022 The Noto Project Authors (https://github.com/notofonts/syriac) | `PxSyriacEastern-Regular.woff2` (20 kB) | [OFL-NotoSansSyriacEastern.txt](assets/fonts/OFL-NotoSansSyriacEastern.txt) | https://github.com/notofonts/syriac · via https://github.com/google/fonts/tree/main/ofl/notosanssyriaceastern |
| Noto Naskh Arabic 2.021 | Google | Copyright 2022 The Noto Project Authors (https://github.com/notofonts/arabic) | `PxArabic-Regular.woff2` (54 kB) | [OFL-NotoNaskhArabic.txt](assets/fonts/OFL-NotoNaskhArabic.txt) | https://github.com/notofonts/arabic · via https://github.com/google/fonts/tree/main/ofl/notonaskharabic |

Licence: SIL Open Font License, Version 1.1 — https://openfontlicense.org

Notes:
* **Ponomar** is the Church Slavonic face of the Slavonic Computing Initiative (ponomar.net), designed by
  Aleksandr Andreev; Google Fonts added it on 2024-12-06. It reproduces the Synodal typeface of liturgical
  books (per the Google Fonts upstream notes).
* **Noto Sans Syriac** is the Estrangela style; **Noto Sans Syriac Western** is Serto (West Syriac) and **Noto
  Sans Syriac Eastern** is Madnhaya (East Syriac).
* **Noto Naskh Arabic** was added (not in the original design brief) because the contract's language codes
  include `ar` (Arabic in Coptic, Antiochian and Melkite use).
* **Cinzel** (display face for titles, based on classical Roman inscriptional capitals) covers Latin only; Greek in
  headings falls back to Noto Serif. Only the Bold instance is bundled; it serves all weights of the display
  face.
* Georgian (`ka`) has no bundled font; it uses the device's fonts.

### Glyph coverage of the subsets

Counts of assigned code points (Unicode 15.0.0, Python `unicodedata`) in each block, present in the original
font and kept in the subset. The subset keeps **everything** the original font has in these blocks.
Where the original font lacks characters (Syriac Supplement = Malayalam-Syriac letters; Cyrillic Extended-D =
modifier letters added in Unicode 15; most of Cyrillic Supplement = non-Slavonic minority-language letters;
Greek letters in Cinzel), the browser falls back to the device's fonts for those characters only.

| Font file | Block | Range | Assigned | In original font | In subset |
|---|---|---|---|---|---|
| PxSerif-Regular | Greek and Coptic (Greek letters) | U+0370-03FF | U+0370-03FF | 121 | 121 |
| PxSerif-Regular | Greek Extended (polytonic) | U+1F00-1FFF | U+1F00-1FFF | 233 | 233 |
| PxSerif-Regular | Latin-1 + Latin Ext-A | U+00A0-017F | U+00A0-017F | 224 | 224 |
| PxSlavonic-Regular | Cyrillic | U+0400-04FF | U+0400-04FF | 150 | 150 |
| PxSlavonic-Regular | Cyrillic Supplement | U+0500-052F | U+0500-052F | 4 | 4 |
| PxSlavonic-Regular | Cyrillic Ext-A (combining) | U+2DE0-2DFF | U+2DE0-2DFF | 29 | 29 |
| PxSlavonic-Regular | Cyrillic Ext-B | U+A640-A69F | U+A640-A69F | 48 | 48 |
| PxSlavonic-Regular | Cyrillic Ext-C | U+1C80-1C8F | U+1C80-1C8F | 9 | 9 |
| PxSlavonic-Regular | Cyrillic Ext-D | U+1E030-1E08F | U+1E030-1E08F | 0 | 0 |
| PxCoptic-Regular | Coptic | U+2C80-2CFF | U+2C80-2CFF | 123 | 123 |
| PxCoptic-Regular | Coptic letters in Greek block | U+03E2-03EF | U+03E2-03EF | 14 | 14 |
| PxCoptic-Regular | Coptic Epact Numbers | U+102E0-102FF | U+102E0-102FF | 28 | 28 |
| PxEthiopic-Regular | Ethiopic | U+1200-137F | U+1200-137F | 358 | 358 |
| PxEthiopic-Regular | Ethiopic Supplement | U+1380-139F | U+1380-139F | 26 | 26 |
| PxEthiopic-Regular | Ethiopic Extended | U+2D80-2DDF | U+2D80-2DDF | 79 | 79 |
| PxEthiopic-Regular | Ethiopic Extended-A | U+AB00-AB2F | U+AB00-AB2F | 32 | 32 |
| PxEthiopic-Regular | Ethiopic Extended-B | U+1E7E0-1E7FF | U+1E7E0-1E7FF | 28 | 28 |
| PxArmenian-Regular | Armenian | U+0530-058F | U+0530-058F | 91 | 91 |
| PxArmenian-Regular | Armenian ligatures (Alphabetic PF) | U+FB13-FB17 | U+FB13-FB17 | 5 | 5 |
| PxSyriac-Regular | Syriac | U+0700-074F | U+0700-074F | 77 | 77 |
| PxSyriac-Regular | Syriac Supplement | U+0860-086F | U+0860-086F | 0 | 0 |
| PxSyriacWestern-Regular | Syriac | U+0700-074F | U+0700-074F | 77 | 77 |
| PxSyriacWestern-Regular | Syriac Supplement | U+0860-086F | U+0860-086F | 0 | 0 |
| PxSyriacEastern-Regular | Syriac | U+0700-074F | U+0700-074F | 77 | 77 |
| PxSyriacEastern-Regular | Syriac Supplement | U+0860-086F | U+0860-086F | 0 | 0 |
| PxArabic-Regular | Arabic | U+0600-06FF | U+0600-06FF | 256 | 256 |
| PxArabic-Regular | Arabic Supplement | U+0750-077F | U+0750-077F | 48 | 48 |
| PxDisplay-Regular | Basic Latin | U+0020-007E | U+0020-007E | 95 | 95 |
| PxDisplay-Regular | Greek and Coptic | U+0370-03FF | U+0370-03FF | 4 | 4 |

## Other

* Build-time tools only (not shipped, not needed at run time): **fontTools** 4.68.0 (MIT) subsets the fonts;
  **resvg-py** 0.5.0 renders the SVG icons (its installed package metadata declares no licence; see the project's
  repository for its terms); **Pillow** 13.0.0 (MIT-CMU) writes the PNG and ICO files.
