//! CYCLONE-ARRAY presets (OMNI-RENDER-GPU-0 § CYCLONE-ARRAY, J 10-08: "saving each setting/preset to an exe"): the training array's
//! layout + wiring as ONE recorded step on our resident session, built natively from a preset — the kernels are embedded in the binary.
//! A preset is admitted here only after its rung passed the gate (`tests/cyclone/rung.py` checks every stream this produces against the
//! CPU references: Build::win, the runtime's rendered T25 core, Program64::t50, bus_coord.py, shmbus.rs).
//! Per step: feed_win (each harness cuts its batch from the resident curriculum) → ev_build ×2 (the trunk's T25 events, keyed per harness /
//! per unit) → ring_addr T25 (each harness's bus) → ring_addr T50 (each unit's cyclone) → hub_mean (each cyclone gathers its models'
//! weights) → [floor: hub_mean ×2 + hub_pull ×2 — the ring between the centre hub and the 4 around] → hub_pull (models → unit mean).
use crate::run::Gpu;
use crate::session::Session;

/// (name, floors, units per floor, harness/model pairs per unit) — the capacity ladder rungs whose wiring has passed its gate.
/// A floor of 5 = the centre unit + 4 around, joined by the ring; floors join by routing (ring 3 = the floor, J 10-08 readback).
pub const PRESETS: [(&str, usize, usize, usize); 5] = [("G1", 1, 1, 1), ("G4", 1, 1, 4), ("G8", 1, 1, 8), ("G40", 1, 5, 8), ("G120", 3, 5, 8)];
const RING_ADDR: &[u8] = include_bytes!("../kernels/ring_addr.spv");
const HUB_MEAN: &[u8] = include_bytes!("../kernels/hub_mean.spv");
const HUB_PULL: &[u8] = include_bytes!("../kernels/hub_pull.spv");
const FEED_WIN: &[u8] = include_bytes!("../kernels/feed_win.spv");
const EV_BUILD: &[u8] = include_bytes!("../kernels/ev_build.spv");
const ROUTE: &[u8] = include_bytes!("../kernels/route.spv");
const MB_COUNT: &[u8] = include_bytes!("../kernels/mb_count.spv");     // the toroid mailbox (JIT-T50 #1): count · scan · scatter ·
const MB_SCAN: &[u8] = include_bytes!("../kernels/mb_scan.spv");       // ledger (dispatched INDIRECT, sized by the GPU from the counts)
const MB_SCATTER: &[u8] = include_bytes!("../kernels/mb_scatter.spv");
const MB_LEDGER: &[u8] = include_bytes!("../kernels/mb_ledger.spv");
const CUTS: &[u8] = include_bytes!("../kernels/cuts.spv");      // gen/cut_kernels.py (our emitter): every toroid pair's min cut from route's tables
/// runtime/src/jit/t25.rs T25 groups and T30_ADD; T50 = these + the 20 odd primes 131…233 dealt round-robin (jit/t50.rs Program64::t50)
const T25: [[u32; 5]; 5] = [[3, 29, 41, 59, 101], [5, 31, 37, 67, 89], [7, 23, 43, 61, 97], [11, 19, 47, 71, 83], [13, 17, 53, 73, 79]];
const T30_ADD: [u32; 5] = [103, 107, 109, 113, 127];
/// one model's measured training state beyond its weight slab (C0: 0.538 GB per model at school settings, CPU engine)
pub const STATE_BYTES: u64 = 537_976_832 - 6_926_912 * 4;

pub struct Config { pub floors: usize, pub upf: usize, pub units: usize, pub per: usize, pub slab: usize, pub full_state: bool, pub b: usize, pub ctx: usize, pub eos: i32,
                    pub km: f32, pub k2: f32, pub k2c: f32, pub seed: u64 }
