## Summary

After we upgraded Ferrygate from 4.6.2 to 4.7.0 with an unchanged config, p99 latency for a proxied 1 KiB response rose from 2.12 ms to 6.89 ms. Each figure is the median of ten 60-second `wrk` runs, and the two ranges do not overlap. Over the same runs, p50 rose from 611 µs to 946 µs and throughput fell 8.5%, from 198114 to 181192 req/s. Every run returned only 2xx responses and no socket errors.

We first saw this in production. In the week after the upgrade on September 15, 2026, our edge dashboard showed p99 at about 7 ms with unchanged traffic.

Bisecting between v4.6.2 and v4.7.0 stops at 3f9c2e71 ("io: coalesce small writes per event-loop tick", !1482). On 4.7.0, `io_batch = "off"` under `[worker]` brings the median p99 back to 2.29 ms (see Workaround).

Expected: with its default config, 4.7.0 keeps p99 on this benchmark within the range 4.6.2 shows (2.06–2.23 ms over ten runs). The parent commit a51d07c measured 2.12 ms. Both 4.6.x and 4.7.x are on the supported-versions page, and the 4.7.0 release notes describe the change only as "Reduces syscalls per request by up to 30%." How to get there is yours to choose: a change to the coalescer for small responses, a different default for `worker.io_batch`, or something else. If higher tail latency is the intended cost of fewer syscalls, neither the release notes nor the `worker.io_batch` reference page says so.

## Environment

- CPU: AMD EPYC 7443P (24 cores, SMT on), 128 GiB RAM, CPU governor `performance`. Nothing else ran on the machine during the measurements.
- OS: Ubuntu 24.04.1, kernel `6.8.0-45-generic`.
- Ferrygate: release tarballs `ferrygate-4.6.2-x86_64-linux-gnu.tar.gz` and `ferrygate-4.7.0-x86_64-linux-gnu.tar.gz`. Bisect builds: Rust 1.81.0, `cargo build --release`.
- Not tested on any build newer than 4.7.0 (a later 4.7.x or `main`).
- Upstream: the project's `tools/bench-upstream` from the v4.7.0 tag, serving a 1 KiB body at `/1k`, used for both versions.
- Load generator: `wrk` 4.2.0.
- Everything over loopback, pinned with `taskset`: Ferrygate to cores 0–7, the upstream to 12–15, `wrk` to 16–23.

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

Per version: one 30-second warm-up run with the same command, discarded, then ten runs of:

```bash
wrk -t4 -c128 -d60s --latency http://127.0.0.1:8080/1k
```

Measured on September 22 and 23, 2026.

## Results

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

Medians: 4.6.2 p50 610.5 µs, p99 2.115 ms (range 2.06–2.23 ms), 198114 req/s. 4.7.0 p50 945.5 µs, p99 6.885 ms (range 6.51–7.40 ms), 181192 req/s.

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

Each step built Ferrygate from source and ran a script that does the warm-up and three of the `wrk` runs above, and exits 1 when the median p99 exceeds 4 ms (`bench/bisect-p99.sh` in our checkout).

```bash
git bisect start v4.7.0 v4.6.2
git bisect run bench/bisect-p99.sh
```

After seven steps:

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

The parent commit a51d07c measured a median p99 of 2.12 ms, and 3f9c2e71 measured 6.91 ms.

The description of !1482 reports the syscall reduction on a 64 KiB-body benchmark and gives no latency numbers. The only open 4.7.0 regression we found, #2291, is memory growth with HTTP/2 upstreams, which is a different symptom.

## Profiling data

Captured on 4.7.0 during run 4. The listing is the top of the report, cut at 3% by `--percent-limit`:

```bash
perf record -F 999 -g -p $(pidof ferrygate) -- sleep 30
perf report --no-children --percent-limit 3
```

```text
    18.42%  ferrygate  [kernel.kallsyms]  [k] do_epoll_wait
    11.07%  ferrygate  ferrygate          [.] ferrygate::io::writer::Coalescer::flush_tick
     7.93%  ferrygate  [kernel.kallsyms]  [k] tcp_sendmsg_locked
     5.61%  ferrygate  ferrygate          [.] ferrygate::worker::loop::Tick::run
     3.12%  ferrygate  libc.so.6          [.] __memmove_avx_unaligned_erms
```

The same capture on 4.6.2 has no `Coalescer` frame. The flame graph from the 4.7.0 capture (40.2 MB) and the `perf.data` file (1.3 GB) exceed the 10 MB attachment limit. We can share either on request.

## Workaround

On 4.7.0, add `io_batch = "off"` under `[worker]` in the config above. Same command, five runs:

| Run | p50 | p99 | req/s |
| --- | --- | --- | --- |
| 1 | 628us | 2.29ms | 195816.00 |
| 2 | 624us | 2.25ms | 196240.18 |
| 3 | 631us | 2.33ms | 195402.77 |
| 4 | 626us | 2.27ms | 196011.43 |
| 5 | 630us | 2.31ms | 195655.09 |

The median p99 is 2.29 ms and the median throughput 195816 req/s. That recovers most of the gap, but the p99 range (2.25–2.33 ms) still sits just above the 4.6.2 range (2.06–2.23 ms). We rolled the setting out to production on September 22, 2026, and the edge dashboard p99 went back to about 2.4 ms.

## Possible cause (untested)

This section is a guess from the commit title and the profile above. We did not read `src/io/writer.rs` closely or test the idea, and the sections above stand without it. The coalescer appears to hold a small response until the end of the event-loop tick, so under load a response waits for the next `epoll_wait` round.

/label ~performance ~"needs triage"
