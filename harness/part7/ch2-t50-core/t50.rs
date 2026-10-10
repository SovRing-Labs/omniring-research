//! T30-CORE-0 S7.2 (J 10-08: "a 35-50t as the memory buss with a 50t as the core for an experiment"). The T50 omniring system:
//! the odd primes 3…233 (50 rings, 10^93 states, Σm 5,348). Every residue is < 256, so a point is 50 bytes = ONE 64-byte AVX-512
//! row; residues ≥ 128 need the UNSIGNED compare (vpcmpub into a k-mask), which AVX2 lacks — hence the EVEX path. Same five
//! fields as the T25 bus (x0 · y0 · w · h · ry = clock · token · plate · level×stage · row), same offsets, 10 rings per field:
//! the T25 group + its T30 ring + 4 of the next 20 primes dealt round-robin. So T25 and T30 are exact sub-tori of T50 (their
//! residues must equal T50's on the shared rings). The 32-lane AVX2 core in t25.rs is untouched (its bytes do not change).

use super::t25::{T25, T30_ADD};

/// A 64-lane tier: lanes 0..50 = the groups flattened, lanes 50..64 zero (inert: residue 0, twist 0).
pub struct Program64 { pub groups: Vec<Vec<u8>>, pub mods: [u8; 64], pub off: [i64; 5] }

fn odd_primes_upto(n: u32) -> Vec<u8> { (3..=n).step_by(2).filter(|&p| (3..).step_by(2).take_while(|d| d * d <= p).all(|d| p % d != 0)).map(|p| p as u8).collect() }

impl Program64 {
    pub fn new(groups: Vec<Vec<u8>>, off: [i64; 5]) -> Program64 {
        let mut mods = [0u8; 64];
        let mut k = 0;
        for g in &groups { for &m in g { mods[k] = m; k += 1; } }
        assert!(k <= 64);
        Program64 { groups, mods, off }
    }
    /// T50 with the T25 offsets (t25::Program::t25().off) so T25 / T30 lanes agree ring for ring.
    pub fn t50(off: [i64; 5]) -> Program64 {
        let mut groups: Vec<Vec<u8>> = T25.iter().zip(T30_ADD).map(|(g, a)| { let mut v = g.to_vec(); v.push(a); v }).collect();
        let more: Vec<u8> = odd_primes_upto(233).into_iter().filter(|&p| p > 127).collect();
        assert_eq!(more.len(), 20);
        for (i, &p) in more.iter().enumerate() { groups[i % 5].push(p); }
        Program64::new(groups, off)
    }
    /// S3: the constant block the vector-encode kernel reads through its 6th argument (r9). Layout (bytes):
    /// 0 mods[64] · 64 off[5] as qwords · 128 0xFFFF ×8 · then per 8-lane chunk c at 192+256c: field index of each lane (qword),
    /// +64 P = 2¹⁶ mod m, +128 M = ⌊(2³²−1)/m⌋+1 (Lemire's c), +192 m. Inert lanes are all 0 → residue 0.
    pub fn consts(&self) -> Vec<u8> {
        let mut c = vec![0u8; 192 + 256 * 8];
        c[..64].copy_from_slice(&self.mods);
        let q = |c: &mut Vec<u8>, at: usize, v: u64| c[at..at + 8].copy_from_slice(&v.to_le_bytes());
        for g in 0..5 { q(&mut c, 64 + 8 * g, self.off[g] as u64); }
        for j in 0..8 { q(&mut c, 128 + 8 * j, 0xFFFF); }
        let mut lane = 0;
        for (g, ms) in self.groups.iter().enumerate() { for &m in ms {
            let (ch, j) = (lane / 8, lane % 8); let b = 192 + 256 * ch + 8 * j; let m = m as u64;
            q(&mut c, b, g as u64); q(&mut c, b + 64, (1u64 << 16) % m); q(&mut c, b + 128, 0xFFFF_FFFFu64 / m + 1); q(&mut c, b + 192, m);
            lane += 1;
        } }
        c
    }
    pub fn lanes(&self) -> usize { self.groups.iter().map(|g| g.len()).sum() }
    pub fn bytes(&self) -> Vec<u8> { self.groups.iter().flat_map(|g| std::iter::once(g.len() as u8).chain(g.iter().copied())).collect() }
    /// Scalar reference: fields → residues, one lane per ring.
    pub fn residues(&self, c: &[i64; 5]) -> [u8; 64] {
        let mut r = [0u8; 64];
        let mut k = 0;
        for (g, ms) in self.groups.iter().enumerate() { for &m in ms { r[k] = (c[g] + self.off[g]).rem_euclid(m as i64) as u8; k += 1; } }
        r
    }
}

