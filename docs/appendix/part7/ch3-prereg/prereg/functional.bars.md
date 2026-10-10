# BROWSER-FUNCTIONAL-0 — make Omni Web functional: JS · utility · connectivity · accessibility (seat: claude, J 2026-10-07)
J 10-07: "finish this today [REPAIR-CORE-HANDOFF]. focus on the webrowser. we need it to be functional. JS, utility, connectivity
and accessability. gather intel and report." + "cant we use omniglyph for the js again?"
Subject: omni-ui Web app (`projects/omni-ui/src/web_app.rs`) on engine `browser/body-0` (worktree `projects/omni-render-browser`,
pinned 6720261 in `projects/omni-ui/.engine`). Lineage: `<plan>` (steps 1–8 DONE), omni-ui MANUAL:80-96 (Gaps line),
`<plan>`, `<plan>`.
Probe kit + raw results: `projects/omni-ui/results/browser-functional-0/` (index.html = JS probe, server.py = connectivity routes,
census.sh/census.jsonl = 24 real sites through `omni-render page`).

## Intel (2026-10-07, every line measured by command this session)
### JS — engine jsi (= JS on the Omniglyph IR, `jsi.rs:1`), run-time parser jsparse, DOM jsdom
- Probe page (106 checks: language, web APIs, DOM, BOM, network, async, loading): **engine 66/106 · Chrome 106/106** (probe valid).
- Language fails: `super` (class), class fields, generators/`yield`, tagged templates, labeled `continue outer` (acts as plain
  continue → infinite loop with `for(;;)`), `Symbol.iterator` protocol, prototype method through `Object.create(new F())`,
  BigInt, WeakMap, Proxy, Reflect, typed arrays (Uint8Array/Uint32Array), `eval`, `new Function`, regex named groups + lookbehind,
  Object.freeze, Intl / toLocaleString, microtask order (sync→micro→macro), `await` on a timer promise.
- Web/DOM fails: atob/btoa, TextEncoder, URL/URLSearchParams, FormData, XMLHttpRequest (send), fetch POST, WebSocket,
  getComputedStyle, getBoundingClientRect / offsetWidth (0: scripts run before layout), template.content, customElements,
  attachShadow, history.pushState→location.hash, bare `innerWidth`, `window.onload`, MutationObserver never fires,
  dynamically inserted `<script src>` never loads.
- Passes: let/const, arrows, destructuring, spread, optional chaining, Map/Set, JSON, querySelector*, createElement/append,
  innerHTML, classList, style, dataset, events (dispatch/bubble/remove), localStorage/sessionStorage, fetch GET (json/text),
  setTimeout/setInterval/rAF/queueMicrotask, DOMContentLoaded, load listener, external/defer/inline-module scripts.
- Budget: ONE page-wide step budget (50 M): one runaway script stops every later script on the page.
- Real sites (census.jsonl, 20 rendered): top errors = jQuery fails to start (weather.gov 1.12.4 "Object is not a function",
  arstechnica 3.7.1) → every jQuery plugin after it fails; ES module imports unsupported (GitHub 8 fail, MDN, X); missing
  globals (addEventListener unqualified, atob, eval, decodeURI, Uint32Array, HTMLLinkElement, ReadableStream);
  `Symbol.iterator` set on undefined (Google/Gmail); parse errors on Next.js chunks (BBC 7) + GitHub behaviors.js.
- Perf: theguardian layout **2,924 ms JS off → 30,837 ms JS on** (same page_h 24,989): the script re-render path is 10× slower.
- Omniglyph: `omniglyph list` → 17 js laws, all CEMENTED for node AND omniir; 0 `dom.*` laws (BROWSER-BODY-0 step 8 named them).

### Connectivity — `net.rs` (119 lines, own HTTP/1.1 + rustls)
- Works: TLS 1.3/1.2 (Mozilla roots; expired / self-signed / wrong-host refused), IPv6, chunked, Content-Length, close-delimited
  plain HTTP, ≤5 redirects, keep-alive, 10 s connect / 15 s read timeouts.
