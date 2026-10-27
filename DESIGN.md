---
name: NinjaApps
description: A NinjaApps Production. A studio frame in pure black and white, and a one-sheet in its own colours for every title.
colors:
  ink: "#000000"
  paper: "#ffffff"
  seal-red: "#d7301f"
  screen: "#000000"
  on-screen: "#ffffff"
  studio-ground: "#000000"
  smalti-ground: "#1c2337"
  smalti-gold: "#d9ab55"
  smalti-ink: "#7d2333"
  smalti-ink-dark: "#e2b866"
  dayfolio-ground: "#b0441c"
  dayfolio-paper: "#fdf3e4"
  dayfolio-ink: "#9a3a16"
  dayfolio-ink-dark: "#f4a27c"
  flectobi-ground: "#06454c"
  flectobi-mint: "#66d4c8"
  flectobi-ink: "#0b5f66"
typography:
  title-poster:
    fontFamily: "Archivo, -apple-system, system-ui, sans-serif"
    fontSize: "clamp(76px, 15vw, 228px)"
    fontWeight: 900
    lineHeight: 0.8
    letterSpacing: "-0.055em"
    fontVariation: "wdth 125"
  title-sheet:
    fontFamily: "Archivo, -apple-system, system-ui, sans-serif"
    fontSize: "clamp(48px, 5.4vw, 84px)"
    fontWeight: 900
    lineHeight: 0.9
    letterSpacing: "-0.045em"
    fontVariation: "wdth 118"
  page-title:
    fontFamily: "Archivo, -apple-system, system-ui, sans-serif"
    fontSize: "clamp(40px, 6vw, 76px)"
    fontWeight: 900
    lineHeight: 0.96
    letterSpacing: "-0.045em"
    fontVariation: "wdth 112"
  group-title:
    fontFamily: "Archivo, -apple-system, system-ui, sans-serif"
    fontSize: "clamp(30px, 3.6vw, 48px)"
    fontWeight: 850
    lineHeight: 1.02
    letterSpacing: "-0.03em"
    fontVariation: "wdth 108"
  heading:
    fontFamily: "Archivo, -apple-system, system-ui, sans-serif"
    fontSize: "clamp(24px, 2.4vw, 30px)"
    fontWeight: 800
    lineHeight: 1.12
    letterSpacing: "-0.02em"
    fontVariation: "wdth 100"
  billing:
    fontFamily: "Archivo, -apple-system, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 650
    lineHeight: 1.5
    letterSpacing: "0.02em"
    fontVariation: "wdth 68"
  action:
    fontFamily: "Archivo, -apple-system, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "0.03em"
    fontVariation: "wdth 75"
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, system-ui, 'Segoe UI', 'Helvetica Neue', sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.6
  code:
    fontFamily: "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
    fontSize: "0.84em"
    fontWeight: 400
rounded:
  code: "4px"
  pre: "6px"
  window: "12px"
  phone: "30px"
  app-icon-sm: "6px"
spacing:
  gutter: "clamp(16px, 4vw, 56px)"
  max: "1280px"
  measure: "68ch"
  sheet-pad: "20px"
  group: "clamp(56px, 7vw, 96px)"
components:
  ticket:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.action}"
    padding: "17px 58px 16px 26px"
  ticket-on-sheet:
    backgroundColor: "{colors.smalti-gold}"
    textColor: "{colors.smalti-ground}"
  ticket-soon:
    textColor: "{colors.ink}"
    typography: "{typography.action}"
    padding: "15px 22px"
  sheet:
    backgroundColor: "{colors.smalti-ground}"
    textColor: "{colors.paper}"
    padding: "18px 20px 20px"
  onesheet:
    backgroundColor: "{colors.flectobi-ground}"
    textColor: "{colors.paper}"
    padding: "18px 56px 22px"
  subnav:
    backgroundColor: "{colors.dayfolio-ground}"
    textColor: "{colors.paper}"
    padding: "12px 56px"
  appbox:
    backgroundColor: "{colors.dayfolio-ground}"
    textColor: "{colors.paper}"
    padding: "24px"
  credits:
    backgroundColor: "{colors.screen}"
    textColor: "{colors.on-screen}"
  footer:
    backgroundColor: "{colors.screen}"
    textColor: "{colors.on-screen}"
    typography: "{typography.billing}"
    padding: "28px 56px"
