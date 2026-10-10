#[allow(unused_parens, unused_variables)]
fn f(a0: i64, a1: i64) -> i64 { ((1i64) + ((a0 - (1i64)) / a1)) }
fn main() {
    assert_eq!(f(57i64, 9i64), 7i64);
    assert_eq!(f(68i64, 8i64), 9i64);
    assert_eq!(f(64i64, 4i64), 16i64);
    assert_eq!(f(89i64, 9i64), 10i64);
    assert_eq!(f(33i64, 9i64), 4i64);
    assert_eq!(f(25i64, 8i64), 4i64);
    assert_eq!(f(17i64, 7i64), 3i64);
    assert_eq!(f(15i64, 7i64), 3i64);
    assert_eq!(f(1i64, 10i64), 1i64);
    assert_eq!(f(0i64, 1i64), 0i64);
    assert_eq!(f(154i64, 2i64), 77i64);
    assert_eq!(f(0i64, 3i64), 0i64);
    assert_eq!(f(0i64, 3i64), 0i64);
    assert_eq!(f(0i64, 7i64), 0i64);
    assert_eq!(f(81i64, 4i64), 21i64);
    assert_eq!(f(136i64, 7i64), 20i64);
    assert_eq!(f(1i64, 9i64), 1i64);
    assert_eq!(f(0i64, 12i64), 0i64);
    assert_eq!(f(143i64, 5i64), 29i64);
    assert_eq!(f(116i64, 11i64), 11i64);
    assert_eq!(f(1i64, 7i64), 1i64);
    assert_eq!(f(1i64, 1i64), 1i64);
    assert_eq!(f(1i64, 6i64), 1i64);
    assert_eq!(f(0i64, 11i64), 0i64);
    println!("ok");
}
