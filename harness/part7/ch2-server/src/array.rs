//! THE ARRAY SERVER (GROW-RUN-0 G3b-4): one resident session holding R harness models (the replica training step, `gen/make_program.py`
//! with "R"), driven by R UNCHANGED `thead-learn` processes — each one's GPU engine library (engine-gpu, client mode: OMR_GPU_SERVER=DIR,
//! OMR_GPU_SLOT=r) hands its training step to the server through a shared-memory SLOT instead of running a session of its own.
//!   · a slot carries the batch + the step's extras (the same inputs the library feeds its own session) and, only when the CPU engine changed
//!     them since the last step (a merge, a restore, a load — the engine's weights are the truth), the harness's weights;
//!   · the server steps every slot that asked within a short window (OMR_ARRAY_WINDOW_MS, default 50) in ONE recorded step; a slot that did
//!     not ask rides along unchanged (its step scalars: lr 0, β₁ = β₂ = 1 → weights and moments untouched, its last batch keeps its loss finite);
//!   · after the step every active slot gets its loss and its updated weights back (the CPU engine decodes with them);
//!   · snapshot / restore of a slot's Adam moments follow the engine's om_snapshot / om_restore.
//! Each replica is bit-identical to its own single-model run (C2 S2, gated at school size on the A40), so a harness through the server trains
//! exactly as through the library alone. Files in DIR: cfg.json (from slot 0's library), prog/ (make_program), ready, slot<r>, stop.
use crate::program;
use crate::run::Gpu;
use std::collections::HashMap;
use std::ffi::c_void;
use std::sync::atomic::{AtomicU32, Ordering};

pub const HDR: usize = 64;                                   // header: 16 u32 words
pub const ST_IDLE: u32 = 0; pub const ST_STEP: u32 = 1; pub const ST_DONE: u32 = 2; pub const ST_SNAP: u32 = 3; pub const ST_REST: u32 = 4;
pub const ST_OPDONE: u32 = 5; pub const ST_FETCH: u32 = 6; pub const ST_GONE: u32 = 9;
// header words: 0 state · 1 dirty · 2 lr (f32 bits) · 3 loss out (f32 bits) · 4 client step · 5 has t25 · 6 has rs · 7 connected ·
// 8 lazy (1 = keep the weights on the GPU after a step: the client fetches them with ST_FETCH only when its CPU side reads them) ·
// 9 decode state (DS_*) · 10 decode config id (DIR/dcfg-<id>.json, written by the client) · 11 decode error
// THE DECODE SERVICE (GROW-RUN-0, run 1: 40 harness processes each with its own GPU decode context time-sliced the A40 to 4.8-10.9 s per
// array step): every harness's decoder runs here, R harness decoders × DS stations in ONE step (decode_step.py with R), on the device's second
// queue — beside the training step, which is submitted without waiting. DS_PREP: the slot's weights (the client's, current) → its replica, the
// BitLinear weights re-quantised (segment 0). DS_STEP: the slot's active stations one token each (segment 1), outputs + logit rows back.
pub const DS_IDLE: u32 = 0; pub const DS_STEP: u32 = 1; pub const DS_DONE: u32 = 2; pub const DS_PREP: u32 = 3; pub const DS_ERR: u32 = 5;
pub const DS: usize = 16; pub const DTMAX: usize = 1024;

extern "C" { fn mmap(a: *mut c_void, len: usize, prot: i32, flags: i32, fd: i32, off: i64) -> *mut c_void; }

