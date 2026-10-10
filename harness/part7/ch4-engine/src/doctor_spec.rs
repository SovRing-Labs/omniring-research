// DOCTOR-INTERP-0 (J 10-07): the two-team clean room on equations — READER → WALL → IMPLEMENTER.
// Field: clean-room design / the Chinese wall (the 1982 IBM PC BIOS re-implementations: one team writes a functional spec from the
// original, a wall passes only the spec, a second team that never saw the original implements from it). Our form:
//   READER  `core --abc spec`  — lowers source with A1, writes per function output a SPEC: argument types, the name-free equation
//                                 (arguments a0…), input → output examples the reader observed by evaluating it, effects count,
//                                 provenance (source hash + licence class). Never a name, a comment, a line, a span or code text.
//   WALL    `core --abc wall`  — refuses any row that is not function: a strict positive schema (keys, value types, the equation's
//                                 grammar) and, behind it, a scan of every string against the source's identifiers, comment words and
//                                 string literals. `--seed-leaks` measures it: every clean row is copied with one leak injected.
//   IMPLEMENTER `core --abc need --needs <wall-passed specs> --build --ff` — the existing FF-SYNTH + CEGIS builder (a spec row IS a need
//                                 row), with a library that excludes the source; verified by rustc on held-out and validate examples.
use super::abc::*;
use std::collections::{HashMap, HashSet};

fn arg(a: &[String], k: &str) -> Option<String> { a.iter().position(|x| x == k).and_then(|i| a.get(i + 1)).cloned() }
fn norm(v: Val) -> Val { match v { Val::T(x) | Val::L(x) => Val::L(x.into_iter().map(norm).collect()), o => o } }
fn to_json(v: &Val) -> Option<serde_json::Value> {
    let sc = |x: &Val| -> Option<serde_json::Value> { match x { Val::I(y) => Some((*y).into()), Val::F(f) if f.is_finite() => serde_json::Number::from_f64(*f as f64).map(serde_json::Value::Number), _ => None } };
    match norm(v.clone()) { Val::L(xs) => xs.iter().map(sc).collect::<Option<Vec<_>>>().map(serde_json::Value::Array), x => sc(&x) }
}
fn sha256_hex(b: &[u8]) -> String { ring::digest::digest(&ring::digest::SHA256, b).as_ref().iter().map(|x| format!("{x:02x}")).collect() }
fn fnv(s: &str) -> u64 { s.bytes().fold(0xcbf2_9ce4_8422_2325u64, |a, b| (a ^ b as u64).wrapping_mul(0x100_0000_01b3)) }
fn mix(x: &mut u64) -> u64 { *x = x.wrapping_add(0x9E37_79B9_7F4A_7C15); let mut z = *x; z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9); z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB); z ^ (z >> 31) }

/// The equation printed with the spec's argument names: input k (eval_inputs order) → `a{k}`. None when deeper than `depth`.
fn term(g: &EGraph, best: &HashMap<Id, (u32, Node)>, c: Id, ins: &[(Id, bool)], depth: usize) -> Option<String> {
    let c = g.find(c);
    if let Some(k) = ins.iter().position(|x| g.find(x.0) == c) { return Some(format!("a{k}")); }
    let (_, n) = best.get(&c)?;
    if n.1.is_empty() { return Some(n.0.sym()); }
    if depth == 0 { return None; }
    let kids: Option<Vec<String>> = n.1.iter().map(|&k| term(g, best, k, ins, depth - 1)).collect();
    Some(format!("({} {})", n.0.sym(), kids?.join(" ")))
}

/// Inputs the reader feeds a spec's equation: the canonical probe table first (8 rows), then seeded values over three scales.
/// arg type codes: 0 int · 1 list (of int) · 2 f32 · 3 f32list
const TY: [&str; 4] = ["int", "list", "f32", "f32list"];
fn fval(seed: &mut u64, k: usize) -> f32 { let span = [1.0f32, 10.0, 1000.0][k % 3]; ((mix(seed) % 2_000_001) as f32 / 1_000_000.0 - 1.0) * span }
fn inputs(types: &[u8], k: usize, seed: &mut u64) -> Vec<Val> {
    if k < 8 { return types.iter().enumerate().map(|(p, &t)| match t { 2 => match probe_val(k, p, false) { Val::I(x) => Val::F(x as f32 * 0.37), v => v },
        3 => match probe_val(k, p, true) { Val::L(v) => Val::L(v.into_iter().map(|x| match x { Val::I(y) => Val::F(y as f32 * 0.37), o => o }).collect()), v => v }, _ => probe_val(k, p, t == 1) }).collect(); }
    types.iter().map(|&t| match t {
        1 => { let n = (mix(seed) % 7) as usize; Val::L((0..n).map(|_| Val::I((mix(seed) % 41) as i64 - 20)).collect()) }
        2 => Val::F(fval(seed, k)),
        3 => { let n = 1 + (mix(seed) % 8) as usize; Val::L((0..n).map(|_| Val::F(fval(seed, k))).collect()) }
        _ => { let span: i64 = [50, 2000, 1_000_000][k % 3]; Val::I((mix(seed) % (2 * span as u64 + 1)) as i64 - span) }
    }).collect()
}

/// READER: `core --abc spec --src F [--src F…] [--licence own] [--opaque-max 0.2] [--depth 14] --out specs.jsonl`
pub fn spec(a: &[String]) {
    let srcs: Vec<String> = a.windows(2).filter(|w| w[0] == "--src").map(|w| w[1].clone()).collect();
    let thr: f64 = arg(a, "--opaque-max").and_then(|v| v.parse().ok()).unwrap_or(0.20);
    let depth: usize = arg(a, "--depth").and_then(|v| v.parse().ok()).unwrap_or(14);
    let licence = arg(a, "--licence").unwrap_or("own".into());
    let max_in: usize = arg(a, "--max-inputs").and_then(|v| v.parse().ok()).unwrap_or(8); // the emit route has no arity limit; synthesis does (≤ 4 in practice)
    let t0 = std::time::Instant::now();
    let (mut nf, mut clean, mut outs_seen) = (0usize, 0usize, 0usize);
    let mut skip: HashMap<&str, usize> = HashMap::new();
    let mut rows: Vec<serde_json::Value> = Vec::new(); let mut seen: HashSet<String> = HashSet::new();
    for s in &srcs {
        let Ok(src) = std::fs::read_to_string(s) else { eprintln!("abc spec: cannot read {s}"); continue };
        let sha = sha256_hex(src.as_bytes());
        let mut g = EGraph::default(); let (mut slots, mut opq) = (0u32, 0u32);
        let fs = lower_file(&src, &mut g, &mut slots, &mut opq);
        let best = g.extract();
        for f in &fs {
            nf += 1;
            if f.nodes == 0 || f.opaque as f64 / f.nodes as f64 > thr { *skip.entry("fn over opaque ceiling").or_default() += 1; continue; }
            clean += 1;
            let effects = f.outs.iter().filter(|o| o.0 == "effect").count();
            for (role, id) in f.outs.iter().filter(|o| o.0 != "effect") {
                outs_seen += 1;
                let Some((_, n)) = best.get(&g.find(*id)) else { continue };
                if n.1.is_empty() || n.0.opaque() { *skip.entry("output is a leaf").or_default() += 1; continue; }
                let ins = eval_inputs(&g, &best, *id, depth);
                if ins.is_empty() || ins.len() > max_in { *skip.entry("inputs 0 or > --max-inputs").or_default() += 1; continue; }
                let Some(eq) = term(&g, &best, *id, &ins, depth) else { *skip.entry("deeper than --depth").or_default() += 1; continue };
                // a unit value as a leaf (an early-return / panic branch) has no number: not a spec
                { let sp = eq.replace('(', " ( ").replace(')', " ) "); let tk: Vec<&str> = sp.split_whitespace().collect();
                  if tk.iter().enumerate().any(|(j, x)| *x == "tup" && (j == 0 || tk[j - 1] != "(")) { *skip.entry("unit value in equation").or_default() += 1; continue; } }
                // an input read through get_k is a tuple / struct: the spec has no type for it yet (int | list) → not offered
                if (0..ins.len()).any(|k| eq.contains(&format!("(get") ) && eq.split("(get").skip(1).any(|t| t.split_once(' ').is_some_and(|(_, r)| r.starts_with(&format!("a{k})")) || r.starts_with(&format!("a{k} "))))) { *skip.entry("tuple-typed input").or_default() += 1; continue; }
                let types: Vec<u8> = ins.iter().map(|x| (x.1 as u8) + if f.floats.iter().any(|q| g.find(*q) == g.find(x.0)) { 2 } else { 0 }).collect();
                let key = format!("{types:?}{eq}"); if !seen.insert(key.clone()) { *skip.entry("duplicate equation").or_default() += 1; continue; }
                // the reader observes the behaviour: evaluate the equation on 40 inputs, keep the defined ones
                let mut seed = fnv(&key); let mut ex: Vec<serde_json::Value> = Vec::new();
                for k in 0..40 {
                    let args = inputs(&types, k, &mut seed);
                    let mut ev = Ev::new(&g, &best); for (i, x) in ins.iter().enumerate() { ev.leaf.insert(g.find(x.0), args[i].clone()); }
                    let out = ev.eval(*id);
                    let (Some(o), Some(aj)) = (to_json(&out), args.iter().map(to_json).collect::<Option<Vec<_>>>()) else { continue };
                    ex.push(serde_json::json!([aj, o]));
                }
                if ex.len() < 12 { *skip.entry("< 12 defined examples").or_default() += 1; continue; }
                if ex.iter().all(|e| e[1] == ex[0][1]) { *skip.entry("constant output").or_default() += 1; continue; }
                let n_ex = 6; let n_hold = (ex.len() - n_ex).min(10);
                rows.push(serde_json::json!({
                    "need": format!("s{:016x}", fnv(&format!("{sha}{key}"))),
                    "args": types.iter().map(|&t| TY[t as usize]).collect::<Vec<_>>(),
                    "equation": eq, "role": role, "effects": effects, "opaque_inputs": ins.iter().filter(|x| best.get(&g.find(x.0)).is_some_and(|b| b.1 .0.opaque())).count(),
                    "examples": ex[..n_ex], "holdout": ex[n_ex..n_ex + n_hold], "validate": ex[n_ex + n_hold..(n_ex + n_hold + 16).min(ex.len())],
                    "provenance": {"src_sha256": sha, "licence": licence, "reader": "doctor-reader-0"}}));
            }
        }
    }
    if let Some(o) = arg(a, "--out") { std::fs::write(&o, rows.iter().map(|r| r.to_string() + "\n").collect::<String>()).ok(); }
    let mut sk: Vec<_> = skip.into_iter().collect(); sk.sort_by(|x, y| y.1.cmp(&x.1));
    println!("{}", serde_json::json!({"fns": nf, "fns_clean": clean, "outputs": outs_seen, "specs": rows.len(), "skipped": sk.iter().map(|(k, v)| format!("{k}: {v}")).collect::<Vec<_>>(), "secs": t0.elapsed().as_secs_f64()}));
}

