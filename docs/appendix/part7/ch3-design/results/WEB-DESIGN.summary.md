# Omni Web — design: "Orbit" (BROWSER-PRODUCT-0 P1, J 2026-10-07)
**What we are making (J 10-07):** not a regular browser — the next development in lightweight modern browsers, of a new era:
modern futuristic aesthetic, fluid, user-intuitive, highly accessible, capable, lightweight, ternary. Drawn by our own renderer
(omni-render); the design leads and the renderer learns what the design calls for (PROCEDURES § When designing).

Vision mockup: `docs/systems/omni-ui/web-design/orbit.html` (live: serve the folder, open `orbit.html#<state>,<theme>,<flags>`,
e.g. `#browse,dark,folded`, `#settings,contrast`). Shots: `web-design/shots/orbit-*.png` (1280×800, Chrome, as the target look).

## Principles (J 10-07)
1. **The page owns the screen.** At rest the chrome is two corner icons: the core (top-left) and settings (top-right).
2. **Features at the ready, taking no space.** Everything appears the moment it is called (touch, key, gesture) and folds away
   after use. No resident taskbars or ribbons.
3. **Fluid.** Every change is motion with meaning: springs, slides, unfolds; Still mode turns motion off.
4. **Seamless.** One surface does address, search, history, tabs and every intent; panels grow out of the icon that called them.
5. **Accessible as infrastructure.** Contrast held on any page (Solid surfaces, Contrast theme), full keyboard, screen-reader
   names on every control, reduced-motion honoured, focus shown as a glow.
6. **Ternary.** State is shown and set as trits: + allow / 0 ask or session / − block; switches are three-position.
7. **Lightweight.** The whole chrome = one 29 KB document (markup + style + script) drawn by our renderer.

## Parts
| Part | Behaviour |
|---|---|
| **Bar** (top ribbon, glass capsule) | core · back · forward · site trit + address · reload · reader. Click the address → the bar unfolds into the command sheet |
| **Fold** (J 10-07) | Settings → *Hide bar* on: after 5 s with no pointer or focus on the bar, it slides left and condenses into the core icon top-left; the tab rail folds with it. Touch the icon with the cursor (hover) or focus it → the bar springs back; the 5 s count restarts when you leave it. Hide off → the bar stays |
| **Core icon** | three rings turning at their own rhythm (3 / 5 / 7 s) on their own axes — the browser's core; spins faster while a page loads |
| **Settings** (top-right icon, J 10-07) | panel on demand: Hide bar · Theme (Dark / Light / Contrast) · Surfaces (Glass / Solid) · Motion (Fluid / Still) · Scripts, Cookies, Trackers defaults as ternary switches. Ctrl+, |
| **Command sheet** | Ctrl+L / F6 / click: one list — open tabs, recalled pages (history + bookmarks, by meaning via omnid sift), actions with their keys, web search |
| **Site trit** | ring around the site mark, three arcs = connection · cookies · trackers; click → panel with a ternary switch per trit |
| **Tab rail** | left, orbs only (each ringed by its site trit); expands with titles on hover; Ctrl+Tab → overview of tab cards |
| **Loading** | light sweep along the bar's lower edge + core rings speed up |
| **Hover link** | small glass pill at the bottom while a link is hovered |

## Field grounding (2026-10-07; platform, not ceiling)
Apple Liquid Glass (translucency, depth, motion; content first) and NN/g's critique of its contrast → our Solid surfaces +
contrast guard; Zen (compact mode, collapsible sidebar); qutebrowser / Nyxt (command palette, keyboard); Chromium URL display
guidelines (origin prominent, path dim); 2026 UI practice: accessibility as infrastructure, motion with purpose.

## Engine work the design creates (measured: orbit.html rendered by omni-render 188e178 in Omni Web, 2026-10-07)
| # | Capability | Spec | Seen in our render |
|---|---|---|---|
| R1 | `border-radius` (incl. 50 % circles, 999 px pills) | CSS Backgrounds 3 §5 | square corners everywhere |
| R2 | `box-shadow` incl. inset + glow | CSS Backgrounds 3 §7 | none |
| R3 | gradients: linear, radial, conic | CSS Images 3 / 4 | none (site trit ring missing) |
| R4 | `backdrop-filter: blur() saturate()` | Filter Effects 2 | glass shows text through, unblurred |
| R5 | transforms 2-D + 3-D + `perspective` | CSS Transforms 1 / 2 | core rings flat |
| R6 | transitions + `@keyframes` animations + `cubic-bezier` springs, on a frame clock | CSS Transitions 1, Animations 1 | no motion |
| R7 | inline SVG stroke / `currentColor` / linecap | SVG 2 painting | icons drawn as filled squares |
| R8 | generic `system-ui` font → the system UI face | CSS Fonts 4 | serif fallback |
| R9 | `inset`, `place-items`, `grid-template-rows` 0fr→1fr, `color-mix()`, `text-overflow`, `::after` positioning, `:focus-visible` | various | panels / rings misplaced |
| R10 | root background → canvas | CSS 2.2 §14.2 | white strip under short pages |
| R11 | `file://` view for local pages | — | refused ("not a web link") |
Path note: R4 + R6 are compositor work — layers drawn once and moved / blurred per frame. Our direction already puts drawing on the
GPU (WebGPU, T25 core lineage); a GPU compositor for the chrome is the natural home for R1–R6.

## Next
J reacts to Orbit → P2 = R1–R11 in the engine (doctor lane gates each: 0 lost) + the chrome rebuilt as this document inside
omni-ui (widget tree → markup, a11y tree from the same tree).

---
## Lineage: rejected first draft (2026-10-07)
`web-design/mockup.html` — flat, square, 3 layouts (one-row / compact / keyboard). J: "the opposite of what we are looking for".
Cause: the seat let the renderer's current CSS set the design → remedy PROCEDURES § When designing.
