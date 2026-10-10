# BROWSER-BODY-0 — plan + status log (seat: claude, J 2026-10-06 "add step 8, begin and continue until done")
Brief: `spawn-briefs/active/BROWSER-BODY-0-builder.md`. Engine branch `browser/body-0` in worktree `projects/omni-render-browser`.
Results: `projects/omni-ui/results/browser-body-0/`.

## Intel (2026-10-06, verified by command)
- All reused parts exist (net/sandbox/hit/scroll/agent/incr; omni-ui App trait). `omni-render safe` wiki page: 5/5 probes PASS, 420 ms.
- Gap 1: renderer replies markdown only, layout fixed 1280x800 (main.rs:551).
- Gap 2: omni-ui frame.rs renders app markup only (MemSource::get → None) → web needs its own page frame.
- Gap 3: omni-ui pinned engine a11e501 is 101 commits behind omni-render main 7d4d169.
- JS: jsi (Omniglyph IR) has no runtime parser (acorn/node at build time), no DOM bindings, fetch bypasses broker.

## Steps (verify command each)
1. Web app skeleton (web_app.rs; verbs open/back/forward/reload/scroll/follow/find).
   verify: `omni-ui shot results/browser-body-0/wiki.png web <wiki url>` writes a frame.
2. Fetch through broker; renderer reply = paint list (items+boxes+links) at window width (engine branch).
   verify: `omni-render safe <url>` probes 5/5 PASS + `omni-render safe --paint <url>` round-trips.
3. Links + history (scroll kept per entry). verify: scripted session via OMNI_UI_LOG ends on expected URLs.
4. Scrolling + resize. verify: median frame ms per scroll step on 3 long pages (scroll.json).
5. Find / reader / zoom. verify: find hit counts on known page; reader toggles.
6. GET forms. verify: DDG html search → results → result link opens.
7. RAM vs Firefox, 10 pages. verify: results/browser-body-0/ram.md; bar ≤ 25 %.
8. JS-0 (J 10-06, added): Rust JS→IR parser (ECMA-262, clean-room; equal IR to js2ir on corpus), DOM bindings to omni-render DOM
   (+ omniglyph `dom` laws), fetch via broker G frames, step/time budget + reader fallback.
   verify: parser IR-equality on tools corpus; omniglyph js laws hold on runtime-parsed path; a page with a JS toggle renders changed DOM;
   ram.md re-measured with JS on.
Gate: merge gate recipe (omni-render MANUAL:225) before merge to main; pin omni-ui engine to the merged commit before commit.

## Status log
- 2026-10-06 plan written.
- 2026-10-06 worktree `projects/omni-render-browser` (browser/body-0) + omni-ui built live against it (deps rustls/ring/webpki/omni-spec, mounts why/jit x86/scroll/pageproc).
- Step 2 DONE: engine `pageproc.rs` = long-lived locked-down page process (frames Y/V/H/Q/J/T/E/M/K/Z) + Broker (subresource cache) + `omni-render page <url>`; lockdown 5/5 PASS, wiki 20 fetches via broker, renderer RSS 19 MB. img_srcs/img_bytes moved main.rs → page.rs (shared). net.rs: 10 s connect timeout (gnu.org hung 135 s).
- Step 1 DONE: omni-ui `web_app.rs` + App::surface/surface_click + frame::render_app; `omni-ui shot results/browser-body-0/wiki.png web <url>`.
- Step 3 DONE: results/browser-body-0/session3.* — open, scroll 1400, follow ×3, back ×2, forward → Moscow_State_University; back ×2 → Ternary at y 1400 (scroll kept). Lazy images (width/height attrs) Moscow 6.9 s → 0.96 s.
- Step 4 DONE: scroll.jsonl — wheel 60 px median 15.1 / 12.7 / 13.8 ms; page step 33 / 17 / 23 ms (Moscow 72k px, Rust book, PEP 8); resize 1280×800 and 700×900 reflow 40–200 ms.
- Step 5 DONE: find 3 boxes + next cycles; reader = agent::reader (main/role=main/article/densest-<p> root, nav/aside/forms dropped, one-line links); zoom = font scale in renderer (page_h 8353 → 10273 at 120 %). omni-ui widgets Link <div> → <span> (closed enclosing <p>); inkcheck notes 2696 / 0 overflow.
- Step 6 DONE: session6.* — address-bar words → DDG html GET → result via meta refresh hop → Wikipedia; Wikipedia search <form method=get> → Balanced_ternary. GAP: DDG's own form is POST (GET-only v1).
- Step 7 DONE: tools/ram_bench.py → results/browser-body-0/ram.{json,md}: 10 pages, peak tree PSS omni 17–37 MB vs Firefox 156 (new profile, headless) 674–783 MB; total 211 MB vs 7,298 MB = 2.9 % (bar ≤ 25 %). Readability: pages-sheet.png — 9/10 read well; LWN: engine positioning fault (sidebar over content) → reader fallback.
- Step 8 DONE (2026-10-06/07): jsparse 345/345 IR = acorn (6/6 mutations caught), 5.3 MB/s; 29 Omniglyph js laws × 2 seeds: jsparse path = node = acorn path (58/58);
  jsdom + click events: tests/js0 page — load scripts, onclick toggle, preventDefault link, fetch via broker, timer (session8, js0-*.png);
  real pages: 0 parse errors, scripts run on 6/10; RAM with JS on: 309 MB vs Firefox 7,424 MB = 4.2 % (ram-js.md).
- Gate (on merge of main 2766d6c): agree 19,002 = main; --check-compiled (with --program) 1,042,384 identical / 0 different; --binary-gate 0 lost / 0 gained
  (prints FAIL on main too: no gain). main then moved to fc1ae42; branch merged it (6720261) — NOT re-gated (J: "finish").
  omni-render main NOT fast-forwarded: J decides. omni-ui engine pinned to browser/body-0 6720261.
