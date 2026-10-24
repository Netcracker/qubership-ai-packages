# Axis: frontend web

Finding prefix: `WEB`.

Whether a person in a browser can complete the main journeys of this application, and is told the truth while doing
it: when the API fails, answers slowly, or returns less than the screen expects; after they change something; when
they reload, share a link, or press Back; when the data is as large as a real customer's; with only a keyboard. The
same axis covers the UI libraries the repository publishes for reuse, judged by what they do to the application that
imports them. The reader of every finding is a user who has not read the code and a maintainer who will.

Prefer driving the running application over reading its code. An observation from a driven browser comes first, and
the code is read afterwards to find the defect behind it. A slice may give you one package of a monorepo; say in your
coverage which journeys you drove, which you only read, and which you did not reach.

## What counts as a finding

- **A failure the UI does not survive.** A request error that leaves a spinner forever; a 403 or a 500 rendered as an
  empty list, so the user concludes there is no data; an unhandled promise rejection that leaves a half-updated
  screen; a render error with no error boundary, so one bad record blanks the whole page; a slow response with no
  feedback that invites a double submit; an optional field missing from a response that crashes the view or renders
  `undefined`. The expectation is the same failure handled on a sibling screen, the server's schema (which fields are
  optional), or the data-fetching library's documented error and loading states.
- **Client state that disagrees with the server or with itself.** Stale data after a successful mutation because the
  cache was not invalidated; two views of one entity that show different values; an optimistic update kept after the
  request failed; a response to an older request that overwrites the newer one (filter typed fast, tab switched
  quickly). The expectation is the data-fetching library's invalidation and cancellation documentation, or the
  framework's documented race handling (React: the `ignore` flag in "Fetching data" under *Synchronizing with
  Effects*).
- **Routing and deep links.** A screen state the user would share (a selected item, a filter, a tab) that the URL does
  not carry; a URL that 404s on reload because the static server has no history fallback; Back that loses unsaved
  input or jumps two screens; a deep link to a missing or forbidden id that shows a generic crash rather than "not
  found" or "no access".
- **Framework misuse that the framework's own documentation calls a bug.** Derive the rules from the framework and
  version in the profile's inventory and cite the page. For React (`react.dev`): an effect that subscribes, sets a
  timer, or adds a listener without cleanup; a stale closure over state in a callback or interval; a list without a
  stable `key`, or keyed by index where items reorder or are deleted; state set during render; a component mutating
  props or shared objects (*Keeping Components Pure*); an effect used to derive state that should be computed in
  render (*You Might Not Need an Effect*), where it causes an extra render or a visible flicker. For Vue, Angular,
  Svelte, or Solid, find the equivalent pages (lost reactivity on destructuring, an Observable subscription never
  unsubscribed, a store subscription outside a component lifecycle). A rule violation, or a framework warning in the
  console of a main page (quote it verbatim), is a candidate; it becomes a finding when you name the trigger and what
  the user sees.
- **Rendering that does not scale to realistic input, measured.** A long list or table rendered without
  virtualization, a large document parsed or diffed on the main thread, a re-render of the whole tree on every
  keystroke. State the input size, the device profile, and the number: long-task duration, time to first usable
  render, interaction latency, DOM node count, heap.
- **What ships to the browser.** Source maps served in production where the project does not intend it; debug flags,
  mock handlers, development builds of the framework, or verbose logging enabled in the production bundle; an initial
  chunk that carries a whole editor or charting library for a route that does not use it; a deploy that strands open
  tabs because `index.html` is cached together with the hashed assets and old chunks are deleted. The expectation is
  the build tool's documented production mode and the project's own budget, if it declares one.
- **Accessibility that blocks use.** A main journey that cannot be completed with a keyboard; a dialog that does not
  move or trap focus, or does not return it; an icon-only button or a form field with no accessible name; a focus
  indicator removed globally. Cite WCAG 2.2 success criteria (2.1.1, 2.4.3, 2.4.7, 4.1.2, 1.3.1) and the axe rule id.
- **A published UI library that harms its host.** Side effects on import (global CSS, polyfills, `window` mutation,
  custom element registration) with `"sideEffects": false` declared or no way to opt out; a peer dependency range that
  admits a framework version the library does not work with, or a framework listed in `dependencies` so the host
  ships two copies; an `exports` map or type entry that fails to resolve for a supported consumer setup; an import of
  one component that pulls in the whole library.

## What is not a finding

- A preference for another framework, state library, or styling approach; visual design and copy, unless the result
  blocks use under the accessibility rules above.
- A Lighthouse or bundle-size number on its own. Say what it costs a user (seconds on a stated network and device) or
  which declared budget it breaks.
- A missing `useMemo` or `memo` without a measured render cost; a lint hit with no demonstrated trigger.
- A full WCAG audit. Report what blocks a journey or what axe classes as `critical` or `serious` on a main page.
- Behavior seen only in the development server (hot reload, StrictMode double invocation) that does not reach the
  production build, except where StrictMode's double invocation exposes a missing cleanup that does reach it.

