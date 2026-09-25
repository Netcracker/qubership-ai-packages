use stream::{ensure_bytes, limits, Limits};

#[test]
fn two_asserts() {
    let result = ensure_bytes(-1);
    assert_eq!(result, 0, "first");
    assert!(result > 0, "second");
}

#[test]
fn whole_struct() {
    assert_eq!(limits(), Limits { min: 0, max: 4096 });
}
