`pgsync` is a Go command-line tool that copies tables between two PostgreSQL databases. Its flag `--jobs` sets how many
tables it copies in parallel and takes a positive integer; the default is `4`. The flag is parsed in `main` before
anything connects:

```go
jobs := flag.Int("jobs", 4, "number of tables to copy in parallel")
flag.Parse()
if *jobs < 1 {
	fmt.Fprintf(os.Stderr, "<message>\n", *jobs)
	os.Exit(2)
}
```

The `%d` verb in the message receives `*jobs`.

Write the format string that replaces `<message>` for this check. Give the format string only, as it would appear
between the quotes in the Go source.
