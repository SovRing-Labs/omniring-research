//! libomnitrain_gpu.so — GROW-RUN-0 G3: the THEAD engine's C ABI with the TRAINING STEP ON THE GPU (plan <notes>/worker/claude/<plan>).
//! `thead-learn` loads it as OMR_TRAIN_LIB and runs unchanged:
//!   · every school switch the harness sets (om_set_port / _tau / _data, _pointer, _router_simplex, _router_ce, _copy, _local, _route,
//!     _route_sat, _roles, _stage_data, _plates, _t25, _voicing, _harmony, _p3, _flags (spark), _avoid) is RECORDED here and forwarded to the
//!     CPU engine (libomnitrain_trial.so, a link dependency — any symbol this library does not define resolves there);
//!   · om_train_step runs the resident GPU step (gen/train_step.build_loop via gen/make_program.py, built on the first call): the CPU
//!     engine's weights are the truth — uploaded before each step, the updated weights written back after — so checkpoint loads, soups and
//!     growth done through om_param_ptr need nothing special; the Adam moments live on the GPU and follow om_snapshot / om_restore;
//!   · decoding, held-out loss, saving run on the CPU engine with the fresh weights.
//! A switch the GPU step does not carry (head_mode ≠ 0, ladder growth, OPT_MODE ≥ 1, bootstrap exits, HOLO memory without plates) sends
//! training back to the CPU engine and says so once. OMR_GPU=0 = always the CPU engine. OMNI_GPU_DEVICE = the device filter.
use std::collections::HashMap;
use std::ffi::{c_char, c_int, c_void, CStr};
use std::sync::Mutex;

type P = *mut c_void;
const RTLD_NOW: c_int = 2; const RTLD_NOLOAD: c_int = 4;
extern "C" { fn dlopen(f: *const c_char, m: c_int) -> P; fn dlsym(h: P, s: *const c_char) -> P; }

fn cpu() -> P {
    static H: Mutex<usize> = Mutex::new(0);
    let mut g = H.lock().unwrap();
    if *g == 0 {
        let h = unsafe { dlopen(c"libomnitrain_trial.so".as_ptr(), RTLD_NOW | RTLD_NOLOAD) };
        assert!(!h.is_null(), "omnitrain_gpu: the CPU engine libomnitrain_trial.so is not loaded (link dependency)");
        *g = h as usize;
    }
    *g as P
}
macro_rules! real { ($name:literal, $t:ty) => {{ let s = unsafe { dlsym(cpu(), concat!($name, "\0").as_ptr() as *const c_char) };
    assert!(!s.is_null(), concat!("omnitrain_gpu: CPU engine lacks ", $name)); unsafe { std::mem::transmute::<P, $t>(s) } }}; }

#[derive(Default)]
struct Rec {
    dims: [i32; 5], primes: Vec<i32>,
    port: Option<(i32, f32)>, tau: f32, hard: i32, pointer: bool, rce: f32, copy: bool,
    local: Option<i32>, route: f32, sat: f32, roles: Option<Vec<u32>>, plates: Option<i32>,
    t25: Option<(usize, [u8; 32], i32)>, voicing: bool, harm: Option<(f32, f32)>, p3: Option<(f32, i32)>, spark: f32,
    pkind: Vec<i32>, pprop: Vec<i32>, pstage: Vec<i32>, avoid: Vec<i32>,
    unsupported: Vec<String>, said: bool, gpu: Option<Gpu>, snap: Option<(Vec<Vec<u8>>, u64)>, cli: Option<Client>,
    fwd: Option<Fwd>, hits: Vec<i8>, hits_gpu: bool, exit: f32,
}
/// the forward alone on the GPU (OMR_GPU_EVAL=1: the held-out eval's om_forward_loss / om_tok_hit; GROW-RUN-0) — weights uploaded when they change
struct Fwd { s: omni_gpu::session::Session<'static>, io: HashMap<String, usize>, b: i32, t: i32, last: Vec<u8> }
unsafe impl Send for Fwd {}   // one session per engine handle, used under RECS' lock (as Gpu)
/// client mode (GROW-RUN-0 G3b-4): this harness's slot in the array server (omni-gpu serve, src/array.rs)
struct Client { slot: omni_gpu::array::Slot, lay: omni_gpu::array::Layout, last: Vec<u8>, step: u64, lazy: bool, stale: bool }
struct Gpu { s: omni_gpu::session::Session<'static>, io: HashMap<String, usize>, names: Vec<String>, sizes: Vec<usize>, b: i32, t: i32, step: u64 }
unsafe impl Send for Gpu {}
static RECS: Mutex<Vec<(usize, Rec)>> = Mutex::new(Vec::new());

fn with<R>(h: P, f: impl FnOnce(&mut Rec) -> R) -> R {
    let mut v = RECS.lock().unwrap();
    let i = match v.iter().position(|(k, _)| *k == h as usize) { Some(i) => i, None => { v.push((h as usize, Rec { spark: 1e30, tau: 1.0, ..Default::default() })); v.len() - 1 } };
    f(&mut v[i].1)
}
fn note(h: P, what: &str) { with(h, |r| if !r.unsupported.iter().any(|x| x == what) { r.unsupported.push(what.into()) }); }

// ── recorded switches (forwarded to the CPU engine) ─────────────────────────────────────────────────────────────────────────────
#[no_mangle] pub extern "C" fn om_create(v: c_int, d: c_int, l: c_int, hh: c_int, t: c_int, primes: *const c_int, np: c_int, seed: u64) -> P {
    let f = real!("om_create", extern "C" fn(c_int, c_int, c_int, c_int, c_int, *const c_int, c_int, u64) -> P);
    let h = f(v, d, l, hh, t, primes, np, seed);
    let pr = unsafe { std::slice::from_raw_parts(primes, np.max(0) as usize) }.to_vec();
    with(h, |r| { r.dims = [v, d, l, hh, t]; r.primes = pr; }); h
}
#[no_mangle] pub extern "C" fn om_set_port(h: P, k: c_int, theta: f32) -> c_int { let r_ = real!("om_set_port", extern "C" fn(P, c_int, f32) -> c_int)(h, k, theta); if r_ > 0 { with(h, |r| r.port = Some((k, theta))); } r_ }
#[no_mangle] pub extern "C" fn om_set_port_tau(h: P, tau: f32, hard: c_int) { real!("om_set_port_tau", extern "C" fn(P, f32, c_int))(h, tau, hard); with(h, |r| { r.tau = tau; r.hard = hard; }); }
#[no_mangle] pub extern "C" fn om_set_port_data(h: P, k: *const c_int, p: *const c_int, n: c_int) {
    real!("om_set_port_data", extern "C" fn(P, *const c_int, *const c_int, c_int))(h, k, p, n);
    let (kk, pp) = unsafe { (std::slice::from_raw_parts(k, n as usize).to_vec(), std::slice::from_raw_parts(p, n as usize).to_vec()) };
    with(h, |r| { r.pkind = kk; r.pprop = pp; });
}
#[no_mangle] pub extern "C" fn om_set_pointer(h: P, on: c_int, b0: f32) -> c_int { let r_ = real!("om_set_pointer", extern "C" fn(P, c_int, f32) -> c_int)(h, on, b0); with(h, |r| r.pointer = on != 0 && r_ > 0); r_ }
#[no_mangle] pub extern "C" fn om_set_router_simplex(h: P, norm: f32, seed: u64) -> f32 { real!("om_set_router_simplex", extern "C" fn(P, f32, u64) -> f32)(h, norm, seed) }
#[no_mangle] pub extern "C" fn om_set_router_ce(h: P, w: f32) { real!("om_set_router_ce", extern "C" fn(P, f32))(h, w); with(h, |r| r.rce = w.max(0.0)); }
#[no_mangle] pub extern "C" fn om_set_copy(h: P, on: c_int, b0: f32) -> c_int { let r_ = real!("om_set_copy", extern "C" fn(P, c_int, f32) -> c_int)(h, on, b0); with(h, |r| r.copy = on != 0); r_ }
#[no_mangle] pub extern "C" fn om_set_local(h: P, on: c_int, stride: c_int) -> c_int {
    let r_ = real!("om_set_local", extern "C" fn(P, c_int, c_int) -> c_int)(h, on, stride);
    if r_ == 0 { with(h, |r| r.local = if on != 0 { Some(stride.max(1)) } else { None }); if on != 0 && on != 2 { note(h, "local rule mode ≠ 2"); } } r_
}
#[no_mangle] pub extern "C" fn om_set_route(h: P, th: f32) -> c_int { let r_ = real!("om_set_route", extern "C" fn(P, f32) -> c_int)(h, th); if r_ == 0 { with(h, |r| r.route = th.max(0.0)); } r_ }
#[no_mangle] pub extern "C" fn om_set_exit(h: P, th: f32) { real!("om_set_exit", extern "C" fn(P, f32))(h, th); with(h, |r| r.exit = th.max(0.0)); }
#[no_mangle] pub extern "C" fn om_set_route_sat(h: P, s: f32) { real!("om_set_route_sat", extern "C" fn(P, f32))(h, s); with(h, |r| r.sat = s.max(0.0)); }
#[no_mangle] pub extern "C" fn om_set_roles(h: P, m: *const u32, l: c_int) {
    real!("om_set_roles", extern "C" fn(P, *const u32, c_int))(h, m, l);
    let v = unsafe { std::slice::from_raw_parts(m, l.max(0) as usize) }.to_vec(); with(h, |r| r.roles = Some(v));
}
#[no_mangle] pub extern "C" fn om_set_stage_data(h: P, st: *const c_int, n: c_int) {
    real!("om_set_stage_data", extern "C" fn(P, *const c_int, c_int))(h, st, n);
    let v = unsafe { std::slice::from_raw_parts(st, n as usize) }.to_vec(); with(h, |r| r.pstage = v);
}
#[no_mangle] pub extern "C" fn om_clear_stage_data(h: P) { real!("om_clear_stage_data", extern "C" fn(P))(h); with(h, |r| r.pstage.clear()); }
#[no_mangle] pub extern "C" fn om_set_plates(h: P, on: c_int, eos: c_int) -> c_int {
    let r_ = real!("om_set_plates", extern "C" fn(P, c_int, c_int) -> c_int)(h, on, eos);
    with(h, |r| r.plates = if on != 0 { Some(eos) } else { None }); if on == 2 { note(h, "plates mode 2 (masked reference)"); } r_
}
#[no_mangle] pub extern "C" fn om_set_t25(h: P, kernel: P, mods: *const u8, eos: c_int) -> c_int {
    let r_ = real!("om_set_t25", extern "C" fn(P, P, *const u8, c_int) -> c_int)(h, kernel, mods, eos);
    with(h, |r| r.t25 = if kernel.is_null() { None } else { let mut m = [0u8; 32]; unsafe { std::ptr::copy_nonoverlapping(mods, m.as_mut_ptr(), 32) }; Some((kernel as usize, m, eos)) }); r_
}
#[no_mangle] pub extern "C" fn om_set_voicing(h: P, on: c_int) { real!("om_set_voicing", extern "C" fn(P, c_int))(h, on); with(h, |r| r.voicing = on != 0); }
#[no_mangle] pub extern "C" fn om_set_harmony(h: P, on: c_int, lam: f32, kap: f32) {
    real!("om_set_harmony", extern "C" fn(P, c_int, f32, f32))(h, on, lam, kap); with(h, |r| r.harm = if on != 0 { Some((lam.max(0.0), kap)) } else { None });
}
#[no_mangle] pub extern "C" fn om_set_p3(h: P, p: f32, full: c_int, compact: c_int) { real!("om_set_p3", extern "C" fn(P, f32, c_int, c_int))(h, p, full, compact); with(h, |r| r.p3 = if p > 0.0 { Some((p, full.max(1))) } else { None }); }
#[no_mangle] pub extern "C" fn om_set_flags(h: P, fixed_emb: c_int, spark: f32, periods: *const c_int) {
    real!("om_set_flags", extern "C" fn(P, c_int, f32, *const c_int))(h, fixed_emb, spark, periods);
    let l = with(h, |r| { r.spark = spark; r.dims[2] });
    if fixed_emb != 0 { note(h, "fixed embedding"); }
    if !periods.is_null() { let p = unsafe { std::slice::from_raw_parts(periods, l.max(0) as usize) }; if p.iter().any(|&x| x != 1) { note(h, "frozen blocks (periods ≠ 1)"); } }
}
#[no_mangle] pub extern "C" fn om_set_avoid(h: P, a: *const c_int, n: c_int) -> c_int {
    let r_ = real!("om_set_avoid", extern "C" fn(P, *const c_int, c_int) -> c_int)(h, a, n);
    let v = if n > 0 && !a.is_null() { unsafe { std::slice::from_raw_parts(a, n as usize) }.to_vec() } else { Vec::new() }; with(h, |r| r.avoid = v); r_
}
#[no_mangle] pub extern "C" fn om_set_head_mode(h: P, mode: c_int, x: c_int) { real!("om_set_head_mode", extern "C" fn(P, c_int, c_int))(h, mode, x); if mode != 0 { note(h, "head_mode ≠ 0"); } }
#[no_mangle] pub extern "C" fn om_set_active(h: P, n: c_int, silence: c_int) -> c_int {
    let r_ = real!("om_set_active", extern "C" fn(P, c_int, c_int) -> c_int)(h, n, silence);
    let l = with(h, |r| r.dims[2]); if r_ > 0 && r_ < l { note(h, "ladder: active blocks < L"); } r_
}
#[no_mangle] pub extern "C" fn om_set_opt(h: P, mode: c_int, wd: f32, b1: f32, b2: f32, clip: f32, kappa: f32, cthr: c_int, leak: c_int) {
    real!("om_set_opt", extern "C" fn(P, c_int, f32, f32, f32, f32, f32, c_int, c_int))(h, mode, wd, b1, b2, clip, kappa, cthr, leak);
    if mode != 0 { note(h, "OPT_MODE ≥ 1 (trit flips)"); }
    if (wd - 0.1).abs() > 1e-7 || (b1 - 0.9).abs() > 1e-7 || (b2 - 0.95).abs() > 1e-7 || (clip - 1.0).abs() > 1e-7 { note(h, "AdamW settings ≠ wd 0.1 b1 0.9 b2 0.95 clip 1"); }
}
#[no_mangle] pub extern "C" fn om_set_boot(h: P, th: f32) { real!("om_set_boot", extern "C" fn(P, f32))(h, th); if th > 0.0 { note(h, "bootstrap exits"); } }

