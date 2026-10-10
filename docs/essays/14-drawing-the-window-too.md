# Drawing the window too: a browser on our own engine

| | |
|---|---|
| **Date** | 2026-10-08 |
| **Authors** | Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted) |
| **Licence** | CC BY 4.0 (see `LICENSE.md` at the corpus root) |
| **AI assistance** | Written with AI assistance (Claude) from the author's conversations of 6–8 October 2026 (unpublished). The author reviews it before publication. |
| **Type** | essay — every number is cited to docs 32–33 or `P7 §3`; anything not measured is marked **Speculative** |

## In one paragraph

Part 6 built a rendering engine that draws web pages the way Chrome does, from our own code. This week the same engine drew the browser around
the pages too — the address bar, the tabs, the settings, all as markup our own engine lays out and paints — and the browser got a name, Omni Web.
The first design was rejected in one line, and the reason it failed became a rule for how we design anything. The browser is remarkably light on
reading pages and not light at all on the heaviest web applications, and both facts are written down. Under it, the author placed a larger
ambition: that the browser is where the ring core lives, and that a page's geometry can be made exact rather than merely Chrome-like.

## The words you need

- **Engine** — omni-render: our packed DOM, CSS engine, integer layout and 2-bit raster (Part 6).
- **Chrome (the browser's)** — the field's word for a browser's own interface around the page: bar, tabs, menus. Not the Google browser.
- **Broker** — the privileged process that owns the window, the network and the files, and never parses a page.
- **Page process** — one locked-down process per open page that parses, runs the page's scripts and paints. If a page is hostile, it is
  trapped there.
- **Accessibility tree** — what a screen reader reads: a tree of roles, names and states that has to match what is on screen.
- **Trit** — a ternary value, −1 / 0 / +1. The browser shows several (site trust, cookies, third parties).
- **Merge gate** — the checks every engine change must pass before the app is allowed to use it.

## The idea, in the author's words and ours

The brief, given when the first design was rejected on 7 October, in full: *"rejected copletely. we are looking for a modernfuturistic aesthetic
fluid user intuitive highly accessible and capable lightweight ternery browser. it was going to be rendered using the renderer right? this design
is the opposite of what we are looking for."* And, on the second try: *"Yes, we'll use principles like this in our design, we are not making a
regular browser. we're making the next development in lightweight modern browser of a new era."* Earlier the same day the author had asked the
plainer question: *"what can we do to take omnibrowser into a fully fleshed out user friendly ternery browser instead of a hacked together search
bar?"*

Behind the browser was a bigger reason, given on 6 October about the ring core: *"this will live in our ternery browser as the system powersource
and intelligence"* — *"it lives in ternery renderer because it would be the most lightweight and powerful seat for it to oversee our local
sysstem."* And the goal for pages: *"our goal in formatting pages for our ternery browser is not to match chrome, it's to make the code on the pages
mathematically pristine"* (essay 15 follows that thread).

Our translation into a design (doc 32): a **broker** that owns the window and the network and never parses page content; one **page process**
per tab, locked down with the kernel's own tools (no new privileges, Landlock for files, a seccomp allow-list for system calls); and **one tree
for the browser's interface that feeds two outputs** — the markup our engine draws, and the accessibility tree a screen reader reads. Every input
— key, pointer, screen reader, voice, switch — ends in the same single action call, so what is drawn and what is read cannot disagree.

## How we got here

**Pages first (6 October).** Scripted against the real broker and page process: open an article, scroll, follow three links, go back and forward
— the first page came back at its saved scroll position; wheel steps took 13–15 ms (median) on three long pages, with one step at 154 ms; find,
reader view and text zoom worked. Then the comparison that mattered for "lightweight": ten pages, one cold start each, every process of each
browser summed. **Omni Web used 211 MiB; Firefox used 7,298 MiB — 2.9 %.** With scripts on, 309 against 7,424 MiB, 4.2 %. Two processes against
13 to 16 (doc 32).

**The network, fixed to the standards (7 October).** A small local route server found the defects one by one: an empty 204 response waited for a
timeout; a TLS connection closed without its closing message dropped the whole page; every error page came back as "could not load"; there was no
gzip, no Brotli, no character-set detection, no cookies, no POST. Each was fixed to the relevant standard, and the thirteen routes pass in every
run. Cookies are **first-party only** by the author's decision — kept in memory unless the person chooses to keep a site's — and the ternary
switch beside the address says so: block, session, keep (doc 32).

**The first design, and the rule it produced.** We offered three layouts in light, dark and high contrast. It was rejected outright, and the
cause was ours: we had first measured what the renderer could already draw — no rounded corners, no shadows, no blur, no motion — and made that
the ceiling, so the design came out flat and boxy. The rule we wrote is now a procedure: *start from the vision and the best work in the field;
design the target in full — look, feel, motion, accessibility; turn every capability the design needs into engine work; show the target with
that work listed beside it* (doc 33).

**Orbit.** The second design was approved the same day. The page fills the window; a glass bar floats over it; at its left sits the core — three
small rings, each turning at its own rhythm, moving only while a page loads; settings sit in an orb. Orbit asked the engine for eleven new
abilities, and nine were built in the paint module: rounded boxes by signed distance with exact anti-aliasing, soft shadows in closed form, linear,
radial and conic gradients, background blur, SVG strokes, the system font and more. Each was gated so that no page's layout moved by a single box
(doc 33). Transforms and keyframe animation, which need a compositor, were not built; motion is a spring computed per tick.

The author's first drive was honest: *"it's quite laggy, is it because the renderer is in use? on clicking anything then loading google is
1600ms."* The causes were three: the glass was blurred again for every tile, the whole window was re-rastered for a small change, and every remote
page was laid out once at 64 pixels wide before its real size because the page process read its viewport too late. Re-drawing only what the bar
covers, remembering tiles between frames and caching each blur brought clicks to about 25 ms (logged; the trace was not kept).

**A defect found by arithmetic.** After a second of ticks the whole interface turned grey and small text nearly vanished. The dark glass at
58 % opacity over a white page is mid-grey, and the third text tone over it measured 1.02 : 1. The fix is a law, not a colour pick: glass at 88 %
and text tones chosen so every one clears 4.5 : 1 against the worst background the glass can sit on (doc 33).

**The platform and the long tail (7–8 October).** A 106-check probe of the language and the page APIs — which Chrome passes 106 / 106 — was
first measured at 66 (working log); eight saved gate builds record 106 / 106. On the language's own conformance suite the engine passes 54.5 % of the executed tests, then 55.33 % and 56.85 % after two
rounds of early-error work. A census of 24 real sites, run three times, went from 69 failed scripts to 39 and from 9 parse errors to 1 (doc 33).

**And where "lightweight" ends.** The same census shows a median page process of 112 MB, twelve sites above 100 MB, and three above 500 MB — one
video site at 2.23 GB, its page still a skeleton. "Twenty-four of twenty-four" means a frame was produced, not that the page was usable: eight of
them built almost nothing. A compact store for the heaviest scripts — functions stored by content and compiled only when first called — was
designed and logged as halving that memory, but its output was not kept. The video site's music front end was repaired step by step until its shell
and menus drew; its grid never filled, and the author stopped the work (doc 33).

**The rule for shipping the engine.** Twice a build script hid a failed build and an old binary was measured and installed; once a branch merge
was not re-checked after the main branch moved. The merge gate came out of that: every engine change must leave the layout baseline unchanged —
24,032 of 28,040 boxes agreeing with Chrome on 49 frozen pages — keep the compiled and interpreted lookups identical, lose no box, pass the
probe and the network routes; only then does the app pin itself to that exact commit (doc 33).

## Where it did not hold

- Not light on script-heavy sites (up to 2.23 GB); the measured lightness is for document pages (docs 32–33).
- Paint error against Chrome and frame times were logged, not retained; no screen-reader session and no full day of daily use were recorded.
- The tracker head (allow / ask / block as a trit per request), plug-ins, developer tools and a mobile port are designed only. The author's
  question about Android — *"what would we have to do to port our omniweb to android, and how would it compare to other browsers?"* — has a plan,
  not a build.

## What this essay does not claim

That Omni Web is a finished browser; that it is lighter than Firefox on heavy web applications (it is not); that the ring core runs inside it as
the machine's processor (the core fires inside the engine's layout pass, essay 15; the machine-wide role is **Speculative**).
