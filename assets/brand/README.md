# NinjaApps brand assets

Standalone exports of the two marks that live inline in the site: the studio
seal (`.studio-seal` in `index.html`) and the wordmark (`.wordmark`, `忍 NinjaApps`).

All files have a transparent background. The SVGs carry the letterforms as
outlines, so nothing here depends on a font being installed or loaded.

| File | Use |
| --- | --- |
| `ninjaapps-seal.svg` | Seal, light theme — vermillion `#c73e26`, paper `#f6f2e9` knock-out |
| `ninjaapps-seal-1024.png`, `-512`, `-256` | Same seal as raster |
| `ninjaapps-seal-dark.svg`, `-dark-1024.png` | Seal, dark theme — `#e05a40` on `#181512` knock-out |
| `ninjaapps-wordmark.svg`, `-2792.png` | Wordmark in ink `#1d1a16`, for light backgrounds |
| `ninjaapps-wordmark-light.svg`, `-light-2792.png` | Wordmark in `#f0e9db`, for dark backgrounds |
| `ninjaapps-avatar.svg`, `-1024/-512/-256.png` | Social avatar — full-bleed, opaque. **Upload this one.** |
| `ninjaapps-avatar-circle.svg`, `-circle-1024/-512/-256.png` | Free-standing round mark, transparent outside the disc |

## Avatars

The two avatar files differ in a way that matters at upload time.

`ninjaapps-avatar.png` is a full-bleed opaque square: the vermillion runs to
all four edges and there is no alpha channel. Every platform crops an avatar
itself — a circle on X and Mastodon, a rounded square on LinkedIn and GitHub —
and this survives either crop, because the ring sits inside the inscribed
circle. Use it as the default. A transparent avatar is the usual mistake here:
platforms flatten alpha against a background you don't control, so the
knocked-out corners come back as black or white.

`ninjaapps-avatar-circle.png` is transparent outside the disc. It is for places
that composite a round mark over your own layout — a site header, a slide, a
README badge — not for an avatar upload field, where its own soft edge would be
cropped a second time.

The avatar is not the seal: the seal's rounded-square frame and its corners
would be eaten by a circular crop, so the avatar uses a circular ring and a
slightly smaller glyph.

Notes:

- The seal is exported upright. The `rotate(-2.5deg)` on the homepage is page
  styling, not part of the mark.
- Wordmark spacing is advance widths plus the site's `.04em` tracking; GPOS
  kerning is not applied.

## Regenerating

`generate.py` rebuilds every SVG from the self-hosted Shippori Mincho 700
subsets in `assets/fonts/`. It needs `fonttools`:

```sh
python3 assets/brand/generate.py
```

The 1024px PNGs are screenshots of those SVGs, rendered with a transparent canvas
(smaller sizes are `sips -Z` downscales of them):

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --hide-scrollbars \
  --default-background-color=00000000 \
  --force-device-scale-factor=4 --window-size=256,256 \
  --screenshot=out.png "file://$PWD/page.html"
```

where `page.html` is a bare page holding `<img src="ninjaapps-seal.svg">` at the
target CSS size with `margin: 0` and a transparent body.