## Method

1. **Read the inventory.** From the profile: framework and version, router, data-fetching or state library, build
   tool, the static server for the production build, and any e2e suite (its config often carries the start command).
   Fetch the documentation of the framework and the data library at that version; a finding cites the page.
2. **Start the application.** Use `00-commands.md`; otherwise `package.json` scripts, a compose file, or the e2e
   config. Run the development build for framework warnings and the production build, behind the server it ships
   with, for everything else. Where the backend cannot run, use the repository's own mocks (MSW handlers, fixture
   servers, recorded HAR) and say so. Record what you started in `work/commands-frontend-web.md`.
3. **Drive the main journeys.** Take three to six from the route table, the navigation, and the e2e suite. Script each
   with Playwright under `work/`, collecting `console`, `pageerror`, `requestfailed`, and every response with status
   400 or above. Keep the scripts; they are the evidence.
4. **Inject failures.** For each journey's main requests, use `page.route` to return 500, 403, 404, an empty
   collection, a body with optional fields removed, a 15-second delay, and `route.abort()`. Fail a mutation after the
   UI has updated optimistically. Delay the first of two requests so the responses arrive out of order. Record what
   the user sees after the wait and take a screenshot.
5. **Exercise routing.** From each state worth sharing, copy the URL, open it in a fresh context, reload, go Back and
   Forward, and open a deep link to a missing id and to a forbidden one, against the production server.
6. **Measure at scale.** Build the largest realistic input from tracked fixtures or anonymized captures, then a tenfold
   one. Use Chromium with 4x CPU throttling (CDP `Emulation.setCPUThrottlingRate`), collect long tasks through a
   `PerformanceObserver`, and record time to usable render, interaction latency, DOM node count, and heap.
7. **Inventory the production bundle.** Build it, list chunk sizes (compressed), request a `.map` file from the
   running server, and search the output for debug flags, mock handlers, `localhost`, internal host names, and
   environment values. Use the build tool's analyzer or `source-map-explorer` to name what dominates the initial chunk.
   Check the cache headers on `index.html` and on hashed assets.
8. **Check accessibility basics.** Run `@axe-core/playwright` on each main page, and complete one main journey with
   the keyboard only.
9. **Read the code behind each observation.** Then sweep for the framework rules in step 1: run the framework's lint
   plugin (for React, `eslint-plugin-react-hooks` with `rules-of-hooks` and `exhaustive-deps`) in a throwaway copy
   and triage each hit into a finding with a trigger, or a line under *Отклонено автором*.
10. **For a published library:** `npm pack --dry-run`, `publint`, and `@arethetypeswrong/cli`; then a scratch
    consumer that imports one export, built twice, at the lowest and the highest framework version the peer range
    admits. Measure what the single import pulls in and what importing it changes globally.

## Required section

End the report with **Journeys driven**, one row per journey and one per library consumer check. Synthesis axes and
the consolidator read it to know which behavior has been seen running.

| Journey | Build (dev / prod) | Backend (real / mock / stub) | Failures injected | What the user saw | Evidence |
| --- | --- | --- | --- | --- | --- |

List under it the journeys you only read, and why.

## Severity

`HIGH`: a main journey cannot be completed under a realistic failure or input size; the UI shows wrong data as
correct (a 403 as an empty list, a stale value after a confirmed save, a rolled-back change still displayed); user
input is lost on navigation or reload; the production build ships a development framework build. `MEDIUM`: a secondary
journey with the same defects, a state that cannot be shared or reloaded, a measured slowdown that makes a realistic
input painful but usable. `LOW`: console noise with no user-visible effect, a single unlabeled control off the main
journeys.

## Ownership

| Concern | Owner axis |
| --- | --- |
| XSS, unsafe HTML injection, CSP, token and session storage in the browser, a credential found in the bundle, anything an attacker exploits | `security` (record the pointer and the bundle path here) |
| Whether the UI's API client agrees with the server's spec: paths, fields, types, status codes | `contracts` |
| How the server shapes an error (status, problem body); how the UI renders it stays here | `error-model` |
| Client-side error reporting and logging: whether a failure reaches Sentry or a log, and what it carries | `telemetry` |
| A label, confirmation, or destructive action whose behavior contradicts what the UI tells the user | `least-surprise` |
| Naming and shape of a published library's API, its doc comments and examples | `api-ux` |
| Breaking changes between versions of a published library | `api-compatibility` |
| Dependency staleness, vulnerabilities, licenses, and tree size; peer ranges and duplicate framework copies stay here | `dependencies` |
| Build reproducibility, CI, publishing; what the production output contains stays here | `build-release` |
| Backend latency and throughput; client rendering and bundle cost stay here | `performance` |
| The chart or server configuration around the static server; history fallback and asset cache headers stay here | `deployment-config` |
| Logic defects unrelated to UI state or the framework (date math, sorting rules) | `correctness` |
| Which journeys have tests, at which level, and whether the e2e suite can fail | `test-strategy`, `tests` |