// ── the moments follow the engine's snapshot / restore ─────────────────────────────────────────────────────────────────────────
#[no_mangle] pub extern "C" fn om_snapshot(h: P) {
    fresh(h); real!("om_snapshot", extern "C" fn(P))(h);
    with(h, |r| if let Some(c) = r.cli.as_ref() { slot_op(c, omni_gpu::array::ST_SNAP); r.snap = Some((Vec::new(), c.step)); });
    with(h, |r| if let Some(g) = r.gpu.as_mut() {
        let mut mv = Vec::new();
        for n in &g.names { for k in ["m", "v"] { mv.push(g.s.read(g.io[&format!("{k}:{n}")]).expect("snapshot read")); } }
        r.snap = Some((mv, g.step));
    });
}
#[no_mangle] pub extern "C" fn om_restore(h: P) -> c_int {
    let r_ = real!("om_restore", extern "C" fn(P) -> c_int)(h);
    if r_ == 1 { with(h, |r| if let (Some(c), Some((_, st))) = (r.cli.as_mut(), r.snap.as_ref()) { slot_op(c, omni_gpu::array::ST_REST); c.step = *st;
        c.last.clear(); c.stale = false; }); }   // the restored CPU weights are the truth: uploaded on the next step (lazy copies would miss it)
    if r_ == 1 { with(h, |r| if let (Some(g), Some((mv, st))) = (r.gpu.as_mut(), r.snap.as_ref()) {
        let mut i = 0; for n in g.names.clone() { for k in ["m", "v"] { g.s.write(g.io[&format!("{k}:{n}")], &mv[i]).expect("restore write"); i += 1; } }
        g.step = *st;
    }); }
    r_
}

// ── the training step ──────────────────────────────────────────────────────────────────────────────────────────────────────
#[no_mangle] pub extern "C" fn om_train_step(h: P, x: *const c_int, y: *const c_int, b: c_int, t: c_int, lr: f32) -> f32 {
    let cpu_step = real!("om_train_step", extern "C" fn(P, *const c_int, *const c_int, c_int, c_int, f32) -> f32);
    let off = std::env::var("OMR_GPU").map(|v| v == "0").unwrap_or(false);
    let blocked = with(h, |r| { let u = r.unsupported.clone(); if !u.is_empty() && !r.said { eprintln!("[omnitrain_gpu] training on the CPU engine: the GPU step does not carry {u:?}"); r.said = true; } !u.is_empty() });
    if off || blocked { return cpu_step(h, x, y, b, t, lr); }
    let step = if std::env::var("OMR_GPU_SERVER").is_ok() { client_step(h, x, y, b, t, lr) } else { gpu_step(h, x, y, b, t, lr) };
    match step {
        Ok(l) => l,
        Err(e) => { eprintln!("[omnitrain_gpu] GPU step failed ({e}) — this step on the CPU engine"); note(h, "GPU failure"); cpu_step(h, x, y, b, t, lr) }
    }
}

fn params(h: P) -> Vec<(String, *mut f32, usize)> {
    let np = real!("om_nparams", extern "C" fn(P) -> c_int)(h);
    let name = real!("om_param_name", extern "C" fn(P, c_int) -> *const c_char);
    let size = real!("om_param_size", extern "C" fn(P, c_int) -> i64);
    let ptr = real!("om_param_ptr", extern "C" fn(P, c_int) -> *mut f32);
    (0..np).map(|i| (unsafe { CStr::from_ptr(name(h, i)) }.to_string_lossy().into_owned(), ptr(h, i), size(h, i) as usize)).collect()
}