/// Scalar twist (reference): per ring (ours − plate) mod m.
pub fn twist_scalar(a: &[u8; 64], b: &[u8; 64], mods: &[u8; 64]) -> [u8; 64] {
    let mut o = [0u8; 64];
    for k in 0..64 { let m = mods[k] as i16; o[k] = if m == 0 { 0 } else { (a[k] as i16 - b[k] as i16).rem_euclid(m) as u8 }; }
    o
}

/// The RENDERED T50 core: the same per-ring encode as t25::render (coordinate + group offset, magic-number reduction
/// q = x·⌈2⁴⁰/m⌉ ≫ 40, r = x − q·m, one byte per ring into a 64-byte row), then the whole row twisted against the plate in
/// AVX-512 BW: k1 = (ours <u plate) by vpcmpub; d = ours − plate (vpsubb); d{k1} += m (masked vpaddb). Unsigned, so residues
/// up to 255 are exact. Entry: fn(coords *const i64 [n×5], n, res_out *mut u8 [n×64], plate *const u8 [n×64],
/// twist_out *mut u8 [n×64], mods *const u8 [64]). Needs avx512bw at run time (caller checks).
pub fn render(pr: &Program64) -> super::t25::Rendered {
    use super::x86::*;
    let t = std::time::Instant::now();
    let mut a = Asm::default();
    a.test64(RSI);
    let to_end = a.jcc(false, 0);
    a.vmovdqu8_ld(15, R9, 0);       // zmm15 = the moduli, one per lane
    let top = a.b.len();
    let mut ring_at = Vec::new();
    let mut k = 0i32;
    for (g, ms) in pr.groups.iter().enumerate() {
        for &m in ms {
            let magic = ((1u128 << 40) + m as u128 - 1) / m as u128;
            ring_at.push(a.b.len());
            a.ld64(RAX, RDI, 8 * g as i32);
            a.add64_i(RAX, pr.off[g] as i32);
            a.mov64(R10, RAX);
            a.movabs(R11, magic as u64);
            a.imul64(R10, R11);
            a.shr64_i(R10, 40);
            a.imul64_i(R10, R10, m as i32);
            a.sub64(RAX, R10);
            a.st8(RDX, k, RAX);
            k += 1;
        }
    }
    let tail_at = a.b.len();
    a.vmovdqu8_ld(0, RDX, 0);       // ours: the event's T50 point
    a.vmovdqu8_ld(1, RCX, 0);       // the plate's point
    a.vpcmpub_k(1, 0, 1, 1);        // k1 = lanes where ours < plate (unsigned)
    a.vpsubb_z(0, 0, 1);
    a.vpaddb_zk(0, 1, 0, 15);       // + m on k1 lanes: the twist, every ring at once
    a.vmovdqu8_st(R8, 0, 0);
    a.add64_i(RDI, 8 * pr.groups.len() as i32); a.add64_i(RDX, 64); a.add64_i(RCX, 64); a.add64_i(R8, 64);
    a.dec64(RSI);
    a.jcc(true, top);
    let end = a.b.len(); a.patch(to_end, end);
    a.vzeroupper(); a.ret();
    let exec = Exec::new(&a.b);
    super::t25::Rendered { exec, hash: super::ir::hash(&pr.bytes()), render_us: t.elapsed().as_secs_f64() * 1e6, code: a.b, ring_at, tail_at }
}