/// the shape of one slot (from DIR/prog/array.txt, written by make_program)
#[derive(Clone)]
pub struct Layout { pub n: usize, pub v: usize, pub b: usize, pub t: usize, pub h: usize, pub params: Vec<(String, usize)>, pub wfloats: usize }
impl Layout {
    pub fn parse(text: &str) -> Result<Layout, String> {
        let mut l = Layout { n: 0, v: 0, b: 0, t: 0, h: 0, params: vec![], wfloats: 0 };
        for line in text.lines() {
            let p: Vec<&str> = line.split_whitespace().collect();
            let num = |i: usize| -> Result<usize, String> { p.get(i).and_then(|x| x.parse().ok()).ok_or(format!("array.txt: {line}")) };
            match p.first().copied() {
                Some("n") => l.n = num(1)?, Some("V") => l.v = num(1)?, Some("B") => l.b = num(1)?, Some("T") => l.t = num(1)?, Some("H") => l.h = num(1)?,
                Some("param") => { let s = num(2)?; l.params.push((p[1].to_string(), s)); l.wfloats += s; }
                _ => {}
            }
        }
        Ok(l)
    }
    pub fn rs(&self) -> usize { self.b * self.h * self.t }
    /// (offset, length in i32) of the input sections, then the weights offset
    pub fn sections(&self) -> (Vec<(&'static str, usize, usize)>, usize) {
        let mut o = HDR; let mut v = Vec::new();
        for (name, len) in [("x", self.n), ("y", self.n), ("pkind", self.n), ("pprop", self.n), ("pstage", self.n), ("pavoid", self.n),
                            ("t25res", self.n * 32), ("rsBH", self.rs())] { v.push((name, o, len)); o += len * 4; }
        (v, o)
    }
    pub fn bytes(&self) -> usize { self.sections().1 + self.wfloats * 4 }
    /// the decode area: i32 tok · kind · prop · pos · act [DS] · res [DS·32] | f32 targ · tmx · t2nd · ex [DS] · pst [DS·5] · pgw [DS·2] · logits [DS·V]
    pub fn dec(&self) -> HashMap<&'static str, (usize, usize)> {
        let mut o = (self.bytes() + 63) / 64 * 64; let mut m = HashMap::new();
        for (k, n) in [("tok", DS), ("pkind", DS), ("pprop", DS), ("dpos", DS), ("act", DS), ("t25res", DS * 32),
                       ("targ", DS), ("tmx", DS), ("t2nd", DS), ("ex", DS), ("pst", DS * 5), ("pgw", DS * 2), ("dlog", DS * self.v)] { m.insert(k, (o, n)); o += n * 4; }
        m.insert("end", (o, 0)); m
    }
    pub fn full_bytes(&self) -> usize { self.dec()["end"].0 }
}

/// a mapped slot file
pub struct Slot { pub p: *mut u8, pub len: usize }
unsafe impl Send for Slot {}
impl Slot {
    pub fn map(path: &str, len: usize, create: bool) -> Result<Slot, String> {
        use std::os::fd::AsRawFd;
        let f = std::fs::OpenOptions::new().read(true).write(true).create(create).open(path).map_err(|e| format!("{path}: {e}"))?;
        if create { f.set_len(len as u64).map_err(|e| format!("{path}: {e}"))?; }
        let p = unsafe { mmap(std::ptr::null_mut(), len, 3, 1, f.as_raw_fd(), 0) };
        if p as isize == -1 { return Err(format!("mmap {path} failed")) }
        Ok(Slot { p: p as *mut u8, len })
    }
    pub fn word(&self, k: usize) -> &AtomicU32 { unsafe { &*(self.p as *const AtomicU32).add(k) } }
    pub fn bytes(&self, off: usize, n: usize) -> &mut [u8] { unsafe { std::slice::from_raw_parts_mut(self.p.add(off), n) } }
    pub fn i32s(&self, off: usize, n: usize) -> &mut [i32] { unsafe { std::slice::from_raw_parts_mut(self.p.add(off) as *mut i32, n) } }
}

fn parse_io(s: &str) -> HashMap<String, usize> {
    s.lines().filter_map(|l| { let l = l.trim().trim_end_matches(','); let (k, v) = l.rsplit_once(':')?;
        Some((k.trim().trim_matches('"').to_string(), v.trim().parse().ok()?)) }).collect()
}
fn b32(v: &[i32]) -> Vec<u8> { v.iter().flat_map(|x| x.to_le_bytes()).collect() }
fn f32b(v: &[f32]) -> Vec<u8> { v.iter().flat_map(|x| x.to_le_bytes()).collect() }

