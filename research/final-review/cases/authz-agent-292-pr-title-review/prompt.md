The skills for this task are under <skills>: `final-review/SKILL.md`, `test-authoring/SKILL.md`,
`english-developer-style/SKILL.md`, and `apm-authoring/SKILL.md`. Read `<skills>/final-review/SKILL.md` in full and
follow it; where it says to load another skill, load the copy under <skills>, and do not load any other copy of these
four.

You are the fresh reviewer that final-review asks for. Review the change `<base>..HEAD` of this repository, one
commit. There is no separate task statement: take the claimed cases from the commit message (`git log <base>..HEAD`),
and say so in the report as the skill asks. Its drift script is at `<skills>/final-review/scripts/comment-drift.py`.

The change goes into an open pull request. The caller hands over the commit its diff starts from, `cd2f261df256068d30736f348fd61ef53193a522`, its title as it stands:

> docs(adr): define which responses ADR-0091 R39 counts as an answer, and add TOKEN_REALM_UNKNOWN

and its description as it stands:

> #289 asked which 404s ADR-0091 R39 counts as an answer, and which reason ADR-0092 R8 gives. The redesign of the trusted providers, which the architect approved on 2026-11-23, answers the first question with a reason code of its own, and removes R8 together with file tokens, so ADR-0092 R8 stays as `main` has it.
>
> On `main`, a 404 for a realm with no keys loaded counts as an answer, so the tokens of that realm get `TOKEN_KID_UNKNOWN`, and the audit and the metric of a refusal report a deleted tenant as a token with an invented `kid`. The code of one case is spread over R23, R38, and R39. R38 does not say what a token gets when its request is canceled while it waits for a load, and it gives `TOKEN_KEYS_UNAVAILABLE` after a wait that ran out even when a load stored an answer during the wait.
>
> This change names what a load stores with two terms, **Result** (an answer, a missing realm, or a failure) and **Last result**, and gives each step one rule:
>
> - R39 decides which result a load ends with: an answer for a JWKS that neither R79 nor R80 refuses; a missing realm when a request of the load got a 404, the source is a realm, and the realm has no keys loaded; a failure in every other case, such as a 404 for a provider or for a realm with keys loaded. The agent does not read the body of a 404.
> - R23 maps a result to a code in one table: an answer gives `TOKEN_KID_UNKNOWN`, a missing realm the new code `TOKEN_REALM_UNKNOWN` (401), and a failure or no result `TOKEN_KEYS_UNAVAILABLE` (503).
> - R38 decides which result a token counts: the last result of its source. A token that started or joined an on-demand load counts only a result stored after that load started, and has no result when none is stored by the time it is checked; a token whose wait runs out, or whose request is canceled or reaches its deadline, is checked at that moment. A token whose on-demand load R33 refused has no result, as on `main`.
> - R79 loads usable entries under one `kid` as one key only when they share key material and `alg`, and refuses the response for any other pair, so the order of the entries never decides which `alg` passes. A13 rejects loading the rest of such a JWKS.
> - R80 refuses a response of any status but 404 whose body is longer than 1 MiB (1048576 bytes) after the gzip coding that the agent requests is removed.
> - R81 logs one warning for a load of a source that is not required whose result is not an answer, with the source, the result, and the address and status of the request that decided it.
>
> A 404 for a realm in `keycloak.requiredRealms` counts like a 404 for any other realm with no keys loaded, as on `main`, and R14, R17, and R19 keep the agent not ready and name the realm until it has a usable key. A14 rejects counting that 404 as a failure. A15 rejects counting only a 404 of the discovery document, so that R39 reads the same once a load is one request to a configured JWKS address, and reverses the answer of 2026-11-16 on which 404 counts. ADR-0095 R16 lists the three codes under ADR-0091 R23, and ADR-0092 R2, ADR-0093 R3, and ADR-0095 A2 cite R23 for the code.
>
> **User-visible changes.**
>
> - A token whose realm got a 404 for its last load while the agent held no keys of that realm is refused with 401 and `TOKEN_REALM_UNKNOWN` instead of `TOKEN_KID_UNKNOWN`.
> - A token whose wait for a load runs out gets the result that a load stored during the wait, so an answer stored meanwhile gives `TOKEN_KID_UNKNOWN` rather than `TOKEN_KEYS_UNAVAILABLE`.
> - A token whose request is canceled or reaches its deadline while it waits for a load gets `TOKEN_KEYS_UNAVAILABLE`, unless a load stored a result during the wait.
> - A JWKS that lists two usable entries under one `kid` with different key material, a different `alg`, or an `alg` in only one of them fails the load, and so does a response other than a 404 whose body is longer than 1 MiB.
> - A load of a source that is not required, whose result is not an answer, logs one warning.
>
> The Negative consequences state the costs: a 404 from a proxy with no route gives the tokens of a realm with no keys 401 rather than 503; where nothing routes traffic by `/ready`, so do the tokens of a required realm that never loaded a key; after a realm is deleted, Pods that loaded its keys accept its tokens until they expire while the others refuse them; and while a source returns a refused response, a key it withdrew stays accepted and a key it added does not load.
>
> The keys code of these rules is in the stack that ends in #208. #208 (e759672a) gives `TOKEN_REALM_UNKNOWN` for a missing realm, and on the path of an R33 refusal it still checks for a result stored after the refusal; R33 checks the token at the refusal, so that check changes no outcome.
>
> **Scope.** ADR-0104 in #329 cites these rules as this change leaves them (d1607e02). Alternative A12 is not used.
>
> Closes #289
>
> <sub>🤖 claude-opus-5-5 xhigh in=447k cached=29618k out=112k usd=11</sub>

Do not change any file and do not commit. You may run local commands such as `git`; there is no network, and you may
not use gh, a browser, or curl. End with the report the skill describes, as your final message.
