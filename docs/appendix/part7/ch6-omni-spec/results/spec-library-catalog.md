# SPEC LIBRARY — published standards we can build our own code from (catalog, 2026-10-06)
Asked by J 2026-10-06: "first find published standards/specsheets that we can have an agent build a quick codebase from for our
most used/needed items. then we'll set up a cleanroom pipeline for when the doctor runs into a problem it can't solve."
Building from a STANDARD is the cleanest clean-room path: the spec is written to be implemented; no third-party code is read.

## 1. Evidence for "most used / most needed" (measured 2026-10-06)
- **Need (renderer):** of 493 origin mismatches (results/mismatches.jsonl), ≈ 65 % sit on TEXT-bearing boxes — top groups: text
  height in blocks 96 (line breaking / line height), text width in blocks 46, text height in flex 45, text width in table cells 26.
  The engine has NO shaping (no GSUB/GPOS in src/font.rs) and splits lines on ASCII whitespace only (`split_ascii_whitespace`,
  src/layout.rs inline()). Doctor "no donor" problems: collapsing borders, inline-flex baseline, shaping.
- **Use (dependencies):** crates pulled by our Rust apps (count of Cargo.toml files): ttf-parser 4 · png 4 · html5ever 4 ·
  serde_json 4 · zune-jpeg 3 · miniz_oxide 3 · image-webp 3 · gif 3 · brotli-decompressor 3 · wasmtime 3 · rustls / ring 2.
  Each of these (except crypto and WebAssembly) implements a public standard we could own.