impl Config {
    pub fn preset(name: &str) -> Option<Config> {
        PRESETS.iter().find(|p| p.0.eq_ignore_ascii_case(name)).map(|&(_, floors, upf, per)| Config { floors, upf, units: floors * upf, per, slab: 1 << 20, full_state: false,
            b: 4, ctx: 512, eos: 0, km: 0.35, k2: 0.25, k2c: 0.10, seed: 0x5EED_C7C1 })
    }
}

/// runtime/src/thead.rs splitmix (the harness's own window draw)
pub fn splitmix(s: &mut u64) -> u64 {
    *s = s.wrapping_add(0x9E3779B97F4A7C15); let mut z = *s;
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58476D1CE4E5B9); z = (z ^ (z >> 27)).wrapping_mul(0x94D049BB133111EB); z ^ (z >> 31)
}

fn le_u32(v: &[u32]) -> Vec<u8> { v.iter().flat_map(|x| x.to_le_bytes()).collect() }
fn le_i32(v: &[i32]) -> Vec<u8> { v.iter().flat_map(|x| x.to_le_bytes()).collect() }
fn le_f32(v: &[f32]) -> Vec<u8> { v.iter().flat_map(|x| x.to_le_bytes()).collect() }
fn words(b: &[u8]) -> Vec<u32> { b.chunks_exact(4).map(|c| u32::from_le_bytes([c[0], c[1], c[2], c[3]])).collect() }
fn grid(n: usize) -> [u32; 3] { let g = n.div_ceil(64); let gx = g.min(65535); [gx as u32, (g / gx + 1) as u32, 1] }

/// the curriculum of a compiled build, every phase concatenated: tokens, plate kinds, stage (−1 where absent), mask (0 where absent)
pub struct Curriculum { pub d: Vec<u32>, pub kind: Vec<u32>, pub stage: Vec<i32>, pub mask: Vec<u32>, pub base: Vec<usize>, pub lens: Vec<usize> }
pub fn curriculum(dir: &str) -> Result<Curriculum, String> {
    let man = std::fs::read_to_string(format!("{dir}/manifest.json")).map_err(|e| format!("{dir}/manifest.json: {e}"))?;
    let at = man.find("\"phases\"").ok_or("manifest has no phases")?;
    let open = man[at..].find('[').ok_or("phases is not an array")? + at;
    let (mut depth, mut in_str, mut esc, mut close) = (0i32, false, false, None);       // the phases array only (other "file" keys follow it)
    for (i, ch) in man[open..].char_indices() {
        if in_str { if esc { esc = false } else if ch == '\\' { esc = true } else if ch == '"' { in_str = false } continue; }
        match ch { '"' => in_str = true, '[' | '{' => depth += 1, ']' | '}' => { depth -= 1; if depth == 0 { close = Some(open + i); break; } } _ => {} }
    }
    let span = &man[open..close.ok_or("phases array not closed")?];
    let mut files = Vec::new(); let mut rest = span;
    while let Some(i) = rest.find("\"file\"") {                                       // each phase's "file": "<name>" in order
        rest = &rest[i + 6..]; let q0 = rest.find('"').ok_or("file value")? + 1; let q1 = rest[q0..].find('"').ok_or("file value")? + q0;
        files.push(rest[q0..q1].to_string()); rest = &rest[q1..];
    }
    let mut c = Curriculum { d: vec![], kind: vec![], stage: vec![], mask: vec![], base: vec![], lens: vec![] };
    for (k, f) in files.iter().enumerate() {
        let raw = std::fs::read(format!("{dir}/{f}")).map_err(|e| format!("{f}: {e}"))?;
        let n = raw.len() / 2; c.base.push(c.d.len()); c.lens.push(n);
        c.d.extend(raw.chunks_exact(2).map(|x| u16::from_le_bytes([x[0], x[1]]) as u32));
        let kd = std::fs::read(format!("{dir}/kind_{k}.u8")).map_err(|e| format!("kind_{k}: {e}"))?;
        c.kind.extend((0..n).map(|i| *kd.get(i).unwrap_or(&255) as u32));
        let sg = std::fs::read(format!("{dir}/stage_{k}.u8")).unwrap_or_default();
        c.stage.extend((0..n).map(|i| sg.get(i).map_or(-1, |&v| v as i32)));
        let mk = std::fs::read(format!("{dir}/mask_{k}.u8")).unwrap_or_default();
        c.mask.extend((0..n).map(|i| *mk.get(i).unwrap_or(&0) as u32));
    }
    Ok(c)
}

