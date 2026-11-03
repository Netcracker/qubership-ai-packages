## Summary

After upgrading Ferrygate from 4.6.2 to 4.7.0 with an unchanged config, the p99 latency of a 1 KiB proxied response at 128 connections rose from a median of 2.115 ms to 6.885 ms over ten 60-second `wrk` runs. Throughput fell by 8.5%. Nothing failed: no errors, no restarts. We run Ferrygate as an edge proxy under a customer contract that requires p99 under 5 ms, and our production dashboard showed p99 at about 7 ms after the upgrade.

Expected: with the default config, 4.7.0 keeps p99 on this benchmark near the 4.6.2 result (2.06–2.23 ms over ten runs) and below 5 ms. This rests on 4.6.2, a supported release, giving that result with the identical config. The 4.7.0 release notes describe the new write coalescing as reducing syscalls per request by up to 30% and mention no latency cost. Whether `auto` should decide differently or the default should change is the project's call.

The 4.7.0 result and the 4.6.2 result below are the same command, config, and machine. Bisect points at !1482 (see Bisect). The closest existing items are !1482 itself, whose description reports the syscall reduction on a 64 KiB-body benchmark and no latency numbers, and #2291 (open, memory growth with HTTP/2 upstreams), which is a different symptom.

## Environment

- Ferrygate 4.6.2 and 4.7.0, from the release tarballs `ferrygate-4.6.2-x86_64-linux-gnu.tar.gz` and `ferrygate-4.7.0-x86_64-linux-gnu.tar.gz`. Both are in the supported-versions list (4.7.x and 4.6.x). Not established: whether a 4.7.x release later than 4.7.0, or the development branch, behaves the same.
- Hardware: AMD EPYC 7443P (24 cores, SMT on), 128 GiB. OS: Ubuntu 24.04.1, kernel `6.8.0-45-generic`, CPU governor `performance`. Nothing else ran on the machine during the measurements.
- Load generator: `wrk` 4.2.0. Upstream: `tools/bench-upstream` from the 4.7.0 tag, used for both versions, serving a 1 KiB body at `/1k`.
- Core pinning with `taskset`: Ferrygate on cores 0–7, the upstream on 12–15, `wrk` on 16–23. All traffic goes over loopback.
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

I left out the customer's name and our production host names. Nothing else was changed.

## How to measure

For each version: one 30-second warm-up run, discarded, then ten runs of

```bash
wrk -t4 -c128 -d60s --latency http://127.0.0.1:8080/1k
```

Every run exited 0 and printed no `Non-2xx or 3xx responses` line and no socket error line.

## Results

Run 2 on 4.6.2, as printed:

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

Medians: 4.6.2 has p50 610.5us, p99 2.115 ms (range 2.06–2.23), and 198114 req/s. 4.7.0 has p50 945.5us, p99 6.885 ms (range 6.51–7.40), and 181192 req/s. The p99 ranges do not overlap.

In production, the edge dashboard showed p99 at about 7 ms in the week after the 2026-09-15 upgrade, at the same traffic as before. This is the edge team's dashboard, not something I measured on the bench.

## Bisect

`git bisect` between `v4.6.2` and `v4.7.0`, with a script that runs the warm-up and three of the `wrk` runs above and exits 1 when the median p99 exceeds 4 ms:

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

It took seven steps. The parent commit `a51d07c` measured a median p99 of 2.12 ms, and the first bad commit measured 6.91 ms.

## Profiling data

`perf record -F 999 -g -p $(pidof ferrygate) -- sleep 30` during run 4 on 4.7.0, then `perf report --no-children --percent-limit 3`. This is the top of the output; the command is unchanged, so the full report can be regenerated:

```text
    18.42%  ferrygate  [kernel.kallsyms]  [k] do_epoll_wait
    11.07%  ferrygate  ferrygate          [.] ferrygate::io::writer::Coalescer::flush_tick
     7.93%  ferrygate  [kernel.kallsyms]  [k] tcp_sendmsg_locked
     5.61%  ferrygate  ferrygate          [.] ferrygate::worker::loop::Tick::run
     3.12%  ferrygate  libc.so.6          [.] __memmove_avx_unaligned_erms
```

The same capture on 4.6.2 has no `Coalescer` frame. The flame graph from the 4.7.0 capture (`flame-470.svg`, 40.2 MB) and `perf.data` (1.3 GB) are over the instance's 10 MB attachment limit, so they are not attached. I can provide either on request.

## Workaround

4.7.0 with `io_batch = "off"` added under `[worker]` in the config above brings p99 back close to 4.6.2. Five runs of the same command:

| Run | p50 | p99 | req/s |
| --- | --- | --- | --- |
| 1 | 628us | 2.29ms | 195816.00 |
| 2 | 624us | 2.25ms | 196240.18 |
| 3 | 631us | 2.33ms | 195402.77 |
| 4 | 626us | 2.27ms | 196011.43 |
| 5 | 630us | 2.31ms | 195655.09 |

The median p99 is 2.29 ms and the median throughput is 195816 req/s, against 2.115 ms and 198114 req/s on 4.6.2. Our edge team set `io_batch = "off"` in production on 2026-09-22, and the dashboard p99 returned to about 2.4 ms.

## Cause (unconfirmed)

This is a guess from the title of !1482 and the profile. I have not read `src/io/writer.rs` closely and did not test it. The coalescer may hold a small response until the end of the event-loop tick, so under load a response waits for the next `epoll_wait` round. Everything above stands without it.

/label ~performance ~"needs triage"
