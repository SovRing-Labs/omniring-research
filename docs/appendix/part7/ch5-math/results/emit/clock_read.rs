#[allow(unused_parens, unused_variables, unused_mut, unused_braces, clippy::all)]
fn f(a0: i64, a1: i64, a2: i64) -> i64 { { let mut acc1: i64 = (-1i64); for item1 in ((0i64)..(105i64)) { acc1 = (if ((((acc1 == (-1i64)) as i64) != 0 && (((((item1 % (3i64)) == a0) as i64) != 0 && (((((item1 % (5i64)) == a1) as i64) != 0 && (((item1 % (7i64)) == a2) as i64) != 0) as i64) != 0) as i64) != 0) as i64) != 0 { item1 } else { acc1 }); } acc1 } }
fn close(a: f32, b: f32) -> bool { (a.is_nan() && b.is_nan()) || (a - b).abs() <= 1e-5 + 1e-4 * a.abs().max(b.abs()) }
fn main() {
    let txt = std::fs::read_to_string(std::env::args().nth(1).unwrap()).unwrap(); let mut n = 0usize;
for line in txt.lines() { let mut t = line.split_whitespace(); n += 1;
        let a0: i64 = t.next().unwrap().parse().unwrap();
        let a1: i64 = t.next().unwrap().parse().unwrap();
        let a2: i64 = t.next().unwrap().parse().unwrap();
        let w: i64 = t.next().unwrap().parse().unwrap(); assert_eq!(f(a0, a1, a2), w, "row {n}");
    }
    println!("ok {n}");
}
