#[allow(unused_parens, unused_variables, unused_mut, unused_braces, clippy::all)]
fn f(a0: i64) -> i64 { { let mut st = (a0,); loop { #[allow(unused_variables)] let (s1_0,) = st; if ((s1_0.wrapping_mul(s1_0) > a0) as i64) == 0 { break; } st = ((s1_0.wrapping_add((a0 / s1_0)) / (2i64)),); } st }.0 }
fn close(a: f32, b: f32) -> bool { (a.is_nan() && b.is_nan()) || (a - b).abs() <= 1e-5 + 1e-4 * a.abs().max(b.abs()) }
fn main() {
    let txt = std::fs::read_to_string(std::env::args().nth(1).unwrap()).unwrap(); let mut n = 0usize;
for line in txt.lines() { let mut t = line.split_whitespace(); n += 1;
        let a0: i64 = t.next().unwrap().parse().unwrap();
        let w: i64 = t.next().unwrap().parse().unwrap(); assert_eq!(f(a0), w, "row {n}");
    }
    println!("ok {n}");
}
