## Summary

With the default configuration, Ferrygate 4.7.0 reports a median p99 of 6.885 ms for 1 KiB proxied responses. Ferrygate 4.6.2 reports 2.115 ms with the same machine, config, and `wrk` command. Median throughput is 8.5% lower (181192 against 198114 req/s). Both medians are over ten runs, and the p99 ranges do not overlap (4.6.2: 2.06 to 2.23 ms, 4.7.0: 6.51 to 7.40 ms). No run had errors.

We run Ferrygate at our edge under a contractual p99 target below 5 ms. After we upgraded from 4.6.2 to 4.7.0 on 2026-09-15, our edge dashboard showed p99 around 7 ms at the same traffic. That reading comes from our edge team's dashboard, and I have no transcript of it. The benchmark below is how I reproduced the change.

**Expected:** on this benchmark, 4.7.0 with the default `worker.io_batch` reports a p99 close to the 4.6.2 value of about 2.1 ms. The same 4.7.0 build with `io_batch = "off"` reports 2.29 ms (see Workaround), which I would accept. The exact bound is the project's to choose. The expectation rests on 4.6.2, a supported release, and on the 4.7.0 release notes, which announce "write coalescing for small responses (`worker.io_batch`, default `auto`). Reduces syscalls per request by up to 30%." and mention no latency cost. The reference page for `worker.io_batch` lists the values `auto` and `off`.

**Versions:** last good 4.6.2, first bad 4.7.0 (both release tarballs). The bisect points at 3f9c2e7141d0 (!1482). I did not test later 4.7.x patch releases or the development branch, so I do not know whether they are affected.

**Nearest existing item:** !1482, the merge request of the bisected commit. Its description reports a syscall reduction on a 64 KiB-body benchmark and gives no latency numbers.

## Environment

- Hardware: AMD EPYC 7443P (24 cores, SMT on), 128 GiB, CPU governor `performance`. Nothing else ran on the machine during the measurements.
- OS: Ubuntu 24.04.1, kernel `6.8.0-45-generic`.
- Ferrygate: `ferrygate-4.6.2-x86_64-linux-gnu.tar.gz` and `ferrygate-4.7.0-x86_64-linux-gnu.tar.gz` from the release tarballs. The bisect used builds from source with Rust 1.81.0 and `cargo build --release`.
- Load generator: `wrk` 4.2.0.
- Upstream: `tools/bench-upstream` from the 4.7.0 tag, serving a 1 KiB body at `/1k`.
- Pinning with `taskset`: Ferrygate on cores 0-7, the upstream on cores 12-15, `wrk` on cores 16-23. All traffic runs over loopback.
- Date of the measurements: 2026-09-22 and 2026-09-23.

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

For each version, I ran one 30-second warm-up run (discarded), then ten runs of:

```bash
wrk -t4 -c128 -d60s --latency http://127.0.0.1:8080/1k
```

Every run exited 0 and printed no `Non-2xx or 3xx responses` line and no socket error line.

<TBD: paste the `taskset` command lines that start Ferrygate and `tools/bench-upstream`>

## Results

All ten runs on each version, as printed by `wrk`:

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

Medians: 4.6.2 has p50 610.5us, p99 2.115ms, and 198114 req/s. 4.7.0 has p50 945.5us, p99 6.885ms, and 181192 req/s. The 4.7.0 p99 is 3.3 times higher.

Run 2 on 4.6.2, in full:

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

Run 1 on 4.7.0, in full:

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

I built from source (Rust 1.81.0, `cargo build --release`) on the same machine. `bench/bisect-p99.sh` runs the warm-up and three `wrk` runs of the command above, and exits 1 when the median p99 exceeds 4 ms.

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

The bisect took seven steps. The parent commit `a51d07c` measured a median p99 of 2.12 ms, and the bad commit measured 6.91 ms. Only Ferrygate, the project's own `tools/bench-upstream`, and `wrk` take part in the measurement.

## Profiling data

`perf record -F 999 -g -p $(pidof ferrygate) -- sleep 30` during run 4 on 4.7.0, then `perf report --no-children --percent-limit 3` (top of the output):

```text
    18.42%  ferrygate  [kernel.kallsyms]  [k] do_epoll_wait
    11.07%  ferrygate  ferrygate          [.] ferrygate::io::writer::Coalescer::flush_tick
     7.93%  ferrygate  [kernel.kallsyms]  [k] tcp_sendmsg_locked
     5.61%  ferrygate  ferrygate          [.] ferrygate::worker::loop::Tick::run
     3.12%  ferrygate  libc.so.6          [.] __memmove_avx_unaligned_erms
```

The same capture on 4.6.2 has no `Coalescer` frame. The flame graph of the 4.7.0 capture (`flame-470.svg`, 40.2 MB) and `perf.data` (1.3 GB) are over this instance's 10 MB attachment limit, so I have not attached them. I can provide them on request.

## Workaround

Adding `io_batch = "off"` under `[worker]` in the config above restores most of the 4.6.2 numbers on 4.7.0. Five runs of the same `wrk` command gave:

| Run | p50 | p99 | req/s |
| --- | --- | --- | --- |
| 1 | 628us | 2.29ms | 195816.00 |
| 2 | 624us | 2.25ms | 196240.18 |
| 3 | 631us | 2.33ms | 195402.77 |
| 4 | 626us | 2.27ms | 196011.43 |
| 5 | 630us | 2.31ms | 195655.09 |

The median p99 is 2.29 ms, about 8% above 4.6.2, and the median throughput is 195816 req/s, 1.2% below 4.6.2. The setting does not remove the whole difference. Our edge team set `io_batch = "off"` in production on 2026-09-22, and their dashboard p99 went back to about 2.4 ms.

## Possible cause (inferred, not tested)

I did not read `src/io/writer.rs` closely and did not test this idea, so treat it as a guess. Everything above stands without it. From the commit title and the profile, the coalescer may delay small responses until the end of the event-loop tick. Under load, each response would then wait for the next `epoll_wait` round.

/label ~performance ~"needs triage"