/// step scalars as the library / the engine: [coef (GPU), lr, wd, β₁, β₂, lr/bc1, √bc2, eps]; inactive = no change at all
fn scalars(lr: f32, step: u64, active: bool) -> [f32; 8] {
    if !active { return [0.0, 0.0, 0.1, 1.0, 1.0, 0.0, 1.0, 1e-8] }
    let (b1, b2) = (0.9f32, 0.95f32); let bc1 = 1.0f32 - b1.powf((step + 1) as f32); let bc2 = 1.0f32 - b2.powf((step + 1) as f32);
    [0.0, lr, 0.1, b1, b2, lr / bc1, bc2.sqrt(), 1e-8]
}

/// `omni-gpu serve DIR --slots R [--device D] [--window-ms 50]`
pub fn serve(gpu: &Gpu, dir: &str, r_: usize, window_ms: u64, log: &mut dyn FnMut(String)) -> Result<(), String> {
    let wait = |p: &str| { while !std::path::Path::new(p).exists() { if std::path::Path::new(&format!("{dir}/stop")).exists() { return false } std::thread::sleep(std::time::Duration::from_millis(50)); } true };
    let mut dec = Decode::new();                                               // the decode service runs from the start (before any training step)
    while !std::path::Path::new(&format!("{dir}/cfg.json")).exists() {
        if std::path::Path::new(&format!("{dir}/stop")).exists() { return Ok(()) }
        if !dec.serve(gpu, dir, r_, log)? { std::thread::sleep(std::time::Duration::from_micros(200)); }
    }
    let _ = &wait;
    std::thread::sleep(std::time::Duration::from_millis(100));                 // slot 0 renames cfg.json into place; settle
    let cfg = std::fs::read_to_string(format!("{dir}/cfg.json")).map_err(|e| e.to_string())?;
    let cfg_r = format!("{{\"R\": {r_}, {}", cfg.trim_start().trim_start_matches('{'));
    std::fs::write(format!("{dir}/cfg-R.json"), &cfg_r).map_err(|e| e.to_string())?;
    let root = std::env::var("OMNI_GPU_ROOT").unwrap_or_else(|_| concat!(env!("CARGO_MANIFEST_DIR")).to_string());
    let out = std::process::Command::new(std::env::var("OMNI_GPU_PYTHON").unwrap_or("python3".into()))
        .arg(format!("{root}/gen/make_program.py")).arg(format!("{dir}/cfg-R.json")).arg(format!("{dir}/prog")).output().map_err(|e| format!("make_program: {e}"))?;
    if !out.status.success() { return Err(format!("make_program: {}", String::from_utf8_lossy(&out.stderr))) }
    let text = std::fs::read_to_string(format!("{dir}/prog/prog.txt")).map_err(|e| e.to_string())?;
    let io = parse_io(&std::fs::read_to_string(format!("{dir}/prog/io.json")).map_err(|e| e.to_string())?);
    let lay = Layout::parse(&std::fs::read_to_string(format!("{dir}/prog/array.txt")).map_err(|e| e.to_string())?)?;
    let mut lo = program::load(gpu, &text, "array")?;
    let s = &mut lo.s;
    let slots: Vec<Slot> = (0..r_).map(|r| Slot::map(&format!("{dir}/slot{r}"), lay.full_bytes(), true)).collect::<Result<_, _>>()?;
    let (secs, woff) = lay.sections();
    log(format!("[array] {} — {r_} slots, {} passes, {:.1} MB resident, slot {} MB", gpu.name, lo.pass_names.len().max(s.passes()), s.bytes() as f64 / 1e6, lay.bytes() / 1_000_000));
    std::fs::write(format!("{dir}/ready"), "ready\n").map_err(|e| e.to_string())?;
    let mut snaps: Vec<Option<Vec<Vec<u8>>>> = vec![None; r_];
    let (mut steps, mut t_gpu, mut t_all, mut act_sum, mut last_gpu) = (0u64, 0f64, 0f64, 0u64, 0f64);
    let slice = |k: &str, s: &crate::session::Session| -> Option<(usize, u64)> { io.get(k).map(|&i| (i, s.size(i) / r_ as u64)) };
    loop {
        // snapshot / restore requests: served at once
        for (r, sl) in slots.iter().enumerate() {
            match sl.word(0).load(Ordering::Acquire) {
                ST_SNAP => {
                    let items: Vec<(usize, u64, u64)> = lay.params.iter().flat_map(|(n, sz)| ["m", "v"].map(|k| (io[&format!("{k}:{n}")], (r * sz * 4) as u64, (sz * 4) as u64))).collect();
                    snaps[r] = Some(s.read_at_many(&items)?); sl.word(0).store(ST_OPDONE, Ordering::Release);
                }
                ST_FETCH => {                                                  // the slot's current weights → its slot (a lazy client's CPU side reads them)
                    let items: Vec<(usize, u64, u64)> = lay.params.iter().map(|(n, sz)| (io[&format!("w:{n}")], (r * sz * 4) as u64, (sz * 4) as u64)).collect();
                    let back = s.read_at_many(&items)?; let mut o = woff;
                    for (j, (_, sz)) in lay.params.iter().enumerate() { sl.bytes(o, sz * 4).copy_from_slice(&back[j]); o += sz * 4; }
                    sl.word(0).store(ST_OPDONE, Ordering::Release);
                }
                ST_REST => {
                    if let Some(mv) = &snaps[r] {
                        let items: Vec<(usize, u64, &[u8])> = lay.params.iter().flat_map(|(n, sz)| ["m", "v"].map(|k| (io[&format!("{k}:{n}")], (r * sz * 4) as u64)))
                            .zip(mv.iter()).map(|((i, o), b)| (i, o, b.as_slice())).collect();
                        s.write_at_many(&items)?;
                    }
                    sl.word(0).store(ST_OPDONE, Ordering::Release);
                }
                _ => {}
            }
        }
        let served = dec.serve(gpu, dir, r_, log)?;
        let req: Vec<usize> = (0..r_).filter(|&r| slots[r].word(0).load(Ordering::Acquire) == ST_STEP).collect();
        if req.is_empty() {
            if std::path::Path::new(&format!("{dir}/stop")).exists() { break }
            if !served { std::thread::sleep(std::time::Duration::from_micros(200)); } continue;
        }
        // the window: wait for every connected slot (or until the window closes) — a slow harness never blocks the rest; decode served meanwhile
        let alive = |slots: &Vec<Slot>| (0..r_).filter(|&r| slots[r].word(7).load(Ordering::Acquire) == 1 && slots[r].word(0).load(Ordering::Acquire) != ST_GONE).count();
        // the window stretches to the last step's GPU time: a step costs the same whatever the number of slots in it (inactive replicas ride
        // along), so waiting that long for more slots is free (run 3: a 50 ms window took 4-6 of 20 slots into each 1.5 s step)
        let win = (window_ms as f64).max(last_gpu) as u128;
        let t0 = std::time::Instant::now();
        let mut act = req;
        while act.len() < alive(&slots) && t0.elapsed().as_millis() < win {
            if !dec.serve(gpu, dir, r_, log)? { std::thread::sleep(std::time::Duration::from_micros(200)); }
            act = (0..r_).filter(|&r| slots[r].word(0).load(Ordering::Acquire) == ST_STEP).collect();
        }
        let ts = std::time::Instant::now();
        let mut w: Vec<(usize, u64, Vec<u8>)> = Vec::new();
        for &r in &act {
            let sl = &slots[r];
            for &(name, off, len) in &secs {
                if name == "t25res" && sl.word(5).load(Ordering::Acquire) == 0 { continue }
                if name == "rsBH" && sl.word(6).load(Ordering::Acquire) == 0 { continue }
                if let Some((i, per)) = slice(name, s) { w.push((i, r as u64 * per, sl.bytes(off, len * 4).to_vec())); }
            }
            let xs = sl.i32s(secs[0].1, lay.n).to_vec();                      // the embedding scatter's grouping (as the library)
            let mut order: Vec<i32> = (0..lay.n as i32).collect(); order.sort_by_key(|&i| xs[i as usize]);
            let mut est = vec![0i32; lay.v + 1]; for &tk in &xs { est[tk as usize + 1] += 1; } for i in 0..lay.v { est[i + 1] += est[i]; }
            if let Some((i, per)) = slice("eord", s) { w.push((i, r as u64 * per, b32(&order))); }
            if let Some((i, per)) = slice("est", s) { w.push((i, r as u64 * per, b32(&est))); }
            let step = sl.word(4).load(Ordering::Acquire) as u64;
            if let Some((i, per)) = slice("stepv", s) { w.push((i, r as u64 * per, b32(&[step as i32]))); }
            if sl.word(1).load(Ordering::Acquire) == 1 {                       // weights changed on the CPU since the last step: upload
                let mut o = woff;
                for (n, sz) in &lay.params { w.push((io[&format!("w:{n}")], (r * sz * 4) as u64, sl.bytes(o, sz * 4).to_vec())); o += sz * 4; }
            }
        }
        if let Some((i, _)) = slice("sc", s) {                                 // every slot's scalars: active ones step, the rest stay still
            let mut sc = Vec::with_capacity(r_ * 8);
            for r in 0..r_ { let on = act.contains(&r); sc.extend(scalars(f32::from_bits(slots[r].word(2).load(Ordering::Acquire)), slots[r].word(4).load(Ordering::Acquire) as u64, on)); }
            w.push((i, 0, f32b(&sc)));
        }
        if let Some(&i) = io.get("acc") { w.push((i, 0, vec![0u8; (s.size(i)) as usize])); }
        let wref: Vec<(usize, u64, &[u8])> = w.iter().map(|(i, o, b)| (*i, *o, b.as_slice())).collect();
        s.write_at_many(&wref)?;
        let tg = std::time::Instant::now(); s.step_async()?;                  // training on queue 1; decode keeps being served on queue 2
        while !s.step_done()? { if !dec.serve(gpu, dir, r_, log)? { std::thread::sleep(std::time::Duration::from_micros(100)); } }
        last_gpu = tg.elapsed().as_secs_f64() * 1e3; t_gpu += last_gpu;
        let lb = s.read(io["loss"])?;
        let back_slots: Vec<usize> = act.iter().copied().filter(|&r| slots[r].word(8).load(Ordering::Acquire) == 0).collect();   // lazy slots: no read-back
        let items: Vec<(usize, u64, u64)> = back_slots.iter().flat_map(|&r| lay.params.iter().map(move |(n, sz)| (n.clone(), r, *sz)))
            .map(|(n, r, sz)| (io[&format!("w:{n}")], (r * sz * 4) as u64, (sz * 4) as u64)).collect();
        let back = s.read_at_many(&items)?;
        let np = lay.params.len();
        for (k, &r) in back_slots.iter().enumerate() {
            let sl = &slots[r]; let mut o = woff;
            for (j, (_, sz)) in lay.params.iter().enumerate() { sl.bytes(o, sz * 4).copy_from_slice(&back[k * np + j]); o += sz * 4; }
        }
        for &r in &act {
            let sl = &slots[r];
            sl.word(3).store(u32::from_le_bytes([lb[r * 4], lb[r * 4 + 1], lb[r * 4 + 2], lb[r * 4 + 3]]), Ordering::Release);
            sl.word(1).store(0, Ordering::Release); sl.word(0).store(ST_DONE, Ordering::Release);
        }
        steps += 1; act_sum += act.len() as u64; t_all += ts.elapsed().as_secs_f64() * 1e3;
        if steps % 50 == 0 { log(format!("[array] {steps} steps · {:.1} slots / step · gpu {:.1} ms · step+io {:.1} ms · decode {} steps, {:.1} stations / step, {:.2} ms",
            act_sum as f64 / steps as f64, t_gpu / steps as f64, t_all / steps as f64, dec.steps, dec.act as f64 / dec.steps.max(1) as f64, dec.ms / dec.steps.max(1) as f64)); }
    }
    std::fs::write(format!("{dir}/stats.json"), format!("{{\"decode_steps\": {}, \"decode_stations_per_step\": {:.3}, \"decode_ms\": {:.3}, \"steps\": {steps}, \"slots\": {r_}, \"mean_active\": {:.3}, \"gpu_ms\": {:.3}, \"step_io_ms\": {:.3}, \"bytes_resident\": {}, \"device\": {:?}}}\n",
        dec.steps, dec.act as f64 / dec.steps.max(1) as f64, dec.ms / dec.steps.max(1) as f64,
        if steps > 0 { act_sum as f64 / steps as f64 } else { 0.0 }, if steps > 0 { t_gpu / steps as f64 } else { 0.0 }, if steps > 0 { t_all / steps as f64 } else { 0.0 }, s.bytes(), gpu.name))
        .map_err(|e| e.to_string())?;
    log(format!("[array] stop after {steps} steps"));
    Ok(())
}