fn build(h: P, b: i32, t: i32) -> Result<Gpu, String> {
    let ps = params(h); let cfg = cfg_of(h, b, t, &ps);
    let root = std::env::var("OMNI_GPU_ROOT").unwrap_or_else(|_| concat!(env!("CARGO_MANIFEST_DIR"), "/..").to_string());
    let dir = format!("{}/omnitrain_gpu-{}-{}", std::env::var("TMPDIR").unwrap_or("/tmp".into()), std::process::id(), h as usize);
    std::fs::create_dir_all(&dir).map_err(|e| format!("{dir}: {e}"))?;
    std::fs::write(format!("{dir}/cfg.json"), &cfg).map_err(|e| e.to_string())?;
    let out = std::process::Command::new(std::env::var("OMNI_GPU_PYTHON").unwrap_or("python3".into()))
        .arg(format!("{root}/gen/make_program.py")).arg(format!("{dir}/cfg.json")).arg(&dir).output().map_err(|e| format!("make_program: {e}"))?;
    if !out.status.success() { return Err(format!("make_program: {}", String::from_utf8_lossy(&out.stderr))); }
    let text = std::fs::read_to_string(format!("{dir}/prog.txt")).map_err(|e| e.to_string())?;
    let io = parse_io(&std::fs::read_to_string(format!("{dir}/io.json")).map_err(|e| e.to_string())?);
    let gpu: &'static omni_gpu::run::Gpu = Box::leak(Box::new(omni_gpu::run::Gpu::open(std::env::var("OMNI_GPU_DEVICE").ok().as_deref())?));
    let lo = omni_gpu::program::load(gpu, &text, "train-step")?;
    eprintln!("[omnitrain_gpu] training step on {} — {} passes, {:.1} MB resident", gpu.name, lo.s.passes(), lo.s.bytes() as f64 / 1e6);
    Ok(Gpu { s: lo.s, io, names: ps.iter().map(|p| p.0.clone()).collect(), sizes: ps.iter().map(|p| p.2).collect(), b, t, step: 0 })
}

/// the program's config from the switches this harness turned on (make_program.py CFG)
fn cfg_of(h: P, b: i32, t: i32, ps: &[(String, *mut f32, usize)]) -> String {
    with(h, |r| {
        let [v, d, l, hh, _] = r.dims; let mut sw = Vec::new(); let mut aux = Vec::new();
        if let Some((_, mods, _)) = r.t25 {
            sw.push("\"t25\": true".to_string());
            let lane: Vec<String> = (0..((d / hh) / 2) as usize).map(|i| { let p = *r.primes.get(i).unwrap_or(&0);
                (0..32).find(|&k| mods[k] != 0 && mods[k] as i32 == p).map(|k| k as i64).unwrap_or(-1).to_string() }).collect();
            aux.push(format!("\"t25lane\": [{}]", lane.join(",")));
        }
        if r.voicing { sw.push("\"voice\": true".into()); }
        if let Some(eos) = r.plates { sw.push("\"plates\": true".into()); aux.push(format!("\"eos\": {eos}")); }
        if r.spark < 1e29 { sw.push(format!("\"spark\": {}", r.spark)); }
        if let Some((p, full)) = r.p3 { sw.push(format!("\"p3\": [{p}, {full}]")); }
        if let Some((lam, kap)) = r.harm { sw.push(format!("\"harm\": [{lam}, {kap}]")); }
        if let Some((k, th)) = r.port { sw.push(format!("\"port\": {{\"K\": {k}, \"theta\": {th}, \"tau\": {}, \"rce\": {}, \"hard\": {}}}", r.tau, r.rce, r.hard)); }
        if r.copy { sw.push("\"copy\": true".into()); }
        if let Some(s) = r.local {
            let roles = r.roles.as_ref().map(|m| format!("[{}]", m.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","))).unwrap_or("null".into());
            sw.push(format!("\"local\": {{\"S\": {s}, \"roles\": {roles}, \"route\": {}, \"sat\": {}}}", r.route, r.sat));
        }
        sw.push("\"avoid\": 1.0".into());                                     // always built: rows without a push feed −1 (identical maths)
        let pl: Vec<String> = ps.iter().map(|(n, _, s)| format!("[\"{n}\", {s}]")).collect();
        format!("{{\"dims\": {{\"V\": {v}, \"D\": {d}, \"L\": {l}, \"H\": {hh}, \"T\": {t}, \"B\": {b}}}, \"params\": [{}], \"sw\": {{{}}}, \"aux\": {{{}}}}}",
                pl.join(", "), sw.join(", "), aux.join(", "))
    })
}

fn parse_io(s: &str) -> HashMap<String, usize> {
    s.lines().filter_map(|l| { let l = l.trim().trim_end_matches(','); let (k, v) = l.rsplit_once(':')?;
        Some((k.trim().trim_matches('"').to_string(), v.trim().parse().ok()?)) }).collect()
}

fn i32b(v: &[i32]) -> Vec<u8> { v.iter().flat_map(|x| x.to_le_bytes()).collect() }
fn f32b(v: &[f32]) -> Vec<u8> { v.iter().flat_map(|x| x.to_le_bytes()).collect() }

/// the step's inputs besides x / y, computed exactly as for the library's own session: kinds, proposals, stages, avoid rows, T25 residues, row starts
fn inputs(r: &Rec, xs: &[i32], b: i32, t: i32) -> (Vec<i32>, Vec<i32>, Vec<i32>, Vec<i32>, Option<Vec<i32>>, Option<Vec<i32>>) {
    let n = (b * t) as usize; let hh = r.dims[3];
    let (pk, pp, pst, av) = (fill(&r.pkind, n), fill(&r.pprop, n), fill(&r.pstage, n), fill(&r.avoid, n));
    let t25 = r.t25.map(|(k, mods, eos)| {
        let mut ev = vec![0i64; n * 5]; let kinds = r.pkind.len() == n;
        for bb in 0..b as usize { let mut row = 0i64; for tt in 0..t as usize { let i = bb * t as usize + tt; let k_ = if kinds { r.pkind[i] } else { -1 };
            ev[i * 5] = tt as i64; ev[i * 5 + 1] = xs[i] as i64; ev[i * 5 + 2] = if (0..64).contains(&k_) { k_ as i64 } else { 36 }; ev[i * 5 + 4] = row;
            if xs[i] == eos { row += 1; } } }
        let (mut res, zero, mut tw) = (vec![0u8; n * 32], vec![0u8; n * 32], vec![0u8; n * 32]);
        let f: extern "C" fn(*const i64, usize, *mut u8, *const u8, *mut u8, *const u8) = unsafe { std::mem::transmute(k) };
        f(ev.as_ptr(), n, res.as_mut_ptr(), zero.as_ptr(), tw.as_mut_ptr(), mods.as_ptr());
        res.iter().map(|&u| u as i32).collect::<Vec<i32>>()
    });
    let rs = r.plates.map(|eos| { let mut o = vec![0i32; b as usize * hh as usize * t as usize];
        for bb in 0..b as usize { let mut st = 0; for tt in 0..t as usize { for k in 0..hh as usize { o[(bb * hh as usize + k) * t as usize + tt] = st; }
            if xs[bb * t as usize + tt] == eos { st = tt as i32 + 1; } } } o });
    (pk, pp, pst, av, t25, rs)
}

/// a lazy client's CPU copy brought up to the GPU's weights (before any CPU-side read of them)
fn fresh(h: P) {
    let need = with(h, |r| r.cli.as_ref().map(|c| c.stale).unwrap_or(false));
    if !need { return }
    let ps = params(h);
    with(h, |r| { let c = r.cli.as_mut().unwrap(); if !c.stale { return }
        slot_op(c, omni_gpu::array::ST_FETCH);
        let woff = c.lay.sections().1; let mut o = 0; let mut cur = Vec::with_capacity(c.lay.wfloats * 4);
        for (_, ptr, size) in &ps { let b = c.slot.bytes(woff + o, size * 4); unsafe { std::ptr::copy_nonoverlapping(b.as_ptr(), *ptr as *mut u8, size * 4) }; cur.extend_from_slice(b); o += size * 4; }
        c.last = cur; c.stale = false; });
}
#[no_mangle] pub extern "C" fn om_param_ptr(h: P, i: c_int) -> *mut f32 { fresh(h); real!("om_param_ptr", extern "C" fn(P, c_int) -> *mut f32)(h, i) }
#[no_mangle] pub extern "C" fn om_sync_latent(h: P) { fresh(h); real!("om_sync_latent", extern "C" fn(P))(h) }

