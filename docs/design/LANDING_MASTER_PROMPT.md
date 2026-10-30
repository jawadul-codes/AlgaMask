# AlgaMask design master prompt

Paste everything below the line into another agent's brief when it builds a new AlgaMask page or screen. It describes the landing page as built in `apps/flutter/lib/src/algamask/landing_screen.dart` (source of truth if anything here drifts). Product facts live in `PRODUCT.md`.

---

You are designing a page for **AlgaMask**, a local tool that helps food R&D formulators screen spirulina and chlorella protein-bar recipes that mask algae off-notes (fishy, grassy), with every claim cited to reviewed evidence. Build the page so it feels like the same family as the AlgaMask landing page, described below. Follow it exactly; where it is silent, choose the quieter option.

## 1. The feeling

Calm, fresh, botanical, quietly scientific. A clean off-white card floating on a pale sage field, enormous confident lettering, real photographic ingredient cutouts, and soft rolling green hills along the bottom. It should read like a premium natural-food brand that happens to be rigorous: no hype, no tech costume, no dashboards-as-decoration.

## 2. Colour palette (exact values)

Flat colour only. **The page uses no gradients anywhere**: not on backgrounds, buttons, text, hills or illustrations. Depth comes from tone steps between flat layers.

| Role | Hex | Where it is used |
|---|---|---|
| Sage field (page ground) | `#BCD2C0` | Everything behind the cards |
| Paper (card surface) | `#ECEEEA` | Hero card, closing card |
| Ink (text, dark buttons) | `#0F2A1F` | Headlines, body text, nav, dark pill buttons |
| Deep forest (dark section) | `#0A2E25` | Full "What it checks" section ground |
| Forest | `#103D30` | Round badge discs |
| Green (hover) | `#176B4E` | Dark pill button hover |
| Lime (accent) | `#B8DF55` | Row titles on the dark section; white pill hover |
| Light tile | `#F7F8F4` | Small cards sitting on the hills |
| White | `#FFFFFF` | Text on hills and dark section; white pill button |
| Muted ink (rare) | `#64716D` | Secondary notes only, never running text |