---

# Design System: NinjaApps

## Overview

**Creative North Star: "A NinjaApps Production"**

The studio is a production company and every app is a title it releases. One frame holds them all: pure black and pure white, a wide heavy grotesque at poster scale, and a condensed uppercase billing voice for facts. Inside that frame each title owns a one-sheet, a field of colour taken from its app icon. The studio frame never borrows those colours and the titles never borrow the studio's. The seal (忍) is the only studio colour and appears only as the ident mark.

Density is poster-like on the Persuade surfaces (home slate, app one-sheets) and plain on Read surfaces (guides, privacy, support, templates), which sit inside the same frame: black-and-white paper, hairline and heavy rules, system-face reading text, and the title's band and link ink as the one touch of its colour. Depth is conveyed by layered planes and rules, not by cards.

The system refuses the indie-studio hero over a row of equal icon cards, and the retired cream, serif, vermillion "paper dojo".

**Key Characteristics:**
- Two-tone frame, no greys; the dark theme inverts paper and ink.
- The slate, end credits, footer and 404 are black in both themes.
- Colour is per title, selected by the page's canonical URL, never by a class on hand-written or generated pages.
- Archivo variable on two axes: wide and heavy for titles, condensed for facts.
- Rows, rules and plates instead of cards and shadows; the ticket is the only App Store action.
- Production numbers NA-01 Smalti, NA-02 Dayfolio, NA-03 FlectoBI; a future web app continues the sequence.

## Colors

A two-tone frame with a single reserved red, plus three title palettes that live only inside their own one-sheets, bands and link ink.

### Primary
- **Seal Red** (`seal-red`): the 忍 seal in the header wordmark, the footer and the ident. Nothing else: not links, not buttons, not highlights.

### Secondary (title palettes)
- **Smalti Glazed Navy** (`smalti-ground`) with **Mosaic Gold** (`smalti-gold`): field and highlight. Link ink on paper is **Smalti Garnet** (`smalti-ink`); in the dark theme it becomes gold-light (`smalti-ink-dark`).
- **Dayfolio Orange Paper** (`dayfolio-ground`) with **Cream** (`dayfolio-paper`): field and highlight. Link ink `dayfolio-ink`; dark theme `dayfolio-ink-dark`.
- **FlectoBI Deep Teal** (`flectobi-ground`) with **Signal Mint** (`flectobi-mint`): field and highlight. Link ink `flectobi-ink`; in the dark theme the mint itself.

### Neutral
- **Ink** (`ink`) and **Paper** (`paper`): text, rules, borders and page; they swap in the dark theme. These are the only two neutrals.
- **Screen** (`screen`, `on-screen`): the black screen of slate, credits, footer and 404, fixed in both themes.
- **Studio Ground** (`studio-ground`): the default one-sheet field outside any title (near-black), with white highlight and ink.

Each title supplies four values: ground (`--app-ground`), type on the ground (`--app-on`, white for all three), highlight (`--app-hi`) and link ink (`--app-ink`). Components read only those four.

### Named Rules
**The No-Grey Rule.** The frame has no intermediate tones. Hierarchy comes from weight, width, size and rule thickness (1px, 3px), never from a lighter ink.
**The Seal-Only Red Rule.** Studio red marks the seal and nothing else.
**The Title Owns Its Colour Rule.** A title's colours appear on its one-sheet, its subnav band, its appbox, its link ink and its ticket. They never colour the studio frame or another title's pages.
**The Screen Rule.** The slate, credits, footer and 404 stay black under both themes.

## Typography

**Display Font:** Archivo variable (self-hosted woff2, latin and latin-ext, weight 100-900, width 62-125%), with the system sans fallback.
**Body Font:** Apple system stack (-apple-system, system-ui, Segoe UI, Helvetica Neue).
**Code Font:** ui-monospace, SF Mono, Menlo, Consolas.

**Character:** The same family plays two roles: a wide, heavy, tightly tracked poster title, and a condensed uppercase credit-block voice. Reading text drops to the system face so long pages stay plain.

