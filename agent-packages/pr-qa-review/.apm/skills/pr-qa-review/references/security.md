# Security

## Review scope

Trace changed trust boundaries and data flows from untrusted input to privileged operations, storage, rendering, logs,
and outbound requests. Check the following concerns when the diff can affect them:

- secrets in source, configuration, rendered descriptors, generated assets, logs, reports, screenshots, and examples;
- authentication and authorization at every entry point and object or tenant boundary;
- command, query, template, header, and structured-data injection;
- cross-site scripting in rendered user-controlled or external content;
- unsafe downloads, content disposition and type handling, and executable or active content;
- server-side request forgery-like behavior, redirect handling, and access to internal or metadata endpoints;
- path traversal, archive extraction, symbolic links, and unsafe file-name handling;
- unbounded work from request size, ranges, fan-out, retries, recursion, concurrency, or allocation;
- dependency and image changes, provenance, known repository policy, and unexpected runtime contents;
- deployment privileges, including Kubernetes identities, RBAC, capabilities, host access, and secret mounts when used;
- transport security, certificate and hostname validation, protocol downgrade, and plaintext fallback; and
- sensitive logging, including credentials, tokens, personal data, request bodies, and internal topology.

Use safe representative inputs on shared environments. Injection payloads, large requests, broad scans, or requests
that could reach internal systems require an isolated environment or explicit permission when they may be disruptive.

## Scanner coverage

Search for repository-native dependency, secret, license, source, image, and deployment-manifest scanners before
selecting an implementation. Run applicable native checks when feasible, or use another available implementation of
the required capability. A particular scanner is never a hard dependency.

Report unavailable or failed scanner coverage separately from the manual security review. Missing scanner evidence
limits the claims that depend on its database or analysis; it does not erase manual findings or make the security track
not applicable.