/// S3 (T30-CORE-0, J 10-08): the VECTOR-ENCODE rendered core — the per-ring scalar encode replaced by Lemire, Kaser & Kurz 2019
/// "Faster remainder by direct computation" (arXiv:1902.01961; clean-room from the paper: c = ⌈2³²/m⌉ = ⌊(2³²−1)/m⌋+1,
/// r = ((c·y mod 2³²)·m) ≫ 32) on 8 qword lanes per zmm, all rings of an event at once. The paper's bound needs F ≥ N + log₂m, so
/// the 31-bit coordinate x is first folded to y = hi·(2¹⁶ mod m) + lo (hi = x ≫ 16 < 2¹⁵, lo = x & 0xFFFF; y < 2²⁴, same residue
/// mod m); the formula was checked EXHAUSTIVELY exact for every y < 2²⁴ and every m in 3…233 (test `lemire_fold_exact`). Domain:
/// 0 ≤ x = field + offset < 2³¹. Per event: one masked load of the 5 fields (k2 = 0x1F, no read past the event), + offsets,
/// split hi/lo; per 8-lane chunk: vpermq the field into its lanes (hi and lo), vpmuludq P, vpaddq, vpmuludq c, vpmuludq m,
/// vpsrlq 32, vpmovqb 8 residues to the row; then the same EVEX twist as `render`. 6th argument = `Program64::consts()`.
pub fn render_v(pr: &Program64) -> super::t25::Rendered {
    use super::x86::*;
    let t = std::time::Instant::now();
    let mut a = Asm::default();
    a.mov32_i(RAX, 0x1F); a.kmovw_kr(2, RAX);   // k2 = the 5 field lanes
    a.test64(RSI);
    let to_end = a.jcc(false, 0);
    a.vmovdqu8_ld(15, R9, 0);                     // zmm15 = the moduli (bytes) for the twist
    let top = a.b.len();
    a.vmovdqu64_ldkz(2, 2, RDI, 0);               // zmm2 = the 5 fields (qwords), lanes 5..7 = 0
    a.vpaddq_zm(2, 2, R9, 64);                    // + group offsets
    a.vpsrlq_zi(3, 2, 16);                        // zmm3 = hi
    a.vpandq_zm(4, 2, R9, 128);                   // zmm4 = lo
    let mut ring_at = Vec::new();
    for c in 0..pr.lanes().div_ceil(8) {
        let b = 192 + 256 * c as i32;
        ring_at.push(a.b.len());
        a.vmovdqu8_ld(5, R9, b);                  // field index per lane
        a.vpermq_z(6, 5, 3);
        a.vpermq_z(7, 5, 4);
        a.vpmuludq_zm(6, 6, R9, b + 64);          // hi · (2¹⁶ mod m)
        a.vpaddq_z(6, 6, 7);                      // y = … + lo  (< 2²⁴)
        a.vpmuludq_zm(6, 6, R9, b + 128);         // c·y (low dword = c·y mod 2³²)
        a.vpmuludq_zm(6, 6, R9, b + 192);         // (c·y mod 2³²)·m
        a.vpsrlq_zi(6, 6, 32);                    // residue
        a.vpmovqb_st(RDX, 8 * c as i32, 6);
    }
    let tail_at = a.b.len();
    a.vmovdqu8_ld(0, RDX, 0); a.vmovdqu8_ld(1, RCX, 0);
    a.vpcmpub_k(1, 0, 1, 1); a.vpsubb_z(0, 0, 1); a.vpaddb_zk(0, 1, 0, 15);
    a.vmovdqu8_st(R8, 0, 0);
    a.add64_i(RDI, 8 * pr.groups.len() as i32); a.add64_i(RDX, 64); a.add64_i(RCX, 64); a.add64_i(R8, 64);
    a.dec64(RSI);
    a.jcc(true, top);
    let end = a.b.len(); a.patch(to_end, end);
    a.vzeroupper(); a.ret();
    let exec = Exec::new(&a.b);
    super::t25::Rendered { exec, hash: super::ir::hash(&pr.bytes()), render_us: t.elapsed().as_secs_f64() * 1e6, code: a.b, ring_at, tail_at }
}

