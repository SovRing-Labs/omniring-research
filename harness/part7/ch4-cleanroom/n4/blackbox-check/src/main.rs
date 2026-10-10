// N4 black-box check: our clean-room rebuilds (emitted from name-free specs) vs the real crate functions on 1M random i64 pairs.
use num_integer::Average;
fn ours_floor(a0: i64, a1: i64) -> i64 { (a0 & a1).wrapping_add((a0 ^ a1).wrapping_shr(((1i64) as u32) & 63)) }
fn ours_ceil(a0: i64, a1: i64) -> i64 { (a0 | a1).wrapping_sub((a0 ^ a1).wrapping_shr(((1i64) as u32) & 63)) }
fn main() {
    let mut x: u64 = 0x9E3779B97F4A7C15; let mut r = || { x = x.wrapping_add(0x9E3779B97F4A7C15); let mut z = x; z = (z ^ (z >> 30)).wrapping_mul(0xBF58476D1CE4E5B9); z = (z ^ (z >> 27)).wrapping_mul(0x94D049BB133111EB); (z ^ (z >> 31)) as i64 };
    let edge = [0i64, 1, -1, 2, -2, i64::MAX, i64::MIN, i64::MAX - 1, i64::MIN + 1];
    let (mut n, mut bad_f, mut bad_c) = (0u64, 0u64, 0u64);
    for i in 0..1_000_000u64 { let (a, b) = if i < 81 { (edge[(i % 9) as usize], edge[(i / 9) as usize]) } else { (r(), r()) };
        n += 1; if ours_floor(a, b) != a.average_floor(&b) { bad_f += 1; } if ours_ceil(a, b) != a.average_ceil(&b) { bad_c += 1; } }
    println!("pairs {n} · floor mismatches {bad_f} · ceil mismatches {bad_c}");
}
