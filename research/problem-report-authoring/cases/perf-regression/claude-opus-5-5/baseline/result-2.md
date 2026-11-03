## Summary

We upgraded Ferrygate from 4.6.2 to 4.7.0 and kept the config unchanged. p99 latency for 1 KiB responses proxied over loopback rose from 2.12 ms to 6.89 ms, and throughput fell 8.5%. Both figures are medians of ten 60-second `wrk` runs per version. Nothing fails: every run exited 0 and reported no non-2xx responses or socket errors.

We saw it in production first. After our edge proxies were upgraded on September 15, 2026, the edge dashboard showed p99 around 7 ms at the same traffic, above the 5 ms p99 target we have to meet.

Expected: on the setup below, 4.7.x with the default config shows a median p99 inside the range 4.6.2 shows, 2.06–2.23 ms over ten runs. How to get there is yours to choose. If the latency cost of the `worker.io_batch = "auto"` default is intended, we'd expect the release notes and the `worker.io_batch` reference page to say that `auto` raises tail latency, so that operators with a latency target know to set `off`. This expectation rests on 4.6.2, which the Supported versions page lists, and on the 4.7.0 release notes. They describe the new default only as "Reduces syscalls per request by up to 30%." and mention no latency cost.

The nearest existing items are !1482, the change the bisect below points to, and #2291. The description of !1482 reports the syscall reduction on a 64 KiB-body benchmark and gives no latency numbers. #2291 reports memory growth with HTTP/2 upstreams on 4.7.0, a different symptom.

## Environment

- CPU and memory: AMD EPYC 7443P (24 cores, SMT on), 128 GiB. Nothing else ran on the machine during the measurements.
- OS: Ubuntu 24.04.1, kernel `6.8.0-45-generic`, CPU governor `performance`.
- Ferrygate: release tarballs `ferrygate-4.6.2-x86_64-linux-gnu.tar.gz` and `ferrygate-4.7.0-x86_64-linux-gnu.tar.gz`. The bisect builds are from source with Rust 1.81.0 and `cargo build --release` on the same machine.
- Upstream: `tools/bench-upstream` from the `v4.7.0` tag, serving a 1 KiB body at `/1k` on `127.0.0.1:9000`, used for both versions.
- Load generator: `wrk` 4.2.0.
- Everything runs over loopback, pinned with `taskset`: Ferrygate to cores 0–7, the upstream to cores 12–15, and `wrk` to cores 16–23.
- Not established: whether a 4.7.x release after 4.7.0, or the default branch, still shows this. Only 4.7.0 was measured.

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

1. Start the upstream and Ferrygate with the config and pinning above.
1. Run one 30-second `wrk` warm-up and discard it.
1. Run this ten times and read the `99%` line and `Requests/sec`:

```bash
wrk -t4 -c128 -d60s --latency http://127.0.0.1:8080/1k
```

Measured on September 22 and 23, 2026.

## Results

Medians: 4.6.2 has p50 610.5us, p99 2.115ms and 198114 req/s; 4.7.0 has p50 945.5us, p99 6.885ms and 181192 req/s. The p99 ranges (2.06–2.23 ms and 6.51–7.40 ms) do not overlap. p99 is 3.3 times higher on 4.7.0.

| Run | 4.6.2 p50 | 4.6.2 p99 | 4.6.2 req/s | 4.7.0 p50 | 4.7.0 p99 | 4.7.0 req/s |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 604us | 2.08ms | 198904.12 | 941us | 6.84ms | 181522.95 |
| 2 | 612us | 2.11ms | 198186.73 | 933us | 6.51ms | 182310.44 |
| 3 | 609us | 2.14ms | 197733.40 | 952us | 7.12ms | 180417.83 |
| 4 | 617us | 2.06ms | 199051.87 | 947us | 6.93ms | 181006.27 |
| 5 | 611us | 2.19ms | 196912.55 | 938us | 6.62ms | 182044.91 |
| 6 | 606us | 2.10ms | 198620.31 | 960us | 7.40ms | 179588.02 |
| 7 | 615us | 2.12ms | 197402.66 | 944us | 6.77ms | 181377.60 |
| 8 | 608us | 2.09ms | 198777.09 | 936us | 6.98ms | 181890.15 |
| 9 | 620us | 2.23ms | 196388.24 | 949us | 6.70ms | 180733.48 |
| 10 | 610us | 2.13ms | 198041.58 | 955us | 7.05ms | 180255.36 |

4.6.2, run 2, as printed:

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

4.7.0, run 1, as printed:

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

`bench/bisect-p99.sh` runs the warm-up and three of the `wrk` runs above, and exits 1 when the median p99 exceeds 4 ms.

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

The bisect took seven steps. The parent commit `a51d07c` measured a median p99 of 2.12 ms, and the first bad commit measured 6.91 ms.

## Profiling data

Captured on 4.7.0 during run 4:

```bash
perf record -F 999 -g -p $(pidof ferrygate) -- sleep 30
perf report --no-children --percent-limit 3
```

Top of the report:

```text
    18.42%  ferrygate  [kernel.kallsyms]  [k] do_epoll_wait
    11.07%  ferrygate  ferrygate          [.] ferrygate::io::writer::Coalescer::flush_tick
     7.93%  ferrygate  [kernel.kallsyms]  [k] tcp_sendmsg_locked
     5.61%  ferrygate  ferrygate          [.] ferrygate::worker::loop::Tick::run
     3.12%  ferrygate  libc.so.6          [.] __memmove_avx_unaligned_erms
```

The same capture on 4.6.2 has no `Coalescer` frame. The flame graph from the 4.7.0 capture (`flame-470.svg`, 40.2 MB) and its `perf.data` (1.3 GB) are over the 10 MB attachment limit. I can share either on request.

## Workaround

With `io_batch = "off"` added under `[worker]` in the config above, 4.7.0, five runs of the same `wrk` command:

| Run | p50 | p99 | req/s |
| --- | --- | --- | --- |
| 1 | 628us | 2.29ms | 195816.00 |
| 2 | 624us | 2.25ms | 196240.18 |
| 3 | 631us | 2.33ms | 195402.77 |
| 4 | 626us | 2.27ms | 196011.43 |
| 5 | 630us | 2.31ms | 195655.09 |

The median p99 is 2.29 ms and the median throughput 195816 req/s. That closes most of the gap, but p99 stays about 8% above the 4.6.2 median and outside its range, and throughput stays 1.2% lower. Our edge team rolled out `io_batch = "off"` on September 22, 2026, and the edge dashboard p99 went back to about 2.4 ms.

## Possible cause (not verified)

This section is a guess from the commit title and the profile. I did not read `src/io/writer.rs` closely or test the idea, and the sections above stand without it. The coalescer appears to hold a small response until the end of the event-loop tick, so under load a response waits for the next `epoll_wait` round.

/label ~performance ~"needs triage"