/// Rows of `t25-layers-bench` for 64-lane programs: per-event ns (one call per event, best of 3) and batched, residues vs scalar,
/// residues vs T25 on the shared rings (`top` = T25's residues, `lane25` = ring → T25 lane), and the twist vs scalar against a
/// plate drawn from other events (ours < plate on every ring; residues ≥ 128 exercised). `vector` = S3 encode (render_v) else the
/// per-ring scalar encode (render). Skipped (not failed) without avx512bw.
pub fn bench_row(name: &str, pr: &Program64, vector: bool, ev: &[i64], top: &[[u8; 32]], lane25: &std::collections::HashMap<u8, usize>) -> serde_json::Value {
    let n = ev.len() / 5;
    let rings: Vec<u8> = pr.mods.iter().copied().filter(|&m| m > 0).collect();
    let rd = if vector { render_v(pr) } else { render(pr) };
    let consts = pr.consts();
    if !std::arch::is_x86_feature_detected!("avx512bw") {
        return serde_json::json!({"layer": name, "rings": rings.len(), "encode": if vector { "lemire-zmm" } else { "scalar-per-ring" },
            "skipped": "no avx512bw on this CPU (rendered code built, not executed)", "code_bytes": rd.code.len()});
    }
    let k = rd.kernel();
    let fields = |i: usize| [ev[5 * i], ev[5 * i + 1], ev[5 * i + 2], ev[5 * i + 3], ev[5 * i + 4]];
    let in_domain = (0..n).all(|i| (0..5).all(|g| { let x = ev[5 * i + g] + pr.off[g]; (0..1i64 << 31).contains(&x) }));
    let plate: Vec<[u8; 64]> = (0..n).map(|i| pr.residues(&fields((i * 7919 + 13) % n))).collect();
    let mut res = vec![[0u8; 64]; n]; let mut tw = vec![[0u8; 64]; n];
    let mut per = f64::MAX;
    for _ in 0..3 { let t = std::time::Instant::now();
        for i in 0..n { k(ev[5 * i..].as_ptr(), 1, res[i..].as_mut_ptr() as *mut u8, plate[i..].as_ptr() as *const u8, tw[i..].as_mut_ptr() as *mut u8, consts.as_ptr()); }
        per = per.min(t.elapsed().as_secs_f64()); }
    let mut batched = f64::MAX;
    for _ in 0..3 { let t = std::time::Instant::now();
        k(ev.as_ptr(), n, res.as_mut_ptr() as *mut u8, plate.as_ptr() as *const u8, tw.as_mut_ptr() as *mut u8, consts.as_ptr());
        batched = batched.min(t.elapsed().as_secs_f64()); }
    let bad_scalar = (0..n).filter(|&i| res[i] != pr.residues(&fields(i))).count();
    let bad_twist = (0..n).filter(|&i| tw[i] != twist_scalar(&res[i], &plate[i], &pr.mods)).count();
    let bad_sub = (0..n).filter(|&i| rings.iter().enumerate().any(|(j, m)| lane25.get(m).map_or(false, |&l| res[i][j] != top[i][l]))).count();
    let hi = (0..n).map(|i| res[i].iter().filter(|&&r| r >= 128).count()).sum::<usize>();
    serde_json::json!({"layer": name, "rings": rings.len(), "encode": if vector { "lemire-zmm" } else { "scalar-per-ring" }, "code_bytes": rd.code.len(),
        "code_hash": format!("{:016x}", super::ir::hash(&rd.code)), "per_event_ns": per * 1e9 / n as f64,
        "batched_ns_per_event": batched * 1e9 / n as f64, "events_per_s": (n as f64 / per) as u64, "events_in_domain": in_domain,
        "mismatches_vs_scalar": bad_scalar, "mismatches_vs_T25_same_rings": bad_sub, "twist_mismatches_vs_scalar": bad_twist,
        "residues_ge_128": hi})
}