Hills, back to front (flat fills, each with a grass texture of short 1px strokes in the layer's light and dark tone at 55% opacity):

| Layer | Fill | Texture tones |
|---|---|---|
| Back | `#69A042` | `#7FB24F` / `#4F8A32` |
| Middle | `#4C8632` | `#5F9A3C` / `#346D25` |
| Front | `#326C26` | `#3F7F2C` / `#23561F` |

Illustrated protein bar (flat faces): top `#5A3826`, front `#3A2216`, cut end `#2D5A35` with flecks `#3F7A46`, `#D9C79A`, `#1B3A22`, `#6F9A4A`, outline `#2A170E`, drizzle `#8A5A3C`, highlight white at 25%.

Powder dust specks: `#1F5D3A`, `#5B7A2A`, `#6B3B22`.

Proportions: sage and paper own most of the screen, green owns the bottom third of the hero, ink is for type, lime appears only on the dark section and as a hover. One accent; never introduce violet, indigo, terracotta, cream-and-rust, or neon.

## 3. Typography

- **One typeface: Urbanist** (variable, self-hosted from `apps/flutter/assets/fonts/Urbanist.ttf`, OFL). No second face, no monospace, no serif.
- **Display words**: weight 500, letter-spacing −0.04em, line-height 1.0, size ≈ 15.5% of the card width on desktop (14.5% on phone), capped at 24% of the card height. Set in capitals as short single words ("ALGAE", "MASK").
- **Section headlines**: 56px desktop / 34px phone (closing card 52 / 34), weight 500, tracking −0.03em, line-height 1.05. Sentence case, two lines maximum.
- **Row titles on dark ground**: 28px, weight 600, lime.
- **Body**: 18px, weight 400, line-height 1.55, full ink (or full white on dark/green grounds). Max ~620px measure.
- **UI text**: nav links 16px; buttons 15px weight 600; badge and card labels 16px weight 600; stage label 17px weight 600.
- **Wordmark**: "ALGAMASK", 20px, weight 700, +0.06em tracking in the nav; repeated at the very bottom of the page at full width (≈15.8% of page width, weight 600, tracking −0.04em).
- Sentence case everywhere except the display words and the wordmark. **No small tracked uppercase labels, no eyebrow/kicker text above headings, no section numbers.**

## 4. Layout and shape

- The page is a stack of **rounded cards on the sage field**: corner radius 30px desktop, 22px phone; outer gutter 28px desktop, 10px phone, equal on all sides and between cards.
- Inner padding: hero 36px (20px phone); content sections 56px horizontal and 80–88px vertical on desktop (22px / 40–44px on phone).
- Hero composition (one full viewport tall): nav row on top (two text links left, wordmark centre, dark pill right); giant "ALGAE" top-left with a one-line stage label beneath it; "MASK" right-aligned, starting at the bottom edge of "ALGAE" so the two words step down diagonally; the animated product scene fills the gap between them; hills fill the bottom 30%; two small tiles bottom-left with a round "Dataset" badge just above them; a white tagline and white pill button bottom-right on the hills; a round "Research use only" badge top-right.
- Small tiles: `#F7F8F4`, radius 14px, no border, no shadow, a 16px label and an ingredient cutout.
- Round badges: forest disc (52px with an image, 34px with an icon) followed by a two-line sentence-case label.
- Buttons are **pills only** (stadium shape), 26×16px padding. Dark pill: ink fill, white text, hover green. Light pill (on green): white fill, ink text, hover lime. One primary action per screen region.
- Content sections never become rows of identical cards. The dark section is a heading followed by rows separated by space only: title column 340px, body column to the right.
- **No borders, hairline dividers, outlined boxes, glass/blur panels, gradient blobs, emoji or icon-topped feature cards.** Shadows only on things that truly float (the illustrated bar's soft ground shadow).

## 5. Imagery

- Photographic, studio-lit, transparent-background ingredient cutouts from `apps/flutter/assets/ingredients/` (spirulina, chlorella, blend, cocoa-spice, vanilla, citrus). Use them large in scenes and small in tiles; never crop them into circles or boxes.
- When no photo exists, draw the object in flat tones from the palette (as with the protein bar), never a generic icon.
- Do not invent customers, testimonials, ratings or statistics. True facts only (e.g. "27 recipes per run", "Dataset 0.1.0-rc.5", "Research use only").

## 6. Motion

- One signature scroll moment per page, not scattered effects. On the landing page the hero pins for 1.6 viewports while scrolling drives: cocoa, vanilla and citrus fly in from beyond the card edges (0.02–0.60 of progress), merge with the two powder mounds (gather 0.18–0.62) amid swirling powder specks, fade (0.50–0.72) and resolve into the drawn bar (0.55–0.95, ease-out cubic). The stage label switches between "Spirulina + chlorella powder", "Masked with cocoa, vanilla, citrus" and "Screened protein bar".
- Progress eases toward the scroll position every frame (16% of the remaining gap), so wheel steps glide. Ease-in-out cubic for travel, ease-out cubic for arrivals; no bounce or overshoot.
- Animated pieces must stay out of the headline words: compute the free area between the text and size the scene to fit it at every width.
- Keep it cheap: images decoded at ≤512px, fades via image opacity, the animated region isolated so the rest of the page does not repaint.
- Hover feedback on every control (pill fills swap colour). Content is visible by default; motion never hides it.

## 7. Voice

Plain, specific, honest. Name what the tool does for a formulator ("Screen spirulina and chlorella bars that hide fishy, grassy off-notes, with every claim cited."). Always make clear results are computational screening that still needs bench and sensory validation. Buttons name the action ("Start screening", "Open the lab").

## 8. Checklist before you finish

- Only the colours above; zero gradients; zero borders and dividers.
- Urbanist only; display tracking −0.04em; body 18px full-ink.
- Cards on sage with 30px radius and equal gutters; pill buttons only.
- Real ingredient cutouts or flat-tone drawings; no invented proof.
- One orchestrated motion moment that never covers text, smooth on scroll.
- Works at phone width (375px) and wide desktop (1920px) without overlaps.
