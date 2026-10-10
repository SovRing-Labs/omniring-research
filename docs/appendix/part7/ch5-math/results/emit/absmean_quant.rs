#[allow(unused_parens, unused_variables, unused_mut, unused_braces, clippy::all)]
fn f(a0: &[f32]) -> Vec<f32> { (0..(a0.len() as i64)).map(|item1: i64| (a0[(item1) as usize] / ({ let mut acc2: f32 = ((0i64) as f32); for item2 in ((0i64)..(a0.len() as i64)) { acc2 = (acc2 + a0[(item2) as usize].abs()); } acc2 } / ((a0.len() as i64) as f32)).max((1e-5f32))).round().min(((1i64) as f32)).max(((-1i64) as f32))).collect::<Vec<_>>() }
fn close(a: f32, b: f32) -> bool { (a.is_nan() && b.is_nan()) || (a - b).abs() <= 1e-5 + 1e-4 * a.abs().max(b.abs()) }
fn main() {
    let txt = std::fs::read_to_string(std::env::args().nth(1).unwrap()).unwrap(); let mut n = 0usize;
for line in txt.lines() { let mut t = line.split_whitespace(); n += 1;
        let n0: usize = t.next().unwrap().parse().unwrap(); let v0: Vec<f32> = (0..n0).map(|_| t.next().unwrap().parse().unwrap()).collect();
        let m: usize = t.next().unwrap().parse().unwrap(); let w: Vec<f32> = (0..m).map(|_| t.next().unwrap().parse().unwrap()).collect(); let tl: Vec<f32> = (0..m).map(|_| t.next().map(|x| x.parse().unwrap()).unwrap_or(0.0)).collect(); let r = f(&v0); assert!(r.len() == w.len() && r.iter().zip(&w).zip(&tl).all(|((x, y), e)| close(*x, *y) || (x - y).abs() <= *e), "row {n}");
    }
    println!("ok {n}");
}
