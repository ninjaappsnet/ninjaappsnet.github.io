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

The PNGs are screenshots of those SVGs, rendered with a transparent canvas:

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --hide-scrollbars \
  --default-background-color=00000000 \
  --force-device-scale-factor=4 --window-size=256,256 \
  --screenshot=out.png "file://$PWD/page.html"
```

where `page.html` is a bare page holding `<img src="ninjaapps-seal.svg">` at the
target CSS size with `margin: 0` and a transparent body.