/// window plan: window w → (phase, offset); harness h = w / b. The draw the reference (rung.py) mirrors.
pub fn windows(c: &Curriculum, n: usize, ctx: usize, seed: u64) -> Vec<(usize, usize)> {
    let mut s = seed;
    (0..n).map(|_| { let ph = (splitmix(&mut s) % c.lens.len() as u64) as usize; let o = (splitmix(&mut s) % (c.lens[ph] - ctx - 1) as u64) as usize; (ph, o) }).collect()
}

fn table(groups: &[Vec<u32>]) -> Vec<u32> {
    let prod4: u64 = T25[4].iter().map(|&m| m as u64).product();
    let off: [i32; 5] = [16384 * 64, 16384 * 64, 0, 0, (prod4 / 2) as i32];
    let mut t = vec![0u32; 133]; let mut k = 0;
    for (g, ms) in groups.iter().enumerate() { for &m in ms { t[k] = m; t[64 + k] = g as u32; k += 1; } }
    for g in 0..5 { t[128 + g] = off[g] as u32; }
    t
}
pub fn t25_groups() -> Vec<Vec<u32>> { T25.iter().map(|g| g.to_vec()).collect() }
pub fn t50_groups() -> Vec<Vec<u32>> {
    let more: Vec<u32> = (131..=233u32).step_by(2).filter(|&p| (3..).step_by(2).take_while(|d| d * d <= p).all(|d| p % d != 0)).collect();
    let mut gs: Vec<Vec<u32>> = (0..5).map(|i| { let mut v = T25[i].to_vec(); v.push(T30_ADD[i]); v }).collect();
    for (i, &p) in more.iter().enumerate() { gs[i % 5].push(p); }
    gs
}

pub struct Run { pub json: String }

