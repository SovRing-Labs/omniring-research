# MATH CORE — computed status (math core M6; regenerate, never hand-edit)
| Concept | Spec (equation = definition on every row) | Law | Emitted Rust | Generator (mutation) | explain | Status |
|---|---|---|---|---|---|---|
| absmean_quant | `(map a0 (max (min (round (/ (idx a0 item1) (max …` | mathkb.absmean.ternary_sign CEMENTED | verified 2084 rows | clean (math-kb check) | ['absmean_quant'] | **M** |
| clock_read | `(fold (range 0 105) -1 (sel (and (== acc1.0 -1) …` | mathkb.clock.roundtrip CEMENTED | verified 2084 rows | clean (math-kb check) | ['clock_read'] | **M** |
| crt2 | `(fold (range 0 (* a1 a3)) -1 (sel (and (== acc1.…` | mathkb.crt.bijection CEMENTED | verified 1369 rows | clean (math-kb check) | ['crt2'] | **M** |
| mod_barrett | `(sel (>= (- a0 (* (>> (* a0 (/ 4294967296 a1)) 3…` | mathkb.barrett.equals_mod CEMENTED | verified 1998 rows | clean (math-kb check) | ['mod_barrett'] | **M** |
| hamming | `(fold (range 0 31) 0 (+ acc1.0 (& (>> (^ a0 a1) …` | mathkb.hamming.triangle CEMENTED | verified 2084 rows | clean (math-kb check) | ['hamming'] | **M** |
| mixed_radix | `(+ a0 (* a3 (+ a1 (* a4 a2))))…` | mathkb.mixed_radix.roundtrip CEMENTED | verified 2082 rows | clean (math-kb check) | ['mixed_radix'] | **M** |
| isqrt | `(get0 (while0.1 (tup a0) (> (* st1.0 st1.0) a0) …` | mathkb.isqrt.newton_brackets CEMENTED | verified 1207 rows | clean (math-kb check) | ['isqrt'] | **M** |
| softmax | `(map a0 (/ (exp (- (idx a0 item1) (maxall a0))) …` | mathkb.softmax.normalised_shift_invariant CEMENTED | verified 2084 rows | clean (math-kb check) | ['softmax'] | **M** |
| period | `(fold (range 1 (+ (len a0) 1)) 0 (sel (and (== a…` | mathkb.period.reproduces CEMENTED | verified 2084 rows | clean (math-kb check) | ['period'] | **M** |
| fib | `(get0 (while0.1 (tup 0 1 a0) (> st1.2 0) (tup st…` | mathkb.fib.cassini CEMENTED | verified 2084 rows | clean (math-kb check) | ['fib'] | **M** |
