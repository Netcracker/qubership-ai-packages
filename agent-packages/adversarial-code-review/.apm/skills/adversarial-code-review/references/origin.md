# Origin of a finding

The verifier reads this file; the axes do not. An axis records a defect without deciding whether the change made it,
and the verifier decides once per finding, here. Decide which commit made the defect, not which hunk shows it: a
defect on a line the change rewrote can still be older than the change.

`input.md` names the branch the change merges into, and, under *Stack*, the other open requests whose commits the
reviewed range carries or builds on. Take the steps in order and stop at the first that decides: each costs more than
the one before it.

1. **The diff decides.** Where the defect lies in lines the diff adds, and not in older code those lines reach, the
   origin is `change`. So is a case the change claims to handle, in its description, a commit message, or the issue it
   closes, however old the code that breaks it: the claim is new. For such a case, still read `<base>` as in step 2,
   to choose its remedy below. Most findings stop here.
2. **Reading the base decides.** Read the code the defect lies in at `<base>` (`git -C <workspace> show <base>:<path>`).
   Where the defect is absent there, `git blame <head> -- <path>` over the defective lines names the commit that made
   it; go to step 4. Where it is present, go to step 4 as well, with the defect older than `<base>`.
3. **Running the base decides.** Only where reading cannot settle step 2, run the probe at `<base>` in your worktree,
   one worktree for all such findings. Where the run cannot settle it either, the origin is `change` with
   `confidence: medium`, and an `inference` in `evidence` says which part could not be checked.
4. **Attribute it.**
   - Where *Stack* is empty, a defect absent at `<base>` is `change`, and one present there is `preexisting`.
   - Where blame names a commit that *Stack* lists under another request, the origin is `stack`.
   - Where `<base>` is another open request's head and the defect exists at `<base>`, read the branch the stack merges
     into the same way: a defect absent there is `stack` too, and blame at `<base>` names the commit and *Stack* the
     request. Where the defect is missing code, such as an unhandled case, blame has no line to name: read, and only
     where reading cannot settle it run, the head of each request in *Stack* from the bottom up, and take the first
     one where the defect appears.
   - A defect on the branch the stack merges into is `preexisting`.

   Set `introduced_by` to the commit, where one is known, and for `stack` the URL of the request.

A `preexisting` defect that the change makes worse, claims to fix, or claims behavior it breaks is `change`. For any
other `preexisting` finding choose a `disposition`:

- `extend_scope`: the change's purpose reaches the defect. The code the change modifies meets a case it does not
  handle, handling the case takes a few lines in the files the change already touches, and it needs no decision the
  change has not already made. `proposed_solution` states the handling, or `suggestion` shows it.
- `follow_up`: everything else, such as a defect in code the axis read for context, or a case whose handling needs a
  design decision, another component, or more code than the change itself. `proposed_solution` states the fix the
  follow-up issue asks for.

A case the change claims to handle beyond the problem it sets out to fix, which fails at `<base>` too, leaves the
author two ways out: handle the case, or withdraw the claim. `proposed_solution` asks for the handling where the
handling meets the conditions of `extend_scope` above. Otherwise it asks to narrow the description or commit message to
the cases the change handles, or to replace a link that closes an issue with one that leaves the issue open, and names
where the other cases go: the open issue, the follow-up of a `preexisting` finding with the same cause, or a new issue
the author files. `retest` accepts either outcome. Where the narrowed claim would leave the change without its purpose,
as when the closed issue's own reproducer still fails, `proposed_solution` asks for the handling.

A `change` finding has no `disposition`, except `split_out`: the change makes the defect, and the fix that removes its
cause belongs in a change of its own. Choose it where all of these hold:

- the defect is a wrong answer for a property the change decides, and the finding is in a `recurring` family or is an
  architecture finding about a case list;
- computing the property needs a design decision the change has not made, another component, or more code than the
  change's own purpose;
- the property is not what the change's description or linked issue sets out to fix, so the change keeps its purpose
  without it.

`proposed_solution` is then two lines. `In this change:` names what to take out so that the change no longer decides
the property where it cannot compute it (the checks it adds that depend on it, the cases it lists for it), keeping the
checks whose context the code already knows. `Separate change:` names the change that computes the property, which a
follow-up issue tracks once delivery files it. `retest` names the neighbors and accepts for each either the answer at
`<base>` or the answer the property gives, so that both the narrowing and a full fix pass it. A `split_out` finding
keeps its severity, so the change does not merge until it is narrowed.

Decide `split_out` for the family, not for one finding: every `change` member whose location the narrowing takes out is
`split_out` with the same `Separate change:` line, and a `preexisting` member of the family is `follow_up` with the
same fix in its `proposed_solution`. Delivery files one issue for them all.