#[cfg(test)]
mod tests {
    use super::*;
    /// S3: Lemire's direct remainder (F = 32) after the 16-bit fold is exact for EVERY y < 2²⁴ and every ring m in 3…233
    /// (exhaustive), and the fold keeps the residue for x in [0, 2³¹) (spot-checked at edges + 1 M pseudo-random x).
    #[test]
    fn lemire_fold_exact() {
        for &m in odd_primes_upto(233).iter() { let m = m as u64; let c = 0xFFFF_FFFFu64 / m + 1;
            for y in 0..1u64 << 24 { assert_eq!(((c * y) & 0xFFFF_FFFF) * m >> 32, y % m, "m {m} y {y}"); }
            let p = (1u64 << 16) % m; let mut s = 0x9E37_79B9_7F4A_7C15u64;
            for i in 0..1_000_000u64 { s ^= s << 13; s ^= s >> 7; s ^= s << 17;
                let x = if i < 64 { [0, 1, 65535, 65536, (1 << 31) - 1, (1 << 31) - 2][i as usize % 6] } else { s % (1 << 31) };
                let y = (x >> 16) * p + (x & 0xFFFF); assert!(y < 1 << 24); assert_eq!(((c * y) & 0xFFFF_FFFF) * m >> 32, x % m); }
        }
    }
    /// The vector-encode kernel disassembles to the intended per-chunk sequence (GNU objdump).
    #[test]
    fn t50_vector_chunk_disassembles() {
        let rd = render_v(&Program64::t50(crate::jit::t25::Program::t25().off));
        let f = std::env::temp_dir().join(format!("omni-t50v-{}.bin", std::process::id()));
        std::fs::write(&f, &rd.code[rd.ring_at[1]..rd.ring_at[2]]).unwrap();
        let o = std::process::Command::new("objdump").args(["-D", "-b", "binary", "-mi386:x86-64", "-M", "intel"]).arg(&f).output().unwrap();
        let _ = std::fs::remove_file(&f);
        let got: Vec<String> = String::from_utf8_lossy(&o.stdout).lines().filter_map(|l| l.split('\t').nth(2).map(|s| s.split_whitespace().collect::<Vec<_>>().join(" "))).collect();
        assert_eq!(got, ["vmovdqu8 zmm5,ZMMWORD PTR [r9+0x1c0]", "vpermq zmm6,zmm5,zmm3", "vpermq zmm7,zmm5,zmm4",
            "vpmuludq zmm6,zmm6,ZMMWORD PTR [r9+0x200]", "vpaddq zmm6,zmm6,zmm7", "vpmuludq zmm6,zmm6,ZMMWORD PTR [r9+0x240]",
            "vpmuludq zmm6,zmm6,ZMMWORD PTR [r9+0x280]", "vpsrlq zmm6,zmm6,0x20", "vpmovqb QWORD PTR [rdx+0x8],zmm6"]);
        assert_eq!(rd.ring_at.len(), 7);
    }
    /// The tier is the odd primes 3…233 exactly, T25 + T30 rings sit in their own fields, Σm and lane count as designed.
    #[test]
    fn t50_tier_shape() {
        let p = Program64::t50(crate::jit::t25::Program::t25().off);
        let mut all: Vec<u8> = p.mods.iter().copied().filter(|&m| m > 0).collect(); all.sort();
        assert_eq!(all, odd_primes_upto(233));
        assert_eq!(all.len(), 50);
        assert_eq!(all.iter().map(|&m| m as u32).sum::<u32>(), 5348);
        for (g, t) in T25.iter().enumerate() { assert_eq!(&p.groups[g][..5], t); assert_eq!(p.groups[g][5], T30_ADD[g]); assert_eq!(p.groups[g].len(), 10); }
    }
    /// The rendered T50 kernel decodes (GNU objdump) to the intended tail: one EVEX twist per event.
    #[test]
    fn t50_rendered_tail_disassembles() {
        let rd = render(&Program64::t50(crate::jit::t25::Program::t25().off));
        let f = std::env::temp_dir().join(format!("omni-t50-{}.bin", std::process::id()));
        std::fs::write(&f, &rd.code[rd.tail_at..]).unwrap();
        let o = std::process::Command::new("objdump").args(["-D", "-b", "binary", "-mi386:x86-64", "-M", "intel"]).arg(&f).output().unwrap();
        let _ = std::fs::remove_file(&f);
        let got: Vec<String> = String::from_utf8_lossy(&o.stdout).lines().filter_map(|l| l.split('\t').nth(2).map(|s| s.split_whitespace().collect::<Vec<_>>().join(" "))).take(6).collect();
        assert_eq!(got, ["vmovdqu8 zmm0,ZMMWORD PTR [rdx]", "vmovdqu8 zmm1,ZMMWORD PTR [rcx]", "vpcmpltub k1,zmm0,zmm1",
                         "vpsubb zmm0,zmm0,zmm1", "vpaddb zmm0{k1},zmm0,zmm15", "vmovdqu8 ZMMWORD PTR [r8],zmm0"]);
    }
}
