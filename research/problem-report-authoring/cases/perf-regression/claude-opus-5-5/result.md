## Summary

After upgrading Ferrygate from 4.6.2 to 4.7.0 with an unchanged config, p99 latency for proxied 1 KiB responses rose from 2.115 ms to 6.885 ms (3.3 times) and throughput fell from 198114 to 181192 req/s (8.5% lower). These are medians of ten `wrk` runs per version on the same idle machine; the p99 ranges do not overlap (4.6.2: 2.06–2.23 ms, 4.7.0: 6.51–7.40 ms). No request failed on either version.

In production we saw the same thing: the week after the upgrade on 2026-09-15, our edge dashboard showed p99 around 7 ms at unchanged traffic, over our 5 ms p99 target.

A `git bisect` between `v4.6.2` and `v4.7.0` stops at 3f9c2e7141d0b8a6e52c9d0f7a1e84b2c6d3f590, "io: coalesce small writes per event-loop tick (!1482)", which added `worker.io_batch` with the default `auto`.

Expected: with the default configuration, 4.7.x keeps the median p99 of the benchmark below within the 4.6.2 range (2.06–2.23 ms) and throughput within the 4.6.2 range (196388–199051 req/s). This rests on 4.6.2, a supported release, and on the 4.7.0 release notes, which describe `worker.io_batch` only as "Reduces syscalls per request by up to 30%"; neither they nor the `worker.io_batch` reference page mention a latency cost. How to get there (a change to the coalescer, a different default, or something else) is yours to choose. If higher tail latency is the intended trade-off of `auto`, I would ask that the release notes and the reference page say so.

## Environment

- CPU: AMD EPYC 7443P, 24 cores, SMT on; 128 GiB RAM
- OS: Ubuntu 24.04.1, kernel `6.8.0-45-generic`, CPU governor `performance`
- Nothing else ran on the machine during the measurements.
- Ferrygate: the release tarballs `ferrygate-4.6.2-x86_64-linux-gnu.tar.gz` and `ferrygate-4.7.0-x86_64-linux-gnu.tar.gz`. For the bisect, builds from source with Rust 1.81.0 and `cargo build --release`.
- Upstream: `tools/bench-upstream` from the `v4.7.0` tag, serving a 1 KiB body at `/1k` on `127.0.0.1:9000`, used for both versions.
- Load generator: `wrk` 4.2.0
- CPU pinning with `taskset`, all over loopback: Ferrygate on cores 0–7, the upstream on 12–15, `wrk` on 16–23.
- Not established: I did not test a 4.7.x release later than 4.7.0 or the default branch.

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

For each version: start the upstream and Ferrygate pinned as above, run `wrk` once for 30 seconds as a warm-up and discard it, then run this ten times:

```bash
wrk -t4 -c128 -d60s --latency http://127.0.0.1:8080/1k
```

Every run exited 0 and printed no `Non-2xx or 3xx responses` line and no socket error line.

## Results

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

All ten runs:

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
| **Median** | 610.5us | 2.115ms | 198114 | 945.5us | 6.885ms | 181192 |

## Bisect

Same machine and setup, builds from source as above. `bench/bisect-p99.sh` runs the 30-second warm-up and three of the `wrk` runs above, and exits 1 when the median p99 exceeds 4 ms.

```bash
git bisect start v4.7.0 v4.6.2
git bisect run bench/bisect-p99.sh
```

The bisect took seven steps and ended with:

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

The parent commit `a51d07c` measured a median p99 of 2.12 ms, and 3f9c2e71 measured 6.91 ms.

## Profiling data

`perf record -F 999 -g -p $(pidof ferrygate) -- sleep 30` during run 4 on 4.7.0, then `perf report --no-children --percent-limit 3`. Top of the output:

```text
    18.42%  ferrygate  [kernel.kallsyms]  [k] do_epoll_wait
    11.07%  ferrygate  ferrygate          [.] ferrygate::io::writer::Coalescer::flush_tick
     7.93%  ferrygate  [kernel.kallsyms]  [k] tcp_sendmsg_locked
     5.61%  ferrygate  ferrygate          [.] ferrygate::worker::loop::Tick::run
     3.12%  ferrygate  libc.so.6          [.] __memmove_avx_unaligned_erms
```

The same capture on 4.6.2 has no `Coalescer` frame. The flame graph from the 4.7.0 capture (40.2 MB) and `perf.data` (1.3 GB) are over the attachment limit here; I can share either on request.

## Workaround

With `io_batch = "off"` added under `[worker]` in the config above, 4.7.0, five runs of the same command:

| Run | p50 | p99 | req/s |
| --- | --- | --- | --- |
| 1 | 628us | 2.29ms | 195816.00 |
| 2 | 624us | 2.25ms | 196240.18 |
| 3 | 631us | 2.33ms | 195402.77 |
| 4 | 626us | 2.27ms | 196011.43 |
| 5 | 630us | 2.31ms | 195655.09 |

Median p99 2.29 ms and 195816 req/s. This recovers most of the regression, not all of it: the p99 range (2.25–2.33 ms) is still above the 4.6.2 range (2.06–2.23 ms), and throughput is 1.2% below 4.6.2. I have not investigated that remainder; the bisect threshold of 4 ms would not have caught it.

Our edge team rolled out `io_batch = "off"` on 2026-09-22, and the dashboard p99 went back to about 2.4 ms.

## Related issues

I searched issues and merge requests in all states for `latency 4.7`, `p99`, `io_batch`, `coalesce`, and `regression 4.7.0`, and found no report of this. !1482 is the bisected change; its description reports the syscall reduction on a 64 KiB-body benchmark and gives no latency numbers. #2291 ("4.7.0: memory growth with HTTP/2 upstreams") is open and reports a different symptom.

## Possible cause (unverified)

This section is a guess from the commit title and the profile above; I have not read `src/io/writer.rs` closely or tested the idea, and the sections above stand without it. The coalescer seems to hold a small response until the end of the event-loop tick, so under load a response waits for the next `epoll_wait` round.

Internal host names and customer details are left out of this report.

/label ~performance ~"needs triage"
