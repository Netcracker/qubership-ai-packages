use rstest::rstest;
use stream::ensure_bytes;

#[rstest]
#[case(-1)]
#[case(-2)]
fn refuses_negative(#[case] n: i64) {
    assert_eq!(ensure_bytes(n), 0);
}

#[rstest]
#[case::minus_one(-1)]
#[case::minus_two(-2)]
fn refuses_negative_named(#[case] n: i64) {
    assert_eq!(ensure_bytes(n), 0);
}