fn slot_op(c: &Client, op: u32) {
    use std::sync::atomic::Ordering;
    c.slot.word(0).store(op, Ordering::Release);
    while c.slot.word(0).load(Ordering::Acquire) != omni_gpu::array::ST_OPDONE { std::thread::sleep(std::time::Duration::from_micros(100)); }
    c.slot.word(0).store(omni_gpu::array::ST_IDLE, Ordering::Release);
}

/// connect this harness to its slot of the array server. bt = Some((B, T)) from a training step (slot 0 then writes the server's cfg.json and
/// waits for it); None from a decode prepare: connects only when the server is already up (else the caller decodes on the CPU)
fn connect(h: P, bt: Option<(i32, i32)>, ps: &[(String, *mut f32, usize)]) -> Result<(), String> {
    use omni_gpu::array::*; use std::sync::atomic::Ordering;
    let dir = std::env::var("OMR_GPU_SERVER").unwrap(); let slot: usize = std::env::var("OMR_GPU_SLOT").ok().and_then(|v| v.parse().ok()).unwrap_or(0);
    let ready = format!("{dir}/ready");
    match bt {
        Some((b, t)) => {
            if slot == 0 && !std::path::Path::new(&ready).exists() { let cfg = cfg_of(h, b, t, ps); std::fs::write(format!("{dir}/cfg.json.tmp"), &cfg).map_err(|e| e.to_string())?;
                           std::fs::rename(format!("{dir}/cfg.json.tmp"), format!("{dir}/cfg.json")).map_err(|e| e.to_string())?; }
            let t0 = std::time::Instant::now();
            while !std::path::Path::new(&ready).exists() {
                if t0.elapsed().as_secs() > 600 { return Err("array server not ready after 600 s".into()) }
                std::thread::sleep(std::time::Duration::from_millis(50));
            }
        }
        None => if !std::path::Path::new(&ready).exists() { return Err("array server not up yet".into()) },
    }
    let lay = Layout::parse(&std::fs::read_to_string(format!("{dir}/prog/array.txt")).map_err(|e| e.to_string())?)?;
    if lay.params.len() != ps.len() { return Err(format!("array server layout {} params ≠ this harness's {}", lay.params.len(), ps.len())) }
    let sl = Slot::map(&format!("{dir}/slot{slot}"), lay.full_bytes(), false)?; sl.word(7).store(1, Ordering::Release);
    let lazy = std::env::var("OMR_GPU_LAZY").map(|v| v != "0").unwrap_or(true);   // weights stay on the GPU; fetched when the CPU side reads them
    sl.word(8).store(lazy as u32, Ordering::Release);
    eprintln!("[omnitrain_gpu] connected to the array server {dir} slot {slot}");
    with(h, |r| r.cli = Some(Client { slot: sl, lay, last: Vec::new(), step: 0, lazy, stale: false }));
    Ok(())
}

/// client mode: hand this harness's step to the array server (src/array.rs) — same inputs as gpu_step, weights only when the engine changed them
fn client_step(h: P, x: *const c_int, y: *const c_int, b: c_int, t: c_int, lr: f32) -> Result<f32, String> {
    use omni_gpu::array::*; use std::sync::atomic::Ordering;
    let n = (b * t) as usize; let (xs, ys) = unsafe { (std::slice::from_raw_parts(x, n).to_vec(), std::slice::from_raw_parts(y, n).to_vec()) };
    let ps = params(h);
    if with(h, |r| r.cli.is_none()) { connect(h, Some((b, t)), &ps)?; }
    if with(h, |r| r.cli.as_ref().map(|c| c.lay.n != n).unwrap_or(true)) { return Err(format!("array server layout n ≠ this harness's {n}")) }
    with(h, |r| -> Result<f32, String> {
        let (pk, pp, pst, av, t25, rs) = inputs(r, &xs, b, t);
        let c = r.cli.as_mut().unwrap(); let (secs, woff) = c.lay.sections();
        for &(name, off, len) in &secs {
            let src: Option<&[i32]> = match name { "x" => Some(&xs), "y" => Some(&ys), "pkind" => Some(&pk), "pprop" => Some(&pp), "pstage" => Some(&pst),
                "pavoid" => Some(&av), "t25res" => t25.as_deref(), "rsBH" => rs.as_deref(), _ => None };
            if let Some(v) = src { c.slot.i32s(off, len.min(v.len())).copy_from_slice(&v[..len.min(v.len())]); }
        }
        c.slot.word(5).store(t25.is_some() as u32, Ordering::Release); c.slot.word(6).store(rs.is_some() as u32, Ordering::Release);
        let mut cur = Vec::with_capacity(c.lay.wfloats * 4);                 // the engine's weights: uploaded only when they changed on the CPU
        for (_, ptr, size) in &ps { cur.extend_from_slice(unsafe { std::slice::from_raw_parts(*ptr as *const u8, size * 4) }); }
        if cur != c.last { c.slot.bytes(woff, cur.len()).copy_from_slice(&cur); c.slot.word(1).store(1, Ordering::Release); }
        c.slot.word(2).store(lr.to_bits(), Ordering::Release); c.slot.word(4).store(c.step as u32, Ordering::Release);
        c.slot.word(0).store(ST_STEP, Ordering::Release);
        while c.slot.word(0).load(Ordering::Acquire) != ST_DONE { std::thread::sleep(std::time::Duration::from_micros(50)); }
        let loss = f32::from_bits(c.slot.word(3).load(Ordering::Acquire));
        if c.lazy { c.last = cur; c.stale = true; }                             // the CPU copy is behind the GPU until a read fetches it
        else {
            let back = c.slot.bytes(woff, cur.len()).to_vec(); let mut o = 0;
            for (_, ptr, size) in &ps { unsafe { std::ptr::copy_nonoverlapping(back.as_ptr().add(o), *ptr as *mut u8, size * 4) }; o += size * 4; }
            c.last = back;
        }
        c.slot.word(0).store(ST_IDLE, Ordering::Release); c.step += 1;
        Ok(loss)
    })
}

fn gpu_step(h: P, x: *const c_int, y: *const c_int, b: c_int, t: c_int, lr: f32) -> Result<f32, String> {
    let n = (b * t) as usize; let (xs, ys) = unsafe { (std::slice::from_raw_parts(x, n).to_vec(), std::slice::from_raw_parts(y, n).to_vec()) };
    let need = with(h, |r| r.gpu.as_ref().map(|g| g.b != b || g.t != t).unwrap_or(true));
    if need { let g = build(h, b, t)?; with(h, |r| r.gpu = Some(g)); }
    let ps = params(h);
    with(h, |r| -> Result<f32, String> {
        let [v, _d, _l, hh, _] = r.dims; let v = v as usize;
        let (pk, pp, pst, av) = (fill(&r.pkind, n), fill(&r.pprop, n), fill(&r.pstage, n), fill(&r.avoid, n));
        // T25 core addresses: the batch's events, ONE call of the rendered core (forward_backward:2075 t25_fill, fields off)
        let t25 = r.t25.map(|(k, mods, eos)| {
            let mut ev = vec![0i64; n * 5]; let kinds = r.pkind.len() == n;
            for bb in 0..b as usize { let mut row = 0i64; for tt in 0..t as usize { let i = bb * t as usize + tt; let k_ = if kinds { r.pkind[i] } else { -1 };
                ev[i * 5] = tt as i64; ev[i * 5 + 1] = xs[i] as i64; ev[i * 5 + 2] = if (0..64).contains(&k_) { k_ as i64 } else { 36 }; ev[i * 5 + 4] = row;
                if xs[i] == eos { row += 1; } } }
            let (mut res, zero, mut tw) = (vec![0u8; n * 32], vec![0u8; n * 32], vec![0u8; n * 32]);
            let f: extern "C" fn(*const i64, usize, *mut u8, *const u8, *mut u8, *const u8) = unsafe { std::mem::transmute(k) };
            f(ev.as_ptr(), n, res.as_mut_ptr(), zero.as_ptr(), tw.as_mut_ptr(), mods.as_ptr());
            res.iter().map(|&u| u as i32).collect::<Vec<i32>>()
        });
        let rs = r.plates.map(|eos| { let mut o = vec![0i32; b as usize * hh as usize * t as usize];
            for bb in 0..b as usize { let mut st = 0; for tt in 0..t as usize { for k in 0..hh as usize { o[(bb * hh as usize + k) * t as usize + tt] = st; }
                if xs[bb * t as usize + tt] == eos { st = tt as i32 + 1; } } } o });
        let g = r.gpu.as_mut().ok_or("no GPU step")?;
        // the embedding scatter's grouping: positions sorted by token (stable), each token's start
        let mut order: Vec<i32> = (0..n as i32).collect(); order.sort_by_key(|&i| xs[i as usize]);
        let mut est = vec![0i32; v + 1]; for &tk in &xs { est[tk as usize + 1] += 1; } for i in 0..v { est[i + 1] += est[i]; }
        let (b1, b2) = (0.9f32, 0.95f32); let bc1 = 1.0f32 - b1.powf((g.step + 1) as f32); let bc2 = 1.0f32 - b2.powf((g.step + 1) as f32);
        let sc = [0.0f32, lr, 0.1, b1, b2, lr / bc1, bc2.sqrt(), 1e-8];
        let w = |g: &mut Gpu, k: &str, bytes: Vec<u8>| -> Result<(), String> { if let Some(&i) = g.io.get(k) { g.s.write(i, &bytes)?; } Ok(()) };
        w(g, "x", i32b(&xs))?; w(g, "y", i32b(&ys))?; w(g, "eord", i32b(&order))?; w(g, "est", i32b(&est))?; w(g, "sc", f32b(&sc))?;
        w(g, "acc", vec![0u8; 8])?; w(g, "stepv", i32b(&[g.step as i32]))?; w(g, "pkind", i32b(&pk))?; w(g, "pprop", i32b(&pp))?;
        w(g, "pstage", i32b(&pst))?; w(g, "pavoid", i32b(&av))?;
        if let Some(t25) = t25 { w(g, "t25res", i32b(&t25))?; }
        if let Some(rs) = rs { w(g, "rsBH", i32b(&rs))?; }
        for (name, ptr, size) in &ps {                                       // the engine's weights are the truth: in before the step …
            let bytes = unsafe { std::slice::from_raw_parts(*ptr as *const u8, size * 4) }; g.s.write(g.io[&format!("w:{name}")], bytes)?;
        }
        g.s.step(1)?;
        let lb = g.s.read(g.io["loss"])?; let loss = f32::from_le_bytes([lb[0], lb[1], lb[2], lb[3]]);
        for (name, ptr, size) in &ps {                                       // … and the updated weights back after it
            let bytes = g.s.read(g.io[&format!("w:{name}")])?; unsafe { std::ptr::copy_nonoverlapping(bytes.as_ptr(), *ptr as *mut u8, size * 4) };
        }
        g.step += 1; let _ = &g.sizes; Ok(loss)
    })
}
fn fill(v: &[i32], n: usize) -> Vec<i32> { if v.len() == n { v.to_vec() } else { vec![-1; n] } }

