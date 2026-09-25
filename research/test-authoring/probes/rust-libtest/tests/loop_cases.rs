use stream::ensure_bytes;

#[test]
fn loop_without_message() {
    for n in [-1, -2] {
        assert_eq!(ensure_bytes(n), 0);
    }
}

#[test]
fn loop_with_message() {
    for n in [-1, -2] {
        assert_eq!(ensure_bytes(n), 0, "ensure_bytes({n})");
    }
}
