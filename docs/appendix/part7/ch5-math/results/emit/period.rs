#[allow(unused_parens, unused_variables, unused_mut, unused_braces, clippy::all)]
fn f(a0: &[i64]) -> i64 { { let mut acc1: i64 = (0i64); for item1 in ((1i64)..(a0.len() as i64).wrapping_add((1i64))) { acc1 = (if ((((acc1 == (0i64)) as i64) != 0 && { let mut acc2: i64 = (1i64); for item2 in ((0i64)..(a0.len() as i64).wrapping_sub(item1)) { acc2 = (if ((a0[(item2) as usize] == a0[(item2.wrapping_add(item1)) as usize]) as i64) != 0 { acc2 } else { (0i64) }); } acc2 } != 0) as i64) != 0 { item1 } else { acc1 }); } acc1 } }
fn close(a: f32, b: f32) -> bool { (a.is_nan() && b.is_nan()) || (a - b).abs() <= 1e-5 + 1e-4 * a.abs().max(b.abs()) }
fn main() {
    let txt = std::fs::read_to_string(std::env::args().nth(1).unwrap()).unwrap(); let mut n = 0usize;
for line in txt.lines() { let mut t = line.split_whitespace(); n += 1;
        let n0: usize = t.next().unwrap().parse().unwrap(); let v0: Vec<i64> = (0..n0).map(|_| t.next().unwrap().parse().unwrap()).collect();
        let w: i64 = t.next().unwrap().parse().unwrap(); assert_eq!(f(&v0), w, "row {n}");
    }
    println!("ok {n}");
}