// ── the forward alone on the GPU: the held-out eval (OMR_GPU_EVAL=1) ─────────────────────────────────────────────────────────
#[no_mangle] pub extern "C" fn om_forward_loss(h: P, x: *const c_int, y: *const c_int, b: c_int, t: c_int) -> f32 {
    fresh(h); let cpu = real!("om_forward_loss", extern "C" fn(P, *const c_int, *const c_int, c_int, c_int) -> f32);
    let on = std::env::var("OMR_GPU_EVAL").map(|v| v == "1").unwrap_or(false);
    let blocked = with(h, |r| { r.hits_gpu = false; !r.unsupported.is_empty() });
    if !on || blocked { return cpu(h, x, y, b, t); }
    match fwd_step(h, x, y, b, t) {
        Ok(l) => l,
        Err(e) => { eprintln!("[omnitrain_gpu] GPU forward failed ({e}) — the CPU engine"); note(h, "GPU forward failure"); cpu(h, x, y, b, t) }
    }
}
#[no_mangle] pub extern "C" fn om_tok_hit(h: P) -> *const i8 {
    let gpu = with(h, |r| if r.hits_gpu { Some(r.hits.as_ptr()) } else { None });
    gpu.unwrap_or_else(|| real!("om_tok_hit", extern "C" fn(P) -> *const i8)(h))
}

fn fwd_step(h: P, x: *const c_int, y: *const c_int, b: c_int, t: c_int) -> Result<f32, String> {
    let n = (b * t) as usize; let (xs, ys) = unsafe { (std::slice::from_raw_parts(x, n).to_vec(), std::slice::from_raw_parts(y, n).to_vec()) };
    let ps = params(h);
    if with(h, |r| r.fwd.as_ref().map(|f| f.b != b || f.t != t).unwrap_or(true)) {
        let cfg = cfg_of(h, b, t, &ps); let cfg = format!("{{\"fwd\": true, {}", cfg.trim_start().trim_start_matches('{'));
        let root = std::env::var("OMNI_GPU_ROOT").unwrap_or_else(|_| concat!(env!("CARGO_MANIFEST_DIR"), "/..").to_string());
        let dir = format!("{}/omnitrain_fwd-{}-{}-{b}x{t}", std::env::var("TMPDIR").unwrap_or("/tmp".into()), std::process::id(), h as usize);
        std::fs::create_dir_all(&dir).map_err(|e| format!("{dir}: {e}"))?; std::fs::write(format!("{dir}/cfg.json"), &cfg).map_err(|e| e.to_string())?;
        let out = std::process::Command::new(std::env::var("OMNI_GPU_PYTHON").unwrap_or("python3".into()))
            .arg(format!("{root}/gen/make_program.py")).arg(format!("{dir}/cfg.json")).arg(&dir).output().map_err(|e| format!("make_program: {e}"))?;
        if !out.status.success() { return Err(format!("make_program (forward): {}", String::from_utf8_lossy(&out.stderr))); }
        let text = std::fs::read_to_string(format!("{dir}/prog.txt")).map_err(|e| e.to_string())?;
        let io = parse_io(&std::fs::read_to_string(format!("{dir}/io.json")).map_err(|e| e.to_string())?);
        let gpu = device()?; let lo = omni_gpu::program::load(gpu, &text, "forward")?;
        eprintln!("[omnitrain_gpu] forward on {} — {b}×{t}, {} passes, {:.1} MB resident", gpu.name, lo.s.passes(), lo.s.bytes() as f64 / 1e6);
        with(h, |r| r.fwd = Some(Fwd { s: lo.s, io, b, t, last: Vec::new() }));
    }
    with(h, |r| -> Result<f32, String> {
        let (pk, pp, pst, av, t25, rs) = inputs(r, &xs, b, t); let v = r.dims[0] as usize;
        let f = r.fwd.as_mut().unwrap();
        let mut order: Vec<i32> = (0..n as i32).collect(); order.sort_by_key(|&i| xs[i as usize]);
        let mut est = vec![0i32; v + 1]; for &tk in &xs { est[tk as usize + 1] += 1; } for i in 0..v { est[i + 1] += est[i]; }
        let mut w: Vec<(usize, u64, Vec<u8>)> = Vec::new();
        let mut put = |k: &str, b_: Vec<u8>| { if let Some(&i) = f.io.get(k) { w.push((i, 0, b_)); } };
        put("x", i32b(&xs)); put("y", i32b(&ys)); put("eord", i32b(&order)); put("est", i32b(&est)); put("pkind", i32b(&pk)); put("pprop", i32b(&pp));
        put("pstage", i32b(&pst)); put("pavoid", i32b(&av)); put("stepv", i32b(&[0]));
        if let Some(t25) = &t25 { put("t25res", i32b(t25)); } if let Some(rs) = &rs { put("rsBH", i32b(rs)); }
        let mut cur = Vec::new(); for (_, ptr, size) in &ps { cur.extend_from_slice(unsafe { std::slice::from_raw_parts(*ptr as *const u8, size * 4) }); }
        if cur != f.last { let mut o = 0; for (name, _, size) in &ps { w.push((f.io[&format!("w:{name}")], 0, cur[o..o + size * 4].to_vec())); o += size * 4; } f.last = cur; }
        let wr: Vec<(usize, u64, &[u8])> = w.iter().map(|(i, o, b_)| (*i, *o, b_.as_slice())).collect();
        f.s.write_at_many(&wr)?; f.s.step(1)?;
        let rd = f.s.read_at_many(&[(f.io["loss"], 0, 4), (f.io["hit"], 0, (n * 4) as u64)])?;
        let loss = f32::from_le_bytes([rd[0][0], rd[0][1], rd[0][2], rd[0][3]]);
        r.hits = rd[1].chunks_exact(4).map(|c| if f32::from_le_bytes([c[0], c[1], c[2], c[3]]) != 0.0 { 1i8 } else { 0i8 }).collect(); r.hits_gpu = true;
        Ok(loss)
    })
}

/// one opened device per process for the forward programs (a new Gpu per shape leaked device handles: 4.4 GB on the A40, E1 first run)
fn device() -> Result<&'static omni_gpu::run::Gpu, String> {
    static DEV: Mutex<usize> = Mutex::new(0);
    let mut g = DEV.lock().unwrap();
    if *g == 0 { *g = Box::leak(Box::new(omni_gpu::run::Gpu::open(std::env::var("OMNI_GPU_DEVICE").ok().as_deref())?)) as *const omni_gpu::run::Gpu as usize; }
    Ok(unsafe { &*(*g as *const omni_gpu::run::Gpu) })
}

