use stream::{checked_bytes, Error};

#[test]
fn matches_variant() {
    let r = checked_bytes(-1);
    assert!(matches!(r, Err(Error::NegativeCount(_))));
}

#[test]
fn unwrap_err_eq() {
    let r = checked_bytes(-1);
    assert_eq!(r.unwrap_err(), Error::NegativeCount(-1));
}