/// one decode program (per decoder config) for every slot: R replicas × DS stations, on queue 2
struct DecSess<'a> { s: crate::session::Session<'a>, io: HashMap<String, usize> }

/// THE DECODE SERVICE's state. Its slots are their own files, DIR/dslot-<id>-<r> (id = the decoder config, DIR/dcfg-<id>.json; layout
/// DIR/dlay-<id>.txt = array.txt's form with n 0: header · that config's weights · the decode area) — created by the client at its first
/// prepare, independent of the training layout: the switches (and the local read-outs' parameters) change after the first prepare, and the
/// decode service runs from the server's start, before any training step (run 3b: every harness's opening answer eval decoded on the CPU)
pub struct Decode<'a> { decs: HashMap<u32, DecSess<'a>>, ds: Vec<(u32, usize, Slot, Layout)>, last_scan: std::time::Instant, used: HashMap<u32, std::time::Instant>,
                        pub steps: u64, pub act: u64, pub ms: f64 }
impl<'a> Decode<'a> {
    pub fn new() -> Self { Decode { decs: HashMap::new(), ds: Vec::new(), last_scan: std::time::Instant::now() - std::time::Duration::from_secs(1), used: HashMap::new(), steps: 0, act: 0, ms: 0.0 } }

    /// new decode slot files (scanned every 100 ms)
    fn scan(&mut self, dir: &str, r_: usize) {
        if self.last_scan.elapsed().as_millis() < 100 { return }
        self.last_scan = std::time::Instant::now();
        let Ok(rd) = std::fs::read_dir(dir) else { return };
        for e in rd.flatten() {
            let name = e.file_name().to_string_lossy().into_owned();
            let Some(rest) = name.strip_prefix("dslot-") else { continue };
            let Some((id, r)) = rest.split_once('-') else { continue };
            let (Ok(id), Ok(r)) = (id.parse::<u32>(), r.parse::<usize>()) else { continue };
            if r >= r_ || self.ds.iter().any(|(i, q, _, _)| *i == id && *q == r) { continue }
            let Ok(t) = std::fs::read_to_string(format!("{dir}/dlay-{id}.txt")) else { continue };
            let Ok(lay) = Layout::parse(&t) else { continue };
            if e.metadata().map(|m| m.len() as usize).unwrap_or(0) < lay.full_bytes() { continue }   // the client is still sizing it
            if let Ok(sl) = Slot::map(&format!("{dir}/{name}"), lay.full_bytes(), false) { self.ds.push((id, r, sl, lay)); }
        }
    }

