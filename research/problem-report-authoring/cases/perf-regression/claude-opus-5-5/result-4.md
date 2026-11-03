## Summary

Proxying a 1 KiB response through Ferrygate 4.7.0 under load gives a p99 latency 3.3 times that of 4.6.2, on the same machine with the same config. Over ten `wrk` runs per version, the median p99 is 6.885 ms on 4.7.0 and 2.115 ms on 4.6.2, and the ranges do not overlap (6.51–7.40 ms against 2.06–2.23 ms). Median throughput drops 8.5%, from 198114 to 181192 requests per second. No run reports a non-2xx response or a socket error.

Expected: with the default `worker.io_batch` (`auto`), the median p99 of ten runs of the command below is no higher than 4.7.0 gives with `io_batch = "off"`, whose highest run was 2.33 ms. 4.6.2 is in a series the "Supported versions" page still lists, and the 4.7.0 release notes describe write coalescing only as "Reduces syscalls per request by up to 30%", with no latency cost. Whether that comes from a change to the coalescer or from a different default is yours to choose.

A `git bisect` between the two tags points to 3f9c2e71 (!1482, "io: coalesce small writes per event-loop tick"), and `io_batch = "off"` brings p99 back to 2.29 ms (see Workaround).

In our production edge, the dashboard showed p99 at about 7 ms at unchanged traffic in the week after we upgraded from 4.6.2 to 4.7.0 on 2026-09-15.

The only other open 4.7.0 regression I found, #2291, reports memory growth with HTTP/2 upstreams, a different symptom.

## Environment

- AMD EPYC 7443P (24 cores, SMT on), 128 GiB RAM, Ubuntu 24.04.1, kernel `6.8.0-45-generic`, CPU governor `performance`. Nothing else ran on the machine during the measurements.
- Ferrygate from the release tarballs `ferrygate-4.6.2-x86_64-linux-gnu.tar.gz` and `ferrygate-4.7.0-x86_64-linux-gnu.tar.gz`. The bisect builds used Rust 1.81.0 and `cargo build --release`.
- `wrk` 4.2.0.
- Upstream: `tools/bench-upstream` from the v4.7.0 tag, serving a 1 KiB body at `/1k` on `127.0.0.1:9000`.
- Everything over loopback, pinned with `taskset`: Ferrygate to cores 0-7, the upstream to 12-15, `wrk` to 16-23.
- Not tested on a 4.7.x release newer than 4.7.0 or on the default branch.

Config, identical for both versions:

```toml
[listen]
addr = "127.0.0.1:8080"

[worker]
threads = 8

[[route]]
path = "/"
upstream = "http://127.0.0.1:9000"
```

## How to measure

For each version: one 30-second `wrk` warm-up run, discarded, then ten runs of

```bash
wrk -t4 -c128 -d60s --latency http://127.0.0.1:8080/1k
```

Measurements taken on 2026-09-22 and 2026-09-23.

## Results

Medians over the ten runs:

| Version | p50 | p99 (range) | req/s |
| --- | --- | --- | --- |
| 4.6.2 | 610.5 µs | 2.115 ms (2.06–2.23) | 198114 |
| 4.7.0 | 945.5 µs | 6.885 ms (6.51–7.40) | 181192 |

All runs:

| Run | 4.6.2 p50 | 4.6.2 p99 | 4.6.2 req/s | 4.7.0 p50 | 4.7.0 p99 | 4.7.0 req/s |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 604 µs | 2.08 ms | 198904.12 | 941 µs | 6.84 ms | 181522.95 |
| 2 | 612 µs | 2.11 ms | 198186.73 | 933 µs | 6.51 ms | 182310.44 |
| 3 | 609 µs | 2.14 ms | 197733.40 | 952 µs | 7.12 ms | 180417.83 |
| 4 | 617 µs | 2.06 ms | 199051.87 | 947 µs | 6.93 ms | 181006.27 |
| 5 | 611 µs | 2.19 ms | 196912.55 | 938 µs | 6.62 ms | 182044.91 |
| 6 | 606 µs | 2.10 ms | 198620.31 | 960 µs | 7.40 ms | 179588.02 |
| 7 | 615 µs | 2.12 ms | 197402.66 | 944 µs | 6.77 ms | 181377.60 |
| 8 | 608 µs | 2.09 ms | 198777.09 | 936 µs | 6.98 ms | 181890.15 |
| 9 | 620 µs | 2.23 ms | 196388.24 | 949 µs | 6.70 ms | 180733.48 |
| 10 | 610 µs | 2.13 ms | 198041.58 | 955 µs | 7.05 ms | 180255.36 |

