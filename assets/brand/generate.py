from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
import os

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
OUT = os.path.dirname(os.path.abspath(__file__))

jp = TTFont(os.path.join(F, "shippori-mincho-700-jp-74e8a6b5.woff2"))
lat = TTFont(os.path.join(F, "shippori-mincho-700-latin-531c46b3.woff2"))

def text_path(font, text, size, x, y, letter_spacing=0.0, center=False):
    """Return (svg path d, advance width in px). Baseline at y, start pen at x."""
    upem = font["head"].unitsPerEm
    scale = size / upem
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    hmtx = font["hmtx"]
    names = [cmap[ord(c)] for c in text]
    adv = sum(hmtx[n][0] * scale for n in names) + letter_spacing * (len(names) - 1)
    pen_x = x - adv / 2 if center else x
    d = []
    for n in names:
        spen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}")
        tpen = TransformPen(spen, Transform(scale, 0, 0, -scale, pen_x, y))
        gs[n].draw(tpen)
        seg = spen.getCommands()
        if seg:
            d.append(seg)
        pen_x += hmtx[n][0] * scale + letter_spacing
    return " ".join(d), adv

# ---------- 1. Studio seal (180x180, matches .studio-seal) ----------
glyph_d, _ = text_path(jp, "忍", 116, 90, 132, center=True)
BG_LIGHT = "#f6f2e9"
BG_DARK = "#181512"

def seal(accent, knock, ring_op=0.4):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 180" width="180" height="180" role="img" aria-label="NinjaApps studio seal">
  <rect x="4" y="4" width="172" height="172" rx="26" fill="{accent}"/>
  <rect x="14" y="14" width="152" height="152" rx="18" fill="none" stroke="{knock}" stroke-opacity="{ring_op}" stroke-width="2"/>
  <path d="{glyph_d}" fill="{knock}"/>
</svg>
'''

open(f"{OUT}/ninjaapps-seal.svg", "w").write(seal("#c73e26", BG_LIGHT))
open(f"{OUT}/ninjaapps-seal-dark.svg", "w").write(seal("#e05a40", BG_DARK))

# ---------- 2. Wordmark: 忍 NinjaApps (700 20px Shippori Mincho, ls .04em) ----------
SIZE = 200.0
LS = 0.04 * SIZE
kanji_d, kanji_adv = text_path(jp, "忍", SIZE, 0, 0, LS)
space = SIZE * 0.25  # word space between 忍 and Latin
lat_x = kanji_adv + LS + space
latin_d, latin_adv = text_path(lat, "NinjaApps", SIZE, lat_x, 0, LS)
total_w = lat_x + latin_adv

# vertical extents: cap/ascender of kanji ~ upem, descender for p/j
asc = SIZE * 0.88      # visual top (kanji em box top)
desc = SIZE * 0.24     # descenders of j / p
PAD = SIZE * 0.08
vb_h = asc + desc + 2 * PAD
vb_w = total_w + 2 * PAD

def wordmark(ink):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w:.2f} {vb_h:.2f}" width="{vb_w:.0f}" height="{vb_h:.0f}" role="img" aria-label="NinjaApps">
  <g transform="translate({PAD:.2f} {PAD + asc:.2f})" fill="{ink}">
    <path d="{kanji_d}"/>
    <path d="{latin_d}"/>
  </g>
</svg>
'''

open(f"{OUT}/ninjaapps-wordmark.svg", "w").write(wordmark("#1d1a16"))
open(f"{OUT}/ninjaapps-wordmark-light.svg", "w").write(wordmark("#f0e9db"))
print("vb", round(vb_w,1), round(vb_h,1))
