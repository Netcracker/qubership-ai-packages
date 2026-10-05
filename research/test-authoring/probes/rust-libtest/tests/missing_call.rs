use stream::ensure_bytes;

#[test]
fn calls_a_function_the_crate_lacks() {
    assert_eq!(stream::ensure_bytes_or_zero(-1), ensure_bytes(0));
}
