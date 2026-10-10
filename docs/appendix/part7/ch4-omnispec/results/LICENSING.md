# Licensing — omni-spec (and omni-posix in posix/)

**Decision (J 2026-10-06, "yes prep"): released free to the community as permissive open source — one of the fleet's freebies,
like dock and omnid.** Stock **Apache License 2.0** (`LICENSE`, byte-identical to dock's): OSI-approved, permissive, express patent
grant. Open for J: dual `MIT OR Apache-2.0` (the Rust-ecosystem convention) instead of Apache-2.0 alone.
This deliberately differs from omni-ring / vsa-core (source-available PolyForm dual) — do not "match the org convention".

## Release gates (all must pass before J publishes; the seat never pushes)
| # | Gate | How | Status |
|---|---|---|---|
| 1 | Clean-room provenance | every module cites spec sections; docs/<module>.md names spec + version; commit history shows spec-only work | per module |
| 2 | Clone check | doctor D0/D1 collage of each module against the best-known open implementation of the same standard (fetched to a scratch dir, never committed): no section with collage err < 0.15 (Type-1/2 clone) | to run per module |
| 3 | Patent screen | per module, a note in docs/<module>.md: JPEG baseline (expired), VP8/WebP (Google royalty-free grant), Brotli (IETF RFC 7932), W3C RECs (W3C royalty-free policy); OpenType features — screen; POSIX tools — no known issues | to run per module |
| 4 | Attribution | `NOTICE` (Unicode License v3 for UCD-derived tables and test files) | done |
| 5 | Third-party test data | only official standards data + our own fixtures in the public tree; PngSuite / JSONTestSuite / html5lib-tests excluded unless their licence allows redistribution | per module |
| 6 | Trademarks | no "OpenType", "Unicode", "POSIX" or "UNIX" in crate names (descriptive use in docs only) | names: omni-spec / omni-posix (J may rename) |
| 6b | Doctor patents seen | US10133657B2 (Fujitsu, to 2036): the doctor follows the design-around in `<notes>/2026-10-06 — DRX Oracle CONVERGE (9-cell).md`; FTO by counsel before the doctor ships | doctor release only |
| 7 | Export | fresh single-commit export under `<home>/release/omni-spec` (release ROADMAP rule); dry-run diff before J cuts it | at release |
Byline: "Juan Carlos De Santiago, with the Sovereign Raptor fleet (AI-assisted)". Org: SovRing-Labs. J publishes.