// ── WALL ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
const KEYS: &[&str] = &["need", "args", "equation", "role", "effects", "opaque_inputs", "examples", "holdout", "validate", "provenance"];
const WALL_VOCAB: &[&str] = &["int", "list", "f32", "f32list", "ret", "out", "field", "src_sha256", "licence", "reader", "doctor"];
const LICENCES: &[&str] = &["own", "MIT", "Apache-2.0", "MIT OR Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "Zlib", "Unlicense", "CC0-1.0", "black-box"];
const SYMS_EXTRA: &[&str] = &["neg", "min", "max", "abs", "clamp", "pow", "sqrt", "floor", "ceil", "round", "and", "or", "not", "sel", "idx", "store",
    "tup", "list", "fill", "range", "map", "filter", "zip", "push", "exp", "ln", "sum", "maxall", "minall", "len", "fold", "str", "opq",
    "+", "-", "*", "/", "%", "<", "<=", ">", ">=", "==", "!=", "<<", ">>", "&", "|", "^"];

fn eq_token_ok(t: &str) -> bool {
    let digits = |s: &str| !s.is_empty() && s.bytes().all(|b| b.is_ascii_digit());
    if SYMS_EXTRA.contains(&t) { return true; }
    if let Some(r) = t.strip_prefix('-') { if digits(r) { return true; } }
    if digits(t) { return true; }
    if let Some(r) = t.strip_suffix('f') { if r.parse::<f64>().is_ok() && r.bytes().all(|b| b.is_ascii_digit() || b == b'.' || b == b'-' || b == b'e' || b == b'+') { return true; } }
    for p in ["a", "item", "get"] { if let Some(r) = t.strip_prefix(p) { if digits(r) { return true; } } }
    for p in ["acc", "st", "while"] { if let Some(r) = t.strip_prefix(p) { if let Some((x, y)) = r.split_once('.') { if digits(x) && digits(y) { return true; } } } }
    false
}
fn val_ok(v: &serde_json::Value) -> bool { v.is_number() || v.as_array().is_some_and(|a| a.iter().all(|x| x.is_number())) }
fn ex_ok(v: &serde_json::Value) -> bool {
    v.as_array().is_some_and(|rows| rows.iter().all(|e| e.as_array().is_some_and(|p| p.len() == 2 && p[0].as_array().is_some_and(|xs| xs.iter().all(val_ok)) && val_ok(&p[1]))))
}

/// Layer 1: strict positive schema. Returns the first reason the row is not function.
fn schema(r: &serde_json::Value) -> Option<String> {
    let Some(o) = r.as_object() else { return Some("not an object".into()) };
    if let Some(k) = o.keys().find(|k| !KEYS.contains(&k.as_str())) { return Some(format!("key {k:?} not in the spec schema")); }
    let need = r["need"].as_str().unwrap_or("");
    if !(need.len() == 17 && need.starts_with('s') && need[1..].bytes().all(|b| b.is_ascii_hexdigit())) { return Some("need id not s+16 hex".into()); }
    if !r["args"].as_array().is_some_and(|a| !a.is_empty() && a.iter().all(|x| TY.iter().any(|t| x == t))) { return Some("args not int|list|f32|f32list".into()); }
    // a black-box spec has no equation (behaviour only); when present it must parse in the alphabet
    let eq = match r.get("equation") { None => "", Some(v) => match v.as_str() { Some(x) => x, None => return Some("equation not a string".into()) } };
    let sp = eq.replace('(', " ( ").replace(')', " ) ");
    let mut d = 0i32;
    for t in sp.split_whitespace() { match t { "(" => d += 1, ")" => { d -= 1; if d < 0 { return Some("equation parens".into()); } } _ if eq_token_ok(t) => {}, _ => return Some(format!("equation token {t:?} outside the alphabet")) } }
    if d != 0 { return Some("equation parens".into()); }
    // structure: exactly ONE well-formed term — operator heads only in head position, leaves only as leaves, nothing after the root
    if !eq.is_empty() { if let Some(why) = eq_shape(eq) { return Some(format!("equation shape: {why}")); } }
    if !matches!(r["role"].as_str(), Some("ret" | "out" | "field")) { return Some("role".into()); }
    if !r["effects"].is_u64() || !r["opaque_inputs"].is_u64() { return Some("counts not integers".into()); }
    for k in ["examples", "holdout", "validate"] { if !ex_ok(&r[k]) { return Some(format!("{k} not [[args], out] numbers")); } }
    let Some(p) = r["provenance"].as_object() else { return Some("provenance missing".into()) };
    if let Some(k) = p.keys().find(|k| !["src_sha256", "licence", "reader"].contains(&k.as_str())) { return Some(format!("provenance key {k:?}")); }
    if !p.get("src_sha256").and_then(|v| v.as_str()).is_some_and(|s| s.len() == 64 && s.bytes().all(|b| b.is_ascii_hexdigit())) { return Some("src_sha256".into()); }
    if !p.get("licence").and_then(|v| v.as_str()).is_some_and(|s| LICENCES.contains(&s)) { return Some("licence not admitted".into()); }
    if !p.get("reader").and_then(|v| v.as_str()).is_some_and(|s| s.strip_prefix("doctor-reader-").is_some_and(|n| !n.is_empty() && n.bytes().all(|b| b.is_ascii_digit()))) { return Some("reader id".into()); }
    None
}

/// What the source would leak: identifiers (≥ 3 chars, not alphabet symbols), comment words (≥ 4), string literals (≥ 3).
fn leak_set(srcs: &[String]) -> (HashSet<String>, HashSet<String>, HashSet<String>) {
    let (mut ids, mut words, mut lits) = (HashSet::new(), HashSet::new(), HashSet::new());
    for s in srcs { let Ok(src) = std::fs::read_to_string(s) else { continue };
        for t in super::lex(&src) { match t.k { 0 if t.s.len() >= 3 && !SYMS_EXTRA.contains(&t.s.as_str()) => { ids.insert(t.s); }
            3 => { let x = src.get(t.p..t.e).unwrap_or("").trim_start_matches(['r', 'b', '#']).trim_matches(|c| c == '"' || c == '\'' || c == '#'); if x.trim().len() >= 3 { lits.insert(x.to_string()); } } _ => {} } }
        for l in src.lines() { if let Some((_, c)) = l.split_once("//") { for w in c.split(|ch: char| !ch.is_alphanumeric() && ch != '_') { if w.len() >= 4 && !w.bytes().all(|b| b.is_ascii_digit()) { words.insert(w.to_string()); } } } }
    }
    (ids, words, lits)
}
fn strings(v: &serde_json::Value, out: &mut Vec<String>) {
    match v { serde_json::Value::String(s) => out.push(s.clone()), serde_json::Value::Array(a) => a.iter().for_each(|x| strings(x, out)),
        serde_json::Value::Object(o) => o.iter().for_each(|(k, x)| { out.push(k.clone()); strings(x, out) }), _ => {} }
}
fn eq_shape(eq: &str) -> Option<String> {
    let sp = eq.replace('(', " ( ").replace(')', " ) "); let t: Vec<&str> = sp.split_whitespace().collect();
    let head = |h: &str| SYMS_EXTRA.contains(&h) && !matches!(h, "str" | "opq") || h.strip_prefix("get").is_some_and(|r| !r.is_empty() && r.bytes().all(|b| b.is_ascii_digit()))
        || h.strip_prefix("while").and_then(|r| r.split_once('.')).is_some_and(|(x, y)| !x.is_empty() && !y.is_empty() && x.bytes().all(|b| b.is_ascii_digit()) && y.bytes().all(|b| b.is_ascii_digit()));
    let leaf = |x: &str| eq_token_ok(x) && !(SYMS_EXTRA.contains(&x) && !matches!(x, "str" | "opq" | "list")) && !x.starts_with("get") && !x.starts_with("while");
    fn go(t: &[&str], i: &mut usize, head: &dyn Fn(&str) -> bool, leaf: &dyn Fn(&str) -> bool) -> Result<(), String> {
        let x = *t.get(*i).ok_or("truncated")?; *i += 1;
        if x == "(" { let h = *t.get(*i).ok_or("truncated")?; if !head(h) { return Err(format!("{h:?} is not an operator")); } *i += 1;
            let mut n = 0; while *t.get(*i).ok_or("truncated")? != ")" { go(t, i, head, leaf)?; n += 1; } *i += 1; if n == 0 { return Err("operator without operands".into()); } Ok(()) }
        else if leaf(x) { Ok(()) } else { Err(format!("{x:?} is not a leaf")) }
    }
    let mut i = 0; if let Err(e) = go(&t, &mut i, &head, &leaf) { return Some(e); }
    if i != t.len() { return Some(format!("{} token(s) after the root term", t.len() - i)); }
    None
}
/// a word the wall itself owns: spec keys, enum values, licences, the reader id parts, alphabet tokens
fn is_vocab(w: &str) -> bool {
    KEYS.contains(&w) || WALL_VOCAB.contains(&w) || LICENCES.iter().any(|l| l.split(|c: char| !c.is_alphanumeric()).any(|x| x == w)) || eq_token_ok(w)
        || matches!(w, "doctor" | "reader" | "get" | "acc" | "item" | "while")
}
/// Layer 2: every string in the row (keys included) against the leak set; whole-word for identifiers / comment words.
fn leaks(r: &serde_json::Value, ls: &(HashSet<String>, HashSet<String>, HashSet<String>)) -> Option<String> {
    let mut ss = Vec::new(); strings(r, &mut ss);
    for s in &ss {
        if s.len() == 64 && s.bytes().all(|b| b.is_ascii_hexdigit()) { continue; } // the source hash
        for w in s.split(|c: char| !c.is_alphanumeric() && c != '_' && c != '.').map(|w| w.trim_matches('.')) { if w.len() < 3 { continue; }
            // the wall's own fixed vocabulary (keys, enum values, the reader id, alphabet tokens) is pinned exactly by layer 1 (schema +
            // equation grammar), so it is not a leak — even when the source is the doctor itself (crate-wide run: 210 + 136 false refusals)
            if is_vocab(w) { continue; }
            if ls.0.contains(w) { return Some(format!("source identifier {w:?}")); }
            if ls.2.contains(w) && !SYMS_EXTRA.contains(&w) { return Some(format!("source string literal {w:?}")); } // an alphabet op is not a leak
            if ls.1.contains(w) { return Some(format!("source comment word {w:?}")); } }
        // a one-word literal is a word (checked above, whole-word, same exemptions); a phrase is matched as a substring
        if let Some(l) = ls.2.iter().find(|l| !l.chars().all(|c| c.is_alphanumeric() || c == '_') && !l.split(|c: char| !c.is_alphanumeric() && c != '_' && c != '.').filter(|x| !x.is_empty()).all(is_vocab) && s.contains(l.as_str())) { return Some(format!("source string literal {l:?}")); }
    }
    None
}

/// WALL: `core --abc wall --specs IN.jsonl --src F… --out PASSED.jsonl [--refused R.jsonl] [--seed-leaks]`
pub fn wall(a: &[String]) {
    let srcs: Vec<String> = a.windows(2).filter(|w| w[0] == "--src").map(|w| w[1].clone()).collect();
    let inp = arg(a, "--specs").expect("--specs F.jsonl");
    let ls = leak_set(&srcs);
    let rows: Vec<serde_json::Value> = std::fs::read_to_string(&inp).expect("specs").lines().filter(|l| !l.trim().is_empty()).map(|l| serde_json::from_str(l).unwrap_or(serde_json::Value::Null)).collect();
    let judge = |r: &serde_json::Value| -> Option<String> { schema(r).map(|x| format!("schema: {x}")).or_else(|| leaks(r, &ls).map(|x| format!("leak: {x}"))) };
    let (mut pass, mut refused): (Vec<&serde_json::Value>, Vec<serde_json::Value>) = (Vec::new(), Vec::new());
    for r in &rows { match judge(r) { None => pass.push(r), Some(w) => refused.push(serde_json::json!({"need": r["need"], "why": w})) } }
    if let Some(o) = arg(a, "--out") { std::fs::write(&o, pass.iter().map(|r| r.to_string() + "\n").collect::<String>()).ok(); }
    if let Some(o) = arg(a, "--refused") { std::fs::write(&o, refused.iter().map(|r| r.to_string() + "\n").collect::<String>()).ok(); }
    let mut j = serde_json::json!({"rows": rows.len(), "passed": pass.len(), "refused": refused.len(), "leak_set": {"identifiers": ls.0.len(), "comment_words": ls.1.len(), "string_literals": ls.2.len()}});
    if a.iter().any(|x| x == "--seed-leaks") {
        // every passed row copied 8 ways, one leak each, drawn from this source; the wall must refuse all of them
        let pick = |set: &HashSet<String>, k: u64| -> String { let mut v: Vec<&String> = set.iter().collect(); v.sort(); if v.is_empty() { "x_leak".into() } else { v[(k as usize) % v.len()].clone() } };
        let kinds = ["name→need", "name→new key", "comment→reader", "literal→equation", "name→equation arg", "literal→example", "name→provenance key", "code text→equation"];
        let mut caught = vec![0usize; kinds.len()]; let mut l2 = 0usize; let mut tried = 0usize; let mut seed = 7u64; let mut missed: Vec<serde_json::Value> = Vec::new();
        for r in &pass {
            for (ki, kind) in kinds.iter().enumerate() {
                let (id, cw, lit) = (pick(&ls.0, mix(&mut seed)), pick(&ls.1, mix(&mut seed)), pick(&ls.2, mix(&mut seed)));
                let mut m = (*r).clone();
                match ki {
                    0 => m["need"] = id.clone().into(),
                    1 => m["name"] = id.clone().into(),
                    2 => m["provenance"]["reader"] = format!("doctor-reader-0 {cw}").into(),
                    3 => m["equation"] = format!("{} {lit}", m["equation"].as_str().unwrap_or("")).into(),
                    4 => { let e0 = m["equation"].as_str().unwrap_or("").to_string(); m["equation"] = if e0.contains("a0") { e0.replacen("a0", &id, 1) } else { format!("(+ {id} 1)") }.into(); }
                    5 => m["examples"][0][1] = lit.clone().into(),
                    6 => m["provenance"][id.clone()] = 1.into(),
                    _ => m["equation"] = format!("(+ a0 {id}.len())").into(),
                }
                tried += 1; if leaks(&m, &ls).is_some() { l2 += 1; }
                if judge(&m).is_some() { caught[ki] += 1; } else if missed.len() < 10 { missed.push(serde_json::json!({"kind": kind, "row": m})); }
            }
        }
        // `leak_scan_alone` = layer 2 without the schema on the same copies (the defence in depth)
        j["seeded"] = serde_json::json!({"tried": tried, "refused": caught.iter().sum::<usize>(), "leak_scan_alone": l2, "per_kind": kinds.iter().zip(&caught).map(|(k, c)| format!("{k}: {c}/{}", pass.len())).collect::<Vec<_>>(), "missed": missed});
    }
    println!("{j}");
}

// ── EQUIVALENCE (implementer's gate) ────────────────────────────────────────────────────────────────────────────────────────
/// Parse a spec equation back into an e-graph term; `a{k}` → input k.
fn parse_eq(eq: &str, g: &mut EGraph, args: &mut Vec<Option<Id>>) -> Option<Id> {
    let sp = eq.replace('(', " ( ").replace(')', " ) "); let toks: Vec<&str> = sp.split_whitespace().collect();
    fn leaf(t: &str, g: &mut EGraph, args: &mut Vec<Option<Id>>) -> Option<Id> {
        if let Some(k) = t.strip_prefix('a').and_then(|r| r.parse::<usize>().ok()) {
            if args.len() <= k { args.resize(k + 1, None); }
            if let Some(id) = args[k] { return Some(id); }
            let id = g.add(Op::Var(1_000_000 + k as u32), vec![]); args[k] = Some(id); return Some(id);
        }
        if let Ok(v) = t.parse::<i64>() { return Some(g.add(Op::Num(v), vec![])); }
        if let Some(r) = t.strip_suffix('f') { if let Ok(f) = r.parse::<f64>() { return Some(g.add(Op::Flt(f.to_bits()), vec![])); } }
        if let Some(d) = t.strip_prefix("item").and_then(|r| r.parse::<u8>().ok()) { return Some(g.add(Op::Item(d), vec![])); }
        if let Some((d, k)) = t.strip_prefix("acc").and_then(|r| r.split_once('.')) { return Some(g.add(Op::Acc(d.parse().ok()?, k.parse().ok()?), vec![])); }
        if let Some((d, k)) = t.strip_prefix("st").and_then(|r| r.split_once('.')) { return Some(g.add(Op::St(d.parse().ok()?, k.parse().ok()?), vec![])); }
        match t { "str" => Some(g.add(Op::Str, vec![])), "opq" => None, _ => None }
    }
    fn go(toks: &[&str], i: &mut usize, g: &mut EGraph, args: &mut Vec<Option<Id>>) -> Option<Id> {
        let t = *toks.get(*i)?; *i += 1;
        if t != "(" { return leaf(t, g, args); }
        let h = *toks.get(*i)?; *i += 1;
        let op = if let Some(k) = h.strip_prefix("get").and_then(|r| r.parse::<u8>().ok()) { Op::Get(k) }
            else if let Some((m, d)) = h.strip_prefix("while").and_then(|r| r.split_once('.')) { Op::While(d.parse().ok()?, m.parse().ok()?) }
            else { SYMS.iter().find(|(x, _)| *x == h)?.1.clone() };
        let mut kids = Vec::new();
        while *toks.get(*i)? != ")" { kids.push(go(toks, i, g, args)?); }
        *i += 1; Some(g.add(op, kids))
    }
    let mut i = 0; go(&toks, &mut i, g, args)
}

/// Differential equivalence: the spec equation (oracle) vs the built term on `n` inputs — signed edge values, multiples of
/// small numbers, three random scales, lists of length 0..8. Returns the first input where the oracle is defined and they differ.
pub fn equiv(eq: &str, types: &[bool], e: &E, n: usize) -> Option<(Vec<Val>, Val)> {
    let mut g = EGraph::default(); let mut args: Vec<Option<Id>> = Vec::new();
    let root = parse_eq(eq, &mut g, &mut args)?;
    let best = g.extract();
    const EDGE: [i64; 21] = [0, 1, -1, 2, -2, 3, -3, 7, -7, 15, -15, 30, -30, 64, -64, 100, -100, 1000, -1000, i32::MAX as i64, i32::MIN as i64];
    let mut seed = fnv(eq);
    for k in 0..n {
        let input: Vec<Val> = types.iter().enumerate().map(|(p, &l)| {
            if l { let len = (mix(&mut seed) % 9) as usize; Val::L((0..len).map(|_| Val::I(if k % 2 == 0 { EDGE[(mix(&mut seed) % 21) as usize] } else { (mix(&mut seed) % 201) as i64 - 100 })).collect()) }
            else if k < 21 * 21 && types.len() <= 2 { Val::I(EDGE[if p == 0 { k % 21 } else { k / 21 % 21 }]) }
            else { match k % 4 { 0 => Val::I(EDGE[(mix(&mut seed) % 21) as usize]), 1 => Val::I((mix(&mut seed) % 101) as i64 - 50), 2 => Val::I((mix(&mut seed) % 4001) as i64 - 2000), _ => Val::I((mix(&mut seed) % 2_000_001) as i64 - 1_000_000) } }
        }).collect();
        let mut ev = Ev::new(&g, &best);
        for (j, a) in args.iter().enumerate() { if let (Some(id), Some(v)) = (a, input.get(j)) { ev.leaf.insert(g.find(*id), v.clone()); } }
        let want = norm(ev.eval(root));
        if matches!(want, Val::Bot) || to_json(&want).is_none() { continue; }
        if norm(ev_e(e, &input, None)) != want { return Some((input, want)); }
    }
    None
}

// ── EMIT (implementer route 0): the spec's equation printed as our Rust ─────────────────────────────────────────────────────
// A clean-room implementer writes code from the functional spec; when the spec carries its equation, writing = printing the
// equation in our own Rust style (wrapping integer semantics = the evaluator's), then the same verification as a built term:
// rustc on the spec's examples + 2,000 oracle rows (the spec equation evaluated on edge + random inputs). Lists in, ints out.
enum T { L(String), A(String, Vec<T>) }
fn tree(eq: &str) -> Option<T> {
    let sp = eq.replace('(', " ( ").replace(')', " ) "); let toks: Vec<&str> = sp.split_whitespace().collect();
    fn go(t: &[&str], i: &mut usize) -> Option<T> { let x = *t.get(*i)?; *i += 1; if x != "(" { return Some(T::L(x.into())); }
        let h = t.get(*i)?.to_string(); *i += 1; let mut k = Vec::new(); while *t.get(*i)? != ")" { k.push(go(t, i)?); } *i += 1; Some(T::A(h, k)) }
    let mut i = 0; go(&toks, &mut i)
}
/// FLOAT-0 typed printer: every node gets a type, so integer index arithmetic and f32 values mix exactly as the evaluator does
/// (an op is f32 when either side is f32; comparisons give 0 / 1 i64; idx into an f32 list gives f32).
#[derive(Clone, PartialEq, Debug)]
enum Ty { I, F, LI, LF, Tup(Vec<Ty>) }
fn rty(t: &Ty) -> Option<String> { Some(match t { Ty::I => "i64".into(), Ty::F => "f32".into(), Ty::LI => "Vec<i64>".into(), Ty::LF => "Vec<f32>".into(),
    Ty::Tup(v) => { let xs: Option<Vec<String>> = v.iter().map(rty).collect(); let xs = xs?; if xs.len() == 1 { format!("({},)", xs[0]) } else { format!("({})", xs.join(", ")) } } }) }
fn as_f(x: (String, Ty)) -> String { if x.1 == Ty::F { x.0 } else { format!("({} as f32)", x.0) } }
struct Px<'a> { args: &'a [u8], acc: HashMap<u8, Ty>, st: HashMap<(u8, u8), Ty>, cur: u8 }
impl Px<'_> {
    fn p(&mut self, t: &T) -> Option<(String, Ty)> {
        Some(match t {
            T::L(x) => {
                if let Some(k) = x.strip_prefix('a').and_then(|r| r.parse::<usize>().ok()) {
                    let ty = match *self.args.get(k)? { 0 => Ty::I, 1 => Ty::LI, 2 => Ty::F, _ => Ty::LF };
                    let s = if matches!(ty, Ty::LI | Ty::LF) { format!("a{k}") } else { format!("a{k}") }; return Some((s, ty)); }
                if let Some(d) = x.strip_prefix("item").and_then(|r| r.parse::<u8>().ok()) { return Some((format!("item{d}"), Ty::I)); }
                if let Some((d, _)) = x.strip_prefix("acc").and_then(|r| r.split_once('.')) { let d: u8 = d.parse().ok()?; return Some((format!("acc{d}"), self.acc.get(&d)?.clone())); }
                if let Some((d, k)) = x.strip_prefix("st").and_then(|r| r.split_once('.')) { let key = (d.parse().ok()?, k.parse().ok()?); return Some((format!("s{d}_{k}"), self.st.get(&key)?.clone())); }
                if let Ok(v) = x.parse::<i64>() { return Some((format!("({v}i64)"), Ty::I)); }
                if let Some(r) = x.strip_suffix('f') { let f: f64 = r.parse().ok()?; return Some((format!("({:?}f32)", f as f32), Ty::F)); }
                return None;
            }
            T::A(h, k) => {
                let n = k.len();
                match (h.as_str(), n) {
                    (op, 2) if ["+", "-", "*", "/", "%", "min", "max", "pow"].contains(&op) => {
                        let (x, y) = (self.p(&k[0])?, self.p(&k[1])?);
                        if x.1 == Ty::F || y.1 == Ty::F { let (a, b) = (as_f(x), as_f(y)); (match op { "min" => format!("{a}.min({b})"), "max" => format!("{a}.max({b})"), "pow" => format!("{a}.powf({b})"), _ => format!("({a} {op} {b})") }, Ty::F) }
                        else if x.1 == Ty::I && y.1 == Ty::I { let (a, b) = (x.0, y.0); (match op { "+" => format!("{a}.wrapping_add({b})"), "-" => format!("{a}.wrapping_sub({b})"), "*" => format!("{a}.wrapping_mul({b})"),
                            "min" => format!("{a}.min({b})"), "max" => format!("{a}.max({b})"), "pow" => format!("{a}.wrapping_pow(({b}) as u32)"), _ => format!("({a} {op} {b})") }, Ty::I) } else { return None }
                    }
                    (op, 2) if ["<", "<=", ">", ">=", "==", "!="].contains(&op) => { let (x, y) = (self.p(&k[0])?, self.p(&k[1])?);
                        if x.1 == Ty::F || y.1 == Ty::F { (format!("(({} {op} {}) as i64)", as_f(x), as_f(y)), Ty::I) } else { (format!("(({} {op} {}) as i64)", x.0, y.0), Ty::I) } }
                    ("and", 2) => (format!("(({} != 0 && {} != 0) as i64)", self.p(&k[0])?.0, self.p(&k[1])?.0), Ty::I),
                    ("or", 2) => (format!("(({} != 0 || {} != 0) as i64)", self.p(&k[0])?.0, self.p(&k[1])?.0), Ty::I),
                    ("not", 1) => (format!("(({} == 0) as i64)", self.p(&k[0])?.0), Ty::I),
                    (op, 2) if ["<<", ">>", "&", "|", "^"].contains(&op) => { let (x, y) = (self.p(&k[0])?, self.p(&k[1])?); if x.1 != Ty::I || y.1 != Ty::I { return None; }
                        (match op { "<<" => format!("{}.wrapping_shl(({} as u32) & 63)", x.0, y.0), ">>" => format!("{}.wrapping_shr(({} as u32) & 63)", x.0, y.0), _ => format!("({} {op} {})", x.0, y.0) }, Ty::I) }
                    ("neg", 1) => { let x = self.p(&k[0])?; if x.1 == Ty::F { (format!("(-{})", x.0), Ty::F) } else { (format!("{}.wrapping_neg()", x.0), Ty::I) } }
                    ("abs", 1) => { let x = self.p(&k[0])?; if x.1 == Ty::F { (format!("{}.abs()", x.0), Ty::F) } else { (format!("{}.wrapping_abs()", x.0), Ty::I) } }
                    (f, 1) if ["sqrt", "exp", "ln"].contains(&f) => (format!("{}.{f}()", as_f(self.p(&k[0])?)), Ty::F),
                    (f, 1) if ["floor", "ceil", "round"].contains(&f) => { let x = self.p(&k[0])?; if x.1 == Ty::F { (format!("{}.{f}()", x.0), Ty::F) } else { x } }
                    ("clamp", 3) => { let (x, lo, hi) = (self.p(&k[0])?, self.p(&k[1])?, self.p(&k[2])?);
                        if [&x, &lo, &hi].iter().any(|v| v.1 == Ty::F) { (format!("{}.max({}).min({})", as_f(x), as_f(lo), as_f(hi)), Ty::F) } else { (format!("{}.max({}).min({})", x.0, lo.0, hi.0), Ty::I) } }
                    ("sel", 3) => { let (c, a, b) = (self.p(&k[0])?, self.p(&k[1])?, self.p(&k[2])?);
                        if a.1 == b.1 { (format!("(if {} != 0 {{ {} }} else {{ {} }})", c.0, a.0, b.0), a.1) }
                        else if matches!((&a.1, &b.1), (Ty::F, Ty::I) | (Ty::I, Ty::F)) { (format!("(if {} != 0 {{ {} }} else {{ {} }})", c.0, as_f(a), as_f(b)), Ty::F) } else { return None } }
                    ("tup", n) if n >= 1 => { let xs: Option<Vec<(String, Ty)>> = k.iter().map(|x| self.p(x)).collect(); let xs = xs?;
                        let s = if n == 1 { format!("({},)", xs[0].0) } else { format!("({})", xs.iter().map(|x| x.0.clone()).collect::<Vec<_>>().join(", ")) };
                        (s, Ty::Tup(xs.into_iter().map(|x| x.1).collect())) }
                    (g, 1) if g.starts_with("get") => { let j: usize = g[3..].parse().ok()?; let x = self.p(&k[0])?; match x.1 { Ty::Tup(v) => (format!("{}.{j}", x.0), v.get(j)?.clone()), _ => return None } }
                    ("len", 1) => { let x = self.p(&k[0])?; if !matches!(x.1, Ty::LI | Ty::LF) { return None; } (format!("({}.len() as i64)", x.0), Ty::I) }
                    ("idx", 2) => { let (l, i) = (self.p(&k[0])?, self.p(&k[1])?); if i.1 != Ty::I { return None; }
                        (format!("{}[({}) as usize]", l.0, i.0), match l.1 { Ty::LI => Ty::I, Ty::LF => Ty::F, _ => return None }) }
                    ("maxall" | "minall", 1) => { let x = self.p(&k[0])?; let (f, fi) = if h == "maxall" { ("max", "f32::NEG_INFINITY") } else { ("min", "f32::INFINITY") };
                        match x.1 { Ty::LF => (format!("{}.iter().fold({fi}, |a, b| a.{f}(*b))", x.0), Ty::F),
                            Ty::LI => (format!("{}.iter().copied().{f}().unwrap_or(0)", x.0), Ty::I), _ => return None } }
                    ("sum", 1) => { let x = self.p(&k[0])?; match x.1 { Ty::LI => (format!("{}.iter().fold(0i64, |s, x| s.wrapping_add(*x))", x.0), Ty::I),
                        Ty::LF => (format!("{}.iter().fold(0f32, |s, x| s + *x)", x.0), Ty::F), _ => return None } }
                    ("push", 2) => { let (l, x) = (self.p(&k[0])?, self.p(&k[1])?); let lt = l.1.clone();
                        let xv = if lt == Ty::LF { as_f(x) } else { x.0 }; (format!("{{ let mut v = {}.to_vec(); v.push({xv}); v }}", l.0), lt) }
                    ("fold", 3) | ("map", 2) => {
                        let body = if h == "fold" { &k[2] } else { &k[1] }; let d = own_depth(body, self.cur + 1);
                        let seq = match &k[0] { T::A(h0, kk) if h0 == "range" && kk.len() == 2 => format!("({}..{})", self.p(&kk[0])?.0, self.p(&kk[1])?.0),
                            x => { let l = self.p(x)?; if !matches!(l.1, Ty::LI | Ty::LF) { return None; } format!("(0..({}.len() as i64))", l.0) } };
                        // a failed print aborts the whole emit, so the depth is restored only on the success path
                        let saved_cur = self.cur; self.cur = d;
                        let r = if h == "map" { let b = self.p(body)?; let lt = match b.1 { Ty::I => Ty::LI, Ty::F => Ty::LF, _ => return None };
                            (format!("{seq}.map(|item{d}: i64| {}).collect::<Vec<_>>()", b.0), lt) }
                        else { let init = self.p(&k[1])?;
                            // the accumulator takes the body's type when the body is f32 and the init an int (the evaluator promotes the same way)
                            self.acc.insert(d, init.1.clone()); let mut b = self.p(body)?;
                            let at = if init.1 == Ty::I && b.1 == Ty::F { self.acc.insert(d, Ty::F); b = self.p(body)?; Ty::F } else { init.1.clone() };
                            if b.1 != at { return None; }
                            let iv = if at == Ty::F { as_f(init) } else { init.0 };
                            (format!("{{ let mut acc{d}: {} = {iv}; for item{d} in {seq} {{ acc{d} = {}; }} acc{d} }}", rty(&at)?, b.0), at) };
                        self.cur = saved_cur; r
                    }
                    (w, 3) if w.starts_with("while") => {
                        let (m, d) = w[5..].split_once('.')?; let dd: u8 = d.parse().ok()?;
                        let init = self.p(&k[0])?; let Ty::Tup(tys) = init.1.clone() else { return None };
                        for (j, ty) in tys.iter().enumerate() { self.st.insert((dd, j as u8), ty.clone()); }
                        let names: Vec<String> = (0..tys.len()).map(|j| format!("s{d}_{j}")).collect();
                        let pat = if tys.len() == 1 { format!("({},)", names[0]) } else { format!("({})", names.join(", ")) };
                        let (cond, step) = (self.p(&k[1])?.0, self.p(&k[2])?);
                        if step.1 != init.1 { return None; }
                        let body = if m == "0" { format!("if {cond} == 0 {{ break; }} st = {};", step.0) } else { format!("let brk = {cond}; st = {}; if brk != 0 {{ break; }}", step.0) };
                        (format!("{{ let mut st = {}; loop {{ #[allow(unused_variables)] let {pat} = st; {body} }} st }}", init.0), init.1)
                    }
                    _ => return None,
                }
            }
        })
    }
}
fn lit(v: &Val, ty: &Ty) -> String {
    let f = |x: &Val| match x { Val::F(y) => format!("{:?}f32", y), Val::I(y) => if matches!(ty, Ty::F | Ty::LF) { format!("{:?}f32", *y as f32) } else { format!("{y}i64") }, _ => "0".into() };
    match v { Val::L(xs) | Val::T(xs) => format!("[{}]", xs.iter().map(f).collect::<Vec<_>>().join(", ")), x => f(x) }
}
/// Route 0: print the equation (typed), compile, run on the spec rows + oracle rows; f32 compared at rel 1e-4 + abs 1e-5.
pub fn emit(nd: &serde_json::Value, dir: &str) -> Option<(String, Result<usize, String>)> {
    let eq = nd["equation"].as_str()?;
    let types: Vec<u8> = nd["args"].as_array()?.iter().map(|t| TY.iter().position(|x| t == x).unwrap_or(0) as u8).collect();
    let t = tree(eq)?;
    let mut px = Px { args: &types, acc: HashMap::new(), st: HashMap::new(), cur: 0 };
    let (body, oty) = px.p(&t)?;
    let ret = rty(&oty)?;
    let (rt, wrap) = match &oty { Ty::Tup(v) => { if v.iter().any(|x| *x != Ty::I) { return None; } (format!("[i64; {}]", v.len()), format!("{{ let t = {body}; [{}] }}", (0..v.len()).map(|j| format!("t.{j}")).collect::<Vec<_>>().join(", "))) } _ => (ret, body.clone()) };
    // rows: the spec's own, then the spec equation as oracle on edge + random inputs
    let mut g = EGraph::default(); let mut args: Vec<Option<Id>> = Vec::new(); let root = parse_eq(eq, &mut g, &mut args)?; let best = g.extract();
    let mut rows: Vec<(Vec<Val>, Val)> = Vec::new();
    for k in ["examples", "holdout", "validate"] { for e in nd[k].as_array().into_iter().flatten() { if let Some(a) = e[0].as_array() { rows.push((a.iter().map(Val::from_json).collect(), Val::from_json(&e[1]))); } } }
    const EDGE: [i64; 13] = [0, 1, -1, 2, -2, 3, 7, -7, 15, 64, -100, 1000, -1000];
    let mut seed = fnv(eq) ^ 0x5eed;
    for j in 0..2000usize {
        let inp: Vec<Val> = types.iter().map(|&ty| { let mut one = || if j % 2 == 0 { EDGE[(mix(&mut seed) % 13) as usize] } else { (mix(&mut seed) % 4001) as i64 - 2000 };
            match ty { 1 => { let n = (j * 7 + 3) % 9; Val::L((0..n).map(|_| Val::I(one())).collect()) } 2 => Val::F(fval(&mut seed, j)),
                3 => { let n = 1 + (j * 7 + 3) % 8; Val::L((0..n).map(|_| Val::F(fval(&mut seed, j))).collect()) } _ => Val::I(one()) } }).collect();
        let mut ev = Ev::new(&g, &best); for (q, a) in args.iter().enumerate() { if let (Some(id), Some(v)) = (a, inp.get(q)) { ev.leaf.insert(g.find(*id), v.clone()); } }
        let o = norm(ev.eval(root)); if to_json(&o).is_some() { rows.push((inp, o)); } }
    rows.retain(|(_, o)| match (o, &oty) { (Val::I(_), Ty::I) | (Val::F(_) | Val::I(_), Ty::F) => true, (Val::L(v), Ty::Tup(n)) => v.len() == n.len(), (Val::L(_), Ty::LI | Ty::LF) => true, _ => false });
    let params: Vec<String> = types.iter().enumerate().map(|(k, &l)| format!("a{k}: {}", ["i64", "&[i64]", "f32", "&[f32]"][l as usize])).collect();
    // rows go to a data file read at run time (one generic loop): compile time no longer grows with the row count
    // (2,000 unrolled vec! asserts kept rustc -O busy > 10 min, FLOAT-0). Line = per arg: scalar | `n v…`; then the expected value(s).
    let sc = |v: &Val| match v { Val::F(y) => format!("{:?}", y), Val::I(y) => format!("{y}"), _ => "0".into() };
    let enc = |v: &Val| match v { Val::L(xs) | Val::T(xs) => format!("{} {}", xs.len(), xs.iter().map(sc).collect::<Vec<_>>().join(" ")), x => sc(x) };
    // per-row f32 tolerance: the running-error bound (2n + 16)·u·M with M = the equation in magnitude mode (Ev::absm) — engine rows
    // reorder sums (lanes / tiles), so cancellation rows need it; appended after the expected value(s), one per output element
    let tols = |a: &[Val]| -> Vec<f32> { let mut em = Ev::new(&g, &best); em.absm = true;
        for (q, id) in args.iter().enumerate() { if let (Some(id), Some(v)) = (id, a.get(q)) { em.leaf.insert(g.find(*id), match v { Val::F(x) => Val::F(x.abs()), Val::L(xs) => Val::L(xs.iter().map(|z| match z { Val::F(y) => Val::F(y.abs()), o => o.clone() }).collect()), o => o.clone() }); } }
        let nmax = a.iter().map(|x| if let Val::L(xs) = x { xs.len() } else { 1 }).max().unwrap_or(1).max(1) as f32;
        let k = (2.0 * nmax + 16.0) * (f32::EPSILON / 2.0);
        match norm(em.eval(root)) { Val::F(m) => vec![k * m + 1e-6], Val::L(ms) => ms.iter().map(|z| match z { Val::F(m) => k * m + 1e-6, Val::I(m) => k * *m as f32 + 1e-6, _ => 1e-6 }).collect(), Val::I(m) => vec![k * m as f32 + 1e-6], _ => vec![1e-6] } };
    let data: String = rows.iter().map(|(a, o)| { let t = if matches!(oty, Ty::F | Ty::LF) { format!(" {}", tols(a).iter().map(|x| format!("{x:?}")).collect::<Vec<_>>().join(" ")) } else { String::new() };
        format!("{} {}{t}\n", a.iter().map(enc).collect::<Vec<_>>().join(" "), enc(o)) }).collect();
    let mut src = format!("#[allow(unused_parens, unused_variables, unused_mut, unused_braces, clippy::all)]\nfn f({}) -> {rt} {{ {wrap} }}\n\
        fn close(a: f32, b: f32) -> bool {{ (a.is_nan() && b.is_nan()) || (a - b).abs() <= 1e-5 + 1e-4 * a.abs().max(b.abs()) }}\n\
        fn main() {{\n    let txt = std::fs::read_to_string(std::env::args().nth(1).unwrap()).unwrap(); let mut n = 0usize;\n\
        for line in txt.lines() {{ let mut t = line.split_whitespace(); n += 1;\n", params.join(", "));
    let mut call = Vec::new();
    for (k, &l) in types.iter().enumerate() { match l {
        0 => src.push_str(&format!("        let a{k}: i64 = t.next().unwrap().parse().unwrap();\n")),
        2 => src.push_str(&format!("        let a{k}: f32 = t.next().unwrap().parse().unwrap();\n")),
        _ => src.push_str(&format!("        let n{k}: usize = t.next().unwrap().parse().unwrap(); let v{k}: Vec<{}> = (0..n{k}).map(|_| t.next().unwrap().parse().unwrap()).collect();\n", if l == 1 { "i64" } else { "f32" })) }
        call.push(if l == 1 || l == 3 { format!("&v{k}") } else { format!("a{k}") }); }
    let c = call.join(", ");
    src.push_str(&match &oty {
        Ty::F => format!("        let w: f32 = t.next().unwrap().parse().unwrap(); let tl: f32 = t.next().map(|x| x.parse().unwrap()).unwrap_or(0.0); let r = f({c}); assert!(close(r, w) || (r - w).abs() <= tl, \"row {{n}}: {{r:?}} vs {{w:?}}\");\n"),
        Ty::I => format!("        let w: i64 = t.next().unwrap().parse().unwrap(); assert_eq!(f({c}), w, \"row {{n}}\");\n"),
        Ty::LF => format!("        let m: usize = t.next().unwrap().parse().unwrap(); let w: Vec<f32> = (0..m).map(|_| t.next().unwrap().parse().unwrap()).collect(); let tl: Vec<f32> = (0..m).map(|_| t.next().map(|x| x.parse().unwrap()).unwrap_or(0.0)).collect(); let r = f({c}); assert!(r.len() == w.len() && r.iter().zip(&w).zip(&tl).all(|((x, y), e)| close(*x, *y) || (x - y).abs() <= *e), \"row {{n}}\");\n"),
        Ty::LI => format!("        let m: usize = t.next().unwrap().parse().unwrap(); let w: Vec<i64> = (0..m).map(|_| t.next().unwrap().parse().unwrap()).collect(); assert_eq!(f({c}), w, \"row {{n}}\");\n"),
        Ty::Tup(v) => format!("        let m: usize = t.next().unwrap().parse().unwrap(); let w: Vec<i64> = (0..m).map(|_| t.next().unwrap().parse().unwrap()).collect(); assert_eq!(f({c}).to_vec(), w, \"row {{n}}\"); let _ = {};\n", v.len()),
        _ => return None });
    src.push_str("    }\n    println!(\"ok {n}\");\n}\n");
    let name = nd["need"].as_str().unwrap_or("emit"); std::fs::create_dir_all(dir).ok();
    let (rsf, bin) = (format!("{dir}/{name}_emit.rs"), format!("{dir}/{name}_emit.bin")); std::fs::write(&rsf, &src).ok()?;
    let c = std::process::Command::new("rustc").args(["-O", "--edition", "2021", "-o", &bin, &rsf]).output().ok()?;
    if !c.status.success() { return Some((body, Err(format!("rustc: {}", String::from_utf8_lossy(&c.stderr).lines().find(|l| l.starts_with("error")).unwrap_or("error"))))); }
    let dat = format!("{dir}/{name}_rows.txt"); std::fs::write(&dat, &data).ok()?;
    let r = std::process::Command::new(&bin).arg(&dat).output().ok()?;
    Some((body, if r.status.success() { Ok(rows.len()) } else { Err(String::from_utf8_lossy(&r.stderr).lines().find(|l| l.contains("panicked") || l.contains("assert")).unwrap_or("failed").chars().take(200).collect()) }))
}
/// ENGINE-0: a loop's own depth = 1 + enclosing when its body uses it at its own level (nested loop bodies excluded), else the deepest
/// own-level placeholder, else 1 + enclosing — the evaluator's rule (`Ev::item_depth`)
fn own_depth(t: &T, want: u8) -> u8 {
    fn go(t: &T, out: &mut Vec<u8>) { match t {
        T::L(x) => { if let Some(d) = x.strip_prefix("item").and_then(|r| r.parse().ok()) { out.push(d); }
            if let Some(d) = x.strip_prefix("acc").and_then(|r| r.split_once('.')).and_then(|(d, _)| d.parse().ok()) { out.push(d); } }
        T::A(h, k) if h == "fold" && k.len() == 3 => { go(&k[0], out); go(&k[1], out); }
        T::A(h, k) if (h == "map" || h == "filter") && k.len() == 2 => go(&k[0], out),
        T::A(_, k) => k.iter().for_each(|x| go(x, out)) } }
    let mut f = Vec::new(); go(t, &mut f);
    if f.contains(&want) { want } else { f.into_iter().max().unwrap_or(want) }
}
/// the loop depth of a fold / map body (first item / acc placeholder found)
fn depth_of(t: &T) -> Option<u8> { match t { T::L(x) => x.strip_prefix("item").and_then(|r| r.parse().ok()).or_else(|| x.strip_prefix("acc").and_then(|r| r.split_once('.')).and_then(|(d, _)| d.parse().ok())),
    T::A(_, k) => k.iter().find_map(depth_of) } }