// ── THE HARNESS DECODE ON THE GPU (OMR_GPU_DECODE=1; gen/decode_step.py) ─────────────────────────────────────────────────────────
// om_decx_new hands out OUR decoder (it keeps a real CPU decoder for anything the GPU step does not carry). Every om_decx_step from the
// station threads joins the next GPU step: the first caller to find the GPU free runs one step for every pending decoder (group commit),
// the rest wait for theirs. The weights are uploaded + re-quantised (segment 0) on om_dec_prepare — exactly when the CPU engine
// re-quantises its own (dec_prepare); a step runs segment 1.
const DSLOTS: usize = 16; const DTMAX: usize = 1024;   // a longer decode falls back to the CPU decoder (its history replayed), never aborts
struct GDec { h: usize, cpu: usize, slot: usize, pos: i32, t25row: i64, router: i32, gate: f32, exits: Vec<i64>, logits: Vec<f32>, rows: i64,
              pend: bool, done: bool, inp: (i32, i32, i32), out: (i32, f32, bool), hist: Vec<(i32, i32, i32)>, on_cpu: bool }
struct DecGpu { s: omni_gpu::session::Session<'static>, io: HashMap<String, usize>, v: usize, l: usize, eos: i32, prepped: bool, cfg: String }
unsafe impl Send for DecGpu {}
/// server mode (OMR_GPU_SERVER): the decoders run in the array server's decode service (src/array.rs DS_*) — no GPU context in this process
struct Rem { v: usize, l: usize, eos: i32, base: usize, dm: HashMap<&'static str, (usize, usize)> }
#[derive(Default)] struct DecState { gpu: Option<DecGpu>, built: HashMap<String, DecGpu>, decs: HashMap<usize, GDec>, busy: bool, used: [bool; DSLOTS], rem: Option<Rem> }
fn rword(base: usize, k: usize) -> &'static std::sync::atomic::AtomicU32 { unsafe { &*(base as *const std::sync::atomic::AtomicU32).add(k) } }
fn rbytes(base: usize, off: usize, n: usize) -> &'static mut [u8] { unsafe { std::slice::from_raw_parts_mut((base + off) as *mut u8, n) } }
/// wait for the server's decode service: DS_DONE → Ok, DS_ERR → Err
fn rwait(base: usize) -> Result<(), String> {
    use omni_gpu::array::*; use std::sync::atomic::Ordering;
    let t0 = std::time::Instant::now();
    loop { let w = rword(base, 9).load(Ordering::Acquire);
        if w == DS_DONE { rword(base, 9).store(DS_IDLE, Ordering::Release); return Ok(()) }
        if w == DS_ERR { rword(base, 9).store(DS_IDLE, Ordering::Release); return Err("array server decode error (see the server log)".into()) }
        if t0.elapsed().as_secs() > 900 { return Err("array server decode: no answer in 900 s".into()) }
        std::thread::sleep(std::time::Duration::from_micros(30)); }
}
/// the remote prepare: this harness's current weights → its replica in the server's decode program (built per config)
fn rem_prepare(h: P) -> Result<Rem, String> {
    use omni_gpu::array::*; use std::sync::atomic::Ordering;
    assert_eq!(DS, DSLOTS); assert_eq!(omni_gpu::array::DTMAX, DTMAX);
    let ps = params(h);
    if with(h, |r| r.cli.is_none()) { connect(h, None, &ps)?; }
    let cfg0 = cfg_of(h, 1, 1, &ps);
    let (ex, sat, v, l, eos) = with(h, |r| (r.exit, r.sat, r.dims[0] as usize, r.dims[2] as usize, r.t25.map(|t| t.2).unwrap_or(-1)));
    let cfg = format!("{{\"decode\": {{\"S\": {DSLOTS}, \"Tmax\": {DTMAX}, \"exit_theta\": {ex}, \"route_sat\": {sat}}}, {}", cfg0.trim_start().trim_start_matches('{'));
    let id = cfg.bytes().fold(0x811c9dc5u32, |a, b| (a ^ b as u32).wrapping_mul(0x01000193)) & 0x7fff_ffff;
    let dir = std::env::var("OMR_GPU_SERVER").unwrap(); let f = format!("{dir}/dcfg-{id}.json");
    if !std::path::Path::new(&f).exists() { let tmp = format!("{f}.{}", std::process::id()); std::fs::write(&tmp, &cfg).map_err(|e| e.to_string())?; std::fs::rename(&tmp, &f).map_err(|e| e.to_string())?; }
    with(h, |r| -> Result<Rem, String> {
        let c = r.cli.as_ref().ok_or("not connected to the array server yet")?;
        let base = c.slot.p as usize; let woff = c.lay.sections().1; let mut o = 0;
        for (_, ptr, size) in &ps { rbytes(base, woff + o, size * 4).copy_from_slice(unsafe { std::slice::from_raw_parts(*ptr as *const u8, size * 4) }); o += size * 4; }
        rword(base, 10).store(id, Ordering::Release); rword(base, 9).store(DS_PREP, Ordering::Release);
        rwait(base)?;
        Ok(Rem { v, l, eos, base, dm: c.lay.dec() })
    })
}
static DEC: Mutex<Option<DecState>> = Mutex::new(None);
static DCV: std::sync::Condvar = std::sync::Condvar::new();
fn dec_on() -> bool { std::env::var("OMR_GPU_DECODE").map(|v| v == "1").unwrap_or(false) }
fn ours(d: P) -> bool { DEC.lock().unwrap().as_ref().map(|st| st.decs.contains_key(&(d as usize))).unwrap_or(false) }

fn dec_build(h: P) -> Result<DecGpu, String> {
    let ps = params(h);
    let cfg0 = cfg_of(h, 1, 1, &ps);                                      // (cfg_of takes the RECS lock itself: never inside with())
    let (ex, sat, v, l, eos) = with(h, |r| (r.exit, r.sat, r.dims[0] as usize, r.dims[2] as usize, r.t25.map(|t| t.2).unwrap_or(-1)));
    let cfg = format!("{{\"decode\": {{\"S\": {DSLOTS}, \"Tmax\": {DTMAX}, \"exit_theta\": {ex}, \"route_sat\": {sat}}}, {}", cfg0.trim_start().trim_start_matches('{'));
    let root = std::env::var("OMNI_GPU_ROOT").unwrap_or_else(|_| concat!(env!("CARGO_MANIFEST_DIR"), "/..").to_string());
    let dir = format!("{}/omnitrain_dec-{}-{}", std::env::var("TMPDIR").unwrap_or("/tmp".into()), std::process::id(), h as usize);
    std::fs::create_dir_all(&dir).map_err(|e| format!("{dir}: {e}"))?; std::fs::write(format!("{dir}/cfg.json"), &cfg).map_err(|e| e.to_string())?;
    let out = std::process::Command::new(std::env::var("OMNI_GPU_PYTHON").unwrap_or("python3".into()))
        .arg(format!("{root}/gen/make_program.py")).arg(format!("{dir}/cfg.json")).arg(&dir).output().map_err(|e| format!("make_program: {e}"))?;
    if !out.status.success() { return Err(format!("make_program (decode): {}", String::from_utf8_lossy(&out.stderr))); }
    let text = std::fs::read_to_string(format!("{dir}/prog.txt")).map_err(|e| e.to_string())?;
    let io = parse_io(&std::fs::read_to_string(format!("{dir}/io.json")).map_err(|e| e.to_string())?);
    let gpu = device()?; let lo = omni_gpu::program::load(gpu, &text, "decode")?;
    eprintln!("[omnitrain_gpu] decode on {} — {DSLOTS} stations × {DTMAX}, {} passes, {:.1} MB resident", gpu.name, lo.s.passes(), lo.s.bytes() as f64 / 1e6);
    Ok(DecGpu { s: lo.s, io, v, l, eos, prepped: false, cfg })
}

/// om_dec_prepare: the CPU engine re-quantises; so does the GPU (weights uploaded, segment 0)
#[no_mangle] pub extern "C" fn om_dec_prepare(h: P) {
    fresh(h); real!("om_dec_prepare", extern "C" fn(P))(h);
    if !dec_on() { return }
    if std::env::var("OMR_GPU_SERVER").is_ok() {                              // server mode: the array server decodes (one GPU context for the array)
        let rp = rem_prepare(h);
        let mut g = DEC.lock().unwrap(); let st = g.get_or_insert_with(Default::default);
        match rp { Ok(r) => st.rem = Some(r), Err(e) => { if st.rem.is_some() || with(h, |r| r.cli.is_some()) { eprintln!("[omnitrain_gpu] server decode off ({e}) — the CPU engine decodes"); } st.rem = None; } }
        return
    }
    let mut g = DEC.lock().unwrap(); let st = g.get_or_insert_with(Default::default);
    let r = (|| -> Result<(), String> {
        let ps0 = params(h); let want = format!("{}|{}|{}", cfg_of(h, 1, 1, &ps0), with(h, |r| r.exit), with(h, |r| r.sat));
        if st.gpu.as_ref().map(|g| g.cfg != want).unwrap_or(true) {            // switches / parameters differ from the active program (e.g. the
            if let Some(old) = st.gpu.take() { st.built.insert(old.cfg.clone(), old); }   // local read-outs on after the first prepare, the port
            let g = match st.built.remove(&want) { Some(g) => g, None => { let mut g = dec_build(h)?; g.cfg = want.clone(); g } };   // soft ↔ hard):
            st.gpu = Some(g);                                                    // one built program per config, switched — never rebuilt twice
        }
        let dg = st.gpu.as_mut().unwrap();
        let ps = params(h); let mut w: Vec<(usize, u64, Vec<u8>)> = Vec::new();
        for (name, ptr, size) in &ps { w.push((dg.io[&format!("w:{name}")], 0, unsafe { std::slice::from_raw_parts(*ptr as *const u8, size * 4) }.to_vec())); }
        let wr: Vec<(usize, u64, &[u8])> = w.iter().map(|(i, o, b)| (*i, *o, b.as_slice())).collect();
        dg.s.write_at_many(&wr)?; dg.s.step_seg(0)?; dg.prepped = true; Ok(())
    })();
    if let Err(e) = r { eprintln!("[omnitrain_gpu] GPU decode off ({e}) — the CPU engine decodes"); st.gpu = None; }
}
#[no_mangle] pub extern "C" fn om_decx_new(h: P) -> P {
    let cpu = real!("om_decx_new", extern "C" fn(P) -> P)(h);
    if !dec_on() { return cpu }
    let mut g = DEC.lock().unwrap(); let st = g.get_or_insert_with(Default::default);
    let Some(slot) = (0..DSLOTS).find(|&i| !st.used[i]) else { return cpu };
    st.used[slot] = true;
    let l = with(h, |r| r.dims[2] as usize);
    let d = Box::into_raw(Box::new(0u8)) as usize;                          // a unique handle of ours
    st.decs.insert(d, GDec { h: h as usize, cpu: cpu as usize, slot, pos: 0, t25row: 0, router: -1, gate: 0.0, exits: vec![0; l], logits: vec![], rows: 0,
                             pend: false, done: false, inp: (0, -1, -1), out: (0, 0.0, false), hist: Vec::new(), on_cpu: false });
    d as P
}
#[no_mangle] pub extern "C" fn om_decx_free(d: P) {
    let mut g = DEC.lock().unwrap();
    if let Some(st) = g.as_mut() { if let Some(x) = st.decs.remove(&(d as usize)) { st.used[x.slot] = false; real!("om_decx_free", extern "C" fn(P))(x.cpu as P); return } }
    drop(g); real!("om_decx_free", extern "C" fn(P))(d)
}
#[no_mangle] pub extern "C" fn om_decx_reset(h: P, d: P) {
    let mut g = DEC.lock().unwrap();
    if let Some(x) = g.as_mut().and_then(|st| st.decs.get_mut(&(d as usize))) { x.pos = 0; x.t25row = 0; x.router = -1; x.gate = 0.0; x.logits.clear(); x.rows = 0;
        x.hist.clear(); x.on_cpu = false;
        let c = x.cpu; drop(g); real!("om_decx_reset", extern "C" fn(P, P))(h, c as P); return }
    drop(g); real!("om_decx_reset", extern "C" fn(P, P))(h, d)
}
#[no_mangle] pub extern "C" fn om_decx_stage(d: P, st_: c_int) {
    let c = DEC.lock().unwrap().as_ref().and_then(|st| st.decs.get(&(d as usize)).map(|x| x.cpu));
    real!("om_decx_stage", extern "C" fn(P, c_int))(c.map(|c| c as P).unwrap_or(d), st_)
}
fn gpu_dec_step(h: P, d: P, tok: c_int, kind: c_int, prop: c_int) -> Result<(i32, f32), String> {
    let mut g = DEC.lock().unwrap();
    { let st = g.as_mut().ok_or("no decode state")?; if st.rem.is_none() && st.gpu.as_ref().map(|x| !x.prepped).unwrap_or(true) { return Err("GPU decode not prepared".into()) }
      let x = st.decs.get_mut(&(d as usize)).ok_or("unknown decoder")?; if x.pos as usize >= DTMAX - 1 { return Err("position past the GPU cache".into()) }
      x.inp = (tok, kind, prop); x.pend = true; x.done = false; }
    loop {
        let st = g.as_mut().unwrap();
        if st.decs[&(d as usize)].done { let x = st.decs.get_mut(&(d as usize)).unwrap(); x.done = false; return Ok((x.out.0, x.out.1)) }
        if !st.busy { st.busy = true; break }
        g = DCV.wait(g).unwrap();
    }
    // the leader: one GPU step for every pending decoder
    let st = g.as_mut().unwrap();
    let res = (|| -> Result<(), String> {
        let t25 = with(h, |r| r.t25);
        if st.rem.is_some() { return rem_step(st, t25) }
        let dg = st.gpu.as_mut().unwrap(); let (v, l) = (dg.v, dg.l);
        let mut tok_ = vec![0i32; DSLOTS]; let mut kd = vec![-1i32; DSLOTS]; let mut pp = vec![-1i32; DSLOTS]; let mut pos = vec![(DTMAX - 1) as i32; DSLOTS];
        let mut res = vec![0i32; DSLOTS * 32]; let mut act = Vec::new();
        for (k, x) in st.decs.iter_mut() { if !x.pend { continue }
            let s = x.slot; let (t, kk, p) = x.inp; tok_[s] = t; kd[s] = kk; pp[s] = p; pos[s] = x.pos; act.push(*k);
            if let Some((kern, mods, eos)) = t25 {                                // T25-CORE: this token's address, one firing of the rendered core
                let f5 = [x.pos as i64, t as i64, if (0..64).contains(&kk) { kk as i64 } else { 36 }, 0, x.t25row];
                let (mut a, z, mut tw) = ([0u8; 32], [0u8; 32], [0u8; 32]);
                let fk: extern "C" fn(*const i64, usize, *mut u8, *const u8, *mut u8, *const u8) = unsafe { std::mem::transmute(kern) };
                fk(f5.as_ptr(), 1, a.as_mut_ptr(), z.as_ptr(), tw.as_mut_ptr(), mods.as_ptr());
                for q in 0..32 { res[s * 32 + q] = a[q] as i32; }
                if t == eos { x.t25row += 1; } } }
        let w = vec![(dg.io["tok"], 0u64, i32b(&tok_)), (dg.io["pkind"], 0, i32b(&kd)), (dg.io["pprop"], 0, i32b(&pp)), (dg.io["dpos"], 0, i32b(&pos)), (dg.io["t25res"], 0, i32b(&res))];
        let wr: Vec<(usize, u64, &[u8])> = w.iter().map(|(i, o, b)| (*i, *o, b.as_slice())).collect();
        dg.s.write_at_many(&wr)?; dg.s.step_seg(1)?;
        let small = dg.s.read_at_many(&[(dg.io["targ"], 0, (DSLOTS * 4) as u64), (dg.io["tmx"], 0, (DSLOTS * 4) as u64), (dg.io["t2nd"], 0, (DSLOTS * 4) as u64),
                                        (dg.io["ex"], 0, (DSLOTS * 4) as u64), (dg.io["pst"], 0, (DSLOTS * 20) as u64), (dg.io["pgw"], 0, (DSLOTS * 8) as u64)])?;
        let fl = |b: &Vec<u8>, i: usize| f32::from_le_bytes([b[i * 4], b[i * 4 + 1], b[i * 4 + 2], b[i * 4 + 3]]);
        let rows: Vec<(usize, u64, u64)> = act.iter().map(|k| (dg.io["dlog"], (st.decs[k].slot * v * 4) as u64, (v * 4) as u64)).collect();
        let lg = dg.s.read_at_many(&rows)?;
        for (j, k) in act.iter().enumerate() {
            let x = st.decs.get_mut(k).unwrap(); let s = x.slot;
            let ex = fl(&small[3], s) as usize; let top = fl(&small[0], s) as i32; let mg = fl(&small[1], s) - fl(&small[2], s);
            if ex < l { x.exits[ex] += 1; } else { x.router = fl(&small[4], s * 5) as i32; x.gate = fl(&small[5], s * 2); }
            x.logits = lg[j].chunks_exact(4).map(|c| f32::from_le_bytes([c[0], c[1], c[2], c[3]])).collect();
            x.pos += 1; x.rows += 1; x.out = (top, mg, ex < l); x.pend = false; x.done = true;
        }
        Ok(())
    })();
    st.busy = false;
    if let Err(e) = &res { for x in st.decs.values_mut() { if x.pend { x.pend = false; x.done = true; x.out = (-1, 0.0, false); } } eprintln!("[omnitrain_gpu] GPU decode step failed: {e}"); }
    DCV.notify_all();
    let x = st.decs.get_mut(&(d as usize)).unwrap(); x.done = false;
    res.map(|_| (x.out.0, x.out.1))
}
/// the leader's step through the array server: every pending decoder's station → the slot's decode area, one service step, outputs back
fn rem_step(st: &mut DecState, t25: Option<(usize, [u8; 32], i32)>) -> Result<(), String> {
    use std::sync::atomic::Ordering;
    let rm = st.rem.as_ref().unwrap(); let (v, l, base) = (rm.v, rm.l, rm.base); let dm = rm.dm.clone();
    let mut act_ = vec![0i32; DSLOTS]; let mut act = Vec::new();
    let put = |k: &str, s: usize, n: usize, vals: &[i32]| { let (o, _) = dm[k]; let b = rbytes(base, o + s * n * 4, n * 4); for (j, x) in vals.iter().enumerate() { b[j * 4..j * 4 + 4].copy_from_slice(&x.to_le_bytes()); } };
    for (k, x) in st.decs.iter_mut() { if !x.pend { continue }
        let s = x.slot; let (t, kk, p) = x.inp; act_[s] = 1; act.push(*k);
        put("tok", s, 1, &[t]); put("pkind", s, 1, &[kk]); put("pprop", s, 1, &[p]); put("dpos", s, 1, &[x.pos]);
        let mut res = [0i32; 32];
        if let Some((kern, mods, eos)) = t25 {
            let f5 = [x.pos as i64, t as i64, if (0..64).contains(&kk) { kk as i64 } else { 36 }, 0, x.t25row];
            let (mut a, z, mut tw) = ([0u8; 32], [0u8; 32], [0u8; 32]);
            let fk: extern "C" fn(*const i64, usize, *mut u8, *const u8, *mut u8, *const u8) = unsafe { std::mem::transmute(kern) };
            fk(f5.as_ptr(), 1, a.as_mut_ptr(), z.as_ptr(), tw.as_mut_ptr(), mods.as_ptr());
            for q in 0..32 { res[q] = a[q] as i32; }
            if t == eos { x.t25row += 1; } }
        put("t25res", s, 32, &res); }
    put("act", 0, DSLOTS, &act_);
    rword(base, 9).store(omni_gpu::array::DS_STEP, Ordering::Release);
    rwait(base)?;
    let fl = |k: &str, i: usize| { let (o, _) = dm[k]; let b = rbytes(base, o + i * 4, 4); f32::from_le_bytes([b[0], b[1], b[2], b[3]]) };
    for k in &act {
        let x = st.decs.get_mut(k).unwrap(); let s = x.slot;
        let ex = fl("ex", s) as usize; let top = fl("targ", s) as i32; let mg = fl("tmx", s) - fl("t2nd", s);
        if ex < l { x.exits[ex] += 1; } else { x.router = fl("pst", s * 5) as i32; x.gate = fl("pgw", s * 2); }
        let (o, _) = dm["dlog"]; x.logits = rbytes(base, o + s * v * 4, v * 4).chunks_exact(4).map(|c| f32::from_le_bytes([c[0], c[1], c[2], c[3]])).collect();
        x.pos += 1; x.rows += 1; x.out = (top, mg, ex < l); x.pend = false; x.done = true;
    }
    Ok(())
}
/// this decoder continues on its CPU twin: the twin is reset and fed the decoder's whole history first (same state as the GPU's), then
/// every later step of this decode goes to the CPU (until om_decx_reset)
fn cpu_twin(h: P, d: P, why: &str) -> Option<P> {
    let mut g = DEC.lock().unwrap(); let x = g.as_mut()?.decs.get_mut(&(d as usize))?;
    let cpu = x.cpu as P;
    if !x.on_cpu {
        eprintln!("[omnitrain_gpu] a decoder continues on the CPU ({why}) — {} tokens replayed", x.hist.len());
        let hist = x.hist.clone(); x.on_cpu = true; drop(g);
        real!("om_decx_reset", extern "C" fn(P, P))(h, cpu);
        let (mut t, mut m) = (0 as c_int, 0f32);
        for (a, b, c) in hist { real!("om_decx_step", extern "C" fn(P, P, c_int, c_int, c_int, *mut c_int, *mut f32))(h, cpu, a, b, c, &mut t, &mut m); }
    }
    Some(cpu)
}
fn on_cpu(d: P) -> Option<P> { DEC.lock().unwrap().as_ref().and_then(|st| st.decs.get(&(d as usize)).and_then(|x| if x.on_cpu { Some(x.cpu as P) } else { None })) }
fn note_hist(d: P, t: c_int, k: c_int, p: c_int) { if let Some(x) = DEC.lock().unwrap().as_mut().and_then(|st| st.decs.get_mut(&(d as usize))) { x.hist.push((t, k, p)); } }
#[no_mangle] pub extern "C" fn om_decx_step(h: P, d: P, tok: c_int, kind: c_int, prop: c_int, top1: *mut c_int, margin: *mut f32) {
    let f = real!("om_decx_step", extern "C" fn(P, P, c_int, c_int, c_int, *mut c_int, *mut f32));
    if ours(d) {
        if let Some(c) = on_cpu(d) { return f(h, c, tok, kind, prop, top1, margin) }
        match gpu_dec_step(h, d, tok, kind, prop) {
            Ok((t, m)) => { note_hist(d, tok, kind, prop); unsafe { *top1 = t; *margin = m; } return }
            Err(e) => { if let Some(c) = cpu_twin(h, d, &e) { return f(h, c, tok, kind, prop, top1, margin) } std::process::abort() } } }
    f(h, d, tok, kind, prop, top1, margin)
}
#[no_mangle] pub extern "C" fn om_decx_step_draft(h: P, d: P, tok: c_int, kind: c_int, prop: c_int, draft: c_int, top1: *mut c_int, margin: *mut f32, acc: *mut c_int) {
    let f = real!("om_decx_step_draft", extern "C" fn(P, P, c_int, c_int, c_int, c_int, *mut c_int, *mut f32, *mut c_int));
    if ours(d) {
        if let Some(c) = on_cpu(d) { return f(h, c, tok, kind, prop, draft, top1, margin, acc) }
        match gpu_dec_step(h, d, tok, kind, prop) {
            Ok((t, m)) => { note_hist(d, tok, kind, prop); unsafe { *top1 = t; *margin = m; if !acc.is_null() { *acc = (t == draft) as c_int; } } return }
            Err(e) => { if let Some(c) = cpu_twin(h, d, &e) { return f(h, c, tok, kind, prop, draft, top1, margin, acc) } std::process::abort() } } }
    f(h, d, tok, kind, prop, draft, top1, margin, acc)
}
#[no_mangle] pub extern "C" fn om_decx_logit(h: P, d: P, tok: c_int) -> f32 {
    if let Some(c) = on_cpu(d) { return real!("om_decx_logit", extern "C" fn(P, P, c_int) -> f32)(h, c, tok) }
    let r = DEC.lock().unwrap().as_ref().and_then(|st| st.decs.get(&(d as usize)).map(|x| x.logits.get(tok as usize).copied().unwrap_or(-1e30)));
    r.unwrap_or_else(|| real!("om_decx_logit", extern "C" fn(P, P, c_int) -> f32)(h, d, tok))
}
#[no_mangle] pub extern "C" fn om_decx_logits(d: P) -> *const f32 {
    let r = DEC.lock().unwrap().as_ref().and_then(|st| st.decs.get(&(d as usize)).map(|x| x.logits.as_ptr()));
    r.unwrap_or_else(|| real!("om_decx_logits", extern "C" fn(P) -> *const f32)(d))
}
#[no_mangle] pub extern "C" fn om_decx_tool(d: P, router: *mut c_int, gate: *mut f32) {
    if let Some(c) = on_cpu(d) { return real!("om_decx_tool", extern "C" fn(P, *mut c_int, *mut f32))(c, router, gate) }
    let r = DEC.lock().unwrap().as_ref().and_then(|st| st.decs.get(&(d as usize)).map(|x| (x.router, x.gate)));
    match r { Some((a, b)) => unsafe { *router = a; *gate = b; }, None => real!("om_decx_tool", extern "C" fn(P, *mut c_int, *mut f32))(d, router, gate) }
}
#[no_mangle] pub extern "C" fn om_decx_exits(h: P, d: P, out: *mut std::ffi::c_long) {
    let r = DEC.lock().unwrap().as_ref().and_then(|st| st.decs.get(&(d as usize)).map(|x| x.exits.clone()));
    match r { Some(e) => for (i, v) in e.iter().enumerate() { unsafe { *out.add(i) = *v as std::ffi::c_long; } },
              None => real!("om_decx_exits", extern "C" fn(P, P, *mut std::ffi::c_long))(h, d, out) }
}
#[no_mangle] pub extern "C" fn om_decx_harmony(h: P, d: P, out: *mut f32) -> c_int {
    if ours(d) { return 0 }                                                    // GPU decode v1 does not report harmony (♪ statistics only)
    real!("om_decx_harmony", extern "C" fn(P, P, *mut f32) -> c_int)(h, d, out)
}
#[no_mangle] pub extern "C" fn om_decx_sieve_rate(d: P) -> f64 {
    let r = DEC.lock().unwrap().as_ref().and_then(|st| st.decs.get(&(d as usize)).map(|_| 0.0f64));
    r.unwrap_or_else(|| real!("om_decx_sieve_rate", extern "C" fn(P) -> f64)(d))
}
