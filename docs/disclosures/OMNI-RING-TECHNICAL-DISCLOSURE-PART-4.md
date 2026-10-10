# omni-ring — Technical Disclosure, Part 4 (2026-10-02): the sifter as code, the decode ladder, the learning core

> Copy notice. This is the research-corpus copy of the omni-ring disclosure (licence of this copy: CC BY 4.0; the same words ship in the omni-ring repository under that repository's licence). Names such as `omni_ring/...` and `experiments/...` refer to files of the omni-ring repository (release 0.2.0 or later). The only difference from the repository copy: pointers to private planning files were replaced by pointers to published files, or by a statement that the file is not published.

Dated prior art. Everything below is measured on one laptop CPU (i5-8365U, 4 cores, AVX2); harnesses and result JSON are in
`experiments/`; every bar was written before its harness (the plan files are internal and are not published) and every bar carries a FIELD PREDICTS line (what published theory says will happen).
Terms are the field's: "render" = JIT-generate executable code into memory; "self-modifying code"; "programs as hypervectors".

## 1. The sifter as a self-rewriting program in the store (CORTEX-2)
- `omni_ring/vm.py`: a vector VM. A program is ONE phase vector (8 instruction slots + 2 check slots bundled, int8-stored);
  15 opcodes × 8 args (NOP HOLD SHARPEN RELEASE FREEZE FOCUS LOAD BIND UNBIND BUNDLE SIFT THRESHOLD PROG JUMP MODE). The VM
  reads its program register every tick, refuses a program whose check slots fail (keeps the last good one), and executes it
  against registers and a mark lattice with the SuperSeed kernels. MODE places a sift METHOD (exact / cascade / soft) on a
  slot; PROG rewrites the program when the tick abstains (margin < spark); JUMP rewrites unconditionally. G1: VM sift ==
  C kernel bit-for-bit; 2,000/2,000 tampered programs refused; rewrite effective next tick 100/100.
- `omni_ring/jit.py`: the sift kernel RENDERED at run time — LLVM IR specialised to the lattice width and the host CPU,
  compiled in-process (26 ms), cached by hash. G2: 0 mismatches / 82 vs the hand AVX2 kernel on a 8,738 × 5,120 lattice.
- `omni_ring/vm_loop.py`: the VM as an always-on tick loop (50 Hz) on the live fleet event stream. G3: 1 h unattended,
  3,304 events, 175,725 idle ticks, 0 refused, idle tick 0.38 ms p50.
- Keyed check slots (`ProgramCodebook(key=…)` / `OMNIRING_PROGRAM_KEY`): HMAC-SHA256 over the instruction ids. Measured
  (PROG-INTEGRITY-0): chosen-program forgery 1.0 with public checksums → 1.2e-4 keyed; random acceptance ≈ 1/(120·103).
- Scale: exact lookup at 1,000,000 packed marks (2.56 GB) 485 ms; which-slot addressing on a 10,000-slot bus 100% to 128
  marks per slot (RINGPACK-1), matching the crowd-noise law.

## 2. The decode ladder (`omni_ring/route.py`): three mechanisms, each with a check
Product encoding v_d = exp(i x Σ_j r_{j,d}), r_{j,d} ∈ 2πZ/m_j (Residue HDC: Kymn, Kleyko, Frady, Kanerva, Sommer, Olshausen).
- **SIEVE** — the elementwise power v^{m_1 m_2} cancels every ring but one (a cyclic factor dies at its own order); one
  codebook sift per ring + CRT. Exact at every tested size: 1,879,981 states (113·127·131) in 0.6 / 1.5 / 8.0 ms at D 512 /
  1,024 / 4,096. Noise-fragile by construction (phase error × m_1 m_2): fails above ~105 states at von Mises κ 64 or 4-bit
  phases. Not found in the field's decoders (resonator / full codebook).
- **PART** — the partitioned (fractal-compression / PIFS-style) resonator: joint search of all residue combinations on a
  few 32-dim blocks via a 16-phase product lattice on the AVX2 sift kernel (built once per codebook), then per-ring block
  votes on the residual unbound by the other rings. Noisy (κ 16) and 4-bit-quantised slots: 1,879,981 states at 100% on both
  codebook draws, ~50 ms, no draw dependence. The plain soft resonator on the same ladder: 33k / 1k / 107k at D 512 / 1,024 /
  4,096 with a codebook lottery (21% of cells at exactly 0.5). Finding: partition blocks need NON-periodic phases — on
  orbit-phase codebooks all partitions alias and fail.
- **PEEL** — cued explaining-away on the kernel (`peel_kernel`; shipped for the bus as `peel.read_all_kernel`): clamp one
  ring per cue, joint-search the rest on a 1,024-dim block with an exact-magnitude int8 seed (per-cue scale), accept if
  17-legal and the codeword still explains ≥ 0.5 of a unit mark, subtract, repeat. On the live bus format (5 rings
  3·5·7·13+17, D 5,120): **24/24, 32/32, 48/48, 64/64, 96/96, 128/128 true marks per slot, 0 fakes, 0.2-0.5 s** (previous
  `read_all`: 16.65/24). 192 → 60.
- **CHECK** — re-encode the candidate and cosine it against the (residual) slot; escalate on a low margin.

## 3. The learning core (`omni_ring/core_learn.py`, CORE-ROUTE-2)
The three mechanisms are VM opcodes; the core holds a library of six program vectors (one per ordering, two check slots) and
every tick Thompson-samples one for the slot's signal bucket (magnitude profile × first-check margin), executes it, leaves a
mark, updates its posterior (fractional Beta: correct × cheap). Mixed stream (clean / κ-16 noisy / 4-bit / 4-superposed) at
1,879,981 states: accuracy 1.00 on every class over the last 100 slots, cost 1.31× the oracle's cheapest correct mechanism,
1.46 mechanisms fired per slot, 0.22 s mean. The core chose its own order from its own marks in 200 slots.

## 4. The spinning prism (PIPE-0/1)
Stations on the clock orbit, one process each; every tick each station works on the slot under it. Throughput is set by the
slowest face (pipeline theory): triangle 1.30×, hexagon 1.21×, square 0.66× (its single check sat after the slow face) vs the
sequential ladder; replicating the slow face (peel ×2) 1.73× on 4 cores, flat at ×3 (cores full). Rule: a check after every
mechanism; the prism scales with cores (one face per core).

## 5. Shapes and laws
- SHAPE-3D-0: routing accuracy at the noise where random keys score 0.80 — square 0.811 → tetrahedron 0.843; hexagon 0.716
  → octahedron 0.806 → 6-simplex 0.838; octagon 0.628 → cube 0.752 → 8-simplex 0.832. Linear in the keys' minimum pairwise
  angle (0.0033 per degree, r 0.97). The octahedron's vertices ±e_i are the ternary alphabet.
- Calibrations against the field: CAL-1 (codebook decode exact under κ 1 noise; 17 check ring 100%), CAL-2 (Plate's √(H/T)
  knee holds for HRR holograms; our capacity form fails in the overload tail), RESON-1b (soft resonator 0.78× the published
  capacity at D 512 with 3 rings; the ring-count collapse is Kent 2020's).
- Draft axioms added to the laws (A0 random is almost always unrelated; A18 binding distributes over bundling; A19 meaning
  is spread) with plain readings and field provenance; a readback law and a field-terms vocabulary for the assistant sessions.

## 6. Provenance (borrowed / ours)
Residue HDC, resonator networks, Plate's HRR, Kent 2020 capacity, Thompson sampling, pipeline theory, LLVM ORC/MCJIT,
sphere-code separation, Burak–Fiete attractors, PIFS (Jacquin / Fisher) are the field's. Ours: the program-as-vector VM
with sift opcodes and self-rewrite, the rendered kernel bit-exact to hand kernels, the power sieve for residue decoding, the
partitioned resonator on the kernel, the kernel cued peel at up to 64 marks/slot (the saved result stops at 64), the learning core over a program library, the
replicated-face prism. None claimed as first without a wider prior-art search; all dated here.