    fn build(&mut self, gpu: &'a Gpu, dir: &str, r_: usize, id: u32, log: &mut dyn FnMut(String)) -> Result<(), String> {
        if self.decs.contains_key(&id) { return Ok(()) }
        if self.decs.len() >= 2 {                                              // at most 2 decode programs resident: drop the least recently used
            if let Some(k) = self.decs.keys().copied().min_by_key(|k| self.used.get(k).copied()) { self.decs.remove(&k); log(format!("[array] decode {k} released")); }
        }
        let cfg = std::fs::read_to_string(format!("{dir}/dcfg-{id}.json")).map_err(|e| format!("dcfg-{id}: {e}"))?;
        let cfg_r = format!("{{\"R\": {r_}, {}", cfg.trim_start().trim_start_matches('{'));
        let pd = format!("{dir}/dprog-{id}"); std::fs::create_dir_all(&pd).map_err(|e| e.to_string())?;
        std::fs::write(format!("{pd}/cfg.json"), &cfg_r).map_err(|e| e.to_string())?;
        let root = std::env::var("OMNI_GPU_ROOT").unwrap_or_else(|_| concat!(env!("CARGO_MANIFEST_DIR")).to_string());
        let out = std::process::Command::new(std::env::var("OMNI_GPU_PYTHON").unwrap_or("python3".into()))
            .arg(format!("{root}/gen/make_program.py")).arg(format!("{pd}/cfg.json")).arg(&pd).output().map_err(|e| format!("make_program: {e}"))?;
        if !out.status.success() { return Err(format!("make_program (decode): {}", String::from_utf8_lossy(&out.stderr))) }
        let text = std::fs::read_to_string(format!("{pd}/prog.txt")).map_err(|e| e.to_string())?;
        let io = parse_io(&std::fs::read_to_string(format!("{pd}/io.json")).map_err(|e| e.to_string())?);
        let mut lo = program::load(gpu, &text, "array-decode")?; lo.s.use_queue2();
        log(format!("[array] decode {id}: {r_} decoders × {DS} stations, {} passes, {:.1} MB resident (queue 2)", lo.s.passes(), lo.s.bytes() as f64 / 1e6));
        self.decs.insert(id, DecSess { s: lo.s, io }); Ok(())
    }

