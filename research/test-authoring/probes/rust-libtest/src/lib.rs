//! The functions under test in every probe. Each has one deliberate defect.

/// Returns `count` instead of refusing a negative one with 0.
pub fn ensure_bytes(count: i64) -> i64 {
    count
}

#[derive(Debug, PartialEq)]
pub enum Error {
    NegativeCount(i64),
}

/// Accepts -1: the bound is off by one.
pub fn checked_bytes(count: i64) -> Result<i64, Error> {
    if count < -1 { Err(Error::NegativeCount(count)) } else { Ok(count) }
}

/// Panics with a message that names no reason.
pub fn require_bytes(count: i64) -> i64 {
    if count < 0 {
        panic!("boom");
    }
    count
}

#[derive(Debug, PartialEq)]
pub struct Limits {
    pub min: i64,
    pub max: i64,
}

/// Returns the bounds in the wrong order.
pub fn limits() -> Limits {
    Limits { min: 4096, max: 0 }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn assert_eq_prints_both() {
        assert_eq!(ensure_bytes(-1), 0);
    }
}
