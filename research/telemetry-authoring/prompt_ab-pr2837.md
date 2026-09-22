# Review this change

`change.diff` is a proposed change to the PostgreSQL JDBC driver, a **library** that ships to applications
the driver authors never see. `src/` holds the two files it touches, at their current state before the change.

Context the author gave for the change:

> AdaptiveFetch dynamically changes the fetch size based on the largest row seen so far, to fit in
> maxResultBufferSize. However it does not work in all cases and I am debugging one:
> `Result set exceeded maxResultBuffer limit. Received: 103887670; Current limit: 103887667`.
> I believe the adaptive fetch gets over-confident and sets too high a fetch size. To confirm, I went to
> turn on debug logs for the values adaptive fetch computes, and discovered there are none.
> I expect I will need to set `adaptiveFetchMaximum` to some sane value.

The driver uses `java.util.logging`. The connection properties a user sets are `adaptiveFetch`,
`adaptiveFetchMinimum`, `adaptiveFetchMaximum`, `maxResultBuffer`, and `defaultRowFetchSize`.
Elsewhere in the driver, `QueryExecutorImpl` already logs at FINEST:
`"  simple execute, handler={0}, maxRows={1}, fetchSize={2}, flags={3}"`.

Write your review to `review.md`. Be specific and concrete: name defects, say what a reader would get wrong,
and say what to change. Do not edit any source file.
