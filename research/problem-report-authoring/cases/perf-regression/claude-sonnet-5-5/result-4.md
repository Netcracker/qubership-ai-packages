## Summary

With the default configuration, `wrk -t4 -c128 -d60s --latency http://127.0.0.1:8080/1k` against Ferrygate 4.7.0 gives a median p99 of 6.885 ms over ten runs. The same command against 4.6.2 gives 2.115 ms, so p99 is 3.3 times higher. Median throughput is 8.5% lower (181192 against 198114 requests per second). No run returned an error: every `wrk` run exited 0 and printed no `Non-2xx or 3xx responses` or socket error line.

A production edge deployment saw the same change after upgrading from 4.6.2 to 4.7.0 on 2026-09-15: its dashboard showed a p99 of about 7 ms at unchanged traffic, against a p99 target of 5 ms. That observation comes from the team running it, and I did not reproduce it.

Expected: with default settings, 4.7.x gives a p99 on this benchmark close to 4.6.2's (2.06 to 2.23 ms over ten runs). Nothing in the 4.7.0 release notes or the reference page for `worker.io_batch` mentions a latency cost, so this rests on 4.6.2's behavior. The exact bound is the maintainers' to set, as is how to reach it. If the latency cost is intended, I expect the release notes and the `worker.io_batch` reference page to say so.

The nearest tracker hit is #2291 (open, memory growth with HTTP/2 upstreams), which reports a different symptom; the upstream here is plain `http://`. The change the bisect below points at is !1482.

I tested 4.6.2 and 4.7.0 only, both from the release tarballs, not a later patch release or the development branch.

## Environment

- Ferrygate 4.6.2 and 4.7.0, from `ferrygate-4.6.2-x86_64-linux-gnu.tar.gz` and `ferrygate-4.7.0-x86_64-linux-gnu.tar.gz`
- AMD EPYC 7443P (24 cores, SMT on), 128 GiB, Ubuntu 24.04.1, kernel `6.8.0-45-generic`, CPU governor `performance`; nothing else ran on the machine during the measurements
- `wrk` 4.2.0; upstream is `tools/bench-upstream` from the 4.7.0 tag, serving a 1 KiB body at `/1k`
- Everything over loopback, pinned with `taskset`: Ferrygate to cores 0-7, the upstream to 12-15, `wrk` to 16-23
- For the bisect only: built from source with Rust 1.81.0, `cargo build --release`
- Observations made on 2026-09-22 and 2026-09-23

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

For each version, one 30-second warm-up run (discarded), then ten runs of:

```bash
wrk -t4 -c128 -d60s --latency http://127.0.0.1:8080/1k
```

The launch lines for Ferrygate and `tools/bench-upstream` are not part of this report. Both ran under `taskset` on the cores listed above, with the config shown.

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

Medians: 4.6.2 has p50 610.5us, p99 2.115ms (range 2.06 to 2.23) and 198114 req/s. 4.7.0 has p50 945.5us, p99 6.885ms (range 6.51 to 7.40) and 181192 req/s. The p99 ranges do not overlap.

## Bisect

`git bisect start v4.7.0 v4.6.2`, then `git bisect run bench/bisect-p99.sh`. The script runs the warm-up and three of the `wrk` runs above, and exits 1 when the median p99 exceeds 4 ms. The 4 ms threshold only separates the two clusters of results; it is not a requirement.

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

The bisect took seven steps. The parent commit `a51d07c` measured a median p99 of 2.12 ms and the bad commit 6.91 ms. The description of !1482 reports a syscall reduction on a 64 KiB-body benchmark and gives no latency numbers; the benchmark here uses a 1 KiB body.

## Profiling data

`perf record -F 999 -g -p $(pidof ferrygate) -- sleep 30` during run 4 on 4.7.0, then `perf report --no-children --percent-limit 3`, top of the output:

```text
    18.42%  ferrygate  [kernel.kallsyms]  [k] do_epoll_wait
    11.07%  ferrygate  ferrygate          [.] ferrygate::io::writer::Coalescer::flush_tick
     7.93%  ferrygate  [kernel.kallsyms]  [k] tcp_sendmsg_locked
     5.61%  ferrygate  ferrygate          [.] ferrygate::worker::loop::Tick::run
     3.12%  ferrygate  libc.so.6          [.] __memmove_avx_unaligned_erms
```

The same capture on 4.6.2 has no `Coalescer` frame. The flame graph from the 4.7.0 capture (`flame-470.svg`, 40.2 MB) and the raw `perf.data` (1.3 GB) are over this instance's 10 MB attachment limit, so neither is attached. I can provide either on request.

## Workaround

The 4.7.0 release notes describe `worker.io_batch` (default `auto`, other value `off`) as write coalescing for small responses. With `io_batch = "off"` added under `[worker]` in the config above, 4.7.0 gave, over five runs of the same command, a median p99 of 2.29 ms (range 2.25 to 2.33) and a median of 195816 req/s. That is most of the way back to 4.6.2, but p99 is still slightly above 4.6.2's range, and I did not look into the remaining difference. The team running the production deployment set `io_batch = "off"` on 2026-09-22, and its dashboard p99 went back to about 2.4 ms.

## Possible cause (unverified)

This is a guess from the commit title and the profile. I did not read `src/io/writer.rs` closely or test it. The coalescer may hold a small response until the end of the event-loop tick, so that under load a response waits for the next `epoll_wait` round. Everything above stands without it.

/label ~performance ~"needs triage"
