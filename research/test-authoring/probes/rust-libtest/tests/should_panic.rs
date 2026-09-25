use stream::require_bytes;

#[test]
#[should_panic(expected = "negative")]
fn other_message() {
    require_bytes(-1);
}

#[test]
#[should_panic(expected = "oo")]
fn matching_substring() {
    require_bytes(-1);
}

#[test]
#[should_panic(expected = "boom")]
fn no_panic() {
    require_bytes(1);
}
