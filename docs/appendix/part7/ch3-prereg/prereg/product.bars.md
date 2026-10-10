# BROWSER-PRODUCT-0 — Omni Web as a finished browser: minimal but usable, plugin + dev friendly, intuitive (staged; J 2026-10-07)
J 10-07: "what can we do to take omnibrowser into a fully fleshed out user friendly ternery browser instead of a hacked together
search bar?" → "minimal but useable, plugin and dev friendly. user intuitive stage as one package."
Builds on: BROWSER-BODY-0 (page process, JS-0), BROWSER-FUNCTIONAL-0 (connectivity, cookie jar, page platform, a11y tree,
tabs / bookmarks / save / WebSockets — `<notes>/worker/claude/<plan>`), omni-ui MANUAL "Web app".
Direction (memory direction-pristine-browser-t25-core): the browser's goal is exact page geometry, not Chrome parity; the T25 core
lives in it as the machine's processor. Chrome of the browser = markup drawn by omni-render itself (no foreign toolkit).
Engine work on branch browser/body-0 (worktree projects/omni-render-browser); app in projects/omni-ui. Never push; J publishes.

## Design principles (J's words → field terms)
- Minimal but usable: one row of chrome (back / forward / reload / address-search / menu), tabs as a thin strip, everything else
  one keystroke or one menu away; nothing shown that is not needed for the page in front of the person.
- Plugin friendly: a documented extension surface (WebExtensions subset: content scripts, page actions, request rules), plugins
  sandboxed like pages, enabled per site.
- Dev friendly: built-in inspector (DOM tree, computed style, box geometry with the doctor's exactness view, console, network
  log), `omni-render page` CLI parity, every intent scriptable (intent socket).
- Intuitive: Firefox / Chrome keyboard and mouse conventions, discoverable menu, designed empty / error states, accessible by default.

## Steps (verify command per step)
| # | Step | Class | Verify |
|---|---|---|---|
| P1 | Design spec + clickable mockup page (layout, tab strip, address box with suggestions, menu, site badge, light / dark / high contrast) | J (reacts) | J picks a variant; spec in docs/systems/omni-ui/WEB-DESIGN.md |
| P2 | Chrome rebuilt from the spec as omni-render markup: SVG icon set (own), hover / pressed / focus states, loading bar, menu | BUILD | `omni-ui shot` per state = mockup; a11y tree complete; keyboard-only script passes |
| P3 | Address box: suggestions from history, bookmarks, open tabs (omnid sift for "find that page"), search-engine choice | BUILD | typing 3 letters of a visited title offers it first; script check |
| P4 | Built-in pages: new tab, history (searchable), downloads, settings (kept-cookie sites, JS, zoom, privacy, search engine), designed error pages (TLS / DNS / 404 / offline) | BUILD | each page has an a11y tree + shot; settings persist |
| P5 | Page interaction: text selection + copy, form fields edited in place, right-click menu (open in new tab, copy link, save image), smooth scroll, middle-click | BUILD (engine + app) | scripted selection copies the expected text; field typing shows in the page |
| P6 | Rendering fidelity for UI basics: CSS mask-image / icon fonts (Wikipedia's icons draw as black squares today), favicons | BUILD (doctor lane) | Wikipedia header icons render; doctor gate 0 lost |
| P7 | Plugin surface v1: manifest, content scripts in the page process, request rules (block / redirect), per-site enable, sandboxed | BUILD | sample plugin (dark-reader-like CSS + a tracker rule) works; cannot reach files / other sites |
| P8 | Dev tools v1: inspector panel (DOM, computed style, box + exactness view, console, network log), `F12` | BUILD | inspector shows a node's box = layout box; console shows page errors |
| P9 | Ternary features: tracker head (allow / ask / block trit per request), ternary selector matching (SEL-T0 probe), T25 core view | BUILD (probe first each) | head vs filter-list agreement; SEL-T0 matched set identical; core view live |
| P10 | Release polish: install-web.sh, .desktop default-browser option, first-run, update path | J | J installs and uses it as the daily browser for a day |

## Status log
- 2026-10-07 plan written and staged (J: "stage as one package").
- 2026-10-07 P1 started (J: "then move on to web browser design"): field grounding (Zen compact, Arc, Safari compact, qutebrowser /
  Nyxt, Chromium URL display guidelines) → spec `docs/systems/omni-ui/WEB-DESIGN.md` + clickable mockup
  `docs/systems/omni-ui/web-design/mockup.html` (3 layouts A one-row / B compact / C keyboard+palette × light / dark / high
  contrast × 7 states; ternary "site trit" = connection · cookies · trackers). Rendered BY omni-render in Omni Web (14–44 ms
  frames) → the picked variant is P2's markup. Engine findings for P2: no border-radius / box-shadow / gradients (design kept
  rectilinear, 4 px grid); font lacks ↻ ☆; inline SVG `stroke=currentColor` draws as a filled square (svg.rs); root background
  not propagated to the canvas (CSS 2.2 §14.2); Omni Web refuses file:// ("not a web link"). Seat recommends A + C as a one-key
  mode. → REJECTED by J ("opposite of what we are looking for"); remedy = PROCEDURES § When designing; redesign next.
