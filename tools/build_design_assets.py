"""Rebuild the Sky Paschalion design assets (fonts and icons). Not needed to run the app.

    python tools/build_design_assets.py            # icons only (needs resvg-py, Pillow)
    python tools/build_design_assets.py --fonts    # also re-subset the fonts (needs fontTools, brotli and the
                                                   # original .ttf files from github.com/google/fonts in ./src_fonts/<dir>/)

Font subsets: each variable font is instanced (wght 400 or 700, wdth 100) with fontTools.varLib.instancer and
subset with fontTools.subset (all OpenType layout features and scripts kept, hinting dropped) to the code-point
ranges below, then saved as WOFF2.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

SPECS = [  # (output name, source file under src_fonts/, axis location, [(first, last) code point ranges])
    ('PxSerif-Regular', 'notoserif/NotoSerif[wdth,wght].ttf', {'wght': 400, 'wdth': 100}, [(0x20, 0x7e), (0xa0, 0x17f), (0x218, 0x21b), (0x2b0, 0x3ff), (0x1dc0, 0x1e9f), (0x1f00, 0x206f), (0x20ac, 0x20ac), (0x2116, 0x2116), (0x2122, 0x2122), (0x2190, 0x2190), (0x2192, 0x2192), (0x2212, 0x2212), (0x25cc, 0x25cc)]),
    ('PxSerif-Bold', 'notoserif/NotoSerif[wdth,wght].ttf', {'wght': 700, 'wdth': 100}, [(0x20, 0x7e), (0xa0, 0x17f), (0x218, 0x21b), (0x2b0, 0x3ff), (0x1dc0, 0x1e9f), (0x1f00, 0x206f), (0x20ac, 0x20ac), (0x2116, 0x2116), (0x2122, 0x2122), (0x2190, 0x2190), (0x2192, 0x2192), (0x2212, 0x2212), (0x25cc, 0x25cc)]),
    ('PxCoptic-Regular', 'notosanscoptic/NotoSansCoptic-Regular.ttf', None, [(0x20, 0x7e), (0xa0, 0xbf), (0x300, 0x36f), (0x3e2, 0x3ef), (0x2000, 0x206f), (0x25cc, 0x25cc), (0x2c80, 0x2cff), (0xfe20, 0xfe2f), (0xfeff, 0xfeff), (0x102e0, 0x102ff)]),
    ('PxEthiopic-Regular', 'notoserifethiopic/NotoSerifEthiopic[wdth,wght].ttf', {'wght': 400, 'wdth': 100}, [(0x20, 0x7e), (0xa0, 0xbf), (0x1200, 0x139f), (0x2000, 0x206f), (0x25cc, 0x25cc), (0x2d80, 0x2ddf), (0xab00, 0xab2f), (0xfeff, 0xfeff), (0x1e7e0, 0x1e7ff)]),
    ('PxArmenian-Regular', 'notoserifarmenian/NotoSerifArmenian[wdth,wght].ttf', {'wght': 400, 'wdth': 100}, [(0x20, 0x7e), (0xa0, 0xbf), (0x530, 0x58f), (0x2000, 0x206f), (0x25cc, 0x25cc), (0xfb13, 0xfb17), (0xfeff, 0xfeff)]),
    ('PxSyriac-Regular', 'notosanssyriac/NotoSansSyriac[wght].ttf', {'wght': 400}, [(0x20, 0x7e), (0xa0, 0xbf), (0x300, 0x36f), (0x60c, 0x60c), (0x61b, 0x61f), (0x640, 0x640), (0x64b, 0x652), (0x670, 0x670), (0x700, 0x74f), (0x860, 0x86f), (0x2000, 0x206f), (0x25cc, 0x25cc), (0xfeff, 0xfeff)]),
    ('PxSyriacEastern-Regular', 'notosanssyriaceastern/NotoSansSyriacEastern[wght].ttf', {'wght': 400}, [(0x20, 0x7e), (0xa0, 0xbf), (0x300, 0x36f), (0x60c, 0x60c), (0x61b, 0x61f), (0x640, 0x640), (0x64b, 0x652), (0x670, 0x670), (0x700, 0x74f), (0x860, 0x86f), (0x2000, 0x206f), (0x25cc, 0x25cc), (0xfeff, 0xfeff)]),
    ('PxSyriacWestern-Regular', 'notosanssyriacwestern/NotoSansSyriacWestern[wght].ttf', {'wght': 400}, [(0x20, 0x7e), (0xa0, 0xbf), (0x300, 0x36f), (0x60c, 0x60c), (0x61b, 0x61f), (0x640, 0x640), (0x64b, 0x652), (0x670, 0x670), (0x700, 0x74f), (0x860, 0x86f), (0x2000, 0x206f), (0x25cc, 0x25cc), (0xfeff, 0xfeff)]),
    ('PxSlavonic-Regular', 'ponomar/Ponomar-Regular.ttf', None, [(0x20, 0x7e), (0xa0, 0xbf), (0x300, 0x36f), (0x400, 0x52f), (0x1c80, 0x1c8f), (0x1dc0, 0x1dff), (0x2000, 0x206f), (0x25cc, 0x25cc), (0x2de0, 0x2e7f), (0xa640, 0xa69f), (0xfe20, 0xfe2f), (0xfeff, 0xfeff), (0x1e030, 0x1e08f)]),
    ('PxDisplay-Bold', 'cinzel/Cinzel[wght].ttf', {'wght': 700}, [(0x20, 0x7e), (0xa0, 0x17f), (0x218, 0x21b), (0x2b0, 0x36f), (0x1e00, 0x1e9f), (0x2000, 0x206f), (0x20ac, 0x20ac), (0x2116, 0x2116), (0x2122, 0x2122), (0x2190, 0x2190), (0x2192, 0x2192), (0x2212, 0x2212), (0x25cc, 0x25cc)]),
    ('PxArabic-Regular', 'notonaskharabic/NotoNaskhArabic[wght].ttf', {'wght': 400}, [(0x20, 0x7e), (0xa0, 0xbf), (0x600, 0x6ff), (0x750, 0x77f), (0x8a0, 0x8ff), (0x2000, 0x206f), (0x25cc, 0x25cc), (0xfb50, 0xfdff), (0xfe70, 0xfeff)]),
]


def build_fonts(src="src_fonts"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    from fontTools import subset
    for out, srcf, axes, ranges in SPECS:
        f = TTFont(os.path.join(src, srcf))
        if axes:
            f = instancer.instantiateVariableFont(f, axes)
        want = set()
        for a, b in ranges:
            want.update(range(a, b + 1))
        uni = sorted(want & set(f.getBestCmap()))
        o = subset.Options()
        o.layout_features = ["*"]; o.layout_scripts = ["*"]; o.name_IDs = ["*"]; o.name_languages = ["*"]
        o.notdef_outline = True; o.glyph_names = False; o.hinting = False; o.flavor = "woff2"
        s = subset.Subsetter(o); s.populate(unicodes=uni); s.subset(f)
        f.flavor = "woff2"
        f.save(os.path.join(HERE, "assets", "fonts", out + ".woff2"))
        print(out, len(uni), "code points")


def _png(svg, w):
    import resvg_py
    from PIL import Image
    return Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=w, height=w)))).convert("RGBA")


def build_icons():
    import ornaments as orn
    A = os.path.join(HERE, "assets")
    os.makedirs(os.path.join(A, "icons"), exist_ok=True)
    art = lambda z: orn.icon_small_svg(z) if z < 96 else orn.chi_rho_svg(z)
    with open(os.path.join(A, "paschalion_emblem.svg"), "w", encoding="utf-8") as fh:
        fh.write(orn.emblem_svg(512))
    with open(os.path.join(A, "icons", "favicon.svg"), "w", encoding="utf-8") as fh:
        fh.write(orn.icon_small_svg(32))
    for name, svg, w in (("apple-touch-icon.png", art(180), 180), ("icon-180.png", art(180), 180),
                         ("icon-192.png", art(192), 192), ("icon-512.png", art(512), 512),
                         ("icon-maskable-512.png", orn.chi_rho_svg(512, maskable=True), 512),
                         ("favicon-32.png", art(32), 32), ("favicon-16.png", art(16), 16)):
        _png(svg, w).save(os.path.join(A, "icons", name), optimize=True)
    _png(art(512), 512).save(os.path.join(A, "paschalion_icon.png"), optimize=True)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    imgs = [_png(art(z), z) for z in sizes]     # each size drawn for its size (no downscaling)
    imgs[-1].save(os.path.join(A, "paschalion_icon.ico"), format="ICO", sizes=[(z, z) for z in sizes],
                  append_images=imgs[:-1])
    print("icons written to", A)


if __name__ == "__main__":
    if "--fonts" in sys.argv:
        build_fonts()
    build_icons()
