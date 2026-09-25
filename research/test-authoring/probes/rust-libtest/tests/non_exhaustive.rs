//! A `match` written before `Unit::Kibibytes` was added, which the compiler rejects.

enum Unit {
    Bytes,
    Kibibytes,
}

fn scale(unit: Unit) -> i64 {
    match unit {
        Unit::Bytes => 1,
    }
}

#[test]
fn bytes_scale_by_one() {
    assert_eq!(scale(Unit::Bytes), 1);
    let _ = Unit::Kibibytes;
}