### Hierarchy
- **Title poster** (900, wdth 125, clamp 76-228px, 0.8, -0.055em): one-sheet title on app pages; 404 and app-hero reuse the same.
- **Title sheet** (900, wdth 118, clamp 48-84px, 0.9, -0.045em): home slate titles. Credits line (900, wdth 112, up to 72px) and the subnav app name (900, wdth 118, 20px) are siblings.
- **Page title** (900, wdth 112, clamp 40-76px, 0.96, -0.045em): Read page h1.
- **Group title** (850, wdth 108, clamp 30-48px, -0.03em): section heads on app pages, followed by a 1px rule and a count.
- **Heading** (800, wdth 100, 24-30px, -0.02em): prose h2; h3 is 750 at 20px; listing row titles 800 at 21px.
- **Billing / label** (650, wdth 68, uppercase, +0.02em, 12.5-15px): billing blocks, facts terms, crumbs, subnav, header nav, pager labels, footer, production number. Short fact runs only.
- **Action** (ticket 800, wdth 75, 16px, +0.03em, uppercase; text actions 750, wdth 80).
- **Body** (400, 17px, 1.6, measure 68ch): prose; ledes 18-20px at 1.45.
- **Code** (400, 0.84em; blocks 14px at 1.65).

### Named Rules
**The Two Axes Rule.** Wide-and-heavy means a title; condensed-and-uppercase means a fact. A fact is never set wide, a title never condensed.
**The Own-Face Rule.** Scripts Archivo does not draw (ru, ko, zh-Hans, ja) take the system face at normal width for headings, nav and crumbs, so no line mixes two typefaces.
**The Tight Title Rule.** Titles carry negative tracking that deepens with size (-0.015em to -0.055em).

## Layout

One 1280px content max, centred through `--pad-side`, with a fluid gutter (16-56px). Home is a three-column subgrid of one-sheets sharing row lines, filling roughly the viewport (540-760px min); at 1080px it stacks to one column with art beside type, at 600px a single column. App pages: a full-bleed one-sheet with a two-column grid (title spanning, art left, logline and ticket in a 300-400px foot column), then sections on paper with `clamp(56px, 7vw, 96px)` rhythm. The poster art overlaps the title's foot by 20% of the title size. Below 860px the one-sheet is one column. Read pages are a single centred column (68ch measure plus gutters). Heavy structural rules are 3px (facts top, pager, toc, contact box), dividers 1px. Phone-screenshot rows of three become a swipe row under 860px.

## Elevation & Depth

Flat. Depth is the one-sheet's layered planes, back to front: field, title, art, type; the art is lifted off the type by 4px on hover and drifts a few percent on scroll. The only shadows are soft ones under device art on a one-sheet (`0 24px 60px -18px rgb(0 0 0 / .55)`) and drop-shadows on window screenshots in prose. No cards with shadows, no hard offset shadows.

### Named Rules
**The Planes Rule.** Separation is by plane and rule. A surface does not gain a shadow to look important.

## Shapes

Mostly square, rectilinear sheets and rules. Radius appears only where it matches a real device: phone screens 22-30px, windows 10-12px, app icons 6-15px, inline code 4px, code blocks 6px. The ticket is the one custom silhouette: semicircle punches in both sides and a dashed perforation before the arrow. The theme toggle is a drawn half-ink disc. Arrows are drawn with one stroke (2.4 in a 24 box) via mask, never glyphs.

## Components

### The Ticket
The only action that sends a visitor to the App Store. Inline stub in uppercase condensed 800; punched sides (7px radius), a dashed perforation 58px from the right, and a drawn arrow. On paper it is ink on paper; on a one-sheet or appbox it is the title's highlight on its ground. Hover (pointer only) nudges the arrow 3px; press scales to 0.97 over 160ms. Focus removes the mask and draws a 2px outline. **Ticket soon** is the unpunched form for a title not yet on the store: 2px dashed outline, same type, highlight colour on a sheet.

### Text actions
`.btn` and `.more`: condensed uppercase 750, always underlined (2px, offset 6px), drawn arrow. `.btn-quiet` is dashed and inert. These never look like the ticket.

### One-sheet (home `.sheet`, page `.onesheet`)
Ground field with a head line (production number in highlight, kind label right), art plane, poster title, logline, a 1px-ruled billing block (condensed uppercase facts, key values bold in highlight), then the ticket. Title links stretch across the sheet. Art placement is cut per title (Smalti phone tilted -4deg, Dayfolio phone straight, FlectoBI window bleeding off the edge).

