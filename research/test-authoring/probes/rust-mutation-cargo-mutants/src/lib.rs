pub mod other;

/// Sums the integers in `0..n`; a non-positive `n` sums nothing.
///
/// The sum wraps rather than panics, so the mutants of `i += 1` that never reach `n` run until the timeout instead
/// of overflowing in a time that depends on the machine.
pub fn sum_below(n: i64) -> i64 {
    let mut total: i64 = 0;
    let mut i = 0;
    while i < n {
        total = total.wrapping_add(i);
        i += 1;
    }
    total
}

/// Whether `n` is strictly positive.
pub fn is_positive(n: i64) -> bool {
    n > 0
}

/// A label for `n`, which no test reads.
pub fn label(n: i64) -> String {
    format!("n={n}")
}

/// A value that has no `Default`, so replacing the body with `Default::default()` does not compile.
pub struct Count(pub u32);

pub fn count_of(n: u32) -> Count {
    Count(n)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sums_below_four() {
        assert_eq!(sum_below(4), 6);
    }

    #[test]
    fn positive_and_negative() {
        assert!(is_positive(5));
        assert!(!is_positive(-5));
    }

    #[test]
    fn count_holds_its_value() {
        assert_eq!(count_of(3).0, 3);
    }
}