- 2026-10-07 P1 v2 "Orbit" (vision first, PROCEDURES § When designing): `docs/systems/omni-ui/web-design/orbit.html` + spec rewritten
  `docs/systems/omni-ui/WEB-DESIGN.md` (7 principles, parts, field grounding, engine work R1–R11 measured by rendering orbit.html in
  Omni Web on engine 188e178). J 10-07 readbacks confirmed: hide toggle → bar folds left into the top-left icon after 5 s unused,
  hover springs it back; settings icon top-right; page owns the screen, features on demand. Fold verified live (touch → 640 px bar;
  3 s open; 6 s folded). Shots web-design/shots/orbit-1…8. WAITING: J reacts → P2 (R1–R11 in the engine, doctor-gated; chrome rebuilt).
- 2026-10-07 J: "design looks good, approved and continue" → Orbit APPROVED. P2 starts.

## P2 — the renderer learns Orbit (engine branch browser/body-0, worktree projects/omni-render-browser)
Probe kit: `projects/omni-ui/results/browser-product-0/paint/*.html` (one page per capability) · `paintdiff.py` = our render
(`omni-render page --png`/`omni-ui shot`) vs headless Chrome, per-pixel mean abs error + max over the feature's box.
Gate per step: layout binary-gate 0 lost + check-compiled 0 different (paint must not move boxes) · paint probe within tolerance.
| # | Step | Verify |
|---|---|---|
| A1 | display list: `Item::Box` (rounded rect, analytic AA coverage — exact geometry) for background + borders when radius / shadow / gradient present; plain boxes keep `Item::Rect` (zero cost for today's pages) | radius probe ≤ 2 % mean err vs Chrome; binary-gate 0 lost |
| A2 | `box-shadow` (outer + inset, blur, spread) — analytic Gaussian of a rounded rect (erf along one axis, integrated along the other; clean-room from the published closed form) | shadow probe within tolerance |
| A3 | gradients linear / radial / conic with stops (CSS Images 3/4) incl. on rounded boxes; tiles holding smooth paint stored lossless (RGB565 bands gradients) | gradient probe within tolerance; site-trit ring drawn |
| A4 | `backdrop-filter: blur() saturate()` — tile drawn with an apron, items below blurred (separable box ×3 ≈ Gaussian) then clipped to the box | glass probe: text behind is blurred |
| A5 | inline SVG stroke / currentColor / linecap / circle (svg.rs) | Orbit icons drawn as strokes |
| A6 | `system-ui` → the system UI face; root background → canvas; `inset`, `place-items`, `color-mix()`, `text-overflow: ellipsis` | orbit.html in Omni Web vs Chrome side by side |
| B1 | compositor: transforms 2-D/3-D (CSS Transforms 1/2) as layers, transitions + @keyframes on a frame clock (the 'k' tick), springs (cubic-bezier) | core rings turn; bar folds in Omni Web |
| C1 | the Omni Web chrome rebuilt as Orbit inside omni-ui (widget tree → markup, a11y tree from the same tree), fold + settings live | `omni-ui shot web` = orbit shots; keyboard + AT-SPI scripts pass |
- 2026-10-07 P2 A1–A6 (engine browser/body-0 121509e + next): paint.rs (Item::Box: rounded SDF coverage, erfc shadows, linear/radial/conic
  gradients, backdrop blur+saturate via apron re-raster, Rgb888 smooth tiles), canvas background, inline <svg> with CSS fill/stroke/
  currentColor in the page process, ancestor opacity on positioned boxes, grid 0fr collapse. Probes vs Chrome (paint/paintdiff.py)
  mean|Δ|: radius 0.39 · shadow 0.59 · gradient 0.08 · icons 0.12 · glass 5.07 (font only). Layout gate every step: 20,973/3,059,
  0 different, 0 lost. Dormant: patch.font_family (+11/−1 weather-gov 1331) → `font:` shorthand pages stay serif until the doctor
  lane clears it. Finding (task chip): Omni Web's page process runs WITHOUT the doctor program (no OMR_PROGRAM) → all gated
  patches off in the browser. Friction: scroll.rs had its own tile loop (glass not drawn until routed through draw_tile).
  NEXT: B1 motion — chrome animated by omni-ui per frame (spring clock re-renders the small chrome markup; core rings = SVG ellipses
  rotated per tick), then C1 (Orbit chrome in omni-ui).
- 2026-10-07 C1 CHECKPOINT (6a5f1e424) driven by J → "quite laggy". Measured: chrome click 160–700 ms = our overlay raster (glass
  blur per tile + whole-window raster); Google 1.7 s = 1.23 s CPU in jsi running ~640 KB of scripts (→ fix 2, J assigns another
  agent: JSI-PERF-2 / script cache) + ~0.5 s fetches; box load 9–13 / 8 cores (rx-chain thead-learn 3.6 cores).
  FIX 1 DONE (engine eb6db5f→next): paint_over + tile memo + per-box cached blur (half-res, full-width region) + integer loops →
  click 22–26 ms steady, panel first open 75–85 ms, steady frame median 32 ms. Probes unchanged.
- 2026-10-07 reader view in Orbit; engine merged to main a51be17 (gate: 20,973/3,059, 0 diff, 0 lost, JS 106/106, conn 13/13);
  scroll perf pass (engine 44a3402): page scroll 54–90 ms, click ~25 ms. RESTART POINT (J): handoff
  <notes>/worker/claude/OMNI-WEB-HANDOFF-2026-10-07.brief.md. Next: panel motion, reader scroll surface, merge body-0 → main.
- 2026-10-07 (after restart) panel fade (own spring, opacity only), reader view as a cached full-height surface (reader scroll
  ~50 ms, 62 chrome tiles). Found + fixed: page process read its viewport frame AFTER the prefetch exchange → every remote page
  was laid out (and its scripts run) at 64 px wide, then again at full size (pageproc serve reads V first; swept into the JS
  agent's 7643a34); OMR_PROGRAM now read before Landlock (c87630d) — measured program on/off on 5 live pages: ±0.4 mean|Δ|, not
  enabled by default. J: "merge the web browser renderer commits" → merge gate on c87630d (20,973/3,059, 0 diff, 0 lost, JS
  106/106, conn 13/13) → engine main = c87630d (incl. the JS agent's modules/attributes/no-freeze commits); omni-ui pinned c87630d.
- 2026-10-07 (seat claude, resume from handoff) site-panel cookie switch is now TERNARY: Block · Session · Keep. Engine 7fbd83b (cookie.rs
  `Jar.block` + block-sites.txt; blocked site: nothing stored, nothing sent; keeping lifts the block; unit test + conn.sh 13/13) →
  ff main (also carried the JS agent's 209a4a7, which has its own gate line) → omni-ui pinned 7fbd83b, rebuilt, installed. omni-ui:
  web_app.rs tree (3 buttons, current = "on"), `keep` verb takes keep|session|block, trit −1 when blocked; orbit.rs pills on their own row.
  Verified by script on :8771 /setcookie: session → COOKIE-OK; blocked → COOKIE-MISSING; kept → COOKIE-OK · cookies kept.
  FINDING: after ~1 s of ticks the whole chrome (bar + panels) renders as translucent GREY over a white page; Block/Keep pills and the
  small text are near-invisible (ink-3 on the washed glass) — accessibility defect, pre-existing (Settings panel too). Next: find
  why the glass washes out (idle dim? glass tint vs white backdrop) and give pills a legible off-state.
- 2026-10-07 CONTRAST FIX (omni-ui orbit.rs css): cause measured, not guessed — dark glass rgba(22,28,44,.58) over a white page is mid-grey, so
  ink-3 #6f7a94 scored 1.02:1 and ink-2 2.0:1 (light theme the mirror on a black page: ink-3 1.5:1). Fix = contrast law: glass α .88 and
  ink-2/ink-3 chosen so every text colour is ≥ 4.5:1 over the worst page (white/black/grey/red): dark ink-2 #c4ccdf 7.4 · ink-3 #a9b3cc 5.6;
  light ink-2 7.1 · ink-3 #4d5870 5.4. Shots (site panel dark, settings light): Block/Session/Keep and all small text legible. Still glass
  (blur + saturate kept); `Surfaces: solid` unchanged. Open: contrast theme untouched (already black/white/yellow).
- 2026-10-07 P3 (history): history is now PERSISTENT — `history.tsv` in `$XDG_DATA_HOME/omni-web` (one row per address, a revisit moves it to the end with its current
  title, ≤ 2000, atomic write like bookmarks); address suggestions (open tabs · bookmarks · history) therefore find a page seen in an earlier run. Verified by script:
  run 1 visited blank/index/blank → 2 rows, blank last; run 2 loaded seen=2. about:bookmarks heading "Pages this session" → "History". Still open for P3: search-engine
  choice, omnid sift ranking. Next: P4 built-in pages (new tab, searchable history, settings, designed error pages).
- 2026-10-07 P4 (error pages): a failed load is now a designed page (`error_page`, web_app.rs): class from the network layer's message — bad address / no such host /
  not answering / certificate-TLS / invalid HTTP answer / other — each with a plain title, one sentence, what to try, the address, a "Try again" link and the raw detail;
  colours follow Orbit's theme (dark / light / contrast). Not added to history. Verified by script: unknown host → "This site can't be found", refused port →
  "This site isn't answering", `ftp://` → "Not opened (not a web link)" (page unchanged); history.tsv stayed empty. Shots /tmp/claude-1000/e1-e3.png.
  FINDING (engine, paint): on a near-black page background (#05070d) a few tile-shaped squares render darker than the rest (tile memo / RGB565 smooth-tile
  quantisation of dark colours) — faint but visible on the error page; candidate for the doctor's pristine-paint lane. Still open P4: new-tab page, searchable history
  page, settings page (kept-cookie sites, JS, zoom, search engine), downloads.
