Title: p99 latency 3.3x higher on 4.7.0 than on 4.6.2 for 1 KiB responses with the default `worker.io_batch`

## Summary

With the same config, `wrk -t4 -c128 -d60s --latency` against a 1 KiB response through Ferrygate shows a median p99 of 6.885 ms on 4.7.0 and 2.115 ms on 4.6.2. That is 3.3 times higher. Median p50 rises from 610.5 us to 945.5 us, and throughput drops 8.5% (198114 to 181192 req/s). Over ten runs per version the p99 ranges do not overlap (2.06–2.23 ms on 4.6.2, 6.51–7.40 ms on 4.7.0). No run had errors or non-2xx responses.

Last good version is 4.6.2 and first bad is 4.7.0. Bisecting between the two tags ends at `3f9c2e7` (!1482, "io: coalesce small writes per event-loop tick"); see Bisect.

Expected: with the default `worker.io_batch = "auto"`, this benchmark's median p99 stays near the 4.6.2 level, and in any case well under 4 ms (the threshold my bisect script used; 4.6.2 measures 2.1 ms). I did not find a latency cost mentioned anywhere for the new default. The 4.7.0 release notes say: "New: write coalescing for small responses (`worker.io_batch`, default `auto`). Reduces syscalls per request by up to 30%." The tolerance and the way to meet it are the project's call.

A production deployment (operator's dashboard, which I have not seen) reported p99 around 7 ms at unchanged traffic after upgrading from 4.6.2 to 4.7.0 on 2026-09-15.

Nearest existing item: !1482 is the merge request the bisect ends at. Its description reports the syscall reduction on a 64 KiB-body benchmark and gives no latency numbers. Issue #2291 (open, memory growth with HTTP/2 upstreams) has a different symptom.

## Environment

- Ferrygate: release tarballs `ferrygate-4.6.2-x86_64-linux-gnu.tar.gz` and `ferrygate-4.7.0-x86_64-linux-gnu.tar.gz`. Not tested on the development branch.
- Hardware: AMD EPYC 7443P (24 cores, SMT on), 128 GiB, CPU governor `performance`. Nothing else ran on the machine during the measurements.
- OS: Ubuntu 24.04.1, kernel `6.8.0-45-generic`.
- Load generator: `wrk` 4.2.0, over loopback.
- Upstream: `tools/bench-upstream` from the 4.7.0 tag, serving a 1 KiB body at `/1k`.
- Pinning (`taskset`): Ferrygate on cores 0–7, upstream on cores 12–15, `wrk` on cores 16–23.
- Bisect builds: Rust 1.81.0, `cargo build --release`, same machine.
- Config, identical for both versions:

```toml
[listen]
addr = "127.0.0.1:8080"

[worker]
threads = 8

[[route]]
path = "/"
upstream = "http://127.0.0.1:9000"
```

The host and operator names are omitted.

## How to measure

For each version: one 30-second warm-up run, discarded, then ten runs of

```bash
wrk -t4 -c128 -d60s --latency http://127.0.0.1:8080/1k
```

Every run exited 0 and printed no `Non-2xx or 3xx responses` line and no socket error line.

Only this workload was measured: 1 KiB responses, 128 connections, 8 worker threads. The exact `taskset` and launch command lines for Ferrygate and `bench-upstream` were not recorded.

## Results

Run 2 on 4.6.2 and run 1 on 4.7.0, as printed:

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

## Bisect

`git bisect run bench/bisect-p99.sh` runs the warm-up and three `wrk` runs from above and exits 1 when the median p99 exceeds 4 ms.

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

The bisect took seven steps. The parent commit `a51d07c` measured a median p99 of 2.12 ms, and `3f9c2e7` measured 6.91 ms.

## Profiling data

Captured during run 4 on 4.7.0 with `perf record -F 999 -g -p $(pidof ferrygate) -- sleep 30`. This is the top of `perf report --no-children --percent-limit 3`, which lists nothing else:

```text
    18.42%  ferrygate  [kernel.kallsyms]  [k] do_epoll_wait
    11.07%  ferrygate  ferrygate          [.] ferrygate::io::writer::Coalescer::flush_tick
     7.93%  ferrygate  [kernel.kallsyms]  [k] tcp_sendmsg_locked
     5.61%  ferrygate  ferrygate          [.] ferrygate::worker::loop::Tick::run
     3.12%  ferrygate  libc.so.6          [.] __memmove_avx_unaligned_erms
```

The same capture on 4.6.2 has no `Coalescer` frame. The flame graph (`flame-470.svg`, 40.2 MB) and `perf.data` (1.3 GB) exceed the instance's 10 MB attachment limit. I can provide them through another route on request.

## Workaround

Adding `io_batch = "off"` under `[worker]` in the config above, on 4.7.0, with five runs of the same command:

| Run | p50 | p99 | req/s |
| --- | --- | --- | --- |
| 1 | 628us | 2.29ms | 195816.00 |
| 2 | 624us | 2.25ms | 196240.18 |
| 3 | 631us | 2.33ms | 195402.77 |
| 4 | 626us | 2.27ms | 196011.43 |
| 5 | 630us | 2.31ms | 195655.09 |

The median p99 is 2.29 ms and the median throughput 195816 req/s. That is most of the way back to 4.6.2 (2.115 ms, 198114 req/s), but the p99 range (2.25–2.33 ms) still sits above the 4.6.2 range (2.06–2.23 ms).

The operators of the production deployment set `io_batch = "off"` on 2026-09-22 and report that their dashboard p99 went back to about 2.4 ms. This is their observation; I did not take it.

## Possible cause (unverified)

This is a guess from the commit title and the profile above. I have not read `src/io/writer.rs` closely or tested it. The coalescer may hold a small response until the end of the event-loop tick, so that under load a response waits for the next `epoll_wait` round. The report above stands without it.

/label ~performance ~"needs triage"
