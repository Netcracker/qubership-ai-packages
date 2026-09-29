use stream::ensure_bytes;

#[test]
fn assert_eq_plain() {
    assert_eq!(ensure_bytes(-1), 0);
}

#[test]
fn assert_eq_with_message() {
    let n = -1;
    assert_eq!(ensure_bytes(n), 0, "ensure_bytes({})", n);
}

#[test]
fn assert_eq_swapped() {
    assert_eq!(0, ensure_bytes(-1));
}

#[test]
fn assert_eq_debug_form() {
    assert_eq!(format!("{} bytes", ensure_bytes(-1)), "0 bytes");
}

#[test]
fn assert_ne_plain() {
    assert_ne!(ensure_bytes(-1), -1);
}

#[test]
fn assert_plain() {
    assert!(ensure_bytes(-1) == 0);
}

#[test]
fn assert_with_message() {
    assert!(ensure_bytes(-1) == 0, "ensure_bytes(-1)");
}

#[test]
fn panic_plain() {
    if ensure_bytes(-1) != 0 {
        panic!();
    }
}
