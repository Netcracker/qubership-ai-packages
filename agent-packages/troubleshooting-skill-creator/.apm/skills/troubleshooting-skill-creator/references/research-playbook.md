# Research playbook

How to find out how a technology actually fails, and how to turn that into a case someone can act on.

This is the hardest phase of the skill and the one that decides whether the reference is worth reading. The trap is
easy to fall into and hard to see afterward: an agent that already knows a technology can produce fifty plausible cases
without opening a browser, and they will read fine, cite nothing, and match no real incident. Plausible is the enemy
here. Everything below exists to keep cases anchored to failures that happened to someone.

## The two-stage method

Symptom and mechanism live in different places, and a case needs both.

**Stage 1 — harvest real symptoms from where operators complain.** Stack Overflow, GitHub issues, Reddit, vendor
forums, mailing lists. These give you what people actually paste: the verbatim log line, the wording they reach for
(`pods keep restarting`, `UI just spins`), and how often a failure comes up. They are terrible sources for fixes —
answers are dated, environment-specific, and confidently wrong roughly as often as they are right.

**Stage 2 — ground the mechanism in the official documentation.** Take the symptom to the vendor's troubleshooting
guide, configuration reference, or the upstream issue the thread points at. This is where you learn why it happens and
what actually fixes it.

Every externally researched case has a required `Sources` block containing both parts. The community thread establishes
that someone reported the failure and supplies the symptom wording; the authoritative source supports the cause and
the fix. A case with only a forum link is folklore. A case with only a documentation link usually means Stage 1 was
skipped and the symptom may not match what an operator reports.

When Stage 2 turns up nothing, that is a finding rather than a license to guess. Do not present the cause or fix as
confirmed. Keep the available source for the build-time audit and report the unsupported claim in chat; do not add a
rating or verification marker to the generated troubleshooting reference.

## Where to look, in the order that pays

Search per technology from the Phase 1 inventory, and separately per install step — installation failures cluster
differently from runtime ones and the same search terms will not find both.

**For symptoms:**

- **GitHub issues on the upstream project** — the highest-yield source. Search the issue tracker for the error string,
  and sort by reactions to find the failures that hit many people. Closed issues carry the fix; open ones tell you a
  workaround is the best available answer.
- **Stack Overflow** — search the exact error string in quotes, then the symptom in plain words. Read the question for
  the symptom, and the accepted answer only as a lead for Stage 2.
- **Reddit** (`r/kubernetes`, `r/devops`, and the technology's own subreddit) — weaker on fixes, unusually good on
  symptom phrasing and on which failures are common enough to be a running joke.
- **Vendor community forums and mailing lists** — where the operators of one specific product congregate.
- **The upstream project's own troubleshooting or FAQ page** — often written from support tickets, so it carries both
  halves at once.

**For mechanism and fix:**

- The vendor's troubleshooting guide, then its configuration reference, then its operations guide.
- The upstream issue or commit the community thread points at.
- The project's release notes when the fix is "upgrade past this version".

**Useful search shapes.** Pair the technology with the failure vocabulary rather than with the word `troubleshooting`:
`<technology> <verbatim error string>`, `<technology> <symptom> site:stackoverflow.com`,
`<technology> pods crashloopbackoff`, `<technology> connection refused after upgrade`, `<technology> install fails
<step name>`, `<technology> "known issues"`. Search the version the repository pins when the failure smells
version-specific.

## What makes a case worth including

Include a failure when all of these hold:

- **It can happen here.** The component ships in this repository, in this configuration. A Cassandra authentication
  failure belongs in a reference for a product that stores traces in Cassandra, and nowhere else.
- **Someone hit it.** It comes from repository material, an issue, a thread, or a vendor page documenting a real
  failure — not from reasoning about what could theoretically go wrong.
- **The symptom is quotable.** You have the log line, the error string, or an honest prose description of what the
  operator sees. Copy it exactly, from the thread or from real output.
- **The fix is grounded.** An official page, an upstream issue, or repository material backs it. If the best available
  answer is a workaround, say so in the case.

Drop a failure when the fix is "configure it correctly" with nothing specific behind it, when it only reproduces in a
configuration this repository cannot produce, or when you cannot cite where it came from.

## Depth over breadth

Cover the components this deployment leans on properly rather than giving every dependency one shallow case. The
storage backend and the install path are where operators actually get stuck; a linting library in the build chain is
not going to page anyone at night.

Stop when the components in the inventory have their common failures covered and new searches keep returning failures
you have already written up. That saturation point is the signal, not a case count.

## Recording sources as you go

Capture the URL and the page title the moment you use a source. Reconstructing citations afterward is slow, and the
citations that go missing are the ones for the cases you were least sure about — precisely the ones a reviewer needs
to check.

Link by name, per the format contract: `[Cluster health — OpenSearch Documentation](https://example.com)`. Prefer
versioned documentation URLs when the vendor publishes them, since `latest` drifts out from under the case.