Run 2 on 4.6.2:

```text
Running 1m test @ http://127.0.0.1:8080/1k
  4 threads and 128 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   712.44us  402.18us  18.31ms   91.27%
    Req/Sec    49.81k     2.13k   55.02k    71.83%
  Latency Distribution
     50%  612.00us
     75%  801.00us
     90%    1.09ms
     99%    2.11ms
  11891204 requests in 1.00m, 13.21GB read
Requests/sec: 198186.73
Transfer/sec:    225.41MB
```

Run 1 on 4.7.0:

```text
Running 1m test @ http://127.0.0.1:8080/1k
  4 threads and 128 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.21ms    1.14ms  41.72ms   93.05%
    Req/Sec    45.62k     3.87k   53.44k    68.12%
  Latency Distribution
     50%  941.00us
     75%    1.32ms
     90%    2.07ms
     99%    6.84ms
  10891377 requests in 1.00m, 12.10GB read
Requests/sec: 181522.95
Transfer/sec:    206.47MB
```

## Bisect

Built from source on the same machine. The bisect script runs the warm-up and three of the `wrk` runs above, and exits 1 when the median p99 exceeds 4 ms.

```bash
git bisect start v4.7.0 v4.6.2
git bisect run bench/bisect-p99.sh
```

```text
3f9c2e7141d0b8a6e52c9d0f7a1e84b2c6d3f590 is the first bad commit
commit 3f9c2e7141d0b8a6e52c9d0f7a1e84b2c6d3f590
Author: Tomas Leino <tleino@ferrygate.dev>
Date:   Tue Jul 14 10:22:31 2026 +0200

    io: coalesce small writes per event-loop tick (!1482)

 src/io/writer.rs      | 88 +++++++++++++++++++++++++++++++++-----
 src/worker/loop.rs    | 23 ++++++----
 src/config/worker.rs  | 11 +++++-
 3 files changed, 102 insertions(+), 20 deletions(-)
```

The bisect took seven steps. The parent commit `a51d07c` measured a median p99 of 2.12 ms, and 3f9c2e71 measured 6.91 ms. The description of !1482 reports the syscall reduction on a 64 KiB-body benchmark and gives no latency numbers.

## Profiling data

Captured during run 4 on 4.7.0 with `perf record -F 999 -g -p $(pidof ferrygate) -- sleep 30`. First lines of `perf report --no-children --percent-limit 3`:

```text
    18.42%  ferrygate  [kernel.kallsyms]  [k] do_epoll_wait
    11.07%  ferrygate  ferrygate          [.] ferrygate::io::writer::Coalescer::flush_tick
     7.93%  ferrygate  [kernel.kallsyms]  [k] tcp_sendmsg_locked
     5.61%  ferrygate  ferrygate          [.] ferrygate::worker::loop::Tick::run
     3.12%  ferrygate  libc.so.6          [.] __memmove_avx_unaligned_erms
```

The same capture on 4.6.2 has no `Coalescer` frame. The flame graph of the 4.7.0 capture (40.2 MB) and `perf.data` (1.3 GB) are over the attachment limit; I can share either on request.

## Workaround

With `io_batch = "off"` added under `[worker]` in the config above, five runs of the same command on 4.7.0:

| Run | p50 | p99 | req/s |
| --- | --- | --- | --- |
| 1 | 628 µs | 2.29 ms | 195816.00 |
| 2 | 624 µs | 2.25 ms | 196240.18 |
| 3 | 631 µs | 2.33 ms | 195402.77 |
| 4 | 626 µs | 2.27 ms | 196011.43 |
| 5 | 630 µs | 2.31 ms | 195655.09 |

The median p99 is 2.29 ms and the median throughput 195816 req/s. That recovers most of the gap but not all of it: p99 stays 8% above 4.6.2's 2.115 ms, and throughput 1.2% below. I have not looked for the source of that remainder; the bisect threshold of 4 ms would not catch it.

In production, the dashboard p99 went back to about 2.4 ms after we rolled out `io_batch = "off"` on 2026-09-22.

## Possible cause (untested)

This is a guess from the commit title and the profile. I did not read `src/io/writer.rs` closely or test the idea, and the sections above stand without it. The coalescer seems to hold a small response until the end of the event-loop tick, so under load the response waits for the next `epoll_wait` round.

/label ~performance ~"needs triage"
