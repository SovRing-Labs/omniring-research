Research corpus 0.3.0 (2026-10-14): designs built or tested after 0.2.0 are disclosed, with their measured status to this date.

**Added**
- `docs/disclosures/CYCLONE-TRAINER-TECHNICAL-DISCLOSURE.md` and `docs/disclosures/THEAD-SUPERSEED-TECHNICAL-DISCLOSURE.md` (design disclosures, previously unpublished).
- `docs/45-status-disclosure-2026-10-14.md`: exact residue-ring softmax / LSE / loss in the trainer (device == host bit-identical, 1.98x the float kernel); the ring core inside attention with T50 addressing, an Armilla 3x3 RRNS guard (recompute on abstain, <= 0.0067 nats) and cyclone routing (gap +1.44 -> +0.26 nats after training); the cyclone shape as the MLP core (negative: +4.2 % held-out loss); the liquid ternary doctor ranker; the open web as the doctor's curriculum (10,312 Common Crawl pages, 99.22 % pristine); BitNet b1.58 2B decoded bit-identically across CPUs; dispatch that stops instead of failing over; a speech core (design only, NOT YET TESTED).

**Evidence status.** Numbers come from saved runs kept in working records; their harnesses are not in this release.

---

Research corpus 0.2.0: the technical disclosures after Part 2 join the corpus, and the repository's own documents are corrected.

**Added (`docs/disclosures/`)**
- omni-ring Technical Disclosure Part 3 (2026-10-01), including the correction measured the same day: random program vectors are
  accepted at about 0.04% over 20,000 trials per arm (8 and 9 of 20,000; analytic (1/48)^2 = 0.043%), so the two small check slots are
  an error-detecting code, not a security boundary. Single-instruction tampering is always caught.
- Part 4 (2026-10-02): the sifter as code (a vector VM whose program is one phase vector), the decode ladder, the learning core.
- Part 5 (2026-10-03): the seed's owned ground, residue memory at scale, our own engines, fleet systems.
- Part 6 (2026-10-04): omni-render, its program runtime, JS on our IR, a self-repair core.
- omnid technical disclosure (front door, hardened web face, hypervector wire).
- dock technical disclosure (draft; every number labelled unverified until its harness output is saved).
- Part 7 (draft, 2026-10-09): live school and growth run, cyclone array and T50, Omni Web, the doctor core, the cores, provenance.
  Numbers carry (partial) or (unsupported) labels where no result file is published; failures are included as measured.

**Corrected**
- `README.md`: contents table now lists the disclosures, the guide and the 11 essays (it said 6); the row for a file that was never
  published is gone; it says which licence covers the disclosure copies and why the code-licence set is not in this repository.
- `MANIFEST.md` rewritten: no private source paths, no stale status wording.
- `CITATION.cff`: version 0.2.0.
- Harness comments: internal planning-file paths replaced by paths inside the repository (comments and usage lines only; no code
  path or number changes).
- `docs/22`: an internal task name removed from the author line of the header.

**Measured results in this release.** The corpus adds no new experiment of its own: its results are the ones in the disclosures,
each of which states its harness and result file or is labelled unsupported, unverified or partial. Evidence status: Parts 3 and 4
cite harnesses and results shipped in the omni-ring repository (`experiments/`); Parts 5 and 6 have no published claim-to-evidence
index yet, and say so in their opening lines.

**Not included.** A draft design disclosure for an unreleased launcher is held back until it is reviewed.
