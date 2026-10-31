## Summary

With the default `worker.io_batch` (`auto`), Ferrygate 4.7.0 has a p99 latency of 6.885 ms on a 1 KiB proxied response, against 2.115 ms on 4.6.2 with the same config, machine, and load. Throughput is 8.5% lower (181192 against 198114 requests per second). Medians of ten 60-second `wrk` runs per version; the p99 ranges do not overlap (4.6.2: 2.06 to 2.23 ms, 4.7.0: 6.51 to 7.40 ms). No run had errors or non-2xx responses.

The first bad commit is 3f9c2e7141d0b8a6e52c9d0f7a1e84b2c6d3f590, "io: coalesce small writes per event-loop tick (!1482)". Setting `io_batch = "off"` brings p99 back to 2.29 ms (see Workaround).

Expected: on this workload, 4.7.0 with default settings has a p99 in the range 4.6.2 shows (2.06 to 2.23 ms), and not 6.5 to 7.4 ms. A test can compare the median p99 of repeated runs of the command under "How to measure" on both versions. The exact threshold is the project's to choose. The expectation rests on 4.6.2, which the supported versions page lists, behaving this way with the same config. The 4.7.0 release notes announce `worker.io_batch` as a default-on change that "reduces syscalls per request by up to 30%" and mention no latency cost. !1482 reports its syscall reduction on a 64 KiB-body benchmark and gives no latency numbers.

In a production deployment, p99 edge latency went from under 5 ms to about 7 ms at the same traffic in the week after the 4.6.2 to 4.7.0 upgrade. I did not run that deployment; the numbers are from its owners' dashboard.

Not established: I did not test a 4.7.x release later than 4.7.0 or the development branch.

## Environment

- Ferrygate 4.6.2 and 4.7.0, from the release tarballs `ferrygate-4.6.2-x86_64-linux-gnu.tar.gz` and `ferrygate-4.7.0-x86_64-linux-gnu.tar.gz`. The bisect used builds from source with Rust 1.81.0 and `cargo build --release`.
- AMD EPYC 7443P (24 cores, SMT on), 128 GiB, Ubuntu 24.04.1, kernel `6.8.0-45-generic`, CPU governor `performance`. Nothing else ran on the machine during the measurements.
- Upstream: `tools/bench-upstream` from the 4.7.0 tag, serving a 1 KiB body at `/1k`.
- `wrk` 4.2.0, over loopback.
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

## How to measure

Ferrygate runs on cores 0-7, the upstream on 12-15, and `wrk` on 16-23, each started under `taskset`. For each version: one 30-second warm-up run, discarded, then ten runs of

```bash
wrk -t4 -c128 -d60s --latency http://127.0.0.1:8080/1k
```

Every run exited 0 and printed no `Non-2xx or 3xx responses` line and no socket error line.

## Results

All numbers were measured by me on 2026-09-22 and 2026-09-23. Run 2 on 4.6.2, as printed:

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

Run 1 on 4.7.0, as printed:

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

All ten runs of each version:

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

Medians: 4.6.2 has p50 610.5us, p99 2.115ms, 198114 req/s. 4.7.0 has p50 945.5us, p99 6.885ms, 181192 req/s.

## Bisect

Last good `v4.6.2`, first bad `v4.7.0`. `bench/bisect-p99.sh` runs the warm-up and three `wrk` runs from above and exits 1 when the median p99 exceeds 4 ms.

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

The bisect took seven steps. The parent commit `a51d07c` measured a median p99 of 2.12 ms, and the bad commit 6.91 ms.

## Profiling data

`perf record -F 999 -g -p $(pidof ferrygate) -- sleep 30` during run 4 on 4.7.0, then `perf report --no-children --percent-limit 3`. The listing is the top of the output, trimmed to the lines of interest:

```text
    18.42%  ferrygate  [kernel.kallsyms]  [k] do_epoll_wait
    11.07%  ferrygate  ferrygate          [.] ferrygate::io::writer::Coalescer::flush_tick
     7.93%  ferrygate  [kernel.kallsyms]  [k] tcp_sendmsg_locked
     5.61%  ferrygate  ferrygate          [.] ferrygate::worker::loop::Tick::run
     3.12%  ferrygate  libc.so.6          [.] __memmove_avx_unaligned_erms
```

The same capture on 4.6.2 has no `Coalescer` frame. The flame graph of the 4.7.0 capture (`flame-470.svg`, 40.2 MB) and `perf.data` (1.3 GB) are over the instance's 10 MB attachment limit. I can provide either on request.

## Workaround

With `io_batch = "off"` added under `[worker]` in the config above, 4.7.0 gives, in five runs of the same command:

| Run | p50 | p99 | req/s |
| --- | --- | --- | --- |
| 1 | 628us | 2.29ms | 195816.00 |
| 2 | 624us | 2.25ms | 196240.18 |
| 3 | 631us | 2.33ms | 195402.77 |
| 4 | 626us | 2.27ms | 196011.43 |
| 5 | 630us | 2.31ms | 195655.09 |

The median p99 is 2.29 ms and the median throughput 195816 req/s, which recovers most but not all of the 4.6.2 figures (2.115 ms, 198114 req/s). The production deployment's owners applied the setting on 2026-09-22 and report that their dashboard p99 returned to about 2.4 ms. I did not observe that.

## Analysis (a guess)

This is my reading of the commit title and the profile above. I did not read `src/io/writer.rs` closely and did not test it. The coalescer may hold a small response until the end of the event-loop tick, so under load a response waits for the next `epoll_wait` round. The report above stands without it.

Nearest tracker hit: !1482, the bisected change, which has no latency numbers. #2291 (open) reports memory growth with HTTP/2 upstreams on 4.7.0, a different symptom.

/label ~performance ~"needs triage"
