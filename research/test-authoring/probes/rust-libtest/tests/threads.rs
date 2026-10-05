//! Two tests that pass only when they run at the same time: each announces itself and waits for the other.

use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::{Duration, Instant};

static STARTED: AtomicUsize = AtomicUsize::new(0);

fn wait_for_the_other() {
    STARTED.fetch_add(1, Ordering::SeqCst);
    let deadline = Instant::now() + Duration::from_secs(3);
    while STARTED.load(Ordering::SeqCst) < 2 {
        assert!(Instant::now() < deadline, "the other test did not start within 3 seconds");
        std::thread::sleep(Duration::from_millis(10));
    }
}

#[test]
fn first() {
    wait_for_the_other();
}

#[test]
fn second() {
    wait_for_the_other();
}