### Billing and facts
Billing is a ruled run of uppercase condensed facts. `.facts` is the paper version: a 3px top rule, 1px row rules, a 9.5em condensed term column, tabular values.

### Crumbs, header, subnav
Header: seal plus wide wordmark left, uppercase condensed nav and the theme toggle right, a 1px ink rule below; black on the home page. Crumbs are condensed uppercase with a drawn dash separator. The subnav is a full-width band in the title's ground with the app icon at 26px, app name in wide 900, nav links with a 2px highlight underline on the current page.

### Listing rows, pager
Index lists are rows, not cards: a 1px top rule, an 800 21px title that underlines on hover, a short description. The pager is two text links under a 3px rule, labels in billing voice.

### Appbox
A mini one-sheet at the foot of every guide page: the title's ground, icon, name in wide 900, a line of copy, and its ticket or `.btn`.

### End credits and footer
Credits: black screen, a wide 900 closing line, and a 1px-ruled run of shared facts. Footer: black, seal plus studio line, social marks in single-colour 18px SVG, privacy link; condensed uppercase.

### Motion
- Ease tokens: `--ease-out` cubic-bezier(0.23, 1, 0.32, 1); `--ease-in-out` cubic-bezier(0.77, 0, 0.175, 1).
- Ident: each home load cuts the three sheets in with clip-path, 700ms, 70ms stagger, plus a 900ms settle of the art. It never blocks interaction.
- Title openings: each title's name is made the way the product works, on a canvas over the real heading. Smalti: glazed polyomino pieces seat into the name (the mosaic stays). Dayfolio: the name is written a ruled line per working day, dated, the last line today, then closes into type. FlectoBI: the same points as bars, a bubble map, then a 3D scatter turned in 15-degree snaps until it faces front and reads as the name. On the home page each sheet plays a short trailer once, after the ident; the 404 is a set "404" that loses a few pieces. Any click, key or scroll ends an opening; under reduced motion there is none.
- Scroll-driven art drift: `animation-timeline: view()`, translate +4% to -4%; where unsupported the planes stay still.
- Hover lift of the art plane: 4px, 240ms, pointer-fine only.
- Ticket press: scale(.97), 160ms. Page navigation: 180ms crossfade.
- Colour and underline changes use `ease`, 150-200ms.
- Reduced motion: the ident becomes a 300ms fade only; hover lift, drift, settle, smooth scroll, view transitions and ticket transitions are off.

## Do's and Don'ts

### Do:
- **Do** keep the frame to `ink` and `paper`; use rule weight and type width for hierarchy.
- **Do** give each title its four app values and let every component read them through `--app-*`.
- **Do** use the ticket for the App Store action and nothing else; use it once per one-sheet.
- **Do** set facts (platforms, price, requirements) in the condensed uppercase billing voice, short runs.
- **Do** continue the production sequence (NA-04 and on) for the next title, including a web app, with its own ground, highlight and link ink.
- **Do** keep requests on the origin and storage limited to the theme preference.
- **Do** list things as rows with rules; keep plates and appboxes as the only filled blocks on paper.

### Don't:
- **Don't** use grey, tinted paper or a second neutral in the studio frame.
- **Don't** use the seal red for anything but the seal.
- **Don't** put title colours on the studio frame or another title's pages.
- **Don't** build a row of equal app-icon cards, or a hero over one.
- **Don't** return to the cream, serif, vermillion paper-dojo look (Shippori, Zen Kaku, Plex).
- **Don't** shape any other control like the ticket.
- **Don't** add hard offset shadows or glyph icons; arrows and the theme mark are drawn.
- **Don't** let hover or colour changes exceed 200ms or use anything but ease on them.

## Not canonized

Carried by the build, not rules for new surfaces: the `sheet-kind` label above each title is a small kicker-like line (the production number is the contract; the kind line is not a pattern to extend); 10-11px, 0.14-0.16em-tracked labels in the template gallery (`.tpl-type`, `.card-from`, `.pack-count`) are legacy and below the billing scale; the legacy `.card`, `.app-hero`, `.app-icon` and `.pack` rules; the `--df-*` Dayfolio entry block (warm neutrals, serif, tinted chips) is Dayfolio's own app voice, used only inside `.entry` template examples; the social cards and banners in `assets/brand/` and the Shippori, Zen Kaku and Plex font files still carry the retired Paper Dojo look.
