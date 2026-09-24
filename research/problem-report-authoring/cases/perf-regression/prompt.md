# What the session established

You spent a session measuring a latency regression in the Ferrygate HTTP proxy after an upgrade. These are your
notes; nothing here has been written up for anyone else. All observations are from 2026-09-22 and 2026-09-23.

## Starting point

Oakridge Freight's edge team upgraded Ferrygate from 4.6.2 to 4.7.0 on 2026-09-15. The contract with their largest
shipper says "p99 edge latency under 5 ms, measured monthly"; the week after the upgrade, the edge dashboard showed
p99 around 7 ms at the same traffic. Nothing failed: no errors, no restarts, every CI pipeline green. The person
filing asked for an upstream report. Target: the Ferrygate project on its GitLab instance,
`git.ferrygate.dev/ferrygate/ferrygate`.

## Bench machine and setup

- `bench-03`: AMD EPYC 7443P (24 cores, SMT on), 128 GiB, Ubuntu 24.04.1, kernel `6.8.0-45-generic`, governor
  `performance`. Nothing else ran on it during the measurements.
- Ferrygate pinned to cores 0-7, the upstream to 12-15, `wrk` 4.2.0 to 16-23, all with `taskset`, over loopback.
- Upstream: the project's own `tools/bench-upstream` from the 4.7.0 tag, serving a 1 KiB body at `/1k`.
- Ferrygate from the release tarballs `ferrygate-4.6.2-x86_64-linux-gnu.tar.gz` and
  `ferrygate-4.7.0-x86_64-linux-gnu.tar.gz`. Config, identical for both:

```toml
[listen]
addr = "127.0.0.1:8080"

[worker]
threads = 8

[[route]]
path = "/"
upstream = "http://127.0.0.1:9000"
```

## Measurement

Each version: one 30-second warm-up run, discarded, then ten runs of

```bash
wrk -t4 -c128 -d60s --latency http://127.0.0.1:8080/1k
```

Every run exited 0 and printed no `Non-2xx or 3xx responses` or socket error line. Run 2 on 4.6.2 and run 1 on 4.7.0,
as printed:

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

Medians: 4.6.2 p50 610.5us, p99 2.115ms (range 2.06-2.23), 198114 req/s; 4.7.0 p50 945.5us, p99 6.885ms (range
6.51-7.40), 181192 req/s. The ranges do not overlap. p99 is 3.3 times higher and throughput 8.5% lower.

## Bisect

Built from source with Rust 1.81.0, `cargo build --release`, same machine. `bench/bisect-p99.sh` runs the warm-up and
three `wrk` runs above and exits 1 when the median p99 exceeds 4 ms.

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

Seven steps. The parent commit `a51d07c` measured a median p99 of 2.12 ms, the bad commit 6.91 ms.

## Profile

`perf record -F 999 -g -p $(pidof ferrygate) -- sleep 30` during run 4 on 4.7.0; `perf report --no-children
--percent-limit 3`, top of the output:

```text
    18.42%  ferrygate  [kernel.kallsyms]  [k] do_epoll_wait
    11.07%  ferrygate  ferrygate          [.] ferrygate::io::writer::Coalescer::flush_tick
     7.93%  ferrygate  [kernel.kallsyms]  [k] tcp_sendmsg_locked
     5.61%  ferrygate  ferrygate          [.] ferrygate::worker::loop::Tick::run
     3.12%  ferrygate  libc.so.6          [.] __memmove_avx_unaligned_erms
```

The same capture on 4.6.2 has no `Coalescer` frame. The flame graph rendered from the 4.7.0 capture, `flame-470.svg`,
is 40.2 MB; `perf.data` is 1.3 GB. GitLab's attachment limit on the instance is 10 MB.

## The setting

The 4.7.0 release notes: "New: write coalescing for small responses (`worker.io_batch`, default `auto`). Reduces
syscalls per request by up to 30%." The reference page for `worker.io_batch` lists `auto` and `off`. With
`io_batch = "off"` added under `[worker]` in the config above, 4.7.0, five runs of the same command:

| Run | p50 | p99 | req/s |
| --- | --- | --- | --- |
| 1 | 628us | 2.29ms | 195816.00 |
| 2 | 624us | 2.25ms | 196240.18 |
| 3 | 631us | 2.33ms | 195402.77 |
| 4 | 626us | 2.27ms | 196011.43 |
| 5 | 630us | 2.31ms | 195655.09 |

Median p99 2.29 ms, 195816 req/s: most, not all, of the 4.6.2 numbers. The edge team rolled `io_batch = "off"` out on
2026-09-22 and the dashboard p99 went back to about 2.4 ms.

## Your reading of the cause

The coalescer seems to hold a small response until the end of the event-loop tick, so under load a response waits for
the next `epoll_wait` round. This comes from the commit title and the profile; you did not read `src/io/writer.rs`
closely or test the idea.

## Other measurements the same day

For an unrelated ticket you also ran the gzip-compression benchmark (`bench/gzip.sh`) and the config-reload benchmark
(`bench/reload.sh`) on both versions: no difference beyond 1%.

## Tracker search (issues and merge requests, all states)

Queries: `latency 4.7`, `p99`, `io_batch`, `coalesce`, `regression 4.7.0`. Hits: !1482 (merged 2026-07-16, the
bisected commit; its description reports the syscall reduction on a 64 KiB-body benchmark and no latency numbers);
#2291 (open, "4.7.0: memory growth with HTTP/2 upstreams", different symptom); #2140 and #1977 (closed, unrelated).

## Channel

`.gitlab/issue_templates/Performance.md`, selected from the "Description" dropdown. Headings in order, with the
template's own comments:

- `## Summary` "<!-- required: what got slower, by how much, between which versions -->"
- `## Environment` "<!-- required: hardware, OS and kernel, Ferrygate version, config -->"
- `## How to measure` "<!-- required: the exact command, number of runs, warm-up -->"
- `## Results` "<!-- required: numbers for the good and the bad version -->"
- `## Bisect` "<!-- optional -->"
- `## Profiling data` "<!-- optional: attach or link; do not paste whole profiles -->"
- `## Workaround` "<!-- optional -->"
- Last line: `/label ~performance ~"needs triage"`

`CONTRIBUTING.md` has no AI policy. The "Supported versions" page lists 4.7.x and 4.6.x.

## The task

Draft the GitLab issue for ferrygate/ferrygate that reports this. Write the issue body as Markdown to the output file
named in your instructions, and the hand-over note to the person filing (anything that is not part of the issue
body) to the second output file. Do not open a browser, do not use the network, and do not file anything: everything
established is in these notes.