/// lay out the preset, wire it, run `steps` recorded steps; dump the checked buffers (feed, T25 + T50 ledgers, weights) when `dump` is set
pub fn run(gpu: &Gpu, cfg: &Config, build: &str, ckpts: &[String], steps: u32, dump: Option<&str>) -> Result<Run, String> {
    let t0 = std::time::Instant::now();
    let (u, per, ctx, b, w) = (cfg.units, cfg.per, cfg.ctx, cfg.b, cfg.slab);
    let h = u * per; let nwin = h * b; let n = nwin * ctx;
    if ckpts.len() < h { return Err(format!("{} checkpoints for {h} models", ckpts.len())); }
    let c = curriculum(build)?;
    let wins = windows(&c, nwin, ctx, cfg.seed);
    let start: Vec<u32> = wins.iter().map(|&(ph, o)| (c.base[ph] + o) as u32).collect();
    let level: Vec<u32> = wins.iter().map(|&(ph, _)| ph as u32).collect();
    let mut slabs: Vec<f32> = Vec::with_capacity(h * w);
    for f in &ckpts[..h] {
        let raw = std::fs::read(f).map_err(|e| format!("{f}: {e}"))?;
        if raw.len() < w * 4 { return Err(format!("{f}: {} floats < slab {w}", raw.len() / 4)); }
        slabs.extend(raw[..w * 4].chunks_exact(4).map(|x| f32::from_le_bytes([x[0], x[1], x[2], x[3]])));
    }
    let mut keep = vec![1u32; h]; let mut kf = vec![cfg.km; h];
    if per > 1 { keep[h - 1] = 0; kf[h - 1] = 1.0; }                                   // one harness dropped by harmony → re-seeded from its unit
    let mut s = Session::new(gpu)?;
    let put = |s: &mut Session, bytes: Vec<u8>| -> Result<usize, String> { let i = s.buffer(bytes.len() as u64)?; s.write(i, &bytes)?; Ok(i) };
    let bd = put(&mut s, le_u32(&c.d))?; let bk = put(&mut s, le_u32(&c.kind))?; let bs = put(&mut s, le_i32(&c.stage))?; let bm = put(&mut s, le_u32(&c.mask))?;
    let bw = put(&mut s, le_u32(&start))?; let bl = put(&mut s, le_u32(&level))?;
    let feed = s.buffer((n * 20) as u64)?; let ev_h = s.buffer((n * 32) as u64)?; let ev_u = s.buffer((n * 32) as u64)?; let plate = s.buffer((n * 256) as u64)?;
    let tab25 = put(&mut s, le_u32(&table(&t25_groups())))?; let tab50 = put(&mut s, le_u32(&table(&t50_groups())))?;
    let ring = |s: &mut Session, g: usize| -> Result<[usize; 4], String> {
        Ok([s.buffer((n * 256) as u64)?, s.buffer((n * 256) as u64)?, s.buffer((g * 64 * 256 * 4) as u64)?, s.buffer((n * 8) as u64)?]) };
    let r25 = ring(&mut s, h)?; let r50 = ring(&mut s, u)?;
    let wt = put(&mut s, le_f32(&slabs))?; let bkeep = put(&mut s, le_u32(&keep))?; let bkf = put(&mut s, le_f32(&kf))?;
    let means = s.buffer((u * w * 4) as u64)?;
    let f = cfg.floors;
    let ringb = if cfg.upf == 5 {                                                     // every floor's ring: centre ↔ the 4 around
        let rep = |v: [u32; 5]| -> Vec<u32> { (0..f).flat_map(|_| v).collect() };
        let repf = |v: [f32; 5]| -> Vec<f32> { (0..f).flat_map(|_| v).collect() };
        Some((put(&mut s, le_u32(&rep([0, 1, 1, 1, 1])))?, put(&mut s, le_u32(&rep([1, 0, 0, 0, 0])))?, put(&mut s, le_f32(&repf([0.0, cfg.k2, cfg.k2, cfg.k2, cfg.k2])))?,
              put(&mut s, le_f32(&repf([cfg.k2c, 0.0, 0.0, 0.0, 0.0])))?, s.buffer((f * w * 4) as u64)?, s.buffer((f * w * 4) as u64)?))
    } else { None };
    // routing (W3): toroid = unit; layout rings ring 3 = the floor (floors > 1, stride 5), ring 5 = the place on the floor (stride 1)
    let routeb = if cfg.upf == 5 {
        let gs = t50_groups(); let flat: Vec<u32> = gs.iter().flatten().copied().collect();
        let lane = |m: u32| flat.iter().position(|&x| x == m).unwrap() as u32;
        let mut lay = vec![0u32; 13];
        let dims: Vec<[u32; 3]> = if f > 1 { vec![[lane(3), f as u32, 5], [lane(5), 5, 1]] } else { vec![[lane(5), 5, 1]] };
        lay[0] = dims.len() as u32; for (i, d) in dims.iter().enumerate() { lay[1 + 3 * i..4 + 3 * i].copy_from_slice(d); }
        Some((put(&mut s, le_u32(&lay))?, s.buffer((n * 4) as u64)?, s.buffer((n * 4) as u64)?, s.buffer((4 * u * u * 4) as u64)?,
              s.buffer((u * 64 * 256 * 4) as u64)?, s.buffer((u * 4) as u64)?,
              s.buffer((4 * 16 * 16 * 4) as u64)?, s.buffer((4 * u * 4) as u64)?, s.buffer((u * u * 4) as u64)?))   // rtab · vtab · cut (G4c)
    } else { None };
    if cfg.full_state { for _ in 0..h { s.buffer(STATE_BYTES)?; } }                   // each model's training state at its measured size
    let m = |s: &mut Session, b: &[u8]| s.module(&words(b));
    let (k_ra, k_hm, k_hp, k_fw, k_eb, k_rt) = (m(&mut s, RING_ADDR)?, m(&mut s, HUB_MEAN)?, m(&mut s, HUB_PULL)?, m(&mut s, FEED_WIN)?, m(&mut s, EV_BUILD)?, m(&mut s, ROUTE)?);
    let k_ct = m(&mut s, CUTS)?;
    let (k_mc, k_ms, k_mx, k_ml) = (m(&mut s, MB_COUNT)?, m(&mut s, MB_SCAN)?, m(&mut s, MB_SCATTER)?, m(&mut s, MB_LEDGER)?);
    let (ctx32, b32, per32, w32) = (ctx as u32, b as u32, per as u32, w as u32);
    s.pass(k_fw, c"main", &[(1, ctx32)], &[bd, bk, bs, bm, bw, feed], grid(n))?;
    s.pass(k_eb, c"main", &[(1, ctx32), (2, b32), (3, 1), (4, cfg.eos as u32)], &[feed, bl, ev_h], [nwin.div_ceil(64) as u32, 1, 1])?;
    s.pass(k_eb, c"main", &[(1, ctx32), (2, b32), (3, per32), (4, cfg.eos as u32)], &[feed, bl, ev_u], [nwin.div_ceil(64) as u32, 1, 1])?;
    let gy = n.div_ceil(4096) as u32;
    s.pass(k_ra, c"main", &[(1, 25)], &[ev_h, tab25, plate, r25[0], r25[1], r25[2], r25[3]], [4096, gy, 1])?;
    s.pass(k_ra, c"main", &[(1, 50)], &[ev_u, tab50, plate, r50[0], r50[1], r50[2], r50[3]], [4096, gy, 1])?;
    if let Some((lay, home, hops, link, hled, inbox, rtab, vtab, cut)) = routeb {     // every item jumps toroid → toroid to its address
        s.pass(k_rt, c"main", &[(1, 50), (2, u as u32)], &[ev_u, r50[0], lay, home, hops, link, hled, inbox, rtab, vtab], [4096, gy, 1])?;
        s.pass(k_ct, c"main", &[(4, u as u32)], &[rtab, vtab, lay, link, cut], grid(u * u))?;   // the T50 interlock read: all-pairs min cut
    }
    // the toroid mailbox (JIT-T50 #1, the pressure valve): each step's items gathered per home toroid; the consumer's workgroups per toroid
    // = ⌈items / 64⌉, decided on the GPU (mb_scan writes the indirect args) — a hot toroid gets more capacity, a quiet one less
    let mbox = if let Some((_, home, ..)) = routeb {
        let b = |s: &mut Session, k: usize| s.buffer((k * 4) as u64);
        let (cnt, off, tcnt, wgo, cur, args) = (b(&mut s, u)?, b(&mut s, u)?, b(&mut s, u)?, b(&mut s, u + 1)?, b(&mut s, u)?, b(&mut s, 3)?);
        let (mail, mled, wgt) = (b(&mut s, n)?, b(&mut s, u * 64 * 256)?, b(&mut s, u)?);
        s.pass(k_mc, c"main", &[], &[home, cnt], grid(n))?;
        s.pass(k_ms, c"main", &[(2, u as u32)], &[cnt, off, tcnt, wgo, cur, args], [1, 1, 1])?;
        s.pass(k_mx, c"main", &[], &[home, off, cur, mail], grid(n))?;
        s.pass_indirect(k_ml, c"main", &[(1, 50), (2, u as u32)], &[wgo, off, tcnt, mail, r50[0], mled, wgt], args)?;
        Some((off, tcnt, wgo, args, mail, mled, wgt))
    } else { None };
    s.pass(k_hm, c"main", &[(1, per32), (2, w32)], &[wt, bkeep, means], grid(u * w))?;
    if let Some((ko, kc, rko, rkc, tc, cc)) = ringb {
        s.pass(k_hm, c"main", &[(1, 5), (2, w32)], &[means, ko, tc], grid(f * w))?;
        s.pass(k_hm, c"main", &[(1, 5), (2, w32)], &[means, kc, cc], grid(f * w))?;
        s.pass(k_hp, c"main", &[(1, 5), (2, w32)], &[means, cc, rko], grid(u * w))?;
        s.pass(k_hp, c"main", &[(1, 5), (2, w32)], &[means, tc, rkc], grid(u * w))?;
    }
    s.pass(k_hp, c"main", &[(1, per32), (2, w32)], &[wt, means, bkf], grid(h * w))?;
    let setup_ms = t0.elapsed().as_secs_f64() * 1e3;
    let t1 = std::time::Instant::now(); let first = s.step(1)?; let first_ms = t1.elapsed().as_secs_f64() * 1e3;
    let rest = if steps > 1 { s.step(steps - 1)? } else { Default::default() };
    if let Some(dir) = dump {
        std::fs::create_dir_all(dir).map_err(|e| format!("{dir}: {e}"))?;
        for (name, i) in [("feed", feed), ("led25", r25[2]), ("led50", r50[2]), ("wt", wt)] {
            std::fs::write(format!("{dir}/{name}.bin"), s.read(i)?).map_err(|e| format!("{e}"))?;
        }
        if let Some((_, home, hops, link, hled, inbox, rtab, vtab, cut)) = routeb {
            for (name, i) in [("home", home), ("hops", hops), ("link", link), ("hled", hled), ("inbox", inbox), ("rtab", rtab), ("vtab", vtab), ("cut", cut)] {
                std::fs::write(format!("{dir}/{name}.bin"), s.read(i)?).map_err(|e| format!("{e}"))?;
            }
        }
        if let Some((off, tcnt, wgo, args, mail, mled, wgt)) = mbox {
            for (name, i) in [("mb_off", off), ("mb_tcnt", tcnt), ("mb_wgo", wgo), ("mb_args", args), ("mb_mail", mail), ("mb_led", mled), ("mb_wgt", wgt)] {
                std::fs::write(format!("{dir}/{name}.bin"), s.read(i)?).map_err(|e| format!("{e}"))?;
            }
        }
    }
    let nst = first.steps + rest.steps; let wall = first.wall_ms + rest.wall_ms;
    let gl = rest.gpu_ms_last.or(first.gpu_ms_last);
    let pm = s.pass_ms()?;                                                             // per-pass GPU ms (OMNI_GPU_PROFILE=1), else []
    let pass_ms = format!("[{}]", pm.iter().map(|x| format!("{x:.4}")).collect::<Vec<_>>().join(","));
    Ok(Run { json: format!("{{\"device\":{:?},\"floors\":{},\"units\":{u},\"pairs_per_unit\":{per},\"models\":{h},\"slab_floats\":{w},\"full_state\":{},\"events_per_step\":{n},\"buffers\":{},\"passes\":{},\"bytes_resident\":{},\"setup_ms\":{setup_ms:.3},\"first_step_ms\":{first_ms:.3},\"steps\":{nst},\"ms_per_step\":{:.4},\"gpu_ms_last\":{},\"pass_ms\":{pass_ms}}}",
        gpu.name, cfg.floors, cfg.full_state, s.buffers(), s.passes(), s.bytes(), wall / nst.max(1) as f64, gl.map(|x| format!("{x:.4}")).unwrap_or("null".into())) })
}
