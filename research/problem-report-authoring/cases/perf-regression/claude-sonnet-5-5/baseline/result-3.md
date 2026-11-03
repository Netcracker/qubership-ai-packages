## Summary

Proxying `GET /1k` (a 1 KiB response body) through Ferrygate 4.7.0 with the default configuration gives a median p99 of 6.885 ms over ten 60-second `wrk` runs. Ferrygate 4.6.2 gives 2.115 ms on the same machine, config, and command. Median p50 is 945.5us against 610.5us, and throughput is 8.5% lower (181192 against 198114 requests/s). The ten-run ranges do not overlap. Nothing fails: every run exited 0 with no non-2xx responses and no socket errors.

The task that broke: keeping an edge proxy inside a service target of "p99 under 5 ms, measured monthly" after upgrading from 4.6.2 to 4.7.0. The operator's edge dashboard (their observation, not reproduced here) showed p99 around 7 ms at the same traffic in the week after the upgrade on 2026-09-15.

Expected: with default settings, 4.7.0 stays within the 4.6.2 p99 range of this measurement (2.06 to 2.23 ms), and in any case below 5 ms. The grounding is the behavior of 4.6.2, which is still on the supported versions page, and the 4.7.0 release notes, which describe the new write coalescing as fewer syscalls per request and mention no latency cost. The requirement is the p99 on default settings. Whether the project meets it by changing the coalescer or the default is the project's call.

Searched issues and merge requests, all states, for `latency 4.7`, `p99`, `io_batch`, `coalesce`, and `regression 4.7.0`. No issue reports this symptom. The nearest hit is !1482 (merged), the change the bisect below points at. Its description reports the syscall reduction on a 64 KiB-body benchmark and gives no latency numbers. Only the 1 KiB body at 128 connections was measured here.

## Environment

- Machine: AMD EPYC 7443P (24 cores, SMT on), 128 GiB, Ubuntu 24.04.1, kernel `6.8.0-45-generic`, CPU governor `performance`. Nothing else ran on it during the measurements.
- Ferrygate: the release tarballs `ferrygate-4.6.2-x86_64-linux-gnu.tar.gz` and `ferrygate-4.7.0-x86_64-linux-gnu.tar.gz`. Last good release 4.6.2, first bad release 4.7.0. Both are inside the supported range (4.6.x and 4.7.x).
- Load generator: `wrk` 4.2.0, over loopback.
- Upstream: `tools/bench-upstream` from the 4.7.0 tag, listening on `127.0.0.1:9000` and serving a 1 KiB body at `/1k`. The same upstream was used for both versions.
- CPU pinning with `taskset`: Ferrygate on cores 0-7, the upstream on cores 12-15, `wrk` on cores 16-23.
- Bisect builds: Rust 1.81.0, `cargo build --release`.
- Not established: later 4.7.x patch releases and the development branch were not tested.

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

For each version, on the same machine and config:

1. Start the upstream on `127.0.0.1:9000`. [TBD before filing: exact start-up command and flags of `tools/bench-upstream`.]
2. Start Ferrygate with the config above, pinned to cores 0-7.
3. Run one 30-second warm-up and discard it.
4. Run the following ten times, pinned to cores 16-23, and record the p50, the p99, and the requests/s of each run:

```bash
wrk -t4 -c128 -d60s --latency http://127.0.0.1:8080/1k
```

All runs are warm. The spread is the ten-run range in the next section.

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

Medians: 4.6.2 has p50 610.5us, p99 2.115 ms (range 2.06 to 2.23), and 198114 requests/s. 4.7.0 has p50 945.5us, p99 6.885 ms (range 6.51 to 7.40), and 181192 requests/s. The p99 is 3.3 times higher.

## Bisect

Between `v4.6.2` and `v4.7.0`, with `bench/bisect-p99.sh`, which runs the warm-up and three of the `wrk` runs above and exits 1 when the median p99 exceeds 4 ms:

```bash
git bisect start v4.7.0 v4.6.2
git bisect run bench/bisect-p99.sh
```

Output, trimmed to the first-bad line and the commit subject:

```text
3f9c2e7141d0b8a6e52c9d0f7a1e84b2c6d3f590 is the first bad commit
    io: coalesce small writes per event-loop tick (!1482)
```

The bisect took seven steps. The parent commit `a51d07c` measured a median p99 of 2.12 ms, and the first bad commit 6.91 ms.

## Profiling data

`perf record -F 999 -g -p $(pidof ferrygate) -- sleep 30` during run 4 on 4.7.0, then `perf report --no-children --percent-limit 3`, top of the output:

```text
    18.42%  ferrygate  [kernel.kallsyms]  [k] do_epoll_wait
    11.07%  ferrygate  ferrygate          [.] ferrygate::io::writer::Coalescer::flush_tick
     7.93%  ferrygate  [kernel.kallsyms]  [k] tcp_sendmsg_locked
     5.61%  ferrygate  ferrygate          [.] ferrygate::worker::loop::Tick::run
     3.12%  ferrygate  libc.so.6          [.] __memmove_avx_unaligned_erms
```

The same capture on 4.6.2 has no `Coalescer` frame. The flame graph of the 4.7.0 capture (`flame-470.svg`, 40.2 MB) and `perf.data` (1.3 GB) are over the 10 MB attachment limit of this instance, so neither is attached. Either is available on request.

## Workaround

`io_batch = "off"` under `[worker]` in the config above removes most of the regression. The 4.7.0 release notes introduce `worker.io_batch` (default `auto`), and the reference page lists `auto` and `off`. Five runs of the same command on 4.7.0 with `off`:

| Run | p50 | p99 | req/s |
| --- | --- | --- | --- |
| 1 | 628us | 2.29ms | 195816.00 |
| 2 | 624us | 2.25ms | 196240.18 |
| 3 | 631us | 2.33ms | 195402.77 |
| 4 | 626us | 2.27ms | 196011.43 |
| 5 | 630us | 2.31ms | 195655.09 |

The median p99 is 2.29 ms and the median throughput is 195816 requests/s. Both are better than the default but not back to 4.6.2: the p99 range (2.25 to 2.33) sits above the 4.6.2 range, and throughput is 1.2% lower. In production, the edge team set `io_batch = "off"` on 2026-09-22, and their dashboard p99 went back to about 2.4 ms.

## Possible cause

This is a guess from the commit title and the profile. The source was not read closely and the idea was not tested, and the report above stands without it. `Coalescer::flush_tick` appears only on 4.7.0, and the coalescer may hold a small response until the end of the event-loop tick. Under load, a response would then wait for the next `epoll_wait` round.

/label ~performance ~"needs triage"
