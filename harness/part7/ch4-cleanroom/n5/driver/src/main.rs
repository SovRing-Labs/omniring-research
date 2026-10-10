// N5 black-box driver: the crate's PUBLIC API only (names from its docs), one call per stdin line "fn a b" → stdout result or "x"
// (panic / overflow / None). The doctor's black-box reader sees only these lines — never the crate's source.
use num_integer::{Integer, Roots};
fn call(f: &str, a: &[i64]) -> Option<i64> {
    Some(match (f, a.len()) {
        ("gcd", 2) => a[0].gcd(&a[1]), ("lcm", 2) => a[0].checked_mul(1).and_then(|_| std::panic::catch_unwind(|| a[0].lcm(&a[1])).ok())?,
        ("div_floor", 2) => { if a[1] == 0 { return None; } a[0].div_floor(&a[1]) }
        ("mod_floor", 2) => { if a[1] == 0 { return None; } a[0].mod_floor(&a[1]) }
        ("div_ceil", 2) => { if a[1] == 0 { return None; } Integer::div_ceil(&a[0], &a[1]) }
        ("is_multiple_of", 2) => a[0].is_multiple_of(&a[1]) as i64,
        ("binomial", 2) => { if !(0..=60).contains(&a[0]) || !(0..=60).contains(&a[1]) { return None; } std::panic::catch_unwind(|| num_integer::binomial(a[0], a[1])).ok()? }
        ("sqrt", 1) => { if a[0] < 0 { return None; } a[0].sqrt() }
        ("cbrt", 1) => a[0].cbrt(),
        _ => return None,
    })
}
fn main() {
    std::panic::set_hook(Box::new(|_| {}));
    use std::io::{BufRead, Write}; let out = std::io::stdout(); let mut o = out.lock();
    for l in std::io::stdin().lock().lines() { let l = l.unwrap(); let mut p = l.split_whitespace(); let f = p.next().unwrap_or("");
        let a: Vec<i64> = p.filter_map(|x| x.parse().ok()).collect();
        match std::panic::catch_unwind(|| call(f, &a)) { Ok(Some(v)) => writeln!(o, "{v}").unwrap(), _ => writeln!(o, "x").unwrap() } }
}