## 2. Catalog (all URLs fetched 200 on 2026-10-06)
| # | Item | Standard (canonical URL) | Official conformance data | Our state | Doctor / app value | Size (est.) |
|---|---|---|---|---|---|---|
| A1 | Line breaking | Unicode UAX #14 https://www.unicode.org/reports/tr14/ | LineBreakTest.txt (UCD auxiliary) | ASCII whitespace only | HIGH — text height/width everywhere | ~1.5k lines + generated tables |
| A2 | Grapheme / word segmentation | Unicode UAX #29 https://www.unicode.org/reports/tr29/ | GraphemeBreakTest.txt, WordBreakTest.txt | none | MED — cursor/wrap units, CSS text | ~800 lines + tables |
| A3 | Kerning + ligatures (shaping) | OpenType GPOS https://learn.microsoft.com/en-us/typography/opentype/spec/gpos · GSUB …/gsub (+ legacy `kern` table) | none official; black-box oracle = glyph advances from an existing shaper on corpus fonts | none (advance widths only) | HIGH — every text width | ~2–3k lines (pair adjustment + ligature subst. first) |
| A4 | Inline formatting / line height | CSS 2.2 §10.8 https://www.w3.org/TR/CSS22/visudet.html · CSS Inline 3 https://www.w3.org/TR/css-inline-3/ | WPT css/CSS2/linebox, css-inline | partial (strut, vertical-align) | HIGH — "text h" groups | engine feature (doctor) |
| A5 | Text properties | CSS Text 3 https://www.w3.org/TR/css-text-3/ | WPT css/css-text | partial (white-space, transform; overflow-wrap held) | MED | engine feature |
| A6 | Font matching / features | CSS Fonts 4 https://www.w3.org/TR/css-fonts-4/ | WPT css/css-fonts | partial | MED | engine feature |
| B1 | Tables incl. collapsing borders | CSS 2.2 §17 https://www.w3.org/TR/CSS22/tables.html | WPT css/CSS2/tables | auto + fixed layout; spacing; no §17.6.2 collapse model | HIGH — wikitables, navboxes | engine feature |
| B2 | Flexbox algorithm | CSS Flexbox 1 §9 https://www.w3.org/TR/css-flexbox-1/ | WPT css/css-flexbox | implemented, gaps | MED | engine feature |
| B3 | Grid track sizing | CSS Grid 2 §11–12 https://www.w3.org/TR/css-grid-2/ | WPT css/css-grid | implemented, gaps (intrinsic added 10-06) | MED | engine feature |
| B4 | Intrinsic sizing | CSS Sizing 3 https://www.w3.org/TR/css-sizing-3/ | WPT css/css-sizing | implemented, gaps | MED | engine feature |
| C1 | Font files | OpenType spec (tables cmap/hmtx/glyf/CFF) + WOFF2 https://www.w3.org/TR/WOFF2/ | font test suites in WPT/fonts | ttf-parser dependency; own woff.rs | MED — replaces a 4× dependency | ~3k lines |
| C2 | DEFLATE / zlib | RFC 1951 https://www.rfc-editor.org/rfc/rfc1951 (+ RFC 1950) | RFC examples + round-trip | miniz_oxide dependency | MED — under PNG/WOFF/HTTP | ~600 lines (inflate) |
| C3 | PNG | W3C PNG 3rd ed. https://www.w3.org/TR/png-3/ | PngSuite (third-party image set: check licence before use) | png dependency | MED | ~800 lines (decode) |
| C4 | JPEG baseline | ITU-T T.81 https://www.w3.org/Graphics/JPEG/itu-t81.pdf | conformance images in the standard's annexes | zune-jpeg dependency | LOW–MED | ~1.5k lines |
| C5 | GIF | GIF89a https://www.w3.org/Graphics/GIF/spec-gif89a.txt | — | gif dependency | LOW | ~400 lines |
| C6 | WebP | RFC 9649 https://www.rfc-editor.org/rfc/rfc9649 (+ VP8 RFC 6386) | — | image-webp dependency | LOW–MED | lossless ~1k, lossy ~3k |
| C7 | Brotli | RFC 7932 https://www.rfc-editor.org/rfc/rfc7932 | RFC test vectors | brotli-decompressor dependency | LOW | ~1.5k lines (+ dictionary) |
| C8 | JSON | RFC 8259 https://www.rfc-editor.org/rfc/rfc8259 | JSONTestSuite (third-party: check licence) | serde_json dependency | LOW | ~400 lines |
| C9 | HTML parsing | WHATWG HTML §13.2 https://html.spec.whatwg.org/multipage/parsing.html | html5lib-tests (third-party: check licence) | html5ever dependency | MED — but very large | ~8–10k lines |
| C10 | CSS syntax | CSS Syntax 3 https://www.w3.org/TR/css-syntax-3/ | WPT css/css-syntax | own css.rs | LOW (already ours) | — |
| D1 | Bidi | Unicode UAX #9 https://www.unicode.org/reports/tr9/ | BidiTest.txt, BidiCharacterTest.txt | none (ltr only) | LOW now (our corpus is ltr) | ~1.5k lines |
| E1 | POSIX utilities (cat wc head tail sort uniq cut tr grep sed find ls cp mv rm mkdir xargs tee date …) | POSIX.1-2024 / Open Group Base Specifications Issue 8, XCU ch. 4 https://pubs.opengroup.org/onlinepubs/9799919799/utilities/contents.html | Open Group VSC suites are licensed (not open) → oracle = the installed GNU tools run differentially (black-box, like A3) | SPEC + READER built (<plan> T1, 10-06): omniglyph `axioms/posix.json` 65 specs / 20 tools, `sh` toolchain runs GNU vs our model; BUILDER = T3 | HIGH — talon term / NeuralOS terminal, every agent's shell | ~150–400 lines per tool from cemented laws |
| E2 | POSIX shell language | XCU ch. 2 Shell Command Language https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html | oracle = bash/dash run on own + generated scripts (no GPL test corpus) | none (<plan> T4) | HIGH — scripts + terminal | ~4–6k lines (expansion/quoting is the bulk) |
| E3 | POSIX regular expressions (BRE/ERE) | XBD ch. 9 https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap09.html | oracle = GNU grep -G/-E; jsi lazy DFA (B1, omni-render 5b33d09) is our ECMAScript engine | ECMAScript regex own (jsi); BRE/ERE none | MED — grep/sed/find under E1 | ~1k lines (BRE/ERE → our DFA) |
| X | NOT to own | TLS / crypto (rustls, ring), WebAssembly runtime (wasmtime) | — | dependencies | — | never hand-roll crypto; wasm is too large for the value |