    /// serve every pending decode prepare / step (→ whether anything was served)
    pub fn serve(&mut self, gpu: &'a Gpu, dir: &str, r_: usize, log: &mut dyn FnMut(String)) -> Result<bool, String> {
        self.scan(dir, r_);
        let mut any = false;
        let fail = |sl: &Slot, e: &str, log: &mut dyn FnMut(String)| { log(format!("[array] decode error: {e}")); sl.word(11).store(1, Ordering::Release); sl.word(9).store(DS_ERR, Ordering::Release); };
        // prepares: the slot's weights → its replica, re-quantised
        for k in 0..self.ds.len() {
            if self.ds[k].2.word(9).load(Ordering::Acquire) != DS_PREP { continue }
            any = true; let id = self.ds[k].0;
            if let Err(e) = self.build(gpu, dir, r_, id, log) { fail(&self.ds[k].2, &e, log); continue }
            self.used.insert(id, std::time::Instant::now());
            let (_, r, sl, lay) = &self.ds[k]; let d = self.decs.get_mut(&id).unwrap();
            let mut o = lay.sections().1; let mut w: Vec<(usize, u64, &[u8])> = Vec::new();
            for (n, sz) in &lay.params { w.push((d.io[&format!("w:{n}")], (r * sz * 4) as u64, &*sl.bytes(o, sz * 4))); o += sz * 4; }
            if let Err(e) = d.s.write_at_many(&w).and_then(|_| d.s.step_seg(0)) { fail(sl, &e, log); continue }
            sl.word(9).store(DS_DONE, Ordering::Release);
        }
        // steps, per decoder config: every pending slot's stations in one GPU step
        let mut by: HashMap<u32, Vec<usize>> = HashMap::new();
        for (k, (id, _, sl, _)) in self.ds.iter().enumerate() { if sl.word(9).load(Ordering::Acquire) == DS_STEP { by.entry(*id).or_default().push(k); } }
        for (id, ks) in by {
            any = true; let t0 = std::time::Instant::now();
            let Some(d) = self.decs.get_mut(&id) else { for &k in &ks { fail(&self.ds[k].2, "decode step before prepare", log); } continue };
            self.used.insert(id, std::time::Instant::now());
            let v = self.ds[ks[0]].3.v; let n = r_ * DS;
            let (mut tok, mut kd, mut pp, mut pos, mut res) = (vec![0i32; n], vec![-1i32; n], vec![-1i32; n], vec![(DTMAX - 1) as i32; n], vec![0i32; n * 32]);
            let mut act: Vec<(usize, usize)> = Vec::new();
            for &k in &ks {
                let (_, r, sl, lay) = &self.ds[k]; let dm = lay.dec(); let g = |key: &str| { let (o, l) = dm[key]; sl.i32s(o, l).to_vec() };
                let (t_, k_, p_, q_, a_, z_) = (g("tok"), g("pkind"), g("pprop"), g("dpos"), g("act"), g("t25res"));
                for s in 0..DS { if a_[s] == 0 { continue }
                    let i = r * DS + s; tok[i] = t_[s]; kd[i] = k_[s]; pp[i] = p_[s]; pos[i] = q_[s]; res[i * 32..i * 32 + 32].copy_from_slice(&z_[s * 32..s * 32 + 32]); act.push((k, s)); }
            }
            let ds = &self.ds;
            let out = (|| -> Result<(Vec<Vec<u8>>, Vec<Vec<u8>>), String> {
                let w = [(d.io["tok"], 0u64, b32(&tok)), (d.io["pkind"], 0, b32(&kd)), (d.io["pprop"], 0, b32(&pp)), (d.io["dpos"], 0, b32(&pos)), (d.io["t25res"], 0, b32(&res))];
                let wr: Vec<(usize, u64, &[u8])> = w.iter().map(|(i, o, b)| (*i, *o, b.as_slice())).collect();
                d.s.write_at_many(&wr)?; d.s.step_seg(1)?;
                let small = d.s.read_at_many(&[(d.io["targ"], 0, (n * 4) as u64), (d.io["tmx"], 0, (n * 4) as u64), (d.io["t2nd"], 0, (n * 4) as u64),
                                               (d.io["ex"], 0, (n * 4) as u64), (d.io["pst"], 0, (n * 20) as u64), (d.io["pgw"], 0, (n * 8) as u64)])?;
                let rows: Vec<(usize, u64, u64)> = act.iter().map(|&(k, s)| (d.io["dlog"], (((ds[k].1 * DS + s) * v) * 4) as u64, (v * 4) as u64)).collect();
                Ok((small, d.s.read_at_many(&rows)?))
            })();
            match out {
                Err(e) => for &k in &ks { fail(&self.ds[k].2, &e, log); },
                Ok((small, lg)) => {
                    for (j, &(k, s)) in act.iter().enumerate() {
                        let (_, r, sl, lay) = &self.ds[k]; let dm = lay.dec(); let i = r * DS + s;
                        for (src, (key, pe)) in [("targ", 1usize), ("tmx", 1), ("t2nd", 1), ("ex", 1), ("pst", 5), ("pgw", 2)].into_iter().enumerate() {
                            let (o, _) = dm[key]; sl.bytes(o + s * pe * 4, pe * 4).copy_from_slice(&small[src][i * pe * 4..(i + 1) * pe * 4]);
                        }
                        let (o, _) = dm["dlog"]; sl.bytes(o + s * v * 4, v * 4).copy_from_slice(&lg[j]);
                    }
                    for &k in &ks { self.ds[k].2.word(9).store(DS_DONE, Ordering::Release); }
                }
            }
            self.steps += 1; self.act += act.len() as u64; self.ms += t0.elapsed().as_secs_f64() * 1e3;
        }
        Ok(any)
    }
}