// ── BLACK-BOX READER (N5) ───────────────────────────────────────────────────────────────────────────────────────────────────
/// `core --abc blackbox --cmd BIN --fn NAME --args int,int [--licence black-box] --out S.jsonl [--append]`: the reader never sees
/// source — it sends `NAME a b` lines to the program and records the answers (`x` = undefined). The spec = types + observed rows,
/// no equation; the implementer must build from behaviour (FF-SYNTH + CEGIS), exactly the Chrome black-box loop.
pub fn blackbox(a: &[String]) {
    // ENGINE-0: typed args (int | f32 | f32list | list), shape constraints `--len K=aI*aJ`, `--int-range LO:HI` for int args,
    // `--ret int|f32|f32list`, and `--equation EQ` (authored on the reader side from the op's published math) CHECKED against
    // every observed row before the spec is written — a single disagreement refuses the spec.
    let cmd = arg(a, "--cmd").expect("--cmd BIN"); let f = arg(a, "--fn").expect("--fn NAME");
    let types: Vec<u8> = arg(a, "--args").expect("--args int,f32list,…").split(',').map(|t| TY.iter().position(|x| *x == t).expect("arg type") as u8).collect();
    let ret = arg(a, "--ret").unwrap_or("int".into());
    let (ilo, ihi): (i64, i64) = arg(a, "--int-range").and_then(|r| r.split_once(':').map(|(x, y)| (x.parse().unwrap_or(-100), y.parse().unwrap_or(100)))).unwrap_or((i64::MIN, i64::MAX));
    let lens: Vec<(usize, Vec<usize>)> = a.windows(2).filter(|w| w[0] == "--len").filter_map(|w| { let (k, e) = w[1].split_once('=')?;
        Some((k.trim_start_matches('a').parse().ok()?, e.split('*').filter_map(|x| x.trim_start_matches('a').parse().ok()).collect())) }).collect();
    let licence = arg(a, "--licence").unwrap_or("black-box".into());
    let n_probe: usize = arg(a, "--probes").and_then(|v| v.parse().ok()).unwrap_or(120);
    let (llo, lhi): (i64, i64) = arg(a, "--list-range").and_then(|r| r.split_once(':').map(|(x, y)| (x.parse().unwrap_or(-20), y.parse().unwrap_or(20)))).unwrap_or((-20, 20));
    let bin = std::fs::read(&cmd).expect("read --cmd"); let sha = sha256_hex(&bin);
    const EDGE: [i64; 11] = [0, 1, -1, 2, -2, 3, 5, -7, 12, 60, -100];
    let n = types.len(); let mut seed = fnv(&format!("{f}{sha}")); let mut ins: Vec<Vec<Val>> = Vec::new();
    for k in 0..(8 + n_probe) {
        let mut v: Vec<Val> = types.iter().enumerate().map(|(p, &t)| match t {
            0 => Val::I(if ilo != i64::MIN { ilo + (mix(&mut seed) % ((ihi - ilo + 1) as u64)) as i64 } else if k < 8 { match probe_val(k, p, false) { Val::I(x) => x, _ => 0 } }
                else if n <= 2 && k < 8 + EDGE.len() { EDGE[k - 8] } else { let span: i64 = [50, 2000, 1_000_000][k % 3]; (mix(&mut seed) % (2 * span as u64 + 1)) as i64 - span }),
            2 => Val::F(fval(&mut seed, k)),
            _ => Val::L(vec![]) }).collect();
        // list lengths: a constraint (product of int args) or a random 1..8, shared by same-typed lists so element-wise ops line up
        let free_len = 1 + (mix(&mut seed) % 8) as usize;
        for (p, &t) in types.iter().enumerate() { if t == 1 || t == 3 {
            let len = lens.iter().find(|(k, _)| *k == p).map(|(_, f)| f.iter().map(|&j| match v.get(j) { Some(Val::I(x)) => (*x).max(0) as usize, _ => 1 }).product()).unwrap_or(free_len);
            v[p] = Val::L((0..len).map(|_| if t == 3 { Val::F(fval(&mut seed, k)) } else { Val::I(llo + (mix(&mut seed) % ((lhi - llo + 1) as u64)) as i64) }).collect()); } }
        ins.push(v);
    }
    let enc = |v: &Val| match v { Val::L(xs) => format!("{} {}", xs.len(), xs.iter().map(|x| match x { Val::F(y) => format!("{y:?}"), Val::I(y) => y.to_string(), _ => "0".into() }).collect::<Vec<_>>().join(" ")),
        Val::F(y) => format!("{y:?}"), Val::I(y) => y.to_string(), _ => "0".into() };
    let input: String = ins.iter().map(|v| format!("{f} {}\n", v.iter().map(enc).collect::<Vec<_>>().join(" "))).collect();
    use std::io::Write;
    let mut ch = std::process::Command::new(&cmd).stdin(std::process::Stdio::piped()).stdout(std::process::Stdio::piped()).spawn().expect("spawn --cmd");
    ch.stdin.take().unwrap().write_all(input.as_bytes()).ok();
    let out = ch.wait_with_output().expect("black box output"); let lines: Vec<String> = String::from_utf8_lossy(&out.stdout).lines().map(|x| x.to_string()).collect();
    let parse = |o: &str| -> Option<Val> { if o.trim() == "x" { return None; } let t: Vec<&str> = o.split_whitespace().collect();
        match ret.as_str() { "f32" => t.first()?.parse::<f32>().ok().map(Val::F), "f32list" => t.iter().map(|x| x.parse::<f32>().ok().map(Val::F)).collect::<Option<Vec<_>>>().map(Val::L),
            _ => t.first()?.parse::<i64>().ok().map(Val::I) } };
    let mut obs: Vec<(Vec<Val>, Val)> = Vec::new();
    for (v, o) in ins.iter().zip(&lines) { if let Some(y) = parse(o) { obs.push((v.clone(), y)); } }
    if obs.len() < 16 { eprintln!("blackbox {f}: only {} defined rows — no spec", obs.len()); std::process::exit(1); }
    // the authored equation must reproduce every observed row (tolerance for f32) — otherwise the reader refuses to write the spec
    let eq = arg(a, "--equation");
    if let Some(q) = &eq {
        let mut g = EGraph::default(); let mut args: Vec<Option<Id>> = Vec::new();
        let Some(root) = parse_eq(q, &mut g, &mut args) else { eprintln!("blackbox {f}: --equation does not parse"); std::process::exit(2) };
        let best = g.extract(); let mut bad = 0; let mut first = None;
        // f32 sums reorder (engine lanes / tiles): a row also passes inside the standard sum bound 2·n·u·M (Higham §3.1), where M =
        // the same equation evaluated on |inputs| (Σ|a·b| for sums of products) and n = the longest list argument
        let absv = |v: &Val| -> Val { match v { Val::F(x) => Val::F(x.abs()), Val::I(x) => Val::I(*x), Val::L(xs) => Val::L(xs.iter().map(|x| match x { Val::F(y) => Val::F(y.abs()), o => o.clone() }).collect()), o => o.clone() } };
        for (v, y) in &obs { let mut ev = Ev::new(&g, &best); for (j, id) in args.iter().enumerate() { if let (Some(id), Some(x)) = (id, v.get(j)) { ev.leaf.insert(g.find(*id), x.clone()); } }
            let got = ev.eval(root);
            let nmax = v.iter().map(|x| if let Val::L(xs) = x { xs.len() } else { 1 }).max().unwrap_or(1).max(1) as f32;
            let mut em = Ev::new(&g, &best); for (j, id) in args.iter().enumerate() { if let (Some(id), Some(x)) = (id, v.get(j)) { em.leaf.insert(g.find(*id), absv(x)); } }
            em.absm = true; let mag = norm(em.eval(root));
            let in_bound = |p: &Val, q: &Val, m: &Val| -> bool { let fl = |x: &Val| match norm(x.clone()) { Val::L(xs) => xs.iter().map(|z| match z { Val::F(f) => *f, Val::I(i) => *i as f32, _ => f32::NAN }).collect::<Vec<_>>(), Val::F(f) => vec![f], Val::I(i) => vec![i as f32], _ => vec![] };
                let (pa, qa, ma) = (fl(p), fl(q), fl(m)); pa.len() == qa.len() && pa.len() == ma.len() && pa.iter().zip(&qa).zip(&ma).all(|((x, y), mm)| (x - y).abs() <= (2.0 * nmax + 16.0) * (f32::EPSILON / 2.0) * mm.abs() + 1e-6) };
            if !same(&got, y) && !in_bound(&got, y, &mag) { bad += 1; if first.is_none() { first = Some(format!("{:?} → engine {:?}, equation {:?}", v.iter().map(enc).collect::<Vec<_>>(), y, got)); } } }
        if bad > 0 { eprintln!("blackbox {f}: equation REFUSED — {bad}/{} rows disagree; first: {}", obs.len(), first.unwrap_or_default().chars().take(300).collect::<String>()); std::process::exit(3); }
        eprintln!("blackbox {f}: equation agrees with all {} engine rows", obs.len());
    }
    let rows: Vec<serde_json::Value> = obs.iter().filter_map(|(v, y)| Some(serde_json::json!([v.iter().map(to_json).collect::<Option<Vec<_>>>()?, to_json(y)?]))).collect();
    let (ne, nh) = (8usize, 12usize);
    let mut row = serde_json::json!({"need": format!("s{:016x}", fnv(&format!("{sha}{f}{types:?}"))), "args": types.iter().map(|&t| TY[t as usize]).collect::<Vec<_>>(),
        "role": "ret", "effects": 0, "opaque_inputs": 0, "examples": rows[..ne], "holdout": rows[ne..ne + nh], "validate": rows[ne + nh..(ne + nh + 64).min(rows.len())],
        "provenance": {"src_sha256": sha, "licence": licence, "reader": "doctor-reader-1"}});
    if let Some(q) = eq { row["equation"] = q.into(); }
    let o = arg(a, "--out").expect("--out");
    let mut fh = std::fs::OpenOptions::new().create(true).append(a.iter().any(|x| x == "--append")).write(true).truncate(!a.iter().any(|x| x == "--append")).open(&o).expect("open --out");
    writeln!(fh, "{row}").ok();
    let mp = format!("{o}.oracle-map.json"); let mut m: serde_json::Value = std::fs::read_to_string(&mp).ok().and_then(|x| serde_json::from_str(&x).ok()).unwrap_or(serde_json::json!({}));
    m[row["need"].as_str().unwrap()] = serde_json::json!([cmd, f]); std::fs::write(&mp, m.to_string()).ok();
    eprintln!("blackbox {f}: {} probes, {} defined → spec {}", ins.len(), obs.len(), row["need"]);
}