- Broken: **204 / no-length 3xx on keep-alive → read_to_end waits for the 15 s timeout ×2 attempts (204: 30.4 s, then fail)**;
  over TLS a close without close_notify is an error → whole response dropped → **craigslist.org fails** (302 with no length →
  geo → www; the final URL alone loads). Any **4xx/5xx → None**: the server's error page is never shown ("Could not load …").
  6+ redirects fail (Fetch allows 20). No Accept-Encoding/Content-Encoding (gzip page → empty title). Charset ignored
  (iso-8859-1 "café" → "caf�"). No cookies (by design: net.rs:3) → no logins, consent walls, sessions. GET only (forms + fetch).
  `data:` image URIs skipped (page.rs:252,256). Request = Host + UA "omni-render/0.1" + Accept */* only.
- Not ours to fix cheaply: stackoverflow / nytimes / ebay return 403 to curl even with a Firefox UA (bot walls) — but the 403
  page should still show.

### Utility — omni-ui `web_app.rs`
- Has: address bar (URL or DDG search), back/forward/reload (scroll kept), links, find + next, reader view, text zoom 50–300 %,
  GET forms (text fields typed in the chrome), JS toggle, scroll keys, RAM 17–37 MB/page (ram.md).
- Missing (grep of shell.rs + web_app.rs: no matches): tabs, bookmarks, persisted history, downloads, clipboard / text
  selection / copy link, checkbox/radio/select editing (submit sends their defaults only, pageproc.rs:87-89), AVIF, video/audio,
  iframes (300×150 box, layout.rs:966). Key gaps: no key starts find (only `n` = next), no Ctrl+L / Ctrl+F / Alt+←/→ / F5.

### Accessibility — omni-ui `a11y.rs` (AccessKit → AT-SPI; orca installed)
- The chrome is accessible (address field, Back/Forward/Reload/Reader buttons, Status). **The page is not**: in page mode
  `tree()` (web_app.rs:321-329) adds no page nodes — a screen reader hears the toolbar and the status line only.
- Reader view (`r`) is the only accessible path: headings / paragraphs / links as widgets (agent.rs keeps img alt + aria-label).
- No keyboard path to page links or controls in page mode (no Tab focus on page content, no focus ring drawn); `follow <n>` is an
  intent-socket verb only. Engine media queries: prefers-reduced-motion = reduce, forced-colors = none, color-scheme = light.

## Plan (ordered by reach; CLOSE = existing parts, BUILD, J = decision) — each step's verify runs against the probe kit
Run: `python3 projects/omni-ui/results/browser-functional-0/server.py 8771 &` then `omni-render page http://127.0.0.1:8771/<route>`.
| # | Step | Class | Verify |
|---|---|---|---|
| C1 | net.rs framing per RFC 9112 §6.3: no body for 1xx/204/304; no-length response on keep-alive = close-delimited; TLS EOF without close_notify = end of body | BUILD | `/204` < 1 s; `https://www.craigslist.org/` renders |
| C2 | 4xx/5xx: keep status + body; render the server's page, status line shows the code | BUILD | `/404` title NOTFOUND-PAGE |
| C3 | Accept-Encoding gzip/deflate/br + decode (flate2/brotli already in the tree for WOFF) ; redirects ≤ 20 ; Accept-Language | BUILD | `/gzip` GZIP-OK, `/redirect/7` REDIRECT-OK, wiki bytes drop |
| C4 | charset: HTTP header → BOM → `<meta charset>`; latin-1/windows-1252 at least | BUILD | `/latin1` title café-LATIN1 |
| C5 | data: URIs (RFC 2397) for img/CSS | BUILD | data-URI png renders |
| C6 | Cookie jar (RFC 6265: first-party only, memory by default, opt-in persist per site) | J (privacy stance, net.rs:3) | `/setcookie` → COOKIE-OK |
| C7 | POST forms (urlencoded) + fetch/XHR POST | BUILD (after C6 for logins) | `/postform` → POSTED q=hello; DDG native form |
| J1 | **Omniglyph route (J 10-07)**: each failing probe → a `js` law (node = oracle, omniir must agree) PROPOSED in `axioms/js.json`; debug on a scratch ledger; grow jsi until each CEMENTS. Language first: super, generators, tagged templates, labeled continue, iterator protocol, Object.create proto lookup, microtask order, await, WeakMap/Proxy/Reflect, typed arrays, eval/new Function, regex named groups/lookbehind | BUILD | `omniglyph test --lang omniir --domain js` all CEMENTED; probe ≥ 90/106 |
| J2 | `dom.*` laws (step 8's unbuilt half): jsdom vs Chrome on the probe's DOM/BOM checks; add atob/btoa, TextEncoder, URL, FormData, XHR, bare window globals, HTML*Element ctors, history.pushState, getComputedStyle, layout boxes before scripts read them, MutationObserver, onload, dynamic `<script src>` | BUILD | probe 106/106 vs Chrome |
| J3 | jQuery starts: 1.12.4 + 3.7.1 load, `$(sel).addClass` works | BUILD | weather.gov + arstechnica jQuery errors 0 in census |
| J4 | per-script step budget (a runaway script cannot stop the rest) | BUILD | probe with `for(;;)` script: later scripts still run |
| J5 | ES module scripts: static imports fetched through the broker | BUILD | GitHub/MDN "module imports not supported" 0 |
| J6 | JS re-render perf: find why the serialized live tree lays out 10× slower | BUILD | theguardian JS-on layout within 2× of JS-off |
| A1 | Page a11y tree: page process exports headings / links / lists / landmarks / img alt / form controls / ARIA role+label with layout bounds; omni-ui mounts them under a Document node | BUILD | AT-SPI dump (gi Atspi) on wiki: Link nodes = meta.links, headings present; orca reads headings |
| A2 | Keyboard: Tab / Shift-Tab through page links + fields with a drawn focus ring, Enter follows/edits; Ctrl+L, Ctrl+F, Alt+←/→, F5 | BUILD | scripted key session ends on the expected URL |
| U1 | Tabs (several page processes), bookmarks + persisted history, downloads for non-HTML (ask first), copy text/link | BUILD | scripted session: 3 tabs, bookmark, reopen |
| U2 | checkbox / radio / select editing in forms | BUILD | probe form submits the chosen values |
Gate before merge to omni-render main: MANUAL:225 merge recipe (agree count, --check-compiled, --binary-gate 0 lost); then re-pin omni-ui.
REPAIR-CORE-HANDOFF §3 (#1 table-width donor study … #6) stays parked behind this list unless J reorders.

## Status log
- 2026-10-07 intel gathered (above); plan written; nothing built yet.
- 2026-10-07 J: "yes add the cookie jar, begin and continue until done".
- C1–C7 DONE (engine e349ed6 on browser/body-0; omni-ui pinned to it): `conn.sh` 13/13 PASS (204 30.4 s → 0.04 s; 404/500 pages
  shown; gzip; 7 redirects; latin-1 café; cookies; JS document.cookie = "srv=2; js=1" with HttpOnly hidden; pdf → save page);
  craigslist renders; neverssl 15.6 → 4.2 s; cargo test cookie::/net::/page::tests 3/3. App script: POST form → "POSTED q=hi+there";
  "HTTP 404 ·" status; Save → Downloads (no overwrite); expired cert → "Could not load …: certificate expired". Jar persistence
  (XDG_DATA_HOME scratch): keep → persistent cookie survives restart, session cookie does not, un-keep empties the file.
  Checkbox / radio / select (click cycles options) values ride the submit; password fields drawn + exposed as dots.
- J1 (Omniglyph route, J 10-07): 42 new js laws in axioms/js.json (node holds all 42 for a = 0…39); bin/omniglyph takes
  OMNIGLYPH_LEDGER (scratch) + OMNIIR_BIN (branch build). Baseline omniir 23/59. Language work delegated to a subagent on
  branch browser/js-lang (worktree projects/omni-render-jslang) — files jsi*.rs / jsparse.rs only. Found + sent to it:
  crypto.randomUUID wrote the step counter (theguardian "step limit" after 1.4 ms).
- J2/J4/J6 page platform DONE (engine dbc1085): scripts after first layout, per-script step slice, §8.1.3 order, inserted
  scripts + load/error, currentScript, onload, XHR, FormData, MutationObserver, Resize/IntersectionObserver, 50 interface
  objects + prototype lookup, customElements, getComputedStyle from the cascade, template.content (dom.rs packs contents after
  the document; yardstick agree 14,941 / 2,894 unchanged), attachShadow, pushState/hash. Probe 66 → 79/106; census 24/24
  render; theguardian 32 s → 6.7 s (the 30.8 s layout no longer reproduces: page changed / JS dies early — recheck after J1).
  Form events (engine 'I' frame): page scripts see typed values + submit (JS search boxes work).
- A1/A2 DONE (engine cc8931c/7195651; omni-ui 0bd95bac6): page a11y tree (W frame, HTML-AAM + accname) under an AccessKit
  Document node; AT click/focus/set-value; Tab focus ring through page controls; keyboard-only form → POSTED nm=Ada&agree=on&c=b.
- U1 DONE (omni-ui ae68b1e0b): tabs (≤ 3 live page processes), bookmarks (Ctrl+D, saved), about:bookmarks + session history,
  copy link, Ctrl+F find field, Ctrl+L, Alt+←/→, F5.
- 2026-10-07 live pages + WebSockets: 'k' tick (10 Hz while timers wait; re-layouts ≤ 1 per max(1 s, 5 × layout)), RFC 6455
  client owned by the broker ('w' frame) — ws_echo.py: open → message → echo → close 1000. Found + sent: setInterval period
  decay, for-init `var` leaking into the caller (law js.scope.var_in_for_is_function_local).
- 2026-10-07 J1 DONE (subagent, browser/js-lang 201c01e…5519c95, merged into browser/body-0): Omniglyph js 60/60 on omniir
  (was 23/59); jQuery / React / lodash / Babel / terser … = node 18. After merge: jsdom stand-ins removed, ES modules through
  Interp::module_loader, createHTMLDocument / NodeList / initEvent / getContext / Image / PromiseRejectionEvent. JS probe
  **106/106 = Chrome**; jQuery 3.7.1 from its CDN works; census 402 ran / 39 failed (morning 148 / 69); yardstick agree
  14,941 / 2,894 unchanged; conn.sh 13/13. Parallel preload ('g' frame): x.com 488 sequential fetches → 64.
- STALL 04:45–09:08: a kernel-bash `cargo build | grep | head` blocked; the tool ignores timeout_s. Fix in fleet-ops memory:
  `timeout` inside the command / file output / run_in_background.
- omni-ui pinned to abc324b, keyboard form / WS / JS form / connectivity scripts pass, Omni Web re-installed (= new build).
- NEXT: GitHub's webpack chunk loader resolves ~250 chunk URLs against the page path (404s, ~30 s) — publicPath from
  currentScript / import.meta.url; weather.gov jQuery 1.12 still fails; renderer RSS 230–270 MB on x.com / GitHub (no GC:
  jsi Rc cycles); binary WebSocket send; BROWSER-PRODUCT-0 staged for the product layer.

- 2026-10-07 17:4x intel pass (new seat, J: "gather intel … follow procedures" → control-center/governance/PROCEDURES.md):
  board row was MISSING → staged via fleet-ratify (dispatch.db), area claimed (bin/claim). Engine browser/body-0 HEAD abc324b =
  omni-ui pin (`projects/omni-ui/.engine/REV`); 28 commits ahead of main, 57 behind; `git merge-tree body-0 main` → ONE conflict,
  src/layout.rs (main's doctor/T25 work). JSI-PERF-1 (f607d66) already in body-0; JSI-PERF-2 (re_of cache) staged.
  Worktree dirty: untracked omr.program.sets.json only. BROWSER-PRODUCT-0 staged (P1 = J design pick).
  Open (from NEXT): (1) GitHub webpack publicPath → ~250 chunk 404s; (2) weather.gov jQuery 1.12; (3) renderer RSS 230–270 MB,
  no GC for jsi Rc cycles; (4) binary WebSocket send; (5) merge body-0 → main via MANUAL:225 recipe (layout.rs conflict), re-pin.
  Friction: control-center/governance/dispatch.db is a 0-byte decoy (authority = control-center/dispatch.db); no sqlite3 CLI
  (use python3 sqlite3); `claim claim --path projects/omni-render-browser` recorded prefix /projects (too broad, advisory overlap);
  fleet-ratify needs verify-then-mark read first even for `staged` (procedure-gate).

## Merge main → browser/body-0 → main (J 10-07 "do up to engine branch") — recipe omni-render MANUAL:231
| # | Step | Verify |
|---|---|---|
| M1 | `git merge --no-ff main` in projects/omni-render-browser; layout.rs conflict = both sides added one Layout field (pad_cb from main, inl_pending from body-0) → keep both | 0 conflict markers; `cargo build --release` exit 0 |
| M2 | doctor gates on the merged build: `core corpus --program results/omr.program.json --max 0` (= main's baseline) · `--check-compiled` 0 different · `--binary-gate` 0 lost | counts read line by line vs main 23fd198 |
| M3 | browser gates: JS probe 106/106 · conn.sh 13/13 · census ≤ 39 failed | same or better than abc324b |
| M4 | commit merge; fast-forward main (worktree projects/omni-render) to it; re-pin omni-ui `.engine/REV`; rebuild + reinstall Omni Web | main == body-0; `omni-ui shot web` renders |
- 2026-10-07 M1–M4 DONE: merge 188e178 (main → browser/body-0, layout.rs field union) gated under tw (merge-gate.20261007-1031):
  baseline 20,973 / 3,059 = main · check-compiled 2,866,688 identical / 0 different · binary-gate lost 0/0 (gained 0/0 → "FAIL" by the
  gate's gained>0 rule, expected for a pure merge) · JS probe 106/106 · conn.sh 13/13. main fast-forwarded 23fd198 → 188e178 (the
  main worktree's 78 uncommitted files of another seat untouched, 0 overlap). omni-ui re-pinned 188e178; omni-ui main.rs mounts
  jit/ir.rs + jit/t25.rs (Layout::run now fires the T25 doctor core); Omni Web rebuilt + reinstalled, wiki renders as before.
  Friction: ran the gate beside school-t25 (capped CPUQuota 300 %, Nice 19) instead of waiting; first ui-build script piped cargo
  through grep, so a compile error still installed the old binary — script now stops on error.
- 2026-10-07 PM: element.attributes (weather.gov jQuery 1.12 runs, 3037e6c); module referrer = the defining module + import maps
  (GitHub 34 s → 8.5 s, 404s 250 → 0, 7643a34); YouTube measured (15.6 s parse of 10.8 MB, 2.2 GB RSS, createTreeWalker
  missing); no-freeze: first layout before scripts, async page tick (engine c87630d, omni-ui f94411074) — not yet seen in a live
  window; installed Omni Web still the 13:43 build (app was open). Handoff: BROWSER-FUNCTIONAL-0.handoff.md.


- 2026-10-07 21:xx YouTube pass (seat resumed from handoff; engine browser/body-0 209a4a7 → 4b10e98, not yet re-pinned in omni-ui / not reinstalled):
  measured kevlar_base (10.8 MB): parse 2.0 s + lower 1.8 s, 1.9 GB RSS = the serde_json estree tree (no gain from one-walk func flags 4→1).
  Fixed one blocker at a time (OMR_BLAME=1 now names the null/undefined expression + call stack — new, jsi.rs): createTreeWalker/NodeIterator/NodeFilter,
  MessageChannel, ErrorEvent, HTMLUnknownElement, CustomElementRegistry, CDATASection/ProcessingInstruction, Window (+window inherits it),
  UI-event prototypes, Range/Selection, Wheel/Drag/Touch/MessageEvent, DOMException, DOMRect, CSS.escape, interface shells, and
  Array(n) holes (F_HOLES: map/forEach/filter/some/every skip them; `Array(3).concat(..).map(f)` = d3-scale-chromatic).
  Result: YouTube scripts 41 ran / 2 failed → 43 / 0, page still the skeleton (39 pending, 497 nodes, 14 s JS, 2.2 GB RSS). Gates: probe 106/106, conn 13/13, js laws all pass.
  NEXT: (1) why the app never draws after scripts run (pending 39: promises/timers/custom-element upgrades; trace with OMR_TRACE) ; (2) memory: lower per function at parse time
  (placeholder J node + side table of Rc<Func>, flags carried) so the 1.9 GB tree is never whole; (3) cache parsed scripts per URL; (4) re-pin omni-ui, rebuild, reinstall, J opens YouTube.
  Friction: kernel bash `pkill -f` matched its own shell (exit -15); `page` takes http(s) only (serve probes with python http.server); a11y text truncates at 80 chars (use document.title → meta).

## PARSE-DOCK (J 10-07 via <home>/Downloads/Parse.txt: parser in the T25 outer-ring/dock tier, feed the renderer ready functions)
Probes (YouTube load, `OMR_FNSTAT=1 omni-render page …` and `OMR_TIME=1 omni-render js-src kb.js --script`, engine 4b10e98+probe edits):
 · functions lowered 47,430 / ever called 1,925 = **4.1 %**  → gated (lower-on-first-call) firing can skip ~96 % of lowering
 · parse tree 2,425,380 object nodes, 794,017 distinct subtrees → **67.3 % of nodes repeat an earlier identical subtree** (content-hash)
| # | Step (CLOSE = existing parts, BUILD = new) | Verify |
|---|---|---|
| P1 | BUILD arena AST: parser emits hash-consed nodes (u32 ids, content hash = the address; ring/CRT residues of it are the index view) instead of serde Values; jsi_ast reads the arena | `js-parse --parity` same JSON as before; probe 106/106; js laws pass; `/usr/bin/time -v js-src kb.js` RSS ≪ 1.9 GB |
| P2 | BUILD lazy lowering: Func keeps its arena node id, body lowered on first call | `OMR_FNSTAT`: lowering time ∝ called share; same results |
| P3 | CLOSE dock feed: broker (outside sandbox) parses in parallel at fetch (extend the 'g' preload frame), sends the arena blob; disk cache keyed by content hash | second visit parse 0 ms; census-4 ran ≥ census-3 |
| P4 | re-pin omni-ui, rebuild, reinstall; J opens YouTube | window live, RSS fraction of 2.2 GB |
Reader for the arena + cache is in the same phase (P1/P3) — no store without its reader.

- 2026-10-07 PM PARSE-DOCK P1–P4 DONE (engine 1771b3a, 71d0825; omni-ui pin 71d0825 + jscomp mount; Omni Web reinstalled, cmp OK):
  P1+P2 jscomp.rs: finished function nodes → hash-consed stored nodes behind placeholders {type,id,$t,fl,fx,np,ss}; jsi_ast Func.b() lowers on first call.
  kevlar_base parse RSS 1.93 GB → 0.86 GB; YouTube renderer 2.2 GB → 0.92 GB; 30.9k functions made, 2.6k lowered (≈8 %), 2.2k called.
  P3: broker parses scripts ≥ 24 KB on a background thread (512 MB stack), blob cached ~/.cache/omni-web/js/<fxhash(bytes)>.omj, renderer 'c' frame
  (B blob | W wait | N parse yourself); 15.8 MB blob loads in 1.2 s (load avg 18). Gates: js-parse --parity 345/345, --feedcheck 345/345 exact, probe 106/106,
  conn 13/13, js laws 0 non-pass, omni-ui story script on real sites. Timings under load 12–18 (school training) are inflated; use ratios.
  NEXT: YouTube still shows the skeleton: 3.8 M interpreter steps ≈ 12 s of JS after parse is now the cost → JSI-PERF (re_of cache, step cost) and the
  39 pending tasks (why the app never draws). Not done: prefetch-time compile start (renderer asks at script time, so first visit parses at that moment).
  Friction: omni-ui mounts engine modules by #[path] — a new engine module needs a mod line there (22 errors until added); 'J' frame tag already taken, used 'c'.

- 2026-10-07 17:30 PDT staged from J's compiler question (after PARSE-DOCK P1–P4): `JS-COMPILE-0.brief.md` (compiler: C1 slot scopes … C7 laws) and `OMNIGLYPH-INTERP-0.brief.md` (laws + ring dispatch probe + operator core emitted from the IR). They take over the NEXT item "interpreter speed = slot-resolved scopes" from the handoff update.