Spec-document terms (to confirm per item before build; spec licences differ from code licences): W3C documents may be used to
implement (W3C Document License; Recommendations under the W3C Royalty-Free Patent Policy); Unicode data files are under the
Unicode License v3 (permissive, attribution); IETF RFCs are freely implementable; the OpenType specification is published by
Microsoft for implementers; JPEG baseline patents have expired; VP8/WebP carry Google's royalty-free grant. Third-party TEST
suites (PngSuite, JSONTestSuite, html5lib-tests) are data, not code — use only after a licence check.

## 3. Recommended first wave ("quick codebase", highest doctor value per line)
New repo `projects/omni-spec` (Rust library, no third-party code, every module cites its spec section in comments, every module
ships the official conformance file as its test):
1. **A1 UAX #14 line breaking** — pass LineBreakTest.txt; then wire into layout's inline() behind a doctor patch switch and gate.
2. **A3 OpenType kerning + ligatures (GPOS pair adjustment, GSUB type 4)** — black-box oracle: advances on the corpus's web fonts;
   then wire into text measurement behind a patch switch and gate (expected: the "text w" groups).
3. **A2 UAX #29 graphemes** — pass GraphemeBreakTest.txt (small; A1 and CSS Text need it).
4. **C2 inflate (RFC 1951/1950)** — round-trip and corpus PNG/WOFF payloads bit-identical to the current dependency.
Engine features (A4, B1 collapse model) stay doctor work: the doctor's gate is their conformance test.

## 3b. POSIX in the library (J 2026-10-06: spec → reader → builder, clean-room)
- **Spec** = each law cites its XCU section; GNU extensions (head -n -K, date -d, seq, xargs -r, cp/ls details) are tagged
  `gnu-ext` and kept apart from the POSIX scope (to do: one tagging pass over posix.json; seq is not POSIX at all).
- **Tagged 2026-10-06** (each utility's XCU page fetched): 50 posix · 9 gnu-ext (seq ×4 — not a POSIX utility; cat -n; head -n -K;
  date -d ×3) · 6 posix+gnu-detail (uniq -c padding, exit value 1 where POSIX says >0, wc -w non-printables, cut -c = bytes in GNU).
  Corrections found by checking: xargs -r and head -c ARE POSIX in Issue 8. Wide refutations split into GNU departures (cut -c,
  wc -w) and OUR model errors (head/tail -c counted characters → v2 laws on bytes, CEMENTED incl. wide; xargs quote/backslash
  processing is POSIX → v2 written: echo/n1 CEMENTED; noempty.v2 REFUTED by a real GNU departure — `-r` skips input that is
  only `""`, POSIX runs it).
- **Reader** = the omniglyph differential harness: GNU runs, our model predicts, a counterexample is kept (T1b); C locale = the
  POSIX locale, the law's scope; `--scope wide` records where GNU leaves POSIX (bytes vs characters).
- **Builder** = our tools generated from cemented laws only (T3), swap-in at 100 % agreement + 10k random cases; module lands in
  omni-spec beside the A–D items. POSIX text is read to implement, never copied into code or shipped.

## 4. Then: the clean-room pipeline for "the doctor cannot solve it" (to design next)
Trigger = a doctor card with no donor and no knob (D1b missing feature with no standard module yet, or D8 transplant fails).
Path: standard exists → spec-build lane (this catalog's method) · no standard → two-team clean room (reading team writes a
code-free spec from open-source study; building team implements from the spec only; D0/D1 clone check against the source
rejects leaks; patent note per spec) → module lands in omni-spec → D9 re-index → the doctor transplants from it and gates.
