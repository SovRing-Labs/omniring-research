# Omni Web: a browser whose page and chrome are both drawn by our own engine — architecture and memory

| | |
|---|---|
| **Date** | 2026-10-06 → 2026-10-07 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Prepared with AI assistance (Claude and the fleet's open-weight models). The author reviews each document before publication. |
| **Type** | design + measured result (one laptop, i5-8365U, shared with training jobs) |
| **Verdict** | Memory bar (≤ 25 % of Firefox) PASS: 2.9 % script off, 4.2 % script on; connectivity 13 / 13 PASS |
| **Code** | `harness/part7/ch3-memory/ram_bench.py`, `harness/part7/ch3-connectivity/conn.sh`, `server.py`; browser source in the omni-ui and omni-render repositories |

The author's brief, verbatim: **"modern, futuristic, fluid, intuitive, highly accessible, capable, lightweight, ternary."** The engine
underneath (packed DOM, own CSS engine, integer layout, 2-bit raster, JIT runtime, JavaScript on our IR) is Part 6; this document is what
was built on top of it. Other browsers were observed as black boxes (rendered output, DOM dump, process memory), never read.

*The record below is the full measured account from the technical disclosure's working chapters: every gate, every failure, with the
harness and result paths in this repository. "Section n" and "§n" inside it refer to the sections of that chapter; the matching documents here
are listed in the README. "Recorded; no saved result" marks a figure the project recorded whose output file is not published.*

## What is measured and what is only designed

The owner's design brief for the browser, verbatim: **modern, futuristic, fluid, intuitive, highly accessible, capable, lightweight,
ternary.** The table says, per word, what exists in this repository as a measurement and what is only a design or an implementation
without a retained measurement.

| Brief word | Implemented | Measured here (with file) | Only designed / not retained |
|---|---|---|---|
| modern, futuristic | Orbit chrome: glass bar, spring motion, fold-to-icon (section 8) | merge gates show layout unmoved by the paint work (section 12) | paint error vs Chrome and frame times were logged but their result files are not retained (the comparison script is not shipped: no output exists) (recorded; no saved result) |
| fluid | per-tick spring motion, cached blur, tile memo | none retained | click 22–26 ms, scroll 54–90 ms are log text only (recorded; no saved result) |
| intuitive | keyboard conventions, designed error pages, address suggestions | none | no test with people was recorded; "use it as the daily browser for a day" is an unrun planned step |
| highly accessible | page accessibility tree, Tab focus ring, contrast law | contrast ratios recomputable from the stated constants (section 7) | AT-SPI dumps and screen-reader sessions not retained (recorded; no saved result) |
| capable | JS platform, connectivity, cookies, forms, tabs | 13/13 connectivity routes at three gates; 24-site census ×3 runs | JS probe 106/106 on our engine: saved only for eight later gate runs of another engine worktree (section 6), not for the three browser gates (partial) |
| lightweight | no GPU process, 2 processes per page | 10-page RAM comparison with Firefox (section 4); census RSS shows it fails on script-heavy pages (section 6) | — |
| ternary | site trit, ternary cookie switch | cookie switch partly covered by one gate route | tracker head, ternary selector matching in the browser: designed only (section 9) |

## Architecture: broker, confined page processes, one tree for drawing and reading

- **Broker** (`omni-ui`, `src/web_app.rs`): owns the window, the network client, the cookie jar, the subresource cache, history, bookmarks
  and tabs. It never parses page content.
- **Page process** (`omni-ui web-renderer` = the engine's `pageproc::serve`): one per live tab, started with no_new_privs, then Landlock
  (file system) and a seccomp-BPF allow-list; it parses, styles, lays out, runs the page's scripts and rasters (`pageproc.rs`; confinement in `omni-render/src/sandbox.rs`: no_new_privs, Landlock read-only fonts with TCP denied, seccomp-BPF allow-list), and answers the broker
  over a framed pipe. The protocol is one tag byte, a 4-byte little-endian length and the payload (`omni-render/src/sandbox.rs`, `write_frame`; frames over 64 MB are refused).
  Start: broker sends `U` url, `D` document bytes, `V` viewport; the renderer answers `S` (lockdown report and probes) and `L` (meta: title, page height, links, timings).
  Requests and replies (header of `omni-render/src/pageproc.rs`, lines 1–34): `Y` scroll → `F` frame of pixels; `V` resize → `L`; `H` point → `A` what is under it;
  `Q` text → `A` boxes of matching elements (find); `J` → `A` every link in document order; `T` fragment → `A` its y; `E` → `A` text-entry controls; `M` → `R` main content as
  markdown (reader view); `K` form → `A` the request to send (GET / POST); `k` ms → `A` timers due in the elapsed real time run (`k` is the tick); `I` values → `A` input and
  change events then a cancelable submit; `Z` percent → `L` text zoom; `W` → `A` accessibility rows (role, name, parent, bounds, extra); `X` exit. At any time the renderer may send
  `G` url (a subresource, answered `B` bytes or `N` refused), `P` (script fetch / XHR), `O` (document.cookie read / write), `w` (WebSocket open / send / close / poll; the broker owns the
  socket) and `g` (preload list, ≤ 6 fetched in parallel). Two more letters named in the author's development notes, `c` (compiled-script feed, section 10) and `e` / `d` (script eval, DOM dump), and the author's manual's
  `C`, are **not** in the source tree reviewed for this section [that tree is a working tree of the engine whose revision is not recorded and which lacks the compiler modules; the meaning of `C` is stated nowhere].
  At most 3 tabs keep a live page process (`omni-ui/src/web_app.rs:168-174`); the others sleep and reload at their scroll position when shown.
- **One tree, two outputs.** The chrome is a packed widget tree (kind, verb, parent, label span, value span; 22 B per widget: kind 1 + verb 1 + parent 4 + label span 8 + value span 8, `omni-ui/src/widgets.rs:2`). The same
  tree emits (a) markup drawn by our engine, each widget an element with its own id, and (b) an AccessKit tree sent over AT-SPI. Every input
  (key, pointer, assistive technology, voice, text, switch) ends in one `act(verb, arg, source)` call, so what is drawn and what is read
  cannot disagree. The page itself joins the accessibility tree as one Document node built from the page process's rows (section 7).
- **Live pages without a busy loop:** the window's event loop wakes at the app's period only while the shown page has timers waiting
  (`ControlFlow::WaitUntil`); the page process's tick runs timers in real time; timer-driven re-layouts are paced at most one per
  max(1 s, 5 × the last layout) (`omni-render/src/pageproc.rs:197,406`). Scripts run after the first layout on an asynchronous tick, so the window shows the page first and the
  chrome stays live while scripts run.

Gate G1 (lockdown, observation): the page process runs five start-up probes (`omni-render/src/sandbox.rs::probes`: read `/etc/passwd`, write under `/tmp`, TCP connect and exec must fail; the system fonts must stay readable); "5 of 5" and "20 fetches through the
broker, renderer RSS 19 MB" are recorded in the author's working log only (not shipped) (recorded; no saved result). Failure found: a connect that never
completed held a page 135 s (gnu.org) [the 135 s is log text only]; a 10 s connect timeout per resolved address was added (`omni-render/src/net.rs:135-138, 207`, present in source). The 24-site census later shows gnu.org at 101.02 s again (section 6) — the
timeout bounds the connect, and the census row attributes 24.2 s of that run to layout, not to connecting.

FIELD PREDICTS: a broker that owns network and files while a confined process parses untrusted content is the published multi-process
browser design (Grier, Tang, King, "Secure Web Browsing with the OP Web Browser", IEEE S&P 2008; Reis & Gribble, "Isolating Web
Programs in Modern Browser Architectures", EuroSys 2009); Landlock (Linux 5.13) and seccomp-BPF (Linux 3.5) are the kernel mechanisms.

## Browsing core and memory on document pages (2026-10-06)

Harness: `omni-ui script web --script <file>` (one verb per line) driving the real broker + page process headlessly. Binary and engine
revision: not recorded in any of the files below (the author's development log names a revision for the close of this step; it is not recorded in a file and is withheld).
Result files: `docs/appendix/part7/ch3-browsing-core/results/` (G2–G5) and `docs/appendix/part7/ch3-memory/results/` (G6); the scripts are in the matching `harness/` folders. Values below were re-read from the files.

- **G2 history session** (`session3.txt` → `session3.out.jsonl`, n = 1 scripted run, 10 steps): open a Wikipedia article, scroll 1,400 px,
  follow three links (Setun, Moscow State University, Moscow), back ×2, forward, back ×2. Measured end state: the first article at
  y = 1,400 (scroll position kept per history entry). Step times: open 884 ms, follows 205 / 383 / 964 ms, backs 167–424 ms.
- **G3 scrolling and resize** (`scroll.jsonl`, 3 long pages; [the script that produced the file is not shipped: only the result]): wheel-60-px median 15.05 / 12.7 / 13.8 ms (max 153.8 / 14.9 / 16.8), page-step
  median 33.3 / 16.9 / 23.3 ms, resize reflow 109–198 ms on the 72,000-px page and 40–89 ms on the others, renderer RSS 41.7 / 19.0 /
  19.3 MB. *Observation* (no numeric bar was registered): medians sit under the 16.6 ms frame for wheel steps and above it for page steps;
  one wheel step on the longest page took 153.8 ms.
- **G4 find, reader, zoom** (`session5.txt` → `session5.out.jsonl`): find "Setun" = 3 hits, "next" cycles 1 of 3 → 3 of 3 (y = 1,273 /
  1,493 / 6,441); reader view toggles on and off; text zoom 100 → 110 → 120 % moves page height 8,353 → 9,321 → 10,273 px and back.
- **G5 forms by GET** (`session6.txt` → `session6.out.jsonl`): words typed in the address bar open a search engine's HTML results
  (44 links, 1,318 ms); a result opens the article; the article site's own `<form method=get>` filled in the chrome and submitted opens
  the expected page (1,679 ms). Failure as registered: the search engine's own form is `method=post`, out of scope for this GET-only version; POST was added in
  section 5.
- **G6 memory against Firefox** (`ram.md`, `ram.json`; script-off; `ram-js.md`, `ram-js.json`; script-on): 10 pages, one page per cold
  start, peak over the run of summed PSS of every process in the browser's tree, sampled every 0.2 s. Firefox 156.0.1, new empty profile,
  `--headless --no-remote`, 15 s. **Bar ≤ 25 % of Firefox. Result: 211.3 MB vs 7,297.6 MB = 2.9 % (script off); 308.8 MB vs 7,423.6 MB =
  4.2 % (script on).** Per page (script off): 17.0–36.7 MB for us, 673.6–782.8 MB for Firefox; 2 processes against 13–16. Caveats stated
  by the data: one tab only; both sides headless (ours draws frames to memory with no window-system surface); a fresh Firefox profile; the
  harness is `harness/part7/ch3-memory/ram_bench.py` (omni-ui: `script web` open + hold 5 s with `OMNI_WEB_JS` 0 / 1; Firefox 15 s). The files print "MB" but compute kB / 1024, so the figures are MiB; the totals
  re-add from `ram.json` / `ram-js.json` to 211.3 / 7,297.6 and 308.8 / 7,423.6 (ratios 2.9 % and 4.16 %). The omni-ui binary and its engine revision are not named by the files.
  Readability of the ten pages was judged by eye on a contact sheet of the ten captures (the captures are of third-party sites and are not shipped; the sixth-row news-site page shows its sidebar over the content, the other nine read well):
  9 of 10 read well; that one has a positioning fault and falls back to reader view. That is a human judgement with no shipped file, not a metric.
- **Failure logged:** the merge of the main branch into the browser branch at the close of this step was *not* re-gated after main moved (the author stopped the step; revision withheld); the next gate is in section 12.

FIELD PREDICTS (G6): process-per-site isolation costs memory in published measurements (Reis, Moshchuk, Oskov, "Site Isolation: Process
Separation for Web Sites within the Browser", USENIX Security 2019, report a memory overhead of order ten percent [check against the paper: the figure is from memory and no document in this repository quotes it]); an engine with a flat packed
DOM, interned styles, no GPU process and no JIT should sit far below a multi-process engine on text pages, with the gap narrowing as script
heaviness grows. FIELD PREDICTS (G3): the 16.6 ms frame at 60 Hz and the ~10 ms the browser itself has to produce a frame are the published
targets (Google's RAIL model, web.dev).

## Connectivity, cookies, forms, WebSockets (2026-10-07)

The network layer was one small own HTTP/1.1 + rustls client. Defects found by probing a local route server, each fixed to the standard:

| Defect (measured before the fix) | Fix (what to build) | Standard |
|---|---|---|
| a 204 response, or a 3xx with no length on a keep-alive connection, waited for the read timeout twice [the "30.4 s" figure is unsupported: no pre-fix result file; the rule itself is in `omni-render/src/net.rs:318`] | body framing by message rules: no body for 1xx / 204 / 304; no length on keep-alive = close-delimited | RFC 9112 §6.3 |
| over TLS a close without close_notify dropped the whole response (one big classifieds site failed through its redirect chain) | EOF without close_notify = end of body | RFC 8446 §6.1 practice |
| any 4xx / 5xx returned nothing ("Could not load") | keep status and body; draw the server's own page; status line shows the code | RFC 9110 |
| no content coding, 5-redirect cap, no charset handling, no `data:` URLs | gzip / deflate / Brotli decode; ≤ 20 redirects; charset: HTTP header → BOM → `<meta>`; windows-1252 fallback; `data:` for images / CSS | RFC 1952 / 1951 / 7932; HTML Standard §13.2.3; RFC 2397 |
| no cookies (no sign-ins, no consent walls) | cookie jar, **first-party only** (a policy decision by the owner, 2026-10-07): in memory by default; a site's persistent cookies survive a restart only after the person chooses "keep"; HttpOnly hidden from script | RFC 6265 |
| GET only | POST (urlencoded; multipart without files; text/plain); checkbox / radio / select values ride the submit; WebSocket client owned by the broker | RFC 9110; RFC 6455 |

**Gate G7 (connectivity, 13 routes).** Harness `harness/part7/ch3-connectivity/conn.sh` + `server.py` (route server on a local port; each route
loaded through `omni-render page`, i.e. broker + confined page process; PASS needs the expected page title and a time bound of 3–5 s). Result
files: `docs/appendix/part7/ch3-merge-gate/results/run-1/conn.txt`, `run-2/conn.txt`, `run-3/conn.txt` (13 PASS, 0 FAIL in each, counted). **Result: 13 of 13 PASS in
each of the three runs** (routes: gzip, chunked, redirect ×3 and ×7, 404 page, 500 page, 204, set-cookie round trip, latin-1 title, close-delimited
body, JavaScript `document.cookie` = "srv=2; js=1", a PDF address, plain text). The 204 route took 0.10 / 0.05 / 0.12 s. Binary: the harness's
default is the browser worktree's engine binary; no revision is printed; the revisions per run are in section 12. The same 13 routes also pass 13 / 13 in eight later gate folders of another engine worktree
(`docs/appendix/part7/ch3-later-gates/results/gate-01/` … `gate-08/`, file `conn.txt`).
Weakness of the gate, stated: the 204 route's expected title is empty, which matches any title, so it only checks the time bound; the
checks exercise the engine CLI, not the omni-ui window; "kept" and "blocked" cookie states and the jar's restart persistence were checked by
script during development (recorded; no saved result). The POST route (`/postform` → "POSTED …") is in the shipped `server.py`; the WebSocket echo server and its pages are not shipped; no output of either was saved (recorded; no saved result).

**Observation (census, section 6):** two sites answer 403 to our requests (a Q&A site and a newspaper) and their 403 pages are shown, as designed.

FIELD PREDICTS (G7): a client that follows RFC 9112 §6.3 does not wait on a 204; a first-party-only jar is stricter than the third-party
blocking published by Safari (Intelligent Tracking Prevention, WebKit 2017+; full third-party cookie blocking, 2020) and Firefox (Total
Cookie Protection, 2021); sites that need cross-site sign-in cookies are predicted to fail to keep a session. No sign-in flow was measured.

## Accessibility: the page in the tree, the keyboard, and a contrast defect found by measuring

- **Finding (by reading the code, 2026-10-07):** in page mode the chrome was accessible but the page was not — a screen reader heard the
  toolbar and the status line only, and there was no keyboard path to page links or controls.
- **Page accessibility tree.** The page process exports one row per exposed node (role, name, states, bounds, link target) in frame W:
  landmarks, headings with level, links, lists, tables, images by alternative text, form controls with value / checked / expanded / placeholder
  (passwords as dots), ARIA role and label; hidden content left out. Roles follow HTML-AAM and names the accessible-name computation 1.2. The
  broker mounts the rows under one Document node of the same AccessKit tree as the chrome; assistive-technology click, focus and set-value act on
  page rows. The status line is a polite live region (page loads, find counts, errors are announced).
- **Keyboard.** Tab / Shift-Tab walk the toolbar and then the page's links and controls with a drawn 3 px focus ring scrolled into view;
  Enter / Space activate; Ctrl+L / F6 / Alt+D address, Ctrl+F find, Alt+←/→, F5, Ctrl+T / W / Tab / 1…9 tabs, Ctrl+D bookmark, Ctrl+C copy link.
  Gate as registered: a keyboard-only form submit ends with the expected posted values; an assistive-technology dump of an article has one node per
  extracted link. **Result: (recorded; no saved result). No screen-reader session was recorded.**
- **Defect found and fixed by arithmetic, not by eye.** After about one second of ticks the whole chrome rendered as translucent grey over a
  white page and small text was near-invisible. Cause: dark glass rgba(22, 28, 44, 0.58) over white is mid-grey, so the third text tone #6f7a94
  scored 1.02 : 1. **Fix = a contrast law:** glass alpha 0.88, and the secondary and tertiary text tones chosen so that every text colour is at
  least 4.5 : 1 over the worst page (white, black, mid-grey, red). Constants now: dark theme glass rgba(22, 28, 44, 0.88), tones #c4ccdf and
  #a9b3cc; light theme glass rgba(255, 255, 255, 0.88), tones #3c4760 and #4d5870; a high-contrast theme is pure black / white / yellow. WCAG 2.x
  relative-luminance ratios recomputed from these constants (`omni-ui/src/orbit.rs:132-134`; glass alpha-composited over a flat page colour; script `harness/part7/ch3-accessibility/contrast.py`, output `docs/appendix/part7/ch3-accessibility/results/contrast.out`) give: dark 7.38 : 1 and 5.66 : 1 over a white page (the worst case), light
  7.03 : 1 and 5.40 : 1 over a black page; old tone 1.02 : 1 (over a black page 4.42). (The author's working log states 7.4 / 5.6 and 7.1 / 5.4; the differences are rounding, the light ink-2 being 7.03 not 7.1.) The script:

```python
def lin(c): c/=255; return c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
def L(rgb): r,g,b=rgb; return .2126*lin(r)+.7152*lin(g)+.0722*lin(b)
def cr(a,b): la,lb=sorted((L(a),L(b)),reverse=True); return (la+.05)/(lb+.05)
over=lambda fg,a,bg: tuple(round(a*f+(1-a)*b) for f,b in zip(fg,bg))