/// The oracle service across the wall: inputs in, numbers out (`None` = undefined). The caller passes a need id; the map stays the
/// reader's. Batch call: one process per batch.
pub fn oracle(map_path: &str, need: &str, inputs: &[Vec<i64>]) -> Option<Vec<Option<i64>>> {
    let m: serde_json::Value = serde_json::from_str(&std::fs::read_to_string(map_path).ok()?).ok()?;
    let (cmd, f) = (m[need][0].as_str()?.to_string(), m[need][1].as_str()?.to_string());
    let input: String = inputs.iter().map(|v| format!("{f} {}\n", v.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(" "))).collect();
    use std::io::Write;
    let mut ch = std::process::Command::new(&cmd).stdin(std::process::Stdio::piped()).stdout(std::process::Stdio::piped()).spawn().ok()?;
    ch.stdin.take()?.write_all(input.as_bytes()).ok()?;
    let out = ch.wait_with_output().ok()?;
    Some(String::from_utf8_lossy(&out.stdout).lines().map(|l| l.trim().parse::<i64>().ok()).collect())
}
/// CEGIS against the live oracle: 2,000 edge + random int inputs; the first disagreement (oracle defined) is the counterexample.
pub fn oracle_cx(map_path: &str, need: &str, n_args: usize, e: &E) -> Option<(Vec<Val>, Val)> {
    const EDGE: [i64; 11] = [0, 1, -1, 2, -2, 3, 5, -7, 12, 60, -100];
    let mut seed = fnv(need) ^ 0x0ac1e; let mut ins: Vec<Vec<i64>> = Vec::new();
    // scales up to ±1e12 and mixed small / large argument pairs (a 1e6-only probe let a range-dependent overfit through, N5 div_ceil)
    let pick = |seed: &mut u64, k: usize| -> i64 { let span: i64 = [50, 2_000, 1_000_000, 1_000_000_000, 1_000_000_000_000][k % 5]; (mix(seed) % (2 * span as u64 + 1)) as i64 - span };
    for j in 0..4000usize { ins.push((0..n_args).map(|p| if j % 6 == 0 { EDGE[(mix(&mut seed) % 11) as usize] } else { let k = (j + p * (j % 3)) % 5; pick(&mut seed, k) }).collect()); }
    let outs = oracle(map_path, need, &ins)?;
    for (v, o) in ins.iter().zip(outs) { let Some(o) = o else { continue }; let args: Vec<Val> = v.iter().map(|x| Val::I(*x)).collect();
        if norm(ev_e(e, &args, None)) != Val::I(o) { return Some((args, Val::I(o))); } }
    None
}
